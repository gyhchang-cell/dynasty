#!/usr/bin/env python3
"""Run-owned, immutable identity snapshot of the actual Gradle development classpath.

Invoked by runClient.doFirst after its compile/resource dependencies. This records
bytes supplied to the client, not a packaged-JAR claim or a model-quality pass.
"""
import hashlib
import json
import re
import sys
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ("com/dynasty/Dynasty.class", "META-INF/mods.toml")
if sys.argv[1] == "--launch":
    # Independent JVMs must not read class directories another local chat can rebuild.
    # Preserve the exact JavaExec configuration, including Forge's legacy classpath file.
    launch = Path(sys.argv[2]).resolve()
    identity = sys.argv[3]
    assert re.fullmatch(r"[A-Za-z0-9_.-]+", identity), "Unsafe run identity"
    config = json.loads(launch.read_text())
    frozen = ROOT / "build/blueprint-client/frozen" / identity
    assert not frozen.exists(), "Immutable runtime already exists; use a fresh identity"
    roots = {Path(p).resolve() for p in config["classpath"].split(os.pathsep) if Path(p).is_dir()}
    aliases = {str(Path(p)): str(Path(p).resolve()) for p in config["classpath"].split(os.pathsep) if Path(p).is_dir()}
    for entry in config.get("environment", {}).get("MOD_CLASSES", "").split(os.pathsep):
        if "%%" in entry:
            directory = Path(entry.split("%%", 1)[1]).resolve()
            aliases[str(Path(entry.split("%%", 1)[1]))] = str(directory)
            directory.mkdir(parents=True, exist_ok=True)
            roots.add(directory)
    for entry in REQUIRED:
        assert any((directory / entry).is_file() for directory in roots), f"Refusing incomplete compile/resources output: {entry}"
    frozen.mkdir(parents=True)
    mapping = {}
    snapshots = []
    for index, directory in enumerate(sorted(roots)):
        target = frozen / f"tree-{index}"
        shutil.copytree(directory, target)
        entries = []
        for path in sorted(target.rglob("*")):
            if path.is_file():
                relative = path.relative_to(target)
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                assert digest == hashlib.sha256((directory / relative).read_bytes()).hexdigest(), "Concurrent compilation changed runtime bytes during copy"
                entries.append(dict(path=relative.as_posix(), sha256=digest))
        mapping[str(directory)] = str(target)
        snapshots.append(dict(source=str(directory), runtime=str(target), entries=entries))
    # macOS resolves /tmp to /private/tmp. Launch strings can retain the alias;
    # both spellings must map to the same immutable directory.
    for alias, canonical in aliases.items():
        if canonical in mapping:
            mapping[alias] = mapping[canonical]
    for entry in REQUIRED:
        if not any((Path(directory) / entry).is_file() for directory in mapping.values()):
            (frozen / "DO_NOT_RUN.txt").write_text("Concurrent compilation left an incomplete mod runtime; no game acceptance may use it.\n")
            raise AssertionError(f"Incomplete frozen mod entry: {entry}")
    def remap(value):
        for original, replacement in sorted(mapping.items(), key=lambda item: -len(item[0])):
            value = value.replace(original, replacement)
        return value
    config["classpath"] = remap(config["classpath"])
    config["environment"] = {key: remap(value) for key, value in config["environment"].items()}
    args = []
    for argument in config["jvmArgs"]:
        if argument.startswith("-DlegacyClassPath.file="):
            original = Path(argument.split("=", 1)[1])
            target = frozen / "legacy-classpath.txt"
            target.write_text(remap(original.read_text()))
            argument = "-DlegacyClassPath.file=" + str(target)
        args.append(remap(argument))
    config["jvmArgs"] = args
    config["args"] = [remap(argument) for argument in config["args"]]
    output = frozen / "launch.json"
    output.write_text(json.dumps(config, indent=2) + "\n")
    (frozen / "runtime-manifest.json").write_text(json.dumps(dict(run=identity, scope="Copied immutable native JVM inputs", trees=snapshots), indent=2)+"\n")
    print(output)
    sys.exit(0)
run = sys.argv[1]
assert re.fullmatch(r"[A-Za-z0-9_.-]+", run), "Unsafe run identity"
base = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else ROOT / "build"
for directory, entry in (("classes/java/main", REQUIRED[0]), ("resources/main", REQUIRED[1])):
    assert (base / directory / entry).is_file(), f"Refusing incomplete compile/resources output: {base}/{directory}/{entry}"
trees = []
for directory in ("classes/java/main", "resources/main", "classes/java/blueprintQa"):
    root = base / directory
    relative = root.relative_to(ROOT).as_posix() if root.is_relative_to(ROOT) else root.as_posix()
    assert root.is_dir(), f"Compile/resources dependency missing: {relative}"
    entries = []
    for path in sorted(root.rglob("*"), key=lambda path: path.relative_to(root).as_posix()):
        if path.is_file():
            entries.append(dict(path=path.relative_to(root).as_posix(), bytes=path.stat().st_size,
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    digest = hashlib.sha256("".join(e["path"] + "\0" + e["sha256"] + "\n" for e in entries).encode()).hexdigest()
    trees.append(dict(root=relative, fileCount=len(entries), bytes=sum(e["bytes"] for e in entries),
                      sha256=digest, entries=entries))
production = hashlib.sha256("".join(t["root"] + "\0" + t["sha256"] + "\n" for t in trees[:2]).encode()).hexdigest()
target = ROOT / "docs/blueprint-cod1/ingame" / run / "artifact-manifest.json"
if target.exists():
    existing = json.loads(target.read_text())
    assert existing["run"] == run and existing["trees"] == trees, "Run's frozen classpath changed; use a new run ID"
else:
    target.parent.mkdir(parents=True, exist_ok=True)
    expanded_inputs = [dict(path=name, sha256=hashlib.sha256((ROOT / name).read_bytes()).hexdigest()) for name in
        ("build.gradle", "gradle.properties", "src/main/resources/META-INF/mods.toml", "src/main/resources/pack.mcmeta")]
    target.write_text(json.dumps(dict(formatVersion=1, run=run, createdAt=datetime.now(timezone.utc).isoformat(),
                                     scope="Gradle runClient.doFirst development classpath supplied to both clients",
                                     productionSha256=production, trees=trees, expandedInputs=expanded_inputs), indent=2) + "\n")
print("Frozen development classpath", run, production)

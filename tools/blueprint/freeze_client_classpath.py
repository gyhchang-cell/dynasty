#!/usr/bin/env python3
"""Run-owned, immutable identity snapshot of the actual Gradle development classpath.

Invoked by runClient.doFirst after its compile/resource dependencies. This records
bytes supplied to the client, not a packaged-JAR claim or a model-quality pass.
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
run = sys.argv[1]
assert re.fullmatch(r"[A-Za-z0-9_.-]+", run), "Unsafe run identity"
trees = []
for relative in ("build/classes/java/main", "build/resources/main", "build/classes/java/blueprintQa"):
    root = ROOT / relative
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

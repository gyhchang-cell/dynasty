"""Publish only this guard art batch, using destination hashes, without Git push.

Run in the existing isolated worktree. All other frozen worktree sources are
deliberately excluded. A changed destination is an error, never overwritten.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PRIMARY = Path("/Users/a15356015027/Desktop/dynasty")
OUT = ROOT / "docs/art/guard-style-v2"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert ROOT != PRIMARY, "Run publication from the isolated art worktree"
    runpy.run_path(str(ROOT / "tools/art/secondary-cuboid/verify_guard_style.py"), run_name="__main__")
    ownership = json.loads((OUT / "source-ownership.json").read_text())["primary"]
    paths = list(ownership) + [
        "tools/art/secondary-cuboid/qa/com/dynasty/client/GuardStyleClientQa.java",
        "tools/art/secondary-cuboid/qa/com/dynasty/client/GuardStyleProof.java",
        "tools/art/secondary-cuboid/qa/com/dynasty/client/character/LegacyGuardModel.java",
        "tools/art/secondary-cuboid/verify_guard_style.py",
        "tools/art/secondary-cuboid/guard_style_views.py",
        "tools/art/secondary-cuboid/sync_guard_style.py",
    ]
    paths += [str(p.relative_to(ROOT)) for p in sorted(OUT.rglob("*")) if p.is_file() and p.name not in ["client.log", "primary-sync.json"]]
    assert len(paths) == len(set(paths))
    originals, payloads = {}, {}
    for name in paths:
        src, dst = ROOT / name, PRIMARY / name
        data = src.read_bytes()
        previous = dst.read_bytes() if dst.exists() else None
        if previous != data:
            assert name in ownership and previous is not None and digest(previous) == ownership[name] or previous is None, "Concurrent destination changes: " + name
        originals[name], payloads[name] = previous, data
    artifact = PRIMARY / "build/maintenance-artifacts/art-guard-style-v2/dynasty-1.4.0.jar"
    frozen = ROOT / "build/secondary-art-native/guard-style-final-03/production.jar"
    artifact_bytes = frozen.read_bytes()
    assert digest(artifact_bytes) == "a30ab98c3801c1b09a09310407b001341fe1df537171316f91dd1acc4ee9923f"
    assert not artifact.exists() or artifact.read_bytes() == artifact_bytes
    for name in paths:
        dst, data = PRIMARY / name, payloads[name]
        previous = dst.read_bytes() if dst.exists() else None
        assert previous == originals[name], "Concurrent edit after preflight: " + name
        if previous == data:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(prefix=".guard-art-", dir=dst.parent)
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(data)
            assert (dst.read_bytes() if dst.exists() else None) == previous, "Concurrent edit before replace: " + name
            os.replace(temp, dst)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    if not artifact.exists():
        shutil.copy2(frozen, artifact)
    assert digest(artifact.read_bytes()) == digest(artifact_bytes)
    for name, data in payloads.items():
        assert (PRIMARY / name).read_bytes() == data, name
    receipt = {"publishedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "primary": str(PRIMARY),
               "source": str(ROOT), "scope": "Explicit guard art/presentation and own evidence only; no other developers' files, no push",
               "files": [{"path": n, "sha256": digest(payloads[n])} for n in paths],
               "artifact": str(artifact), "artifactSha256": digest(artifact_bytes),
               "sourceFreeze": "Historical isolated source snapshot; this JAR excludes newer unrelated primary WIP", "pushed": False}
    (OUT / "primary-sync.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    shutil.copy2(OUT / "primary-sync.json", PRIMARY / "docs/art/guard-style-v2/primary-sync.json")
    print(f"Published {len(paths)} explicitly owned files and exact frozen artifact to local main checkout; no push")


if __name__ == "__main__":
    main()

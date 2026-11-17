#!/usr/bin/env python3
"""Verify local evidence against pinned manifests and existing Git objects. No fetch."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "src/main/java/com/dynasty").is_dir())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def main():
    errors, reports = [], []
    proposal = json.loads((HERE / "immune-reference-batch-007.json").read_text())
    prov = proposal["provenance"]
    manifest_raw = (ROOT / prov["manifest_path"]).read_bytes()
    assert sha(manifest_raw) == prov["manifest_sha256"]
    manifest = next(r for r in json.loads(manifest_raw) if r["repo"] == proposal["repo"])
    assert manifest["commit"] == proposal["commit"]
    git = ["git", "--git-dir=" + str(ROOT / prov["bare_git_path"])]

    def git_bytes(path):
        return subprocess.check_output(git + ["cat-file", "blob", proposal["commit"] + ":" + path])

    tree = subprocess.check_output(git + ["rev-parse", proposal["commit"] + "^{tree}"], text=True).strip()
    assert tree == prov["git_tree"] == manifest["git_tree"]
    entries = {f["source"]: f for f in manifest["files"]}
    held = json.loads((HERE / "offline-held-candidates-003.json").read_text())
    held_raw = (ROOT / held["source_manifest_path"]).read_bytes()
    assert sha(held_raw) == held["source_manifest_sha256"]
    held_sources = {s["repo"]: s for s in json.loads(held_raw)}
    checked, paths = 0, set()

    def check_ref(ref, native_bytes=None):
        nonlocal checked
        path = (ROOT / ref["path"]).resolve()
        assert path.is_relative_to(ROOT)
        raw = path.read_bytes()
        assert sha(raw) == ref["file_sha256"], str(path)
        assert blob(raw) == ref["git_blob_sha1"], str(path)
        start, end = ref["lines"]
        assert 1 <= start <= end <= len(raw.decode().splitlines()), (path, start, end)
        if native_bytes is not None:
            assert raw == native_bytes, str(path)
        checked += 1
        paths.add(str(path.relative_to(ROOT)))

    for ref in proposal["source_refs"]:
        entry = entries[ref["path"]]
        assert entry["sourceSha256"] == ref["file_sha256"]
        assert entry["source_blob"] == ref["git_blob_sha1"]
        check_ref(ref, git_bytes(ref["upstream_path"]))
    for case in held["cases"]:
        source = held_sources[case["repo"]]
        assert source["commit"] == case["commit"]
        base = "tools/cod4/immune-feedback-research/sources/" + case["repo"].replace("/", "__") + "/"
        index = {base + f["path"]: f for f in source["files"]}
        assert case["research_credit"] == case["maximum_proposed_credit"] == 0
        for ref in case["source_refs"]:
            entry = index[ref["path"]]
            assert entry["sha256"] == ref["file_sha256"]
            assert entry["git_blob_sha1"] == ref["git_blob_sha1"]
            check_ref(ref)
    sound = proposal["sound_binding_local_git_evidence"]
    raw = git_bytes(sound["upstream_path"])
    assert sha(raw) == sound["file_sha256"] and blob(raw) == sound["git_blob_sha1"]
    bindings = json.loads(raw)
    assert all(bindings[k] == v for k, v in sound["selected_bindings"].items())
    for entry in sound["audio_objects"]:
        assert entry["present_in_local_git"] and not entry["auditioned"]
        assert blob(git_bytes(entry["upstream_path"])) == entry["git_blob_sha1"]
    for name, document in [("immune-reference-batch-007.json", proposal), ("offline-held-candidates-003.json", held)]:
        assert document["research_credit"] == 0 and document["production_changes"] is False
        assert document["runtime_executed"] is False
        reports.append({"path": str((HERE / name).relative_to(ROOT)), "sha256": sha((HERE / name).read_bytes()),
                        "maximum_proposed_credit": document["maximum_proposed_credit"]})
    ledger = ROOT / proposal["dedup_snapshot"]["path"]
    current = ledger.read_bytes()
    result = {"status": "PASS", "artifacts": reports, "source_ranges_checked": checked,
              "unique_source_files": len(paths), "betweenlands_ranges_verified_against_local_git": len(proposal["source_refs"]),
              "sound_index_and_audio_git_objects_checked": 3,
              "immune_ledger_rows_observed": len(json.loads(current)),
              "ledger_changed_since_semantic_snapshot": sha(current) != proposal["dedup_snapshot"]["sha256"],
              "research_credit_awarded": 0, "network_fetches": 0, "runtime_executed": False,
              "limits": ["Source provenance consistency only; independent semantic acceptance remains pending.",
                         "No upstream program, Minecraft, native runtime or audio playback executed.",
                         "Held candidates remain zero even when their available source hashes pass."]}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

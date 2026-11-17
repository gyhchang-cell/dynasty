#!/usr/bin/env python3
"""Read-only fixed-local Git evidence check; awards no semantic credit."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "src/main/java/com/dynasty").is_dir())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    proposal_path = HERE / "immune-reference-batch-013.json"
    proposal_raw = proposal_path.read_bytes()
    doc = json.loads(proposal_raw)
    assert doc["research_credit"] == 0 and doc["maximum_proposed_credit"] == 0
    assert doc["production_changes"] is False and doc["runtime_executed"] is False
    prov = doc["provenance"]
    manifest_raw = (ROOT / prov["manifest_path"]).read_bytes()
    assert sha(manifest_raw) == prov["manifest_sha256"]
    manifest = next(s for s in json.loads(manifest_raw) if s["repo"] == doc["repo"])
    assert manifest["commit"] == doc["commit"]
    entries = {f["source"]: f for f in manifest["files"]}
    git = ["git", "--git-dir=" + str(ROOT / prov["bare_git_path"])]
    tree = subprocess.check_output(git + ["rev-parse", doc["commit"] + "^{tree}"], text=True).strip()
    assert tree == manifest["git_tree"] == prov["git_tree"]
    cached, checked, covered = {}, [], set()
    for ref in doc["source_refs"]:
        path = (ROOT / ref["path"]).resolve()
        assert path.is_relative_to(ROOT)
        raw = path.read_bytes()
        entry = entries[ref["path"]]
        assert entry["path"] == ref["upstream_path"]
        assert sha(raw) == entry["sourceSha256"] == ref["file_sha256"]
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        assert blob == entry["source_blob"] == ref["git_blob_sha1"]
        if ref["upstream_path"] not in cached:
            cached[ref["upstream_path"]] = subprocess.check_output(
                git + ["cat-file", "blob", doc["commit"] + ":" + ref["upstream_path"]])
        assert raw == cached[ref["upstream_path"]]
        lines = raw.decode("utf-8", errors="replace").splitlines()
        start, end = ref["lines"]
        assert 1 <= start <= end <= len(lines), (ref["path"], start, end)
        covered.update((ref["path"], line) for line in range(start, end + 1))
        checked.append({"path": ref["path"], "lines": [start, end],
                        "range_text_sha256": sha("\n".join(lines[start - 1:end]).encode())})
    ledger_raw = (ROOT / doc["dedup_snapshot"]["path"]).read_bytes()
    ledger = json.loads(ledger_raw)
    accepted_ids = {r["id"] for r in ledger}
    assert all(r["accepted_id"] in accepted_ids for r in doc["dedup_snapshot"]["comparisons"])
    result = {"status": "PASS", "proposal_path": str(proposal_path.relative_to(ROOT)),
              "proposal_sha256": sha(proposal_raw), "source_ranges_verified": len(checked),
              "unique_source_files_verified_against_existing_local_git": len(cached),
              "unique_cited_source_lines": len(covered), "ranges": checked,
              "ledger_rows_observed": len(ledger),
              "ledger_changed_since_semantic_snapshot": sha(ledger_raw) != doc["dedup_snapshot"]["sha256"],
              "range_text_decoding": "UTF-8 errors=replace; raw bytes still checked exactly against Git",
              "maximum_pending_credit": 0, "research_credit_awarded": 0,
              "network_requests": 0, "game_or_upstream_execution": False,
              "limits": ["Provenance consistency does not establish semantic uniqueness or runtime correctness.",
                         "All cited lines, wrappers and arithmetic examples are support, never separate credit.",
                         "Independent coordinator must read actual source and decide acceptance."]}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

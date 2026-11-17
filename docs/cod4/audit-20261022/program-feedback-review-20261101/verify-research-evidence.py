#!/usr/bin/env python3
"""Read-only evidence verification; does not execute Minecraft or award credit."""
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "src/main/java/com/dynasty").is_dir())
ARTIFACTS = [
    "immune-reference-batch-003.json",
    "immune-reference-batch-004.json",
    "immune-reference-batch-005.json",
    "immune-reference-batch-006.json",
    "clone-reference-batch-001.json",
    "clone-persistence-acceptance-proposal.json",
    "program-p04-world-event-lifecycle-review.json",
    "program-p05-sequence-and-death-receipt-review.json",
    "program-p06-transaction-and-secret-review.json",
    "program-p14-damage-chain-review.json",
]


def objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from objects(child)


def main():
    failures, reports, snapshot_changes = [], [], []
    all_paths = set()
    dispatch = json.loads((ROOT / "docs/cod4/audit-20261022/all-cod-direct-dispatch-20261101.json").read_text())
    authorized_briefs = {Path(entry["path"]).resolve() for entry in dispatch["files"]}
    manifest_path = ROOT / "docs/cod4/audit-20261022/immune-feedback-research/sources.json"
    manifest = json.loads(manifest_path.read_text())
    indexed = {}
    for source in manifest:
        base = "tools/cod4/immune-feedback-research/sources/" + source["repo"].replace("/", "__") + "/"
        for entry in source["files"]:
            indexed[base + entry["path"]] = entry

    for name in ARTIFACTS:
        raw = (HERE / name).read_bytes()
        document = json.loads(raw)
        checked = native = blob_checked = 0
        if document.get("research_credit") != 0:
            failures.append(f"{name}: unexpectedly awards research credit")
        if document.get("production_changes") not in (False, 0):
            failures.append(f"{name}: production_changes must be false")
        for node in objects(document):
            path = node.get("path")
            expected = node.get("file_sha256", node.get("sha256"))
            if not path or not expected:
                continue
            try:
                full_path = (ROOT / path).resolve()
                if not full_path.is_relative_to(ROOT) and full_path not in authorized_briefs:
                    raise ValueError("reference outside project and explicitly dispatched source briefs")
                data = full_path.read_bytes()
                actual = hashlib.sha256(data).hexdigest()
                if actual != expected:
                    if node is document.get("dedup_snapshot"):
                        snapshot_changes.append({"artifact": name, "path": path,
                            "recorded_sha256": expected, "current_sha256": actual,
                            "reason": "Shared ledger is a historical dedup snapshot, not immutable source. Re-review uniqueness against current ledger."})
                    else:
                        failures.append(f"{name}: content changed: {path}")
                if "lines" in node:
                    start, end = node["lines"]
                    if not 1 <= start <= end <= len(data.decode("utf-8").splitlines()):
                        failures.append(f"{name}: invalid source range: {path}:{start}-{end}")
                blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                if "git_blob_sha1" in node:
                    blob_checked += 1
                    if node["git_blob_sha1"] != blob:
                        failures.append(f"{name}: Git blob mismatch: {path}")
                if path.startswith("tools/cod4/immune-feedback-research/sources/"):
                    native += 1
                    stored = indexed.get(path)
                    if stored is None or stored["sha256"] != actual:
                        failures.append(f"{name}: current pinned source manifest mismatch: {path}")
                    elif "git_blob_sha1" in stored and stored["git_blob_sha1"] != blob:
                        failures.append(f"{name}: pinned manifest Git blob mismatch: {path}")
                checked += 1
                all_paths.add(path)
            except (OSError, ValueError, TypeError, KeyError) as error:
                failures.append(f"{name}: {path}: {error}")
        if checked == 0:
            failures.append(f"{name}: no independently verifiable references")
        reports.append({"artifact": name, "sha256": hashlib.sha256(raw).hexdigest(),
                        "checked_references": checked, "native_source_references": native,
                        "explicit_git_blob_checks": blob_checked})

    ledger = ROOT / "docs/cod4/audit-20261022/immune-feedback-research/reviewed.json"
    rows = json.loads(ledger.read_text())
    result = {"status": "PASS" if not failures else "FAIL", "artifacts": reports,
              "unique_reference_files": len(all_paths), "failures": failures,
              "mutable_snapshot_changes": snapshot_changes,
              "immune_ledger_snapshot": {"path": str(ledger.relative_to(ROOT)),
                  "sha256": hashlib.sha256(ledger.read_bytes()).hexdigest(),
                  "rows_observed": len(rows)},
              "research_credit_awarded": 0, "runtime_or_game_tests_executed": False,
              "limits": ["Hashes/ranges verify provenance consistency, not semantic correctness or gameplay.",
                         "Existing source manifest checked locally; no new remote Git-tree verification.",
                         "Master reviewer alone determines semantic uniqueness and acceptance."]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

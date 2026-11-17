"""Unexecuted private137 v1, current513/ecology53 and exact private514 postimages.

All old136 HELD/v2/v3 authorities remain permanently consumed. No import/help/run is authorized.
Main must independently review this fresh exact
plan and external one-use authority. Sequential three-file writes are not atomic;
an attempt consumes authority and must never be retried or silently rebased.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = Path(__file__).resolve().parent
PLAN = PRIVATE / "batch-137-current513-ecology53-v1-private-append-plan-20261111.json"
MAIN = "01a16364-cac0-7ca2-a042-a5312781ca34"
FORMAL = ["docs/cod4/audit-20261022/immune-feedback-research/" + n
          for n in ("reviewed.json", "semantic-dedup.json", "progress.json")]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode())


def resolve(label):
    path = Path(label)
    return path if path.is_absolute() else ROOT / path


def checked_bytes(bound):
    raw = resolve(bound["path"]).read_bytes()
    require(len(raw) == bound["bytes"] and digest(raw) == bound["sha256"],
            "Frozen bytes changed: " + bound["path"])
    return raw


def bound_here(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)),
            "sha256": digest(raw), "bytes": len(raw)}


def exclusive_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-sha256", required=True)
    parser.add_argument("--review-bytes", type=int, required=True)
    args = parser.parse_args()
    plan_raw = PLAN.read_bytes()
    plan_binding = {"path": str(PLAN.resolve().relative_to(ROOT)),
                    "sha256": digest(plan_raw), "bytes": len(plan_raw)}
    plan = json.loads(plan_raw)
    require(plan["batch"] == 137 and plan["allowed_formal_paths_now"] == [],
            "Wrong private proposal")
    # A grant cannot waive drift in this immutable version. A separately reviewed
    # new proposal is necessary; this script never refreshes any frozen input.
    require(not plan["unresolved_prior_input_drifts"] and
            not plan["unresolved_inventory_differences"], "HELD input drift")
    require(plan["unexecuted_append_script"] == bound_here(__file__), "Code drift")
    review_path = resolve(plan["future_Main_exact_plan_review_path"])
    review_raw = review_path.read_bytes()
    require(digest(review_raw) == args.review_sha256 and
            len(review_raw) == args.review_bytes, "Exact review differs")
    review = json.loads(review_raw)
    require(review.get("reviewer_thread_id") == MAIN and
            review.get("append_authorized") is True and
            review.get("single_execution_granted") is True and
            review.get("production_authorized") is False, "No exact Main authority")
    require(review.get("plan") == plan_binding and
            review.get("script") == bound_here(__file__) and
            review.get("readset") == plan["current_readset"] and
            review.get("allowed_formal_paths") == FORMAL and
            review.get("private_preimages") == plan["private_preimages"] and
            review.get("private_postimages") == plan["private_postimages"],
            "Authority scope differs")
    marker = resolve(plan["future_one_time_start_marker"])
    proof = resolve(plan["future_proof_path"])
    require(not marker.exists() and not proof.exists(), "Authority already consumed")
    readset = json.loads(checked_bytes(plan["current_readset"]))
    require(len(readset["files"]) == plan["frozen_input_count"], "Input count drift")
    require(not readset["unresolved_prior_input_drifts"] and
            not readset["unresolved_inventory_differences"], "HELD readset drift")

    def check_frozen():
        for bound in readset["files"]:
            checked_bytes(bound)
        for inventory in readset["inventories"]:
            actual = sorted(str(p.resolve()) for p in
                            resolve(inventory["directory"]).glob(inventory["glob"])
                            if p.is_file())
            require(actual == inventory["paths"], "Inventory changed")
        for label in readset["must_remain_absent"]:
            require(not resolve(label).exists(), "Expected absence changed")

    check_frozen()
    before = [checked_bytes(b) for b in plan["private_preimages"]]
    after = [checked_bytes(b) for b in plan["private_postimages"]]
    require(plan["allowed_formal_paths_after_later_explicit_authorization"] == FORMAL,
            "Output path drift")
    require([resolve(p).read_bytes() for p in FORMAL] == before, "Baseline differs")
    old_rows, old_dedup, old_progress = [json.loads(b) for b in before]
    rows, dedup, progress = [json.loads(b) for b in after]
    require(len(old_rows) == 513 and len(rows) == 514 and rows[:-1] == old_rows,
            "Whole row preservation failed")
    require([canonical(v) for v in old_rows] ==
            plan["old513_complete_object_canonical_hashes"], "Old row hashes differ")
    require(len(old_dedup["groups"]) == 241 and len(dedup["groups"]) == 242 and
            dedup["groups"][:-1] == old_dedup["groups"], "Old groups differ")
    require({k: v for k, v in dedup.items() if k != "groups"} ==
            {k: v for k, v in old_dedup.items() if k != "groups"}, "Dedup metadata differs")
    require(rows[-1] == plan["entry"] and dedup["groups"][-1] == plan["dedup_group"],
            "New whole differs")
    require(old_progress["reviewed_effective_semantic_dedup"] == 513 and
            old_progress["remaining"] == 487 and
            old_progress["formal_design_gate_satisfied"] is False, "Baseline progress differs")
    require([v["id"] for v in old_rows] ==
            plan["old513_complete_object_id_order"], "Old identity order differs")
    expected_progress = dict(old_progress)
    expected_progress.update(reviewed_effective_semantic_dedup=514, remaining=486)
    require(progress == expected_progress and
            progress["formal_design_gate_satisfied"] is False, "Progress differs")
    require(len({r["id"] for r in rows}) == 514 and
            len({r["semantic_dedup_key"] for r in rows}) == 514 and
            rows[-1]["research_credit"] == 1, "Identity/count differs")
    require([canonical(v) for v in old_dedup["groups"]] ==
            plan["old241_complete_group_canonical_hashes"], "Old group hashes differ")
    for index, tail in [(0, b"\n]\n"), (1, b"\n  ]\n}\n")]:
        prefix = before[index][:-len(tail)]
        require(before[index].endswith(tail) and after[index].startswith(prefix + b",\n"),
                "Old raw prefix differs")
    # All validations finish before authority consumption. No rollback or retry
    # is implemented after any attempt; Main must inspect any partial outcome.
    exclusive_json(marker, {"plan": plan_binding, "script": bound_here(__file__),
                            "review_sha256": args.review_sha256,
                            "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            "retry_authorized": False})
    check_frozen()
    written = []
    for index, label in enumerate(FORMAL):
        target = resolve(label)
        require(target.read_bytes() == before[index], "Output changed before write")
        with target.open("r+b") as stream:
            require(stream.read() == before[index], "Open output differs")
            stream.seek(0)
            stream.write(after[index])
            stream.truncate()
            stream.flush()
            os.fsync(stream.fileno())
        require(target.read_bytes() == after[index], "Output postimage differs")
        written.append(bound_here(target))
    for bound in readset["files"]:
        if resolve(bound["path"]) not in [resolve(p) for p in FORMAL]:
            checked_bytes(bound)
    for label in readset["must_remain_absent"]:
        require(not resolve(label).exists(), "Expected absence changed after write")
    for inventory in readset["inventories"]:
        actual = sorted(str(p.resolve()) for p in
                        resolve(inventory["directory"]).glob(inventory["glob"])
                        if p.is_file())
        require(actual == inventory["paths"], "Postwrite inventory changed")
    exclusive_json(proof, {"plan": plan_binding, "script": bound_here(__file__),
                           "formal_outputs": written, "research_count": 514,
                           "groups": 242, "remaining": 486, "gate_satisfied": False,
                           "native_acceptance": False, "production_changes": False,
                           "retry_authorized": False})


if __name__ == "__main__":
    main()

"""Unexecuted draft. Requires a separately reviewed exact plan and one-use Main grant."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = Path(__file__).resolve().parent
PLAN = PRIVATE / "batch-121-formal-append-plan-20261110.json"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":")).encode())


def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def binding(path):
    p = resolve(path)
    raw = p.read_bytes()
    label = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
    return {"path": label, "sha256": digest(raw), "bytes": len(raw)}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def exclusive_json(path, value):
    with path.open("x", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())


def encode_append(old, tail, value, indentation):
    require(old.endswith(tail), "Exact baseline tail changed")
    encoded = json.dumps(value, ensure_ascii=False, indent=2)
    encoded = "\n".join(" " * indentation + line for line in encoded.splitlines()).encode()
    return old[:-len(tail)] + b",\n" + encoded + tail


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-sha256", required=True)
    parser.add_argument("--review-bytes", type=int, required=True)
    args = parser.parse_args()
    frozen_plan_binding = binding(PLAN)
    plan = json.loads(PLAN.read_text())
    require(plan["batch"] == 121, "Wrong plan")
    require(plan["allowed_formal_paths_now"] == [], "Draft permission boundary changed")
    require(binding(__file__) == plan["unexecuted_append_script"], "Script changed")
    review_path = resolve(plan["future_Main_exact_plan_review_path"])
    rb = binding(review_path)
    require(rb["sha256"] == args.review_sha256 and rb["bytes"] == args.review_bytes,
            "Actual independent Main review binding differs")
    review = json.loads(review_path.read_text())
    require(review.get("append_authorized") is True and
            review.get("single_execution_granted") is True,
            "No explicit one-use Main grant")
    require(review.get("plan") == binding(PLAN) and
            review.get("script") == binding(__file__), "Review does not bind exact plan/script")
    allowed = plan["allowed_formal_paths_after_later_explicit_authorization"]
    require(review.get("allowed_formal_paths") == allowed and
            review.get("production_authorized") is False, "Wrong write scope")
    expected_paths = ["docs/cod4/audit-20261022/immune-feedback-research/" + name
                      for name in ("reviewed.json", "semantic-dedup.json", "progress.json")]
    require(allowed == expected_paths, "Only three exact formal outputs may change")
    marker = resolve(plan["one_time_start_marker"])
    proof = resolve(plan["proof_path"])
    require(not marker.exists() and not proof.exists(), "One-use marker/proof already exists")
    inputs = plan["all_current_input_bindings"]
    require(len({b["path"] for b in inputs}) == len(inputs), "Duplicate frozen inputs")
    for b in inputs:
        require(binding(b["path"]) == b, "Frozen input drift: " + b["path"])
    old_raw = {name: resolve(b["path"]).read_bytes() for name, b in plan["baseline"].items()}
    old_rows = json.loads(old_raw["reviewed.json"])
    old_dedup = json.loads(old_raw["semantic-dedup.json"])
    require(len(old_rows) == 508 and len(old_dedup["groups"]) == 236, "Baseline count changed")
    require([x["id"] for x in old_rows] == plan["old508_complete_object_id_order"], "Old order changed")
    require({x["id"]: canonical(x) for x in old_rows} == plan["old508_complete_object_canonical_hashes"],
            "Old complete objects changed")
    require([canonical(g) for g in old_dedup["groups"]] == plan["old_dedup_group_canonical_hashes"],
            "Old complete groups changed")
    entry, group = plan["entry"], plan["dedup_group"]
    require(entry["id"] not in {x["id"] for x in old_rows}, "Entry already present")
    require(canonical(entry) == plan["planned_entry_canonical_sha256"] and
            canonical(group) == plan["planned_group_canonical_sha256"], "New whole objects changed")
    outputs = {
        "reviewed.json": encode_append(old_raw["reviewed.json"], b"\n]\n", entry, 2),
        "semantic-dedup.json": encode_append(old_raw["semantic-dedup.json"], b"\n  ]\n}\n", group, 4),
    }
    progress = old_raw["progress.json"]
    for key, old, new in (("reviewed_effective_semantic_dedup", 508, 509), ("remaining", 492, 491)):
        before = f'"{key}": {old}'.encode()
        after = f'"{key}": {new}'.encode()
        require(progress.count(before) == 1, "Progress literal is not unique")
        progress = progress.replace(before, after, 1)
    outputs["progress.json"] = progress
    before_progress = json.loads(old_raw["progress.json"])
    expected_progress = dict(before_progress, reviewed_effective_semantic_dedup=509, remaining=491)
    require(json.loads(progress) == expected_progress and
            expected_progress["formal_design_gate_satisfied"] is False, "Unexpected progress change")
    for name, raw in outputs.items():
        require(digest(raw) == plan["planned_output_sha256"][name] and
                len(raw) == plan["planned_output_byte_lengths"][name], "Unexpected future bytes")
    require(json.loads(outputs["reviewed.json"]) == old_rows + [entry], "Old rows not preserved")
    new_dedup = json.loads(outputs["semantic-dedup.json"])
    require(new_dedup == dict(old_dedup, groups=old_dedup["groups"] + [group]), "Old groups not preserved")
    nonformal = [b for b in inputs if b["path"] not in allowed]
    started = {"status": "permanently-consumed-once-started", "batch": 121,
               "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "plan": binding(PLAN), "script": binding(__file__), "Main_exact_plan_review": rb,
               "all_prewrite_inputs_matched": len(inputs), "retry_or_rebase_allowed": False}
    require(binding(PLAN) == frozen_plan_binding and binding(review_path) == rb,
            "Plan or Main review drift before marker")
    for b in inputs:
        require(binding(b["path"]) == b, "Frozen input drift immediately before marker: " + b["path"])
    exclusive_json(marker, started)
    result = dict(started, status="failed-after-marker-permanently-consumed",
                  allowed_formal_paths=allowed, nonformal_input_count=len(nonformal))
    try:
        for name, raw in outputs.items():
            b = plan["baseline"][name]
            require(binding(b["path"]) == b, "Formal drift after marker: " + name)
            with resolve(b["path"]).open("r+b") as out:
                out.seek(0)
                out.write(raw)
                out.truncate()
                out.flush()
                os.fsync(out.fileno())
        actual_outputs = {name: binding(b["path"]) for name, b in plan["baseline"].items()}
        for name, b in actual_outputs.items():
            require(b["sha256"] == plan["planned_output_sha256"][name] and
                    b["bytes"] == plan["planned_output_byte_lengths"][name], "Postwrite bytes differ")
        require(binding(PLAN) == frozen_plan_binding and binding(review_path) == rb,
                "Plan or Main review drift after write")
        for b in nonformal:
            require(binding(b["path"]) == b, "Nonformal input changed: " + b["path"])
        context = json.loads(resolve(plan["current508_ecology51_context"]["path"]).read_text())
        master = json.loads(resolve(context["current_ecology_master"]["path"]).read_text())
        require({x["id"]: canonical(x) for x in master["accepted"]} ==
                context["all51_complete_accepted_master_object_canonical_hashes"], "Ecology objects changed")
        result.update(status="actual-three-output-append-awaiting-independent-Main-delta-review",
                      actual_outputs=actual_outputs, all_nonformal_inputs_unchanged=True,
                      old508_complete_objects_order_preserved=True, old236_complete_groups_preserved=True,
                      old_raw_prefixes_preserved=True, complete51_ecology_objects_and_receipts_preserved=True,
                      current_formal_count=509, current_groups=237, current_shortfall=491,
                      gate_met=False, new_native_acceptance=0, new_ecology_credit=0,
                      production_changes=0, game_starts=0, checklist_deletions=0,
                      all_prewrite_bindings=inputs, actual_marker=binding(marker))
    except Exception as exc:
        result["error"] = str(exc)
        exclusive_json(proof, result)
        raise
    exclusive_json(proof, result)


if __name__ == "__main__":
    main()

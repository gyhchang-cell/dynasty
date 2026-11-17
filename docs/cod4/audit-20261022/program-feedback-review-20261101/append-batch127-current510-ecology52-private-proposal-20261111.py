"""NEW CURRENT510/ECOLOGY52 PRIVATE UNEXECUTED proposal. Not the stale421 plan.
No current grant, token, readiness assertion or execution is supplied.

Future use requires independent exact Main review and a separate explicit one-use
instruction. Three writes are sequential, not atomic; failure consumes the grant.
Never retry, roll back automatically, or rebase any ecology proposal.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PRIVATE = Path(__file__).resolve().parent
PLAN = PRIVATE / "batch-127-current510-ecology52-private-append-plan-20261111.json"
MAIN = "01a16364-cac0-7ca2-a042-a5312781ca34"
FORMAL = ["docs/cod4/audit-20261022/immune-feedback-research/" + name
          for name in ("reviewed.json", "semantic-dedup.json", "progress.json")]


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


def binding(label):
    path = resolve(label)
    raw = path.read_bytes()
    name = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    return {"path": name, "sha256": digest(raw), "bytes": len(raw)}


def load(bound):
    require(binding(bound["path"]) == bound, "Bound file changed: " + bound["path"])
    return json.loads(resolve(bound["path"]).read_bytes())


def exclusive_json(path, value):
    with path.open("x", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())


def append_bytes(raw, tail, value, indent):
    require(raw.endswith(tail), "Formal tail changed")
    text = json.dumps(value, ensure_ascii=False, indent=2)
    added = "\n".join(" " * indent + line for line in text.splitlines()).encode()
    return raw[:-len(tail)] + b",\n" + added + tail


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-sha256", required=True)
    parser.add_argument("--review-bytes", type=int, required=True)
    args = parser.parse_args()
    plan_binding = binding(PLAN)
    plan = json.loads(PLAN.read_bytes())
    require(plan["batch"] == 127 and plan["allowed_formal_paths_now"] == [], "Wrong proposal")
    require(binding(__file__) == plan["unexecuted_append_script"], "Script drift")
    require(plan["allowed_formal_paths_after_later_explicit_authorization"] == FORMAL, "Scope drift")
    review_path = resolve(plan["future_Main_exact_plan_review_path"])
    review_binding = binding(review_path)
    require(review_binding["sha256"] == args.review_sha256 and
            review_binding["bytes"] == args.review_bytes, "Exact Main review differs")
    review = load(review_binding)
    require(review.get("reviewer_thread_id") == MAIN and
            review.get("append_authorized") is True and
            review.get("single_execution_granted") is True and
            review.get("production_authorized") is False, "No exact one-use Main grant")
    require(review.get("plan") == plan_binding and
            review.get("script") == binding(__file__) and
            review.get("allowed_formal_paths") == FORMAL, "Grant scope/bindings differ")
    marker, proof = resolve(plan["one_time_start_marker"]), resolve(plan["proof_path"])
    require(not marker.exists() and not proof.exists(), "Attempt already consumed")
    readset = load(plan["current_readset"])
    inputs = readset["files"]
    require(len(inputs) == plan["frozen_input_count"] and 421 <= len(inputs) <= 1024,
            "Frozen current readset count changed")
    def check_inventories():
        for inventory in readset["inventories"]:
            actual = sorted(str(p.resolve()) for p in resolve(inventory["directory"]).glob(inventory["glob"])
                            if p.is_file())
            require(actual == inventory["paths"], "Current ecology inventory drift")
    check_inventories()
    by_path = {b["path"]: b for b in inputs}
    require(len(by_path) == len(inputs), "Duplicate frozen inputs")
    historical = load(plan["historical_stale_plan"])
    for key, count in (("carried371_prior_nonformal_bindings", 371),
                       ("carried339_old_nonformal_bindings", 339)):
        require(len(plan[key]) == count and all(by_path.get(b["path"]) == b for b in plan[key]),
                "Current complete nonformal coverage reduced")
        require(plan["historical_" + key] == historical[key] and
                [b["path"] for b in plan[key]] == [b["path"] for b in historical[key]],
                "Historical whole binding list or current coverage changed")
    actual_supersessions = [{"before": b, "after": by_path[b["path"]]}
                            for b in historical["all_current_input_bindings"]
                            if b != by_path[b["path"]]]
    require(actual_supersessions == readset["historical421_five_supersessions"] and
            len(actual_supersessions) == 5, "Historical input changes differ")
    for bound in inputs:
        require(binding(bound["path"]) == bound, "Frozen input drift: " + bound["path"])
    old_raw = {name: resolve(b["path"]).read_bytes() for name, b in plan["baseline"].items()}
    require([b["path"] for b in plan["baseline"].values()] == FORMAL, "Baseline scope differs")
    for name, bound in plan["baseline"].items():
        require(binding(bound["path"]) == bound and by_path.get(bound["path"]) == bound,
                "Formal preimage binding changed")
        require(resolve(plan["private_preimages"][name]["path"]).read_bytes() == old_raw[name],
                "Private preimage differs")
    rows, dedup = json.loads(old_raw["reviewed.json"]), json.loads(old_raw["semantic-dedup.json"])
    require(len(rows) == 510 and len(dedup["groups"]) == 238, "Baseline counts changed")
    require([x["id"] for x in rows] == plan["old510_complete_object_id_order"] and
            {x["id"]: canonical(x) for x in rows} == plan["old510_complete_object_canonical_hashes"],
            "Old510 whole objects/order changed")
    require([canonical(x) for x in dedup["groups"]] == plan["old238_complete_group_canonical_hashes"],
            "Old238 whole groups changed")
    candidate, main_review = load(plan["proposal"]), load(plan["Main_receipt"])
    ack, ack_review = load(plan["actual_author_confirmation"]), load(plan["Main_actual_author_ack_review"])
    entry, group = plan["entry"], plan["dedup_group"]
    require(ack["complete_original_candidate_preserved"] == candidate and
            ack["complete_Main_review_preserved"] == main_review and
            main_review["original_candidate_judgment_preserved"] == candidate, "Historical whole lost")
    require(entry["complete_original_candidate"] == candidate and
            entry["complete_Main_whole_review"] == main_review and
            entry["complete_actual_author_confirmation"] == ack and
            entry["complete_Main_ACK_closure"] == ack_review, "Entry whole evidence lost")
    require(entry["author_observations"] == candidate["full_chain_observation"] and
            len(entry["author_observations"]) == 15 and
            entry["author_limitations"] == candidate["limitations"] and len(entry["author_limitations"]) == 15 and
            entry["main_independent_findings"] == main_review["Main_findings"] and
            len(entry["main_independent_findings"]) == 20 and
            entry["main_preappend_limits_verbatim"] == main_review["Main_limits"] and
            len(entry["main_preappend_limits_verbatim"]) == 15, "Original15/15 or Main20/15 reduced")
    require(entry["actual_author_acknowledgment"] == ack["specific_Main_finding_responses"] and
            entry["actual_author_limit_acknowledgment"] == ack["specific_Main_limit_responses"],
            "Actual35 author responses lost")
    for key, original, label in (("specific_Main_finding_responses", "Main_findings", "Main_original_finding"),
                                  ("specific_Main_limit_responses", "Main_limits", "Main_original_limit")):
        require(len(ack[key]) == len(main_review[original]) and
                all(response[label] == text and bool(response["actual_author_response"].strip())
                    for response, text in zip(ack[key], main_review[original])), "ACK mismatch")
    require(ack_review["maximum_whole_research_credit"] == 1 and
            ack_review["formal_applied_credit"] == 0 and
            ack_review["append_execution_authorized"] is False, "Preformal closure differs")
    key = entry["semantic_dedup_key"]
    require(entry["id"] == key == candidate["semantic_dedup_key"] == group["credited_chain"] and
            all(x["id"] != key and x.get("semantic_dedup_key") != key for x in rows), "Entry conflict")
    require(all(g.get("family") != group["family"] and g.get("credited_chain") != key and
                key not in g.get("credited_chains", []) for g in dedup["groups"]), "Dedup conflict")
    require(canonical(entry) == plan["planned_entry_canonical_sha256"] and
            canonical(group) == plan["planned_group_canonical_sha256"], "Proposed objects drift")
    outputs = {"reviewed.json": append_bytes(old_raw["reviewed.json"], b"\n]\n", entry, 2),
               "semantic-dedup.json": append_bytes(old_raw["semantic-dedup.json"], b"\n  ]\n}\n", group, 4)}
    progress = old_raw["progress.json"]
    for name, before, after in (("reviewed_effective_semantic_dedup", 510, 511), ("remaining", 490, 489)):
        old_literal, new_literal = f'"{name}": {before}'.encode(), f'"{name}": {after}'.encode()
        require(progress.count(old_literal) == 1, "Progress literal not unique")
        progress = progress.replace(old_literal, new_literal, 1)
    outputs["progress.json"] = progress
    require(json.loads(progress) == dict(json.loads(old_raw["progress.json"]),
                                        reviewed_effective_semantic_dedup=511, remaining=489) and
            json.loads(progress)["formal_design_gate_satisfied"] is False, "Progress scope changed")
    require(json.loads(outputs["reviewed.json"]) == rows + [entry] and
            json.loads(outputs["semantic-dedup.json"]) == dict(dedup, groups=dedup["groups"] + [group]),
            "Old objects/order not preserved")
    for name, raw in outputs.items():
        require(digest(raw) == plan["planned_output_sha256"][name] and
                len(raw) == plan["planned_output_byte_lengths"][name] and
                resolve(plan["private_postimages"][name]["path"]).read_bytes() == raw,
                "Exact proposed postimage differs")
    context = load(plan["current510_ecology52_context"])
    master = load(context["current_ecology_master"])
    validation = load(context["current_ecology_validation"])
    closure = load(context["EA53_actual52_independent_review"])
    require(closure["formal_ecology_count"] == 52 and closure["gate_met"] is False and
            closure["reviewer_thread_id"] == MAIN and closure["exit_code"] == 0 and
            closure["timed_out"] is False, "Ecology52 Main actual closure differs")
    require(len(master["accepted"]) == len(validation["receipt_inputs"]) == 52 and
            master["accepted"] == context["complete52_accepted_master_objects"] and
            validation["receipt_inputs"] == context["complete52_validation_result_objects"],
            "Ecology52 whole results changed")
    require({x["id"]: canonical(x) for x in master["accepted"]} ==
            context["all52_complete_accepted_master_object_canonical_hashes"], "Ecology changed")
    require({str(resolve(b["path"])) for b in closure["actual_five_outputs"]} ==
            {str(resolve(x["before"]["path"])) for x in actual_supersessions},
            "Supersessions not the exact accepted five ecology outputs")
    for accepted in closure["actual_five_outputs"]:
        actual = binding(accepted["path"])
        require(actual["sha256"] == accepted["sha256"] and actual["bytes"] == accepted["bytes"] and
                by_path.get(actual["path"]) == actual, "Current ecology five differs from Main closure")
    require(len(context["all52_actual_ecology_receipt_bindings"]) == 52, "Receipt coverage reduced")
    for bound in context["all52_actual_ecology_receipt_bindings"]:
        require(binding(bound["path"]) == bound and by_path.get(bound["path"]) == bound,
                "Ecology receipt changed")
    require(entry["current510_ecology52_context"] == plan["current510_ecology52_context"],
            "New entry current context differs")
    require(binding(plan["current_readset"]["path"]) == plan["current_readset"], "Readset drift")
    check_inventories()
    require(binding(PLAN) == plan_binding and binding(review_path) == review_binding, "Review/plan drift")
    for bound in inputs:
        require(binding(bound["path"]) == bound, "Pre-marker drift: " + bound["path"])
    started = {"status": "permanently-consumed-once-started", "batch": 127,
               "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "plan": plan_binding, "script": binding(__file__), "Main_exact_plan_review": review_binding,
               "all_prewrite_inputs_matched": len(inputs), "retry_or_rebase_allowed": False}
    exclusive_json(marker, started)
    result = dict(started, status="failed-after-marker-permanently-consumed", allowed_formal_paths=FORMAL)
    try:
        for name, raw in outputs.items():
            bound = plan["baseline"][name]
            require(binding(bound["path"]) == bound, "Formal drift after marker")
            with resolve(bound["path"]).open("r+b") as out:
                out.write(raw)
                out.truncate()
                out.flush()
                os.fsync(out.fileno())
        actual_outputs = {name: binding(b["path"]) for name, b in plan["baseline"].items()}
        for name, b in actual_outputs.items():
            require(b["sha256"] == plan["planned_output_sha256"][name] and
                    b["bytes"] == plan["planned_output_byte_lengths"][name], "Postwrite mismatch")
        require(binding(PLAN) == plan_binding and binding(review_path) == review_binding, "Postwrite review drift")
        for bound in inputs:
            if bound["path"] not in FORMAL:
                require(binding(bound["path"]) == bound, "Nonformal drift: " + bound["path"])
        check_inventories()
        result.update(status="actual-three-output-append-awaiting-independent-Main-delta-review",
                      actual_outputs=actual_outputs, all_nonformal_inputs_unchanged=True,
                      old510_complete_objects_order_preserved=True, old238_complete_groups_preserved=True,
                      old_raw_prefixes_preserved=True, complete52_ecology_objects_and_receipts_preserved=True,
                      current_formal_count=511, current_groups=239, current_shortfall=489, gate_met=False,
                      new_native_acceptance=0, new_ecology_credit=0, production_changes=0,
                      game_starts=0, checklist_deletions=0, all_prewrite_bindings=inputs,
                      actual_marker=binding(marker))
    except Exception as exc:
        result["error"] = str(exc)
        exclusive_json(proof, result)
        raise
    exclusive_json(proof, result)


if __name__ == "__main__":
    main()

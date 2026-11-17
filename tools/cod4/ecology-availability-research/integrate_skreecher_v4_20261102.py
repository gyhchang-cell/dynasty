"""Coordinator's one-shot installation of the actually reviewed v4 delta.

This publishes a zero-credit proposal and evidence tools, never an accepting
reviewer receipt. Existing proposal records and reviewer namespaces stay intact.
"""
import ast
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools/cod4/ecology-availability-research"
DOCS = ROOT / "docs/cod4/audit-20261022/ecology-availability-research"
DRAFT = TOOLS / ".work/skreecher-v4-draft"
sys.path.insert(0, str(TOOLS))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def definitions(raw):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(raw).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


manifest_raw = (DRAFT / "draft-manifest.json").read_bytes()
manifest = json.loads(manifest_raw)
validator, summary = TOOLS / "receipt_validation.py", TOOLS / "summarize.py"
old_validator, old_summary = validator.read_bytes(), summary.read_bytes()
assert sha(old_validator) == manifest["baseline_validator_sha256"] == "b041efbc7006e9ec68e203aade707c791b0a8d635c983adec22757f6f20b33b4"
assert sha(old_summary) == manifest["baseline_summarize_sha256"] == "e13eef8080091ddf905920f69c7f117fa32a3f481d6347b307b430088710a15a"
master_before = (DOCS / "master-acceptance-ledger.json").read_bytes()
assert sha(master_before) == manifest["baseline_master_sha256"]
assert json.loads(master_before)["independently_accepted"] == 15
for a in manifest["artifacts"]:
    assert sha((DRAFT / a["path"]).read_bytes()) == a["sha256"], a["path"]
new_validator = (DRAFT / "receipt_validation_v4.py").read_bytes()
new_summary = (DRAFT / "summarize_v4.py").read_bytes()
assert sha(new_validator) == "7e6f0121d8b572a4dafb296b224b0bff004c895a968802fbd3b49756a8b332fc"
assert sha(new_summary) == "36f74cf758429e4751945d1822238e5e4b89efada3922953754bea8fe20af8a6"
old_defs, new_defs = definitions(old_validator), definitions(new_validator)
preserved = ["InvalidReceipt", "require", "local_path", "Snapshot", "validate_source", "extra_support", "general_context", "resolve"]
assert all(old_defs[n] == new_defs[n] for n in preserved)
old = load("_ea16_pre_install_v3", validator)
new = load("_ea16_reviewed_draft_v4", DRAFT / "receipt_validation_v4.py")
assert old.AUTHORIZED["coordinator"] == new.AUTHORIZED["coordinator"]
assert old.AUTHORIZED["carson"] == new.AUTHORIZED["carson"]
assert {k:v for k,v in old.AUTHORIZED["general"].items() if k != "allowed_ids"} == {k:v for k,v in new.AUTHORIZED["general"].items() if k != "allowed_ids"}
assert old.AUTHORIZED["general"]["allowed_ids"] == {"EA-0017"}
assert new.AUTHORIZED["general"]["allowed_ids"] == {"EA-0016", "EA-0017"}

preserved_raw = (DRAFT / "preserved-existing-records.json").read_bytes()
preservation = json.loads(preserved_raw)
by = {}
for desc in preservation["batches"]:
    p = ROOT / desc["path"]
    assert sha(p.read_bytes()) == desc["sha256"]
    for rec in json.loads(p.read_text())["records"]:
        assert rec["id"] not in by
        by[rec["id"]] = (p, rec)
assert len(by) == 15
for desc in preservation["records"]:
    rec = by[desc["id"]][1]
    assert sha(json.dumps(rec, ensure_ascii=False, sort_keys=True).encode()) == desc["canonical_record_sha256"]

copies = []
for s in manifest["source_stage"]:
    original, staged, destination = (ROOT / s[k] for k in ("original", "staged", "destination"))
    assert destination.resolve().is_relative_to((TOOLS / "sources/AlexModGuy__AlexsMobs").resolve())
    data = staged.read_bytes()
    assert data == original.read_bytes() and sha(data) == s["sha256"]
    if destination.exists():
        assert destination.read_bytes() == data
    else:
        copies.append((destination, data))
assert len(copies) == 3
batch_path = DOCS / "batch-012.json"
receipt_path = DOCS / "independent-reviews/general-EA0016.json"
protocol_path = DOCS / "AGGREGATION-PROTOCOL-v4.md"
report_path = DOCS / "coordinator-v4-install-review-20261102.json"
assert not any(p.exists() for p in [batch_path, receipt_path, protocol_path, report_path])
batch = json.loads((DRAFT / "batch-012.json").read_text())
assert len(batch["records"]) == 1 and batch["records"][0]["id"] == "EA-0016"
batch["status"] = "ACTUAL_REVIEWED_PROPOSAL_PENDING_SEPARATE_AUTHORIZED_RECEIPT_ZERO_CREDIT"
batch["coordinator_publication"] = {
    "thread_id": "01a16364-cac0-7ca2-a042-a5312781ca34",
    "draft_path": str((DRAFT / "batch-012.json").relative_to(ROOT)),
    "draft_sha256": manifest["draft_batch_sha256"],
    "record_unchanged_from_actual_reviewed_draft": True,
    "accepted_credit": 0,
}
batch_raw = encode(batch)

protocol = """# 独立接受汇总协议 v4：Skreecher 精确单项扩展

保留 v3 原文与旧收据。用户已授权现有对话按专业持续工作；主协调实际读完 EA16 全链及真实独立审阅、floor 澄清，并审阅此次隔离代码增量后，核定以下有限扩展，不新建对话或绕过配额。

- `general` 仍是实际既有对话 `01a12516-2eaf-73e2-b615-20f8b422158c`；允许 ID 仅从 EA17 扩为 EA16、EA17，原精确标签、decision、作者独立性不变。coordinator、Carson 规则不变，不冒充其身份。
- EA17 原 `general_context` 与源验证、路径限制、快照、额外支持和冲突/去重函数 AST 保持不变；EA16 独立函数精确固定原 proposal、完整 independent review、不可变 floor clarification 三份路径和完整 SHA，拒绝候选 ID。EA16 本来没有候选号，不得编造。
- EA16 `batch-012.json` 只形成一项零信用待接受记录。15 mod 范围逐项重算原字节/正式副本、固定 Git blob/tree/metadata/revision/excerpt/URL；完整24范围与真实审阅逐项匹配，9 native 范围/4文件以原 Forge sources Jar SHA 和 entry 字节复核，全部支持0。
- floor 澄清具有强制身份绑定：向下搜索后没有 sturdy-floor 拒绝门，未找到支撑仍可能尝试生成；新 Warden 的初始 target/anger 接收者是 Skreecher 自身。尝试位、声音和非空 create 均不是实际加入证据。
- 正式独立接受收据必须由实际 General 审阅者另写、绑定当前批次完整 SHA。隔离草稿内存正例不形成实际收据；synthetic Snapshot 禁止发布。主协调不代写 General/Carson 身份。
- 同 ID 多收据最多1，拒绝/不完整/冲突归0，跨 ID 同 semantic key归0。校验器核证据身份和字节，语义独立仍由实际阅读者判断。27/24/15/9 等范围/文件数均不是研究数量。

本次仅安装研究证据工具和零信用提案，不批准生产、cap/概率/分类、游戏、资产或清单删除。原始 runtime01–04、24/30出生+9/10拾取及原失败断言不变；不创建定时任务。旧协议中 EA15/16 均为未执行草稿的描述是历史状态，本协议仅更新实际 EA16，EA15 未正式形成。
"""

# All input/identity checks above precede mutations. Only these three absent
# evidence copies, the two reviewed tools, a proposed batch and protocol change.
for p, data in copies:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("xb") as f:
        f.write(data)
assert validator.read_bytes() == old_validator and summary.read_bytes() == old_summary
validator.write_bytes(new_validator)
summary.write_bytes(new_summary)
with batch_path.open("xb") as f:
    f.write(batch_raw)
with protocol_path.open("x") as f:
    f.write(protocol)

actual = load("_ea16_installed_v4", validator)
by["EA-0016"] = (batch_path, batch["records"][0])
accepted, validation, snap = actual.aggregate(by)
snap.stable()
assert len(accepted) == 15 and not validation["conflicts"]
assert validation["counts"]["invalid_or_nonaccepting"] == 0
assert not receipt_path.exists()
assert (DOCS / "master-acceptance-ledger.json").read_bytes() == master_before
assert {r['id']: r for r in accepted} == {r['id']: r for r in json.loads(master_before)['accepted']}
for desc in preservation["batches"]:
    assert sha((ROOT / desc["path"]).read_bytes()) == desc["sha256"]
report = {
    "recorded_utc": datetime.now(timezone.utc).isoformat(),
    "status": "COORDINATOR_ACTUAL_DELTA_REVIEW_AND_INSTALL_PASS_NO_EA16_ACCEPTANCE_YET",
    "actual_code_read": ["whole new general_skreecher_context delta", "complete validator dispatch/schema delta", "whole summary delta", "whole packaging builder", "whole memory auditor", "protocol/manifest/formal observation and limits"],
    "source_read_reused": "Skreecher complete24 source ranges actually read earlier this turn; this code review and hashes confer no new source reading credit",
    "ast_preserved_definitions": preserved,
    "coordinator_carson_policies_unchanged": True,
    "general_only_id_scope_extension": ["EA-0016", "EA-0017"],
    "existing_accepted_records_identical": 15,
    "installed_tools": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p.read_bytes())} for p in [validator, summary]],
    "formal_batch": {"path": str(batch_path.relative_to(ROOT)), "sha256": sha(batch_raw), "accepted_credit": 0},
    "protocol": {"path": str(protocol_path.relative_to(ROOT)), "sha256": sha(protocol_path.read_bytes())},
    "new_same_fixed_source_copies": [{"path": str(p.relative_to(ROOT)), "sha256": sha(data), "research_credit": 0} for p, data in copies],
    "draft_manifest_sha256": sha(manifest_raw),
    "peer_memory_case_report": {"path": str((DRAFT / "memory-counterexample-audit.json").relative_to(ROOT)), "sha256": sha((DRAFT / "memory-counterexample-audit.json").read_bytes()), "actual_case_implementation_read": True, "case_count": 39, "research_credit": 0, "rerun_claimed": False},
    "actual_aggregate_replayed_once_after_install": 15,
    "actual_master_unchanged_sha256": sha(master_before),
    "formal_acceptance_receipts_written": 0, "research_credit_applied": 0,
    "upstream_or_Java_game_execution": False, "production_changes": 0,
    "checklist_deletions": 0, "duration_hours_claimed": 0,
}
with report_path.open("xb") as f:
    f.write(encode(report))
print(json.dumps({"report": str(report_path.relative_to(ROOT)), "report_sha256": sha(report_path.read_bytes()),
                  "batch_sha256": sha(batch_raw), "actual_accepted_unchanged": 15,
                  "EA16_applied_credit": 0, "new_source_copies": len(copies)}))

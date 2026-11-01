"""Consolidate manual family/applicability proposals, never grant the 1000 gate."""
import json
from pathlib import Path
from datetime import datetime, timezone

D = Path(__file__).resolve().parent
groups = {}
stage_proposals = 0
for path in sorted(D.glob('review-batch-*.json')):
    batch = json.loads(path.read_text())
    stage_proposals += batch['proposed_distinct_design_families']
    for r in batch['rows']:
        family = r['semantic_family']
        if family.startswith(('EXCLUDE', 'PENDING')):
            continue
        ref = r.get('reference_id', 'MC-TRIM-' + r.get('design', 'unknown'))
        g = groups.setdefault(family, dict(family=family, representative=r.get('family_representative', ref), members=[],
            observation_scope=r['scope'], new_accepted_credit=0, novelty='PENDING_GLOBAL_SEMANTIC_REVIEW',
            target_proposals=[], scope_proposals=[], source_batch_files=[]))
        g['members'].append(ref)
        g['source_batch_files'] = sorted(set(g['source_batch_files'] + [path.name]))
        g['target_proposals'] = sorted(set(g['target_proposals'] + r.get('applicable_targets_proposal', [])))

# Cross-task duplicates are reviewed as EQUIPMENT cases, not byte identity.
prior_rows = [r for name in ['prior-case-semantic-review.json', 'prior-batch07-semantic-review.json']
              for r in json.loads((D / name).read_text())['rows']]
for r in prior_rows:
    for g in groups.values():
        if r['current_reference'] not in g['members']:
            continue
        if r.get('slot_comparable') and r.get('novelty_decision') == 'ALREADY_STUDIED_EQUIPMENT_CASE':
            g['novelty'] = 'HISTORICALLY_STUDIED_EQUIPMENT_REUSE_NO_NEW_CREDIT'
        elif g['novelty'] != 'HISTORICALLY_STUDIED_EQUIPMENT_REUSE_NO_NEW_CREDIT':
            if r.get('novelty_decision') == 'HOLD_VARIANT_OR_VERSION_BINDING':
                g['novelty'] = 'HOLD_VARIANT_OR_VERSION_BINDING'
            else:
                g['novelty'] = 'HOLD_SLOT_MISMATCH' if 'prior_local_png' in r else 'HOLD_PRIOR_PNG_UNAVAILABLE'
        g.setdefault('prior_comparison_cases', []).append(r['case'])

# First two batches: specific motif applicability, not blanket allotment to every weapon.
assign = {
 'ornate-four-cardinal-open-center': ['zhenyue_blade'],
 'quadrant-linked-square-crosses': ['chiling_brush','supreme_sword'],
 'interlocked-square-guard': ['zhenyue_blade','supreme_sword'],
 'four-inward-triangles-with-discs': ['chiling_brush'],
 'concave-square-crossed-arcs': ['chiling_brush','supreme_sword'],
 'goety-orthogonal-square-lattice': ['chiling_brush','supreme_sword'],
 'goety-branched-cross-central-square': ['chiling_brush','leifu_staff'],
 'goety-nested-square-hanging-seal': ['chiling_brush','supreme_sword'],
 'malum-bent-flow': ['chiling_brush','leifu_staff'],
 'malum-fork-hook': ['chiling_brush','leifu_staff'],
 'malum-fire-s': ['leifu_staff'],
 'malum-stacked-bars': ['chiling_brush','leifu_staff'],
 'malum-closed-lozenge': ['chiling_brush','supreme_sword'],
 'malum-tree-fork': ['chiling_brush'],
 'malum-center-post-ward': ['zhenyue_blade','chiling_brush'],
}
mapping = json.loads((D.parent / 'identity-chapter-mapping-20261030.json').read_text())
targets = {r['id'].split(':')[1]:r for r in mapping['rows'] if r['kind']=='weapon'}
for family, g in groups.items():
    g['target_proposals'] = sorted(set(g['target_proposals'] + assign.get(family, [])))
    for target in g['target_proposals']:
        scope = targets[target]['researchScope']
        g['scope_proposals'] += scope.split('+')
    g['scope_proposals'] = sorted(set(g['scope_proposals']))
    if g['observation_scope'] in ['equipment_material', 'vanilla_armor_trim_composition']:
        g['application_level'] = 'MATERIAL_OR_TRIM_READING_ONLY_NOT_FULL_UV_CASE'
        g['equipment_uv_context_only'] = True
        g['scope_proposals'] = []
        g['limit_zh'] = '材料分区可借鉴；尚未逐套核实与本项目现有模型的完整 UV 对应。不把西式装备或原版纹饰自动充为完整帝王/护卫装备案例。'
    elif g['target_proposals']:
        g['application_level'] = 'PARTIAL_COMPOSITION_ONLY_NOT_TARGET_COMPLETE'
        g['limit_zh'] = '仅参考主干/负空间/方向组织。未绑定本项目纹样、动画或运行时，不证明完整学院身份设计；同族跨目标使用也不重复扩成多例。'
    else:
        g['application_level'] = 'GENERIC_CONTEXT_ONLY_NO_TARGET_GATE_PROPOSAL'
        g['limit_zh'] = '泛圆环、月轮或元素布局与当前具体身份关联不足，不分摊给每把武器凑数。'

scopes = ['school_talisman','school_archery','school_melee','imperial_guard','imperial_decal','equipment_uv']
scope_rows = []
for scope in scopes:
    proposed = [g['family'] for g in groups.values() if scope in g['scope_proposals']]
    scope_rows.append(dict(scope=scope, original_threshold=1000, threshold_waived=False,
        related_partial_composition_family_proposals=proposed, partial_proposals_count=len(proposed),
        new_accepted_visual_credit=0, historical_technical_ledger_untouched=True, production_gate_met=False,
        limitation='This is this batch visual contribution only, not replacement/reset of any existing accepted ledger; partial composition proposal count is not gate credit.'))
target_rows = []
for key, t in targets.items():
    target_rows.append(dict(id=t['id'], scope=t['researchScope'],
        current_motif_proposal=t['narrativeProposal']['motif'],
        related_partial_family_proposals=[g['family'] for g in groups.values() if key in g['target_proposals']],
        new_accepted_credit=0, original_assets_preserved=True, production_allowed=False))
out = dict(recorded_at=datetime.now(timezone.utc).isoformat(),
    reviewer='same agent/chats own manual second pass; no independent acceptance claimed',
    purpose='Semantic groups and applicability before future production; source image hashes are provenance only.',
    original_stage_family_proposal_sum=stage_proposals, consolidated_family_names=len(groups),
    historically_reused_equipment_family_names=sum(g['novelty'].startswith('HISTORICALLY') for g in groups.values()),
    scope_contribution=scope_rows, targets=target_rows, families=list(groups.values()),
    accepted_new_visual_credit=0, production_gate_met=False,
    boundaries=['No resetting or merging original six scope gates.', 'No 227 Java methods converted into art cases.',
                'No icons, layers, recolors, UV screenshots or CTM fragments separately credited as the same design.',
                'No automatic acceptance from number of family strings. Further historical semantic review remains.'])
(D/'semantic-applicability-register.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(dict(consolidated_family_names=len(groups), historical_reuse_families=out['historically_reused_equipment_family_names'],
    partial_scope_proposals={r['scope']:r['partial_proposals_count'] for r in scope_rows}, accepted_credit=0), ensure_ascii=False))

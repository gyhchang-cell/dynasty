"""Main source review receipt only; never assigns a formal ecology ID."""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/Users/a15356015027/Desktop/dynasty')
BASE = ROOT / 'docs/cod4/audit-20261022/ecology-availability-research'
P = BASE / 'general-zombie-reinforcement-whole-policy-proposal-20261109.json'
OUT = BASE / 'coordinator-zombie-reinforcement-whole-policy-review-20261109.json'
assert not OUT.exists()
sha = lambda b: hashlib.sha256(b).hexdigest()
canon = lambda o: sha(json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
load = lambda p: json.loads(p.read_text())
def binding(p):
    return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}

assert sha(P.read_bytes()) == 'c9a2f7253789a3c35b2da7f3712eb2f4c3285de6a978a5613502d828eef5bf37'
d = load(P)
assert d['formal_candidate_id'] is None and d['accepted_credit'] == 0
archive = ROOT / d['source_archive']
assert sha(archive.read_bytes()) == d['source_archive_sha256']
ranges = []
positions = set()
with zipfile.ZipFile(archive) as z:
    for a in d['actual_native_read_ranges']:
        raw = z.read(a['entry'])
        assert sha(raw) == a['entry_sha256']
        lines = raw.decode().splitlines(keepends=True)
        lo,hi = a['lines']
        excerpt = ''.join(lines[lo-1:hi])
        assert excerpt == a['raw_excerpt_utf8'] and sha(excerpt.encode()) == a['raw_excerpt_sha256']
        assert not a['full_file'] or (lo == 1 and hi == len(lines))
        positions.update((a['entry'],i) for i in range(lo,hi+1))
        ranges.append({k:a[k] for k in ['entry','entry_sha256','lines','full_file','raw_excerpt_sha256']})
assert len(ranges) == 25 and len(positions) == 1674
comparators = []
for a in d['prior_whole_decisions']:
    p = ROOT / a['path']
    assert sha(p.read_bytes()) == a['sha256']
    record = next(x for x in load(p)['records'] if x['id'] == a['id'])
    assert canon(record) == a['canonical_record_sha256']
    fields = {k:record[k] for k in ['semantic_key','observation','application','limits']}
    assert fields == a['complete_selected_semantic_judgment_fields']
    comparators.append({'id':a['id'],'source':binding(p),'record_canonical_sha256':canon(record),
        'actual_full_selected_judgment_fields_read':fields,'old_original_source_chain_reread':False,
        'new_credit':0})
shulker = load(BASE/'batch-032.json')['records'][0]
assert shulker['id'] == 'EA-0041'
comparators.append({'id':'EA-0041','source':binding(BASE/'batch-032.json'),
    'record_canonical_sha256':canon(shulker),'actual_full_selected_judgment_fields_read':{k:shulker[k] for k in ['semantic_key','observation','application','limits']},
    'old_original_source_chain_reread':False,'new_credit':0})
migration = ROOT/d['migration_ledger']['path']
assert sha(migration.read_bytes()) == d['migration_ledger']['sha256']
owner_ids = {x['candidate_id'] for x in d['existing_global_migration_whole_owners']}
rows = {x['candidate_id']:x for x in map(json.loads,migration.read_text().splitlines()) if x['candidate_id'] in owner_ids}
for a in d['existing_global_migration_whole_owners']:
    row = rows[a['candidate_id']]
    assert canon(row) == a['canonical_complete_row_sha256']
    assert {k:v for k,v in row.items() if k != 'evidence'} == a['actual_current_non_evidence_decision_fields']
master = load(BASE/'master-acceptance-ledger.json')
assert master['independently_accepted'] == 45 and len(master['accepted']) == 45
index = {x['id']:x for x in d['current45_accepted_semantic_index']}
assert set(index) == {x['id'] for x in master['accepted']}
for a in master['accepted']:
    b = index[a['id']]
    assert (a['semantic_key'],a['batch'],a['batch_sha256']) == (b['semantic_key'],b['batch'],b['batch_sha256'])
    p = ROOT/a['batch']; assert sha(p.read_bytes()) == a['batch_sha256']
    record = next(x for x in load(p)['records'] if x['id'] == a['id'])
    assert canon(record) == b['canonical_record_sha256']

findings = [
 'At most one related whole per-actor damage-conditioned reinforcement encounter policy: accepted parent hurt -> preferred existing target/event override/default current probability -> bounded spatial trials and placement/player/body gates -> candidate finalization -> unacknowledged add-with-passengers -> permanent caller and callee chance modifiers. These stages are one mechanism; no class/range/modifier/axis/attempt helper earns separate credit.',
 'Full Zombie547 and Monster129 read. Zombie.hurt first delegates parent; parent false returnsfalse, nonserver after parent true also returnsfalse. The own reinforcement body has no fresh caller-alive or NoAI check. Current target is preferred; source owner LivingEntity is only fallback if targetnull. No positive-health-delta, attacker-player identity or fatal-hit exploit follows from the parent Boolean alone.',
 'Actual SummonAidEvent is HasResult, not Cancelable. Javadoc refers to actuallyHurt and says ALLOW summons, but actual invocation is hurt and ALLOW only short-circuits default living-target/HARD/random-current-attribute/doMobSpawning conjunction. DENY returns true before search. Captured event chance is not the post-event live chance used by the DEFAULT branch. Listeners/current config remain unknown.',
 'Custom aid is a Zombie and used only on ALLOW+nonnull; otherwise factory is called once before the loop. No null guard is shown before getType, and the same object is repositioned across trial sites. This does not certify a fresh safe object or reproduce null failure. Up to50 draws each axis independently include zero and +/-7..40, so sites can repeat and allzero is possible; not a radius shell or50born actors.',
 'First physical placement check precedes predicate-result callback. Native ZOMBIE ON_GROUND/Monster check additionally requires nonPeaceful,darkness and valid below support for REINFORCEMENT. Forge placement result can alter the predicate outcome, not the already failed physical-position gate. SummonAid ALLOW by itself cannot certify Peaceful/daylight/body eligibility. No current cap/registry/tag/biome/config deployment proof.',
 'Physical spawn check handles border/support/empty cells for ordinary ON_GROUND; NO_RESTRICTIONS has a distinct earlytrue path. After candidate setPos, hasNearbyAlivePlayer rejects living nonspectators at strict squared distance<49, including creative under the actual predicates. No line-of-sight or all-world protective zone. Additional unobstructed/noCollision/no-liquid calls precede finalization, without a shown post-finalization body recheck.',
 'Target assignment precedes Zombie.finalizeSpawn at the candidate block local difficulty with REINFORCEMENT. Complete method delegates parent, may assign baby/equipment/holiday headwear, requests existing/new chicken riding, then randomizes chance and may add leader modifiers. Secondary chicken admission is separate; primary trial bound is not total population. Neither overridden finalization target nor post-finalization geometry is guaranteed.',
 'ServerLevelAccessor void addFreshEntityWithPassengers iterates self/passengers and discards every addFreshEntity Boolean. ServerLevel rejects removed, then manager posts join event and rejects known UUID before tracking. No atomic group commit. Normal add request return is not authoritative actor UUID/birth/survival/kill/pickup/payment receipt; it differs from the unused tryAdd overload which checks loaded UUID first.',
 'Only after the normal void add request, caller then callee receive distinct constructed permanent ADDITION modifiers amount(double)-0.05F, then loopbreak. A normal rejected admission can still reach both charges; a throw can interrupt the shown sequence. No rollback/refund or admitted-success coupling exists in this local path. This is a source order condition, not a tested gameplay failure.',
 'Complete AttributeModifier119 uses generated UUID in name-only constructor and equality by UUID, not display name. Complete AttributeInstance205 refuses duplicate UUID on add, stores permanent modifiers separately, computes addition->multiply-base->multiply-total then sanitizes. Reinforcement attr default0/range0..1 and NaN->min are source declarations. Chance penalties are actor propensity, not player material or currency. EventALLOW/leader/external modifiers mean no universal finite quota or per-night cap.',
 'Full Zombie randomization and leader behavior plus bounded Forge default0.1 range0..1 were read. DefaultAttributes long line83 and lookup were actually displayed in full in this review; Forge attributes view wins over fallback. Registration and numbers are helper support0, not proof actual loaded attribute supplier, config or probability.',
 'Full attribute modifier/instance save/load and bounded LivingEntity writer/server Attributes reader plus AttributeMap show a possible base/permanent-modifier source serialization route. Load does not generally clear existing modifier collections; malformed modifier may returnnull, unknown attribute may be ignored, and attributes absent in supplier can remain uninstantiated. No native flush/reload/reused-instance recovery, arbitrary capabilities or playerClone entitlement is accepted.',
 'Whole comparisons actually read complete current four selected judgment fields for EA16/32/36/39 and additionally EA41. EA16 spends a persisted lifetime attempt before alarm environment; EA32 owns a world exact-time setup veto and finite wave clock/quota; EA36 changes a preexisting dormant block reservoir after delayed hurt; EA39 rebuilds category/player/energy state; EA41 couples specific survived bullet/open state, parent relocation and old-site density to child. Current reinforcement owns a hurt/event/default attribute gate, repeated physical search and both actors permanent propensity depletion. Unchecked add and shared Zombie/finalize helpers alone are not the distinction.',
 'Three whole old Zombie migration judgments were read completely in their current non-evidence fields, actual full-row canonical hashes verified: earned cure-state transfer, old role/profession compatibility, two-stage drowning/door restoration. All remain0new credit. Whole Zombie source reading does not recredit those, skull/drop/egg/jockey/registration/attribute helpers or every saved field.',
 'Current45 semantic-key index and batch/canonical bindings checked, not45entire old semantic/source chains reread. Bounded selected-owner comparison supports maximum1related ecology policy only; not exhaustive global novelty. Fixed local mapped source artifact is not fresh upstream authentication, current pack execution, inherited damage/event/AI/collision/IO or native ecology acceptance.',
]
limits = [
 'Maximum1 pending related complete policy only; formal candidate ID remainsnull and no formal tool/receipt/ledger/aggregate is created here. Applicable ecology1000 remains unmet at45, not46 merely from this Main judgment.',
 'Author17observations/13mandatoryconstraints/7limits are preserved verbatim below; none of their limitations is relaxed. Keep target provenance, result-vs-cancelable distinction, placement order, mutable chance, zero/repeated coordinates and no own alive/NoAI recheck.',
 'Do not call postrequest propensity modifiers an admitted birth/payment receipt, success-only cost, fixed quota, population cap bypass or a reproduced failure/exploit. No runtime current handlers/config/registry/collision/chunk/world proof.',
 'Source save/load route only; no actual persistence/UUID lineage/Clone/world recovery or general clear-reset claim. Three old whole migration owners and all helpers remain0, no arbitrary cross-scope credit.',
 'If packaging proceeds, retain this entire distinct Main judgment and exact source/old-owner bindings; author must actually acknowledge full context after any Main-reviewed minimal package install before one strict aggregation. No author-independent-review impersonation, made-up candidateID or self-reviewed aggregate.',
 'No production/spawn cap/probability fix, asset/model/texture/building/sharedJar/world/nativeQA/game/process/display/network/Git/masterprompt/task deletion or active-hours claim. Preserve original IDs/rewards/progress; future gameplay progress needs authoritative outcome receipts.',
]
report = {
 'recorded_at':datetime.now(timezone.utc).isoformat(),'reviewer_thread_id':'01a16364-cac0-7ca2-a042-a5312781ca34',
 'author_thread_id':d['owner_thread_id'],'decision':'SUPPORT_MAXIMUM_ONE_RELATED_WHOLE_POLICY_PENDING_FORMAL_PROTOCOL_NOT_GAMEPLAY',
 'proposal':binding(P),'semantic_key':d['semantic_key'],'maximum_related_whole_credit':1,
 'formal_candidate_id':None,'formal_credit_applied_by_this_receipt':0,
 'actual_Main_reading':{'ranges':ranges,'cited_distinct_text_lines':1674,'ranges_count':25,'entries':21,
    'whole_files':8,'full_files':['Zombie.java','ZombieEvent.java','ServerLevelAccessor.java','AttributeInstance.java','AttributeModifier.java','Monster.java','Attributes.java','RangedAttribute.java'],
    'remaining_entries_bounded_only':True,'range_file_line_counts_are_reference_credit':False,
    'first_long_comparator_dump_clipped':True,'recovered_complete_fields':'EA36/39 plus all3migrationowners and45semantic-key-only index subsequently printed bounded;EA16/32 complete selected fields displayed before clipping; no clippedoldsourceclaim',
    'shared_native_artifact':binding(archive),'archive_integrity_all25exact':True},
 'independent_findings':findings,'mandatory_limits':limits,
 'author_observations_all17_retained':d['observed_chain'],
 'author_constraints_all13_retained':d['mandatory_constraints'],'author_limits_all7_retained':d['limits'],
 'complete_prior_semantic_judgments_actually_read':comparators,
 'three_whole_migration_owners':d['existing_global_migration_whole_owners'],
 'index_only_not_full45judgment_rereading':d['current45_accepted_semantic_index'],
 'formal_baseline':binding(BASE/'master-acceptance-ledger.json'),'formal_before':45,'formal_after_this_review':45,
 'global_novelty_credit':0,'migration_credit':0,'native_acceptance':False,'production_changes':0,
 'game_starts':0,'checklist_deletions':0,'active_hours_claimed':None,
}
with OUT.open('x') as f:
    json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(binding(OUT),ensure_ascii=False))

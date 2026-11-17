"""Fixed local source research: one charge-paid dodge lifecycle, pending review."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
A = H.parent
sha = lambda b: hashlib.sha256(b).hexdigest()
def ref(p):
    return {'path': str(p.relative_to(R)), 'sha256': sha(p.read_bytes())}
def read(p):
    return json.loads(p.read_text())

prior = read(H/'immune-reference-batch-045.json')
assert ref(H/'immune-reference-batch-045.json')['sha256'] == '5143b6437262a929aa1844c5c15920272dae828fb043349089f321532fc04e50'
root = R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration'
provenances = []
manifests = {}
for batch, repo in [('batch-011','HellFirePvP/AstralSorcery'), ('batch-012','HellFirePvP/ObserverLib')]:
    mp = root/batch/'source-manifest.json'
    m = next(x for x in read(mp) if x['repo'] == repo)
    meta = root/batch/'provenance'/repo.replace('/','__')
    provenance = {'repo':repo, 'commit':m['commit'], 'branch':m['branch'], 'git_tree':m['git_tree'],
        'manifest_path':str(mp.relative_to(R)), 'manifest_sha256':sha(mp.read_bytes()),
        'commit_metadata_path':str((meta/'commit.json').relative_to(R)),
        'commit_metadata_sha256':m['commit_metadata_sha256'],
        'tree_metadata_path':str((meta/'tree.json').relative_to(R)),
        'tree_metadata_sha256':m['tree_metadata_sha256'],
        'scope':'Existing fixed local source only. ObserverLib is supporting historical1.5.2 source, not a new credit or a claim about installed binaries.'}
    provenances.append(provenance)
    manifests[repo] = (m, {e['path']:e for e in m['files']})
assert provenances[0]['manifest_sha256'] == prior['provenances'][0]['manifest_sha256']

refs = []
def source(name, start=1, end=None, repo='HellFirePvP/AstralSorcery', context='actual_read050'):
    m, es = manifests[repo]
    prefix = 'src/main/java/hellfirepvp/' + ('astralsorcery/' if repo.endswith('AstralSorcery') else 'observerlib/')
    e = es[prefix+name]
    raw = (R/e['source']).read_bytes()
    lines = raw.decode().splitlines()
    end = end or len(lines)
    assert sha(raw) == e['sourceSha256']
    refs.append({'repo':repo,'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],
        'lines':[start,end],'file_sha256':sha(raw),'git_blob_sha1':e['source_blob'],
        'range_text_sha256':sha('\n'.join(lines[start-1:end]).encode()),'reading_context':context})

full = [
 'common/perk/type/AttributeTypeDodge.java', 'common/perk/modifier/AttributeModifierDodge.java',
 'common/auxiliary/charge/AlignmentChargeHandler.java', 'common/perk/type/PerkAttributeType.java',
 'common/perk/PerkAttributeHelper.java', 'common/perk/PerkAttributeLimiter.java', 'common/event/AttributeEvent.java',
 'common/perk/PerkAttributeMap.java', 'common/network/play/server/PktSyncCharge.java',
 'client/event/AlignmentChargeRenderer.java', 'common/perk/type/AttributeTypeChargeMaximum.java',
 'common/registry/RegistryPerkAttributeTypes.java', 'common/perk/PerkEffectHelper.java',
 'common/perk/source/ModifierManager.java', 'common/perk/modifier/PerkAttributeModifier.java',
 'common/constellation/world/DayTimeHelper.java', 'common/perk/modifier/AttributeModifierPerk.java',
 'common/network/play/server/PktSyncPerkActivity.java', 'common/network/play/server/PktSyncModifierSource.java',
 'common/registry/RegistryPerks.java', 'common/registry/internal/InternalRegistryPrimer.java',
 'common/lib/PerkAttributeTypesAS.java', 'common/perk/node/key/KeyChargeBalancing.java']
for f in full:
    source(f)
for f,a,z in [
 ('client/ClientProxy.java',120,154),
 ('common/registry/internal/PrimerEventHandler.java',55,131),
 ('common/registry/internal/PrimerEventHandler.java',195,197),
 ('common/registry/internal/PrimerEventHandler.java',267,269),
 ('common/data/research/ResearchHelper.java',1,89),
 ('common/data/research/ResearchHelper.java',243,245),
 ('common/data/research/PlayerPerkData.java',1,91),
 ('common/perk/AbstractPerk.java',52,141),
 ('common/data/research/ResearchManager.java',231,289),
 ('common/data/research/ResearchManager.java',332,418)]:
    source(f,a,z)
for f in ['common/util/tick/TickManager.java','common/util/tick/ITickHandler.java']:
    source(f,repo='HellFirePvP/ObserverLib')
reuse_names = {'AstralSorcery.java','common/event/handler/EventHandlerCache.java',
    'common/CommonProxy.java','common/network/PacketChannel.java','common/network/base/ASPacket.java',
    'common/network/channel/SimpleSendChannel.java','common/network/channel/BufferedReplyChannel.java'}
prefix = 'src/main/java/hellfirepvp/astralsorcery/'
for x in prior['source_refs']:
    if x['upstream_path'].removeprefix(prefix) in reuse_names:
        assert sha((R/x['path']).read_bytes()) == x['file_sha256']
        refs.append(dict(x,reading_context='exact045_shared_support_reused0'))

ledger = A/'immune-feedback-research/reviewed.json'
lb = ledger.read_bytes()
rows = json.loads(lb)
index = {r['id']:r for r in rows}
policy = 'astralsorcery-native-attribute-qualified-paid-dodge-with-retained-uuid-charge-and-regeneration-only-self-reconciliation'
assert policy not in {r['semantic_dedup_key'] for r in rows}
judgments = {
 'ars-elemental-native-mana-bubble-harmful-applicability-refusal-and-asymmetric-payment':
    'Ars owns randomized harmful-effect admission with unequal mana threshold/payment. This policy cancels LivingDamage after exact successful drain of a shared UUID/side charge balance; attribute eligibility can disappear independently of that balance, and only below-cap regeneration sends reconciliation. Not a new probability constant or harmful-effect variant.',
 'redstonearsenal-native-charge-shield-refusal-with-break-cue-and-self-hud':
    'Arsenal owns armor-item charges with NBT recharge timestamps, invulnerability-window reuse and immediate self sync/cues. Astral owns shared player UUID charge independent of the source of the dodge attribute, drains only after roll, and synchronizes through a separate regenerating state machine with no per-dodge receipt. Last-source removal and balance persistence differ from item charge exhaustion.',
 'malum-native-aegis-incoming-denial-transformed-capacity-and-postattack-window':
    'Aegis transforms capacity into integer charges, consumes on qualified incoming damage and immediately syncs/cues. Astral fraction-valued shared balance has two logical-side maps, success-gated chance/drain and independent attribute-membership removal; no hit dirty-sync or post-attack window write. Whole settlement/reconciliation lifetime differs, not merely resource naming.',
 'spellengine-native-evasion-eligibility-with-explicit-feedback':
    'SpellEngine qualifies native evasion by source tag/angle/busy state and emits a reason-specific event, animation and sound with source correlation. Astral has no such hit acknowledgment and instead exposes shared resource state after regeneration; its paid eligibility and retained balance form a different whole owner.',
 'enigmatic-native-nebula-dodge-denial-independent-of-teleport-success':
    'Nebula grants a denial/window regardless of counter-teleport outcome. Astral requires successful charge drain, grants no explicit invulnerability window and has no teleport; persistent shared balance and delayed resource presentation are the proposed policy, not another random dodge roll.',
 'werewolves-native-motion-two-stage-dodge-with-failed-arrow-roll-fallback':
    'Werewolves has two-stage motion/source skill qualification with fallback rolls and no resource settlement/reconciliation owner. Astral one roll followed by exact drain has independently removed attribute eligibility and retained UUID resource state; do not count the one versus two rolls separately.'}
fields = ['id','status','repo','commit','category','semantic_dedup_key','count_unit','full_chain_observation',
          'concrete_observation','application_to_boss_immune','limitations','research_credit','reviewed_utc']
cmps = [{'accepted_id':k,'complete_semantic_decision_read':{f:index[k][f] for f in fields},'distinction':v}
        for k,v in judgments.items()]
migration = A/'legacy-migration-acceptance/reviewed.jsonl'
mi = {r['candidate_id']:r for r in map(json.loads,migration.read_text().splitlines())}
old_owner = next(c for c in prior['migration_overlap_screen']['comparisons'] if c['accepted_id']=='a23e5ed56cdd1ec1e084')
assert all(mi[old_owner['accepted_id']][k] == v for k,v in old_owner['complete_semantic_decision_read'].items())
mc = {'accepted_id':old_owner['accepted_id'],'complete_semantic_decision_read':old_owner['complete_semantic_decision_read'],
      'distinction':'Accepted research owner covers UUID disk progress, old perk formats and clone effect dispatch; its own boundary explicitly stops before ModifierManager numeric behavior. This proposal is live attribute admission/charge settlement/regeneration-only presentation and cleanup, not a second persistence/migration reference. Disk IO and allocation formats remain support0.'}
progress_path = A/'immune-feedback-research/progress.json'
progress = read(progress_path)
assert len(rows) == progress['reviewed_effective_semantic_dedup']

observations = [
 'Native startup is wired: AstralSorcery→CommonProxy initialization, registry primer generic events and registerItems→registerRemainingData create/register AttributeTypeDodge and charge maximum. Base type constructor attaches the overridden HIGH LivingDamage listener to Forge EVENT_BUS. RegistryPerks submits Dodge config; configured cost default80 range1..500 is a declaration, not the installed value. CommonProxy attaches limiter and charge PLAYER/END ticker; ClientProxy includes inherited ticker and self-HUD CLIENT/END ticker/render listener.',
 'Ordinary native player login reads persistent progression then PerkEffectHelper adds each unsealed effect-granting perk; clone removes old/adds new, logout removes existing sources. AttributeModifierPerk supplies unsealed modifiers, from registered type factories/JSON. Actual map applies converters and extra modifiers, deduplicates by comparisonKey, then onApply puts UUID into side-specific type applicationCache. Full generic modifier/source bodies read; current installed perk-tree JSON and all equipment/converter producers not expanded. This is a real registered event/attribute path, not proof a particular save has unlocked dodge.',
 'Server applyPerk validates allocation and applies the source for a new perk. Seal/removal invokes source removal before/with allocation mutation. Source helper temporarily removes/reapplies other sources to handle converters; final removed modifier type onRemove receives !map.hasModifiers(type). Thus removal of one source does not disable dodge while another contributes the same type. Last-type removal deletes UUID membership; no charge refund or charge-clear call is made. Client activity/source packets enqueue corresponding modifications on current player, guarded for null in these handlers. Deep allocation codecs and source-provider deserialization remain existing persistence boundary.',
 'Dodge HIGH LivingDamage handler accepts PlayerEntity and computes LogicalSide from world.isRemote. It requires type applicationCache membership, not a per-hit equipment lookup. modifyValue starts0 and combines additions, added multiplies, stacking multiplies, each with perk-effect scaling. Divide100 then post AttributeEvent. The registered HIGH limiter clamps dodge0..0.75; post returns final event value, so later listeners can still change it. Do not claim a universal final75% cap under other handlers.',
 'One roll uses chance>=rand.nextFloat, then short-circuit drainCharge(...,false); only drain true cancels event. No local positive damage, source tag/type, attacker, angle, Boss, side-only, target cooldown, sound, animation or dedicated refusal packet check. A numeric chance0 is not a syntactic impossible condition because comparison includes equality and the Random API includes0; no frequency was measured. Native LivingDamage invocation/order, earlier absorption/armor effects and later arbitration remain Forge/MC boundaries. Cancellation does not prove all earlier side effects were undone or later cancellation stayed true.',
 'Charge is a shared runtime owner, not stored on the dodge perk/item: static maximumCharge and currentCharge are Map<LogicalSide,Map<UUID,Float>>. Initial getters independently default to1000. Creative/spectator report maximum and drain true without subtraction. Survival drain first checks current>=cost, computes result, rejects negative, and when not simulate writes clamp(result,0,currentMax). There is no receipt, sync, source identity, per-hit ID, cooldown or refund in drain. A later listener changing the damage event cannot automatically recover this already-submitted charge.',
 'Capacity recalculation is invoked by the charge-maximum attribute onApply/onRemove, with perk modifiers and postprocess, max(0,cap), then clamps current if above new cap. It does not directly sync. Initial default current1000 is not derived from a custom cap unless recalculation/path updates it. Filled percentage divides by max without a local max==0 guard; no actual zero-cap HUD failure claimed. Removing dodge membership does not remove capacity/current owner. Shared charge can also serve other registered consumers; those separate behaviors are not researched/countable here.',
 'Charge PLAYER/END reads supplied logical side and returns immediately if charge>=max. Otherwise regen=max/120 times day/cave factors, then charge-regen attribute/postprocess, adds and clamps only upper bound with min(charge,max), and constructs/sends PktSyncCharge. Outdoor day factor0.3+0.7*dayDistribution; underground0.85*0.25; unsealed KeyChargeBalancing adjusts each factor0.6+0.4*factor. DayTimeHelper uses configured cycle length. These formulas describe code, not current config or measured recharge times; negative/nonfinite extension values have no shown lower/finite check.',
 'Historical fixed ObserverLib TickManager actually forwards PlayerTickEvent player and side at allowed phase, with handlers in registration-list order. The charge handler has no server-only early exit, so both side states can regenerate. SimpleSendChannel.sendToPlayer only transmits for ServerPlayerEntity. However PktSyncCharge(player) is constructed before that guard and explicitly reads SERVER maps, even if called from a client-side tick. This is a code boundary, not an assertion of installed cross-thread race or confirmed wrong network traffic. Observer support source fixed separately; no installed Jar equivalence inferred.',
 'The only PktSyncCharge producer found in fixed Astral Java source is the below-cap regeneration branch. Drain and capacity clamp do not publish. A capacity reduction that leaves balance at new cap makes the next charge tick return, so that path alone does not reconcile the new max to client. Attribute source synchronization may independently recompute client capacity; no guaranteed stale UI is asserted. The final recovery tick sends after reaching cap, subsequent full ticks stop. Thus packets acknowledge shared state during regeneration, not specific dodges or reasons.',
 'PktSyncCharge codec is max/current two floats. CLIENT handler enqueues work then uses Minecraft current player without null check; receive writes both CLIENT UUID values as received, no range/finite/world/epoch/sequence validation. No originating target, attack cause, paid amount or actual damage result is carried. Old packet application after player/world replacement is not excluded by this handler. Transport direction/thread internals and actual queue order are not run.',
 'HUD reads CLIENT charge ratio. CLIENT/END <=0.95 or equipped AlignmentChargeRevealer requests20 reveal ticks, then15-tick alpha fade; render Post ALL skips spectator and alpha<=0. It previews cost for first equipped AlignmentChargeConsumer, not dodge ability, and draws colored/usage rectangles. Preview strict percFilled>usagePerc differs from drain allowing exact balance>=cost, but this preview is item-based, not a dodge affordability promise. No per-dodge gray text, target particles or sound. Helpers/shaders/assets not visually validated; numeric draw inputs are not pixels.',
 'Cleanup distinguishes eligibility and resource state. EventHandlerCache client disconnect clears attribute maps/type membership/perk sources; server stop clears attribute maps/type membership and other caches; logout/clone revoke/rebuild perks through native events. AlignmentChargeHandler has no clear/reset API and its private static maps are untouched by those shown chains. They have no world/session key and are not shown persisted to NBT. Same-process UUID reuse can retain balances; process restart resets statics. Capacity onRemove can clamp a retained balance; do not imply it is always unchanged. HUD resetChargeReveal has no call site in the fixed Java tree; alpha naturally ticks down, no explicit disconnect reset established.',
 'One whole policy is proposed: attribute-qualified paid damage denial with separately retained UUID/side resource and regeneration-only self reconciliation. Entire entry→eligibility/drain→cancel/state presentation→eligibility teardown and missing resource teardown studied. Formula, packet, cache, renderer, percent formatting, source kinds, default cost, equality edge and missing clear each contribute0 extra. Six nearest complete saved immune judgments compared; all480 IDs/text screened but not480 original chains reread. One full existing Astral migration owner explicitly retains prior credit and boundary.'
]
doc = {'schema_version':1,'owner':'program-feedback-review-050','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'ONE_WHOLE_ATTRIBUTE_PAID_DODGE_LIFECYCLE_PENDING_INDEPENDENT_REVIEW',
 'research_credit':0,'maximum_proposed_credit':1,'semantic_dedup_key':policy,
 'repo':provenances[0]['repo'],'commit':provenances[0]['commit'],'provenances':provenances,'source_refs':refs,
 'prior_read_reuse':{'evidence':ref(H/'immune-reference-batch-045.json'),
    'scope':'Exact045 bootstrap/cache/network support reused; CommonProxy, EventHandlerCache and SimpleSendChannel reread for relevant boundaries. New050 reads include whole concrete files and selected complete methods/declarations; ResearchHelper was fully read but only query/clear ranges cited. Earlier exploratory Dodge89 reread, never credited. No claim historical migration files first read today. No old verifier executed.'},
 'baseline':{'progress':ref(progress_path),'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),
    'accepted048':ref(A/'immune-feedback-research/coordinator-roots-aqua-bubble-acceptance-20261104.json'),
    'held049':ref(H/'immune-reference-batch-049-screen.json')},
 'dedup_snapshot':{'path':str(ledger.relative_to(R)),'sha256':sha(lb),'rows':len(rows),'comparisons':cmps,
    'screen_scope':'480 saved records screened by relevant concepts; six nearest whole semantic decisions actually read. No mass source-read/credit claim.'},
 'migration_overlap_screen':{'path':str(migration.relative_to(R)),'sha256':sha(migration.read_bytes()),'comparisons':[mc],
    'scope':'All five saved045 Astral owner judgments read; only the relevant full player-progress owner bound here. No disk migration re-audit or new credit.'},
 'whole_chain_observation':observations,
 'application':'原cod4体质/免控应分别管理效果资格、共享资源余额及结果回执；换装/解除资格不应靠HUD隐藏冒充状态清理。Boss拒控灰字需来自权威拒控理由，不能拿星能条下降或后续恢复包替代。普通阴阳体质不新增灰字。只研究，不移植。',
 'critical_boundaries':['Fixed historical1.16-indev and separately pinned ObserverLib support, not Dynasty1.20.1 deployed binaries. No runtime/new installed dependency validation.',
    'Installed perk-tree data, every possible equipment/converter source, Forge final event ordering, engine final damage/control and all protocol scheduling remain explicit boundaries. Native login and complete generic source application provide entry, not assurance a current player has this perk.',
    'Attribute removal and shown connection/server callbacks are inspected; missing resource cleanup is bounded to actual private owner class and fixed local call graph, not arbitrary mod/reflection behavior.',
    'Six full immune semantic decisions and one reused complete migration owner compared. Main reviewer may hold/merge entire policy; currently0/max1, never split details into new counts.',
    'No game/Gradle/Java/upstream execution/network/production/tests/assets/sharedJar/userworld/main ledger/checklist edits or hours claim.'],
 'counting':{'whole_policies_proposed':1,'accepted_credit':0,'runtime_credit':0},
 'next_work':'Independent whole-policy review by coordinator; continue next distinct original-program fixed-source owner without waiting for repeated dispatch.',
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0}
covered = {}
for x in refs:
    a,z=x['lines']; incoming=set(range(a,z+1)); prev=covered.setdefault(x['path'],set())
    assert not incoming.intersection(prev)
    prev.update(incoming)
doc.update(source_ranges=len(refs),unique_files=len(covered),
           full_files=sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),
           cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-050.json'
with out.open('x') as f:
    json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'ranges':doc['source_ranges'],'files':doc['unique_files'],
                  'full_files':doc['full_files'],'lines':doc['cited_lines'],'credit':0,'max_pending':1}))

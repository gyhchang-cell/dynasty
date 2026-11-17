"""Seal a bounded local Mace of Distortion overlap screen; no research credit."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path('/Users/a15356015027/Desktop/dynasty')
H = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
def binding(p):
    return {'path': str(p.relative_to(R)), 'sha256': sha(p.read_bytes())}

prior = H / 'immune-reference-batch-037.json'
assert prior.exists()
old = json.loads(prior.read_text())
provenances = []
manifests = {}
for v in old['provenances']:
    v = dict(v)
    assert sha((R / v['manifest_path']).read_bytes()) == v['manifest_sha256']
    for label in ['commit', 'tree']:
        v[label + '_metadata_sha256'] = sha((R / v[label + '_metadata_path']).read_bytes())
    provenances.append(v)
    manifests[v['repo']] = next(x for x in json.loads((R / v['manifest_path']).read_text()) if x['repo'] == v['repo'])

refs = []
def add(repo, prefix, specs):
    m = manifests[repo]
    files = {e['path']: e for e in m['files']}
    for name, limits, purpose in specs:
        e = files[prefix + name]
        raw = (R / e['source']).read_bytes()
        lines = raw.decode().splitlines()
        a, z = limits or [1, len(lines)]
        assert sha(raw) == e['sourceSha256']
        refs.append({'repo': repo, 'commit': m['commit'], 'path': e['source'],
                     'upstream_path': e['path'], 'lines': [a, z], 'file_sha256': sha(raw),
                     'git_blob_sha1': e['source_blob'],
                     'range_text_sha256': sha('\n'.join(lines[a-1:z]).encode()),
                     'reading_context': 'new_actual_source_read056', 'purpose': purpose})

add('CyclopsMC/EvilCraft', 'src/main/java/org/cyclops/evilcraft/', [
    ('item/ItemMaceOfDistortion.java', None, 'Concrete target enumeration, ignored hurt result, multiplicative motion and local cue calls.'),
    ('item/ItemMaceOfDistortionConfig.java', None, 'Actual item factory; constants/config do not earn credit.'),
    ('item/ItemMace.java', None, 'Whole item input, admission, partial-charge settlement, inherited release overload and feedback request methods.'),
    ('core/item/ItemBloodContainer.java', None, 'Whole simulation/execute resource helper and inventory fallback. Fluid placement arms context only.'),
    ('item/ItemPowerableHelpers.java', None, 'Whole server power setter and setting confirmation, distinct from target result.'),
    ('core/helper/ItemHelpers.java', [1,85], 'Complete get/set integer methods only; remainder not read. Power0 removes NBT key.'),
    ('core/degradation/effect/KnockbackDistortDegradation.java', None, 'Alternate caller invokes same target method with null initiator; parent scheduler not expanded, adds0.'),
])
add('CyclopsMC/CyclopsCore', 'src/main/java/org/cyclops/cyclopscore/', [
    ('item/DamageIndicatedItemFluidContainer.java', None, 'Whole capability factory, simulation exact-amount check and delegated state HUD inputs; historical support0.'),
    ('capability/fluid/FluidHandlerItemCapacity.java', None, 'Whole capacity and fluid NBT adapter; inherited Forge drain not expanded, no migration credit.'),
])
new_count = len(refs)
for x in old['source_refs']:
    if x['upstream_path'].endswith('/EvilCraft.java'):
        y = dict(x)
        raw = (R/y['path']).read_bytes()
        assert sha(raw) == y['file_sha256']
        a,z = y['lines']
        y['range_text_sha256'] = sha('\n'.join(raw.decode().splitlines()[a-1:z]).encode())
        y['reading_context'] = 'exact037_registration_range_reused_not_newly_read'
        y['purpose'] = 'Existing config-list context registers Mace and degradation configs. Reuse0; not rerun old verification.'
        refs.append(y)

fields = ['id','status','repo','commit','category','semantic_dedup_key','count_unit',
          'full_chain_observation','concrete_observation','application_to_boss_immune',
          'limitations','research_credit','reviewed_utc']
lp = H.parent / 'immune-feedback-research/reviewed.json'
rows = json.loads(lp.read_text())
by = {x['id']:x for x in rows}
comparisons = {
    'pnc-native-kick-actor-rate-budget-server-selected-target-and-damage-independent-motion-receipt':
        'Nearest whole accepted owner already covers authoritative admission, damage-independent motion write and attempt cues. Mace scales existing velocity rather than overwriting it and iterates an AABB; these differences alone do not establish another whole policy. Mace has no equivalent explicit server request throttle or target revalidation. Hold0.',
    'pnc-native-fall-resource-budget-total-refusal-versus-partial-mitigation':
        'Already covers budget-conditioned partial result versus total refusal and cues that are not final damage receipts. Mace uses consumed blood to rescale area/charge; resource units, integer formula and payment order are supporting boundaries, not a new immunity owner. Hold0.',
    'botania-native-deferred-control-revalidation-and-qualified-target-receipt':
        'Existing owner demonstrates deferred revalidation and qualified native control receipt. Mace is immediate, ignores hurt result and emits client attempt cues; absence of a stronger receipt and different effect helper do not supply an independent counted mechanism. Hold0.',
}
observations = [
    {'stage':'concrete entry and registration', 'observation':
     'MaceOfDistortion config creates concrete item; exact prior EvilCraft config-list range retained0. ItemMace use first lets crouching power setter run server-side, cycles modulo5 and emits setting actionbar. Noncrouching use requires canConsume(1), then startUsingItem. On failure client emits smoke/sound and returns FAIL; server falls through PASS. Left-click returns !isUsable to reject. hurtEnemy separately attempts fixed5 drain from current stack and ignores actual result. This does not prove same native callback order or paid melee damage.'},
    {'stage':'power identity and bounded lifecycle', 'observation':
     'Power is current ItemStack integer tag; missing tag returns0 and setting0 removes key. getUseDuration=100*(5-power). Normal setter produces0..4; direct NBT values are not clamped in getter. Native loading/use state and malformed-data outcomes are unexecuted. No custom actor token, target membership, timed immunity or delayed target callback in the concrete charged release. Native use cancellation/equipment switching remain engine-owned, not proven by these overrides.'},
    {'stage':'partial payment before target selection', 'observation':
     'releaseUsing requires Player; retrieves capacity handler then computes used=getUseDuration-currentRemaining. toDrain=used*capacity*(power+1)/(duration*5), using Java int arithmetic. consume executes on ordinary server player, simulates for creative or client; creative still needs fluid available to simulation, not unconditional free grant. Recomputed used=returnedAmount*duration/capacity. Only returnedAmount>0 invokes use then client burst, else client out-of-energy. No refund when AABB empty, hurt fails or velocity stays unchanged. No independent source-result acknowledgment. Zero payment, partial payment and full cost are distinct; no asserted exact installed capacity or arithmetic safety.'},
    {'stage':'fallback resource semantics', 'observation':
     'consume first drains held stack then iterates other inventory containers of matching fluid. canConsume fallback only tests nonempty simulated return, not total requested amount; the concrete usability call asks1. drainFromOthers accumulates into drained then subtracts cumulative drained amount from remaining each iteration, not just thisDrained amount. With multiple donors this can terminate early compared with a per-donor subtraction; it does not establish duplicated fluid, full payment or an exploitable runtime path. Final nonempty && empty condition is contradictory. Resource arithmetic is supporting0, not another mechanism. Inventory iterator order/coverage and arbitrary third-party handler guarantees were not read.'},
    {'stage':'capability support and presentation limits', 'observation':
     'Pinned historical Core canDrain simulates and requires exact amount, initCapabilities constructs FluidHandlerItemCapacity. Adapter permits configured fluid, reads capacity override and writes/removes Fluid NBT; getFluid updates inherited capacity, serializes fluid/capacity and delegates capability. Actual drain/fill amount behavior is inherited Forge source and unexpanded. HUD is delegated to DamageIndicatedItemComponent, not a target success receipt. Fixed Core tag is supporting source, not proof of exact installed dependency or complete item-stack synchronization.'},
    {'stage':'actual target policy', 'observation':
     'distortEntities captures initiator coordinates and queries AABB inflate(used/5+2) excluding initiator; no explicit alive/Boss/line-of-sight/team gate here. For each candidate distortEntity computes inverseStrength=distance/(used+1), or0.1 for null initiator; knock=power+used/200+1 with int division. It computes and normalizes displacement only when d!=0. Normalized dx/dy/dz are never used to construct velocity. For Living target it requests radial damage3*power and ignores boolean; client then calls distortion sound/particle. VengeanceSpirit receives setSwarm(true), whose downstream behavior is not expanded in056. Finally it multiplies EXISTING velocity by strength/2, not an outward vector or native knockback call. Stationary velocity need not move at all; negative strength can reverse components where reachable. No universal Boss movement or successful hurt assertion.'},
    {'stage':'feedback and receipt boundary', 'observation':
     'Client charge rings/targeted blur depend on local item duration; release burst depends on local simulated returned amount. Concrete target client cue requests explosion sound once plus again for nonnull initiator and one particle, irrespective of hurt result. Server advancement call receives entire candidate list after loop, not a filtered successful-hit/motion list; advancement predicate implementation unexpanded. Config actionbar confirms selected power only. No shown per-target refusal reason/gray text/receipt dedup or server→client target acknowledgment in these concrete classes. Engine particle consumers, native sync and actual pixels/audio not executed/read.'},
    {'stage':'overloads and alternate call are not extra owners', 'observation':
     'Concrete animateOutOfEnergy(World,Player) overload handles the Player-typed use call; releaseUsing uses LivingEntity-typed entity and selects base LivingEntity method, so cue routing differs. It is an overload boundary0, not an independent policy or proven defect. Degradation.canRun threshold3, runClientSide calls runServerSide, which invokes same distortEntity for area entities, null initiator, configured position and degradation*10 charge/power1. Parent scheduler, actual active degradable producer and cadence unexpanded; this is only a concrete alternate caller, not a second complete chain or accepted control family.'},
]

# These fully displayed classes were exploratory only; no provenance/whole-chain credit.
discovery = []
for path, note in [
    ('tools/cod4/immune-feedback-research/sources/WayofTime__BloodMagic/src/main/java/wayoftime/bloodmagic/ritual/types/RitualFeatheredKnife.java',
     'Whole concrete ritual read, but parent ritual activation/network/altar chain and fixed manifest not bound here. Direct setHealth, explicit health packet and altar call cannot alone prove a novel whole owner. Deferred, credit0, not declared duplicate or repository exhaustion.'),
    ('tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-002/sources/CyclopsMC__EvilCraft/src/main/java/org/cyclops/evilcraft/potion/PotionPaling.java',
     'Whole small class read. Tick damage amplifier/4 ignores hurt result. Producer/exit unexpanded; simple tick-damage wrapper not a new immune/control owner. Held0.'),
]:
    p = R/path
    discovery.append({**binding(p), 'actual_lines_read':[1,len(p.read_text().splitlines())],
                      'credit':0, 'fixed_commit_provenance_claimed_in_this_screen':False, 'note':note})

covered = {}
for x in refs:
    a,z=x['lines']; s=covered.setdefault(x['path'],set()); new=set(range(a,z+1))
    assert not s.intersection(new); s.update(new)
doc = {
    'schema_version':1, 'owner':'program-feedback-review-056',
    'created_utc':datetime.now(timezone.utc).isoformat(),
    'status':'HELD_ZERO_EXISTING_DAMAGE_INDEPENDENT_MOTION_AND_PARTIAL_RESOURCE_POLICY',
    'research_credit':0, 'maximum_proposed_credit':0,
    'repo':'CyclopsMC/EvilCraft', 'commit':manifests['CyclopsMC/EvilCraft']['commit'],
    'provenances':provenances, 'source_refs':refs,
    'prior_read_reuse':{'evidence':binding(prior),'new_ranges':new_count,
                       'reused_ranges':len(refs)-new_count,'old_verifier_executed':False},
    'baseline':{'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'ledger':binding(lp)},
    'dedup_snapshot':{**binding(lp),'comparisons':[
        {'accepted_id':k,'complete_semantic_decision_read':{f:by[k][f] for f in fields if f in by[k]},'comparison':v}
        for k,v in comparisons.items()],
        'scope':'Three complete substantive accepted decisions actually read; broad identifier scans are discovery0, not full483 reviews. Kick trailing credit/time fields recovered separately after combined output truncation.'},
    'bounded_chain_observations':observations,
    'decision':'Screen closed at0, maximum0: no sufficiently distinct complete immunity/control/refusal-feedback mechanism. Do not split velocity formula, sound overload, fallback subtraction, NBT fields, zero power or client/server branches into credits. Further runtime/parent expansion is not required to reject this candidate; no complete native-engine validation claimed.',
    'application':'Use explicit final control admission before velocity writes and tie refusal feedback to that decision. Keep damage success, resource payment, control result and presentation receipt separate. This is research advice only, not production work or a new UI change.',
    'limitations':[
        'Historical fixed source, not Dynasty runtime. No Java/Gradle/game/network/display/audio execution.',
        'Core exact dependency binary binding, Forge fluid handler/Inventory iterator/native item-use scheduling, Entity velocity/hurt/sync, advancement predicates and concrete particles remain unexpanded.',
        'No complete degradation producer or spirit swarm consumer chain claimed; helper/file/context counts never semantic credit.',
        'BloodMagic and Paling exploratory class reads are explicitly outside bound source totals and have0credit.',
        'No production, tests, art, background, shared Jar, original save, master ledger/session/pending or checklist mutations.'
    ],
    'discovery_only':discovery,
    'source_ranges':len(refs),'unique_files':len(covered),
    'full_files':sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),
    'cited_lines':sum(map(len,covered.values())),
    'production_changes':False,'runtime_executed':False,'network_requests':0,
    'master_changes':False,'checklist_deletions':0,'hours_claimed':0,
    'next_work':'Choose a different fixed-local whole program mechanism. Do not reopen Mace motion/payment/overload variants. FeatheredKnife remains an unclosed discovery, not a proposed reference.053/055 acceptance remains coordinator-owned.'
}
out = H/'immune-reference-batch-056-screen.json'
with out.open('x') as f:
    json.dump(doc,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps({'evidence':binding(out),'ranges':doc['source_ranges'],'files':doc['unique_files'],
                  'full_files':doc['full_files'],'lines':doc['cited_lines'],'credit':0}))

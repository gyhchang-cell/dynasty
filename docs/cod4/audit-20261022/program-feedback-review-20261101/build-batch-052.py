"""Bind the fixed-local launch/fall source-token lifecycle; never award credit."""
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
def load(p):
    return json.loads(p.read_text())
p50 = H/'immune-reference-batch-050.json'
p51 = H/'immune-reference-batch-051.json'
p49 = H/'immune-reference-batch-049-screen.json'
assert ref(p50)['sha256'] == '59958fbe55e28774eee1642642401e7da4539601b103d37b8bafa8450051ef6e'
assert ref(p51)['sha256'] == '176f6f8226778744ed87ea66d0d5a0c42a5000e0063454985401f5a86b0c48c7'
d50, d51 = load(p50), load(p51)
v = d50['provenances'][0]
raw = (R/v['manifest_path']).read_bytes()
assert sha(raw) == v['manifest_sha256']
m = next(x for x in json.loads(raw) if x['repo'] == v['repo'])
es = {x['path']: x for x in m['files']}
prefix = 'src/main/java/hellfirepvp/astralsorcery/'
refs = []
def source(n, a=1, z=None):
    e = es[prefix+n]
    b = (R/e['source']).read_bytes()
    lines = b.decode().splitlines()
    z = len(lines) if z is None else z
    assert 1 <= a <= z <= len(lines)
    assert sha(b) == e['sourceSha256']
    refs.append({'repo': m['repo'], 'commit': m['commit'], 'path': e['source'],
        'upstream_path': e['path'], 'lines': [a,z], 'file_sha256': sha(b),
        'git_blob_sha1': e['source_blob'],
        'range_text_sha256': sha('\n'.join(lines[a-1:z]).encode()),
        'reading_context': 'actual_read052'})

for n in ['common/event/helper/EventHelperDamageCancelling.java',
          'common/item/wand/ItemBlinkWand.java', 'common/item/wand/ItemGrappleWand.java',
          'common/entity/technical/EntityGrapplingHook.java',
          'common/network/play/server/PktShootEntity.java',
          'client/ClientScheduler.java', 'common/util/Counter.java']:
    source(n)
for n,a,z in [
    ('common/CommonProxy.java',324,328),
    ('client/ClientProxy.java',68,102), ('client/ClientProxy.java',156,159),
    ('common/registry/RegistryItems.java',98,99),
    ('common/registry/RegistryItems.java',174,182),
    ('common/registry/RegistryEntities.java',127,136),
    ('common/registry/RegistryEntities.java',159,165),
    ('common/registry/internal/PrimerEventHandler.java',149,152),
    ('common/item/armor/ItemMantle.java',158,201),
    ('common/util/data/ByteBufUtils.java',54,71),
    ('common/util/data/ByteBufUtils.java',246,257),
    ('common/util/nbt/NBTHelper.java',54,81),
    ('common/util/nbt/NBTHelper.java',235,242),
    ('common/util/MiscUtils.java',128,137)]:
    source(n,a,z)

reuse = {
    'common/auxiliary/charge/AlignmentChargeHandler.java',
    'common/network/play/server/PktSyncCharge.java',
    'client/event/AlignmentChargeRenderer.java',
    'client/ClientProxy.java', 'common/registry/internal/InternalRegistryPrimer.java',
    'common/registry/internal/PrimerEventHandler.java',
    'common/event/handler/EventHandlerCache.java', 'AstralSorcery.java',
    'common/network/PacketChannel.java', 'common/network/base/ASPacket.java',
    'common/network/channel/SimpleSendChannel.java', 'common/CommonProxy.java'}
for x in d50['source_refs']:
    n = x['upstream_path'].removeprefix(prefix)
    if x['repo'] == 'HellFirePvP/ObserverLib' or n in reuse:
        if n == 'common/registry/internal/PrimerEventHandler.java' and x['lines'] == [195,197]:
            continue
        assert sha((R/x['path']).read_bytes()) == x['file_sha256']
        refs.append(dict(x, reading_context='exact050_shared_support_reused0'))
for x in d51['source_refs']:
    if x['upstream_path'] == prefix+'common/util/NameUtil.java':
        assert sha((R/x['path']).read_bytes()) == x['file_sha256']
        refs.append(dict(x, reading_context='exact051_registration_support_reused0'))

ledger = A/'immune-feedback-research/reviewed.json'
lb = ledger.read_bytes()
rows = json.loads(lb)
idx = {x['id']: x for x in rows}
policy = 'astralsorcery-native-flight-issued-coalesced-source-token-with-hurt-consumption-versus-grounded-expiry'
assert policy not in {x['semantic_dedup_key'] for x in rows}
distinctions = {
 'goety-no-knockback-single-use-native-event-stamp':
 'Goety bridges attack to knockback with a victim tick stamp and removes even stale stamps on the next knockback. Astral marks before later injury from voluntary movement, coalesces the same DamageSource in a UUID set, ignores unrelated sources, and has a competing onGround END removal without an elapsed-tick deadline. Difference proposed is the whole admission/consumption/ground invalidation ownership, not replacing knockback with fall or choosing a different map.',
 'ars-bounce-fall-source-avoidance-and-next-tick-motion':
 'Ars evaluates an active bounce effect at fall dispatch and queues subsequent motion. Astral writes a future source-qualified token during launch or pull; either a matching LivingHurt consumes it or a separate grounded tick invalidates it. Merely resetting fallDistance and applying motion is shared context0.',
 'ars-blink-qualified-warp-and-feedback-order':
 'Ars qualified warp invokes teleport admission with route-specific feedback. Astral launch directly writes motion and sends motion FX before enrolling the later fall token; its separate TELEPORT branch is not a new candidate and its deep raytrace helpers are excluded. Token denial feedback cannot be inferred from launch success.',
 'spellengine-teleport-minimum-displacement-explicit-fizzle-before-cost-callback':
 'SpellEngine returns explicit displacement failure before cost callback, with actual fizzle submission. Astral has no final displacement check or fall-refusal cue and pays before motion. The proposal is the later competing source-token cleanup lifecycle, not this missing fizzle or different cost.',
 'pnc-native-fall-resource-budget-total-refusal-versus-partial-mitigation':
 'PNC allocates pressure at the fall event and chooses cancellation versus partial mitigation. Astral pays for movement earlier, then cancels one matching hurt without any new charge check; no partial budget branch. Coalesced entitlement and ground cleanup can expire independently of payment.',
 'redstonearsenal-native-trident-plunge-hit-dependent-fall-refusal':
 'Trident qualified plunge uses hit outcome and live held-item state to choose fall refusal or reduction. Astral later hurt consumer does not recheck item, motion, payment or actual hit; prior flight token and separate onGround state are its only relevant owners. No second credit for a wand or projectile variant.',
 'lycanites-native-weight-heavy-pickup-refusal-and-safe-release-control-lease':
 'Lycanites owns continuous forced movement plus saved flying/safe-position restoration on release. Astral moves the thrower voluntarily and issues no restoration lease: one source token can survive hook removal, changing held items or logout until a matching hurt/ground event. Distinct proposed refusal lifecycle, not an alternative controlled actor.',
 'betweenlands-native-nonrenewing-environmental-footing-lease-with-heavyweight-first-mud-veto-and-sludge-specific-control-skip':
 'MudWalker is a deadline-derived environmental floor/contact lease with source-specific heavyweight precedence. Astral has no duration clock, floor change, material predicate or repeated-contact immunity. It is a coalesced one-use source token, independently invalidated by grounded tick; common environmental qualification alone earns0.'}
fields = ['id','status','repo','commit','category','semantic_dedup_key','count_unit',
          'full_chain_observation','concrete_observation','application_to_boss_immune',
          'limitations','research_credit','reviewed_utc']
cmps = [{'accepted_id': k,
         'complete_semantic_decision_read': {f: idx[k][f] for f in fields},
         'distinction': value} for k,value in distinctions.items()]
progress_path = A/'immune-feedback-research/progress.json'
progress = load(progress_path)
assert len(rows) == progress['reviewed_effective_semantic_dedup']

observations = [
 'Native registration is concrete: RegistryItems creates both wand items through the named primer helper, PrimerEventHandler registers items/entities, RegistryEntities creates the hook factory and custom client factory. CommonProxy attaches EventHelperDamageCancelling to Forge; its default-priority LivingHurt and PlayerTick listeners are not dormant utilities. Astral bootstrap, primer fill and PacketChannel registration are exact prior050 support. Registration blocks are bounded context, not entire RegistryItems/Entities files read or current installed availability proof.',
 'Blink right-click sneak cycles persisted blinkMode and actionbar mode text; otherwise no item cooldown permits setActiveHand. Use duration72000 and BOW action. ServerPlayer-only onPlayerStoppedUsing reads current mode; release does not repeat item-cooldown gate. LAUNCH calculates strength from held ticks and current elytra state (.8 flying/2.4 otherwise), requires strength>.3, then drains fixed850*.8=680 charge. Shared050 drain permits creative/spectator without deduction; capacity, retained UUID balance, regen-only sync and HUD remain existing ownership0.',
 'Paid launch writes look-based motion (strength*3 with positive-Y adjustment), clears fallDistance, optionally schedules startFallFlying for enabled Vicio mantle, then emits PktShootEntity with strength before checking current !isElytraFlying to mark FALL. No launch cooldown is set here; teleport branch alone sets40 after a paid position write. No collision/displacement confirmation or refund gates the later token. TELEPORT branch never calls the token helper. Its raytrace/safe destination helpers were not expanded, so teleport receives no complete-chain or novelty claim.',
 'Mode storage is stack persistent compound blinkMode ordinal; enum helper clamps invalid integers to existing bounds. ItemMantle qualifies actual chest mantle, weak expected constellation and enabled effect. CommonProxy.scheduleClientside is empty; ClientProxy queues the captured player callback on ClientScheduler CLIENT END. It decrements counters before run, with callbacks added while ticking deferred. This is physical-proxy-dependent scheduling, not an S2C start-flight command: no guaranteed server-wide two-tick flight transition. Constellation resolution, engine startFallFlying validity and cross-thread effects unexpanded/unexecuted. Token enrollment checks state before that delayed callback can be presumed effective.',
 'Alternate producer is same policy0: server grapple right-click with nonempty held stack/no cooldown drains450, attempts world.addEntity and sets40 cooldown without checking spawn result. Hook constructor retains throwing entity and shoots; block impact begins pulling, living-entity impact excludes self but not boss/team and anchors to the hit actor. It moves the thrower, not the hit anchor. Invalid/dead thrower or unlatched age>=30 starts despawn; proximity/timeout while pulling also starts despawn. Only a non-despawning pull iteration applies movement and source mark.',
 'Hook pull sets thrower fallDistance=-2, adds bounded pull acceleration and first-pull vertical impulse, then marks FALL for PlayerEntity. Its tick writes motion on either side, while the marker itself rejects remote worlds. Non-improving rough distance increments timeout; improving resets it. Every pull can re-add after a consumed/ground-cleared token; repetitions while already present coalesce. Despawning increments until>10 then remove; there is no token revocation on setDespawning/remove or item change. Actual native entity ticking, spawn sync and motion acceptance unexpanded; hook renderer/buildLine/despawn sparkles add0.',
 'Token owner is private static Map<UUID,Set<DamageSource>>, shared by both movement producers. Server-world mark inserts source into HashSet, so repeated same-source marks do not queue charges and different sources would coexist. Fixed local call-site search found only Blink launch and hook pull, both using DamageSource.FALL. No grant-side source lifetime, cast/flight generation, stack identity, entity ID, dimension or amount is stored. Equality is Java set equality; native DamageSource equality implementation was not read, so no stronger object-identity or broad damage-type claim.',
 'LivingHurt consumer first requires PlayerEntity, removes event.getSource from that UUID set, removes outer UUID entry if now empty, then cancels. No explicit logical-side, amount>0, current tool/cooldown/charge, motion, last producer or fallDistance check. Unmatched damage leaves token intact. Registration does not request receiveCanceled explicitly; default Forge cancellation dispatch and ordering relative to native fall/PlayerTick were not expanded. An integrated-client matching event could only be assessed after those native details; no actual cross-side steal or guaranteed extra protection is asserted.',
 'Competing cleanup is PlayerTick END on server world while player.isOnGround: remove FALL only. This path does not remove an empty outer UUID map entry. Ground cleanup can invalidate without injury; later hook iteration may re-enroll. Hurt consumption and grounded invalidation are two competing state transitions, not a duration timer or a stack of free falls. Native landing-to-hurt-to-END order is external, so no proof normal landings always cancel or always lose the token. Multi-hit same-source events need a fresh mark after the first successful removal.',
 'Complete helper exposes no reset/logout/clone/death/dimension/server-stop API; static UUID map is not native NBT/capability storage. Reused EventHandlerCache shutdown/disconnect handlers do not clear this map. Therefore source shows no lifecycle cleanup at those boundaries: a marked entry is not automatically tied to the original player entity or world. It may retain an empty entry after grounded cleanup and a nonempty entry until a later matching event/ground tick; actual relog/world-transfer event ordering untested. A fresh process/classloader initializes a fresh map. No persistence across a real process restart claimed.',
 'PktShootEntity is registered and nearby target point includes sending world dimension through existing PacketChannel; payload itself has int entityId, optional motion vector, hasEffect boolean and effectLength float, no UUID/dimension/epoch/result token. Client enqueues, looks up entity in current client world and writes motion, then requests300 particles from current entity look and packet strength. If no entity/world exists it drops; no retry/ack. Optional vector codec permits null but consumer dereferences it when entity exists; normal launch producer supplies a nonnull vector, so malformed/null crash remains a conditional protocol boundary, not a demonstrated normal failure. Float/vector finite/range validation is absent in these methods; external transport trust is not expanded.',
 'Launch packet/particles precede token enrollment and do not acknowledge damage refusal; mantle-flying branch can still emit them without enrolling. Neither marker, grounded cleanup nor hurt cancellation sends a custom cue. Holding-use particles gate item state/cooldown but do not check charge affordability. HUD cost preview varies with held-time (.2..1)*850 while server launch is fixed680; shared050 HUD is state/cost presentation, not a refusal receipt. Hook despawn sparkles only concern hook removal. No actual rendering/audio/delivery validated; no asset copies or UI edits.',
 'Eight complete nearest accepted semantic decisions compared, plus held049 and pending050/051. Entire source-qualified token lifecycle is max1 pending0: movement admission, coalescing, independent hurt consumption, onGround invalidation and absent lifecycle clear form the candidate. Different wands, source constant, amount, packet, scheduler, missing guards and empty-map retention are support0. Earlier Goety one-shot stamp is the nearest possible merge; coordinator must decide whole-policy novelty. Broad480 concept/ID screen is not480 original chains reread.'
]
doc = {
 'schema_version':1, 'owner':'program-feedback-review-052',
 'created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'ONE_WHOLE_FLIGHT_SOURCE_TOKEN_POLICY_PENDING_INDEPENDENT_REVIEW',
 'research_credit':0, 'maximum_proposed_credit':1,
 'repo':m['repo'], 'commit':m['commit'], 'semantic_dedup_key':policy,
 'provenances':d50['provenances'], 'source_refs':refs,
 'prior_read_reuse':{'evidence':[ref(p50),ref(p51)],
   'scope':'Seven newly cited whole files and complete selected methods/registration blocks actually read052. Exact050 transport/resource/registration/cache/Observer support and051 NameUtil reused0. Whole ItemBlinkWand was read before the continuation compaction; selected release branch reread to resolve cost/order. CommonScheduler whole explored but unused0; truncated ActivePlayerAttunementRecipe exploration excluded and not claimed whole. No old verifier rerun.'},
 'baseline':{'progress':ref(progress_path),'formal_count_observed':len(rows),
             'gap_to1000':1000-len(rows),'old_verifier_or_ledger_rerun':False},
 'dedup_snapshot':{'path':str(ledger.relative_to(R)),'sha256':sha(lb),'rows':len(rows),
                  'comparisons':cmps,
                  'scope':'Eight complete saved semantic decisions, not original sources, actually read. First six were read during052 before compaction; two lease judgments read after. Broad concept screen over480 identities/text, not480 complete-chain reads.'},
 'existing_work_overlap':[
   {'evidence':ref(p49),'distinction':'049 held reactive true-source relocation and holder-state FX.052 enrollment comes from voluntary movement then independent source-specific hurt; motion/FX themselves add0.'},
   {'evidence':ref(p50),'distinction':'050 direct chance/attribute damage refusal with charge owner and regen reconciliation.052 does not re-award charge; grant and later hurt consumer are separate, with grounded invalidation and coalescing shared across producers.'},
   {'evidence':ref(p51),'distinction':'051 prepaid timed potion death token plus separate UUID/perk cooldown, expiry and teardown.052 has no potion/cooldown owner: repeated flight marks coalesce and onGround invalidates source membership. Prepayment/token analogy acknowledged; novelty rests on whole source membership lifecycle, not alternative effect or resource values.'}],
 'whole_chain_observation':observations,
 'application':'原程序的拒伤资格应明确来源、消费条件和失效条件；发射或位移特效不能冒充最终拒伤回执。Boss拒控提示要由最终拒控结果触发，不能从曾授予的标记推断当前有效；普通阴阳体质不新增灰字。仅研究，不引入新道具或改变生产。',
 'critical_boundaries':[
   'Historical fixed Astral1.16-indev/Observer1.5.2 source only; installed Dynasty binary/config/recipe/current-save availability not certified.',
   'Native MC/Forge item dispatch, entity collision, DamageSource equality, landing/hurt/tick ordering, canceled event behavior and server-client scheduling not expanded/executed. No guaranteed safe landing, bypass exploit, data race or successful movement claim.',
   'Motion S2C contains no protection result. Optional null vector is accepted by codec but normal producer supplies vector. No false positive claim of normal-path crash. Particle renderer/assets not visually accepted.',
   'Teleport safe-destination helpers and constellation resolver not expanded; neither is an independent candidate. CommonScheduler explored0, attunement partial/truncated exploration0.',
   'Shared resource, transport, helper/packet defects, actor/item variants and cleanup omissions0 additional credits. Nearest stamp/death-token families can cause merge/hold; max1 pending coordinator review.',
   'No production/test/art/background/sharedJar/user-instance/master checklist edits, no network/upstream execution/Java/Gradle/game/focus/audio/display actions, no hours claimed.'
 ],
 'counting':{'whole_policies_proposed':1,'accepted_credit':0,'runtime_credit':0},
 'next_work':'Coordinator independently accepts/merges/holds052. Next original-program source must be a genuinely different complete refusal/control/feedback owner, not another charge consumer or source constant. Attunement exploration remains incomplete, no exhaustion of Astral repository asserted.',
 'production_changes':False, 'runtime_executed':False, 'network_requests':0,
 'master_changes':False, 'checklist_deletions':0, 'hours_claimed':0}
covered = {}
for x in refs:
    a,z = x['lines']
    new = set(range(a,z+1))
    old = covered.setdefault(x['path'],set())
    assert not old.intersection(new)
    old.update(new)
doc.update(source_ranges=len(refs), unique_files=len(covered),
    full_files=sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),
    cited_lines=sum(map(len,covered.values())))
out = H/'immune-reference-batch-052.json'
with out.open('x') as f:
    json.dump(doc,f,ensure_ascii=False,indent=2)
    f.write('\n')
print(json.dumps({'evidence':ref(out),'ranges':doc['source_ranges'],
    'files':doc['unique_files'],'full_files':doc['full_files'],'lines':doc['cited_lines'],
    'credit':0,'maximum_pending':1}))

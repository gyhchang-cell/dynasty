"""Fixed-local area control with retained tile objects and identity-weak release."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def load(p):return json.loads(p.read_text())
paths={'045':H/'immune-reference-batch-045.json','050':H/'immune-reference-batch-050.json',
 '052':H/'immune-reference-batch-052.json','053':H/'immune-reference-batch-053.json','054':H/'immune-reference-batch-054-screen.json'}
ds={k:load(p) for k,p in paths.items()}
v=ds['050']['provenances'][0];raw=(R/v['manifest_path']).read_bytes();assert sha(raw)==v['manifest_sha256']
m=next(x for x in json.loads(raw) if x['repo']==v['repo']);es={x['path']:x for x in m['files']}
prefix='src/main/java/hellfirepvp/astralsorcery/';refs=[]
def source(n,a=1,z=None):
 e=es[prefix+n];b=(R/e['source']).read_bytes();ls=b.decode().splitlines();z=z or len(ls)
 assert 1<=a<=z<=len(ls) and sha(b)==e['sourceSha256']
 refs.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],
 'lines':[a,z],'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(ls[a-1:z]).encode()),'reading_context':'actual_read055'})
full=['common/constellation/mantle/effect/MantleEffectHorologium.java',
 'common/constellation/effect/aoe/CEffectHorologium.java','common/data/sync/server/DataTimeFreezeEffects.java',
 'common/util/time/TimeStopEffectHelper.java','common/data/config/registry/TileAccelerationBlacklistRegistry.java',
 'common/data/config/registry/sets/TileAccelerationBlacklistEntry.java','common/data/sync/client/ClientTimeFreezeEffects.java',
 'client/event/TimeStopEffectHandler.java','common/data/config/base/ConfigDataAdapter.java','common/data/config/base/ConfigDataSet.java']
for n in full:source(n)
source('common/util/nbt/NBTHelper.java',413,425)
reuse45={'common/util/time/TimeStopController.java','common/util/time/TimeStopZone.java',
 'common/event/helper/EventHelperEntityFreeze.java','common/data/sync/SyncDataHolder.java',
 'common/network/play/server/PktSyncData.java','common/network/login/server/PktLoginSyncDataHolder.java',
 'common/data/sync/SyncDataRegistry.java','common/data/sync/base/AbstractData.java',
 'common/data/sync/base/AbstractDataProvider.java','common/data/sync/base/ClientData.java',
 'common/data/sync/base/ClientDataReader.java','common/data/sync/server/DataTimeFreezeEntities.java',
 'common/data/sync/client/ClientTimeFreezeEntities.java'}
for x in ds['045']['source_refs']:
 if x['upstream_path'].removeprefix(prefix) in reuse45:
  refs.append(dict(x,reading_context='exact045_control_transport_support_reused0_zone_controller_revisited055'))
reuse54={'common/constellation/mantle/MantleEffect.java','common/item/armor/ItemMantle.java',
 'common/registry/RegistryMantleEffects.java','common/constellation/IWeakConstellation.java',
 'common/constellation/ConstellationRegistry.java','common/constellation/IConstellation.java',
 'common/registry/RegistryItems.java','common/registry/internal/PrimerEventHandler.java',
 'common/registry/internal/InternalRegistryPrimer.java','common/auxiliary/charge/AlignmentChargeHandler.java',
 'common/CommonProxy.java','common/event/handler/EventHandlerCache.java','AstralSorcery.java',
 'common/network/PacketChannel.java','common/network/base/ASPacket.java',
 'common/network/channel/SimpleSendChannel.java','common/network/channel/BufferedReplyChannel.java',
 'common/util/nbt/NBTHelper.java','common/util/NameUtil.java'}
for x in ds['054']['source_refs']:
 if x['repo']=='HellFirePvP/ObserverLib' or x['upstream_path'].removeprefix(prefix) in reuse54:
  refs.append(dict(x,reading_context='exact054_mantle_resource_nbt_bootstrap_reused0'))
for x in ds['050']['source_refs']:
 if x['upstream_path']==prefix+'client/ClientProxy.java':refs.append(dict(x,reading_context='exact050_client_handler_registration_reused0'))
for x in ds['052']['source_refs']:
 if x['upstream_path']==prefix+'common/util/MiscUtils.java' and x['lines']==[128,137]:refs.append(dict(x,reading_context='exact052_enum_helper_reused0'))

ledger=A/'immune-feedback-research/reviewed.json';lb=ledger.read_bytes();rows=json.loads(lb);idx={x['id']:x for x in rows}
policy='astralsorcery-native-area-tick-list-capture-with-position-dedup-and-class-qualified-stale-object-release'
assert policy not in {x['semantic_dedup_key'] for x in rows}
fields=['id','status','repo','commit','category','semantic_dedup_key','count_unit','full_chain_observation','concrete_observation','application_to_boss_immune','limitations','research_credit','reviewed_utc']
dist={
 'wizardry-slowtime-control-orphan-world-cleanup':'Wizardry restores updateBlocked on live entities by host search. Astral physically removes tickable tile objects from a world list, privately caches by position and later reinserts retained objects after current block factory/class test, without live tile identity or overlap ownership. Whole capture/release policy proposed, not merely entity versus block target type.',
 'wizardry-native-block-hosted-statue-placement-denial-and-actor-restoration':'Statue captures a living actor in a newly placed block host and restores via spawn. Astral leaves blocks in place, removes existing tile tick participation and reinserts retained objects; no actor-to-statue or native replacement transaction. Class-compatible replacement and overlapping zone release are distinct ownership boundaries.',
 'roots-native-area-replenishes-consumed-effect-before-target-update-veto-with-global-refresh-exemption-and-terminal-source-fallthrough':'Roots renews a disposable potion consumed on LivingUpdate and removal can damage. Astral maintains autonomous zones, blocks tile dispatch by list removal and must explicitly restore retained tile objects. Shared entity-update veto alone adds0; area timer/particles are not novelty.',
 'astralsorcery-native-vortex-renews-object-timeout-with-dimension-id-freeze-membership-and-change-only-server-receipts':'Accepted045 owns Vortex direct entity object timeout plus dimension/intID sets; area helper classes were support0 with explicit no area-producer proposal.055 primary mantle produces real zones that seize tile tick-list membership and release cached objects. Shared entity maintenance, geometry helpers and packet infrastructure remain0; no recredit for having read these classes before.'}
cmps=[]
for k,val in dist.items():
 if 'vortex' in k:
  c=next(x for x in ds['053']['dedup_snapshot']['comparisons'] if x['accepted_id']==k)
  assert all(idx[k][f]==v for f,v in c['complete_semantic_decision_read'].items())
  q=c['complete_semantic_decision_read']
 else:q={f:idx[k][f] for f in fields}
 cmps.append({'accepted_id':k,'complete_semantic_decision_read':q,'distinction':val})
progress_path=A/'immune-feedback-research/progress.json';progress=load(progress_path);assert len(rows)==progress['reviewed_effective_semantic_dedup']
obs=[
 'Primary complete producer is registered Horologium mantle: actual MantleEffect constructor attaches its hurt listener; current equipped enabled constellation + PlayerEntity + server + nonfire damage + no MANTLE cooldown + hasCharge qualify. It creates zone excluding current player numeric ID, sets item cooldown, then drains charge with return ignored. It never cancels/reduces original hurt, never requires amount>0 or hostile attacker. No intervening charge mutation is established in the shown create/cooldown path; ignored return alone does not prove normal free-zone/payment failure. Existing050 resource/054 equipment registration retained0. Defaults range20/duration180/cooldown1000/cost400 only, not installed config.',
 'freezeWorldAt always constructs active TimeStopZone, appends to static map keyed world dimension, attempts display-data ADD and returns zone; it does not verify provider presence, world side, terrain membership or any actual frozen target. Primary caller is server. Zone retains World, fixed BlockPos/range/controller and tick budget; no source-stack/caster tether or drop/unequip revocation. Owner exclusion is numeric entity ID, not UUID/generation; owner movement does not move zone.',
 'Actual controller registered SERVER START checks expiration before work, invokes onServerTick then checks again. Zone decrements lifetime before scanning, so final positive-life invocation can capture and restore within same handler. Scan enumerates intersecting chunk coordinates using world.getChunk (no explicit loaded-only guard), iterates chunk tile map, requires ITickable/nonblacklisted, spherical BlockPos.withinDistance and presence in world.tickableTileEntities. It removes live tile from that world list then caches reference. No block replacement, NBT snapshot, scheduled block/fluid tick queue or all-world-time freeze. Native world tick scheduling/chunk acquisition remains external.',
 'safeCacheTile deduplicates solely by position after removal, not by object identity. A replacement at same position can be removed but not added to that zone cache if the old object is already cached. Other zones normally see a tile absent from world tick list and do not take their own lease. There is no global per-tile owner set/refcount or saved original membership generation. Conditional replacement/overlap consequences depend on native tick ordering; no reproduced permanently paused tile claimed.',
 'stopEffect visits retained tiles, queries CURRENT block state at cached position, requires state block hasTileEntity and constructs a fresh tile solely for compatibility test. It accepts when newTile.class.isAssignableFrom(cached.class), then adds the OLD cached object to world.tickableTileEntities. It never compares current world tile object, removed flag, native generation, prior insertion or another zone still covering the position. It clears cache and sets active=false afterward. This is class-qualified retained-object release, not restore-current-object or atomic ownership transfer; constructors/native world operations can have external effects and no success guarantee is made.',
 'Overlapping zones may capture only through whichever scan finds actual world-list presence first. Expiring that holder reinserts regardless of others. Later remaining-zone scans can recapture depending list iteration/phase; do not promise continuous pause or a definite free-running tick. Restore can reinsert a retained object even after same-compatible-class replacement; static boundary only, not a claim about engine behavior/duplication exploit. Class/default blacklist checks apply on capture, not again on release.',
 'Blacklist entry requires tickable class, excludes explicit errored class/subclasses and configured entries. Entry tries loaded class assignability, otherwise lowercased type-registry-name or class-name prefix. Config adapter returns empty list before built; after build lazily caches deserialized values. Default list includes piston/storage and Astral network/altar/ritual tiles; defaults are not proof installed config built. Normal CEffectHorologium acceleration catches exceptions and adds errored tile class, so that shared list can later affect capture. It does not retroactively unfreeze cached tiles.',
 'Same zone also suppresses living updates/knockback through existing HIGHEST EventHelperEntityFreeze -> skipLivingTick. Area controller requires alive/positive health, excludes dying dragon, configured player policy and optional owner numeric ID, tests current entity corner distance. It calls existing maintenance (hurt timers/interpolation/travelZERO/dragon holding phase) then server cancellation; not damage immunity or all physical motion freeze. LivingDestroyBlock uses direct-membership path only, so area alone does not confer that veto. All shared045 entity mechanics0; novelty claim is whole tile membership capture/release with zone lifetime.',
 'Alternate fixed-source call site CEffectHorologium.playEffect corrupted branch finds FIRST zone at equal center only (no controller/range/source match), creates noPlayers100 if absent, otherwise resets its TTL100 without changing range/controller. Thus shared-center refresh can extend an existing zone with different owner/player policy. Entire concrete CEffect file read; ritual pedestal/parent/property/activation pipeline is NOT expanded and gets no independent complete-producer or second reference claim. Primary mantle chain is sufficient entry; normal acceleration branch is context0.',
 'Zone publication is separate List<TimeStopEffectHelper> by dimension plus ADD/REMOVE change queue. Helper serializes center/range/controller, no zone UUID/nonce or remaining TTL. Equality/hash use only center+range, omit controller/owner. Multiple equal-geometry zones can coexist but remove(effect) removes first equal helper, potentially different policy than the expired server zone. Client list mirrors those actions with same equality and no expiry; neither side uses target/tile acceptance data. Source lifetime and display-list identity are not identical.',
 'SyncDataHolder SERVER END emits queued diff and clears changes/dirty flags, broadcast via registered PktSyncData; client enqueues concrete reader. Full login snapshot includes dimension lists and client full reader first clears all; diff ADD appends/REMOVE first-equal/CLEAR drops dimension. Do not import045 direct-entity absent-dimension-full-sync limitation into this area reader. No ACK, sequence, TTL, native delivery or rendering guarantee; primary zone can exist even when display provider absent.',
 'Registered client END TimeStopEffectHandler looks up current world list and calls helper. Helper queries current alive target-controlled nearby living actors, eligible nearby tile types and random positions/lightning, without knowing actual server cachedTiles or successful world-list removal. Particles can describe still-ticking/unaccepted tiles or stale geometry, and source cape sparkles only use cooldown-dependent probabilities. No dedicated per-control rejection, restoration, payment or immune gray-text receipt; actual assets/renderer/audio untested.',
 'World unload native EventHandlerCache calls SyncDataHolder.clearWorld first, then TimeStopController.onWorldUnload. Server data.clear(dim) removes active display list but neither marks dirty nor removes queued changes; controller restores every cached zone then removes dimension map, without removeEffect action. Client clearWorld does not call data.clear. Hence missing explicit per-world CLEAR and retained pending actions are source boundaries, not measured stale display. Client disconnect explicitly clearClient removes all lists. Server stop clears display data; active-zone cleanup is tied to world unload, no separate controller clear-all in the shown stop hook. Native stop/unload order unexecuted.',
 'No shown durable zone/cached-tile NBT state: helper NBT is network representation only, including no TTL. World unload explicitly releases, not suspend/resume. Direct living membership, shared charged trigger, config defaults, alternate ritual, target IDs, packet bugs and helpers are0 extra. Proposed one whole spatial tick-list capture with position-only cache/class-qualified release and geometry-keyed feedback. Four full nearest saved decisions compared plus050-054 whole mechanisms; primary distinction is ownership/restoration of existing world update entries, not another item, radius, mana cost or visual.'
]
doc={'schema_version':1,'owner':'program-feedback-review-055','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'ONE_WHOLE_AREA_TICK_LIST_CAPTURE_RELEASE_POLICY_PENDING_INDEPENDENT_REVIEW','research_credit':0,'maximum_proposed_credit':1,
 'repo':m['repo'],'commit':m['commit'],'semantic_dedup_key':policy,'provenances':ds['050']['provenances'],'source_refs':refs,
 'prior_read_reuse':{'evidence':[ref(p) for p in paths.values()],
 'scope':'Ten complete files newly cited055 plus complete position helpers; enum helper exact052 reused0. TimeStopZone210/Controller179 revisited fully, exact045 bindings retained; other045 transport/native hooks and054 mantle/resource/registry support reused0. Full TimeStopEffectHelper200 now actually read, never treating old0451..101 as EOF. CEffect concrete alternate caller read but parent ritual chain unexpanded.'},
 'baseline':{'progress':ref(progress_path),'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'old_verifier_or_ledger_rerun':False},
 'dedup_snapshot':{'path':str(ledger.relative_to(R)),'sha256':sha(lb),'rows':len(rows),'comparisons':cmps,
 'scope':'Three complete saved decisions newly read; full045Vortex decision previously read053 reused verbatim/checked unchanged. Broad483 text screen is not483 old source reads.'},
 'existing_work_overlap':[{'evidence':ref(p),'distinction':'Shared resource/registration/state and previous mechanism retained0.055 proposes only whole world tick-list ownership/release; neither new charge consumer nor extra entity-freeze constant.'} for p in [paths['050'],H/'immune-reference-batch-051.json',H/'immune-reference-batch-052.json',paths['053'],paths['054']]],
 'whole_chain_observation':obs,
 'application':'原程序控制應記住實際接管的物件及其身份，重疊施加者退出時不能只按位置或類別恢復舊物件；同步回執也需要對應同一份狀態。只研究，Boss免控提示仍須最終拒控原因，不新增時停玩法或普通體質灰字。',
 'critical_boundaries':['Historical Astral1.16 source, not current Dynasty binary/runtime. No game/Java/Gradle/native tick/chunk acquisition/constructors/render/audio/network executed.',
 'Native World tick-list invariants/iteration, tile removal/replacement, class factory effects, region chunk loading and server-stop/world-unload order unexpanded. Static list mutation is read, not proof of actual paused machine or working restore; no duplicated/orphan exploit claim.',
 'Full mantle entry and shared source/tick/control/feedback/exit shown. Alternate corrupted ritual concrete method read only; parent pedestal/property lifecycle not claimed complete and adds0.',
 'Existing045 includes whole zone/controller as support0 and independent entity direct-membership owner. Reuse does not itself establish novelty; coordinator can merge/hold055.',
 'Geometry-only helper equality/identity-weak tile restore are mechanism boundaries, not each separate implementation credit. Max1 pending0; no production/test/art/background/sharedJar/instance/master/checklist changes or hours claim.'],
 'counting':{'whole_policies_proposed':1,'accepted_credit':0,'runtime_credit':0},
 'exploratory_exclusions':['IE event keyword scan and missing concrete effect source paths did not establish a complete new candidate;0, no repository exhaustion claim.',
 'IronSpells SoulBurnMobEffect class read for discovery: multiplicative heal amount reduction alone insufficient new whole mechanism. No pinned-source binding or full upstream chain claimed for that discarded lead;0.'],
 'next_work':'Independent review055; next genuinely distinct source only after bounded primary lifecycle closed. Shared temporal helpers/resource variants do not count.',
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0}
covered={}
for x in refs:
 b=(R/x['path']).read_bytes();assert sha(b)==x['file_sha256']
 a,z=x['lines'];new=set(range(a,z+1));old=covered.setdefault(x['path'],set());assert not old.intersection(new);old.update(new)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-055.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'ranges':doc['source_ranges'],'files':doc['unique_files'],'full_files':doc['full_files'],'lines':doc['cited_lines'],'credit':0,'maximum_pending':1}))

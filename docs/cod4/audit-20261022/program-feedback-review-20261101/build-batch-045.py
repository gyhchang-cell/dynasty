#!/usr/bin/env python3
"""Pinned Astral Sorcery vortex/direct freeze lifetime proposal, maximum one."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
C=R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-011'
mp=C/'source-manifest.json';m=json.loads(mp.read_text())[0];assert m['commit']=='3599b4819dba3553896f87c0505ccd84bafb0550'
prefix='src/main/java/hellfirepvp/astralsorcery/';entries={x['path']:x for x in m['files']}
whole=['common/event/helper/EventHelperEntityFreeze.java','common/util/time/TimeStopController.java','common/util/tick/TimeoutList.java',
 'common/data/sync/server/DataTimeFreezeEntities.java','common/data/sync/client/ClientTimeFreezeEntities.java','common/network/play/server/PktSyncData.java',
 'common/data/sync/SyncDataHolder.java','common/util/time/TimeStopZone.java','common/crafting/nojson/fountain/FountainEffectVortex.java',
 'common/crafting/nojson/fountain/FountainEffect.java','common/crafting/nojson/FountainEffectRegistry.java','common/data/config/registry/TechnicalEntityRegistry.java',
 'common/block/tile/fountain/BlockFountainPrimeVortex.java','common/event/handler/EventHandlerCache.java','AstralSorcery.java',
 'common/network/PacketChannel.java','common/data/sync/base/AbstractData.java','common/network/login/server/PktLoginSyncDataHolder.java',
 'common/network/base/ASPacket.java','common/network/channel/SimpleSendChannel.java','common/network/channel/BufferedReplyChannel.java',
 'common/data/sync/SyncDataRegistry.java','common/data/sync/base/AbstractDataProvider.java','common/data/sync/base/ClientData.java',
 'common/data/sync/base/ClientDataReader.java','common/network/base/ASLoginPacket.java']
selected={'common/tile/TileFountain.java':[[1,265]],'common/CommonProxy.java':[[146,260],[353,363]],
 'common/util/entity/EntityUtils.java':[[100,114]],'common/util/MiscUtils.java':[[219,228],[279,291]],
 'common/util/time/TimeStopEffectHelper.java':[[1,101]],'common/registry/RegistryBlocks.java':[[121,123]],
 'common/registry/RegistryTileEntities.java':[[38,38],[46,46]],'common/util/data/ByteBufUtils.java':[[186,192],[318,330]]}
def sources(n,ranges=None,kind='actual_read045'):
 e=entries[prefix+n];raw=(R/e['source']).read_bytes();lines=raw.decode().splitlines();out=[]
 for a,z in ranges or [[1,len(lines)]]:
  out.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],'lines':[a,z],
   'file_sha256':sha(raw),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(lines[a-1:z]).encode()),'reading_context':kind,
   'purpose':'Whole class or explicit complete methods/declarations; one native vortex/direct-freeze policy only, helpers/zone mode0.'})
 return out
refs=[x for n in whole for x in sources(n)]+[x for n,ranges in selected.items() for x in sources(n,ranges)]
aux=[x for n in ['common/data/sync/client/ClientTimeFreezeEffects.java','client/event/TimeStopEffectHandler.java'] for x in sources(n,kind='auxiliary_area_visual_context_zero')]
prov={'repo':m['repo'],'branch':m['branch'],'tag':m.get('tag'),'commit':m['commit'],'git_tree':m['git_tree'],
 'manifest_path':str(mp.relative_to(R)),'manifest_sha256':sha(mp.read_bytes()),
 'commit_metadata_path':str((C/'provenance/HellFirePvP__AstralSorcery/commit.json').relative_to(R)),
 'tree_metadata_path':str((C/'provenance/HellFirePvP__AstralSorcery/tree.json').relative_to(R))}
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
distinct={
 'wizardry-slowtime-final-update-control-exclusion':'Host interval updateBlocked vs renewable object timeout plus separate dimension/intID membership. Direct freeze still manually travels and advances hurt clocks; no persistent updateBlocked mutation.',
 'wizardry-slowtime-control-orphan-world-cleanup':'No world scan for missing host; producer loss leaves shared20-END-update timeout. Expiry looks up current entity world/id rather than captured membership key. Multiple producers renew one list entry, not range-outside unlock.',
 'bumblezone-native-paralysis-authoritative-duration-clear-receipt-versus-client-render-lazy-expiry':'No MobEffect duration or zero-clear packet. Dirty dimensions send complete integer membership sets; clients have no TTL and replace only present dimension keys, even on full sync. Actual membership consumer is server update/knockback veto plus client particles, not local forced effect map.',
 'betweenlands-native-nonrenewing-environmental-footing-lease-with-heavyweight-first-mud-veto-and-sludge-specific-control-skip':'Nonrenewing absolute player deadline for terrain permission differs from continuously refreshed object list counter and dimension/entity-ID denial membership; no heavyweight or geometry-footing exemption here.',
 'icefire-native-frozen-admission-and-server-fire-death-expiry-release-versus-shell':'Entity-owned frozen timer with fire/death clearing differs from global object timeout and numeric membership. Dead/dying skips update veto without removing membership; block-destruction still uses membership directly. No fire cure or per-entity saved frozen state.',
 'roots-native-area-replenishes-consumed-effect-before-target-update-veto-with-global-refresh-exemption-and-terminal-source-fallthrough':'Roots consumes one potion token each target update and removal can hurt; Astral retains membership until separate server timeout, renews without dirtying unchanged membership, manually advances selected damage/movement state even on knockback-hook calls. No effect-remove callback/refresh-global flag.'}
cmps=[{'accepted_id':k,'full_semantic_decision_read':{a:v for a,v in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':why} for k,why in distinct.items()]
prior=json.loads((H/'immune-reference-batch-044-screen.json').read_text());migp=R/prior['migration_overlap_screen']['path'];mr=migp.read_bytes();mi={x['candidate_id']:x for x in [json.loads(l) for l in mr.decode().splitlines() if l.strip()]}
mids=['a23e5ed56cdd1ec1e084','cbc96209dcff750b83af','206440a906a99cc580c6','2242ddb31ad789c7c3ec','83c1a291a29a171db9a7']
keys=['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
mc=[{'accepted_id':k,'complete_semantic_decision_read':{a:mi[k][a] for a in keys},'distinction':'Existing Astral player research/knowledge share/crystal properties/tree beacon/gateway persistent owners were read as whole semantic judgments. None owns vortex direct freeze object timeout and dirty membership lifetime. Their helper/registration/storage context0 new credit.'} for k in mids]
doc={'schema_version':1,'owner':'program-feedback-review-045','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'PENDING_INDEPENDENT_REVIEW_MAXIMUM_ONE_VORTEX_OBJECT_TIMEOUT_AND_DIMENSION_MEMBERSHIP_LIFECYCLE',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'astralsorcery-native-vortex-renews-object-timeout-with-dimension-id-freeze-membership-and-change-only-server-receipts',
 'repo':m['repo'],'commit':m['commit'],'provenances':[prov],'source_refs':refs,'auxiliary_refs':aux,
 'baseline':{'accepted042_receipt':prior['baseline']['accepted042_receipt'],'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'044_zero':ref(H/'immune-reference-batch-044-screen.json')},
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(rows),'comparisons':cmps,'scope':'Six whole accepted judgments read; not476original source-chain rereads.'},
 'migration_overlap_screen':{'path':str(migp.relative_to(R)),'sha256':sha(mr),'rows':len(mi),'comparisons':mc,'scope':'Five whole Astral nine-field substantive judgments read. No claim all original migration methods reread.'},
 'whole_chain_observation':[
  'Actual @Mod constructor initializes CommonProxy and attaches native Forge bus; CommonProxy initializes packet channel, SyncDataHolder concrete providers, external ObserverLib TickManager registration and EventHelperEntityFreeze native listeners. Native TileFountain.tick dispatches current effect after multiblock and base1 liquid payment. Prime provider returns registered static FountainEffectVortex. Block/tile assignment declarations are read; full external registry-primer injection and full multiblock/parent tile engine remain boundaries.',
  'Tile active counter advances through STARTUP60/PREPARATION200 then stays RUNNING; server Vortex tick calls pullEntities only RUNNING or later. It excludes null/dead/players/config technical type. Captured box is5x5x5 below fountain; small targets motionZERO, larger-volume targets reposition near center, dragon manually livingTick with MOB_GRIEFING temporarily false then restored without finally. Pull box grows14, removes captured list, then eligible remaining also freeze before vortex motion/near-center relocation. No generic Boss exclusion; dragon explicitly handled.',
  'Captured density extra liquid cost occurs after control requests and return bool ignored; pull-zone targets are controlled after that call even if extra payment exhausted supply. Base next tile tick payment controls continued operation. Freeze bool ignored. Technical blacklist and null/dead/player checks are source admission; no potion applicability layer. Capture particles/segment transition do not certify a controlled target.',
  'EventHelperEntityFreeze.freeze calls TimeoutList.setOrAddTimeout(20,entity). New adds and existing setTimeout both returntrue; not first-insertion-only. It then attempts SyncDataHolder executeServer freezeEntity and returns true even if provider missing. Timeout key is Entity equality/object reference, no source owner lease/refcount. Multiple fountains reset one timeout; removing one source does not unfreeze while another renews.',
  'DataTimeFreezeEntities stores HashMap<dimensionKey,Set<integerEntityID>>, not UUID/entity/expiry. Add marks dirty only if set changed. Repeated same-dimension refresh keeps timeout alive without new membership packet. Server END TimeoutList decrements once per dispatched call, delegate unfreezes before iterator removal at<=0. Effect loss/leave capture/pull range/prime replacement stops renewal but retains residue up to remaining20 END dispatches; no onReplace server mass release.',
  'Expiry delegate uses retained entity current world dimension and current numericID, not key captured when originally added. If native lifetime keeps the same object but changes dimension/ID, removal can miss old membership. Old-ID reuse is not prevented by membership type. These are conditional static boundaries; native transfer object/ID semantics not executed. List has no shown external clear API through EventHelperEntityFreeze; actual server/world cleanup clears data maps but does not clear this static timeout list.',
  'Native HIGHEST LivingUpdate and LivingKnockBack both call skipLivingTick. Direct membership bypasses control for dead/health<=0 or dying dragon but does not delete membership; same method may still consider area zones. Eligible server branch calls handleImportantEntityTicks then cancels. That helper decrements hurtTime/hurtResistantTime, copies pose/position interpolation fields, calls travel(ZERO), and can force dragon HOLDING_PATTERN. Thus knockback delivery also runs these maintenance writes, not solely normal ticks. No full motion freeze or zero damage guarantee.',
  'LivingDestroyBlock uses isFrozenDirectly alone and cancels irrespective of alive/dragon phase gate; it does not consult area containment. Client skipLivingTick can emit random entity particles but direct membership branch only returns true server-side; no equivalent direct client tick veto asserted. Physical pull/zeroing is source action; retained membership veto does not save/restore prefreeze velocity/AI/dragon phase.',
  'SyncDataHolder marks keys dirty and at SERVER END serializes changed dimension sets then clears dirty flags and broadcasts through SimpleSendChannel PacketDistributor.ALL. Data writer sends empty set for a dirty dimension whose last member disappeared. CommonProxy registers sync before freeze timeout, but ObserverLib scheduler internals not adopted here, so exact same/next-tick send ordering not promised. No applied-control acknowledgement, refusal reason, nonce or sequence.',
  'PktSyncData registered play packet, ASPacket reception dispatches client, handler enqueueWork applies concrete reader. Reader replaces sets for dimension keys present in packet, accepts numericIDs without current entity relookup/UUID/generation. Full login packet calls writeAll and same reader without first clearing absent dimensions. Initial membership data exists as login path, not verified delivery. Login acknowledgement is generic sync completion, not target freeze acceptance.',
  'World unload calls SyncDataHolder.clearWorld: server data.remove(dim) without markDirty; client world unload does not clear here. Disconnect clears all client data, server stop clears membership+syncTypes, but helper timeoutlist not named in this cleanup. Therefore no universal per-world client clear receipt or same-session old-world immunity to stale ID sets. Pending network work/engine disconnect ordering not executed.',
  'Direct client particle helper samples current entity bounds and submits configured EffectHelper chain. Separate ClientTimeFreezeEffects/TimeStopEffectHandler concern area effects, not direct timeout membership and are auxiliary0. TimeStopZone full class read for actual shared maintenance/area fallback; block-tick capture/restore and separate area producer not proposed here. All callbacks, fields, config targets, packets, dragon branches, rendering and shared tick helpers one complete candidate max1.'
 ],
 'critical_boundaries':[
  'Pinned historical1.16-indev commit, not release or Dynasty1.20.1 runtime. No Java/Gradle/game/upstream execution, external acquisition, asset/media edit, shared Jar or main ledger/session/checklist mutation.',
  'ObserverLib TickManager/ITickHandler native distribution, Forge event/damage/knockback/potion/teleport internals and actual entity IDs across worlds not expanded. Registration call order alone is not dispatch order proof.',
  'Native Entity.travel(ZERO) still uses engine physics; this is AI/update veto with selected maintenance, not total stopped time. Damage iframe decrement can also happen per knockback callback; no runtime frequency claim.',
  'Technical registry uses configured type membership; default entries read, actual installed config adapter population not evaluated. No universal Boss immunity/player immunity: only Vortex producer excludes players.',
  'Partial TileFountain1-265 contains complete actual tick/source-selection/payment/segment methods; persistent NBT methods beyond range not read or claimed. RegistryBlocks121-123 and RegistryTileEntities38/46 are declarations only, not full registration methods. CommonProxy selected whole methods only.',
  'FountainVortex initial large output clipped; complete missing298-370 recovered explicitly. TimeStopZone header1-40 recovered; no truncated source range counted as fully read. Metadata searches are discovery0.',
  'Full/diff reader absence is not explicit dimension clearing. Client disconnect reset exists; do not claim never clears. Expiry current-dimension mismatch is conditional, not a reproduced stale-freeze exploit.',
  'Native API submission and client state application are not measured networking/visible particle/actual control receipts. No new gray text. Shared server registry/cost/storage/support does not earn separate credit.'
 ],
 'application':'控制期限應與施加時目標UUID、維度和世代綁定；解除必須刪除當初那份狀態，不能按已移動物件的當前身份猜測。刷新、最後一次施加者離開、世界卸載和客戶端清理各有不同回執責任；不能把傳送成功或粒子生成當作拒控接納。僅研究。',
 'counting':{'whole_candidate':1,'accepted_credit':0,'helper_variant_parameter_credit':0,'native_acceptance':0},
 'next_work':'Coordinator independent whole-policy review max1or0. Specialist next independently audits current Dynasty infusion95/99/102 contract and historical changes, proposal only until applicable accepted1000 gate confirmed.'}
covered={}
for x in refs:
 a,b=x['lines'];now=set(range(a,b+1));prev=covered.setdefault(x['path'],set());assert not prev.intersection(now);prev.update(now)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(v)==len((R/k).read_text().splitlines()) for k,v in covered.items()),cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-045.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'ranges':len(refs),'files':len(covered),'lines':doc['cited_lines']},ensure_ascii=False))

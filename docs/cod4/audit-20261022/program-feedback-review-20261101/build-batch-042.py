#!/usr/bin/env python3
"""Fixed-local consumed-effect update refusal proposal, reusing exact041 support."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
rel=lambda p:str(p.relative_to(R))
def ref(p):return {'path':rel(p),'sha256':sha(p.read_bytes())}
p41=H/'immune-reference-batch-041.json';raw41=p41.read_bytes();old=json.loads(raw41)
assert sha(raw41)=='b674cf5e13c20c08c9747a763c7bd0ed2b93cf4ebb065ae988f6ebb5eb2a9f2b'
v=old['provenances'][0];m=next(x for x in json.loads((R/v['manifest_path']).read_text()) if x['repo']==v['repo'])
entries={x['path']:x for x in m['files']};prefix='src/main/java/epicsquid/roots/'
specs=[('spell/SpellTimeStop.java',None),('entity/spell/EntityTimeStop.java',None),
 ('potion/PotionTimeStop.java',None),('entity/spell/EntitySpellModifiable.java',None),
 ('network/fx/MessageTimeStopStartFX.java',None),('properties/PropertyTable.java',None),
 ('particle/ParticleUtil.java',[[97,108]]),('spell/SpellBase.java',[[407,429]]),('config/EntityConfig.java',[[319,349]])]
refs=[]
for n,ranges in specs:
 e=entries[prefix+n];b=(R/e['source']).read_bytes();lines=b.decode().splitlines()
 for a,z in ranges or [[1,len(lines)]]:
  refs.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],'lines':[a,z],
   'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(lines[a-1:z]).encode()),
   'reading_context':'new_actual_source_read042','purpose':'Concrete source/producer/removal/feedback or complete directly used support0; not per-file credit.'})
new=list(refs)
support={'Roots.java','RegistryManager.java','proxy/CommonProxy.java','spell/SpellRegistry.java',
 'init/ModEntities.java','init/ModPotions.java','init/ModSounds.java','init/ModDamage.java',
 'network/RootsPacketHandler.java','network/ClientMessageHandler.java','network/MessageHandler.java','event/ClientTickHandler.java',
 'item/ItemStaff.java','spell/info/StaffSpellInfo.java','spell/info/storage/StaffSpellStorage.java',
 'util/EntityUtil.java','util/EntityLists.java','util/ServerHerbUtil.java','util/types/RegistryItem.java',
 'modifiers/instance/staff/StaffModifierInstanceList.java','modifiers/instance/staff/ModifierSnapshot.java',
 'EventManager.java','spell/SpellBase.java','init/ModItems.java','particle/ParticleUtil.java','config/EntityConfig.java'}
for x in old['source_refs']:
 name=x['upstream_path'].removeprefix(prefix)
 if name not in support or (name=='config/EntityConfig.java' and x['lines']!=[1,61]):continue
 assert sha((R/x['path']).read_bytes())==x['file_sha256']
 y=dict(x);y['reading_context']='exact041_already_read_support_reused_not_reread';y['purpose']='Existing complete041 method/registration support0; Geas branches and other spell arms not proposed again.';refs.append(y)
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
dist={
 'wizardry-slowtime-final-update-control-exclusion':'Prior retained updateBlocked toggled by host interval. Here source repeatedly adds a potion token; target LivingUpdate removes token before canceling that update. No persisted updateBlocked or prior-motion restore. Removal can itself invoke cold-damage callback, so clearing is part of pulse consumption, not only end-of-control.',
 'wizardry-slowtime-control-orphan-world-cleanup':'Prior world END scans orphan markers and restores updateBlocked. Current target consumes its next received time_stop in its own update even if source already expired, so no separate host search or orphan-marker sweep appears. This does not prove exact native skipped tick count or all cleanup cases.',
 'bumblezone-native-paralysis-authoritative-duration-clear-receipt-versus-client-render-lazy-expiry':'Prior explicit duration/zero effect sync and persistent effect immobility/render state. Here source effect duration40 is not guaranteed40 frozen updates: consumer removes on next event then cancels. Start visual packet only coordinates, not accepted per-target state. No lazy-render state expiry protocol.',
 'icefire-native-frozen-admission-and-server-fire-death-expiry-release-versus-shell':'Prior entity-owned frozen timer, environmental release and current shell. Here area reapplication and destructive one-event consumption; no fire/death thaw branch or stored frozen flag. FIRE can run alongside repeated control; aftereffects are independent of core token admission.',
 'evilcraft-native-beam-additive-freeze-preserves-spirit-finite-lifespan-with-synced-control-state-and-visibility-gated-renderer':'Prior additive frozen stock suspends own remainingLife clock. Current controller owns independently decreasing lifetime; target consumes incoming effect before canceling its update. Source terminal onUpdate still falls through to a final application pass; no target lifetime preservation claim.'}
k34=list(dist)[-1];p37=H/'immune-reference-batch-037.json'
prior34=next(x['full_semantic_decision_read'] for x in json.loads(p37.read_text())['dedup_snapshot']['comparisons'] if x['accepted_id']==k34)
assert prior34=={k:v for k,v in by[k34].items() if k not in ['source_refs','auxiliary_refs']}
cmps=[{'accepted_id':k,'full_semantic_decision_read':{a:v for a,v in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':w,
 'reading_context':'Exact previously fully read034 decision reused from037; not claiming truncated042 output complete.' if k==k34 else 'complete_semantic_decision_read042'} for k,w in dist.items()]
mig=old['migration_overlap_screen'];mlraw=(R/mig['path']).read_bytes();mi={x['candidate_id']:x for x in [json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]}
for x in mig['comparisons']:assert all(mi[x['accepted_id']][k]==v for k,v in x['complete_semantic_decision_read'].items())
accept41=A/'immune-feedback-research/coordinator-roots-geas-acceptance-20261103.json'
assert sha(accept41.read_bytes())=='60c0783cbe8fb5c63542735077e7990258229b21e6d88014b955443f4537315d'
assert json.loads(accept41.read_text())['after_count']==475
k41=old['semantic_family']
cmps.append({'accepted_id':k41,'full_semantic_decision_read':{k:v for k,v in by[k41].items() if k not in ['source_refs','auxiliary_refs']},'reading_context':'complete newly accepted041 semantic decision read042 after coordinator acceptance','distinction':'Geas retains an attack-source suppression effect until type-dispatched removal; TimeStop replenishes and consumes an update-veto effect with shared refresh suppression and terminal controller fallthrough. Shared event handlers, registration and staff support earn0.'})
doc={'schema_version':1,'owner':'program-feedback-review-042','created_utc':datetime.now(timezone.utc).isoformat(),
 'repo':m['repo'],'commit':m['commit'],'provenances':old['provenances'],
 'status':'PENDING_INDEPENDENT_REVIEW_MAXIMUM_ONE_REPLENISHED_EFFECT_CONSUMPTION_UPDATE_VETO_WITH_REMOVAL_DAMAGE_AND_TERMINAL_SOURCE_PASS',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'roots-native-area-replenishes-consumed-effect-before-target-update-veto-with-global-refresh-exemption-and-terminal-source-fallthrough',
 'source_refs':refs,'prior_read_reuse':{'evidence':ref(p41),'new_ranges':len(new),'new_cited_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in new),'reused_ranges':len(refs)-len(new),'source_reread_credit':0},
 'baseline':{'accepted039_receipt':old['baseline']['accepted039_receipt'],'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'accepted041_receipt':ref(accept41),'041_original_proposal':ref(p41),'040_screen':old['baseline']['040_screen'],'040_credit':0},
 'dedup_snapshot':{'path':rel(lp),'sha256':sha(lr),'rows':len(rows),'comparisons':cmps,'reused034_decision':{'evidence':ref(p37),'accepted_id':k34},
   'scope':'Existing ledger metadata search, four newly read whole decisions plus one exact previously read034 decision, and newly accepted041 complete semantic decision. Not all475 source chains reread.'},
 'migration_overlap_screen':{'path':mig['path'],'sha256':sha(mlraw),'rows':len(mi),'comparisons':mig['comparisons'],
   'reuse_evidence':ref(p41),'scope':'Complete roots staff/library migration owner already read041, exact current comparison verified; TimeStop/EntitySpellModifiable metadata search yielded no named migration owner. No library/storage/cost recredit.'},
 'accepted041_comparison':{'evidence':ref(p41),'same_methods_support_only':True,
   'distinction':'041 Geas keeps a target effect while suppressing attack-source damage/target assignment and dispatches removal aftermath by actor type.042 time_stop is repeatedly consumed by LivingUpdate before update cancellation, with source-lifetime and shared refresh gate. One each only if independent review accepts distinct complete policies. Shared EventManager onDamage/onEntityTick, registry, staff and feedback queue support0.'},
 'full_chain':[
  'Existing exact041 native ItemStaff onItemRightClick -> cost check -> SpellBase wrapper -> concrete instantaneous SpellTimeStop.cast. Actual SpellRegistry instance/finalise, potion register, EntityTimeStop and RenderNull registration, message registration and mod lifecycle already read and reused exactly. New spell server chooses duration (LONGER then SHORTER overrides), builds EntityTimeStop, sets player UUID/position/modifier reference, attempts spawn, sends start FX and optionally attempts player SPEED. spawn result ignored; cast returnstrue on either side, so wrapper sound and noncreative server cost/cooldown do not establish area insertion or any accepted target.',
  'Actual parent is EntitySpellModifiable directly extending native Entity, not EntitySpellBase/EntityLifetimeBase. Constructor records instance, invisible/size and data-manager lifetime. onUpdate does not call native super; decrements own watched lifetime and setsDirty each delivered update, invokes onDeath and setDead at<=0. No side check in parent. EntityTimeStop.onDeath submits configured end sound. Child then continues its onUpdate without isDead/return gate: client smoke or server application still runs on terminal invocation.',
  'Server child caches AABB on first update using current position/radius, then queries living targets each update. Box is not recomputed after later source movement or config change; not a follow-caster field. Excludes every EntityPlayer. Optional PEACEFUL consults friendly classification; FAMILIARS uses generic owned-familiar test, not recorded caster UUID. There is no EntityUtil.isBoss call here. Actual native potion applicability remains a separate unverified admission gate.',
  'Each admitted-by-scan nonplayer sets static EntityTimeStop.refreshing=true, writes modifier core snapshot to target entityData, attempts addPotionEffect(time_stop,40), then resets static false. SLOW/WEAKNESS extended by40 and FIRE are attempted independently afterward. No result acknowledgment or rollback. Guards tolerate modifiersnull only for first two skip tests; later toArray/has dereference can fail. Flag is process-wide, not target/source keyed and has no finally; exception before reset can leave ittrue.',
  'Exact041 native EventManager.onEntityTick: if target currently has time_stop, first removePotionEffect(time_stop), then event.setCanceled(true), and continues remaining handler branches. It does not set NoAI, velocity or updateBlocked. Thus source effect is a replenished consumable control token, not a40-update durable latch. No native LivingUpdate cancellation contract or event ordering executed; do not assert full physical freeze, exact per-tick coverage or absence of other listeners.',
  'Concrete PotionTimeStop.removeAttributesModifiersFromEntity calls super and, unless shared refreshing flag istrue, attempts COLD_DAMAGE with configured cold_damage. It does not consult FREEZE modifier or saved snapshot, and ignores damage result. Consequently the explicit per-update remove outside the source refresh scope can invoke cold damage, not only natural final expiration. Source add/refresh callbacks within flagtrue suppress this branch if native engine invokes it there. Precise native remove-map/callback order and overlap/reentrancy not expanded.',
  'Same native onDamage checks current time_stop on the victim and multiplies event amount by0.1, before other later effects. Whether the removal-triggered COLD_DAMAGE still sees the effect cannot be inferred without matching native potion-removal order; no asserted4 or0.4 final HP. FREEZE is registered/accepted by SpellTimeStop but unused in the shown entity/potion final damage gate; not a separate modifier implementation reference.',
  'Ending source does not iterate targets or explicitly remove their current tokens. Any retained effect can be consumed by a later delivered target update (or other native removal); no orphan updateBlocked flag to sweep in this chain. Final source call may already sound/remove and still submit another token. Bonus slowness/weakness/fire has its own native lifetime, not an all-effects release at area death. Multiple sources overwrite same target snapshot and share one effect/refresh flag; no source-owned lease or reference counting.',
  'Parent entity NBT writes playerId and modifier core array, reads ModifierSnapshot; it does not write/read watched lifetime. Reconstructed EntityTimeStop(World) uses current base spell duration, not saved remaining/selected extended duration in shown reader. This is a static persistence boundary, not actual save/reload validation. Spawn runtime modifiers are live StaffModifierInstanceList reference; reloaded modifiers are frozen ModifierSnapshot. playerId is stored but is not read for target eligibility in EntityTimeStop.',
  'Start FX packet contains only xyz at caster; actual client registration/END runnable queue and concrete handler call glow helper with lifetime40. Coordinates are a snapshot with no entityID/UUID/dimension/accepted-target list/reason. No target-control receipt. Handler random nextInt(4) increments can be0 and has no world-null gate. New smoke helper and existing glow helper submit through external MysticalLib renderer with global random counter/particle-setting filter. Client area smoke uses fixed8-radius geometry, not server control AABB; second palette supplies red2 as green argument. These are visibility boundaries, not art work or additional credit.',
  'PropertyTable complete getRadius/default lookup read to bind axis ordering. Config TimeStop getters are fixed lazy lists through external parser. Existing exact041 spell getters/cost/payment/storage/source damage/context used without recount. One complete replenishment -> consumed update veto -> removal effect -> source terminal and feedback lifecycle max1; modes, fields, constants, packets and native helper boundaries0 extra.'
 ],
 'critical_boundaries':[
  'Fixed Roots1.12.2 commit, no imported behavior from modern Forge. Native Entity.onUpdate caller, LivingUpdate cancellation, potion map/removal/refresh callback ordering, NBT reconstruction/entity data sync and MysticalLib transport/renderer internals remain unexpanded. Static conditional mechanism only, no game/Java/Gradle/native/visual/audio acceptance.',
  'No explicit Boss exemption in area loop; blanket player exclusion is different. Friendly/familiar optional skip is not a Boss immune receipt. General EntityUtil ownership checks are not caster ownership checks.',
  'Source lifespan decrements both client/server codepaths and still falls through aftersetDead; do not promise synchronized timing or exactlyone end sound. Parent intentionally skips super.onUpdate; no inference that native ticksExisted is the control clock.',
  'Shared static refreshing flag is not a persistent freeze-state field. No finally/reentrant scope protection; native actual callbacks may differ. Removal cold-damage branch has no explicit side check. No guarantee of absent recursion, actual positive HP loss or one callback per tick.',
  'Rejected base potion does not undo auxiliary effect/fire/snapshot writes; failed area spawn does not prevent castFX/speed/sound/cost path. Successful cast is not control acceptance.',
  'Only source-owned local NBT writer/reader proves omission of lifetime; no native generic entity data persistence behavior asserted. No owner cleanup afterlogout/dimensionchange in current controller methods.',
  'Read EntitySpellBase13 lines during parent discovery, then verified it is not parent; exclude it from cited/counting scope. 041 was accepted separately by coordinator; exact support reuse adds no independent semantic credit to042.',
  'No assets/models/textures edited, no image/texture/sound data read. Ordinary constitution no new gray text.041 sealed,040 zero,039 not rerun.'
 ],
 'static_examples_not_executed_tests':[
  {'condition':'time_stop present when target LivingUpdate delivered','observation':'remove first, cancel event second; removal damage depends on shared flag and native callback ordering.'},
  {'condition':'source lifetime1 when source update called','observation':'parent sets0,onDeath,setDead; child still reaches server target pass in the same call.'},
  {'condition':'base effect not accepted by native target','observation':'snapshot and auxiliary slowness/weakness/fire attempts still independent, no applied-target receipt.'},
  {'condition':'no FREEZE core; removal callback with refreshingfalse','observation':'cold damage still attempted; no FREEZE gate in complete potion method.'},
  {'condition':'after source expiry target retains token before its next update','observation':'source contains no mass release; next target event can consume leftover token. No maximum wall-clock delay proof.'}
 ],
 'application':'Boss拒控要在最终控制准入点明确裁决，不用区域施法成功、开场粒子或结束声替代。控制标记消费、effect removal副作用与区域寿命必须分清；重入保护应按目标/调用作用域恢复，不能以共享boolean冒充安全状态。仅研究，不移植。',
 'counting':{'whole_candidate':1,'accepted_credit':0,'helper_variant_parameter_credit':0,'native_acceptance':0},
 'next_work':'Coordinator independent complete-policy review max1or0. 041 separately accepted at475; preserve its original historical pending proposal. No self-merge/master writes or rechecking039.'}
covered={}
for x in refs:
 a,b=x['lines'];now=set(range(a,b+1));prev=covered.setdefault(x['path'],set());assert not prev.intersection(now);prev.update(now)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(v)==len((R/k).read_text().splitlines()) for k,v in covered.items()),cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-042.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'path':rel(out),'sha256':sha(out.read_bytes()),'new_ranges':len(new),'new_lines':doc['prior_read_reuse']['new_cited_lines'],'reused_ranges':len(refs)-len(new),'all_ranges':len(refs)},ensure_ascii=False))

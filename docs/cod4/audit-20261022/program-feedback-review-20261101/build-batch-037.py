#!/usr/bin/env python3
"""Pinned local lightning/item-protection policy. No production or master writes."""
import hashlib
import json
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
p34=H/'immune-reference-batch-034.json';old=json.loads(p34.read_text())
assert sha(p34.read_bytes())=='294cbff57eae34cdcb7314542f1f0c1e50305aa6b72263acaba6b01df3c7bf24'
ms={x['repo']:x for x in json.loads((R/old['provenances'][0]['manifest_path']).read_text())};refs=[]
def add(repo,prefix,specs):
 m=ms[repo];entries={e['path']:e for e in m['files']}
 for f,ranges in specs:
  e=entries[prefix+f];b=(R/e['source']).read_bytes();n=len(b.decode().splitlines())
  for limits in ranges or [[1,n]]:
   refs.append({'repo':repo,'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],'lines':limits,
    'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'reading_context':'new_actual_source_read037',
    'purpose':'Concrete registered lightning/item replacement, protection predicate and lifetime initialization; helper/variant/other event arm support0.'})
add('CyclopsMC/EvilCraft','src/main/java/org/cyclops/evilcraft/',[
 ('core/entity/item/EntityItemIndestructable.java',None),('core/entity/item/EntityItemExtended.java',None),
 ('entity/item/EntityItemEmpowerable.java',None),('entity/item/EntityItemUndespawnable.java',None),
 ('item/IItemEmpowerable.java',None),('item/ItemInvertedPotentia.java',None),('item/ItemInvertedPotentiaConfig.java',None),
 ('event/EntityStruckByLightningEventHook.java',None),('entity/item/EntityItemEmpowerableConfig.java',None),
 ('proxy/CommonProxy.java',None),('proxy/ClientProxy.java',[[1,86]]),
 ('entity/item/EntityLightningGrenade.java',None),('item/ItemLightningGrenade.java',None),
 ('item/ItemLightningGrenadeConfig.java',None),('entity/item/EntityLightningGrenadeConfig.java',None),
 ('item/ItemAbstractGrenade.java',None),('RegistryEntries.java',[[145,150],[379,380],[383,384]])])
add('CyclopsMC/CyclopsCore','src/main/java/org/cyclops/cyclopscore/',[
 ('proxy/ClientProxyComponent.java',None),('proxy/CommonProxyComponent.java',None),('helper/EntityHelpers.java',[[1,49]])])
newrefs=list(refs)
for x in old['source_refs']:
 if x['repo']=='CyclopsMC/CyclopsCore' or x['upstream_path'].endswith('/EvilCraft.java'):
  assert sha((R/x['path']).read_bytes())==x['file_sha256']
  y=dict(x);y['reading_context']='unchanged034_range_reused_not_reread_or_recredited';y['purpose']='Unchanged accepted registration/helpers0; no exact Core build750 binary correspondence.';refs.append(y)
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
keys={
 'wizardry-lightning-conversion-consumable-duplicate-suppression':'Prior replaces living lightning damage with custom shock then consumes perentity flag on later native hit; here item stack identity is replaced immediately, event canceled and bolt removed. No replacement hurt or one-shot immunity flag. Perbolt villager set in same hook is excluded0.',
 'draconic-native-crystal-refusal-recharge-cue-and-destabilization-window':'Prior explicit timed vulnerability window with shield/charge cue. New policy uses live current item empowerment for predicate but construction-only lifespan selection and unconditional fireImmune; no duration/recharge or perhit cue.',
 'icefire-gorgon-native-gaze-final-admission-replacement-lifetime-type-cache':'Prior actor→statue replacement/removal and cached visual entity. Here same dropped entity keeps identity while replacing held stack; stack count explicitly copied but NBT not copied for concrete Potentia. Existing drop lifetime is not reinitialized by this conversion. Not actor conversion or victim control.',
 'evilcraft-native-beam-additive-freeze-preserves-spirit-finite-lifespan-with-synced-control-state-and-visibility-gated-renderer':'Accepted034 freeze stock selects whether to spend life each aiStep; here damage predicate reads current stack each query while lifespan assigned only in constructors, so later empowerment need not revise lifespan. Shared entity configs/Core helpers0. Full accepted decision reused unchanged from035 snapshot, not source reread.',
 'evilcraft-native-necromancer-projectile-observer-removal-veto-with-target-bound-group-cleanup-and-independent-child-ttl':'Accepted035 remove veto and sampled child-group cleanup are separate. Item entity has no remove veto or independent saved custom timer here; no group reference/owner relation. Grenade is one-shot producer, not observing projectile.',
 'evilcraft-native-source-current-stack-wear-clamp-refuses-attack-and-used-hand-break-with-repair-qualified-reentry':'Accepted036 also reads current item state, but clamps actor durability/cancels action and concrete repair permits reentry. Here converts dropped item type, consumes lightning event/bolt and switches entity protection without rebuilding constructor lifetime. No action wear clamp, repair, or actor-hand policy.'}
p35=H/'immune-reference-batch-035.json';j35=json.loads(p35.read_text())
k34='evilcraft-native-beam-additive-freeze-preserves-spirit-finite-lifespan-with-synced-control-state-and-visibility-gated-renderer'
s34=next(x['full_semantic_decision_read'] for x in j35['dedup_snapshot']['comparisons'] if x['accepted_id']==k34)
assert s34=={k:v for k,v in by[k34].items() if k not in ['source_refs','auxiliary_refs']}
mlp=A/'legacy-migration-acceptance/reviewed.jsonl';mlraw=mlp.read_bytes();ml=[json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]
mi={x['candidate_id']:x for x in ml};mk=['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
receipt=A/'immune-feedback-research/coordinator-evilcraft-unusing-wear-acceptance-20261103.json'
assert sha(receipt.read_bytes())=='191b7cf45d39a115349069ed792dc3755ef5b03acdd4e8b0fc2ec87d2401b7e8'
screen=H/'batch-037-local-native-archive-screen.json'
doc={'schema_version':1,'owner':'program-feedback-review-037','repo':'CyclopsMC/EvilCraft','commit':ms['CyclopsMC/EvilCraft']['commit'],
 'provenances':old['provenances'],'status':'PENDING_INDEPENDENT_REVIEW_MAXIMUM_ONE_LIGHTNING_STACK_REPLACEMENT_AND_SPLIT_PROTECTION_LIFETIME_POLICY',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'evilcraft-native-lightning-item-empowerment-switches-live-damage-predicate-without-reinitializing-construction-selected-lifetime',
 'source_refs':refs,'prior_read_reuse':{'path':str(p34.relative_to(R)),'sha256':sha(p34.read_bytes()),'new_ranges':len(newrefs),
 'new_cited_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in newrefs),'reused_ranges':len(refs)-len(newrefs),
 'limits':'034/035/036 accepted sources not re-audited. Exact034 support ranges reused0.'},
 'baseline':{'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'ledger_sha256':sha(lr),
  'accepted036_receipt_path':str(receipt.relative_to(R)),'accepted036_receipt_sha256':sha(receipt.read_bytes())},
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(rows),
  'comparisons':[{'accepted_id':k,'full_semantic_decision_read':{a:b for a,b in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':v} for k,v in keys.items()],
  'reading_order':'First3 complete substantive policies read before item classes;035/036 actual current complete accepted decisions read after discovery.034 full prior semantic decision reused after exact equality check from035, no source rerun.',
  'reused034_decision':{'path':str(p35.relative_to(R)),'sha256':sha(p35.read_bytes()),'accepted_id':k34}},
 'migration_overlap_screen':{'path':str(mlp.relative_to(R)),'sha256':sha(mlraw),'rows':len(ml),
  'comparisons':[{'accepted_id':key,'complete_semantic_decision_read':{k:mi[key][k] for k in mk},'distinction':dist} for key,dist in [
   ('ee8c255bbd2f7596debe','Werewolf profession/fullmoon/cross-species snapshot remains old owner. Same lightning hook villager arm was read as class context only, no new villager transformation/lastbolt-set credit.'),
   ('4eb007f55db1d4efb736','Crafter own inventory schema and empower tag-copy/count behavior remain old owner. Current concrete item is InvertedPotentia, with count copied and no tag copy. No new schema/upgrade variant credit; whole candidate must be dropped-entity protection/lifetime policy.') ]]},
 'native_archive_screen':{'path':str(screen.relative_to(R)),'sha256':sha(screen.read_bytes()),
  'decision':'Bounded local metadata inventory found readable1.20.1 Forge47.4.10 mapped sources with ItemEntity/LightningBolt/ForgeEventFactory. No actual member source read or used: fixed EvilCraft manifest lacks build.gradle/gradle.properties/mods.toml to bind exact Forge revision. Do not claim native source unavailable globally or substitute this archive as proven dependency. No download/Java/Gradle.'},
 'full_chain':[
  {'stage':'registered item/custom entity/event','observation':'Actual EvilCraft config list creates normal and empowered InvertedPotentia, lightning grenade and item_empowerable entity. ItemConfig/EntityConfig shared factories and register/getRender pipeline reused exactly. New CommonProxy.registerEventHooks registers EntityStruckByLightningEventHook; ClientProxy constructs delegated CommonProxy and Core ClientProxyComponent forwards registerEventHooks. Existing ModBase setup calls actual selected proxy. No explicit server guard in empowerItem hook itself; native event dispatch/thread not inferred from grenade source.'},
  {'stage':'actual lightning producer and attempt cues','observation':'ItemAbstractGrenade.use server shrinks1 unless creative, calls ARROW_SHOOT then actual getThrowableEntity→EntityLightningGrenade, shoots andaddFreshEntity ignoring result; returns SUCCESS helper on both sides. Impact ENTITY calls hurt(thrown,0) without checking result; server with ServerPlayer owner calls EntityHelpers.onEntityCollided→block.stepOn, creates LightningBolt, positions at grenade coordinates, requests add ignoringresult, then discards grenade. Other serverowners still discard without bolt. Client onHit emits32CRIT without proving bolt/empowerment. No nullbolt/rollback/receipt; native collision/strike dispatch unexpanded.'},
  {'stage':'concrete conversion and event termination','observation':'Hook receives ItemEntity with IItemEmpowerable and !isEmpowered, calls empower then entity.setItem(result), cancels strike event, discards lightning. Concrete InvertedPotentia.empower creates new empowered registered ItemStack with old count, doesnot copy tags/caps/name/damage. Predicate is finalboolean on item type, not mutable perstackNBT. No owner/weather/samebolt set or damage-result precondition in item branch. Already empowered skips replacement, cancel and bolt removal. Sameentity repeated event after successful replacement sees new true state; no universal oneitem-perbolt claim because native iteration after remove notread.'},
  {'stage':'custom dropped entity construction and current predicate','observation':'Both Potentia types hasCustomEntitytrue; createEntity casts locationItemEntity and creates EntityItemEmpowerable(world,original), ignoring separate itemStack parameter. Extended original constructor sets pickupDelay40, copies motion/position and original stack reference before Indestructable.init. It doesnot explicitly copy original age/owner/thrower/pickupdelay. isIndestructable reads current item everyquery: IItemEmpowerable uses its isEmpowered, otherwise supertrue. isInvulnerableTo returns that OR super. fireImmune always true independent of empowerment. Hook accepts any ItemEntity, so conversion doesnot itself guarantee custom subclass or this protection override was installed.'},
  {'stage':'construction-selected lifetime stays separate','observation':'Indestructable.init calls virtual isUndespawnable, which defaults to isIndestructable, and only then sets lifespan Integer.MAX_VALUE when true. Original ordinary Potentia is set before init, so false doesnot request this lifetime override; empowered originaltrue requestsMAX. Later lightning entity.setItem switches live protection predicate but invokes no init/age/lifespan reset. Re-dropping an empowered item through customconstructor can selectMAX. Default type/world constructor and clientcopy construct before caller assigns finalstack; exact initial native ItemEntity stack and native load/lifespan decode are unexpanded, so no asserted load-time infinity. Undespawnable sibling forces lifespan branchtrue but isIndestructablefalse while fireImmune remainstrue; whole sibling only support0.'},
  {'stage':'actual feedback consumer and end limits','observation':'InvertedPotentia.isFoil delegates to isEmpowered; entity config registers native ItemEntityRenderer, and Extended.getAddEntityPacket delegates to NetworkHooks. Client copy creates bytype then copies stack andposition but notage fields (commented). These are actual mod presentation inputs, not native tracked-stack/renderer/foil delivery proof. No dedicated item refusal/upgrade message/sound/particle receipt or cooldown. Arrow sound precedes projectile acceptance and CRIT derives localimpact. Permanent item type state has no de-empower/timedreset in these classes. Pickup/merge/despawn/removal remain inherited native paths not expanded; damage predicate true is not proof every native source/removal is denied.'}
 ],
 'critical_boundaries':[
  'One maximum whole lightning replacement/live protection/constructor lifetime policy. Native fireImmune, lifespan, two itemvariants, helpers and concrete grenade add0 separately.',
  'Event canceled and lightning removal are actual mod calls after stack replacement; not receipt of final immunity, world-add success, correct native drop installation or upgrade transaction.',
  'Same ItemEntity object is reused by empowerment. Concrete Potentia preserves count only; no claim all IItemEmpowerable implementations preserve it.',
  'Current predicate may change without constructor lifetime recomputation. No fixed duration/wall-clock despawn result or mathematical immortality claim; underlying ItemEntity path not bound/read.',
  'Native isInvulnerableTo override may be only part of actual hurt/remove pipeline. No universal out-of-world/creative/command/unload immunity assertion.',
  'Villager samebolt/RNG/cancel-false arm and ExaltedCrafter schema are existing-owner context0, not extra policies.',
  'No new native archive source used: readable candidate exists but exact47.4.10 dependency correspondence not established. Core tag/build750 limit unchanged.'
 ],
 'native_gaps':[
  {'missing':'Exact pinned EvilCraft Forge/Minecraft dependency binding and native ItemEntity.hurt/tick/NBT/custom-drop replacement.', 'impact':'Bounded mod-owned overridden predicates and lifespan writes only; no final all-source immunity, exact remaining despawn or save/load behavior.'},
  {'missing':'Native LightningBolt strike/event ordering and world add/removal.', 'impact':'No proved only-one-item upgrade per bolt, no natural weather guarantee, no guaranteed original hurt suppression after all mods.'},
  {'missing':'Native tracked ItemStack packet receiver/ItemEntityRenderer/isFoil call and actual pixels/audio.', 'impact':'Inputs and register/copy hooks only, no delivered feedback receipt. No assets inspected or changed.'},
  {'missing':'Independent proof Core tag exactly matches build750 binary.', 'impact':'Pinned source support0 only.'}
 ],
 'static_examples_not_executed_tests':[
  {'case':'in-place ordinary upgrade','assumptions':'Custom entity constructed from ordinary Potentia stack and later receives qualifying lightning event.', 'derivation':'Initial virtualpredicatefalse doesnot setMAX; replacement to empowered item makes later livepredicate true, but hook doesnot rewrite lifespan orage. Native actual expiry boundary not asserted.'},
  {'case':'already empowered input','assumptions':'Incoming strike event sees empowered Potentia item.', 'derivation':'Item hook skips allthree replacement/cancel/bolt-remove operations. Separate entity predicate can stilltrue; no new strike receipt.'},
  {'case':'ordinary ItemEntity input','assumptions':'Qualifying ordinary native ItemEntity contains unempowered Potentia, without custom subclass installation.', 'derivation':'Hook upgrades contained stack and cancels strike, but entity class unchanged. Cannot infer EntityItemEmpowerable override for that object.'},
  {'case':'fresh empowered drop','assumptions':'createEntity receives originalItemEntity containing empowered Potentia.', 'derivation':'Originalstack assigned before init, so virtualisIndestructabletrue and lifespanMAX requested. Pickupdelay40 reset; no originalage/ownership copy in shown constructor.'}
 ],
 'application':'Separate protection derived from live payload from constructor-only lifetime settings. When replacing contents in place, explicitly decide whether lifetime and ownership should change; distinguish attempted conversion cues from authoritative success.',
 'counting':{'formal_baseline_observed':len(rows),'credit':0,'whole_policy_maximum_pending':1,'variant_helper_storage_credit':0},
 'next_work':'Independent review at most1 or merge0. Native archive mismatch/binding gap stays explicit; no game/network or production gate bypass.'}
with (H/'immune-reference-batch-037.json').open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'ranges':len(refs),'new_ranges':len(newrefs),'new_lines':doc['prior_read_reuse']['new_cited_lines'],
 'reused_ranges':doc['prior_read_reuse']['reused_ranges'],'formal_baseline':len(rows),'maximum_pending':1,'credit':0}))

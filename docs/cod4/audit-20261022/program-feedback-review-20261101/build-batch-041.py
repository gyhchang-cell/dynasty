#!/usr/bin/env python3
"""Write one fixed-local Geas policy proposal; no upstream/master mutations."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
rel=lambda p:str(p.relative_to(R))
def ref(p):return {'path':rel(p),'sha256':sha(p.read_bytes())}
mp=R/'tools/cod4/legacy-migration-acceptance/helpers/halley-migration/batch-032/source-manifest.json'
m=next(x for x in json.loads(mp.read_text()) if x['repo']=='MysticMods/Roots')
pb=mp.parent/'provenance/MysticMods__Roots'
prov={'repo':m['repo'],'commit':m['commit'],'branch':m['branch'],'tag':m.get('tag'),
 'manifest_path':rel(mp),'manifest_sha256':sha(mp.read_bytes()),'commit_metadata_path':rel(pb/'commit.json'),
 'tree_metadata_path':rel(pb/'tree.json'),'git_tree':m['git_tree'],
 'acquisition':'Existing fixed local source, cached commit and Git tree only; no network, dependency download or upstream execution.'}
entries={x['path']:x for x in m['files']};refs=[]
whole=['spell/SpellGeas.java','potion/PotionGeas.java','util/SlaveUtil.java',
 'modifiers/instance/staff/StaffModifierInstanceList.java','modifiers/instance/staff/ModifierSnapshot.java',
 'init/ModPotions.java','Roots.java','util/EntityUtil.java','item/ItemStaff.java',
 'network/ClientMessageHandler.java','RegistryManager.java','proxy/CommonProxy.java',
 'spell/SpellRegistry.java','init/ModEntities.java','entity/mob/EntityZombieSlave.java',
 'entity/mob/EntityHuskSlave.java','entity/mob/EntityPigZombieSlave.java','init/ModDamage.java',
 'network/MessageHandler.java','event/ClientTickHandler.java','network/RootsPacketHandler.java',
 'network/fx/MessageGeasFX.java','network/fx/MessageGeasRingFX.java','util/EntityLists.java',
 'util/ServerHerbUtil.java','util/types/RegistryItem.java','init/ModSounds.java','spell/info/StaffSpellInfo.java']
specs=[(n,None,'Whole file actually read; concrete Geas chain or directly used support. Other methods/variants0.') for n in whole]
specs += [
 ('EventManager.java',[[1,249]],'Header/subscriber and complete onDamage/onEntityTarget/onEntityTick; other effect arms context0. Remainder not cited.'),
 ('spell/SpellBase.java',[[1,240],[347,403],[431,453],[496,539]],'Complete selected constructor/properties/cost checks/payment submissions, CastResult/wrapper, getters and finalisation methods. Not whole file.'),
 ('spell/info/storage/StaffSpellStorage.java',[[1,135],[367,370]],'Complete selected slot/cooldown tick/use methods and fromStack entry; storage reader/writer not expanded or recredited.'),
 ('init/ModItems.java',[[74,74],[136,136]],'registerItems signature and complete staff assignment only, not its whole containing registration method.'),
 ('particle/ParticleUtil.java',[[1,20],[119,130]],'Header and two complete glow helpers through external renderer submission; unrelated partial neighboring helpers excluded.'),
 ('config/EntityConfig.java',[[1,61],[643,673]],'Config registration and complete relevant general/Geas lazy getters and declaration sections; external ConfigUtil parser not expanded.'),
 ('config/GeneralConfig.java',[[76,77]],'Boss-health threshold declaration only; not whole configuration class.')]
for name,ranges,purpose in specs:
 e=entries['src/main/java/epicsquid/roots/'+name];b=(R/e['source']).read_bytes();lines=b.decode().splitlines()
 for limits in ranges or [[1,len(lines)]]:
  s,t=limits
  refs.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],'lines':limits,
   'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(lines[s-1:t]).encode()),
   'purpose':purpose,'reading_context':'Actual reading041. Truncated output portions were recovered before citing; no duplicate source range credit.'})
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
dist={
 'relics-native-tremor-attacker-disable-versus-victim-immunity':'Prior direct attacker TREMOR marks victim invulnerable. Here trueSource active Geas and not exact converted class receives a separate psychic damage attempt, original event amount0 and source-position ring; targeting is also cleared. Owner source covers a different gate from direct living source. Rejection is attacker control, not victim immunity.',
 'botania-native-persistent-ai-pacification-change-qualified-target-cue-and-reload-restore':'Prior permanently modifies AI goals, saves pacified flag and reconstructs on reload. Here active effect clears target assignments without NoAI/goal deletion, and removal callback runs captured modifier aftermath or replaces converted actor; no permanent pacified-state restoration promise.',
 'bumblezone-native-combat-revokes-offhand-pacification-and-target-clearing-budget':'Prior offhand active qualification is revoked by combat. Geas instead keeps its effect when the afflicted attacker tries to hurt, attempts punishment each event and zeros victim damage. No combat depletion, area clearing budget or offhand maintenance.',
 'wizardry-native-paralysis-tail-tick-ai-release-versus-critical-hurt-early-removal':'Prior NoAI tail-tick restoration can be skipped by hurt removal. Here there is no NoAI mutation; target assignment is suppressed while effect exists, and the actual potion attribute-removal hook dispatches aftermath/reversion rather than restoring a stored target or running a tail tick.',
 'wizardry-possession-control-release-restores-native-actor':'Prior retained hidden actor/player-possession state with inventory and dimensions restoration. Geas exact-class conversion creates a new actor and copies a limited live field/equipment/effect set, then builds another new actor on removal. No preserved original identity, player control or original AI snapshot.',
 'goety-native-lethal-capture-owner-transfer-instead-of-death-and-unshackle-release':'Prior lethal capture is owner-qualified death cancellation and release via hurt/interaction. Here player cast chooses ordinary attack suppression versus exact-type temporary replacement by modifier, and potion removal drives reversion. No owner UUID/leader transfer, lethal requirement or explicit death cancellation.'}
cmps=[{'accepted_id':k,'full_semantic_decision_read':{a:v for a,v in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':v} for k,v in dist.items()]
mlp=A/'legacy-migration-acceptance/reviewed.jsonl';mlraw=mlp.read_bytes();migration=[json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]
old=next(x for x in migration if x['candidate_id']=='d163d771f89ee9b86e84')
mk=['candidate_id','status','family','trigger','input','output','preservation','application_limit','credit']
accepted=A/'immune-feedback-research/coordinator-champions-shielding-acceptance-20261103.json'
assert json.loads(accepted.read_text())['after_count']==474
doc={
 'schema_version':1,'owner':'program-feedback-review-041','created_utc':datetime.now(timezone.utc).isoformat(),
 'repo':m['repo'],'commit':m['commit'],'provenances':[prov],
 'status':'PENDING_INDEPENDENT_REVIEW_MAXIMUM_ONE_GEAS_SOURCE_PUNISHMENT_TARGET_SUPPRESSION_AND_TYPE_DISPATCHED_RELEASE_POLICY',
 'research_credit':0,'maximum_proposed_credit':1,'production_changes':False,'runtime_executed':False,
 'semantic_family':'roots-native-effect-qualified-true-attacker-punishment-zeroes-victim-damage-with-target-suppression-and-type-dispatched-removal-aftermath',
 'source_refs':refs,'source_ranges':len(refs),'unique_files':len(specs),'full_files':len(whole),
 'cited_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in refs),
 'baseline':{'accepted039_receipt':ref(accepted),'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'040_screen':ref(H/'immune-reference-batch-040-screen.json'),'040_credit':0},
 'dedup_snapshot':{'path':rel(lp),'sha256':sha(lr),'rows':len(rows),'comparisons':cmps,
   'scope':'Existing474 metadata discovery and six complete nearest semantic decisions read; not all474 source chains reread.'},
 'migration_overlap_screen':{'path':rel(mlp),'sha256':sha(mlraw),'rows':len(migration),'comparisons':[
  {'accepted_id':old['candidate_id'],'complete_semantic_decision_read':{k:old[k] for k in mk},
   'distinction':'Old staff formats, UUID permanent spell library, modifiers, cost/storage helpers and LightDrifter belong to existing migration owner. No new credit for these. New proposal is Geas live attacker control, ordinary-vs-converted effect removal and its actual feedback consumers, all one family.'}]},
 'full_chain':[
  'Roots @Mod preInit explicitly registers RegistryManager and delegates CommonProxy lifecycle. RegistryManager potion callback registers concrete Geas; custom content callback submits staff item, mob registrations and RootsPacketHandler messages. EventManager and ClientTickHandler have explicit @EventBusSubscriber annotations. CommonProxy calls SpellRegistry preInit/init/finalise; Geas instance is inserted, configured, initialized with cast sound and finalised properties. Exact external MysticalLib event dispatch/LibRegistry internals not expanded.',
  'ItemStaff native onItemRightClick selects current staff info, rejects cooldown and checks instantaneous spell costs. It calls SpellBase.cast, which delegates actual SpellGeas.cast and submits cast sound on success/server/ticks0 or72000. After success, noncreative server enacts costs and sets cooldown. ServerHerbUtil checks/sums pouches and requests powder spending with armor reduction; inner pouch transaction/ClientHerbUtil not expanded. StaffSpellInfo.use sets cooldownTotal and stopTime=argument+cooldown, so CastResult.SUCCESS.modifyCooldown returning0 does NOT mean no cooldown; current world time is passed and normal total remains.',
  'Geas scans20 overlapping AABBs at three-block look-vector intervals; amount budget1 plus two optional extras. affect excludes active Geas, then Boss predicate (!isNonBoss or maxHealth>configured threshold), then requires hostile classification or current attack target==player. Player is excluded by hostility routine unless EntityLiving conditions apply (ordinary player is not EntityLiving). No raytrace/LOS or unique-target set. Existing Geas cannot be refreshed by this affect method. Boss refusal returns0 without dedicated rejection reason feedback.',
  'Ordinary qualified target: on server write enabled/applied/nonconflicting modifier-core snapshot to entityData under cached spell ID, attempt addPotionEffect with configured duration, and clear current EntityLiving target. Return1 after qualification on either side, without checking actual effect admission or resulting active state. Thus cast success, sound, herb spending and cooldown can represent attempted control; overlapping AABBs may count a rejected-effect target again until budget. Optional peaceful absorption runs separately before hostile loop and continues each AABB even after hostile budget; friendly-only changes can occur although affected==0 makes cast returnfalse.',
  'GUARDIANS modifier with exact eligible class routes to SlaveUtil.convert instead: new matching slave class, copies existing PotionEffect objects, equipment stack references, current health, selected movement/position/collision/timer fields. spawnEntity result ignored, then old drops disabled, old setDead, new position submitted and new modifier snapshot/Geas attempted. No original-entity pointer, ownerUUID or whole NBT snapshot. Exact Zombie/Husk/PigZombie classes only; subclasses do not qualify through map lookup.',
  'Native HIGHEST LivingHurt handler obtains trueSource. After other effect arms, if trueSource is living with Geas and not exact slave class, it first attempts3 psychic damage to that source, ignores returned success, sets original event amount0 and sends ring at source coordinates. This branch does not itself setCanceled; other earlier arms may already cancel. It has no explicit side, positive-amount, effect-consumption or per-target throttle guard. Generic PSYCHIC_DAMAGE has no supplied entity owner; no copied projectile/attacker identity. Source attribution and native reentrant pipeline are not runtime-verified.',
  'Native LivingSetAttackTarget handler independently clears EntityLiving.attackTarget while Geas active and not slave. It directly clears the field to avoid another setter call; no NoAI change and no original target stored. Ordinary movement/other AI continues outside this specific assignment gate. Slave classes bypass both target suppression and Geas damage punishment; their applyEntityAI adds a hostile EntityMob/non-slave target goal. This is type-based hostility selection, not caster-owned following or universal allied-team protection.',
  'PotionGeas.removeAttributesModifiersFromEntity calls super, submits configured end sound, then dispatches on current target type. Exact slave maps back via new original-type object, submits spawn (ignores result), disables old drops/kills old and submits position. Ordinary target reads captured modifier-core snapshot and executes first matching WEAKNESS, else FIRE, else PHYSICAL, else WATER; damage/effect results ignored. No owner/target restoration or snapshot-key deletion here. Callback lacks explicit side guard even though SlaveUtil.convert returnsnull on client, so safe invocation depends on native side contract not established here.',
  'Current-state presentation: LivingUpdate sends MessageGeasFX whenever effect present, including slave; incoming suppression sends separate MessageGeasRingFX regardless psychic hit success. Both contain only xyz, no UUID/dimension/reason/sequence or expiry token. Actual Side.CLIENT registrations, client runnable queue at END and both concrete handlers read. Handler uses current Minecraft world and submits glow particles; no target relookup or explicit world-null check. Geometry loops have zero-possible random increments, not a fixed per-packet bounded iteration proof.',
  'ParticleUtil.glow gates external renderer submission by client proxy and global randomized particle counter/setting. FX requested lifetimes20/24/40 are renderer arguments only, not verified on-screen lifetime. No pixel/audio assets were read or edited. ClientTickHandler queue has no shown world-change flush; runnable exceptions can prevent iterator removal/ticking reset. Sound end precedes reversion/aftermath success. These presentation boundaries stay support0.',
  'Release is tied to actual potion removal callback, not independently decremented Geas timer in this code. Native expiration/cure/replacement/attribute reapplication dispatch order was not expanded, so no promise callback runs exactly once or only at natural expiry. Ordinary gates stop when effect absent; no old AI target is restored. Converted actor replacement preserves only listed data and depends on successful engine insertion/registration. One whole control/removal/feedback policy max1, not per mode/species/aftermath/packet.'
 ],
 'critical_boundaries':[
  'This is fixed Roots1.12.2 source, not matching Dynasty runtime. No game, Gradle, Java, upstream executable, assets, sharedJar, main ledger or checklist changes.',
  'ModEntities.registerMobs explicitly lists ZombieSlave and HuskSlave but not PigZombieSlave, although SlaveUtil exact map contains allthree. Do not claim allthree conversion paths naturally registered or successful; PigZombie class is read context0. External auto-registration not assumed.',
  'Fresh actor conversion does not copy UUID, custom name, owner, original AI target or arbitrary entityData in the shown converter. Equipment/potion references are not deep copied here. Spawn result is not transactional; old removal is not conditioned on accepted insertion. No identity/persistence/lossless claim.',
  'Ordinary effect attempt snapshots modifier cores before native admission and clears target regardless of admission. StaffModifierInstanceList.has checks applied+enabled, while toArray also filters conflicts; a selected immediate mode and captured end-effects can differ with malformed/conflicting input. Native effect rules not expanded.',
  'No complete immutable Boss rejection acknowledgment: Boss check returns0, source-ring indicates punitive gate execution, cast sound indicates qualification, end sound indicates removal callback entry. None proves all requested control, damage or reversion succeeded.',
  'Geas damage uses trueSource; attack-source immunity is not target Boss immunity. Other earlier arms can retaliate, cancel or modify before Geas zeroing. Only Geas is proposed; full EventManager onDamage context read to avoid assuming an isolated handler.',
  'Specific Geas/global config sets route through external ConfigUtil parseLocationsSet and static lazy caches. Default lists include villager as hostile and enderman as friendly; boss threshold declaration40 is read, not a claim of current deployment config. No dynamic config reload cache guarantee.',
  'Staff storage former-format/UUID library and herb inventory deep readers belong to already accepted migration work and are not reaccepted here. Main payment submission methods read; no transaction/refund or positive final cost guarantee.',
  'MysticalLib1.12 dependency APIs are actual imported/submitted boundaries. Batch032 manifest contains Roots only; no exact matching dependency proof or sender/renderer delivery guarantee. No global claim that dependency source is unavailable.',
  'ModItems reference cites only complete staff assignment and method signature; entire large registerItems body not read. SpellBase/EventManager/config/particle references are explicitly selected complete methods/declarations, not false whole-file reading.'
 ],
 'static_examples_not_executed_tests':[
  {'condition':'ordinary afflicted trueSource attacks a victim','local_observation':'Attempt psychic hurt first, then amount0/ring regardless returned hurt bool; Geas effect not spent by this branch.'},
  {'condition':'same actor class recognized by isSlave and has Geas','local_observation':'Skip ordinary punishment and target clearing; periodic aura still requested.'},
  {'condition':'qualified target rejects addPotionEffect in native engine','local_observation':'Server snapshot and target clear can still happen; affect returns1 and caller can sound/pay/cooldown. Engine rejection itself untested.'},
  {'condition':'ordinary Geas removal with both WEAKNESS and FIRE core membership','local_observation':'Else-if applies weakness only; no fire branch after it. Snapshot core membership differs from live modifiers.'},
  {'condition':'converted Geas removal invoked on client','local_observation':'convert returnsnull, callback lacks null/side guard before spawn/position access. Conditional source hazard, not proven actual callback dispatch or Dynasty bug.'},
  {'condition':'hostile affected count0 but peaceful branch found friendly entities','local_observation':'Absorption attempts can occur although castfalse skips normal successful-cast cost/cooldown path; no claimed gameplay exploit test.'}
 ],
 'application':'Boss拒控须在真实目标拒绝点带明确原因发回执；攻击者被约束、目标免疫、效果接纳失败不能混称Immune。状态解除应按真实对象生命周期处理，不能靠结束声判断还原成功；保留普通阴阳无新增灰字。仅研究，不移植。',
 'counting':{'whole_candidate':1,'accepted_credit':0,'variant_helper_packet_parameter_credit':0,'migration_recredit':0,'native_or_production_acceptance':0},
 'next_work':'Coordinator independent whole-policy reading/novelty decision max1or0. Keep039 sealed and do not self-merge. Next work remains fixed-local original-program research only.'
}
out=H/'immune-reference-batch-041.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'path':rel(out),'sha256':sha(out.read_bytes()),'ranges':len(refs),'files':len(specs),'full_files':len(whole),'lines':doc['cited_lines'],'maximum_pending':1},ensure_ascii=False))

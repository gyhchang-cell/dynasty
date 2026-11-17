"""Pinned local disarm mutation/settlement policy, max1 pending independent review."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def read(n):return json.loads((H/n).read_text())
p46=H/'immune-reference-batch-046.json';d46=read(p46.name)
assert ref(p46)['sha256']=='241f4333e4b45d62a7a583109f27d5d88fd760d9781ed01b3f06919da513f932'
d44=read('immune-reference-batch-044-screen.json');d41=read('immune-reference-batch-041.json')
v=d46['provenances'][0];m=next(x for x in json.loads((R/v['manifest_path']).read_text()) if x['repo']==v['repo'])
assert sha((R/v['manifest_path']).read_bytes())==v['manifest_sha256']
entries={x['path']:x for x in m['files']};prefix='src/main/java/epicsquid/roots/'
def source(n,ranges=None):
 e=entries[prefix+n];b=(R/e['source']).read_bytes();lines=b.decode().splitlines();assert sha(b)==e['sourceSha256']
 return [{'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],'lines':[a,z],
          'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(lines[a-1:z]).encode()),
          'reading_context':'new_actual_read047','purpose':'Actual whole method/class in one equipment mutation/settlement policy; not per-slot or per-target credit.'}
         for a,z in ranges or [[1,len(lines)]]]
refs=source('spell/SpellDisarm.java')+source('network/fx/MessageDisarmFX.java')+source('config/EntityConfig.java',[[496,529]])
new=list(refs)
generic={'Roots.java','RegistryManager.java','proxy/CommonProxy.java','spell/SpellRegistry.java','item/ItemStaff.java',
 'spell/info/StaffSpellInfo.java','spell/info/storage/StaffSpellStorage.java','spell/SpellBase.java','util/ServerHerbUtil.java',
 'util/types/RegistryItem.java','modifiers/instance/staff/StaffModifierInstanceList.java','modifiers/instance/staff/ModifierSnapshot.java','init/ModSounds.java','init/ModItems.java'}
reuse=[]
for old,name,selector in [
 (d46,p46.name,lambda x:x['upstream_path'].removeprefix(prefix) in generic),
 (d44,'immune-reference-batch-044-screen.json',lambda x:x['upstream_path'].removeprefix(prefix) in {'network/ClientMessageHandler.java','network/MessageHandler.java','event/ClientTickHandler.java','network/RootsPacketHandler.java','particle/ParticleUtil.java'}),
 (d41,'immune-reference-batch-041.json',lambda x:x['upstream_path'].removeprefix(prefix) in {'util/EntityUtil.java','util/EntityLists.java'} or (x['upstream_path'].endswith('/config/EntityConfig.java') and x['lines']==[1,61]))]:
 for x in old['source_refs']:
  if not selector(x):continue
  assert sha((R/x['path']).read_bytes())==x['file_sha256']
  y=dict(x);y.update(reading_context='exact_saved_read_reuse:'+name,purpose='Already read producer/classification/transport support; no additional semantic credit.')
  refs.append(y)
 reuse.append(ref(H/name))
lp=A/'immune-feedback-research/reviewed.json';lb=lp.read_bytes();lr=json.loads(lb);idx={x['semantic_dedup_key']:x for x in lr}
dist={
 'wizardry-native-direct-mainhand-disarm-admission-before-inventory-mutation':'Telekinesis accepts configured player mainhand after anchoring check, then drop before empty; Roots excludes players, iterates hostile area equipment and mutates before aggregate result. Player ownership/anchoring/ray is not inherited. Multi-target false-after-commit and per-target FX before no-payment are distinct whole-policy settlement.',
 'pnc-native-first-nonempty-slot-disarm-commit-independent-of-drop':'PNC first nonempty Mob slot is committed then void hack completion; Roots processes all hand/armor slots per eligible entity and DUO aggregate returns false after1or2 mutated targets, true at3. Shared drop-not-guaranteed principle is not another credit; proposal is whole mutation/payment/result mismatch and independent coordinate receipt.',
 'illagerinvasion-native-finite-block-budget-destructive-disarm-and-stun-release':'Basher self shield→axe after finite hurt budget and stun, with current attack falling through parent. Roots caster-driven area removal has no blocked-hit budget, temporary stun ownership or restore; spell aggregate success controls caster payment while each target gets earlier mutation FX.'}
cmps=[{'accepted_id':idx[k]['id'],'complete_semantic_decision_read':{f:t for f,t in idx[k].items() if f!='source_refs'},'distinction':val} for k,val in dist.items()]
mig=d46['migration_overlap_screen'];mb=(R/mig['path']).read_bytes();mi={r['candidate_id']:r for r in map(json.loads,mb.decode().splitlines())};mc=[]
for c in mig['comparisons']:
 assert all(mi[c['accepted_id']][k]==v for k,v in c['complete_semantic_decision_read'].items())
 mc.append({'accepted_id':c['accepted_id'],'complete_semantic_decision_read':c['complete_semantic_decision_read'],
 'distinction':'Whole owner judgments already read046 and unchanged. Pouch/staff migration and shared herb/spell wrapper support remain0; neither owner describes this actual Disarm six-slot mutation, chance-only drop and DUO aggregate-result/payment/coordinate-feedback policy. LightDrifter remains excluded044, not reopened.'})
policy='roots-native-area-disarm-equipment-commit-precedes-multitarget-settlement-and-coordinate-receipt'
assert policy not in idx
ac=A/'immune-feedback-research/coordinator-astral-vortex-acceptance-20261103.json';ad=json.loads(ac.read_text())
assert len(lr)==477 and sha(lb)==ad['after_ledger_sha256']
doc={'schema_version':1,'owner':'program-feedback-review-047','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'ONE_WHOLE_DISARM_SETTLEMENT_POLICY_PENDING_INDEPENDENT_REVIEW','research_credit':0,'maximum_proposed_credit':1,
 'repo':m['repo'],'commit':m['commit'],'semantic_dedup_key':policy,'provenances':[v],'source_refs':refs,
 'prior_read_reuse':{'evidence':reuse,'new_ranges':len(new),'new_cited_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in new),'reused_ranges':len(refs)-len(new),'reread_credit':0,
 'reading_scope':'Disarm206 and MessageDisarmFX55 full read; specific config496-529 full declarations/getters. EntityUtil/EntityLists whole re-read but prior credit retained. Initial oversized config/network/particle output clipped and not claimed as new full reading; actual used ParticleUtil1-20,97-108 recovered; all cited old network classes already complete in044. Registry snippets are support reuse, not new reading.'},
 'baseline':{'accepted045_receipt':ref(ac),'accepted045_review':ad['independent_review'],'formal_count_observed':477,'gap_to1000':523,'046_pending':ref(p46),'old_verifier_or_ledger_rerun':False},
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lb),'rows':len(lr),'comparisons':cmps,'scope':'Three closest complete saved semantic judgments read without source-ref arrays; differences compared as whole control/payment/receipt policies.'},
 'migration_overlap_screen':{'path':mig['path'],'sha256':sha(mb),'rows':len(mi),'comparisons':mc,'reuse_evidence':ref(p46),'scope':'Unchanged complete nine-field owner judgments actually read046; not re-awarding their shared producer/resources.'},
 'whole_chain_observation':[
 'Actual SpellRegistry.preInit registers SpellDisarm and applies disable config; shared Roots/CommonProxy/RegistryManager initialization and ItemStaff entry previously read. INSTANTANEOUS declared cooldown350, moonglow_leaf0.425+wildewheet0.125 plus current modifier costs. ItemStaff checks selected capability/cooldown/costs, invokes concrete cast; only CastResult success enacts costs and selected-spell cooldown on noncreative server. Creative bypasses payment/cooldown. Native dual-side item invocation exists but equipment mutation/FX guarded server; no custom Disarm C2S result assertion.',
 'cast builds AABB from integer caster BlockPos ±configured radii default5, gets EntityLivingBase and removes caster. No sort/nearest ray/line-of-sight check in this method. EntityUtil.isHostile excludes all EntityPlayer before config; specific BLOCK means force hostile, ALLOW means friendly, then general lists, IMob/monster classification. Do not read blacklist as immune. Default Disarm BLOCK villager/ALLOW enderman; these are config declarations, not evaluated runtime config. No isBoss/canSummonHostile call, so unrelated helper boss exclusion is not inherited.',
 'Lazy static HANDS order mainhand/offhand, ARMOR head/chest/legs/feet. For each qualified target, every nonempty hand except any RED_FLOWER item marks disarmed before server writes. Server replaces hand with flower if FLOWERS else EMPTY, then randomly submits original stack to external ItemUtil.spawnItem. No item-copy or drop-result acknowledgment in concrete class; engine/helper handling not expanded. Flowers with any metadata are skipped by item identity, not recognized original weapon ownership.',
 'Hand drop condition always uses drop_chance+chance_increase, even without info.has(DROP_CHANCE); at declared defaults0.35+0.35=0.70. Registered boost_drops modifier is not consulted by this branch. This is source arithmetic, not observed loot frequency; runtime properties/config may change it. Do not infer native spawn success from probability or receipt.',
 'Armor flags compute only drop probability: ARMOR1 adds armor_chance, ARMOR2 adds same value; default noflags0, one0.30, both0.60. Yet every nonempty armor slot marks disarmed and is cleared server-side regardless of flags/chance. With default chance0 and no flags, equipped armor removed without drop submission. Removal precedes optional spawn, no rollback/custody return/restore schedule. All slots in same target complete before count logic.',
 'For each disarmed target, server optionally attempts poison, fire, weakness and native knockBack then sends MessageDisarmFX using integer target BlockPos to sendToAllTracking(...,caster). This flag means at least one nonempty eligible slot found, not verified drop, potion admission, knockback acceptance, final damage or delivery. Anchor selection passed to tracking helper is caster rather than target; helper audience implementation external. No Boss resistance text, final refusal reason or per-target rate limiter here.',
 'DUO result asymmetry: withoutDUO first disarmed target returns true; withDUO, count initially0, first and second mutations count++ and continue; third reaches count==2 and returns true after mutation/FX. If loop ends after only1or2 eligible disarmed targets it returns false although equipment/effects/FX already committed. Nonhostile/empty/flower-only targets do not increment; no targets0false. Thus max3 targets can mutate with DUO, not inferred2 from name; list order native unspecified.',
 'Shared SpellBase maps concretefalse to CastResult.FAIL: suppresses generic initial cast sound and prevents ItemStaff.enactCosts/setCooldown, while earlier per-target removal and FX are not reverted. costsMet still required before cast (noncreative). With3 successful-slot targets returns true and costs/cooldown only once; with0 no mutation. This is exact local branch reasoning, not a runnable reproduction or claim no other mod charges resources. No upstream code executed.',
 'MessageDisarmFX contains only xyz doubles, no targetID/UUID/dimension/reason/slot/drop identity/success aggregate. ClientMessageHandler enqueues through ClientTickHandler END then MessageHandler executes concrete consumer. It obtains current Minecraft.world without explicit null/world-generation check and submits smoke at stored BlockPos +(0.5,3,0.5), fixed velocity0, red=spell red1,greenblue0,alpha1,randomscale6..12,lifetime60. No continuing entity tracking or current target lookup. Missing/changed dimension semantics not protected by payload; actual transport/lifecycle not run.',
 'ParticleUtil checks MysticalLib client proxy and global counter/random particleSetting throttle before external PARTICLE_SMOKE spawn; additive argument not forwarded by this overload (last argument1). Therefore API receipt can be suppressed by visual settings and cannot prove actual visible smoke. RootsPacketHandler registers MessageDisarmFX twice in same method, but external registration semantics not read; no claim duplicate delivery/crash. Common END queue removes after runnable returns; throwing handler can skip removal/ticking reset; no finally/queue world-reset shown, only conditional static risk.',
 'Config getters lazily cache parsed sets; EntityConfig.onConfigChanged shown only sync, no explicit invalidation of these four sets. Parsing helper external. Classification helper/native equipment changes, effect application, knockback, spawn helper, packet distribution and renderer are distinct external success boundaries. Whole concrete chain is read and bounded; no universal Boss immunity, successful salvage/drop or visual acceptance inferred.',
 'One independent aggregate settlement policy only. Six slots, chance knobs, DUO counts, per-target cues, producer costs, queue, packet, config and damage/effect variants earn0 extra. Adjacent Sanctuary remains exploratory0;046 nondetection pending independent and not counted.'
 ],
 'settlement_cases':[{'duo':False,'disarmed_targets_available':0,'mutated_targets':0,'cast_return':False,'native_wrapper_payment':False},
 {'duo':False,'disarmed_targets_available':1,'mutated_targets':1,'cast_return':True,'native_wrapper_payment':'once noncreative server'},
 {'duo':True,'disarmed_targets_available':1,'mutated_targets':1,'cast_return':False,'native_wrapper_payment':False},
 {'duo':True,'disarmed_targets_available':2,'mutated_targets':2,'cast_return':False,'native_wrapper_payment':False},
 {'duo':True,'disarmed_targets_available':'3 or more','mutated_targets':3,'cast_return':True,'native_wrapper_payment':'once noncreative server'}],
 'case_limits':'Static normal-return branches given prior eligibility/cost checks, nonthrowing external operations and unchanged traversed slots; not executed tests or fake server receipts.',
 'critical_boundaries':['Roots1.12.2 pinned source only; no current Dynasty behavior or cross-version code compatibility claim.',
 'External MysticalLib ItemUtil.spawnItem/PacketHandler/ConfigUtil/particle renderer and native Forge equipment/drop/potion/knockback/transport internals absent from local expanded chain. API submission not native acceptance.',
 'No production/test/art/source modification, no native game/Java/Gradle/upstream execution, no network/download, no shared Jar/master/session/pending/checklist changes.',
 'Formal477 remains;046/047 both pending0. Existing migration and045 accepted verifiers not rerun. No hashes/line counts as semantic credit.'],
 'application':'Boss免控應在真正裝備變更前拒絕並回傳原因；逐目標效果、整次施法成功與付款是不同結果，不能用false代表沒有控制提交，也不能用煙霧代表掉落已成功。只研究原程序邊界，普通陰陽type9不增加灰字。',
 'counting':{'whole_policies_proposed':1,'accepted_credit':0,'native_acceptance':0},
 'next_work':'Independent whole-policy review; keep studying different source-owned mechanism without waiting for repeated dispatch.',
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0}
covered={}
for x in refs:
 a,b=x['lines'];s=set(range(a,b+1));old=covered.setdefault(x['path'],set());assert not old.intersection(s);old.update(s)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(x)==len((R/p).read_text().splitlines()) for p,x in covered.items()),cited_lines=sum(map(len,covered.values())))
p=H/'immune-reference-batch-047.json'
with p.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(p),'ranges':len(refs),'files':doc['unique_files'],'lines':doc['cited_lines'],'credit':0,'maximum_pending':1},ensure_ascii=False))

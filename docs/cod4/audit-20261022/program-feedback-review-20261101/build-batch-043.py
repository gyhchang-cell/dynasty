#!/usr/bin/env python3
"""Record a fixed-local PetalShell whole-chain screen with zero new credit."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
p42=H/'immune-reference-batch-042.json';old=json.loads(p42.read_text())
assert ref(p42)['sha256']=='d401997e18a907c7e5c235cc1db9eb3930d55b143e89319e3c69980ef8ec5924'
v=old['provenances'][0];m=next(x for x in json.loads((R/v['manifest_path']).read_text()) if x['repo']==v['repo'])
entries={x['path']:x for x in m['files']};prefix='src/main/java/epicsquid/roots/'
specs=[('spell/SpellPetalShell.java',None),('potion/PotionPetalShell.java',None),
 ('network/fx/MessagePetalShellBurstFX.java',None),('network/fx/MessagePetalShellRingFX.java',None),
 ('network/fx/ModifierPacket.java',None),('modifiers/instance/staff/ISnapshot.java',None),
 ('particle/ParticleUtil.java',[[154,173]])]
refs=[]
for n,ranges in specs:
 e=entries[prefix+n];b=(R/e['source']).read_bytes();lines=b.decode().splitlines()
 for a,z in ranges or [[1,len(lines)]]:
  refs.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],'lines':[a,z],
   'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(lines[a-1:z]).encode()),
   'reading_context':'new_actual_source_read043','purpose':'Whole source/consumer/codec or complete directly called helper; zero semantic credit.'})
new=list(refs)
support={'Roots.java','RegistryManager.java','proxy/CommonProxy.java','spell/SpellRegistry.java','init/ModPotions.java','init/ModSounds.java','init/ModDamage.java',
 'network/RootsPacketHandler.java','network/ClientMessageHandler.java','network/MessageHandler.java','event/ClientTickHandler.java','item/ItemStaff.java',
 'spell/info/StaffSpellInfo.java','spell/info/storage/StaffSpellStorage.java','util/EntityUtil.java','util/ServerHerbUtil.java','util/types/RegistryItem.java',
 'modifiers/instance/staff/StaffModifierInstanceList.java','modifiers/instance/staff/ModifierSnapshot.java','EventManager.java','spell/SpellBase.java','init/ModItems.java'}
for x in old['source_refs']:
 n=x['upstream_path'].removeprefix(prefix)
 if n not in support and not (n=='particle/ParticleUtil.java' and x['lines'] in [[1,20],[97,108]]):continue
 assert sha((R/x['path']).read_bytes())==x['file_sha256']
 y=dict(x);y['reading_context']='exact042_already_read_support_reused';y['purpose']='Existing staff/registration/event/queue/helper support0. EventManager1-249 and smoke97-108 additionally reread043, not new ranges.';refs.append(y)
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr);by={x['id']:x for x in rows}
decisions={
 'domestication-native-replenishing-retaliation-stock-refusal-with-last-hit-recharge-reset':'Closest existing stock-consumption plus independent retaliation and hit-reset clock. Petal replaces potion amplitude and refreshes remaining duration rather than collar recharge. That clock/storage difference is recorded but conservatively not enough by itself to award another complete policy.',
 'spellengine-stashed-combat-charge-consumed-on-attempt-with-deferred-effect-replacement':'Existing effect charge consumption even without accepted impact and type-based replacement. Petal is immediate and refreshes configured duration before retaliation, not deferred; no separate credit for amplifier encoding or attempt-versus-success caveat.',
 'redstonearsenal-native-charge-shield-refusal-with-break-cue-and-self-hud':'Existing charged refusal/resource transition/sound/HUD chain. Petal ring packet and potion state differ, but new visual codec or storage field is not a new semantic unit.',
 'tf-lich-shield-and-clone-rejection':'Already includes refusal after decrementing shield resource and dedicated break feedback. Petal has no damage-type break qualification and is not a new Boss-specific refusal receipt.',
 'dungeonsmobs-native-shared-shield-overflow-tick-cascade-versus-regeneration':'This accepted policy has shared damage debt, later tick cascade and regeneration. Petal has none of those; no independent damage debt/overflow mechanism is being proposed merely because several shells are drawn.',
 'wizardry-shadowward-retaliatory-split-and-recursion-exclusion':'Existing retaliation/refusal control explicitly excludes retaliatory source. Petal has no such source exclusion and decrements stock before retaliatory requests; finite stock is not proof of safe engine recursion. No separate retaliation-family credit.'}
cmps=[{'accepted_id':k,'full_semantic_decision_read':{a:v for a,v in by[k].items() if a not in ['source_refs','auxiliary_refs']},'distinction':s,'reading_context':'complete_semantic_decision_read043'} for k,s in decisions.items()]
mig=old['migration_overlap_screen'];mlraw=(R/mig['path']).read_bytes();mi={x['candidate_id']:x for x in [json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]}
for x in mig['comparisons']:assert all(mi[x['accepted_id']][k]==value for k,value in x['complete_semantic_decision_read'].items())
doc={'schema_version':1,'owner':'program-feedback-review-043','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'HOLD_ZERO_EXISTING_STOCK_REFUSAL_RETALIATION_AND_EFFECT_REPLACEMENT_OVERLAP','research_credit':0,'maximum_proposed_credit':0,
 'production_changes':False,'runtime_executed':False,'repo':m['repo'],'commit':m['commit'],'provenances':old['provenances'],'source_refs':refs,
 'prior_read_reuse':{'evidence':ref(p42),'new_ranges':len(new),'new_cited_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in new),'reused_ranges':len(refs)-len(new),'source_reread_credit':0},
 'baseline':{'accepted041_receipt':old['baseline']['accepted041_receipt'],'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'042_pending_proposal':ref(p42),'040_credit':0},
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(rows),'comparisons':cmps,'scope':'Metadata screen and six complete saved semantic judgments read. Not all ledger source chains reread.'},
 'migration_overlap_screen':{'path':mig['path'],'sha256':sha(mlraw),'rows':len(mi),'comparisons':mig['comparisons'],'reuse_evidence':ref(p42),
  'scope':'Existing Roots staff/library migration owner exact previously read judgment reused, current equality checked. PetalShell/petal_shell/petal shell metadata search found no named owner; this does not imply every migration source was reread.'},
 'whole_chain_observation':[
  'Exact earlier native lifecycle, concrete SpellRegistry insertion/finalise, potion registration, client packet registration and actual staff right-click wrapper reused. SpellPetalShell server cast saves modifier snapshot before addPotionEffect and sends burst independently of native effect acceptance. Return true on both sides; usual cast sound/cost/cooldown cannot prove target protection.',
  'Self always receives application attempt. Optional PEACEFUL chooses one random EntityLivingBase in precomputed relative box offset to player block position, filtered with EntityUtil.isFamiliar(player,target), so this owner-specific predicate differs from TimeStop generic familiar skip. No guaranteed candidate, no Boss check, no all-familiar grant. Snapshot replaced before querying old effect.',
  'With CHARGES, calculated shells=maxShells+extraShells is used only when target already has petal_shell. A first application uses maxShells even with CHARGES, both for selected familiar and caster. Native potion combination/admission semantics are external; do not assert every recast exactly overwrites existing stronger effect or accepted duration.',
  'Native HIGHEST LivingHurt onDamage reads current petal effect then server-side computes amplifier-1, removes effect, reads saved modifiers, and if newCount>0 attempts a replacement potion with the full configured duration. It does not preserve remaining duration. Otherwise no replacement. Break/end sound selected solely by newCount, gated by spell sound setting; replacement acceptance not checked.',
  'No local amount>0, unblockable, fire, environmental, trueSource existence or already-canceled guard is required to consume stock once handler is invoked. Earlier Aqua/Storm/TimeStop/Resistance branches can alter/cancel/retaliate within the same method and continue to Petal. Amplifier0/negative still enters presence gate, removes, then refuses. Native event dispatch can filter events before this handler; not claiming every attack reaches it.',
  'After stock removal/replacement, independent modifier if branches attempt radiant/physical/fire damage and poison/levitation/weakness/slow/bleed on trueSource as appropriate. Returned hurt/effect outcomes ignored. Final original event amount0 and canceledtrue occur after retaliation, followed by burst. No explicit retaliatory damage-source exclusion. Normal positive stocks can be depleted through nested calls, but no engine recursion, immortality, exact damage or exception safety guarantee.',
  'Once effect absent the next delivered handler has no Petal gate until recast. Passive duration expiration is native, and complete PotionPetalShell has no removal callback/explicit end sound or snapshot deletion. End sound in EventManager denotes count exhaustion path, not every duration expiry. No stock-regeneration tick, world orphan sweep or saved prior target state.',
  'Potion isReady always true; performEffect server-side obtains current modifier snapshot and sends ring with target ticksExisted, xyz, amplifier and modifier snapshot. Both ring and burst registered clientside. Actual inherited handler queues at client END from previous evidence. No entityID/UUID/dimension/generation/sequence/expiry or current target revalidation; ring is positional snapshot, not authoritative client shield-state storage.',
  'Ring handler computes angle from transmitted amplifier and loops up to locally configured maxShells+optional extra, stopping after decrement count<=0. An incoming count0 is not rejected before division, so infinity/NaN positions can be constructed if such a packet is processed; no malformed packet runtime tested. Negative local shell cap can skip loop. Commented legacy loop is not runtime behavior. Client cap/config and server amplifier may disagree; no exact visual stock guarantee.',
  'Burst packet has same meaning for initial cast and consumed hit: coordinates/modifier snapshot only, no refusal reason/result. First loop ten attempts, second loop random nextInt12 increment can0. No fixed worst-case loop bound claimed. Ring and burst use current world without null check; actual delivery/tracking self inclusion/external MysticalLib internals unverified.',
  'Concrete petal array overload substitutes vz for vx, then scalar no-boolean overload calls smoke helper, which submits LibRegistry.PARTICLE_SMOKE. Both actual ring/burst paths use that overload. Boolean noDepth variant submits registered petal type but is not invoked here. These are read code call-path findings, no asset/pixel evaluation and no new art/particle-policy credit.',
  'ModifierPacket delegates StaffModifierInstanceList snapshot serialization; ISnapshot default toBytes is empty but actual snapshot/list overrides from reused whole files apply. No target identity/result magically added by superclass. Shared staff payment/migration infrastructure0, modifier/color/familiar variants0.'
 ],
 'decision':'Hold0. Complete native consumed-stock refusal/retaliation already has accepted owners, and effect-instance charge replacement and feedback boundaries also already studied. Immediate replacement with full duration, first-cast extra-shell omission and presentation helper differences are recorded implementation details, not sufficient new independent complete-policy credit. Not a claim that every implementation byte is identical.',
 'critical_boundaries':[
  'Fixed Roots1.12.2 commit only. Native potion merge/removal/timer, LivingHurt dispatch/cancellation/recursive damage, matching MysticalLib transport/particle engine are not expanded or executed.',
  'No Boss-specific immune message or ordinary constitution gray text added. Damage refusal, failed application, exhausted resource and visual effect are separate meanings.',
  'No source acquisition, game, Java, Gradle, shared Jar, model/texture/building, master ledger/session/checklist changes. No accepted reference or completed original task claimed.',
  'EventManager and particle smoke full selected methods explicitly reread; other support reused unchanged from042/041, not claimed newly read. Six old semantic decisions read, not their entire upstream chains.'
 ],
 'application':'将控制拒绝与护盾吸收分开；不要因施法或反击请求就发送接纳回执。库存消费、剩余期限重置与到期解除的提示须各自绑定真实结果。保留这次完整观察供排重，不据此新增参考数或修改生产。',
 'counting':{'whole_policies_proposed':0,'accepted_credit':0,'helper_variant_parameter_credit':0,'native_acceptance':0},
 'next_work':'042 separate independent review continues. Keep043 hold0; seek another genuinely different complete original-program mechanism in fixed local cache.'}
covered={}
for x in refs:
 a,b=x['lines'];now=set(range(a,b+1));prev=covered.setdefault(x['path'],set());assert not prev.intersection(now);prev.update(now)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(v)==len((R/k).read_text().splitlines()) for k,v in covered.items()),cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-043-screen.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'new_ranges':len(new),'new_lines':doc['prior_read_reuse']['new_cited_lines'],'all_ranges':len(refs),'credit':0},ensure_ascii=False))

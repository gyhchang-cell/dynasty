"""Close Armara stock and perk knockback screen conservatively at zero."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def load(p):return json.loads(p.read_text())
prior=H/'batch-054-discovery-checkpoint.json';d0=load(prior)
assert ref(prior)['sha256']=='39bd44c986a7501c3650f2edc2dfbd1d801bc26f362de04cdd324462d4409fc4'
ps={n:H/f'immune-reference-batch-{n}.json' for n in ['050','051','052','053']}
ds={n:load(p) for n,p in ps.items()}
v=ds['050']['provenances'][0];raw=(R/v['manifest_path']).read_bytes();assert sha(raw)==v['manifest_sha256']
m=next(x for x in json.loads(raw) if x['repo']==v['repo']);es={x['path']:x for x in m['files']}
prefix='src/main/java/hellfirepvp/astralsorcery/'
refs=[dict(x,reading_context='exact054_discovery_whole_file_reused0') for x in d0['source_refs']]
def source(n,a=1,z=None):
 e=es[prefix+n];b=(R/e['source']).read_bytes();ls=b.decode().splitlines();z=z or len(ls)
 assert 1<=a<=z<=len(ls) and sha(b)==e['sourceSha256']
 refs.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],
 'lines':[a,z],'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(ls[a-1:z]).encode()),'reading_context':'actual_read054_closure'})
for n in ['common/constellation/mantle/MantleEffect.java','common/item/armor/ItemMantle.java',
 'common/event/PlayerAffectionFlags.java','common/registry/RegistryMantleEffects.java',
 'common/constellation/IWeakConstellation.java','common/constellation/ConstellationRegistry.java']:source(n)
for n,a,z in [('common/constellation/IConstellation.java',96,98),('common/constellation/IConstellation.java',135,155),
 ('common/registry/internal/PrimerEventHandler.java',187,189),('common/registry/RegistryItems.java',103,103)]:source(n,a,z)
reuse50={'common/auxiliary/charge/AlignmentChargeHandler.java','common/network/play/server/PktSyncCharge.java',
 'client/event/AlignmentChargeRenderer.java','common/event/handler/EventHandlerCache.java','AstralSorcery.java',
 'common/CommonProxy.java','common/registry/internal/PrimerEventHandler.java','common/registry/internal/InternalRegistryPrimer.java',
 'common/network/PacketChannel.java','common/network/base/ASPacket.java','common/network/channel/SimpleSendChannel.java','common/network/channel/BufferedReplyChannel.java'}
for x in ds['050']['source_refs']:
 n=x['upstream_path'].removeprefix(prefix)
 if x['repo']=='HellFirePvP/ObserverLib' or n in reuse50:
  if n=='common/registry/internal/PrimerEventHandler.java' and x['lines']==[195,197]:continue
  refs.append(dict(x,reading_context='exact050_shared_resource_transport_bootstrap_reused0'))
for x in ds['051']['source_refs']:
 if x['upstream_path'].removeprefix(prefix) in {'common/util/tick/TimeoutList.java','common/util/tick/TimeoutListContainer.java','common/util/NameUtil.java'}:
  refs.append(dict(x,reading_context='exact051_timeout_registration_support_reused0'))
for x in ds['052']['source_refs']:
 n=x['upstream_path'].removeprefix(prefix)
 if n=='common/util/nbt/NBTHelper.java' or (n=='common/registry/RegistryItems.java' and x['lines']==[174,182]):
  refs.append(dict(x,reading_context='exact052_stack_nbt_registration_support_reused0'))
for x in ds['053']['source_refs']:
 if x['upstream_path']==prefix+'common/util/MiscUtils.java' and x['lines']==[645,677]:
  refs.append(dict(x,reading_context='exact053_fake_player_guard_reused0'))
ledger=A/'immune-feedback-research/reviewed.json';lb=ledger.read_bytes();rows=json.loads(lb);idx={r['id']:r for r in rows}
fields=['id','status','repo','commit','category','semantic_dedup_key','count_unit','full_chain_observation','concrete_observation','application_to_boss_immune','limitations','research_credit','reviewed_utc']
cmps=[]
for c in d0['dedup_snapshot']['complete_saved_decisions']:
 assert all(idx[c['id']][k]==v for k,v in c.items())
 cmps.append({'accepted_id':c['id'],'complete_semantic_decision_read':c,
 'distinction':'No new credit: final knockback admission or replenishing-stock refusal already has a whole accepted owner. Different perk/equipment/charge qualifier and absence of retaliation are insufficient on this evidence.'})
k='malum-native-aegis-incoming-denial-transformed-capacity-and-postattack-window'
cmps.append({'accepted_id':k,'complete_semantic_decision_read':{f:idx[k][f] for f in fields},
 'distinction':'Accepted native stock conversion/refusal/sync lifecycle already covers replenishing charge budget. Armara equipment NBT, prechecked energy and orbit particles are recorded differences, not sufficient new whole-policy credit.'})
p43=H/'immune-reference-batch-043-screen.json';d43=load(p43)
progress_path=A/'immune-feedback-research/progress.json';progress=load(progress_path);assert len(rows)==progress['reviewed_effective_semantic_dedup']
observations=[
 'RegistryMantleEffects constructs Armara; base constructor names it with constellation key and attaches HIGH LivingHurt plus PLAYER END tick through real Forge/Observer registrations. Registry primer initializes mantle registry and fills it; IWeakConstellation.getMantleEffect queries by the same registry name. ItemMantle is registered chest armor; live getEffect resolves chest stack constellation and enabled effect. Actual configured values/installed binary and native registry injection unexecuted.',
 'Regeneration base tick first checks effect enabled, live matching mantle, then server player/nonfake for server branch. It marks a NoOpAffectionFlag and invokes tickServer. Client invokes particle tick on qualified local side. Damage listener separately permits any LivingEntity wearing a qualifying mantle on server, not only the player type eligible for regeneration. No actual autonomous mob equipment acquisition or native transfer behavior inferred.',
 'Armara tick reads current chest-stack IStacks. At or above configured max it resets ITick to configured recharge and returns, without clamping excess stack count. Below cap, decrements local tick; when due and hasCharge passes, writes ITick reset and IStacks+1 BEFORE calling drainCharge(false), whose boolean is ignored. Due insufficient charge does not write decremented value, so retries on later eligible ticks with old ITick. Existing050 ordinary same-thread shared drain has no shown intervening callback here: ignored result is not proof of free stock on normal execution. Creative/spectator hasCharge/drain both allow without payment. Default3/300/750 are declared defaults only.',
 'Armara HIGH LivingHurt checks server world and live enabled Armara mantle, then rejects source.canHarmInCreative; positive stock consumes exactly1 and returns true, caller cancels. No amount>0, attacker existence/team, damage receipt, actual HP loss, new energy payment or post-hit recharge reset in this path. Nonpositive stocks do not cancel. Native event defaults/composition and actual DamageSource bypass definitions remain outside this read; no all-source invulnerability claim.',
 'Data owner is current chest ItemStack persistent astralsorcery compound, fields IStacks and ITick; getData returns detached empty compound for null/non-mantle. This is neither UUID balance nor global player flag. Unequip/mismatched constellation/disabled effect stops regeneration and admission but these complete classes do not erase stock/countdown. ItemMantle.setConstellation edits only constellationName, leaving fields; direct switch/re-equip retains existing stack fields if native stack NBT survives. No shared process/world tick decay or clone policy is implemented here. Engine save/death item retention/inventory transport unexpanded.',
 'PlayerAffectionFlags uses UUID/list timeout10 renewal but Armara base creates NoOpAffectionFlag; expiry callback is empty and does not clear stock or restore armor. Server cache clear clears flags, not current equipment NBT. Full helper, TimeoutList and container support establish that boundary; these accepted timer helpers add0. No mantle-specific explicit removal cleanup path exists in complete base/item/Armara classes.',
 'Feedback is client current stack count. Armara draws orbiting particles seeded by player UUID, plus cape sparkles, with point-of-view-dependent transparency. Stock mutators only putInt and emit no dedicated packet/dirty setter/refusal reason. No custom hit/deplete sound or graytext in these shown paths. Native item NBT/equipment synchronization is external, so visibility/remote timing and same-frame correctness are not claimed. Shared050 PktSyncCharge/HUD concerns energy balance; ItemMantle.getAlignmentChargeCost returns0, so it does not expose Armara refill cost through that preview. Neither orbit nor charge HUD certifies actual cancellation.',
 'KeyNoKnockback complete52 lines already read in discovery: live player side research hasPerkEffect then LivingKnockBack cancel, no own distinct state/payment/receipt lifecycle. Discovery prose53 was a count typo; bound1..52 and total279 were already correct, corrected by handoff044. Pure eligibility variant stays0 and is not expanded into another whole candidate.',
 'Three complete accepted stock/knockback decisions and full043 held policy observations/decision compared. Accepted050 owns charge availability/arithmetic/reconciliation; pending053 concerns repeated player immunity/cinematic exits, accepted052 one-use source token, accepted051 independent death token. Armara differences in current stack owner, no hit reset, event/source predicate, refund absence and client orbit are not sufficient independent whole-policy novelty here. Conservatively hold entire replenishment/refusal family0, not a claim that source bytes match.'
]
doc={'schema_version':1,'owner':'program-feedback-review-054','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'HOLD_ZERO_EXISTING_REPLENISHING_STOCK_AND_KNOCKBACK_QUALIFICATION_OVERLAP',
 'research_credit':0,'maximum_proposed_credit':0,'repo':m['repo'],'commit':m['commit'],
 'provenances':ds['050']['provenances'],'source_refs':refs,
 'prior_read_reuse':{'evidence':[ref(prior)]+[ref(p) for p in ps.values()],
 'scope':'Two full discovery classes reused; six newly read complete base/item/flag/registry/interface classes plus selected exact NBT/registration methods. Accepted resource/bootstrap and previously read timeout/stack helpers reused0. No old verifier rerun or old sources claimed newly read.'},
 'baseline':{'progress':ref(progress_path),'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'old_verifier_or_ledger_rerun':False},
 'dedup_snapshot':{'path':str(ledger.relative_to(R)),'sha256':sha(lb),'rows':len(rows),'comparisons':cmps,
 'scope':'Two entire saved decisions read in054 discovery and exact retained, Malum full decision newly read during closure. Original old source chains not reread.'},
 'held_comparison':{'evidence':ref(p43),'complete_policy_observations_read':d43['whole_chain_observation'],'complete_decision_read':d43['decision'],'critical_boundaries_read':d43['critical_boundaries']},
 'existing_work_overlap':[{'evidence':ref(p),'distinction':'Prior whole mechanism kept intact; no new shared-charge/timer/source-token/death-token/ceremony variant credit.'} for p in ps.values()],
 'whole_chain_observation':observations,'decision':'Hold0/max0. Stock regeneration plus conditional one-stock refusal and current-equipment qualification have existing whole owners. Retained-NBT, prechecked shared charge and state particles recorded as implementation details, not new credit. KeyNoKnockback is also qualification-only overlap0.',
 'critical_boundaries':['Fixed historical source only; native inventory/NBT sync, MC/Forge event order and damage-source definitions not expanded or executed. No successful protection/remote orbit/damage or runtime defect proof.',
 'Ordinary hasCharge then drain path has no shown callback between; ignored drain bool is not proof of normal payment failure or resource exploit.',
 'Unequip/config/constellation changes gate current qualification but do not erase stack fields in these classes. Native clone/death/dropped-item retention unknown; do not claim unconditional persistence.',
 'Whole screen0. No new semantic candidate, no self-credit, no production/test/art/background/sharedJar/game/master/checklist changes, network/Java/Gradle/upstream execution or hours claim.'],
 'application':'原程序仍須把可用庫存、當前裝備資格、實際拒絕結果與顯示分開。只記錄邊界，不新增護盾玩法或普通體質灰字。',
 'counting':{'whole_policies_proposed':0,'accepted_credit':0,'runtime_credit':0},
 'next_work':'Proceed to a different fixed-local original-program mechanism; do not count another charge consumer/stock constant/knockback qualifier. Astral repository not declared exhausted.',
 'production_changes':False,'runtime_executed':False,'network_requests':0,'master_changes':False,'checklist_deletions':0,'hours_claimed':0}
covered={}
for x in refs:
 b=(R/x['path']).read_bytes();assert sha(b)==x['file_sha256']
 a,z=x['lines'];new=set(range(a,z+1));old=covered.setdefault(x['path'],set());assert not old.intersection(new);old.update(new)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(s)==len((R/p).read_text().splitlines()) for p,s in covered.items()),cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-054-screen.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'ranges':doc['source_ranges'],'files':doc['unique_files'],'full_files':doc['full_files'],'lines':doc['cited_lines'],'credit':0,'maximum_pending':0}))

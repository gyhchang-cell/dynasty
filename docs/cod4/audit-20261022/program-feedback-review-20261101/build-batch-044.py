#!/usr/bin/env python3
"""Fixed-local LightDrifter ownership exclusion; no new semantic proposal."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
R=Path('/Users/a15356015027/Desktop/dynasty');H=Path(__file__).resolve().parent;A=H.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
p43=H/'immune-reference-batch-043-screen.json';old=json.loads(p43.read_text())
assert ref(p43)['sha256']=='520f95549a0176dbe9b4d94dee475086c3727a12202c3631e8c3563bd3fbba88'
v=old['provenances'][0];m=next(x for x in json.loads((R/v['manifest_path']).read_text()) if x['repo']==v['repo'])
entries={x['path']:x for x in m['files']};prefix='src/main/java/epicsquid/roots/'
def source(n,ranges=None,context='new_actual_source_read044'):
 e=entries[prefix+n];b=(R/e['source']).read_bytes();lines=b.decode().splitlines();out=[]
 for a,z in ranges or [[1,len(lines)]]:
  out.append({'repo':m['repo'],'commit':m['commit'],'path':e['source'],'upstream_path':e['path'],'lines':[a,z],
   'file_sha256':sha(b),'git_blob_sha1':e['source_blob'],'range_text_sha256':sha('\n'.join(lines[a-1:z]).encode()),'reading_context':context,
   'purpose':'Actual complete class/selected method reading; no semantic credit.'})
 return out
refs=[]
for n in ['spell/SpellAugment.java','network/MessageLightDrifterSync.java','client/SpectatorHandler.java','client/gui/GuiFakeSpectator.java','network/fx/MessageLightDrifterFX.java']:refs+=source(n)
refs+=source('EventManager.java',[[251,289]])
new=list(refs)
support={'Roots.java','RegistryManager.java','proxy/CommonProxy.java','spell/SpellRegistry.java','init/ModSounds.java','network/RootsPacketHandler.java',
 'network/ClientMessageHandler.java','network/MessageHandler.java','event/ClientTickHandler.java','item/ItemStaff.java','spell/info/StaffSpellInfo.java',
 'spell/info/storage/StaffSpellStorage.java','util/ServerHerbUtil.java','util/types/RegistryItem.java','modifiers/instance/staff/StaffModifierInstanceList.java',
 'modifiers/instance/staff/ModifierSnapshot.java','EventManager.java','spell/SpellBase.java','init/ModItems.java'}
for x in old['source_refs']:
 n=x['upstream_path'].removeprefix(prefix)
 if n not in support and not (n=='particle/ParticleUtil.java' and x['lines'] in [[1,20],[97,108]]):continue
 assert sha((R/x['path']).read_bytes())==x['file_sha256']
 y=dict(x);y.update(reading_context='exact043_already_read_support_reused',purpose='Unchanged producer/registration/update/refusal/client queue support0; no new reading credit.');refs.append(y)
probes=[]
for n in ['spell/SpellSanctuary.java','event/SneakHandler.java','potion/PotionNondetection.java']:probes+=source(n,context='exploratory_full_file_read044_incomplete_chain_zero')
lp=A/'immune-feedback-research/reviewed.json';lr=lp.read_bytes();rows=json.loads(lr)
mig=old['migration_overlap_screen'];mlraw=(R/mig['path']).read_bytes();mi={x['candidate_id']:x for x in [json.loads(l) for l in mlraw.decode().splitlines() if l.strip()]}
cmps=[]
for x in mig['comparisons']:
 assert all(mi[x['accepted_id']][k]==value for k,value in x['complete_semantic_decision_read'].items())
 cmps.append({'accepted_id':x['accepted_id'],'complete_semantic_decision_read':x['complete_semantic_decision_read'],
  'distinction':'No distinct proposal. Existing migration owner explicitly already includes actual LightDrifter cast temporary spectator/damage-disable/flight, event countdown, expiry restore and root-key deletion. Current full server/client observation supports exclusion; do not re-award by network/helper/detail.'})
ac=A/'immune-feedback-research/coordinator-roots-time-stop-acceptance-20261103.json';accept=json.loads(ac.read_text())
assert accept['after_count']==476 and accept['decision']=='ACCEPTED_ONE_RESEARCH_REFERENCE_ONLY'
review=R/accept['independent_review']['path'];assert ref(review)['sha256']=='038361eade7d8f27f87d069bd9fab3c4a05199870acbe5b1e00f8d5f8bce8179'
doc={'schema_version':1,'owner':'program-feedback-review-044','created_utc':datetime.now(timezone.utc).isoformat(),
 'status':'HOLD_ZERO_LIGHT_DRIFTER_ALREADY_OWNED_BY_ACCEPTED_MIGRATION_FAMILY','research_credit':0,'maximum_proposed_credit':0,
 'production_changes':False,'runtime_executed':False,'repo':m['repo'],'commit':m['commit'],'provenances':old['provenances'],'source_refs':refs,
 'prior_read_reuse':{'evidence':ref(p43),'new_ranges':len(new),'new_cited_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in new),'reused_ranges':len(refs)-len(new),'source_reread_credit':0},
 'exploratory_reads':probes,'exploratory_read_credit':0,
 'baseline':{'accepted042_receipt':ref(ac),'accepted042_review':ref(review),'formal_count_observed':len(rows),'gap_to1000':1000-len(rows),'043_hold_zero':ref(p43)},
 'dedup_snapshot':{'path':str(lp.relative_to(R)),'sha256':sha(lr),'rows':len(rows),'comparisons':[],
  'scope':'Relevant immune IDs screened only; no new whole immune judgment claim. Exact preexisting migration owner already excludes this chain.'},
 'migration_overlap_screen':{'path':mig['path'],'sha256':sha(mlraw),'rows':len(mi),'comparisons':cmps,'reuse_evidence':ref(p43),
  'scope':'Complete nine-field saved owner judgment read without truncation and checked against current ledger. Earlier oversized metadata/context output was truncated and is not claimed fully read.'},
 'whole_chain_observation':[
  'Native ItemStaff and SpellBase wrapper/registered SpellAugment already read and reused. LIGHT_DRIFTER makes actedtrue even client-side. Server enables disableDamage/allowFlying/noClip, writes finite duration and starting xyz (Y+0.5)/dimension, records CREATIVE if creative flag else SURVIVAL, then sets SPECTATOR and sends UUID state packet plus coordinate FX. It does not preserve arbitrary original capabilities or ADVENTURE mode. Client cast independently installs fake spectator GUI.',
  'No already-active tag check in concrete cast. A repeat invocation can overwrite saved origin/dimension/mode from then-current state; normal ability to trigger another cast while spectator, engine flag details and cooldown remain unverified. Do not claim a reproducible mode-loss bug or native route.',
  'Existing native onEntityTick server EntityPlayer with root tag decrements and invokes onEnd at<=0. TimeStop removal/cancel earlier in same handler does not return, so this code can still run within that invocation. Delivery frequency/canceled event/native spectator update behavior unexpanded; duration is delivered updates, not proven wall-clock.',
  'Concrete onEnd first attempts RESISTANCE40 amplifier10; existing onDamage cancels while RESISTANCE amplifier equals10. Then explicitly clears flying/disableDamage/noClip/isFlying. If different dimension, request changeDimension to saved BlockPos and yaw; same dimension calls setPositionAndUpdate with current xyz, not saved origin. changeDimension result ignored. setGameType saved CREATIVE/SURVIVAL occurs after explicit clears and may have native side effects not expanded.',
  'Then extinguish, send disable packet with UUID/current coordinates/saved mode/current dimension, remove six root keys, optionally submit configured end sound. Native effect/teleport success and packet delivery are not conditions for key deletion. No returned handle or rollback. Native clone/save/logout/offline timers not investigated, no seamless resume guarantee.',
  'MessageLightDrifterSync codecs carry UUID,xyz,enable,mode,dimension. Client native END queue reused. Handler guards Minecraft/player but not world explicitly, finds matching UUID in current world; missing target silently loses update. Dimension field is serialized but neither validated nor applied (changeDimension lines commented). No generation/sequence/replay protection.',
  'Client disable path sets position, restores real spectator GUI only for local target, sets noClipfalse; enable sets noCliptrue and position but does not install fake GUI. Then isFlying=enable, setGameType(mode fallback), followed by disableDamage/allowFlying=enable. Thus disablefalse writes these flags false after game-mode application, including a CREATIVE mode packet. Code ordering only, native renderer/ability behavior not run.',
  'SpectatorHandler directly delegates GuiFakeSpectator. Fake GUI lazy-static captures original spectatorGui once and suppresses hotbar/tooltips/page/selection/scroll/middle-click with no-op overrides, reports menu inactive. Restore uses saved instance; no current world/player generation guard, no reset method in complete class. Current client GUI lifecycle external, no asserted observed stale GUI.',
  'Start FX coordinate-only current-world smoke submission, random step can0, no target identity or actual protection result. Native registered LightDrifter state/FX calls plus current source END sound are API submissions, not delivery/visibility/sound proof. Particle array smoke helper exactly reused; no media/art work.',
  'Existing migration judgment explicitly covered this same runtime lifetime/restore/root deletion and permanent-versus-temporary distinction. UUID sync/GUI/detail observations are support to that owner, not a new independent reference or a split variant.'
 ],
 'exploratory_limits':[
  'SpellSanctuary165 lines read completely: continuous cast overwrites qualified targets motion by position delta within distance-squared threshold r=1+x+z, optional effects, periodic ring. External radius helper, spell feature classification config, actual continuous cast cadence and concrete FX consumers not expanded here. Incomplete whole-chain candidate, no proposed credit.',
  'SneakHandler87 and PotionNondetection37 lines read completely. Visibility multiplier0 or999 based on SENSE_PLANTS, but lowest target-assignment clears EntityMob revenge/attack target whenever player nondetection active. No complete SpellExtension producer or native visibility aggregation contract read here. Quiver sneaking branch unrelated support0; do not infer nondetection manipulates sneaking input.'
 ],
 'decision':'Hold0: exact accepted migration owner already contains LightDrifter complete lifecycle. Exploratory Sanctuary/Nondetection files remain incomplete chains0. No new immune or migration count.',
 'critical_boundaries':['Fixed Roots1.12.2 only, no native potion/damage/teleport/capability/GUI/transport runtime assurance.',
  'No file count, code-line count, branch/mode/parameter/packet is semantic credit. No full truncated metadata output reading claimed.',
  '042 accepted476 by coordinator separate receipt; original042 remains historical.043/044 zero. No rerun of ledger.py or accepted verification.',
  'No production/master/session/sharedJar/instance/assets/checklist writes, no new task completion or hours claim.'],
 'application':'临时免伤的结束应分别验证模式、能力、维度、位置与客户端UI还原；不能以结束声或删除计时键替代成功回执。此处仅补齐既有owner排重证据，不移植。',
 'counting':{'whole_policies_proposed':0,'accepted_credit':0,'native_acceptance':0},
 'next_work':'Seek a truly independent complete policy; use saved exploratory files as prior reading if continued, then expand actual producer/consumer and compare closest accepted owners before proposing.'}
covered={}
for x in refs:
 a,b=x['lines'];now=set(range(a,b+1));prev=covered.setdefault(x['path'],set());assert not prev.intersection(now);prev.update(now)
doc.update(source_ranges=len(refs),unique_files=len(covered),full_files=sum(len(v)==len((R/k).read_text().splitlines()) for k,v in covered.items()),cited_lines=sum(map(len,covered.values())))
out=H/'immune-reference-batch-044-screen.json'
with out.open('x') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'evidence':ref(out),'new_ranges':len(new),'new_lines':doc['prior_read_reuse']['new_cited_lines'],'exploratory_lines':sum(x['lines'][1]-x['lines'][0]+1 for x in probes),'credit':0},ensure_ascii=False))

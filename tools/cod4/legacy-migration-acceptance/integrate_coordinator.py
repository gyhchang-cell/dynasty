"""Verify and integrate concrete coordinator proposals; pending wrappers grant no credit."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';source=O/'coordinator-reviewed-batch-001.json'
b=json.loads(source.read_text());idx={r['candidate_id']:r for r in map(json.loads,(O/'candidates.jsonl').read_text().splitlines())};notes=[];full=[]
details={
 '70fbae3fc4fb0d3ff0d0':('QuestRam.readAdditionalSaveData','ColorFlags int/default0 and Rewarded boolean/defaultfalse plus home point','restores quest collection bitmask and reward receipt without calling reward','Same-file customServerAiStep (not generic aiStep) lines114-131 requires countColorsSet>15 AND !Rewarded, calls rewardQuest then sets true. rewardQuest emits loot, triggers advancement and marks structure. Progress and receipt must move together.'),
 '82a27a76ddd3a57610f6':('ManaCapabilityStorage.readNBT','MAX_MANA/MAX_BURNOUT/MANA/BURNOUT doubles and optional BLOOD_TYPE','sets maxima before current amounts then optional blood type','Paired writer emits those four doubles and type only when nonnull; missing primitives become0, no type assertion before NBTTagCompound cast. Ordering protects bound-sensitive setters conceptually, not proof all these fields survive death.'),
 '219ebcb77ac8240888e9':('MiscCapabilityStorage.readNBT','optional fairy_selected UUID','hasUniqueId path resolves UUID, else explicitly sets selected fairy null','Paired writer writes UUID only if selected UUID nonnull. Reader clears stale optional selection on absent/wrong-shaped UUID; this is different from wiping earned progress on missing source key.')}
for r in b['rows']:
 e=r['evidence'];c=idx[e['candidate_id']];p=R/c['private_file'];raw=p.read_bytes()
 assert hashlib.sha256(raw).hexdigest()==e['file_sha256']
 for k in ('revision','path','start_line','end_line','method_sha256','structural_fingerprint','context'):assert c[k]==e[k],(k,e['candidate_id'])
 n={k:r[k] for k in ('candidate_id','status','family','application_limit')}
 n.update(review_origin='main coordinator proposal verified by migration reviewer',coordinator_evidence_file=str(source.relative_to(R)),coordinator_observation=r['coordinator_observation'])
 if r['status']=='accepted':
  t,i,out,obs=details[r['candidate_id']];n.update(trigger=t,input=i,output=out,preservation=obs)
  full.append(dict(candidate_id=r['candidate_id'],file_sha256=e['file_sha256'],private_file=c['private_file'],full_source=raw.decode(),credit=0,purpose='writer and consumer context for accepted reader; no extra credit'))
 else:n['reason']=r['coordinator_observation']+' '+r['application_limit']
 notes.append(n)
(O/'reviews/batch-008-coordinator.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
(O/'coordinator-integration-evidence.json').write_text(json.dumps({'proposal_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'verified_rows':len(notes),'accepted':3,'full_supporting_files':full,'correction':'QuestRam actual method name customServerAiStep, original coordinator observation called it aiStep; exact code reviewed.'},ensure_ascii=False,indent=2)+'\n')
print('verified and integrated',len(notes),'decisions, 3 accepted; wrappers pending0')

"""Verify AlexsMobs full pinned contexts; retain negative implementation as explicit counterexample."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance';p=O/'coordinator-reviewed-batch-003.json';b=json.loads(p.read_text())
idx={x['candidate_id']:x for x in map(json.loads,(O/'candidates.jsonl').read_text().splitlines())};prior=list(map(json.loads,(O/'reviewed.jsonl').read_text().splitlines()));used={x['candidate_id'] for x in prior};families={x.get('family') for x in prior if x['status']=='accepted'};structs={x['evidence'][0]['structural_fingerprint'] for x in prior if x['status']=='accepted'};notes=[];files={}
details={
'7184875bae022c29b992':('Catfish readAdditionalSaveData','Items list plus swallowed entity type, HasSwallowedEntity receipt and additional entity NBT','restores owned cargo and coupled swallowed payload/receipt'),
'8148c1d8f4848ec49e86':('Elephant readAdditionalSaveData','Tamed/Chested owner flags, saved Items unsignedbyte slots, numeric DespawnDelay','initializes inventory before inserting saved stacks; typed optional delay leaves default when missing'),
'67a2fb6960951c68f75d':('Flutter readAdditionalSaveData','FlowersEaten count and indexed FlowerEaten registry IDs','clears/rebuilds paid flower diversity ledger used in tame interaction'),
'ce478305bdd43f13933e':('Hummingbird readAdditionalSaveData','CropsPollinated earned count, separate cooldown and optional HLP tuple','restores actual feeder-consumption counter; absent HLPX clears derived feeder target'),
'3e82f937e3646296a6d7':('MimicOctopus readAdditionalSaveData','FishFeedings and MimicreamFeedings paid counters and Upgraded unlock plus temporary state','restores partial paid taming/upgrade progression and unlocked state without consuming again'),
'b6655685d585e5434679':('VoidPortal readAdditionalSaveData','SisterUUID identity, destination position and ExitDimension codec','typed UUID restored, absent destination clears optional, invalid supplied dimension falls back overworld'),
'b9b065200815b0326958':('TransmutationTable load/saveAdditional negative data-loss case','TotalCount plus per-player UUID→TransmutationData and Possibility/Possiblity keys','TotalCount actual roundtrip works; per-player load writes source instead of reading, save reads instead of writing; possibility guard and read key disagree')}
for n in b['rows']:
 assert n['candidate_id'] not in used
 e=n['evidence'];es=e if isinstance(e,list) else [e]
 for e in es:
  c=idx[e['candidate_id']];raw=(R/c['private_file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['file_sha256']
  for k in ('revision','path','start_line','end_line','method_sha256','structural_fingerprint','context'):assert c[k]==e[k],(e['candidate_id'],k)
  assert hashlib.sha256(c['context'].encode()).hexdigest()==c['method_sha256']
  files[c['private_file']]={'path':c['private_file'],'revision':c['revision'],'sha256':c['file_sha256'],'full_source':raw.decode(),'credit':0}
 q={k:n[k] for k in ('candidate_id','status','family','application_limit')};q.update(review_origin='main coordinator003; primary migration reviewer verified source/hashes/dedup and full writer/consumer windows',coordinator_evidence_file=str(p.relative_to(R)))
 if n['status']=='accepted':
  assert n['family'] not in families and idx[n['candidate_id']]['structural_fingerprint'] not in structs
  t,i,o=details[n['candidate_id']];q.update(trigger=t,input=i,output=o,preservation=n['coordinator_observation'])
  if n['candidate_id']=='b9b065200815b0326958':q.update(study_kind='negative_data_loss_implementation',not_a_working_migration_example=True)
 else:q['reason']=n['coordinator_observation']+' '+n['application_limit']
 notes.append(q)
for e in b['supporting_source_windows']:
 raw=(R/e['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['file_sha256']
 assert '\n'.join(raw.decode().splitlines()[e['start_line']-1:e['end_line']]).rstrip('\n')==e['context'].rstrip('\n'),e['path']
(O/'reviews/batch-016-coordinator003.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
(O/'coordinator003-integration-evidence.json').write_text(json.dumps({'proposal_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'accepted':7,'duplicate':1,'pending_no_credit':5,'counting':'Seven whole owner restoration chains; negative transmutation implementation is studied failure case, not working fix; no per-field/key/species credits.','full_sources':list(files.values()),'windows_verified':len(b['supporting_source_windows']),'upstream_executed':False,'production_changed':False},ensure_ascii=False,indent=2)+'\n')
print('verified7 proposals including1 explicit negative, 1 duplicate, 5 pending0')

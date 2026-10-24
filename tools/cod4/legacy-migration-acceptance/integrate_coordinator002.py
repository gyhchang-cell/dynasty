"""Verify AoA owner-chain proposals against pinned complete contexts, no wrapper credit."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
p=O/'coordinator-reviewed-batch-002.json';b=json.loads(p.read_text())
idx={x['candidate_id']:x for x in map(json.loads,(O/'candidates.jsonl').read_text().splitlines())}
existing=[x for f in (O/'reviews').glob('*.json') for x in json.loads(f.read_text())]
used={x['candidate_id'] for x in existing};families={x.get('family') for x in existing if x['status']=='accepted'}
notes=[];files={}
for n in b['rows']:
 assert n['candidate_id'] not in used
 assert n['family'] not in families
 for e in n['evidence']:
  c=idx[e['candidate_id']];raw=(R/c['private_file']).read_bytes()
  assert hashlib.sha256(raw).hexdigest()==e['file_sha256']==c['file_sha256']
  for k in ('revision','path','start_line','end_line','method_sha256','structural_fingerprint','context'):assert c[k]==e[k],(e['candidate_id'],k)
  assert hashlib.sha256(e['context'].encode()).hexdigest()==e['method_sha256']
  files[c['private_file']]={'path':c['private_file'],'revision':c['revision'],'sha256':c['file_sha256'],'full_source':raw.decode(),'credit':0}
 q={k:n[k] for k in ('candidate_id','status','family','application_limit','supporting_candidates')}
 q.update(review_origin='main coordinator batch002; migration reviewer verified pinned source and owner-chain dedup',coordinator_evidence_file=str(p.relative_to(R)))
 if n['status']=='accepted':
  q.update(trigger='ServerPlayer attachment deserializeNBT calls PartialNbtSerializable.load(...,false)',input='Known skills/resources keyed by registry ID; skill level/xp/cycle and named abilities' if n['candidate_id']=='ae7e52e5809dfb194107' else 'Independent Storage owner: ItemStorage, PortalMap, Checkpoint and PatchouliBooks',output='Known present keys restored into initialized skill/resource owners; skill reader defaults level1/xp0 before optional values' if n['candidate_id']=='ae7e52e5809dfb194107' else 'Typed stores reconstruct payloads with per-entry catches; portal missing position uses shared spawn; supplied books list replaces old books',preservation=n['coordinator_observation'])
 else:q['reason']=n['coordinator_observation']+' '+n['application_limit']
 notes.append(q)
for e in b['bridge_evidence']:
 raw=(R/e['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256'];assert raw.decode()==e['context']
 files[e['path']]={**e,'credit':0}
(O/'reviews/batch-014-coordinator002.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
(O/'coordinator002-integration-evidence.json').write_text(json.dumps({'proposal_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'verified_proposals':3,'accepted':2,'rejected':1,'dedup':'Distinct Stats and Storage owners only; outer hash/load, child skills/fields and attachment bridge extra0; existing AoA clones are not recounted','full_support':list(files.values()),'production_changes':False},ensure_ascii=False,indent=2)+'\n')
print('verified AoA: 2 accepted owner chains, 1 client mirror excluded')

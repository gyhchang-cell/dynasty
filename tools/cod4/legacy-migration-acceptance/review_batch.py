"""Persist manually authored semantic reviews and full supporting sources. No auto acceptance."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3]; O=R/'docs/cod4/audit-20261022/legacy-migration-acceptance'
def record(number,rows,extra_files=()):
 index={r['candidate_id']:r for r in map(json.loads,(O/'candidates.jsonl').read_text().splitlines())}
 old={r['candidate_id'] for p in (O/'reviews').glob('*.json') if p.name!=f'batch-{number:03d}.json' for r in json.loads(p.read_text())}
 assert not old.intersection(r['candidate_id'] for r in rows),'previously reviewed candidate'
 files={index[i]['private_file'] for r in rows for i in [r['candidate_id']]+r.get('supporting_candidates',[])}|set(extra_files)
 context=[]
 for f in sorted(files):
  raw=(R/f).read_bytes();context.append(dict(path=f,file_sha256=hashlib.sha256(raw).hexdigest(),full_source=raw.decode(),credit=0))
 (O/f'support-contexts-batch{number:03d}.json').write_text(json.dumps(context,ensure_ascii=False,indent=2)+'\n')
 (O/f'reviews/batch-{number:03d}.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 print(f'batch{number}: authored {len(rows)} decisions; full sources{len(context)}; support credit0')
def accepted(i,f,t,inp,out,p,l,s=()):
 return dict(candidate_id=i,status='accepted',family=f,trigger=t,input=inp,output=out,preservation=p,application_limit=l,supporting_candidates=list(s))

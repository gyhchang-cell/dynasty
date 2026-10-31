"""Pinned supplemental acquisition, zero credit, no retries; retain verified successes on error."""
from pathlib import Path
import json,hashlib,subprocess,sys,datetime
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/immune-feedback-research'
repo=sys.argv[1];root=B/'sources'/repo.replace('/','__');meta=json.loads((root/'source.json').read_text());tree=json.loads((root/'tree.json').read_text());by={x['path']:x for x in tree['tree']};saved={x['path']:x for x in meta['files']};completed=[]
def persist():
 meta['files']=list(saved.values());(root/'source.json').write_text(json.dumps(meta,indent=2)+'\n');p=O/'sources.json';sources=json.loads(p.read_text());sources=[meta if x['repo']==repo else x for x in sources];p.write_text(json.dumps(sources,indent=2)+'\n')
for rel in sys.argv[2:]:
 try:
  x=by[rel];assert x['type']=='blob';dest=root/rel
  data=dest.read_bytes() if dest.exists() else subprocess.run(['curl','-fLsS','--max-time','25','--retry','0',f'https://raw.githubusercontent.com/{repo}/{meta["commit"]}/{rel}'],capture_output=True,check=True).stdout
  assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==x['sha']
  data.decode('utf-8');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);saved[rel]={'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':x['sha']};completed.append(rel);persist()
 except Exception as exc:
  persist();error={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repo':repo,'commit':meta['commit'],'failed_path':rel,'verified_retained':completed,'error':str(exc),'stderr':getattr(exc,'stderr',b'').decode('utf-8',errors='replace'),'retry_performed':False,'research_credit':0}
  with (O/'acquisition-errors.jsonl').open('a') as f:f.write(json.dumps(error,ensure_ascii=False)+'\n')
  print(json.dumps(error,ensure_ascii=False));sys.exit(1)
print(json.dumps({'repo':repo,'pinned':meta['commit'],'supplemental_files':len(completed),'credit':0}))

"""Acquire exact supplemental text/blob files at an already pinned revision; zero research credit."""
from pathlib import Path
import json,hashlib,subprocess,sys
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/immune-feedback-research'
repo=sys.argv[1];root=B/'sources'/repo.replace('/','__');meta=json.loads((root/'source.json').read_text());tree=json.loads((root/'tree.json').read_text());by={x['path']:x for x in tree['tree']};saved={x['path']:x for x in meta['files']}
for rel in sys.argv[2:]:
 x=by[rel];assert x['type']=='blob';dest=root/rel
 data=dest.read_bytes() if dest.exists() else subprocess.run(['curl','-fLsS','--max-time','25','--retry','1',f'https://raw.githubusercontent.com/{repo}/{meta["commit"]}/{rel}'],capture_output=True,check=True).stdout
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==x['sha']
 data.decode('utf-8');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);saved[rel]={'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':x['sha']}
meta['files']=list(saved.values());(root/'source.json').write_text(json.dumps(meta,indent=2)+'\n');p=O/'sources.json';all=json.loads(p.read_text());all=[meta if x['repo']==repo else x for x in all];p.write_text(json.dumps(all,indent=2)+'\n');print(json.dumps({'repo':repo,'pinned':meta['commit'],'supplemental_files':len(sys.argv)-2,'credit':0}))

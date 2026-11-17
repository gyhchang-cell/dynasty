"""Acquire fixed metadata once, no retry and no credit. Never execute upstream code."""
from ledger import B,O
import json,subprocess,datetime,hashlib
repo='TelepathicGrunt/Bumblezone';root=B/'sources/TelepathicGrunt__Bumblezone';root.mkdir(exist_ok=True)
def get(url):return subprocess.run(['curl','-fLsS','--max-time','25','--retry','0',url],check=True,capture_output=True).stdout
try:
 if (root/'source.json').exists():
  print('Already fixed; do not refresh source revision.');raise SystemExit
 rev=json.loads(get('https://api.github.com/repos/'+repo+'/commits/HEAD'))['sha'];(root/'commit.json').write_text(json.dumps({'repo':repo,'commit':rev,'research_credit':0})+'\n')
 data=get(f'https://api.github.com/repos/{repo}/git/trees/{rev}?recursive=1');tree=json.loads(data);assert tree['sha']==rev and not tree.get('truncated');(root/'tree.json').write_bytes(data)
 meta={'repo':repo,'commit':rev,'acquisition':'fixed git tree only, no candidate or research credit','tree_sha256':hashlib.sha256(data).hexdigest(),'files':[],'research_credit':0,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(root/'source.json').write_text(json.dumps(meta,indent=2)+'\n')
 f=O/'sources.json';old=json.loads(f.read_text());assert not any(x['repo']==repo for x in old);old.append(meta);f.write_text(json.dumps(old,indent=2)+'\n');print(json.dumps({'repo':repo,'commit':rev,'tree_entries':len(tree['tree']),'credit':0}))
except Exception as e:
 error={'repo':repo,'error':str(e),'stderr':getattr(e,'stderr',b'').decode(errors='replace'),'retry_performed':False,'research_credit':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (root/'acquisition-failed.json').write_text(json.dumps(error,indent=2)+'\n');print(json.dumps(error));raise SystemExit(1)

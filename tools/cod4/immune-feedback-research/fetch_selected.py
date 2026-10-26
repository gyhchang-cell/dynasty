"""Fetch pinned Git tree plus selected complete source files, without asset archives."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,hashlib,sys,datetime,re
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/immune-feedback-research'
def get(url):return subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','25','--retry','1',url],capture_output=True,check=True).stdout
def run(repo,pattern):
 root=B/'sources'/repo.replace('/','__');root.mkdir(exist_ok=True)
 cached=R/'build/item-use-references'/repo.replace('/','__')
 if (cached/'source.json').exists():
  rev=json.loads((cached/'source.json').read_text())['sha'];tb=(cached/'tree.json').read_bytes()
 else:
  rev=json.loads(get(f'https://api.github.com/repos/{repo}/commits/HEAD'))['sha'];tb=get(f'https://api.github.com/repos/{repo}/git/trees/{rev}?recursive=1')
 tree=json.loads(tb);assert tree['sha']==rev and not tree.get('truncated');(root/'tree.json').write_bytes(tb)
 selected=[x for x in tree['tree'] if x['type']=='blob' and x['path'].endswith('.java') and re.search(pattern,x['path'])]
 def one(x):
  dest=root/x['path']
  if dest.exists():content=dest.read_bytes()
  else:content=get(f'https://raw.githubusercontent.com/{repo}/{rev}/{x["path"]}')
  assert hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()==x['sha']
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(content)
  return {'path':x['path'],'sha256':hashlib.sha256(content).hexdigest(),'git_blob_sha1':x['sha']}
 saved=[];errors=[]
 with ThreadPoolExecutor(max_workers=6) as pool:
  fs=[(x,pool.submit(one,x)) for x in selected]
  for x,f in fs:
   try:saved.append(f.result())
   except Exception as e:errors.append({'path':x['path'],'error':str(e)})
 data={'repo':repo,'commit':rev,'acquisition':'pinned git tree + complete selected Java; each Git blob verified','tree_sha256':hashlib.sha256(tb).hexdigest(),'selection':pattern,'files':saved,'errors':errors,'research_credit':0,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(root/'source.json').write_text(json.dumps(data,indent=2)+'\n')
 p=O/'sources.json';old=json.loads(p.read_text());by={x['repo']:x for x in old};by[repo]=data;p.write_text(json.dumps(list(by.values()),indent=2)+'\n');print(json.dumps({'repo':repo,'commit':rev,'files':len(saved),'errors':len(errors),'research_credit':0}),flush=True)
run(sys.argv[1],sys.argv[2])

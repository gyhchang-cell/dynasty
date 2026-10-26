"""Acquire immutable upstream source text only. Downloading gives no research credit."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,zipfile,io,hashlib,datetime,sys
B=Path(__file__).resolve().parent; R=B.parents[2]; O=R/'docs/cod4/audit-20261022/immune-feedback-research'; W=B/'sources';W.mkdir(exist_ok=True)
def get(url):
 return subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','50','--retry','1',url],capture_output=True,check=True).stdout
def fetch(repo):
 dest=W/repo.replace('/','__');meta=dest/'source.json'
 if meta.exists():return json.loads(meta.read_text())
 try:
  rev=json.loads(get('https://api.github.com/repos/'+repo+'/commits/HEAD'))['sha']
  url='https://codeload.github.com/'+repo+'/zip/'+rev;data=get(url);z=zipfile.ZipFile(io.BytesIO(data));saved=[]
  for m in z.infolist():
   parts=Path(m.filename).parts[1:]
   if m.is_dir() or not parts or '..' in parts:continue
   rel=Path(*parts)
   if rel.suffix not in {'.java','.kt','.json','.toml','.properties','.gradle'} and not rel.name.lower().startswith(('license','copying')):continue
   if len(parts)>1 and any(x in {'node_modules','.gradle','build'} for x in parts):continue
   content=z.read(m);p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
   saved.append({'path':str(rel),'sha256':hashlib.sha256(content).hexdigest()})
  d={'repo':repo,'commit':rev,'archive_url':url,'archive_sha256':hashlib.sha256(data).hexdigest(),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':saved,'research_credit':0,'upstream_code_executed':False}
  meta.write_text(json.dumps(d,indent=2)+'\n');return d
 except Exception as e:return {'repo':repo,'error':str(e),'research_credit':0}
with ThreadPoolExecutor(max_workers=4) as pool:result=list(pool.map(fetch,sys.argv[1:]))
p=O/'sources.json';old=json.loads(p.read_text()) if p.exists() else [];by={x['repo']:x for x in old};by.update({x['repo']:x for x in result});p.write_text(json.dumps(list(by.values()),indent=2)+'\n')
for d in result:print(json.dumps({k:v for k,v in d.items() if k not in {'files'}},ensure_ascii=False),flush=True)

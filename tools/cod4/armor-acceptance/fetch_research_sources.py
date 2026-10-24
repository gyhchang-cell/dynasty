"""Fetch pinned upstream Java sources into private research cache, without executing upstream code."""
from pathlib import Path
import subprocess,json,hashlib,datetime,io,zipfile,concurrent.futures,sys
B=Path(__file__).resolve().parent;R=B.parents[2];dest=B/'.work/research-sources';dest.mkdir(parents=True,exist_ok=True)
repos=sys.argv[1:] or ['ochotonida/artifacts','Octo-Studios/relics','TheIllusiveC4/Curios','wisp-forest/accessories','SlimeKnights/TinkersConstruct']
def get(url):return subprocess.run(['curl','--fail','--location','--silent','--show-error','--max-time','60','--retry','1',url],capture_output=True,check=True).stdout
def one(repo):
 folder=dest/repo.replace('/','__')
 try:
  if (folder/'source.json').exists():return json.loads((folder/'source.json').read_text())
  previous=R/'build/item-use-references'/repo.replace('/','__')/'source.json'
  rev=json.loads(previous.read_text())['sha'] if previous.exists() else json.loads(get(f'https://api.github.com/repos/{repo}/commits/HEAD'))['sha']
  cached_tree=previous.parent/'tree.json'
  treebytes=cached_tree.read_bytes() if cached_tree.exists() else get(f'https://api.github.com/repos/{repo}/git/trees/{rev}?recursive=1');tree=json.loads(treebytes);assert not tree.get('truncated');assert tree['sha']==rev
  zipurl=f'https://codeload.github.com/{repo}/zip/{rev}';data=get(zipurl);z=zipfile.ZipFile(io.BytesIO(data));blobs={x['path']:x['sha'] for x in tree['tree'] if x['type']=='blob'};count=0
  for member in z.infolist():
   parts=Path(member.filename).parts[1:]
   if not parts or '..' in parts:continue
   rel=Path(*parts)
   if member.is_dir() or not (rel.suffix=='.java' or (len(parts)==1 and rel.name.lower().startswith(('license','copying')))):continue
   content=z.read(member);blob=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest();assert blobs[str(rel)]==blob, f'Git blob mismatch: {repo}:{rel}: expected {blobs[str(rel)]}, archive {blob}'
   out=folder/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(content);count+=1
  (folder/'tree.json').write_bytes(treebytes);meta={'repo':repo,'sha':rev,'url':f'https://github.com/{repo}/tree/{rev}','download_url':zipurl,'archive_sha256':hashlib.sha256(data).hexdigest(),'retrieved_at':datetime.datetime.now().astimezone().isoformat(),'files_saved':count,'scope':'Java plus license only; no upstream code executed; Git blob SHA1 verified against pinned tree'};(folder/'source.json').write_text(json.dumps(meta,indent=2)+'\n');return meta
 except Exception as e:return {'repo':repo,'status':'error','error_type':type(e).__name__,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,repos))
receipt=B/'evidence/expanded-source-downloads.json';old=json.loads(receipt.read_text()) if receipt.exists() else []
attempts=B/'evidence/source-download-attempts.json';history=json.loads(attempts.read_text()) if attempts.exists() else [{'previous_receipt':old}]
history.append({'at':datetime.datetime.now().astimezone().isoformat(),'results':results});attempts.write_text(json.dumps(history,indent=2)+'\n')
merged={v['repo']:v for v in old};merged.update({v['repo']:v for v in results})
receipt.write_text(json.dumps(list(merged.values()),indent=2)+'\n');print(json.dumps(results,indent=2))

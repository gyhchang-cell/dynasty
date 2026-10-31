"""Verify evidence-only manual chains. No gameplay count or review inference."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse,datetime,hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/sweep-receipt-research'
p=argparse.ArgumentParser();p.add_argument('chain');a=p.parse_args();f=R/a.chain;assert f.parent==O
h=lambda b:hashlib.sha256(b).hexdigest();data=json.loads(f.read_text());sources={};errors=[]
for chain in data['chains']:
 assert chain['additional_credit']==0
 for n in chain['nodes']:
  path=R/n['source_local'];raw=path.read_bytes();assert h(raw)==n['source_sha256'];code=n['excerpt'];assert h(code.encode())==n['snippet_sha256']
  # Byte hashes above remain exact; line-range comparison treats CRLF and LF alike.
  actual='\n'.join(raw.decode().splitlines()[n['line']-1:n['end_line']])
  assert actual.strip()=='\n'.join(code.splitlines()).strip(),(n['path'],n['method'])
  key=f"{n['repo']}@{n['revision']}:{n['path']}";sources[key]=n
cachepath=O/'chain-source-pins.json';cache=json.loads(cachepath.read_text()) if cachepath.exists() else {}
known=json.loads((O/'remote-pins.json').read_text())
def check(pair):
 key,n=pair;path=R/n['source_local'];raw=path.read_bytes();root=path.parents[len(Path(n['path']).parts)-1];assert root/n['path']==path;tree=root/'tree.json'
 if tree.exists():
  t=json.loads(tree.read_text())
  if t['sha']!=n['revision']:
   commit=json.loads((root/'commit.json').read_text());assert commit['sha']==n['revision'] and commit['commit']['tree']['sha']==t['sha'], 'Tree must be bound to exact commit'
  blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert any(x['path']==n['path'] and x['sha']==blob for x in t['tree']);return key,dict(matches=True,kind='pinned_tree_blob',retrieved_sha256=h(raw),tree=str(tree.relative_to(R)),tree_sha256=h(tree.read_bytes()),blob_sha1=blob)
 for c in (cache,known):
  if c.get(key,{}).get('matches') and c[key].get('retrieved_sha256')==n['source_sha256']:return key,c[key]
 url=f"https://raw.githubusercontent.com/{n['repo']}/{n['revision']}/{n['path']}";q=subprocess.run(['curl','--fail','--silent','--show-error','--location','--max-time','25',url],capture_output=True)
 return key,dict(url=url,matches=q.returncode==0 and h(q.stdout)==n['source_sha256'],expected_sha256=n['source_sha256'],retrieved_sha256=h(q.stdout),exit_code=q.returncode,retrieved_at=datetime.datetime.now().astimezone().isoformat())
with ThreadPoolExecutor(max_workers=6) as pool:
 for key,result in pool.map(check,sources.items()):
  cache[key]=result
  if not result['matches']:errors.append(key)
cachepath.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n')
out=dict(chain=a.chain,chain_sha256=h(f.read_bytes()),full_method_nodes=sum(len(c['nodes']) for c in data['chains']),unique_sources=len(sources),errors=errors,additional_credit=0,line_range_comparison='splitlines normalized LF, outer strip; source and excerpt SHA256 remain byte-exact',checked_at=datetime.datetime.now().astimezone().isoformat())
outpath=O/(f.stem+'-verification.json');outpath.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False));assert not errors

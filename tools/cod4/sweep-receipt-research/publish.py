"""Verify authored judgments and fixed source bytes, then publish a separate ledger."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,collections,re,subprocess,datetime,argparse
B=Path(__file__).resolve().parent;R=B.parents[2];O=R/'docs/cod4/audit-20261022/sweep-receipt-research'
ap=argparse.ArgumentParser();ap.add_argument('--verify-remote',action='store_true');a=ap.parse_args()
sha=lambda b:hashlib.sha256(b).hexdigest()
cs=[json.loads(x) for x in (O/'candidates.jsonl').read_text().splitlines()];by={c['candidate_id']:c for c in cs}
notes=[r for p in sorted((O/'reviews').glob('*.json')) for r in json.loads(p.read_text())]
seen=set();structs=set();ranges=collections.defaultdict(list);rows=[];trees={};needed={}
remote_path=O/'remote-pins.json';remote=json.loads(remote_path.read_text()) if remote_path.exists() else {}
old=R/'tools/cod4/armor-acceptance/evidence/armor-remote-pin-verification.json'
existing=json.loads(old.read_text()) if old.exists() else {}
for n in notes:
 c=by[n['candidate_id']];assert c['candidate_id'] not in seen;seen.add(c['candidate_id'])
 assert n['snippet_sha256']==c['snippet_sha256'];assert n['decision'] in ('accepted','excluded','pending')
 row={**c,**n,'credit':int(n['decision']=='accepted'),'external_runtime_tested':False}
 if n['decision']=='accepted':
  raw=(R/c['source_local']).read_bytes();assert sha(raw)==c['source_sha256']
  excerpt=c['excerpt'];assert sha(excerpt.encode())==c['snippet_sha256'];text=raw.decode(errors='replace');start=text.find(excerpt);assert start>=0
  assert text[:start].count('\n')+1==c['line'];assert text[:start+len(excerpt)].count('\n')+1==c['end_line']
  assert not c['parse_error'];assert c['structural_fingerprint'] not in structs,('same AST clone family',c['candidate_index'] if 'candidate_index' in c else n['candidate_index'])
  structs.add(c['structural_fingerprint']);filekey=(c['repo'],c['revision'],c['path'])
  for lo,hi in ranges[filekey]:assert c['end_line']<lo or c['line']>hi,('overlap',c['candidate_id'])
  ranges[filekey].append((c['line'],c['end_line']))
  root=R/c['source_root'];treefile=root/'tree.json';key=f"{c['repo']}@{c['revision']}:{c['path']}"
  if treefile.exists():
   if root not in trees:
    t=json.loads(treefile.read_text());assert t['sha']==c['revision'];trees[root]={v['path']:v['sha'] for v in t['tree'] if v['type']=='blob'}
   blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert trees[root][c['path']]==blob
   row['pin_verification']={'kind':'pinned_tree_blob','tree':str(treefile.relative_to(R)),'tree_sha256':sha(treefile.read_bytes()),'blob_sha1':blob}
  else:
   needed[key]=c
   if existing.get(key,{}).get('matches') and existing[key].get('retrieved_sha256')==c['source_sha256']:remote[key]=existing[key]
   row['pin_verification']={'kind':'raw_commit_bytes','receipt':key}
 rows.append(row)
def fetch(item):
 key,c=item;url=f"https://raw.githubusercontent.com/{c['repo']}/{c['revision']}/{c['path']}"
 r=subprocess.run(['curl','--fail','--location','--silent','--show-error','--max-time','25','--retry','1',url],capture_output=True)
 actual=sha(r.stdout);return key,dict(url=url,expected_sha256=c['source_sha256'],retrieved_sha256=actual,matches=r.returncode==0 and actual==c['source_sha256'],exit_code=r.returncode,retrieved_at=datetime.datetime.now().astimezone().isoformat())
if a.verify_remote:
 with ThreadPoolExecutor(max_workers=6) as pool:
  for k,v in pool.map(fetch,[(k,c) for k,c in needed.items() if not (remote.get(k,{}).get('matches') and remote[k].get('retrieved_sha256')==c['source_sha256'])]):remote[k]=v
 remote_path.write_text(json.dumps(remote,ensure_ascii=False,indent=2)+'\n')
for k,c in needed.items():assert remote.get(k,{}).get('matches') and remote[k].get('retrieved_sha256')==c['source_sha256'],('unverified pin',k)
accepted=[r for r in rows if r['credit']];count=len(accepted)
(O/'reviewed.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
(O/'accepted.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in accepted))
summary={'required':1000,'accepted':count,'gap':max(0,1000-count),'gate_met':count>=1000,'candidates':len(cs),'decisions':dict(collections.Counter(r['decision'] for r in rows)),'unreviewed':len(cs)-len(rows),'repositories':len({c['repo'] for c in accepted}),'pinned_files':len(ranges),'prior_corpus_credit':0,'accepted_ledger_sha256':sha((O/'accepted.jsonl').read_bytes()),'production_changed':False,'upstream_code_executed':False,'candidate_count_is_not_review_count':True,'updated_at':datetime.datetime.now().astimezone().isoformat()}
(O/'progress.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))

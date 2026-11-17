"""Import read-only fixed helper cache with pinned-tree verification; credit remains zero."""
from ledger import B,R,O
import json,sys,hashlib,subprocess,datetime
repo=sys.argv[1];manifest=R/'docs/cod4/audit-20261022/sweep-receipt-research/helpers/combat-spectrum/source-manifest.json';prior=next(x for x in json.loads(manifest.read_text()) if x['repo']==repo);rev=prior['revision'];assert rev==prior['commit_sha_confirmed'];src=R/prior['source_root'];dst=B/'sources'/repo.replace('/','__');dst.mkdir(exist_ok=True);tp=dst/'tree.json'
if not tp.exists():
 attempt=dst/'tree-request-attempt.json';assert not attempt.exists(),'No repeat after an earlier external attempt'
 attempt.write_text(json.dumps({'commit':rev,'retry':False}))
 res=subprocess.run(['curl','-fLsS','--retry','0','--max-time','25',f'https://api.github.com/repos/{repo}/git/trees/{rev}?recursive=1'],capture_output=True)
 if res.returncode:
  (dst/'tree-request-failed.json').write_text(json.dumps({'code':res.returncode,'stderr':res.stderr.decode(errors='replace'),'partial_bytes':len(res.stdout),'retry':False}));(dst/'tree-partial.bin').write_bytes(res.stdout);raise SystemExit('fixed tree unavailable; retained, no retry')
 tree=json.loads(res.stdout);assert tree['sha']==rev and not tree.get('truncated');tp.write_bytes(res.stdout)
tree=json.loads(tp.read_text());assert tree['sha']==rev and not tree.get('truncated');by={x['path']:x for x in tree['tree']};files=[]
for x in prior['files']:
 rel=x['path'];p=src/rel
 if not p.suffix=='.java':continue
 data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==x['sha256'];blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert by[rel]['sha']==blob
 out=dst/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data);files.append({'path':rel,'sha256':x['sha256'],'git_blob_sha1':blob})
meta={'repo':repo,'commit':rev,'acquisition':'read-only existing fixed helper cache, SHA256 and fixed Git tree blob verified independently; old/helper credits not transferred','research_credit':0,'files':files};(dst/'source.json').write_text(json.dumps(meta,indent=2)+'\n');p=O/'sources.json';rows=json.loads(p.read_text());assert repo not in [x['repo'] for x in rows];rows.append(meta);p.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'repo':repo,'verified_cached_files':len(files),'credit':0}))

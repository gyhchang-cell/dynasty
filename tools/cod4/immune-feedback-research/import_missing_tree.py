"""Recover one missing fixed Git tree; never follow HEAD, retry, or credit downloads."""
from ledger import B,O,R
from pathlib import Path
import json,subprocess,datetime,sys,hashlib
repo=sys.argv[1];src=R/'build/item-use-references'/repo.replace('/','__');root=B/'sources'/repo.replace('/','__');root.mkdir(exist_ok=True);meta=json.loads((src/'source.json').read_text());rev=meta['sha'];out=root/'tree.json'
assert not out.exists(), 'Existing tree must be reused, never refetched.'
try:
 raw=subprocess.run(['curl','-fLsS','--retry','0','--max-time','25',f'https://api.github.com/repos/{repo}/git/trees/{rev}?recursive=1'],capture_output=True,check=True).stdout
 tree=json.loads(raw);assert tree['sha']==rev and not tree.get('truncated');assert isinstance(tree['tree'],list)
 out.write_bytes(raw);print(json.dumps({'repo':repo,'commit':rev,'entries':len(tree['tree']),'tree_sha256':hashlib.sha256(raw).hexdigest(),'credit':0}))
except Exception as exc:
 error={'repo':repo,'commit':rev,'error':str(exc),'stderr':getattr(exc,'stderr',b'').decode(errors='replace'),'retry_performed':False,'research_credit':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (O/'acquisition-errors.jsonl').open('a') as f:f.write(json.dumps(error)+'\n')
 print(json.dumps(error));raise SystemExit(1)

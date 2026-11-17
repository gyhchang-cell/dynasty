"""Fixed local 1.20.1 branch; preserve metadata-only main tree, never count it."""
from ledger import B,R,O
import json,subprocess,hashlib,datetime
repo='Fuzss/illager-invasion';root=B/'sources'/repo.replace('/','__');src=R/'build/bestiary-v43/references/Fuzss__illager-invasion__1.20.1';prior=json.loads((src/'source.json').read_text());rev=prior['sha'];dest=root/'tree.json'
assert not (root/'source.json').exists()
old=json.loads(dest.read_text());assert old['sha']=='f012bd94c9ef25b2963b2262df85203fec764da3'
archive=root/'main-metadata-only-tree.json';assert not archive.exists();dest.rename(archive)
try:
 raw=subprocess.run(['curl','-fLsS','--retry','0','--max-time','25',f'https://api.github.com/repos/{repo}/git/trees/{rev}?recursive=1'],capture_output=True,check=True).stdout
 tree=json.loads(raw);assert tree['sha']==rev and not tree.get('truncated');dest.write_bytes(raw)
 print(json.dumps({'repo':repo,'commit':rev,'entries':len(tree['tree']),'metadata_only_main_credit':0,'acquisition_credit':0}))
except Exception as exc:
 error={'repo':repo,'commit':rev,'error':str(exc),'retry_performed':False,'research_credit':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 with (O/'acquisition-errors.jsonl').open('a') as f:f.write(json.dumps(error)+'\n')
 print(json.dumps(error));raise SystemExit(1)

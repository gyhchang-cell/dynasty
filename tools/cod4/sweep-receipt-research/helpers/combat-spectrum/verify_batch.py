"""Independent read-only validation of downloaded text and authored evidence JSON."""
from pathlib import Path
import json,hashlib,collections
root=Path(__file__).resolve().parents[5]
doc=root/'docs/cod4/audit-20261022/sweep-receipt-research/helpers/combat-spectrum'
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((doc/'source-manifest.json').read_text())
allowed={'ZsoltMolnarrr/BetterCombat','DaFuqs/Spectrum'}
assert {m['repo'] for m in manifest}==allowed
files_checked=0
for m in manifest:
 assert m['revision']==m['commit_sha_confirmed'] and len(m['revision'])==40 and not m['fork']
 for f in m['files']:
  raw=(root/m['source_root']/f['path']).read_bytes()
  assert sha(raw)==f['sha256'],f['path']
  files_checked+=1
rows=[]
for name in ['batch-001.json','reviewed-zero-credit.json']:
 rows+=json.loads((doc/name).read_text())['records']
contexts=json.loads((doc/'evidence-contexts.json').read_text())['evidence']
required='repo revision path source_local source_sha256 line end_line excerpt observation application limits url'.split()
for r in rows:
 assert all(k in r for k in required),r['candidate_id']
 assert r['credit']==r['master_credit']==0
 assert all(k in contexts for k in r['support_evidence'])
for r in rows+list(contexts.values()):
 assert r['repo'] in allowed
 p=root/r['source_local']; raw=p.read_bytes(); lines=raw.decode().splitlines(keepends=True)
 assert sha(raw)==r['source_sha256']
 assert ''.join(lines[r['line']-1:r['end_line']])==r['excerpt']
 assert sha(r['excerpt'].encode())==r['snippet_sha256']
 assert r['url']==f"https://github.com/{r['repo']}/blob/{r['revision']}/{r['path']}#L{r['line']}-L{r['end_line']}"
 if r.get('scope')=='complete_method':
  assert r['excerpt'].strip().endswith('}') and '(' in r['excerpt'].splitlines()[0]
 c=r.get('preceding_context')
 if c: assert ''.join(lines[c['line']-1:c['end_line']])==c['excerpt']
eligible=[r for r in rows if r['proposed_credit']]
assert len({r['independent_chain_key'] for r in eligible})==len(eligible)
assert len({(r['repo'],r['path'],r['line'],r['end_line']) for r in eligible})==len(eligible)
assert len({r['candidate_id'] for r in rows})==len(rows)
print(json.dumps(dict(pinned_files_verified=files_checked,review_records=len(rows),proposed_eligible=len(eligible),zero_credit=len(rows)-len(eligible),support_excerpts=len(contexts),proposed_by_repo=dict(collections.Counter(r['repo'] for r in eligible)),gap_to_80=80-len(eligible),master_credit_added=0,checks='PASS'),ensure_ascii=False))

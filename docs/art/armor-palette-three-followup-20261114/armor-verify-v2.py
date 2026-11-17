from pathlib import Path
import json,hashlib,zipfile,sys
r=Path.cwd();b=Path(sys.argv[1]).resolve();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();d=json.load(open(b/'coordinator-delivery.json'));assert H(Path(d['receipt']))==d['receipt_sha256'];rec=json.load(open(d['receipt']));assert rec['file_count']==len(rec['files']);assert all(H(b/f)==h for f,h in rec['files'].items());p=json.load(open(b/'provenance.json'));assert H(Path(p['archive']))==p['archive_sha256'];z=zipfile.ZipFile(p['archive'])
for e in p['entries']:
 assert hashlib.sha256(z.read(e['entry'])).hexdigest()==H(b/e['local'])==e['sha256']
 if 'python_decode' in e:assert H(b/e['python_decode'])==e['decode_sha256']
for e in json.load(open(b/'historic-family-dedup.json'))['historic_original_comparisons']:assert H(Path(e['old']))==H(b/e['current'])==e['sha256']
for e in json.load(open(b/'historic-family-dedup.json')).get('historic_version_differences',[]):
 assert H(Path(e['old']))==e['old_sha256'];assert H(b/e['current'])==e['current_sha256'];assert e['old_sha256']!=e['current_sha256']
for k,n in [('protected',289),('priority',70)]:
 a=json.load(open(b/(k+'-before.json')));assert a==json.load(open(b/(k+'-after.json')));assert len(a)==n;assert all(H(r/f)==h for f,h in a.items())
l=json.load(open(b/'combined-semantic-ledger.json'));prior=l['current_batch_prior'];assert H(Path(prior['path']))==prior['sha256'];old=json.load(open(prior['path']));assert set(l['case_scope_followups'])-set(old['case_scope_followups'])=={p['case']}
for k in old:
 if k not in ['case_scope_followups','current_batch_prior']:assert l[k]==old[k]
for k in old['case_scope_followups']:assert l['case_scope_followups'][k]==old['case_scope_followups'][k]
pp=json.load(open(r/'docs/art/armor-continuation-20261102/progress.json'));assert any(v=={'path':str(b/'coordinator-delivery.json'),'sha256':H(b/'coordinator-delivery.json')} for v in pp.values() if isinstance(v,dict));print('PASS',d['batch'],rec['file_count'],'files',len(p['entries']),'source entries; prior credit preserved,289+70 unchanged')

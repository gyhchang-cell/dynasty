from pathlib import Path
import json,hashlib,re,datetime
B=Path(__file__).resolve().parent;m=json.loads((B/'selected-source-manifest.json').read_text());j=json.loads((B/'ballista-study.json').read_text());checks=[]
def check(n,v):
 checks.append(dict(name=n,ok=bool(v)))
 if not v:raise AssertionError(n)
check('fixed archive hash',hashlib.sha256((B/m['archive']).read_bytes()).hexdigest()==m['archive_sha256'])
by={}
for x in m['files']:
 p=B/x['local'];check('file hash '+x['path'],hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);by[x['path']]=x
 if x['ranges']:
  n=len(p.read_text().splitlines())
  for lo,hi in x['ranges']:check('read range '+x['path'],1<=lo<=hi<=n)
for e in j['evidence']:
 check(e['id']+' limit/credit',bool(e['limit']) and e['credit_added']==0)
 for r in e['sources']:
  x=by[r['path']];lo,hi=r['range'];check(e['id']+' hash/range',r['sha256']==x['sha256'] and any(u<=lo<=hi<=v for u,v in x['ranges']))
g=json.loads((B/'geometry-inspection.json').read_text());check('atlas declaration matches',g['declared_texture']==g['actual_texture']==[128,128])
check('not accepted/runtime',j['accepted_credit']==j['creature_reference_credit']==0 and not j['production_changed'] and not j['java_game_started'])
for link in re.findall(r'(?:src|href)="([^"]+)"',(B/'index.html').read_text()):
 if not link.startswith('http') and link!='local-verification.json':check('report '+link,(B/link).is_file())
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),results=checks,scope='source/asset hash and ranges,model declaration,report path only; not build/game/dependency closure or accepted references',saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))

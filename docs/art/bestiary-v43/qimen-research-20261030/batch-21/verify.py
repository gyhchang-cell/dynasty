from pathlib import Path
import json,hashlib,re,datetime
B=Path(__file__).resolve().parent;j=json.loads((B/'grapple-core-study.json').read_text());m=json.loads((B/'selected-source-manifest.json').read_text());checks=[]
def check(name,v):
 checks.append(dict(name=name,ok=bool(v)))
 if not v:raise AssertionError(name)
check('fixed archive hash',hashlib.sha256((B/m['archive']).read_bytes()).hexdigest()==m['archive_sha256'])
S={}
for x in j['sources']:
 p=B/x['local'];check(x['id']+' hash',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);S[x['id']]=x;n=len(p.read_text().splitlines())
 for lo,hi in x['ranges']:check(x['id']+f' range{lo}-{hi}',1<=lo<=hi<=n)
for x in j['evidence']:
 check(x['id']+' limit/credit',bool(x['limit']) and x['credit_added']==0)
 for a in x['sources']:
  check(x['id']+' source exists',a['source'] in S)
  for lo,hi in a['ranges']:check(x['id']+f' within read {lo}-{hi}',any(u<=lo<=hi<=v for u,v in S[a['source']]['ranges']))
check('truncation example half',int(.5)*4==0);check('truncation example full',int(1.)*4==4)
# Independent simple arithmetic trace of the observed post-increment cap check, not world execution.
count=66;destroyed=0
for _ in range(10):
 destroyed+=1;old=count;count+=1
 if old>67:break
check('postincrement can exceed cap',count==69 and destroyed==3)
check('not accepted/runtime',j['accepted_credit']==0 and j['creature_reference_credit']==0 and not j['production_changed'] and not j['java_game_started'])
for f in re.findall(r'(?:href|src)="([^"]+)"',(B/'index.html').read_text()):
 if not f.startswith('http') and f!='local-verification.json':check('report '+f,(B/f).is_file())
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),results=checks,scope='range/hash/report and offline arithmetic only; not merged Mixin,build or gameplay',saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))

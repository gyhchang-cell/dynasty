from pathlib import Path
import json,hashlib,re,datetime
B=Path(__file__).resolve().parent;m=json.loads((B/'selected-source-manifest.json').read_text());j=json.loads((B/'dependency-consumers.json').read_text());c=[]
def check(n,v):
 c.append(dict(name=n,ok=bool(v)))
 if not v:raise AssertionError(n)
p=B/m['archive'];check('source sha256',hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256']);check('published SHA1',hashlib.sha1(p.read_bytes()).hexdigest()==m['published_sha1']);check('POM hash',hashlib.sha256((B/'source-archives/geckolib-fabric-1.19-3.1.6.pom').read_bytes()).hexdigest()==m['pom_sha256'])
for x in m['files']:
 p=B/x['local'];check('hash '+x['path'],hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);n=len(p.read_text().splitlines())
 for lo,hi in x['ranges']:check('range '+x['path'],1<=lo<=hi<=n)
by={x['local']:x for x in m['files']}
for x in j['evidence']:
 check(x['id']+' limit/credit',bool(x['limit']) and x['credit_added']==0)
 for r in x['sources']:
  lo,hi=r['range'];z=by[r['local']];check(x['id']+' read range',r['sha256']==z['sha256'] and any(u<=lo<=hi<=v for u,v in z['ranges']))
d=json.loads((B/'fractional-box-uv-diagnostic.json').read_text());check('diagnostic source hash',hashlib.sha256((B/d['source']).read_bytes()).hexdigest()==d['source_sha256']);check('core gap retained',j['core_sources_unavailable'][0]['result']=='404, not retried')
for link in re.findall(r'href="([^"]+)"',(B/'index.html').read_text()):
 if not link.startswith('http') and link!='local-verification.json':check('report '+link,(B/link).is_file())
check('zero production/credit/runtime',j['accepted_credit']==j['creature_reference_credit']==j['new_source_studies']==0 and not j['production_changed'] and not j['java_game_started'])
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(c),results=c,scope='source/published hash,ranges,diagnostic input/report links; not core controller,build/game or reference acceptance',saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),ensure_ascii=False,indent=2)+'\n');print('PASS',len(c))

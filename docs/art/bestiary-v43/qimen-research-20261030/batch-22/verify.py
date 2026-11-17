from pathlib import Path
import json,hashlib,re,datetime
B=Path(__file__).resolve().parent;j=json.loads((B/'render-client-study.json').read_text());a=json.loads((B/'asset-inspection.json').read_text());checks=[]
def check(name,v):
 checks.append(dict(name=name,ok=bool(v)))
 if not v:raise AssertionError(name)
for x in j['sources']:
 p=B/x['local'];check(x['id']+' hash',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);n=len(p.read_text().splitlines())
 for lo,hi in x['ranges']:check(x['id']+' ranges',1<=lo<=hi<=n)
ids={x['id'] for x in j['sources']}
for x in j['evidence']:
 check(x['id']+' sources/limit',set(x['sources'])<=ids and bool(x['limit']) and x['credit_added']==0)
for x in a['textures']:check('PNG '+x['local'],hashlib.sha256((B/x['local']).read_bytes()).hexdigest()==x['sha256'])
check('resolved nondegenerate faces',not a['issues'])
for m in a['models']:
 for p in m['chain']:check('model path '+p,(B/p).is_file())
for p in j['visual']['actually_viewed']:check('viewed exists '+p,(B/p).is_file())
for link in re.findall(r'(?:src|href)="([^"]+)"',(B/'index.html').read_text()):
 if not link.startswith('http') and link!='local-verification.json':check('report '+link,(B/link).is_file())
check('same family / no asset edit',j['new_source_studies']==j['accepted_credit']==j['creature_reference_credit']==0 and not j['production_changed'] and not j['java_game_started'])
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),results=checks,scope='selected source/PNG hashes,range bounds,asset paths,report links only; no build/runtime/merged Mixin proof',saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))

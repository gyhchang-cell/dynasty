from pathlib import Path
from PIL import Image
import json,hashlib,math,re,datetime
B=Path(__file__).resolve().parent;j=json.loads((B/'hook-study.json').read_text());m=json.loads((B/'selected-source-manifest.json').read_text());checks=[]
def check(name,v):
 checks.append({'name':name,'ok':bool(v)})
 if not v:raise AssertionError(name)
check('fixed archive hash',hashlib.sha256((B/m['archive']).read_bytes()).hexdigest()==m['archive_sha256'])
S={}
for x in j['sources']:
 p=B/x['local'];check(x['id']+' hash',hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']);S[x['id']]=x
 if p.suffix!='.png':
  n=len(p.read_text().splitlines())
  for lo,hi in x['ranges']:check(x['id']+f' range{lo}-{hi}',1<=lo<=hi<=n)
for x in j['evidence']:
 check(x['id']+' boundary recorded',bool(x['limit']) and x['credit_added']==0)
 for a in x['sources']:
  check(x['id']+' source '+a['source'],a['source'] in S)
  for lo,hi in a['ranges']:check(x['id']+f' read range {lo}-{hi}',any(a<=lo<=hi<=b for a,b in S[a['source']]['ranges']))
for s in m['files']:
 p=B/s['local']
 if '/models/item/' in s['path']:
  model=json.loads(p.read_text())
  for val in model.get('textures',{}).values():
   ns,path=val.split(':',1);texture=p.parents[2]/'textures'/(path+'.png');check(s['path']+' real texture',texture.is_file())
for x in json.loads((B/'texture-inspection.json').read_text()):
 im=Image.open(B/x['path']);check(x['path']+' png dimensions',list(im.size)==x['size'])
check('distance not squared confusion',math.isclose(math.sqrt(2048),45.254833995939045))
check('length lower bound',max(2*.5-3,1.5)==1.5)
check('length long distance',max(30*.5-3,1.5)==12)
check('references not accepted',j['accepted_credit']==0 and j['creature_reference_credit']==0 and not j['production_changed'] and not j['java_game_started'])
check('one study max',j['source_studies']==1 and j['proposed_independent_units_max']==1)
for f in re.findall(r'(?:href|src)="([^"]+)"',(B/'index.html').read_text()):
 if not f.startswith('http') and f!='local-verification.json':check('report link '+f,(B/f).is_file())
(B/'local-verification.json').write_text(json.dumps(dict(status='PASS',checks=len(checks),results=checks,scope='file/range/hash/asset references and offline formula examples only; no compilation,game,network behavior verification',saved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),ensure_ascii=False,indent=2)+'\n');print('PASS',len(checks))

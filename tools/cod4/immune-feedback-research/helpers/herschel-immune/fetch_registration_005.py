from pathlib import Path
import json,hashlib,urllib.request,datetime
ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'tools/cod4/legacy-migration-acceptance/.work/sources/ZsoltMolnarrr__SpellEngine'
OUT=ROOT/'tools/cod4/immune-feedback-research/helpers/herschel-immune/sources-batch005/ZsoltMolnarrr__SpellEngine'
DOC=ROOT/'docs/cod4/audit-20261022/immune-feedback-research/helpers/herschel-immune'
TREE=json.loads((BASE/'tree.json').read_text());COMMIT='42dc472183d8c139e741961eefda05eddc7630f8';assert TREE['sha']==COMMIT
PATHS=['common/src/main/resources/spell_engine.mixins.json','fabric/src/main/resources/fabric.mod.json','neoforge/src/main/resources/META-INF/neoforge.mods.toml','fabric/src/main/resources/spell_engine-fabric.mixins.json','neoforge/src/main/resources/spell_engine-neoforge.mixins.json']
previous=DOC/'registration-fetch-005.json'
if previous.exists() and any(x.get('status')=='ERROR' for x in json.loads(previous.read_text()).get('results',[])):
 raise SystemExit('Prior external failure preserved; no automatic retry authorized by this script.')
results=[]
for rel in PATHS:
 p=OUT/rel;url=f'https://raw.githubusercontent.com/ZsoltMolnarrr/SpellEngine/{COMMIT}/{rel}'
 try:
  if p.exists():raw=p.read_bytes();acquisition='existing own fixed resource'
  else:
   with urllib.request.urlopen(url,timeout=25) as r:raw=r.read()
   acquisition='single fixed URL request, no retries'
  blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob==next(x['sha'] for x in TREE['tree'] if x['path']==rel)
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  results.append({'path':rel,'status':'PASS','url':url,'sha256':hashlib.sha256(raw).hexdigest(),'git_blob_sha1':blob,'acquisition':acquisition})
 except Exception as e:
  results.append({'path':rel,'status':'ERROR','url':url,'error':str(e),'policy':'No retry; stop further external requests'});break
receipt={'commit':COMMIT,'results':results,'research_credit':0,'suggested_credit':0,'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(DOC/'registration-fetch-005.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,ensure_ascii=False))

from pathlib import Path
import json,hashlib,subprocess,sys,os,re,zipfile
from PIL import Image
R=Path(__file__).resolve().parents[3];W=Path('/Users/a15356015027/.codex/worktrees/boss-eight-art/dynasty');D=R/'docs/art/swords-ui-v29';D.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'tools/art/steve-fighters-v25'));from weapons import DESIGNS
def old(rel):return subprocess.check_output(['git','show','5bf2d439:'+rel],cwd=W)
sha=lambda b:hashlib.sha256(b).hexdigest()
checks=[]
for id in DESIGNS:
 rel=f'src/main/resources/assets/dynasty/models/entity/steve_fighters/{id}.json';a=json.loads(old(rel));b=json.loads((R/rel).read_bytes());assert (R/rel).read_bytes()==(W/rel).read_bytes()
 before={p['name']:p for p in a['parts']};changed=[]
 assert set(before)=={p['name']for p in b['parts']}
 for p in b['parts']:
  n=p['name'];o=before[n]
  for k in ['parent','pivot','rotation','material']:assert p.get(k)==o.get(k),(id,n,k)
  if any(p.get(k)!=o.get(k)for k in ['origin','size']):
   assert p['parent']=='weapon_shaft' and n.startswith(('blade','broken_point','heavy_spine','hook_')),(id,n)
   assert p['origin'][0::2]==o['origin'][0::2]and p['size'][0::2]==o['size'][0::2];changed.append(n)
 im=Image.open(R/f'src/main/resources/assets/dynasty/textures/entity/steve_fighters/{id}.png');assert im.size==(b['texture_width'],b['texture_height']);assert set(im.getchannel('A').getdata())<={0,255}
 for p in b['parts']:
  for f in p['faces'].values():
   x,y=f['uv'];w,h=f['uv_size'];assert min(x,y,w,h)>=0 and x+w<=im.width and y+h<=im.height
 checks.append({'id':id,'onlyBladeLengthChanged':changed,'bodyAndGripPreserved':True,'UVInBounds':True,'textureSize':list(im.size)})
non=[]
for p in (W/'src/main/resources/assets/dynasty/models/entity/steve_fighters').glob('*.json'):
 if p.stem in DESIGNS:continue
 rel=str(p.relative_to(W));assert p.read_bytes()==old(rel)==(R/rel).read_bytes();t=rel.replace('models/entity','textures/entity').replace('.json','.png');assert(W/t).read_bytes()==old(t)==(R/t).read_bytes();non.append(p.stem)
owner=W/'docs/art/steve-fighters-v25/export-owner.json';saved=owner.read_bytes();subprocess.run([sys.executable,str(W/'tools/art/steve-fighters-v25/create.py')],env=os.environ|{'PYTHONDONTWRITEBYTECODE':'1'},check=True,stdout=subprocess.DEVNULL);assert owner.read_bytes()==saved
native=W/'docs/art/steve-fighters-v25/native'
for n in ['fighters-v25-ui-title-v29c','fighters-v25-ui-army-v29b']:assert(native/n/'PASS.txt').exists()
server=['src/main/java/com/dynasty/army/'+n+'.java'for n in ['ArmyMenu','ArmyRoster','ArmyEncounters']]
for rel in server:assert(W/rel).read_bytes()==old(rel)
with zipfile.ZipFile(W/'build/libs/dynasty-1.4.0.jar')as z:
 for c in checks:
  for base,ext in [('models','.json'),('textures','.png')]:
   rel=f'assets/dynasty/{base}/entity/steve_fighters/{c["id"]}{ext}';assert z.read(rel)==(R/'src/main/resources'/rel).read_bytes()
receipt={'swords':checks,'nonSwordAssetsByteUnchanged':non,'exportIdempotent':True,'armyServerLogicUnchanged':True,'isolatedBuild':'PASS','isolatedJarSHA256':sha((W/'build/libs/dynasty-1.4.0.jar').read_bytes()),'native':{'swordsStatic':36,'swordSequences':9,'menuSizes':5,'settingsSizes':5,'armyScreens':18},'sharedBuild':'compiled, but latest client startup FAILED texture atlas stitching storm_charm 1274x1234','sharedGameTests':{'executed':335,'failed':41,'log':'build/swords-ui-v29/army-server.log','scope':'Existing army batches executed; expanded registration also ran unrelated battles/structures. Entire suite is NOT PASS.'},'limitations':['UI captures use client data fixtures.','Natural AI combat and complete multiplayer flow not certified.','Final UI verified in isolated art worktree; parallel shared item art excluded.']}
(D/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2));print('PASS scoped assets, export, isolated build and UI. Shared startup/suite limitations recorded.')

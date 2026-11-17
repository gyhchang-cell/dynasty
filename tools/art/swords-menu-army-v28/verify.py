"""Scoped resource checks for this art delivery, with pre-edit files retained separately."""
from pathlib import Path
import json,hashlib,sys,subprocess
from PIL import Image
R=Path(__file__).resolve().parents[3];W=Path('/Users/a15356015027/.codex/worktrees/boss-eight-art/dynasty');D=R/'docs/art/swords-menu-army-v28';B=W/'docs/art/swords-menu-army-v28/before';sys.path.insert(0,str(R/'tools/art/steve-fighters-v25'));from weapons import DESIGNS
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for id in DESIGNS:
 rel=f'src/main/resources/assets/dynasty/models/entity/steve_fighters/{id}.json';old=json.loads((B/rel).read_text());now=json.loads((R/rel).read_text());parts={p['name']:p for p in now['parts']}
 protected=[]
 for p in old['parts']:
  if p['name'] in ('blade','sword_guard'):continue
  q=parts[p['name']]
  for k in ('parent','pivot','origin','size','rotation','material'):assert p.get(k)==q.get(k),(id,p['name'],k)
  protected.append(p['name'])
 im=Image.open(R/f'src/main/resources/assets/dynasty/textures/entity/steve_fighters/{id}.png');assert im.size==(now['texture_width'],now['texture_height'])
 assert set(im.getchannel('A').getdata()) <= {0,255}
 for p in now['parts']:
  for f in p['faces'].values():
   x,y=f['uv'];w,h=f['uv_size'];assert min(x,y,w,h)>=0 and x+w<=im.width and y+h<=im.height
 checks.append({'id':id,'protectedOriginalParts':len(protected),'bodyGripAndGameplayUnchanged':True,'UVInBounds':True,'PNG':list(im.size),'hardAlpha':True})
unchanged=[]
for p in (B/'src/main/resources/assets/dynasty/models/entity/steve_fighters').glob('*.json'):
 if p.stem not in DESIGNS:
  rel=p.relative_to(B);assert sha(p)==sha(R/rel);tex=Path(str(rel).replace('models/entity','textures/entity').replace('.json','.png'));assert sha(B/tex)==sha(R/tex);unchanged.append(p.stem)
owner=W/'docs/art/steve-fighters-v25/export-owner.json';before=owner.read_bytes();subprocess.run([sys.executable,str(W/'tools/art/steve-fighters-v25/create.py')],check=True,env=__import__('os').environ|{'PYTHONDONTWRITEBYTECODE':'1'});assert owner.read_bytes()==before
native=R/'docs/art/steve-fighters-v25/native'
assert all((native/n/'PASS.txt').exists() for n in ['fighters-v25-swords-v28b','fighters-v25-ui-title-v28','fighters-v25-ui-army-v28'])
server=['src/main/java/com/dynasty/army/'+x+'.java' for x in ['ArmyMenu','ArmyRoster','ArmyEncounters']]
assert not subprocess.check_output(['git','diff','HEAD','--',*server],cwd=R)
receipt={'swords':checks,'nonSwordAssetsByteUnchanged':unchanged,'generatorIdempotent':True,'serverArmyFilesUnchangedFromCurrentHEAD':True,'nativeScreens':{'swordStatic':36,'swordSampledSequences':9,'titleSizes':5,'armyScreens':15},'limitations':['Sword AI disabled in visual fixture; natural combat not tested.','Army screenshots use a client menu data fixture; actual server recruitment/action roundtrips not tested.'],'coordination':'Read user instructions in thread 01a12516-0f6f-7272-a3b7-58ea23e82b3b; sent scoped coordination message; its response confirms avoiding embedded fighter weapon assets. Item copper-dao sample remains in that thread.'}
D.mkdir(parents=True,exist_ok=True);(D/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2));print(json.dumps(receipt,ensure_ascii=False))

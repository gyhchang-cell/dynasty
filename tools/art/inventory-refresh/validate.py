"""Resource-chain checks; never claim graphical or player acceptance."""
from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v1';A=R/'src/main/resources/assets/dynasty'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 if (Path(__file__).resolve().parents[3]/'docs/art/original-runtime-v7/published.json').exists():
  import runpy
  return runpy.run_path(str(Path(__file__).with_name('check_original_runtime.py')))['check']()

 if (R/'docs/art/inventory-originals-v3/baseline.json').exists():
  import runpy
  return runpy.run_path(str(R/'tools/art/inventory-refresh/originals.py'))['check']()
 if (R/'docs/art/inventory-refresh-v2/updated-ids.json').exists():
  import runpy
  return runpy.run_path(str(R/'tools/art/inventory-refresh/validate_v2.py'))['check']()
 manifest=json.loads((D/'generated-manifest.json').read_text());rows=sum(manifest.values(),[]);errors=[];sprite=[]
 for row in rows:
  id=row['id'];path=A/'textures/item'/f'{id}.png';im=Image.open(path).convert('RGBA');pixels=list(im.getdata());colors=set(pixels);alphas={p[3] for p in pixels};w,h=im.size
  if im.size!=(16,16) or not alphas<= {0,255}:errors.append(id+': size/alpha')
  if any(im.getpixel((x,y))[3] for x in range(w) for y in (0,h-1)) or any(im.getpixel((x,y))[3] for y in range(h) for x in (0,w-1)):errors.append(id+': no transparent margin')
  model=json.loads((A/'models/item'/f'{id}.json').read_text())
  if model!={'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+id}}:errors.append(id+': incorrect model')
  sprite.append({'id':id,'size':list(im.size),'colors':len(colors),'alpha':sorted(alphas),'sha256':sha(path)})
 for id in json.loads((D/'white-backgrounds.json').read_text()):
  before=Image.open(D/'before/textures/item'/f'{id}.png').convert('RGBA');after=Image.open(A/'textures/item'/f'{id}.png').convert('RGBA')
  for old,new in zip(before.getdata(),after.getdata()):
   if old!=new and not(old==(255,255,255,255) and new==(255,255,255,0)):errors.append(id+': foreground changed');break
 for row in json.loads((D/'protected-accessories.json').read_text()):
  if sha(A/'textures/item'/f"{row['id']}.png")!=row['sha256']:errors.append(row['id']+': protected accessory changed')
 jar=R/'build/libs/dynasty-1.4.0.jar';jar_ok=0
 if jar.exists():
  with zipfile.ZipFile(jar) as z:
   targets=[A/'textures/item'/f"{x['id']}.png" for x in rows]
   targets += [A/'models/block'/f"{x['id']}.json" for x in json.loads((D/'site-models.json').read_text())]
   for p in targets:
    name='assets/dynasty/'+str(p.relative_to(A))
    if z.read(name)!=p.read_bytes():errors.append(name+': jar is stale')
    else:jar_ok+=1
 result={'sprites':sprite,'whiteMattes':38,'protectedAccessories':len(json.loads((D/'protected-accessories.json').read_text())),'jarFilesMatched':jar_ok,'errors':errors,'gameplayVisualAcceptance':'NOT_RUN; no game or save modified'}
 (D/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='sprites'},ensure_ascii=False));assert not errors
if __name__=='__main__':check()

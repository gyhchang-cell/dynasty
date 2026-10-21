from pathlib import Path
import json,zipfile,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-originals-v4';A=R/'src/main/resources/assets/dynasty'
def check():
 atlas=R/'src/main/resources/assets/minecraft/atlases/blocks.json';sources=json.loads(atlas.read_text())['sources'];count=0
 for source in sources:
  if source['type']!='minecraft:unstitch':continue
  id=source['resource'].split('/')[-1];im=Image.open(A/'textures/item'/f'{id}.png').convert('RGBA');w,h=im.size;rebuilt=Image.new('RGBA',im.size);model=json.loads((A/'models/item'/f'{id}.json').read_text());fronts=[e for e in model['elements'] if 'south' in e['faces']];assert len(fronts)==len(source['regions'])
  coverage=0
  for r,e in zip(source['regions'],fronts):
   x,y,tw,th=[r[k] for k in ('x','y','width','height')];assert source['divisor_x']==w and source['divisor_y']==h
   assert model['textures'][e['faces']['south']['texture'][1:]]==r['sprite'];assert e['faces']['south']['uv']==[0,0,16,16]
   actual=[e['from'][0]*w/16,h-e['to'][1]*h/16,e['to'][0]*w/16,h-e['from'][1]*h/16]
   assert all(abs(a-b)<1e-6 for a,b in zip(actual,[x,y,x+tw,y+th]))
   rebuilt.paste(im.crop((x,y,x+tw,y+th)),(x,y));coverage+=tw*th
  assert coverage==w*h and rebuilt.tobytes()==im.tobytes();count+=1
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:assert z.read('assets/minecraft/atlases/blocks.json')==atlas.read_bytes()
 chosen={r['id'] for r in json.loads((D/'selection.json').read_text())};baseline=json.loads((D/'baseline.json').read_text());protected=0
 for path,sha in baseline.items():
  if Path(path).stem not in chosen:assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,path;protected+=1
 result={'losslessReconstructedModels':count,'unchangedOtherItemTextures':protected,'atlasInJar':True,'gameClientTest':'NOT_RUN'};(D/'tile-validation.json').write_text(json.dumps(result,indent=2));print(result)
if __name__=='__main__':check()

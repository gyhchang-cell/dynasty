"""Check identity/size update scope and actual packaged runtime assets."""
from pathlib import Path
import json,hashlib,zipfile
from PIL import Image
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v2';V1=R/'docs/art/inventory-refresh-v1';A=R/'src/main/resources/assets/dynasty'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 ids=json.loads((D/'updated-ids.json').read_text());errors=[];sprites=[]
 for id in ids:
  p=A/'textures/item'/f'{id}.png';im=Image.open(p).convert('RGBA');box=im.getchannel('A').getbbox();colors=set(im.get_flattened_data());alphas={c[3] for c in colors};model=json.loads((A/'models/item'/f'{id}.json').read_text())
  if im.size!=(16,16) or alphas!={0,255}:errors.append(id+': invalid dimensions or alpha')
  if not box or min(box[:2])<1 or max(box[2:])>15:errors.append(id+': margin')
  if box and max(box[2]-box[0],box[3]-box[1])<13:errors.append(id+': undersized')
  if id in ['jade_brush_holder','qilin_hoof_charm'] and box and box[2]-box[0]<9:errors.append(id+': narrow identity')
  if len(colors)>12:errors.append(id+': excessive colors')
  if model!={'parent':'minecraft:item/generated','textures':{'layer0':'dynasty:item/'+id}}:errors.append(id+': resource chain')
  sprites.append({'id':id,'box':box,'colors':len(colors),'sha256':sha(p)})
 untouched=json.loads((D/'untouched-baseline.json').read_text())
 for row in untouched:
  if sha(R/row['path'])!=row['sha256']:errors.append('Outside art scope changed: '+row['path'])
 matches=0
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:
  for id in ids:
   for folder,ext in [('textures/item','.png'),('models/item','.json')]:
    p=A/folder/(id+ext);name='assets/dynasty/'+str(p.relative_to(A))
    if z.read(name)!=p.read_bytes():errors.append('Stale jar '+name)
    else:matches+=1
  for row in json.loads((V1/'site-models.json').read_text()):
   for folder in ['models/block','models/item']:
    path=A/folder/(row['id']+'.json');name='assets/dynasty/'+str(path.relative_to(A))
    if z.read(name)!=path.read_bytes():errors.append('Stale site model '+name)
    else:matches+=1
  for id in ['broken_waterwheel_repaired','wayside_tea_stall_overturned']:
   path=A/'models/block'/(id+'.json');name='assets/dynasty/'+str(path.relative_to(A))
   if z.read(name)!=path.read_bytes():errors.append('Stale state model '+id)
   else:matches+=1
  tooltip=z.read('com/dynasty/infusion/InfusionTooltips.class')
  if b'infusion.dynasty.material_hint' in tooltip or b'infusion.dynasty.tooltip' not in tooltip:errors.append('Infusion tooltip regression')
 result={'updatedItems':len(ids),'protectedItemTextures':len(untouched),'jarEntriesMatched':matches,'errors':errors,'sprites':sprites,'gameplayVisualAcceptance':'Pending; no graphical client/save/sound/brightness changes'}
 (D/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='sprites'},ensure_ascii=False));assert not errors
if __name__=='__main__':check()

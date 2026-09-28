"""Private local resource backport: change only acacia trapdoor appearance.

Uses the player's installed vanilla client assets without re-authoring artwork.
Never reads or writes saves, JAR mods, or other textures.
"""
from pathlib import Path
import json, zipfile, hashlib

ROOT=Path(__file__).resolve().parents[2]
VANILLA=Path('/Users/a15356015027/Public/.minecraft/versions/26.2/26.2.jar')
INSTANCE=Path('/Users/a15356015027/Public/.minecraft/versions/Dynasty 王朝')
OUT=ROOT/'docs/art/acacia-shelf-only'
PACK=OUT/'Dynasty-Acacia-Mangrove-Shelf.zip'

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(VANILLA) as src:
  model=json.loads(src.read('assets/minecraft/models/block/template_shelf_inventory.json'))
  model['display'].pop('on_shelf',None)
  model['textures']={'all':'minecraft:block/dynasty_mangrove_shelf','particle':'minecraft:block/stripped_mangrove_log'}
  # A thin trapdoor must not hide shelf surfaces when adjacent blocks are present.
  for element in model['elements']:
   for face in element['faces'].values():face.pop('cullface',None)
  variants={}
  for facing,angle in [('north',0),('east',90),('south',180),('west',270)]:
   for half in ['bottom','top']:
    for opened in [False,True]:
     x=(0 if half=='bottom' else 180) if opened else (90 if half=='bottom' else 270)
     y=(angle+180)%360 if opened and half=='top' else angle
     variants[f'facing={facing},half={half},open={str(opened).lower()}']={'model':'minecraft:block/dynasty_mangrove_shelf','x':x,'y':y}
  files={
   'pack.mcmeta':json.dumps({'pack':{'pack_format':15,'description':'仅金合欢活板门 → 原版红树木展示架外观'}},ensure_ascii=False).encode(),
   'assets/minecraft/textures/block/dynasty_mangrove_shelf.png':src.read('assets/minecraft/textures/block/mangrove_shelf.png'),
   'assets/minecraft/models/block/dynasty_mangrove_shelf.json':json.dumps(model).encode(),
   'assets/minecraft/models/item/acacia_trapdoor.json':json.dumps({'parent':'minecraft:block/dynasty_mangrove_shelf'}).encode(),
   'assets/minecraft/blockstates/acacia_trapdoor.json':json.dumps({'variants':variants}).encode(),
  }
 with zipfile.ZipFile(PACK,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in files.items():z.writestr(name,data)
 target=INSTANCE/'resourcepacks'/PACK.name
 target.parent.mkdir(exist_ok=True)
 if target.exists() and target.read_bytes()!=PACK.read_bytes():
  raise SystemExit('Existing resource pack differs; inspect before replacing')
 target.write_bytes(PACK.read_bytes())
 assert len(files)==5 and len(variants)==16
 report={'source':str(VANILLA),'installed':str(target),'sha256':hashlib.sha256(PACK.read_bytes()).hexdigest(),'files':list(files),'variants':len(variants),'scope':'Only acacia trapdoor visual overrides; no save or mod writes. Activate in Resource Packs.'}
 (OUT/'installation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

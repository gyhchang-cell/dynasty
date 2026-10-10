"""Final exported boss resource checks, separate from native combat acceptance."""
import json,hashlib
from pathlib import Path
from PIL import Image
from build_models import ASSET,REPO
OUT=REPO/'docs/art/cod6-cuboid-v1'

def main():
 manifest=json.loads((OUT/'model-manifest.json').read_text());results={}
 for id,entry in manifest.items():
  files=[ASSET/f'geo/boss_cuboid/{id}.geo.json',ASSET/f'animations/boss_cuboid/{id}.animation.json',ASSET/f'textures/entity/boss_cuboid/{id}.png']
  g=json.loads(files[0].read_text())['minecraft:geometry'][0];a=json.loads(files[1].read_text())['animations'];im=Image.open(files[2]).convert('RGB')
  assert im.size==(16,16) and len(im.getcolors(1000))==4,id
  assert g['description']['texture_width']==16 and g['description']['texture_height']==16
  white=(255,255,255)
  for y in range(16):
   for x in range(16):
    if x in (0,15) or y in (0,15):assert im.getpixel((x,y))==white,id
    assert im.getpixel((x,y))==im.getpixel((x-x%2,y-y%2)),(id,'sub2px detail')
  names=set()
  for b in g['bones']:
   assert b['name'] not in names and (not b.get('parent') or b['parent'] in names),(id,b['name'])
   names.add(b['name'])
   for c in b.get('cubes',[]):
    assert len(c['size'])==3 and all(v>0 for v in c['size'])
    assert len(c['uv'])==6
    for uv in c['uv'].values():
     x,y=uv['uv'];w,h=uv['uv_size'];assert 0<=x<x+w<=16 and 0<=y<y+h<=16
     assert white not in set(im.crop((x,y,x+w,y+h)).getdata()),(id,'background on mesh')
  assert set(entry['animationNames'])==set(a),id
  for clip,anim in a.items():
   assert set(anim['bones'])<=names,(id,clip,'unknown bone')
   for track in anim['bones'].values():
    for values in track.values():
     assert max(map(float,values))<=anim['animation_length']
     if anim.get('loop'):assert list(values.values())[0]==list(values.values())[-1]
  results[id]={'bones':len(names),'cuboids':sum(len(b.get('cubes',[])) for b in g['bones']),'clips':len(a),'actualPixels':[16,16],'pureColorsIncludingWhite':4,
               'resources':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'combatSkillSync':'pending; resource matrix only'}
 (OUT/'static-validation.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS boss exported resources:',len(results),'models,',sum(v['clips'] for v in results.values()),'clips')

if __name__=='__main__':main()

"""Sparse original emissive mask on the existing V17 atlas; never changes its base pixels."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[3];D=R/'docs/art/tianjiang-aura-v18'
A=R/'src/main/resources/assets/dynasty';ID='nine_heaven_general'
OUT=A/'textures/entity/boss_cuboid'/f'{ID}_aura.png'
def export():
 baseline=json.loads((D/'baseline-hashes.json').read_text())
 for n,h in baseline.items():
  if '/assets/' in n:assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,'Accepted V17 asset changed'
 geo=json.loads((A/'geo/boss_cuboid'/f'{ID}.geo.json').read_text())['minecraft:geometry'][0]
 src=Image.open(A/'textures/entity/boss_cuboid'/f'{ID}.png').convert('RGB')
 im=Image.new('RGBA',src.size,(0,0,0,0));counts={}
 for b in geo['bones']:
  for i,c in enumerate(b.get('cubes',[])):
   for face,u in c['uv'].items():
    x,y=u['uv'];w,h=u['uv_size']
    for py in range(h):
     for px in range(w):
      color=None
      if b['name']=='chest' and face=='north' and 6<=px<=10 and 6<=py<=12:
       if src.getpixel((x+px,y+py)) in [(177,138,80),(222,195,145)]:color=(229,194,125,255)
      if b['name']=='weapon' and i==2 and face=='north' and px==w//2-1 and 2<=py<=h-4:
       color=(144,220,221,225)
      # One short section of each broad cutting face; not a full glowing weapon.
      if b['name']=='weapon' and i==4 and face in ['north','south'] and px==(0 if face=='north' else w-1) and h//3<=py<=2*h//3:
       color=(156,216,228,185)
      if color:
       im.putpixel((x+px,y+py),color);counts[b['name']]=counts.get(b['name'],0)+1
 assert counts.get('chest',0)>3 and counts.get('weapon',0)>3 and set(counts)=={'chest','weapon'}
 OUT.parent.mkdir(parents=True,exist_ok=True);im.save(OUT);im.save(D/'emissive-mask.png')
 im.resize((512,512),Image.Resampling.NEAREST).save(D/'emissive-mask-4x.png')
 (D/'mask-validation.json').write_text(json.dumps({'atlas':[128,128],'activePixelsByBone':counts,'headPixels':0,'baseTextureGeometryAnimationUnchanged':True,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()},indent=2)+'\n')
 print(counts)
if __name__=='__main__':export()

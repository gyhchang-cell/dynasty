"""Original effect-only atlas and emissive marks. Never writes the accepted body atlas/rig."""
from pathlib import Path
from PIL import Image
import json,hashlib,math
R=Path(__file__).resolve().parents[3];D=R/'docs/art/tianjiang-aura-v19';A=R/'src/main/resources/assets/dynasty'
ID='nine_heaven_general'
LOCKS={'geo/boss_cuboid/'+ID+'.geo.json':'35549c51b8f2f6752ee219bf5fd3136ee8ba99d5fa0654456b0fae5475191700','animations/boss_cuboid/'+ID+'.animation.json':'862b4d8839449d269635f67c131a9639f69ad4dae4c74d7f0cf78f8c3c861ced','textures/entity/boss_cuboid/'+ID+'.png':'248154f020451e64731bceee31997fcf937171ee62927fed52ea55b69afae05a'}
def run():
 for p,h in LOCKS.items():assert hashlib.sha256((A/p).read_bytes()).hexdigest()==h,p
 # A 16-step alpha cross-section: crisp luminous centre with a wider dissolving envelope.
 # This is an original runtime effect primitive, not a blur/filter applied to body materials.
 im=Image.new('RGBA',(16,32),(255,255,255,0))
 for y in range(32):
  t=abs((y+.5)/16-1);alpha=round((max(0,1-t)**2.2)*15)*17
  for x in range(16):im.putpixel((x,y),(255,255,255,alpha))
 out=A/'textures/effect/tianjiang_stream.png';out.parent.mkdir(parents=True,exist_ok=True);im.save(out)
 # Base colours and UV remain locked. Follow existing thunder emblem, wrist trim and jade weapon channels.
 geo=json.loads((A/'geo/boss_cuboid'/f'{ID}.geo.json').read_text())['minecraft:geometry'][0]
 base=Image.open(A/'textures/entity/boss_cuboid'/f'{ID}.png').convert('RGB');mask=Image.new('RGBA',base.size);counts={}
 for bone in geo['bones']:
  name=bone['name']
  for ci,cube in enumerate(bone.get('cubes',[])):
   for face,uv in cube['uv'].items():
    x,y=uv['uv'];w,h=uv['uv_size']
    for py in range(h):
     for px in range(w):
      rgb=base.getpixel((x+px,y+py));color=None
      if name=='chest' and face=='north' and 6<=px<=10 and 6<=py<=12 and rgb in [(177,138,80),(222,195,145)]:color=(255,205,106,255)
      if name=='weapon' and ci==2 and face in ['north','south'] and px in [w//2-1,w//2] and 1<=py<h-1:color=(128,231,255,255)
      if name=='weapon' and ci in [4,5,6] and face in ['north','south'] and px==(0 if face=='north' else w-1) and 1<=py<h-1:color=(178,238,255,215)
      if color:mask.putpixel((x+px,y+py),color);counts[name]=counts.get(name,0)+1
 mask.save(A/'textures/entity/boss_cuboid'/f'{ID}_aura.png')
 mask.save(D/'emissive-mask.png');mask.resize((512,512),Image.Resampling.NEAREST).save(D/'emissive-mask-4x.png')
 (D/'asset-validation.json').write_text(json.dumps({'lockedAcceptedAssets':LOCKS,'activeEmissivePixels':counts,'headUnchanged':True,'originalEffectTexture':[16,32]},indent=2)+'\n');print(counts)
if __name__=='__main__':run()

"""Actual exported geometry; same orthographic scale for every model and player."""
import importlib.util,inspect,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/boss-forms-v2';A=R/'src/main/resources/assets/dynasty'
s=importlib.util.spec_from_file_location('render',R/'tools/art/secondary-cuboid/review_models.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);r.CATEGORY='boss_forms';r.OUT=D
code=inspect.getsource(r.raster).replace('baseline=False):','baseline=False,gray=False,common_scale=3.8):').replace('scale=min((w-64)/(hi[0]-lo[0]),(h-70)/(hi[1]-lo[1]))','scale=common_scale\n    assert (hi[0]-lo[0])*scale<w-26 and (hi[1]-lo[1])*scale<h-28, (hi-lo,scale,size)').replace("color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade", "color=np.zeros((*xx.shape,3)) if silhouette else atlas[ty,tx]*shade\n            if gray:color=np.full((*xx.shape,3),1.0)*np.array([176,181,185])*shade\n            if bone=='__player':color=np.full((*xx.shape,3),1.0)*np.array([62,110,133])*shade")
exec(code,r.__dict__)
F='/System/Library/Fonts/STHeiti Medium.ttc';font=lambda n:ImageFont.truetype(F,n) if Path(F).exists() else r.font(n)
def player(offset):
 q=[]
 # Width 0.6m / visible height1.8m, with head and limbs for immediate scale recognition.
 for o,size in [([-4,21.6,-4],[8,7.2,8]),([-4,10.8,-2],[8,10.8,4]),([-7,10.8,-2],[3,10.8,4]),([4,10.8,-2],[3,10.8,4]),([-4,0,-2],[4,10.8,4]),([0,0,-2],[4,10.8,4])]:
  for f,cs in r.FACES.items():q.append((np.array(cs)*size+np.array(o)+offset,{'uv':[2,2],'uv_size':[2,2]},'__player'))
 return q

def view(g,angle,gray=True,omit=(),clip=None,tick=0,scale=3.6,size=(620,360),silhouette=False):
 q=r.geometry(g['id'],clip=clip,tick=tick);bones=json.loads((A/'geo/boss_forms'/f"{g['id']}.geo.json").read_text())['minecraft:geometry'][0]['bones'];excluded=set(omit)
 for b in bones:
  if b.get('parent') in excluded:excluded.add(b['name'])
 q=[v for v in q if v[2] not in excluded];pts=np.concatenate([v[0] for v in q]);a=math.radians(angle);right=np.array([math.cos(a),0,math.sin(a)]);offset=right*((pts@right).min()-17);q+=player(offset)
 return r.raster(q,angle,6,size=size,gray=gray,common_scale=scale,silhouette=silhouette)
def label(im,text):
 out=Image.new('RGB',(im.width,im.height+42),(238,235,225));out.paste(im,(0,0));ImageDraw.Draw(out).text((14,im.height+4),text,font=font(18),fill=(35,40,45));return out

def main():
 import argparse;p=argparse.ArgumentParser();p.add_argument('--color',action='store_true');args=p.parse_args();gray=not args.color;ms=json.loads((D/'forms.json').read_text());overview=Image.new('RGB',(1240,4*402+65),(238,235,225));d=ImageDraw.Draw(overview);d.text((18,14),'八种形态 · 同一比例 / 玩家 1.8m · '+('灰模' if gray else '实际像素UV'),font=font(24),fill=(35,40,45))
 dimensions={}
 for i,m in enumerate(ms):
  q=r.geometry(m['id']);v=np.concatenate([x[0] for x in q]);lo=v.min(0);hi=v.max(0);dimensions[m['id']]={'width':round((hi[0]-lo[0])/16,2),'height':round(hi[1]/16,2),'length':round((hi[2]-lo[2])/16,2),'lowestY':round(lo[1]/16,3)}
  views=[label(view(m,a,gray),t) for a,t in [(0,'正视'),(90,'侧视'),(45,'三分之二视角'),(180,'背面')]]
  views+=[label(view(m,45,gray,omit=m['weapons']+m['decor']),'隐藏武器及身份装饰'),label(view(m,0,False,silhouette=True),'纯黑剪影 / 玩家比例')]
  card=Image.new('RGB',(1860,804+60),(238,235,225));ImageDraw.Draw(card).text((18,10),m['name']+'   '+f"宽{hi[0]/16-lo[0]/16:.1f} × 高{hi[1]/16:.1f} × 长{hi[2]/16-lo[2]/16:.1f} 米 · 玩家1.8米",font=font(24),fill=(35,40,45))
  for j,im in enumerate(views):card.paste(im,((j%3)*620,60+(j//3)*402))
  card.save(D/(m['id']+('-gray.png' if gray else '-color.png')))
  overview.paste(label(view(m,45,gray),m['name']+f"   高{hi[1]/16:.1f}m"),((i%2)*620,65+(i//2)*402))
 overview.save(D/('gray-overview.png' if gray else 'color-overview.png'));(D/'dimensions.json').write_text(json.dumps(dimensions,indent=2)+'\n');print(dimensions)
if __name__=='__main__':main()

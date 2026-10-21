"""Three original nonhuman refinements. Existing entities, hierarchy and combat clips retained.
Canonical shape inputs live beside this file, so legacy exports cannot undo the new UV/art.
"""
import json,math,copy
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3]; A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/steve-fighters-v25/nonhuman';SRC=Path(__file__).parent/'nonhuman-source'
IDS=['carp_spirit','tree_spirit','clockwork_rat'];NAMES=['鲤鱼精','树灵','机关鼠']
def export(ids=None):
 SRC.mkdir(exist_ok=True);D.mkdir(parents=True,exist_ok=True)
 for id in (IDS if ids is None else ids):
  gp=A/f'geo/secondary/{id}.geo.json';ap=A/f'animations/secondary/{id}.animation.json';tp=A/f'textures/entity/secondary/{id}.png';dd=D/id;dd.mkdir(exist_ok=True)
  if not (SRC/(id+'.geo.json')).exists():
   (SRC/(id+'.geo.json')).write_bytes(gp.read_bytes());(SRC/(id+'.animation.json')).write_bytes(ap.read_bytes());(dd/'before.geo.json').write_bytes(gp.read_bytes());(dd/'before.png').write_bytes(tp.read_bytes())
  doc=json.loads((SRC/(id+'.geo.json')).read_text());g=doc['minecraft:geometry'][0];by={b['name']:b for b in g['bones']}
  def cubes(n,items):by[n]['cubes']=[dict(origin=o,size=s,material=m)for o,s,m in items]
  if id=='carp_spirit':
   cubes('body',[([-3.5,5,-6],[7,7,12],'scales'),([-2.5,4,-4],[5,2,10],'belly')])
   cubes('head',[([-3,6,-10],[6,5,4],'scales'),([-2.5,6,-11],[5,3,1],'snout'),([-3.5,8,-9],[1,2,2],'eye'),([2.5,8,-9],[1,2,2],'eye'),([-3,6,-13],[.5,1,3],'barbel'),([2.5,6,-13],[.5,1,3],'barbel')])
   cubes('jaw',[([-2,5.25,-11.25],[4,1,2],'belly')])
   cubes('dorsal',[([-.5,12,-4],[1,3,9],'fin'),([-.5,15,-1],[1,1,5],'fin')])
   for side,s in [('left',1),('right',-1)]:cubes(side+'_fin',[([3 if s>0 else -7,6,-2],[4,1,7],'fin')])
   cubes('tail',[([-2,6,6],[4,4,4],'scales')]);cubes('tail_tip',[([-1,6,9],[2,4,3],'fin')]);cubes('tail_fan',[([-.5,4,12],[1,7,4],'fin'),([-.5,3,15],[1,3,2],'fin'),([-.5,9,15],[1,3,2],'fin')])
  elif id=='tree_spirit':
   cubes('body',[([-6,4,-4.5],[12,15,9],'bark'),([-4,19,-3],[8,7,6],'bark'),([-6.5,7,0],[1.5,7,4],'bark'),([5,9,-3],[2,6,4],'bark')])
   # The gaze is a knot in the trunk; no human nose or human head under a tree hat.
   cubes('head',[([-4,18,-5],[8,7,2],'facewood'),([-3,20,-5.7],[2,2,1],'sapeye'),([1,20,-5.7],[2,2,1],'sapeye'),([-2,18,-5.6],[4,.5,1],'hollow')])
   for i,(x,z) in enumerate([(-4,-2),(4,-2),(-4,2),(4,2)]):
    cubes('leg_'+str(i),[([x-2,1,z-2],[4,5,4],'root')]);cubes('foot_'+str(i),[([x-3 if x<0 else x,0,z-2],[4,2,4],'root')])
   for side,s in [('left',1),('right',-1)]:
    cubes(side+'_branch',[([5 if s>0 else -8,17,-1],[3,6,3],'branch')]);cubes(side+'_twig',[([7 if s>0 else -10,18,-1],[3,5,3],'branch'),([8 if s>0 else -12,21 if s>0 else 19,-3],[4,4,5],'leaves')])
    by[side+'_branch']['rotation']=[0,0,-s*18];by[side+'_twig']['rotation']=[0,s*12,0]
   for i in range(4):
    items=[]
    for c in by['branch_'+str(i)].get('cubes',[]):items.append((c['origin'],c['size'],'branch'))
    if i in (0,2):items.append(([-7 if i==0 else 0,28 if i==0 else 30,-4],[6,4,5],'leaves'))
    cubes('branch_'+str(i),items)
   cubes('tail',[([-3,1,3],[6,3,4],'root')])
  else:
   cubes('body',[([-3.5,2,-3],[7,5,8],'wood'),([-3.5,5,-2],[7,1,6],'brass'),([-4,3,-2],[1,3,5],'iron'),([3,3,-2],[1,3,5],'iron')])
   cubes('neck',[([-2,3,-4],[4,3,2],'iron')]);cubes('head',[([-2.5,3,-7],[5,3,4],'wood'),([-1.5,2.5,-10],[3,2,3],'brass'),([-1,3,-11],[2,1,1],'iron'),([-3,4,-7.15],[1,1.5,1],'eye'),([2,4,-7.15],[1,1.5,1],'eye')])
   cubes('ears',[([-4,5,-5],[2,3,1],'brass'),([2,5,-5],[2,3,1],'brass')])
   for b in g['bones']:
    for c in b.get('cubes',[]):c.setdefault('material','brass' if b['name']=='key' else 'iron' if b['name'].startswith('leg_') else 'wood' if b['name'].startswith('tail') else 'iron')
  atlas=Image.new('RGB',(128,128),(28,33,32));x=y=row=0;islands=[]
  for b in g['bones']:
   for j,c in enumerate(b.get('cubes',[])):
    mat=c.pop('material','fin' if 'fin' in b['name'] else 'branch');sx,sy,sz=c['size'];dims={'north':(sx,sy),'south':(sx,sy),'west':(sz,sy),'east':(sz,sy),'up':(sx,sz),'down':(sx,sz)};c['uv']={}
    for face,(w,h) in dims.items():
     w=max(1,math.ceil(w));h=max(1,math.ceil(h))
     if x+w+2>128:x=0;y+=row+2;row=0
     assert y+h<=128,(id,b['name'],y)
     tile=paint(id,mat,face,w,h,b['name'],j,c['size']);atlas.paste(tile,(x,y));c['uv'][face]={'uv':[x,y],'uv_size':[w,h]};islands.append({'bone':b['name'],'cube':j,'face':face,'material':mat,'rect':[x,y,w,h]});x+=w+2;row=max(row,h)
  g['description'].update(texture_width=128,texture_height=128)
  # Crop bounds are conservative but finite; no server collision or dimension change.
  g['description'].update(visible_bounds_width=3 if id=='tree_spirit' else 2.5,visible_bounds_height=3 if id=='tree_spirit' else 2,visible_bounds_offset=[0,1 if id=='tree_spirit' else .5,0])
  gp.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n');ap.write_bytes((SRC/(id+'.animation.json')).read_bytes());atlas.save(tp);atlas.save(dd/'texture.png');atlas.resize((512,512),Image.Resampling.NEAREST).save(dd/'texture-4x.png');(dd/'islands.json').write_text(json.dumps(islands,indent=2)+'\n')
  overlay=atlas.resize((512,512),Image.Resampling.NEAREST);d=ImageDraw.Draw(overlay)
  for n,i in enumerate(islands):x0,y0,w,h=i['rect'];d.rectangle((x0*4,y0*4,(x0+w)*4-1,(y0+h)*4-1),outline=(224,99,148))
  overlay.save(dd/'uv-overlay.png')
 print('Original nonhuman model/UV refinements:',', '.join(IDS if ids is None else ids))

def paint(id,mat,face,w,h,bone,j,size):
 colors={'scales':(160,71,48),'belly':(220,183,113),'snout':(202,131,63),'barbel':(197,147,85),'fin':(155,88,54),'bark':(104,76,49),'facewood':(128,95,59),'root':(79,63,44),'branch':(117,85,52),'leaves':(73,100,58),'wood':(130,94,57),'brass':(158,133,71),'iron':(56,69,68),'eye':(225,193,97),'sapeye':(195,165,88),'hollow':(47,46,36)}
 base=colors[mat];shade=lambda m:tuple(round(c*m)for c in base);im=Image.new('RGB',(w,h),shade(.8)if face=='down' else base);d=ImageDraw.Draw(im)
 if mat in ('bark','facewood','branch','root','wood'):
  axis=max(range(3),key=lambda n:size[n]);vertical=axis==1 or face in ('north','south')and axis==2
  # Seams follow growth or the beam's long axis, with only a few broken strands.
  if vertical:
   for u in range(2,w,4):d.line((u,1,u,max(1,h-2)),fill=shade(.75));d.line((min(w-1,u+1),max(1,h//3),min(w-1,u+1),max(1,h*2//3)),fill=shade(1.12))
  else:
   for v in range(2,h,4):d.line((1,v,max(1,w-2),v),fill=shade(.76))
  if mat=='wood' and face in ('up','north'):d.line((1,0,max(1,w-2),0),fill=shade(1.15))
 elif mat=='scales':
  if face=='up':d.rectangle((0,0,w-1,h-1),fill=(132,59,43))
  elif face=='down':d.rectangle((0,0,w-1,h-1),fill=(217,175,104))
  else:
   for yy in range(1,h,3):
    for xx in range((yy//3%2)*2,w,4):d.line((xx,yy,min(w-1,xx+2),yy),fill=shade(1.19));d.point((min(w-1,xx+2),min(h-1,yy+1)),fill=shade(.83))
 elif mat=='fin':
  for yy in range(1,h,3):d.line((0,yy,w-1,min(h-1,yy+1)),fill=shade(1.22))
  if w>2:d.line((w-1,0,w-1,h-1),fill=shade(.72))
 elif mat in ('eye','sapeye'):
  d.rectangle((0,0,w-1,h-1),fill=(48,48,37));d.rectangle((0,h//3,max(0,w-1),max(h//3,h*2//3)),fill=base)
  if w>1:d.rectangle((w//2,h//3,w//2,max(h//3,h*2//3)),fill=(34,36,33))
 elif mat=='brass':
  d.line((0,0,max(0,w-2),0),fill=shade(1.25));d.line((max(0,w-1),1,max(0,w-1),h-1),fill=shade(.72))
 elif mat=='iron':
  if h>2:d.line((0,1,max(0,w-2),1),fill=shade(1.3));d.line((0,h-1,w-1,h-1),fill=shade(.72))
 elif mat=='leaves':
  d.rectangle((0,max(0,h-1),w-1,h-1),fill=shade(.7));
  for xx in range(1,w,3):d.line((xx,0,min(w-1,xx+1),max(0,h-2)),fill=shade(1.2))
 elif mat=='belly':
  for yy in range(2,h,4):d.line((0,yy,w-1,yy),fill=shade(.9))
 return im
if __name__=='__main__':export()

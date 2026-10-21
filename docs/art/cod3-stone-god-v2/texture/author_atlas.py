"""Original native pixel brush recipes on frozen 1024px per-face islands.
No noise, gradients, image resampling or sampled third-party asset pixels.
"""
from pathlib import Path
import json,math,hashlib
import numpy as np
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[3];H=D.parent/'TEXTURE_HANDOFF.json'
P={
 'rock':[(55,66,66),(79,90,88),(101,111,104),(121,130,119),(141,147,132),(43,53,54)],
 'strata':[(65,78,75),(93,105,98),(118,129,117),(140,150,133),(155,163,146),(52,65,64)],
 'joint_rock':[(40,53,53),(57,72,69),(75,90,83),(94,108,97),(113,124,110),(32,43,46)],
 'crown':[(57,74,69),(82,101,87),(109,126,104),(134,147,122),(147,157,135),(45,61,58)],
 'stone_face':[(68,81,78),(96,110,99),(126,140,120),(147,158,135),(163,170,148),(43,58,56)],
 'bronze':[(56,47,35),(84,66,43),(115,90,55),(141,115,73),(66,88,74),(43,41,33)],
 'jade':[(40,65,59),(64,98,82),(98,130,104),(122,148,120),(46,77,67),(31,48,47)],
 'haft':[(40,33,27),(66,49,33),(89,67,43),(114,89,58),(79,61,43),(32,29,25)],
 'binding':[(41,46,42),(64,69,57),(88,91,72),(112,111,87),(66,82,68),(30,37,36)],
 'axe_edge':[(69,85,83),(99,116,108),(137,150,134),(170,179,158),(120,138,122),(50,65,66)]}
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def xyz(row,u,v):
 a,b,c,e=np.array(row['uv_corners_local_normalized'],float);q=a+(b-a)*u+(e-a)*v
 return np.array(row['cube_origin'])+np.array(row['cube_size'])*q

def tile(row):
 w,h=row['rect'][2:];mat=row['material'];p=P[mat];part=row['part'];face=row['face'];im=Image.new('RGB',(w,h),p[2 if mat in ('stone_face','strata') else 1]);d=ImageDraw.Draw(im)
 def poly(points,n):d.polygon([(int(x*(w-1)),int(y*(h-1))) for x,y in points],fill=p[n])
 def stroke(points,n,width=1):d.line([(int(x*(w-1)),int(y*(h-1))) for x,y in points],fill=p[n],width=width)
 if mat in ('rock','strata','joint_rock','crown'):
  # Curated broad fracture topologies by anatomical role, not per-pixel RNG.
  if row['grain_axis_local']=='Y' and face not in ('up','down'):
   poly([(0,0),(.38,0),(.38,.25),(.27,.25),(.27,.7),(.12,.7),(.12,1),(0,1)],2)
   poly([(.8,0),(1,0),(1,1),(.58,1),(.58,.78),(.72,.78),(.72,.39),(.8,.39)],0)
   if min(w,h)>=10:
    stroke([(.51,.13),(.51,.3),(.62,.3),(.62,.48)],0,max(1,w//28))
    stroke([(.52,.14),(.52,.28),(.65,.28)],2,max(1,w//40))
  else:
   poly([(0,0),(1,0),(1,.17),(.73,.17),(.73,.25),(.36,.25),(.36,.32),(0,.32)],2)
   poly([(0,.78),(.21,.78),(.21,.67),(.63,.67),(.63,.76),(1,.76),(1,1),(0,1)],0)
   # Strata is a thick irregular bed, not repeated bricks or full edge outlines.
   if mat=='strata':
    poly([(0,.32),(.3,.32),(.3,.24),(.7,.24),(.7,.32),(1,.32),(1,.49),(.7,.49),(.7,.42),(.3,.42),(.3,.49),(0,.49)],3)
   if min(w,h)>=12:
    if 'pectoral' in part or 'deltoid' in part:
     stroke([(.12,.46),(.31,.46),(.31,.53),(.47,.53),(.47,.63)],0,max(1,min(w,h)//22))
    elif part in ('ribcage','pelvic_mass','scapular_shelf','skull','axe_cheek') or 'heel' in part:
     stroke([(.68,.18),(.68,.37),(.59,.37),(.59,.52),(.75,.52)],0,max(1,min(w,h)//27))
    elif 'shin' in part or 'forearm' in part:
     stroke([(.2,.22),(.2,.43),(.32,.43),(.32,.6)],0,max(1,min(w,h)//25))
  if mat=='crown' and face=='up':poly([(.13,.12),(.7,.12),(.7,.29),(.34,.29),(.34,.55),(.13,.55)],3)
  # A small flat corner spall; only selected substantial blocks, never an all-edge frame.
  if min(w,h)>=24 and part in ('ribcage','right_femur','left_femur','axe_root'):
   poly([(.09,.08),(.3,.08),(.3,.15),(.22,.15),(.22,.23),(.09,.23)],3)
 elif mat=='stone_face':
  poly([(0,0),(.2,0),(.2,.55),(.28,.55),(.28,1),(0,1)],1)
  poly([(.78,0),(1,0),(1,1),(.7,1),(.7,.64),(.78,.64)],0)
  if face=='up':poly([(.2,.1),(.8,.1),(.8,.6),(.65,.6),(.65,.8),(.2,.8)],3)
  if part=='stone_mask' and face=='south':
   # The existing jade eye geometry is the eye; no painted duplicate eyes.
   for yy in range(h):
    for xx in range(w):
     x,y,z=xyz(row,(xx+.5)/w,(yy+.5)/h)
     if 433<=y<437 and 18<=abs(x)<29:im.putpixel((xx,yy),p[0])
     if 459<=y<462 and abs(x)<22:im.putpixel((xx,yy),p[1])
   stroke([(.11,.64),(.2,.64),(.2,.84)],0)
  if part=='nose_bridge' and face=='south':
   poly([(0,0),(.39,0),(.39,.75),(.23,.75),(.23,1),(0,1)],0)
   poly([(.45,.03),(.75,.03),(.75,.72),(.92,.72),(.92,.88),(.45,.88)],3)
  if part=='jaw_plane' and face=='south':
   # A restrained carved mouth on the existing jaw, no moustache ornament.
   d.line((w//5,h//3,4*w//5,h//3),fill=p[5],width=max(1,h//5))
   d.line((w//3,h//3+2,2*w//3,h//3+2),fill=p[1],width=1)
 elif mat=='bronze':
  poly([(0,0),(1,0),(1,.18),(.46,.18),(.46,.27),(0,.27)],2)
  poly([(0,.8),(.34,.8),(.34,.7),(.7,.7),(.7,.84),(1,.84),(1,1),(0,1)],0)
  if part=='central_girdle' and face=='south':
   # Original broad stepped mountain relief; dark recessed corners, not a gilt frame.
   poly([(.2,.73),(.2,.43),(.36,.43),(.36,.27),(.55,.27),(.55,.48),(.76,.48),(.76,.73)],2)
   stroke([(.25,.73),(.25,.49),(.41,.49),(.41,.34)],3)
  if w>=12 and h>=4:poly([(.72,.52),(.95,.52),(.95,.68),(.82,.68),(.82,.86),(.72,.86)],4)
 elif mat=='jade':
  d.rectangle((0,0,w-1,h-1),fill=p[1]);d.line((1,0,max(1,w-2),0),fill=p[2])
  if h>2:d.line((0,h-1,w-1,h-1),fill=p[0])
 elif mat=='haft':
  if face in ('up','down'):
   d.rectangle((0,0,w-1,h-1),fill=p[0]);d.rectangle((1,1,max(1,w-2),max(1,h-2)),fill=p[2])
  else:
   d.rectangle((max(1,w//3),0,max(1,w//3+1),h-1),fill=p[2])
   for lo,hi in [(.08,.26),(.4,.57),(.74,.91)]:d.line((max(0,w-2),int(h*lo),max(0,w-2),min(h-1,int(h*hi))),fill=p[0],width=1)
 elif mat=='binding':
  if part=='axe_socket':
   poly([(0,0),(.65,0),(.65,.2),(.2,.2),(.2,.6),(0,.6)],2)
   poly([(.8,.3),(1,.3),(1,1),(.28,1),(.28,.8),(.8,.8)],0)
  else:
   d.line((0,0,w-1,0),fill=p[2]);d.line((0,h-1,w-1,h-1),fill=p[0])
   if w>7 and h>2:d.rectangle((w//2,1,w//2+1,max(1,h-2)),fill=p[0])
 elif mat=='axe_edge':
  for yy in range(h):
   for xx in range(w):
    x,y,z=xyz(row,(xx+.5)/w,(yy+.5)/h);ox=row['cube_origin'][0];sx=row['cube_size'][0];t=(x-ox)/sx
    color=p[3 if t<.22 else 2 if t<.55 else 1]
    if 416<=y<422 and t<.14:color=p[1]
    im.putpixel((xx,yy),color)
 return im

def main():
 h=json.loads(H.read_text());assert h['status']=='UV_FROZEN' and h['atlas_size']==[1024,1024]
 assert json.loads((D.parent/'UV_LOCK.json').read_text())==h
 im=Image.new('RGB',(1024,1024),(30,39,40));used=np.zeros((1024,1024),np.uint8);records=[]
 for row in h['islands']:
  x,y,w,ht=row['rect'];assert min(x,y,w,ht)>0 and x+w<1024 and y+ht<1024
  assert not used[y:y+ht,x:x+w].any();used[y:y+ht,x:x+w]=1;t=tile(row);im.paste(t,(x,y))
  im.paste(t.crop((0,0,w,1)),(x,y-1));im.paste(t.crop((0,ht-1,w,ht)),(x,y+ht));im.paste(t.crop((0,0,1,ht)),(x-1,y));im.paste(t.crop((w-1,0,w,ht)),(x+w,y))
  for dx,dy,sx,sy in [(-1,-1,0,0),(w,-1,w-1,0),(-1,ht,0,ht-1),(w,ht,w-1,ht-1)]:im.putpixel((x+dx,y+dy),t.getpixel((sx,sy)))
  records.append({'island_id':row['island_id'],'part':row['part'],'face':row['face'],'material':row['material'],'rect':row['rect'],'nativeColors':len(t.getcolors(w*ht))})
 im.save(D/'stone_god.png')
 (D/'authoring.json').write_text(json.dumps({'workflow':'Original native per-face pixel brush recipes; explicit flat palette, curated anatomical plane/fracture patterns; no random noise, gradients, resampling or asset copying','palettes':P,'atlas':[1024,1024],'islands':len(records),'sampledTexels':int(used.sum()),'totalColors':len(im.getcolors(1024*1024)),'sourcePngSha256':SHA(D/'stone_god.png'),'handoffSha256':SHA(H),'islandRecords':records},ensure_ascii=False,indent=2)+'\n')
 print('Authored420 islands;',int(used.sum()),'sampled texels;',len(im.getcolors(1024*1024)),'explicit colors')
if __name__=='__main__':main()

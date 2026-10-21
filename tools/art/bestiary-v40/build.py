"""Original paired quadrupeds: native model-layer source + block UV atlases.
No external image pixels enter authoring. Existing legacy textures stay untouched.
"""
from pathlib import Path
import json,math,uuid,base64,sys,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];D=R/'docs/art/bestiary-v40';A=R/'src/main/resources/assets/dynasty';SIDE=256
PAL={'hide':['28303d','3d4b5b','596877','7a8992'],'mane':['707d82','a4b0af','d0d4c7','e5e4cf'],'scale':['263e35','3f6250','658669','91a27a'],'belly':['777f67','a1ac85','c5cfaa','dce1c1'],'red':['542d30','7b3f39','a55643','c47953'],'horn':['5c5038','958452','c4b079','dfd1a4'],'hoof':['25282b','3b4142','555b57','767a6e'],'mouth':['291e29','56313b','915058','c17c73']}
PAL={k:[tuple(bytes.fromhex(s)) for s in v] for k,v in PAL.items()}
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def design(kind):
 parts=[]
 def box(n,parent,pivot,o,size,mat,rot=(0,0,0)):
  parts.append(dict(name=n,parent=parent,pivot=list(pivot),origin=list(o),size=list(size),material=mat,rotation=list(rot)))
 # Coordinates use Bedrock Y-up. Native export reverses Y around ground=24.
 if kind=='nian_beast':
  box('body','root',(0,19,0),(-7,13,-8),(14,13,24),'hide')
  box('hind','body',(0,20,10),(-6,13,8),(12,11,11),'hide')
  box('chest','body',(0,22,-8),(-8,11,-15),(16,17,12),'hide')
  box('neck','chest',(0,24,-12),(-6,20,-21),(12,11,11),'mane')
  box('head','neck',(0,25,-18),(-7,19,-28),(14,12,12),'hide')
  box('snout','head',(0,23,-26),(-5,19,-34),(10,6,8),'hide')
  box('jaw','head',(0,20,-27),(-5,17,-33),(10,3,7),'mouth')
  for s in (-1,1):
   tag='left' if s==1 else 'right'
   box('cheek_'+tag,'head',(s*6,23,-23),(s*6-2,18,-25),(4,11,9),'mane')
   box('ear_'+tag,'head',(s*6,29,-21),(s*6-2,28,-23),(4,5,3),'hide',(-8,0,s*16))
   box('horn_'+tag,'head',(s*5,29,-23),(s*5-1,29,-25),(2,7,3),'horn',(-25,0,-s*18))
   box('fang_'+tag,'head',(s*4,20,-31),(s*4-1,16,-33.5),(2,5,2),'horn')
  box('mane','neck',(0,25,-13),(-8,16,-16),(16,16,7),'mane')
  box('tail','hind',(0,21,17),(-2,19,16),(4,4,10),'hide',(-12,0,8))
  box('tail_tuft','tail',(0,21,25),(-3,18,23),(6,6,7),'mane')
  for front in (True,False):
   for s in (-1,1):
    n=('leg_front_' if front else 'leg_back_')+('left' if s==1 else 'right');x=s*(6 if front else 5);z=-10 if front else 12
    box(n+'_upper','chest' if front else 'hind',(x,19,z),(x-3,7,z-3),(6,13,7),'hide',(5 if front else -12,0,0))
    box(n+'_lower',n+'_upper',(x,8,z),(x-2,2,z-3),(4,7,5),'hide',(-5 if front else 12,0,0))
    box(n+'_paw',n+'_lower',(x,3,z),(x-3,0,z-5),(6,4,8),'hoof')
 else:
  box('body','root',(0,15,0),(-5,12,-5),(10,9,18),'scale')
  box('hind','body',(0,15,9),(-4,11,7),(8,9,10),'scale')
  box('chest','body',(0,17,-5),(-6,10,-11),(12,13,10),'scale')
  box('neck','chest',(0,19,-9),(-3,19,-13),(6,10,6),'scale',(-16,0,0))
  box('head','neck',(0,28,-12),(-4,26,-19),(8,7,9),'scale')
  box('snout','head',(0,28,-18),(-3,26,-24),(6,4,6),'belly')
  box('jaw','head',(0,27,-18),(-3,25,-23),(6,2,6),'scale')
  box('mane','neck',(0,25,-9),(-2,17,-9),(4,14,4),'red')
  for s in (-1,1):
   tag='left' if s==1 else 'right'
   box('ear_'+tag,'head',(s*3,31,-13),(s*3-1,30,-15),(2,5,4),'scale',(0,0,s*25))
   box('antler_'+tag,'head',(s*2,32,-15),(s*2-1,32,-17),(2,7,2),'horn',(-18,0,-s*14))
   box('antler_tip_'+tag,'antler_'+tag,(s*2,38,-15),(s*2-1,37,-16),(2,5,2),'horn',(-35,0,s*15))
   box('antler_branch_'+tag,'antler_'+tag,(s*2,35,-16),(s*2-1,35,-20),(2,2,5),'horn')
  box('tail','hind',(0,17,15),(-1,16,14),(2,2,11),'scale',(-15,10,0))
  box('tail_tuft','tail',(0,17,24),(-2,14,23),(4,5,5),'red')
  for front in (True,False):
   for s in (-1,1):
    n=('leg_front_' if front else 'leg_back_')+('left' if s==1 else 'right');x=s*4;z=-7 if front else 11
    box(n+'_upper','chest' if front else 'hind',(x,15,z),(x-2,7,z-2),(4,9,5),'scale',(0 if front else -10,0,0))
    box(n+'_lower',n+'_upper',(x,8,z),(x-1,2,z-1),(2,7,3),'belly',(0 if front else 10,0,0))
    box(n+'_paw',n+'_lower',(x,3,z),(x-2,0,z-3),(4,3,5),'hoof')
 # Avoid identical outer planes between overlapping anatomical volumes.
 # Small authored-space offsets preserve silhouette and native integer UV size.
 for i,p in enumerate(parts):
  for axis in range(3):
   for attempt in range(12):
    moved=False
    for q in parts[:i]:
     other=[a for a in range(3) if a!=axis]
     if not all(min(p['origin'][a]+p['size'][a],q['origin'][a]+q['size'][a])-max(p['origin'][a],q['origin'][a])>0.01 for a in other):continue
     for pa in (0,1):
      for qa in (0,1):
       if abs(p['origin'][axis]+pa*p['size'][axis]-q['origin'][axis]-qa*q['size'][axis])<1e-5:
        p['origin'][axis]+= -.125 if pa==0 and qa==1 else .125
        moved=True;break
      if moved:break
     if moved:break
    if not moved:break
 return parts

def paint(size,mat,name,face):
 w,h=size;p=PAL[mat];im=Image.new('RGB',(w,h),p[1]);d=ImageDraw.Draw(im)
 # Coherent upper/lower plane organization, sparse aligned clusters; no noise.
 if face=='up':d.rectangle((0,0,w-1,h-1),fill=p[2])
 elif face=='down':d.rectangle((0,0,w-1,h-1),fill=p[0])
 else:
  d.rectangle((0,max(1,h*2//3),w-1,h-1),fill=p[0]);d.rectangle((0,0,w-1,max(0,h//4-1)),fill=p[2])
 if mat in ('hide','mane','red') and w>=4 and h>=4:
  for x in range(2,w-1,5 if mat=='hide' else 3):
   y=(x//5%2)+max(1,h//3);d.line((x,y,x,min(h-2,y+3)),fill=p[2]);d.point((x-1,min(h-2,y+3)),fill=p[2])
 if mat=='scale' and face not in ('up','down'):
  for y in range(2,h-1,4):
   for x in range(1+(y//4%2)*2,w-2,5):d.line((x,y,x+2,y),fill=p[0]);d.line((x+1,y+1,x+2,y+1),fill=p[2])
 if mat=='horn':
  for y in range(2,h,4):d.line((0,y,max(0,w-1),y),fill=p[2])
 if mat=='hoof' and face=='north' and w>=4:d.line((w//2,1,w//2,h-1),fill=p[0])
 if name=='head' and face in ('east','west'):
  # Forward-facing gaze, strong brow and one bright pupil; no full-face sticker.
  x=w-3 if face=='east' else 1;y=max(1,h//3);d.rectangle((x,y,min(w-1,x+2),min(h-1,y+2)),fill=PAL['hoof'][0]);d.point((min(w-1,x+1),y+1),fill=PAL['horn'][3]);d.line((x,max(0,y-1),min(w-1,x+2),max(0,y-1)),fill=p[0])
 if name=='snout' and face=='north':
  d.rectangle((1,0,w-2,max(0,h//3)),fill=PAL['hoof'][0]);d.line((1,h-1,w-2,h-1),fill=PAL['mouth'][0])
 return im

def export(kind):
 parts=design(kind);out=D/kind;out.mkdir(parents=True,exist_ok=True);im=Image.new('RGB',(SIDE,SIDE),(25,28,29));x=y=2;row=0;bones=[{'name':'root','pivot':[0,0,0]}];java=[];records=[]
 for p in parts:
  w,h,d=p['size'];bw=2*(w+d);bh=h+d
  if x+bw+2>SIDE:x=2;y+=row+2;row=0
  assert y+bh+2<SIDE
  uv={'east':(x,y+d,d,h),'north':(x+d,y+d,w,h),'west':(x+d+w,y+d,d,h),'south':(x+d+w+d,y+d,w,h),'up':(x+d,y,w,d),'down':(x+d+w,y,w,d)}
  for f,(u,v,fw,fh) in uv.items():im.paste(paint((fw,fh),p['material'],p['name'],f),(u,v));records.append({'part':p['name'],'face':f,'rect':[u,v,fw,fh],'material':p['material']})
  c={'origin':p['origin'],'size':p['size'],'uv':{f:{'uv':[u,v],'uv_size':[fw,fh]} for f,(u,v,fw,fh) in uv.items()}}
  c['uv']['down']['uv'][1]+=d;c['uv']['down']['uv_size'][1]=-d
  b={'name':p['name'],'parent':p['parent'],'pivot':p['pivot'],'cubes':[c]}
  if any(p['rotation']):b['rotation']=p['rotation']
  bones.append(b)
  # Native model Y down. Each child local pivot relative to its actual parent.
  parent=next((q for q in parts if q['name']==p['parent']),None);pp=parent['pivot'] if parent else [0,0,0]
  px,py,pz=p['pivot'];ox,oy,oz=p['origin'];rx,ry,rz=p['rotation'];local=[px-pp[0],-(py-pp[1]),pz-pp[2]]
  if parent is None:local[1]=24-py
  def f(v):return f'{float(v):.6f}F'
  java.append(f'        part(root, "{p["parent"]}", "{p["name"]}", {x}, {y}, {", ".join(map(f,[ox-px,py-oy-h,oz-pz]))}, {w}, {h}, {d}, {", ".join(map(f,local))}, {", ".join(map(f,[math.radians(rx),math.radians(ry),math.radians(rz)]))});')
  x+=bw+2;row=max(row,bh)
 geo={'format_version':'1.12.0','minecraft:geometry':[{'description':{'identifier':'geometry.bestiary.'+kind,'texture_width':SIDE,'texture_height':SIDE,'visible_bounds_width':6,'visible_bounds_height':5,'visible_bounds_offset':[0,1,0]},'bones':bones}]}
 dump(out/'model.geo.json',geo);dump(out/'uv.json',records);dump(out/'design.json',parts)
 runtime=A/f'textures/entity/bestiary/{kind}.png';runtime.parent.mkdir(parents=True,exist_ok=True);im.save(runtime);im.save(out/'texture.png');im.resize((SIDE*3,SIDE*3),Image.Resampling.NEAREST).save(out/'texture-3x.png')
 # Neutral and walk clips mirror the native limb phasing for offline inspection.
 tracks={};times=[0,.25,.5,.75,1]
 for p in parts:
  if p['name'].endswith('_upper'):
   phase=1 if ('front_left' in p['name'] or 'back_right' in p['name']) else -1
   tracks[p['name']]={'rotation':{str(t):[math.cos(t*math.tau)*phase*math.degrees(.6),0,0] for t in times}}
   tracks[p['name'].replace('_upper','_lower')]={'rotation':{str(t):[max(0,-math.cos(t*math.tau)*phase*math.degrees(.6))*.5,0,0] for t in times}}
 anim={'format_version':'1.8.0','animations':{'animation.bestiary.idle':{'loop':True,'animation_length':2,'bones':{}},'animation.bestiary.walk':{'loop':True,'animation_length':1,'bones':tracks}}}
 dump(out/'model.animation.json',anim)
 # BB source uses the same face UVs, converted Bedrock X handedness.
 groups={};elements=[]
 def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'dynasty/bestiary40/'+kind+'/'+s))
 for b in bones:
  cp=b['pivot'];rot=b.get('rotation',[0,0,0]);groups[b['name']]={'name':b['name'],'uuid':uid(b['name']),'origin':[-cp[0],cp[1],cp[2]],'rotation':[-rot[0],-rot[1],rot[2]],'children':[]}
  for c in b.get('cubes',[]):
   o=c['origin'];s=c['size'];faces={}
   for f,t in c['uv'].items():
    u,v=t['uv'];du,dv=t['uv_size'];faces[f]={'texture':0,'uv':[u+du,v+dv,u,v] if f in ('up','down') else [u,v,u+du,v+dv]}
   ident=uid('cube/'+b['name']);elements.append({'name':b['name'],'uuid':ident,'type':'cube','from':[-o[0]-s[0],o[1],o[2]],'to':[-o[0],o[1]+s[1],o[2]+s[2]],'origin':groups[b['name']]['origin'],'faces':faces,'box_uv':False});groups[b['name']]['children'].append(ident)
 for b in bones:
  if b.get('parent'):groups[b['parent']]['children'].append(groups[b['name']])
 dump(out/(kind+'.bbmodel'),{'meta':{'format_version':'4.10','model_format':'geckolib_model','box_uv':False},'name':kind,'resolution':{'width':SIDE,'height':SIDE},'elements':elements,'outliner':[groups['root']],'textures':[{'name':kind+'.png','uuid':uid('texture'),'source':'data:image/png;base64,'+base64.b64encode(runtime.read_bytes()).decode()}]})
 return '\n'.join(java)

def main():
 definitions={k:export(k) for k in ('nian_beast','qilin')}
 source='''package com.dynasty.client;

import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import java.util.HashMap;
import java.util.Map;

/** Generated from tools/art/bestiary-v40/build.py. Native 1.20.1 block UVs. */
final class BestiaryQuadrupedLayers {
    private static final Map<String, PartDefinition> PARTS = new HashMap<>();
    private static void part(PartDefinition root, String parent, String name, int u, int v,
            float x,float y,float z,int w,int h,int d,float px,float py,float pz,float rx,float ry,float rz) {
        var base = parent.equals("root") ? root : PARTS.get(parent);
        PARTS.put(name, base.addOrReplaceChild(name, CubeListBuilder.create().texOffs(u,v).addBox(x,y,z,w,h,d),
                PartPose.offsetAndRotation(px,py,pz,rx,ry,rz)));
    }
    static LayerDefinition build(boolean nian) {
        PARTS.clear();
        var mesh = new MeshDefinition(); var root = mesh.getRoot();
        if (nian) {
'''+definitions['nian_beast']+'''
        } else {
'''+definitions['qilin']+'''
        }
        PARTS.clear(); return LayerDefinition.create(mesh,256,256);
    }
}
'''
 (R/'src/main/java/com/dynasty/client/BestiaryQuadrupedLayers.java').write_text(source)
 print('Exported original two-species rigs and native atlases')
if __name__=='__main__':main()

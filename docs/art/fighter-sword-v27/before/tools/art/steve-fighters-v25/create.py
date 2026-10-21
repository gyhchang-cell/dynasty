"""Original Steve-body combatants; runtime model definitions and pixel atlases share one source.
No external assets, server logic, hitboxes or nonhuman resources are read or replaced.
"""
from pathlib import Path
import json,math,hashlib
from PIL import Image,ImageDraw
import identity
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty';D=R/'docs/art/steve-fighters-v25'
# id, name, profession, cloth, metal, trim, scale (ordinary humans remain around player height)
SPECS=[
('archer','弓兵','bow','465b46','687e78','b79d67',.95),
('imperial_soldier','帝国士兵','soldier','304e60','70828a','bda16c',1),
('royal_guard','锦衣卫','guard','662f38','525e68','b7955c',1.03),
('rebel_soldier','叛军','rebel','66513f','62676a','a87958',.97),
('assassin','刺客','assassin','333747','535c6b','947667',.95),
('bandit_thug','山匪','bandit','624b3d','676f70','ab825b',.96),
('night_watchman','更夫','watch','364853','667580','bea66f',.96),
('zuwu_daoshou','卒伍刀手','soldier','593f39','69727c','b49a70',.98),
('ludun_jiashi','橹盾甲士','shield','384e4a','657679','a88b5c',1.04),
('juma_changqiangbing','拒马长枪兵','spear','3c4f5d','74828b','b59969',1),
('liannu_zhenzu','连弩阵卒','crossbow','514739','6a797a','b69968',.96),
('tiesuo_chihou','铁索斥候','scout','3e434c','68757d','ad8766',.96),
('kuijun_sishi','溃军死士','powder','59463c','666966','a8825c',.96),
('pijia_panjiang_huwei','披甲叛将护卫','axe','58383b','66747c','b79a65',1.10)]
CORE=[('head',[0,0,0],[-4,-8,-4],[8,8,8]),('body',[0,0,0],[-4,0,-2],[8,12,4]),('right_arm',[-5,2,0],[-3,-2,-2],[4,12,4]),('left_arm',[5,2,0],[-1,-2,-2],[4,12,4]),('right_leg',[-1.9,12,0],[-2,0,-2],[4,12,4]),('left_leg',[1.9,12,0],[-2,0,-2],[4,12,4])]
def col(h):return tuple(bytes.fromhex(h))
def shade(c,m):return tuple(max(0,min(255,round(v*m))) for v in c)
def make(spec):
 id,name,role,cloth,metal,trim,scale=spec;P={k:col(v) for k,v in dict(cloth=cloth,metal=metal,trim=trim,skin='bc9474',skinhi='d6af87',skinshadow='8c6955',hair='342d2a',ink='252d33',white='ddd5b4',leather='594634',wood='74543a',jade='6c9b8c').items()};parts=[]
 identity.palette(id,P)
 def box(n,parent,piv,origin,size,material,rot=None):parts.append(dict(name=n,parent=parent,pivot=piv,origin=origin,size=size,material=material,rotation=rot or [0,0,0]))
 for n,p,o,s in CORE:box(n,'root',p,o,s,'face' if n=='head' else 'torso' if n=='body' else 'arm' if 'arm'in n else 'leg')
 heavy=role in ('guard','shield','axe','soldier','spear');masked=role in ('assassin','scout');cap=role in ('watch','rebel','powder','bandit','bow','crossbow')
 if heavy:
  box('helmet_rim','head',[0,-6.5,0],[-4.25,-.5,-4.25],[8.5,1,8.5],'metal')
  box('helmet_cap','head',[0,-8,0],[-4.1,-.6,-4.1],[8.2,.8,8.2],'metal')
  for s in [-1,1]:box('cheek_'+str(s),'head',[s*3.5,-2.5,-3.8],[-.45,-1.8,-.3],[.9,3.6,.6],'metal',[0,0,-s*7])
 elif cap:
  box('cloth_cap','head',[0,-7.2,0],[-4.15,-.8,-4.15],[8.3,1.2,8.3],'cloth')
  box('cap_knot','head',[3.7,-5,3.7],[-.6,0,-.4],[1.2,3.3,.8],'cloth',[10,0,-12])
 else:box('hood_lip','head',[0,-6.8,-4.1],[-4,-.3,-.3],[8,.6,.6],'leather')
 for s in [-1,1]:box('brow_'+str(s),'head',[s*2,-4.9,-4.12],[-1,-.15,-.12],[2,.3,.3],'brow',[0,0,-s*(4 if role in ('bow','watch') else 7)])
 if not masked:box('nose','head',[0,-2.9,-4.12],[-.4,-.35,-.12],[.8,.7,.3],'skin')
 for s in [-1,1]:
  arm='right_arm' if s<0 else 'left_arm';cx=-1 if s<0 else 1
  if heavy or s==-1:
   box('shoulder_'+str(s),arm,[cx,-1.4,0],[-2.1,-.45,-2.25],[4.2,.9,4.5],'metal' if heavy else 'leather')
  box('cuff_'+str(s),arm,[cx,7.7,0],[-2.05,0,-2.05],[4.1,1,4.1],'metal' if heavy else 'leather')
  if heavy:box('tasset_'+str(s),'right_leg' if s<0 else 'left_leg',[0,.1,-2.1],[-1.7,0,-.25],[3.4,2.8,.5],'tasset')
 box('collar','body',[0,.4,-2.1],[-3.5,0,-.3],[7,1,.6],'collar')
 box('belt_clasp','body',[0,9.6,-2.15],[-.8,0,-.3],[1.6,1.1,.6],'trim')
 if role in ('bow','crossbow'):
  box('quiver','body',[2,2,2.2],[-1.2,0,0],[2.4,8,2.1],'quiver',[0,0,-12])
  for i in range(3):box('arrow_'+str(i),'body',[1+i*.7,1,3],[-.15,-2,0],[.3,3,.3],'white')
 elif role=='powder':box('powder_pack','body',[0,3,2.2],[-3,0,0],[6,6,3],'powder_pack')
 elif role in ('assassin','scout'):box('small_pouch','body',[-3.7,7,1],[-.7,0,0],[1.4,2.5,2],'leather')
 elif heavy:box('back_cloth','body',[0,1,2.15],[-3.5,0,0],[7,10,.35],'back_cloth')
 # Equipment is a child of its real arm; the archer uses the actual vanilla bow layer.
 if role not in ('bow','crossbow'):
  if role=='watch':
   box('lantern','left_arm',[1,10,-2.3],[-1.2,0,-1.2],[2.4,3.4,2.4],'lantern')
   box('clapper','right_arm',[-1,8,-2.6],[-.45,-3,-.4],[.9,7,.8],'wood')
  else:
   length=27 if role=='spear' else 12 if role=='axe' else 11 if role in ('guard','shield') else 6 if role in ('powder','assassin','scout') else 8
   # Sword tang is inside the grip only: no wooden shaft overlapping the blade face.
   shaft=length if role in ('spear','axe') else 2
   box('weapon_shaft','right_arm',[-1,8,-2.8],[-.45,-shaft,-.45],[.9,shaft+4,.9],'grip')
   if role=='spear':box('spear_tip','weapon_shaft',[0,-length,0],[-.7,-5,-.4],[1.4,5,.8],'blade')
   elif role=='axe':box('axe_head','weapon_shaft',[0,-length+1,0],[-4,-3,-.55],[6,5,1.1],'blade')
   else:
    box('sword_guard','weapon_shaft',[0,-2,0],[-2,-.4,-.7],[4,.8,1.4],'trim')
    box('blade','weapon_shaft',[0,-2,0],[-.8,-length,-.35],[1.6,length,.7],'blade')
 if role=='shield':box('shield','left_arm',[1,5,-3.5],[-4,-5,-1],[8,15,2],'shield')
 if role=='scout':box('chain_coil','body',[3.8,8,-2.2],[-.7,0,-.2],[1.4,2,.6],'metal')
 identity.shape(id,parts,box,P)
 # Native box UVs at 2 texels per model unit, with separate full islands per part.
 image=Image.new('RGBA',(256,256),(0,0,0,0));draw=ImageDraw.Draw(image);x=y=row=0
 for q in parts:
  w,h,d=[max(1,math.ceil(v*2)) for v in q['size']];W=2*(w+d);H=h+d
  if x+W+2>256:x=0;y+=row+2;row=0
  assert y+H<=256,(id,q['name'],y,H)
  q['uv']=[x,y];q['textureSize']=[w,h,d]
  faces={'west':(x,y+d,d,h),'north':(x+d,y+d,w,h),'east':(x+d+w,y+d,d,h),'south':(x+2*d+w,y+d,w,h),'up':(x+d,y,w,d),'down':(x+d+w,y,w,d)}
  q['faces']={}
  for f,(u,v,fw,fh) in faces.items():
   tile=paint(q['material'],f,fw,fh,P,role,id);image.paste(tile,(u,v));q['faces'][f]={'uv':[u,v],'uv_size':[fw,fh]}
  x+=W+2;row=max(row,H)
 # ModelPart rounds UV dimensions. Quantized dimensions keep 2px/unit consistent with its bake.
 for q in parts:q['size']=[n/2 for n in q['textureSize']]
 out={'id':id,'name':name,'role':role,'scale':scale,'texture_width':256,'texture_height':256,'texelScale':2,'parts':parts}
 for folder in ['models/entity/steve_fighters','textures/entity/steve_fighters']:(A/folder).mkdir(parents=True,exist_ok=True)
 (A/'models/entity/steve_fighters'/f'{id}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');image.save(A/'textures/entity/steve_fighters'/f'{id}.png')
 dd=D/id;dd.mkdir(parents=True,exist_ok=True);image.save(dd/'texture.png');image.resize((1024,1024),Image.Resampling.NEAREST).save(dd/'texture-4x.png')
 return out

def paint(mat,face,w,h,P,role,id):
 authored=identity.surface(mat,face,w,h,P,id)
 if authored is not None:return authored
 base=P.get(mat,P['cloth']);im=Image.new('RGBA',(w,h),(*base,255));d=ImageDraw.Draw(im)
 def xy(x,y):return (round(x*(w-1)/15),round(y*(h-1)/23))
 def rect(a,b,c,e,color):d.rectangle((*xy(a,b),*xy(c,e)),fill=color)
 def line(points,color):d.line([xy(*p)for p in points],fill=color,width=1)
 def poly(points,color):d.polygon([xy(*p)for p in points],fill=color)
 front=face=='north';side=face in ('west','east');up=face=='up';dark=shade(base,.73);hi=shade(base,1.16)
 if mat=='face':
  d.rectangle((0,0,w,h),fill=P['hair'])
  if front:
   rect(2,5,13,22,P['skin']);rect(2,7,2,16,P['skinshadow']);rect(13,7,13,16,P['skinshadow']);rect(4,7,11,10,P['skinhi'])
   # Two narrow eyes under a connected brow; no villager nose or cartoon smile.
   for a in (3,9):rect(a,10,a+3,11,P['hair']);rect(a,12,a+3,13,P['white']);rect(a+1,12,a+2,13,P['ink'])
   rect(7,16,8,17,P['skinshadow']);rect(6,20,9,20,P['skinshadow'])
   if role in ('assassin','scout'):rect(2,16,13,23,P['cloth']);line([(3,18),(7,19),(12,18)],shade(P['cloth'],1.2))
   elif role in ('bandit','watch','axe'):poly([(3,18),(5,20),(11,20),(13,18),(11,23),(5,23)],P['hair']);rect(6,20,10,20,P['skinshadow'])
   if role in ('powder','rebel'):line([(11,6),(10,8),(11,10)],P['skinshadow'])
   if role=='bow':rect(3,6,5,8,P['hair'])
  elif side:rect(2,9,10,19,P['skinshadow']);rect(6,10,10,15,P['skin'])
 elif mat in ('torso','arm','leg'):
  base=P['cloth'];d.rectangle((0,0,w,h),fill=base)
  if side:rect(0,0,15,23,shade(base,.8))
  if mat=='torso':
   if front:
    poly([(2,0),(7,6),(12,0),(10,0),(7,3),(4,0)],P['white']);line([(2,0),(7,7),(11,3)],P['leather']);rect(0,18,15,20,P['leather']);rect(6,18,9,20,P['trim'])
    if role in ('guard','shield','spear','soldier','axe'):
     poly([(2,7),(13,7),(13,15),(9,17),(2,15)],P['metal']);line([(3,8),(11,8)],shade(P['metal'],1.22));
     for yy in (11,14):line([(3,yy),(12,yy)],shade(P['metal'],.7))
     for xx in (5,9):line([(xx,9),(xx,15)],shade(P['metal'],.85))
     if role=='guard':line([(2,7),(7,10),(13,7)],P['trim']);poly([(6,11),(9,11),(8,15),(7,15)],shade(P['trim'],.8))
     if role=='axe':poly([(2,7),(5,7),(5,14),(3,15)],shade(base,1.12));line([(9,9),(11,11)],shade(P['metal'],.55))
     if role=='spear':line([(7,8),(7,16)],P['leather'])
    elif role in ('bow','crossbow','scout'):poly([(1,0),(4,0),(14,17),(11,18)],P['leather']);line([(3,2),(12,16)],P['trim'])
    elif role=='powder':rect(2,8,13,15,P['leather']);line([(3,9),(12,9)],P['trim'])
    else:line([(10,7),(10,16)],shade(base,.65));line([(4,21),(4,23)],shade(base,1.2))
   elif face=='south':line([(4,2),(4,16)],shade(base,.7));rect(0,18,15,20,P['leather'])
  elif mat=='arm':
   rect(0,19,15,23,P['skin']);rect(0,15,15,18,P['leather']);line([(2,5),(2,12)],shade(base,.7));line([(4,1),(10,1)],shade(base,1.15))
   if front and role in ('guard','shield','axe','spear','soldier'):rect(2,3,13,11,P['metal']);line([(3,4),(11,4)],shade(P['metal'],1.2));line([(3,9),(11,9)],shade(P['metal'],.7))
  else:
   rect(0,17,15,23,P['leather']);rect(0,22,15,23,P['ink']);line([(3,1),(3,14)],shade(base,.75))
   if front:line([(2,18),(12,18)],P['trim']);line([(6,4),(6,13)],shade(base,1.12))
 elif mat=='brow':d.rectangle((0,0,w,h),fill=P['hair'])
 elif mat=='collar':d.rectangle((0,0,w,h),fill=P['leather']);line([(1,3),(7,18),(14,3)],P['trim'])
 elif mat in ('metal','tasset'):
  base=P['metal'];d.rectangle((0,0,w,h),fill=shade(base,.85) if face=='down' else base)
  if front or side:line([(1,2),(10,2)],shade(base,1.26));line([(1,19),(12,19)],shade(base,.65));line([(11,8),(13,6)],shade(base,1.1))
 elif mat=='blade':
  d.rectangle((0,0,w,h),fill=P['metal']);rect(0,0,3,23,shade(P['metal'],1.55));rect(12,0,15,23,shade(P['metal'],.6));line([(3,4),(5,6)],P['white']);line([(3,18),(4,17)],P['white'])
 elif mat in ('quiver','powder_pack','shield','wood','grip'):
  base=P['wood'] if mat in ('wood','shield') else P['leather'];d.rectangle((0,0,w,h),fill=base)
  if not up:
   for xx in ([4,10] if mat in ('wood','shield') else [3]):line([(xx,2),(xx,14),(xx+1,22)],shade(base,.7))
   for yy in ([3,19] if mat!='grip' else [4,10,16,22]):line([(0,yy),(15,yy)],P['metal'] if mat=='shield' else shade(base,1.3))
   if mat=='shield' and front:poly([(6,6),(9,6),(11,12),(8,17),(4,12)],P['metal']);line([(6,7),(9,7)],P['trim'])
 elif mat=='lantern':
  d.rectangle((0,0,w,h),fill=P['wood']);rect(3,4,12,20,P['trim']);rect(5,7,10,17,P['white']);line([(7,3),(7,21)],P['wood'])
 elif mat=='back_cloth':
  d.rectangle((0,0,w,h),fill=shade(P['cloth'],.85));line([(3,2),(3,20)],P['cloth']);line([(12,2),(12,20)],shade(P['cloth'],.65));line([(1,21),(14,21)],P['trim'])
 else:
  if side or face=='down':d.rectangle((0,0,w,h),fill=dark)
  elif front:line([(2,2),(10,2)],hi)
 return im

def main():
 D.mkdir(parents=True,exist_ok=True);owner=D/'export-owner.json'
 if owner.exists():
  for rel,h in json.loads(owner.read_text()).items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==h,rel
 entries=[make(s) for s in SPECS];paths=[p for e in entries for p in [A/'models/entity/steve_fighters'/(e['id']+'.json'),A/'textures/entity/steve_fighters'/(e['id']+'.png')]]
 owner.write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},indent=2)+'\n')
 (D/'targets.json').write_text(json.dumps([{'id':e['id'],'name':e['name'],'role':e['role'],'scale':e['scale'],'parts':len(e['parts'])}for e in entries],ensure_ascii=False,indent=2)+'\n')
 print('Exported',len(entries),'original human combatants')
if __name__=='__main__':main()

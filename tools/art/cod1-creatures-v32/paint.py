"""Original, component-directed pixel atlases for the existing nine cod1 elite rigs.
Only UV and texture size change. Old 16px swatches are retained for tools/effects.
Called by each authoritative exporter after it writes the original geometry.
No imported images, randomness, PBR, new bones, combat edits or weapon redesign.
"""
from pathlib import Path
import json,math,copy,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];A=R/'src/main/resources/assets/dynasty'
SPECS={
'gudu_tianzhunv':('蛊毒天蛛女','generate_spider_woman.py',{'tianzhu_brood'},'蛛壳、腹纹与毒囊，骨白面部；保留混合体结构'),
'yinyang_liandan_fangshi':('阴阳炼丹方士','generate_alchemist.py',{'alchemist_cast_orb'},'铜炉、瓷面、焦紫封布与双温炉口'),
'fubo_xunhai_yecha':('伏波巡海夜叉','generate_tide_yasha.py',{'yasha_tidal_vortex'},'深海甲壳、腹板、关节与琥珀眼'),
'banshan_jiazhou_shikuang':('搬山甲胄尸狂','generate_rage_corpse.py',set(),'棺木、束尸布、死灰肌肉与内部血门'),
'mojia_jueying_cike':('墨家绝影刺客','generate_ink_assassin.py',{'assassin_ink_bamboo_anchor','assassin_finite_ink_cloud'},'折帛墨翼、竹橇、铁滑轨与墨核'),
'hanshan_tongjia_juyuan':('撼山铜甲巨猿','generate_bronze_gorilla.py',{'gorilla_cast_boulder','gorilla_stone_fragment'},'顺向黑毛、古铜背甲、掌节与猿面'),
'qingdeng_panguan_guichai':('青灯判官鬼差','generate_lamp_judge.py',{'judge_falling_pen','judge_ink_stroke','judge_chain_cage'},'紫封铁册、纸页断层、独眼、青灯与墨盂'),
'liefeng_jindiao_yushi':('烈风金雕羽士','generate_golden_eagle.py',{'eagle_finite_gold_arrow'},'深褐覆羽、金褐飞羽、淡颈羽与鹰目'),
'zhenmu_suanni_tonghou':('镇墓狻猊铜吼','generate_bronze_suanni.py',{'suanni_fixed_flame_jet','suanni_ground_fire_crack'},'古铜狮壳、暗铁风箱、炉芯与趾部接触面')}
PALETTES={
'copper':['453d36','755c44','a48052','c4a573'],
'iron':['242e34','3d4a50','63747b','8d9da1'],
'wood':['32231e','553a2d','80573b','a17b50'],
'linen':['6d6758','a39a7c','c9bea0','e4d9bb'],
'porcelain':['777c76','a9aea1','d9dbcb','eeeadd'],
'purple':['242031','3c2d47','5b4262','7b5b7e'],
'fur':['222c2b','34413b','53604e','7a8064'],
'skin':['3c4140','5b6860','86917b','acb69b'],
'chitin':['182f36','244f58','3a7277','67a09b'],
'spider':['25232f','413443','69535e','987080'],
'blood':['302731','593843','854451','aa6570'],
'ink':['17282c','283b3e','435b58','72887b'],
'paper':['6e7769','a3ab8c','cbd0ac','e0dec1'],
'bamboo':['333d2d','59613d','859065','b3bd8b'],
'feather':['3b3027','6d4e32','a67b46','c6a365'],
'pale_feather':['786e52','aa9b71','d5c696','e6dbb1'],
'jade':['193b3c','2c6664','65a59b','bad4bd'],
'fire':['3e3030','85472c','c77b3b','e4ba68'],
'eye':['352f24','7b6b3c','c1ad63','e3d8a0'],
'stone':['343e3c','505e58','7d8b7d','a5ad96']}
PAL={k:[tuple(bytes.fromhex(c))for c in cols]for k,cols in PALETTES.items()}
def path(id,kind):return A/({'geo':'geo/blueprint/elite','texture':'textures/entity/blueprint/elite','anim':'animations/blueprint/elite'}[kind])/(id+{'geo':'.geo.json','texture':'.png','anim':'.animation.json'}[kind])
def category(id,n,j,c):
 """Individual anatomical/material ownership; none is inferred from random colour choice."""
 if id=='gudu_tianzhunv':
  if n=='face':return ('porcelain','face') if j==0 else ('blood','eye') if j in (1,2) else ('porcelain','jaw')
  if 'hair' in n:return 'ink','hair'
  if n=='venom_sac':return 'jade','sac'
  if n=='abdomen':return 'spider','abdomen'
  if any(t in n for t in ['pelvis','waist','chest','neck','hand','arm']):return 'porcelain','skin'
  return 'spider','leg' if 'leg' in n else 'shell'
 if id=='yinyang_liandan_fangshi':
  if n.startswith(('whisk','gold')):return None,None # existing held implements unchanged
  if n=='alchemical_core':return ('jade','core') if j==0 else ('copper','seal')
  if n=='mask':return ('porcelain','mask') if j!=4 else ('copper','nose')
  if n=='warm_port':return 'fire','core'
  if n=='cold_port':return 'jade','core'
  if 'cloak' in n:return 'purple','cloth'
  if n in ('furnace','cradle'):return ('copper','cast') if j not in (5,6,7) else ('iron','interior')
  if 'knee' in n or n.startswith('furnace_foot') and j==1:return 'iron','hinge'
  if n=='lid' and j==0:return 'iron','case'
  return 'copper','cast'
 if id=='fubo_xunhai_yecha':
  if n in ('trident','planted_trident'):return None,None
  if n.endswith('eye'):return ('iron','socket') if j==0 else ('eye','eye')
  if n=='belly':return 'linen','belly'
  if 'vent' in n:return 'jade','vent'
  if n=='mandible':return 'porcelain','jaw'
  if n in ('fork_hinge','fork_foresegment','fork_clamp'):return 'iron','hinge'
  if 'knee' in n:return 'iron','hinge'
  return 'chitin','shell' if 'leg' not in n else 'leg'
 if id=='banshan_jiazhou_shikuang':
  if 'blade' in n:return None,None
  if 'linen' in n:return 'linen','cloth'
  if 'chain' in n or 'socket' in n:return 'iron','hinge'
  if 'eye' in n:return ('iron','socket') if j==0 else ('jade','eye')
  if 'blood' in n:return ('iron','gate') if j==0 else ('blood','core')
  if n=='coffin_shell':return ('wood','coffin') if j in (0,1,2,3) else ('iron','band')
  if n=='stitched_viscera':return ('blood','viscera') if j==0 else ('linen','stitch')
  if n=='death_mud':return 'ink','pool'
  return 'skin','muscle'
 if id=='mojia_jueying_cike':
  if 'dagger' in n:return None,None
  if n=='ink_heart':return 'jade','core'
  if n=='front_ink_slot':return 'paper','eye'
  if 'skid' in n:return 'bamboo','beam'
  if 'wing' in n or 'fold' in n:return ('paper','crease') if j==2 else ('ink','fold')
  if 'tail' in n:return 'ink','cloth'
  if n=='death_wash':return 'ink','pool'
  return 'iron','case'
 if id=='hanshan_tongjia_juyuan':
  if n=='broken_bronze_pile':return None,None
  if n=='held_rock':return 'stone','rock'
  if n=='ape_skull':
   if j in (5,7):return 'eye','eye'
   if j in (3,4):return 'skin','muzzle'
   return ('copper','brow') if j in (1,2) else ('fur','facefur')
  if n=='ape_jaw':return ('skin','muzzle') if j==0 else ('linen','tooth')
  if 'plate' in n:return 'copper','plate'
  if n=='ribcage':return ('fur','coat') if j in (0,1,4) else ('copper','plate')
  if 'knuckle' in n:return ('copper','knuckle') if j<4 else ('fur','coat')
  if 'arm' in n:return ('fur','coat') if j==0 else ('copper','plate')
  return 'fur','coat'
 if id=='qingdeng_panguan_guichai':
  if n in ('judgment_brush','broken_brush_tip'):return None,None
  if 'butterfly' in n:return 'paper','pages'
  if 'pages' in n:return ('paper','pages') if j==0 else ('ink','writing')
  if 'ledger' in n:return ('purple','book') if j<2 else ('iron','hinge')
  if 'ribbon' in n:return 'purple','ribbon'
  if n=='judicial_eye':return [('iron','socket'),('porcelain','sclera'),('jade','pupil')][j]
  if n=='green_lamp':return ('iron','case') if j==0 else ('jade','core')
  if n=='inkstone':return ('stone','basin') if j<5 else ('ink','pool')
  return 'iron','hinge'
 if id=='liefeng_jindiao_yushi':
  if any(t in n for t in ['bow','string','arrow']):return None,None
  if n=='raptor_skull':
   return ('iron','socket') if j in (2,4) else ('eye','eye') if j in (3,5) else ('pale_feather','facefeather')
  if n=='hooked_beak':return 'copper','beak'
  if 'talon' in n or 'hock' in n:return 'copper','claw'
  if n=='raptor_neck':return 'pale_feather','feather'
  if 'outer_wing' in n:return ('feather','flight') if j%2 else ('pale_feather','flight')
  return 'feather','feather'
 if id=='zhenmu_suanni_tonghou':
  if n=='stone_fire_core':return 'fire','core'
  if n=='hollow_furnace':return ('copper','cast') if j<10 else ('iron','interior')
  if 'bellows' in n:return 'iron','bellows'
  if n=='lion_head':
   if j in (4,8):return 'fire','eye'
   if j in (3,7):return 'iron','socket'
   if j in (6,10):return 'linen','tooth'
   if j==2:return 'iron','nose'
   return 'copper','lionface'
  if 'mane' in n:return 'copper','mane'
  if 'ball' in n:return 'stone','rock'
  if 'shin' in n:return 'iron','hinge'
  return 'copper','cast'
 raise ValueError(id)
CORNERS={'north':[(0,1,0),(1,1,0),(1,0,0),(0,0,0)],'south':[(1,1,1),(0,1,1),(0,0,1),(1,0,1)],'west':[(1,1,0),(1,1,1),(1,0,1),(1,0,0)],'east':[(0,1,1),(0,1,0),(0,0,0),(0,0,1)],'up':[(0,1,1),(1,1,1),(1,1,0),(0,1,0)],'down':[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]}
def worldpixel(c,f,x,y,w,h):
 cs=CORNERS[f];u=(x+.5)/w;v=(y+.5)/h
 p=[(1-u)*(1-v)*cs[0][k]+u*(1-v)*cs[1][k]+u*v*cs[2][k]+(1-u)*v*cs[3][k]for k in range(3)]
 return [c['origin'][k]+p[k]*c['size'][k]for k in range(3)]
def tile(id,n,j,c,f,w,h,mat,role):
 p=PAL[mat];im=Image.new('RGBA',(w,h),p[2]);d=ImageDraw.Draw(im)
 axis=max(range(3),key=lambda k:c['size'][k]);base=1 if f=='down' or role in ('interior','hinge','socket','pool') else 2
 # Direction is model-space: adjacent cubes continue the same fur/wood/feather flow.
 for y in range(h):
  for x in range(w):
   X,Y,Z=worldpixel(c,f,x,y,w,h);v=base
   if mat in ('wood','bamboo'):
    along=[X,Y,Z][axis];across=[Y,Z,X][axis]
    if int(across)%7==0 and int(along)%17<12:v=1
    if mat=='bamboo' and int(along)%11 in (0,1):v=1
    if (f in ('up','down')and axis==1) or (f in ('north','south')and axis==2) or (f in ('east','west')and axis==0):
     v=1 if int(max(abs(X),abs(Z),abs(Y)))%4==0 else 2
   elif mat=='fur':
    # Sparse tapered fur clusters descend limbs and sweep backwards on torso.
    t=Z if role in ('coat','facefur') and n in ('ribcage','haunch') else -Y
    s=X if f in ('north','south','up','down')else Z
    k=int(s)//3;q=int(t)%9
    if q in (0,1) and int(s+k)%7<2:v=1
    elif q==2 and int(s+k)%7==1:v=3
   elif mat in ('feather','pale_feather'):
    t=abs(X) if 'wing' in n else Z if 'tail' in n else -Y
    s=Z if 'wing' in n else X
    # Broad vane tiers with a quiet narrow shaft; no random patches.
    if int(t)%10 in (0,1):v=1
    elif int(s)%8==0:v=3
    if role=='flight' and int(t)%10>=8:v=1
   elif mat=='chitin':
    # Body plating grows tailward; limbs use joint-facing bands.
    t=Z if role=='shell' else Y
    if int(t)%10 in (0,1):v=1
    if f=='up'and int(t)%10==2:v=3
   elif mat=='spider':
    if role=='abdomen':
     # Continuous chevrons across the actual abdominal surface.
     dist=abs(X);band=int(Z+dist*.65)%18
     if band in (0,1,2):v=1
     elif band==3:v=3
    elif role=='leg' and int(Y)%14==0:v=1
   elif mat in ('purple','linen','paper'):
    if role=='pages':v=1 if int(Y)%3==0 else 2
    elif role=='book':
     if f in ('north','south')and abs(X)>7 and int(Y)%17 in (0,1):v=1
    elif role=='cloth'and int(X)%7==0:v=1
    elif role=='ribbon':v=3 if int(X)%7==0 else 2
    elif mat=='linen'and role=='cloth'and int(Y+Z*.5)%8==0:v=1
   elif mat=='copper':
    # Cast mass: limited upper lip, dark underside. Not every box gets an outline.
    if f=='up':v=3 if role in ('brow','knuckle','mane') else 2
    elif y<1 and role in ('plate','cast') and h>=6:v=3
    elif y>=h-2 and role in ('plate','cast','knuckle'):v=1
    if role in ('cast','plate') and f in ('north','south')and abs(int(X))%19==0 and int(Y)%21<4:v=1
   elif mat=='iron':
    if role=='bellows':v=1 if int(Y)%4<2 else 2
    elif role=='gate':v=0 if int(X)%4<2 else 2
    elif f=='up'and role!='interior':v=2
   elif mat=='skin':
    if role=='muscle'and int(Y)%15 in (0,1)and abs(X)>8:v=1
    if role=='muzzle'and f=='north'and abs(X)<2:v=1
   elif mat=='stone':
    if role=='basin'and f=='up':v=1
    elif int(Y)%12==0 and abs(int(X))%13<4:v=1
   elif mat=='blood':
    v=1 if role=='viscera' else 2
    if f=='up'and role=='core':v=3
   elif mat=='ink':
    if role in ('fold','cloth')and f in ('north','south','up'):
     if int(X+Z*.5)%19 in (0,1):v=1
    elif role=='hair'and int(X)%5==0:v=1
   elif role in ('core','sac'):
    if abs(x-w//2)<=max(1,w//5):v=3
    if f=='down':v=1
   # Character-specific relief, aligned in object space rather than per-box frames.
   if id=='hanshan_tongjia_juyuan' and mat=='copper' and 'chest_plate' in n and j==0:
    if f in ('north','south'):
     chevron=int(Y-abs(X)*.35)
     if chevron in (24,25):v=1
     elif chevron==26:v=3
   if id=='fubo_xunhai_yecha' and mat=='chitin' and role=='shell':
    # Overlapping carapace plates; broad clean fields between the staggered seams.
    tier=math.floor(Z/8);across=(int(X)+4*(tier%2))%12
    if int(Z)%8==0 and across in range(2,10):v=1
    elif int(Z)%8==1 and across in range(3,9):v=3
   if id=='zhenmu_suanni_tonghou' and mat=='copper' and role=='lionface':
    if n=='lion_head' and j==0 and f in ('east','west'):
     # One cast cheek curl, quiet elsewhere, no texture-only fake opening.
     if int(Y) in (26,27) and int(Z) in range(-22,-16):v=1
     if int(Y)==28 and int(Z) in range(-20,-16):v=3
   if id=='yinyang_liandan_fangshi' and mat=='copper' and n=='furnace':
    if f in ('north','south') and abs(X) in range(4,7) and int(Y)%12 in (3,4,5):v=1
   if id=='hanshan_tongjia_juyuan' and mat=='copper' and any(t in n for t in ('forearm','knuckles')):
    # Overlapping bronze cuffs share model-space tones, not independent box borders.
    v=3 if f=='up' else 1 if Y<2 else 2
   im.putpixel((x,y),p[v])
   # Existing hair overlaps the same planes as the skull. Match the hidden scalp
   # pixels to the hair so these approved surfaces do not produce pale z-fighting.
   if id=='gudu_tianzhunv' and n=='face' and j==0 and (f in ('south','up') or f=='north' and Y>=29):
    im.putpixel((x,y),PAL['ink'][1 if int(X)%5==0 else 2])
 if role in ('eye','pupil'):
  # Looking direction: bright outer iris and a defined vertical pupil, not an emissive square.
  d.rectangle((max(0,w//2-1),max(0,h//5),min(w-1,w//2),max(0,h*4//5)),fill=p[0])
  if w>=4 and h>=3:d.point((max(0,w//2-2),max(0,h//4)),fill=p[3])
 if role in ('mask','face') and f=='north'and w>=5 and h>=5:
  d.line((1,h//3,max(1,w//3),h//3+1),fill=p[0]);d.line((w*2//3,h//3+1,w-2,h//3),fill=p[0])
 if role=='book'and f in ('north','south')and w>=8 and h>=10:
  # Simple sealed court ledger ruling, original marks without a new faction crest.
  xx=w//3;d.line((xx,h//4,xx,h*3//4),fill=p[1])
  for yy in [h//3,h//2,h*2//3]:d.line((xx+1,yy,min(w-2,xx+3),yy),fill=p[3])
 return im

def topology(g):
 q=copy.deepcopy(g);d=q['minecraft:geometry'][0]['description'];d.pop('texture_width',None);d.pop('texture_height',None)
 for b in q['minecraft:geometry'][0]['bones']:
  for c in b.get('cubes',[]):c.pop('uv',None)
 return q

def finish(id):
 gp=path(id,'geo');tp=path(id,'texture');g=json.loads(gp.read_text());desc=g['minecraft:geometry'][0]['description']
 if desc['texture_width']!=16:return # A re-export first writes its 16px source again.
 old=copy.deepcopy(g);tex=Image.open(tp).convert('RGBA');original=tex.copy();records=[]
 for b in g['minecraft:geometry'][0]['bones']:
  for j,c in enumerate(b.get('cubes',[])):
   mat,role=category(id,b['name'],j,c)
   if mat is None:continue
   for f in CORNERS:
    dims={'north':(0,1),'south':(0,1),'west':(2,1),'east':(2,1),'up':(0,2),'down':(0,2)}[f]
    w,h=[max(1,math.ceil(c['size'][a]))for a in dims]
    records.append({'bone':b['name'],'index':j,'face':f,'material':mat,'role':role,'w':w,'h':h,'cube':c})
 # Height-sorted shelves, integer pixel coordinates; one model unit per texel.
 for size in [128,256,512,1024]:
  x=0;y=18;row=0;ok=True
  for rec in sorted(records,key=lambda r:(-r['h'],-r['w'])):
   w,h=rec['w'],rec['h']
   if x+w+2>size:x=0;y+=row+2;row=0
   if w+2>size or y+h+2>size:ok=False;break
   rec['xy']=(x+1,y+1);x+=w+2;row=max(row,h)
  if ok:break
 else:raise AssertionError('Atlas cannot fit '+id)
 atlas=Image.new('RGBA',(size,size),(0,0,0,0));atlas.paste(tex,(0,0));islands=[]
 for rec in records:
  x,y=rec['xy'];w,h=rec['w'],rec['h'];c=rec['cube'];f=rec['face']
  painted=tile(id,rec['bone'],rec['index'],c,f,w,h,rec['material'],rec['role']);atlas.paste(painted,(x,y));c['uv'][f]={'uv':[x,y],'uv_size':[w,h]}
  # Extrude a pixel into the gutter, without sharing any UV area.
  atlas.paste(painted.crop((0,0,w,1)),(x,y-1));atlas.paste(painted.crop((0,h-1,w,h)),(x,y+h));atlas.paste(painted.crop((0,0,1,h)),(x-1,y));atlas.paste(painted.crop((w-1,0,w,h)),(x+w,y))
  islands.append({k:v for k,v in rec.items()if k not in ('cube','xy')}|{'rect':[x,y,w,h]})
 desc.update(texture_width=size,texture_height=size);assert topology(g)==topology(old)
 gp.write_text(json.dumps(g,indent=2)+'\n');atlas.save(tp)
 # Several existing projectile renderers share this character's PNG. Retain their 16px
 # swatches and adjust only the scale declaration so their UVs sample the same pixels.
 for aux in SPECS[id][2]:
  p=path(aux,'geo')
  if p.exists():
   data=json.loads(p.read_text());data['minecraft:geometry'][0]['description'].update(texture_width=size,texture_height=size);p.write_text(json.dumps(data,indent=2)+'\n')
 dead=tp.with_name(id+'_dead.png')
 if dead.exists():
  from PIL import ImageChops
  # Keep a readable dead surface, quieting actual core/eye pixels rather than blanking armour.
  dim=atlas.copy()
  for r in islands:
   if r['role'] in ('core','eye','pupil','sac'):
    x,y,w,h=r['rect'];patch=dim.crop((x,y,x+w,y+h));patch=patch.point(lambda v:int(v*.62))
    alpha=Image.new('L',patch.size,255);patch.putalpha(alpha);dim.paste(patch,(x,y))
  dim.save(dead)
 D=R/'docs/art/cod1-creatures-v32'/id;D.mkdir(parents=True,exist_ok=True)
 if not (D/'before.geo.json').exists():(D/'before.geo.json').write_text(json.dumps(old,indent=2)+'\n')
 atlas.save(D/'texture.png');atlas.resize((size*2,size*2),Image.Resampling.NEAREST).save(D/'texture-2x.png');original.save(D/'before-texture.png')
 (D/'islands.json').write_text(json.dumps(islands,ensure_ascii=False,indent=2)+'\n')
 (D/'changes.json').write_text(json.dumps({'id':id,'name':SPECS[id][0],'focus':SPECS[id][3],'geometryRigAndAnimationsPreserved':True,'textureSize':size,'faceIslands':len(records),'legacyToolAndEffectPixelsPreserved':True,'source':SPECS[id][1]},ensure_ascii=False,indent=2)+'\n')
 print(id,size,len(records))
if __name__=='__main__':
 import sys
 for id in sys.argv[1:]or SPECS:finish(id)

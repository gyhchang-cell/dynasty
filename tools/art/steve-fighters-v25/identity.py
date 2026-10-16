"""Original per-identity facial drawing and equipment shapes; no imported character art."""
from PIL import Image,ImageDraw
SKINS={'fufa_jijiu':'b9a181','archer':'cea47c','imperial_soldier':'aa7858','royal_guard':'dcc0a0','rebel_soldier':'b48b65','assassin':'a98872','bandit_thug':'996d4f','night_watchman':'b49a7b','zuwu_daoshou':'c39576','ludun_jiashi':'a3866a','juma_changqiangbing':'bca087','liannu_zhenzu':'c3aa8d','tiesuo_chihou':'a97a58','kuijun_sishi':'d0ad8b','pijia_panjiang_huwei':'a77f66'}
DESCRIPTIONS={'fufa_jijiu':'灰眉长须、道冠与额玉；暗紫交领、双条法衣、腰侧符袋，右手朱符。无领域或装饰粒子。','archer':'短发露面、松眉窄眼；绿兜帽、单肩皮护与斜挂箭袋','imperial_soldier':'护鼻铁盔、方颌；青灰整胸甲与横向腰封','royal_guard':'高冠、白面短髭；暗朱交领、窄金绣边与护肩','rebel_soldier':'露额布带、独眼伤面；旧布衣和单侧补甲','assassin':'黑兜头、窄眼裂、整片口鼻蒙布；贴身无亮甲','bandit_thug':'秃额、宽鼻、络腮胡；敞领皮背心与粗肩革','night_watchman':'灰鬓、下垂细眉、两撇灰须；短褂、腰绳和灯具','zuwu_daoshou':'开面皮盔、短胡茬；单侧札甲与绑腕','ludun_jiashi':'闭合铁面、细横眼缝；横叠重甲与橹盾','juma_changqiangbing':'颈帘盔、长脸长髭；纵向札甲与肩颈防护','liannu_zhenzu':'额部镜片、下脸围巾；皮护胸与绗缝弩衣','tiesuo_chihou':'单眼布带、斜裹面巾；非对称短披与铁索腰具','kuijun_sishi':'白色额带、青年无须面；绑带布甲、药包和短刃','pijia_panjiang_huwei':'暗朱铁鬼面、压眼盔；兽吞肩甲、阶梯铜镜与叠札重甲'}
def palette(id,P):
 c=tuple(bytes.fromhex(SKINS[id]));P['skin']=c;P['skinhi']=tuple(min(255,v+22)for v in c);P['skinshadow']=tuple(max(0,v-35)for v in c)
 if id in ('night_watchman','fufa_jijiu'):P['hair']=(100,101,91)
 if id=='archer':P['hair']=(91,62,40)
 if id=='royal_guard':P['metal']=(69,73,81)

def shape(id,parts,box,P):
 # Replace the universal angry brow/nose and repeated helmet/shoulder template.
 parts[:]=[p for p in parts if not p['name'].startswith('brow_') and p['name']!='nose']
 by={p['name']:p for p in parts}
 def remove(*ns):parts[:]=[p for p in parts if p['name']not in ns]
 def b(n,parent,p,o,s,m,rot=None):box(n,parent,p,o,s,m,rot)
 if id=='fufa_jijiu':
  remove('hood_lip','shoulder_-1','cuff_-1','cuff_1')
  b('ritual_crown','head',[0,-8,0],[-3,-1.5,-3],[6,2,6],'cloth')
  b('crown_jade','head',[0,-7,-4],[-.75,-1,-.5],[1.5,2,.5],'jade')
  b('beard','head',[0,-1,-4],[-1.5,0,-.5],[3,3,.5],'brow')
  b('beard_tip','beard',[0,2,0],[-1,0,-.5],[2,2,.5],'brow')
  for side,x in [('right',-2),('left',2)]:
   b('stole_'+side,'body',[x,1,-2],[-.75,0,-.5],[1.5,10,.5],'priest_stole')
   b('robe_'+side,side+'_leg',[0,0,0],[-2,0,-2.5],[4,6,.5],'cloth')
  b('talisman_bundle','body',[4,7,0],[0,0,-1],[1.5,3,2],'priest_pouch')
  b('held_talisman','right_arm',[-1,8,-2],[-1,-2,-.5],[2,4,.5],'priest_paper')
 elif id=='archer':
  remove('cap_knot','cloth_cap');b('hood_crown','head',[0,-8,0],[-4.25,-.5,-3.75],[8.5,1,8],'cloth')
  for x in [-4,3.5]:b('hood_flap'+str(x),'head',[x,-6,0],[0,0,-3.25],[.5,6.5,7.5],'cloth')
  b('short_mantle','body',[0,1,2],[-3.5,0,0],[7,6,.5],'cloth');remove('cuff_1')
 elif id=='imperial_soldier':
  b('nasal_guard','head',[0,-6.5,-4.25],[-.5,0,-.25],[1,4.5,.5],'metal');b('breastplate','body',[0,2,-2],[-3.75,0,-.5],[7.5,6.5,.75],'cuirass')
 elif id=='royal_guard':
  remove('helmet_rim','helmet_cap','cheek_-1','cheek_1');b('court_crown','head',[0,-8,0],[-3.5,-2,-3.25],[7,2.5,6.5],'cloth');b('crown_band','head',[0,-7.5,-4],[-4.25,0,-.25],[8.5,1,.5],'trim');b('coat_lapel','body',[0,.3,-2.15],[-3.5,0,-.25],[7,4,.5],'court')
  for s in [-1,1]:b('coat_skirt'+str(s),'right_leg'if s<0 else'left_leg',[0,1,0],[-2.1,0,-2.25],[4.2,4.5,.5],'cloth')
 elif id=='rebel_soldier':
  remove('cloth_cap','cap_knot','shoulder_-1');b('head_band','head',[0,-6.3,-4],[-4.2,0,-.25],[8.4,1.5,.5],'cloth');b('patch_shoulder','left_arm',[1,-1.5,0],[-2.25,0,-2.25],[4.5,1.5,4.5],'leather');b('patch_vest','body',[-3,3,-2],[-.5,0,-.5],[3,5,.5],'patched')
 elif id=='assassin':
  for x in [-4.25,3.75]:b('cowl_side'+str(x),'head',[x,-7,0],[0,0,-4],[.5,7,8.25],'cloth')
  b('mask_fold','head',[0,-2,-4],[-4,0,-.5],[8,2.5,.5],'cloth');remove('shoulder_-1','cuff_1');b('chest_wrap','body',[0,3,-2],[-4,0,-.5],[8,2,.5],'leather')
 elif id=='bandit_thug':
  remove('cloth_cap','cap_knot');b('leather_pauldron','right_arm',[-1,-1,0],[-2.5,-.5,-2.25],[5,2,4.5],'leather');b('beard_jaw','head',[0,-1,-4],[-2.5,0,-.5],[5,1.5,.5],'brow')
 elif id=='night_watchman':
  by['cloth_cap']['size']=[8.5,2,8.5];b('short_jacket','body',[0,5,-2],[-4,0,-.5],[8,4,.5],'watchcoat');remove('shoulder_-1')
 elif id=='zuwu_daoshou':
  remove('helmet_cap','cheek_1','shoulder_1','back_cloth');by['helmet_rim']['material']='leather';b('half_lamella','body',[-3.25,2,-2],[-.25,0,-.5],[4,6.5,.5],'lamellar')
 elif id=='ludun_jiashi':
  b('closed_faceplate','head',[0,-5.8,-4],[-3.5,0,-.5],[7,5.5,.5],'shieldface');by['helmet_cap']['size']=[9,1.5,8.5]
  for j in range(3):b('breast_lame'+str(j),'body',[0,2+j*2,-2],[-4,0,-.75],[8,1.75,.75],'cuirass')
 elif id=='juma_changqiangbing':
  for x in [-4.25,3.75]:b('neck_lame'+str(x),'head',[x,-2.5,0],[0,0,-2.5],[.5,4.5,6.5],'metal')
  b('breast_lamella','body',[0,2,-2],[-3.5,0,-.5],[7,7,.5],'lamellar');b('helmet_crest','head',[0,-9,0],[-.5,-1,-2],[1,1.5,4],'metal')
 elif id=='liannu_zhenzu':
  remove('cap_knot');b('scarf_mask','head',[0,-1.5,-4],[-3.75,0,-.5],[7.5,2,.5],'cloth');b('forehead_goggles','head',[0,-5.5,-4],[-3.5,0,-.5],[7,1.5,.5],'goggles');b('leather_bib','body',[0,2,-2],[-3.5,0,-.5],[7,6,.5],'crossleather')
 elif id=='tiesuo_chihou':
  b('diagonal_wrap','head',[0,-3.5,-4],[-3.75,0,-.5],[7.5,1,.5],'cloth',[0,0,-14]);b('scout_drape','left_arm',[1,-1,1],[-2.25,0,0],[4.5,5.5,1],'cloth');remove('cuff_1')
 elif id=='kuijun_sishi':
  remove('cloth_cap','cap_knot','shoulder_-1');b('white_headband','head',[0,-6,-4],[-4.25,0,-.5],[8.5,1.5,.5],'white');b('sash','body',[0,3,-2],[-4,0,-.5],[8,1.5,.5],'white',[0,0,12])
 else:
  b('war_mask','head',[0,-5.5,-4],[-3.5,0,-.75],[7,5.5,.75],'warmask')
  # Small relief over the unchanged six Steve blocks; armour carries identity.
  by['helmet_cap']['material']='guard_iron';by['helmet_rim']['material']='guard_iron'
  b('helmet_ridge','head',[0,-8.5,0],[-1,-.5,-3.5],[2,1,7],'guard_iron')
  b('war_breast','body',[0,1.5,-2],[-4,0,-1],[8,7,1],'guard_lamella')
  # Stepped octagonal mirror, not a sphere or a painted square badge.
  b('heart_mirror','body',[0,4,-3],[-2,-1.5,-.5],[4,3,.5],'guard_mirror')
  for y in [-2,1.5]:b('mirror_step'+str(y),'body',[0,4,-3],[-1.5,y,-.5],[3,.5,.5],'guard_mirror')
  for sign in [-1,1]:
   arm='right_arm' if sign<0 else 'left_arm';cx=-1 if sign<0 else 1
   q=by['shoulder_'+str(sign)];q.update(origin=[-2.25,-.5,-2.5],size=[4.5,1.5,5],material='guard_iron')
   b('beast_pauldron'+str(sign),arm,[cx,-.5,-2.5],[-1.75,0,-.5],[3.5,2.5,.5],'guard_beast')
   b('beast_muzzle'+str(sign),arm,[cx,1,-3],[-1,0,-.5],[2,1,.5],'guard_bronze')
   by['tasset_'+str(sign)]['material']='guard_lamella'
  by['back_cloth']['material']='guard_back'


def face(id,P):
 im=Image.new('RGBA',(16,16),P['hair']);d=ImageDraw.Draw(im);s=P['skin'];hi=P['skinhi'];sh=P['skinshadow'];hair=P['hair'];ink=P['ink'];metal=P['metal'];cloth=P['cloth'];white=P['white']
 r=lambda q,c:d.rectangle(q,fill=c)
 poly=lambda q,c:d.polygon(q,fill=c)
 line=lambda q,c:d.line(q,fill=c)
 # Every branch owns the face silhouette, eye spacing, expression and exposed skin.
 if id=='fufa_jijiu':
  poly([(2,4),(13,4),(13,11),(10,15),(5,15),(2,11)],s)
  r((4,5,11,7),hi);line([(2,7),(5,6),(6,7)],white);line([(9,7),(11,6),(13,7)],white)
  r((3,8,5,8),ink);r((10,8,12,8),ink);r((7,9,8,11),sh)
  line([(2,10),(4,11)],sh);line([(13,10),(11,11)],sh)
  poly([(3,12),(6,11),(8,12),(10,11),(13,12),(10,14),(5,14)],hair)
  r((0,0,15,3),cloth);r((7,1,8,3),P['jade'])
 elif id=='archer':
  poly([(2,4),(12,3),(14,7),(12,14),(5,15),(2,11)],s);r((3,5,11,7),hi);r((3,8,5,8),hair);r((10,7,12,7),hair);r((4,9,5,9),ink);r((10,8,11,8),ink);r((7,9,8,11),sh);r((6,13,10,13),sh);poly([(2,1),(8,1),(5,6),(2,7)],hair)
 elif id=='imperial_soldier':
  r((2,4,13,13),s);r((3,5,12,7),hi);r((2,7,5,8),hair);r((10,7,13,8),hair);r((3,9,5,9),ink);r((10,9,12,9),ink);r((6,12,10,12),sh);r((3,14,12,15),hair);r((0,0,15,3),metal)
 elif id=='royal_guard':
  poly([(3,3),(12,3),(13,10),(10,15),(5,15),(2,10)],s);r((4,5,11,7),hi);line([(3,7),(5,6),(6,7)],hair);line([(9,7),(10,6),(12,7)],hair);r((4,8,5,8),ink);r((10,8,11,8),ink);r((7,9,8,11),sh);r((5,12,6,12),hair);r((9,12,10,12),hair);r((7,14,8,15),hair)
 elif id=='rebel_soldier':
  poly([(1,4),(12,3),(14,7),(12,15),(3,14)],s);r((3,6,7,8),hi);r((2,8,5,9),hair);r((3,10,4,10),ink);r((9,7,13,10),P['leather']);line([(13,6),(7,9),(1,9)],P['leather']);line([(10,11),(11,12),(10,14)],sh);r((4,13,8,13),hair)
 elif id=='assassin':
  r((2,6,13,9),s);poly([(1,5),(7,6),(14,4),(14,6),(9,8),(2,7)],cloth);r((3,8,5,8),ink);r((10,7,12,7),ink);r((0,10,15,15),cloth);line([(2,11),(8,13),(13,11)],tuple(min(255,v+20)for v in cloth))
 elif id=='bandit_thug':
  poly([(1,2),(12,1),(14,5),(14,12),(10,15),(3,14),(1,10)],s);r((2,4,11,6),hi);r((2,7,6,8),hair);r((10,6,13,7),hair);r((3,9,5,9),ink);r((10,8,12,8),ink);r((6,8,8,11),sh);poly([(1,9),(4,12),(10,12),(14,9),(13,15),(2,15)],hair);r((5,12,9,12),sh)
 elif id=='night_watchman':
  r((2,3,13,14),s);r((4,4,11,6),hi);line([(2,7),(5,8),(6,7)],hair);line([(9,7),(10,8),(13,7)],hair);r((4,9,5,9),ink);r((10,9,11,9),ink);r((7,8,8,11),sh);line([(6,12),(3,13),(3,14)],hair);line([(9,12),(12,13),(12,14)],hair);r((7,14,8,14),sh);r((1,5,2,10),hair);r((13,5,14,10),hair)
 elif id=='zuwu_daoshou':
  poly([(2,3),(12,3),(14,8),(11,15),(4,15),(1,9)],s);r((3,5,12,7),hi);r((3,8,6,8),hair);r((10,8,12,8),hair);r((4,9,5,9),ink);r((10,9,11,9),ink);r((7,10,8,11),sh);r((5,13,10,13),hair);r((4,14,5,14),sh);r((10,14,11,14),sh)
 elif id=='ludun_jiashi':
  r((1,2,14,15),metal);r((2,7,6,8),ink);r((9,7,13,8),ink);r((7,5,8,12),P['trim']);line([(2,11),(5,13),(6,14)],tuple(v//2 for v in metal));line([(13,11),(10,13),(9,14)],tuple(v//2 for v in metal))
 elif id=='juma_changqiangbing':
  poly([(3,2),(12,2),(12,12),(10,15),(5,15),(3,11)],s);r((4,5,11,6),hi);line([(3,7),(6,7)],hair);line([(9,7),(12,7)],hair);r((4,8,5,8),ink);r((10,8,11,8),ink);r((7,8,8,11),sh);line([(5,12),(3,13)],hair);line([(10,12),(12,13)],hair);r((7,13,8,15),hair)
 elif id=='liannu_zhenzu':
  r((2,4,13,13),s);r((2,6,13,8),P['leather']);r((3,6,5,7),P['jade']);r((10,6,12,7),P['jade']);r((3,9,5,9),ink);r((10,9,12,9),ink);r((7,8,8,11),sh);poly([(1,12),(8,11),(14,12),(14,15),(1,15)],cloth);line([(3,13),(8,14),(12,13)],P['leather'])
 elif id=='tiesuo_chihou':
  r((2,4,13,12),s);r((2,6,6,9),cloth);line([(1,5),(14,10)],cloth);r((10,7,12,7),ink);r((2,11,13,15),cloth);line([(3,12),(7,13),(11,12)],P['leather'])
 elif id=='kuijun_sishi':
  poly([(3,4),(13,3),(14,9),(11,15),(5,15),(2,11)],s);r((4,5,11,7),hi);line([(3,8),(5,7),(6,7)],hair);line([(9,7),(11,7),(13,8)],hair);r((4,9,5,9),ink);r((10,9,11,9),ink);r((8,10,8,11),sh);r((6,13,10,13),sh);r((0,2,15,4),white)
 else:
  r((1,3,14,15),metal);poly([(2,4),(7,6),(6,9),(2,8)],P['cloth']);poly([(13,4),(8,6),(9,9),(13,8)],P['cloth']);r((3,7,5,7),ink);r((10,7,12,7),ink);r((7,6,8,11),P['trim']);poly([(3,11),(6,12),(7,14),(5,14)],P['trim']);poly([(12,11),(9,12),(8,14),(10,14)],P['trim'])
 return im

def guard_surface(mat,face,w,h,P):
 iron=P['metal'];bronze=(151,123,72);dark=(47,55,58);bright=(158,173,175)
 base=bronze if mat in ('guard_mirror','guard_bronze') else P['cloth'] if mat=='guard_back' else iron
 im=Image.new('RGBA',(w,h),base);d=ImageDraw.Draw(im)
 def line(points,c):d.line(points,fill=c)
 if face in ('west','east','down'):
  d.rectangle((0,0,w-1,h-1),fill=tuple(int(v*.73)for v in base))
  return im
 if mat=='guard_mirror':
  # One restrained light facet across the copper shield, no bright box outline.
  if face=='north':
   d.polygon([(0,0),(w//2,0),(max(0,w//2-1),h-1),(0,h-1)],fill=(182,153,94))
   if w>4 and h>3:line([(w-2,1),(w-2,h-2)],(112,88,54))
 elif mat=='guard_beast' and face=='north':
  for x in [1,max(1,w-3)]:
   line([(x,1),(min(w-1,x+1),1)],bronze)
   line([(x,2),(min(w-1,x+1),2)],dark)
  line([(w//2,2),(w//2,h-1)],bronze)
 elif mat=='guard_lamella' and face=='north':
  for y in range(3,h,4):
   line([(0,y),(w-1,y)],dark)
   for x in range(1,w,4):
    line([(x,max(0,y-2)),(x,y-1)],(116,130,134))
  # Attachment straps on chest edges, leaving copper mirror as the focus.
  if w>10:
   for x in [1,w-2]:line([(x,0),(x,h-1)],P['leather'])
 elif mat=='guard_back':
  for x in [w//3,w*2//3]:line([(x,1),(x,h-2)],(65,39,43))
  if h>5:line([(1,h-3),(w-2,h-3)],(125,91,66))
 elif mat=='guard_iron' and face=='north':
  line([(1,0),(max(1,w-2),0)],bright)
  if h>3:line([(0,h-1),(w-1,h-1)],dark)
 return im

def surface(mat,face,w,h,P,id):
 if mat.startswith('guard_'):return guard_surface(mat,face,w,h,P)
 if mat.startswith('priest_'):
  base=P['white'] if mat=='priest_paper' else P['leather'] if mat=='priest_pouch' else P['trim']
  im=Image.new('RGBA',(w,h),base);d=ImageDraw.Draw(im)
  if face in ('north','south'):
   ink=P['cloth'];cx=w//2
   if mat=='priest_paper':
    d.line([(cx,1),(cx,max(1,h-2))],fill=ink)
    for y in [h//3,h*2//3]:d.line([(max(0,cx-1),y),(min(w-1,cx+1),y)],fill=ink)
   elif mat=='priest_stole':
    d.line([(0,0),(0,h-1)],fill=P['cloth'])
    for y in [h//3,h*2//3]:d.rectangle((max(0,w-2),y,w-1,min(h-1,y+1)),fill=ink)
   else:d.line([(0,h//3),(w-1,h//3)],fill=P['trim'])
  return im
 if id=='fufa_jijiu' and mat=='torso':
  im=Image.new('RGBA',(w,h),P['cloth']);d=ImageDraw.Draw(im)
  if face=='north':
   d.polygon([(w//4,0),(w//2,h//3),(w*3//4,0),(w*2//3,0),(w//2,h//5),(w//3,0)],fill=P['white'])
   d.rectangle((0,h*3//4,w-1,h*3//4+1),fill=P['leather'])
  elif face in ('west','east'):d.line([(w//3,2),(w//3,h-3)],fill=P['ink'])
  return im
 if mat=='face' and face=='north':return globals()['face'](id,P).resize((w,h),Image.Resampling.NEAREST)
 if mat not in ('torso','cuirass','court','lamellar','patched','watchcoat','crossleather','shieldface','warmask','warplate','goggles'):return None
 if mat=='shieldface':return globals()['face']('ludun_jiashi',P).crop((1,4,15,15)).resize((w,h),Image.Resampling.NEAREST)
 if mat=='warmask':return globals()['face']('pijia_panjiang_huwei',P).crop((1,4,15,15)).resize((w,h),Image.Resampling.NEAREST)
 if mat=='goggles':
  im=Image.new('RGBA',(w,h),P['leather']);d=ImageDraw.Draw(im)
  if face=='north':d.rectangle((1,0,max(1,w//3),max(0,h-2)),fill=P['jade']);d.rectangle((w*2//3,0,w-2,max(0,h-2)),fill=P['jade'])
  return im
 im=Image.new('RGBA',(16,24),P['cloth']);d=ImageDraw.Draw(im);r=lambda q,c:d.rectangle(q,fill=c);line=lambda q,c:d.line(q,fill=c);metal=P['metal'];shade=lambda c,f:tuple(round(v*f)for v in c)
 if mat=='torso':
  if face=='north':
   if id=='archer':r((2,3,12,18),P['leather']);d.polygon([(0,0),(3,0),(14,18),(11,19)],fill=P['trim']);r((5,0,9,4),P['skin'])
   elif id=='imperial_soldier':r((1,3,14,17),metal);r((6,0,9,3),P['ink']);line([(2,6),(13,6)],shade(metal,1.25));r((0,19,15,21),P['leather'])
   elif id=='royal_guard':d.polygon([(1,0),(6,0),(13,10),(9,12)],fill=P['trim']);d.polygon([(14,0),(10,0),(2,8),(4,10)],fill=P['white']);line([(1,15),(7,13),(13,16)],P['trim']);r((5,15,10,17),P['metal']);r((2,20,13,21),P['trim'])
   elif id=='rebel_soldier':r((6,0,9,7),P['skin']);r((1,9,6,16),P['leather']);line([(9,0),(10,18)],P['leather']);r((0,19,15,20),P['ink'])
   elif id=='assassin':d.polygon([(1,0),(4,0),(14,12),(12,14)],fill=P['leather']);r((0,17,15,20),P['leather']);line([(5,4),(6,14)],shade(P['cloth'],1.25))
   elif id=='bandit_thug':r((4,0,10,12),P['skin']);d.polygon([(0,0),(4,0),(5,17),(0,18)],fill=P['leather']);d.polygon([(11,0),(15,1),(15,18),(10,17)],fill=P['leather']);r((0,18,15,21),P['leather'])
   elif id=='night_watchman':r((5,0,10,3),P['white']);line([(8,4),(8,17)],P['ink']);r((0,19,15,19),P['trim']);r((8,6,9,6),P['trim']);r((8,11,9,11),P['trim'])
   elif id=='zuwu_daoshou':r((0,3,6,16),metal);d.polygon([(9,1),(12,1),(5,18),(2,18)],fill=P['leather']);r((0,20,15,21),P['leather'])
   elif id=='ludun_jiashi':r((0,2,15,17),metal);r((6,0,9,2),P['ink']);r((0,19,15,22),P['leather'])
   elif id=='juma_changqiangbing':r((1,2,14,18),metal);r((7,2,8,18),P['leather']);r((0,20,15,22),P['leather'])
   elif id=='liannu_zhenzu':r((2,3,13,17),P['leather']);line([(2,6),(12,6)],P['trim']);line([(3,12),(12,12)],shade(P['leather'],1.25));r((0,20,15,21),P['ink'])
   elif id=='tiesuo_chihou':d.polygon([(0,0),(3,0),(13,15),(11,17)],fill=P['leather']);r((10,12,14,18),metal);r((0,20,15,21),P['leather'])
   elif id=='kuijun_sishi':r((0,10,15,12),P['leather']);d.polygon([(1,0),(3,0),(14,17),(12,19)],fill=P['white']);r((0,20,15,21),P['leather'])
   else:r((0,3,15,17),metal);d.polygon([(0,3),(5,3),(7,16),(0,17)],fill=P['cloth']);line([(11,7),(13,9),(10,12)],P['ink']);r((0,20,15,22),P['trim'])
  elif face in ('west','east'):r((0,0,15,23),shade(P['cloth'],.8));line([(5,3),(5,16)],P['cloth'])
  elif face=='south':line([(5,1),(5,17)],shade(P['cloth'],.7));r((0,20,15,21),P['leather'])
 else:
  base=metal if mat in ('cuirass','lamellar','warplate')else P['cloth']if mat in ('court','watchcoat')else P['leather'];r((0,0,15,23),base)
  if face=='north':
   if mat=='cuirass':line([(1,2),(13,2)],shade(metal,1.25));line([(1,20),(14,20)],shade(metal,.65))
   elif mat=='lamellar':
    for x in [3,7,11]:line([(x,2),(x,20)],shade(metal,.65));line([(x+1,3),(x+1,8)],shade(metal,1.18))
    for y in [9,17]:line([(1,y),(14,y)],P['leather'])
   elif mat=='court':d.polygon([(1,0),(5,0),(14,19),(11,22)],fill=P['trim']);d.polygon([(14,0),(10,0),(1,12),(3,15)],fill=P['white'])
   elif mat=='warplate':d.polygon([(0,0),(6,0),(5,18),(0,22)],fill=P['cloth']);line([(9,4),(12,6),(11,8)],P['ink']);line([(2,1),(13,1)],P['trim'])
   elif mat=='crossleather':
    for y in [5,11,17]:line([(1,y),(14,y)],shade(base,1.2))
    for x in [4,10]:line([(x,2),(x,21)],shade(base,.68))
   elif mat=='patched':line([(1,1),(13,1),(13,21)],P['trim']);line([(2,19),(12,19)],shade(base,.6))
   elif mat=='watchcoat':line([(8,0),(8,23)],P['ink']);r((9,6,10,7),P['trim']);r((9,16,10,17),P['trim'])
  elif face=='down':r((0,0,15,23),shade(base,.75))
 return im.resize((w,h),Image.Resampling.NEAREST)

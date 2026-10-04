"""Original native32 weapons, tools, instruments and consumables, no live writes."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import importlib.util,json,hashlib,shutil
D=Path(__file__).resolve().parent;ROOT=D.parents[3];S=ROOT/'src/main/resources/assets/dynasty';A=D/'candidate/assets/dynasty'
spec=importlib.util.spec_from_file_location('core',D.parent/'items-core/build_core.py');core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
Art=core.Art
# Each blade has its own silhouette/guard/material assignment, rather than palette-only tiers.
SWORDS={
 'sword_bronze':('gold','goldlight','goldshade','straight',2,'brown'),
 'sword_silver':('steel','white','steelshade','straight',1,'blue'),
 'sword_jade':('jade','jadelight','jadedark','broad',2,'redshade'),
 'tie_jian':('steelshade','steel','ink','straight',2,'brown'),
 'peach_sword':('toast','bread','brown','wood',2,'red'),
 'qinggang_sword':('steel','steellight','bluedark','split',2,'jade'),
 'yitian_sword':('bluelight','white','blue','long',2,'purpleshade'),
 'supreme_sword':('gold','goldlight','goldshade','broad',2,'redshade'),
 'tong_dao':('gold','goldlight','goldshade','curve',3,'brown'),
 'huan_shou_dao':('steel','steellight','steelshade','curve',2,'redshade'),
 'dragon_slayer':('steelshade','steel','bluedark','cleaver',4,'red'),
 'zhanma_dao':('steel','steellight','steelshade','longcurve',3,'brown'),
 'ziwei_saber':('purple','purplelight','purpleshade','crescent',3,'gold'),
}
POLES={
 'chang_qiang':'iron_spear','mu_mao':'wood_spear','dragon_spear':'dragon_spear','thunder_spear':'thunder_spear',
 'baihu_glaive':'hook_glaive','halberd_fangtian':'double_halberd','sea_trident':'trident',
 'shi_ge':'stone_dagger','gilded_mace':'mace','pojun_axe':'war_axe','qilin_war_axe':'horn_axe','xuantian_axe':'crescent_axe',
 'pickaxe_jade':'jade_pick','pickaxe_dragon_crystal':'crystal_pick'}
BOWS={'lie_gong':('toast','bread','brown','plain'),'luoyan_bow':('blue','bluelight','bluedark','wing'),
 'sunbow':('gold','goldlight','redshade','sun'),'tianlang_bow':('steelshade','steel','bluedark','wolf'),'zhuque_bow':('red','gold','redshade','feather')}
def draw(n):
 a=Art()
 if n in SWORDS:
  base,hi,lo,shape,w,grip=SWORDS[n]
  a.line([(4,28),(12,20)],'ink',5);a.line([(5,27),(11,21)],grip,3)
  a.line([(5,27),(6,28)],'gold');a.line([(8,23),(9,24)],'goldshade')
  pts={'straight':[(11,19),(24,5),(28,3),(26,8),(14,22)],
   'broad':[(10,17),(23,4),(28,3),(27,9),(15,23)],
   'wood':[(11,18),(24,5),(27,4),(26,8),(14,22)],
   'split':[(10,18),(21,8),(23,4),(28,3),(27,8),(24,9),(14,23)],
   'long':[(11,19),(23,7),(27,2),(29,3),(28,7),(14,23)],
   'curve':[(11,18),(19,12),(24,7),(27,3),(28,8),(25,14),(20,19),(14,23)],
   'cleaver':[(10,17),(20,7),(28,3),(28,10),(25,13),(23,19),(16,24)],
   'longcurve':[(10,18),(21,11),(28,3),(29,6),(26,13),(19,21),(14,24)],
   'crescent':[(10,19),(20,13),(24,8),(25,3),(29,6),(27,13),(23,19),(15,24)]}[shape]
  a.poly(pts,lo,'ink');a.poly([pts[0],(pts[1][0],pts[1][1]+1),(pts[2][0]-1,pts[2][1]+1),(pts[-1][0]-1,pts[-1][1]-2)],base)
  a.line([(12,19),(23,8),(26,5)],hi)
  a.line([(9,16),(15,22)],'ink',3);a.line([(9,17),(14,22)],'gold',2)
  if n=='huan_shou_dao':a.oval((2,25,7,30),'goldshade','ink');a.oval((4,27,5,28),'#00000000')
  if n in ('supreme_sword','qinggang_sword','yitian_sword','ziwei_saber'):
   a.gem(12,21,2,'jade' if n!='ziwei_saber' else 'purple','jadelight' if n!='ziwei_saber' else 'purplelight','jadedark' if n!='ziwei_saber' else 'purpleshade')
  if shape=='cleaver':a.line([(19,16),(21,13),(24,12)],'goldshade',2)
  if shape=='wood':a.line([(17,14),(19,14),(21,11)],'brown')
 elif n in POLES:
  typ=POLES[n];a.line([(4,28),(24,8)],'ink',4);a.line([(5,27),(23,9)],'brown',2);a.line([(5,26),(10,21)],'bread')
  a.line([(11,20),(12,21)],'gold');a.line([(14,17),(15,18)],'goldshade')
  if typ in ('iron_spear','wood_spear','dragon_spear','thunder_spear'):
   base,hi,lo=('toast','bread','brown') if typ=='wood_spear' else ('steel','white','steelshade')
   if typ=='thunder_spear':base,hi,lo='blue','bluelight','bluedark'
   a.poly([(18,11),(22,4),(29,2),(27,9),(21,15)],lo,'ink');a.poly([(20,11),(25,5),(28,3),(25,9)],base);a.line([(22,9),(27,4)],hi)
   if typ=='dragon_spear':
    a.line([(22,10),(18,8),(17,11),(19,13)],'gold',2);a.gem(20,13,2,'jade','jadelight','jadedark')
   if typ!='wood_spear':
    a.poly([(17,12),(21,14),(20,20),(17,17),(14,20),(15,15)],'redshade' if typ!='thunder_spear' else 'purpleshade','ink');a.line([(18,14),(18,17)],'red' if typ!='thunder_spear' else 'purplelight')
  elif typ=='trident':
   a.line([(18,13),(21,16),(29,7)],'ink',3);a.line([(15,10),(18,13),(25,5)],'ink',3);a.line([(18,13),(26,5)],'ink',3)
   for pts in [[(18,13),(21,15),(28,7)],[(15,10),(17,12),(24,5)],[(19,12),(27,3)]]:a.line(pts,'steel',2);a.dot(pts[-1],'white')
   a.gem(19,14,2,'jade','jadelight','jadedark')
  elif typ in ('double_halberd','hook_glaive'):
   a.poly([(19,10),(24,3),(28,2),(27,7),(22,13)],'steel','ink');a.line([(22,8),(26,4)],'white')
   a.poly([(15,6),(17,8),(20,8),(21,12),(18,15),(13,14),(16,12),(17,10)],'steelshade','ink');a.line([(15,7),(18,9),(20,10)],'steel')
   if typ=='double_halberd':a.poly([(24,14),(25,11),(29,9),(29,15),(25,19),(22,18)],'steel','ink');a.line([(27,12),(27,15),(25,17)],'white')
   else:a.poly([(23,12),(27,10),(25,16),(21,19),(22,15)],'gold','ink')
  elif typ=='stone_dagger':
   a.poly([(14,8),(18,9),(23,14),(21,18),(11,13),(9,9)],'steelshade','ink');a.poly([(12,9),(17,10),(20,13),(15,13)],'steel');a.line([(18,13),(22,17)],'bread',2)
  elif typ=='mace':
   a.poly([(12,18),(23,4),(26,3),(28,6),(28,9),(16,22)],'goldshade','ink');a.poly([(14,18),(24,6),(26,5),(26,8),(16,20)],'gold');a.line([(15,17),(24,6)],'goldlight')
   for x,y in [(16,16),(19,12),(22,8)]:a.line([(x-1,y-1),(x+2,y+2)],'goldshade');a.line([(x,y-1),(x+2,y+1)],'goldlight')
  elif typ.endswith('pick'):
   base,hi,lo=('jade','jadelight','jadedark') if typ=='jade_pick' else ('purple','purplelight','purpleshade')
   a.poly([(8,9),(10,6),(17,5),(25,9),(29,14),(28,19),(25,14),(20,11),(13,10)],lo,'ink');a.line([(10,8),(16,7),(24,11),(27,15)],base,3);a.line([(11,7),(16,6),(21,8)],hi)
  else:
   base,hi,lo=('steel','white','steelshade') if typ=='war_axe' else ('jade','jadelight','jadedark') if typ=='horn_axe' else ('gold','goldlight','goldshade')
   a.poly([(12,4),(16,6),(19,8),(23,8),(27,5),(28,10),(26,17),(20,21),(13,19),(9,14),(9,8)],lo,'ink');a.poly([(12,6),(16,9),(20,10),(25,8),(25,14),(21,18),(15,17),(11,13)],base);a.line([(11,9),(11,13),(15,17),(20,19),(24,16)],hi)
   if typ=='horn_axe':a.poly([(21,7),(20,2),(24,5),(24,9)],'cream','goldshade')
   if typ=='crescent_axe':a.poly([(19,9),(22,8),(24,6),(24,12),(21,14),(18,13)],'#00000000')
   a.line([(17,10),(22,15)],'goldshade',2)
 elif n in BOWS:
  base,hi,lo,motif=BOWS[n]
  outlines={'plain':[(6,3),(13,3),(20,5),(26,9),(29,15),(29,22),(27,27),(25,25),(26,20),(25,14),(22,10),(17,7),(11,6),(6,6)],
   'wing':[(5,3),(12,3),(19,5),(26,10),(29,16),(29,23),(27,28),(25,25),(26,20),(24,13),(19,9),(11,6),(5,6)],
   'sun':[(6,3),(13,3),(20,5),(27,11),(29,17),(29,23),(27,28),(24,26),(25,20),(24,14),(20,10),(12,7),(6,7)],
   'wolf':[(5,3),(11,2),(18,5),(25,9),(29,14),(29,21),(27,27),(24,26),(26,20),(24,15),(20,11),(14,8),(8,6),(5,6)],
   'feather':[(5,3),(12,3),(19,6),(26,9),(29,15),(29,23),(27,28),(24,26),(25,20),(24,15),(20,11),(13,8),(6,6)]}
  a.poly(outlines[motif],lo,'ink');a.line([(9,4),(16,6),(23,10),(27,16),(27,22),(26,25)],base,2);a.line([(13,4),(20,7),(25,12)],hi)
  a.line([(7,6),(26,26)],'clothlight');a.line([(25,12),(27,17)],'goldshade',4);a.line([(25,12),(27,16)],'gold')
  if motif=='sun':a.oval((18,4,23,9),'goldlight','goldshade');a.dot((21,6),'red')
  elif motif=='feather':
   a.line([(12,5),(10,9),(6,10)],'red',2);a.line([(16,6),(15,10),(11,12)],'gold')
  elif motif=='wolf':a.poly([(23,8),(28,7),(29,12),(26,14)],'steel','ink');a.dot((27,10),'blue')
  elif motif=='wing':a.poly([(13,4),(8,8),(4,7),(7,5)],'bluelight','blue')
 elif n in ('bamboo_flute','yu_di'):
  base,hi,lo=('leaf','leaflight','leafdark') if n=='bamboo_flute' else ('jade','jadelight','jadedark')
  a.line([(5,27),(25,5)],'ink',5);a.line([(6,26),(25,5)],base,3);a.line([(7,24),(24,5)],hi)
  for x,y in [(10,22),(13,18),(16,15),(19,12)]:a.rect((x,y,x+1,y+1),lo)
  a.line([(22,5),(26,8)],'gold');a.line([(4,25),(8,29)],'goldshade')
  if n=='yu_di':a.line([(19,8),(17,5),(13,5),(11,9)],'redshade');a.line([(12,8),(12,13)],'red')
 elif n=='drum_beater':
  a.line([(6,27),(23,9)],'ink',4);a.line([(7,26),(22,10)],'toast',2);a.poly([(18,7),(23,3),(28,7),(28,11),(24,15),(19,12)],'redshade','ink');a.line([(21,6),(24,5),(27,8)],'rose',2);a.line([(20,10),(23,13)],'gold')
 elif n=='conch_horn':
  a.poly([(5,23),(8,16),(13,8),(21,4),(26,7),(28,14),(24,22),(17,25),(12,23),(7,28)],'bread','brown');a.poly([(11,17),(15,10),(21,7),(25,10),(24,17),(20,21),(15,21)],'cream');a.line([(14,16),(17,11),(21,10),(23,13),(21,17),(18,17),(17,15)],'toast');a.line([(7,23),(10,23),(9,26)],'white')
 elif n=='folding_fan':
  a.poly([(3,15),(5,8),(12,4),(20,4),(27,8),(29,15),(16,27)],'bread','dark');a.poly([(4,14),(7,9),(12,6),(20,6),(25,9),(28,14),(16,24)],'cream')
  for pt in [(5,12),(10,7),(16,6),(22,7),(27,12)]:a.line([pt,(16,26)],'toast')
  a.line([(8,13),(11,11),(15,14),(19,10),(24,12)],'blue');a.line([(16,25),(16,29)],'brown',2)
 elif n.startswith('dynasty_'):
  a.rect((13,3,19,6),'toast','dark');a.rect((12,7,20,12),'bluelight','bluedark')
  if n=='dynasty_potion':pts=[(12,11),(20,11),(25,17),(25,25),(21,29),(10,29),(6,24),(7,17)]
  elif n=='dynasty_splash_potion':pts=[(12,10),(19,8),(23,13),(27,20),(25,26),(19,29),(11,28),(6,22),(8,15)]
  else:pts=[(12,11),(20,11),(24,15),(28,20),(26,27),(21,29),(10,29),(5,25),(4,20),(8,15)]
  liquid,light={'dynasty_potion':('jade','jadelight'),'dynasty_splash_potion':('red','rose'),'dynasty_lingering_potion':('purple','purplelight')}[n]
  a.poly(pts,'blue','bluedark');a.poly([(9,18),(23,18),(24,24),(20,27),(11,26),(8,23)],liquid);a.poly([(10,19),(22,19),(21,23),(11,24)],light);a.line([(10,14),(8,18),(8,21)],'white');a.line([(14,8),(18,8)],'white')
  if n=='dynasty_lingering_potion':a.rect((12,3,20,5),'goldshade','dark');a.line([(13,3),(18,3)],'gold')
  if n=='dynasty_splash_potion':a.line([(13,5),(11,3),(9,4)],'brown')
 elif n in ('golden_pill','pill_focus','pill_longevity'):
  a.poly([(5,22),(10,18),(25,19),(28,25),(23,28),(9,28)],'cream','toast')
  base,hi,lo={'golden_pill':('gold','goldlight','goldshade'),'pill_focus':('purple','purplelight','purpleshade'),'pill_longevity':('jade','jadelight','jadedark')}[n]
  if n=='golden_pill':a.oval((7,7,24,24),lo,'dark');a.oval((9,8,22,21),base);a.oval((10,10,15,14),hi);a.line([(17,18),(20,16)],hi)
  else:
   for x,y in [(11,18),(21,19),(16,10)]:a.oval((x-5,y-5,x+4,y+4),lo,'dark');a.oval((x-3,y-4,x+2,y+1),base);a.line([(x-2,y-3),(x,y-3)],hi)
 elif n=='healing_salve':
  a.rect((8,7,24,11),'redshade','dark');a.line([(10,8),(21,8)],'red');a.poly([(9,11),(23,11),(25,15),(24,27),(8,27),(7,15)],'bread','brown');a.rect((9,15,22,23),'cream');a.rect((14,16,17,22),'red');a.rect((11,18,20,20),'red');a.line([(9,12),(9,16)],'white')
 elif n=='rebel_head':
  # A stylised head icon with a tied helmet, no blood or injury detail.
  a.rect((8,7,24,26),'toast','dark');a.poly([(9,10),(22,10),(23,20),(20,25),(12,25),(9,20)],'bread');a.rect((7,6,25,12),'steelshade','ink');a.line([(8,7),(23,7)],'steel');a.rect((13,3,19,7),'ink');a.line([(13,4),(17,4)],'steelshade');a.line([(11,16),(13,16)],'dark');a.line([(19,16),(21,16)],'dark');a.line([(14,23),(19,23)],'brown');a.poly([(9,22),(12,24),(20,24),(23,22),(21,28),(11,28)],'dark')
 else:raise ValueError(n)
 return a.im

def main():
 ids=json.loads((D/'allowed.json').read_text());records=[]
 for n in ids:
  source=S/'textures/item'/f'{n}.png';before=D/'before/textures/item'/source.name;before.parent.mkdir(parents=True,exist_ok=True)
  if not before.exists():shutil.copy2(source,before)
  assert source.read_bytes()==before.read_bytes()
  model=S/'models/item'/f'{n}.json';mb=D/'before/models/item'/model.name;mb.parent.mkdir(parents=True,exist_ok=True)
  if not mb.exists():shutil.copy2(model,mb)
  im=draw(n);out=A/'textures/item'/source.name;out.parent.mkdir(parents=True,exist_ok=True)
  assert set(im.getchannel('A').tobytes())<={0,255}
  bbox=im.getbbox();assert bbox[0]>=1 and bbox[1]>=1 and bbox[2]<=31 and bbox[3]<=31,(n,bbox)
  im.save(out)
  records.append({'id':'dynasty:'+n,'path':str(out.relative_to(D)),'source':str(source.relative_to(ROOT)),
   'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
   'model_source_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'model_parent':json.loads(model.read_text()).get('parent'),
   'dimensions':[32,32],'alpha':[0,255],'status':'candidate_not_installed'})
 (D/'previews').mkdir(exist_ok=True);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
 for page in range((len(records)+19)//20):
  c=Image.new('RGB',(1120,880),'#e8e9df');d=ImageDraw.Draw(c)
  for j,r in enumerate(records[page*20:page*20+20]):
   n=r['id'].split(':')[1];x=16+j%5*222;y=16+j//5*218;d.text((x,y),n,font=font,fill='#263831')
   for xx,base in [(x,D/'before/textures/item'),(x+104,A/'textures/item')]:
    im=Image.open(base/(n+'.png')).convert('RGBA');z=im.resize((96,96),Image.Resampling.NEAREST);c.paste(z,(xx,y+30),z);c.paste(im,(xx,y+143),im)
   d.text((x,y+186),'Before / After | native 32',font=font,fill='#64715d')
  c.save(D/'previews'/f'contact-{page+1:02}.png')
 (D/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print('Equipment PNG candidates',len(records))
if __name__=='__main__':main()

"""Original native 32px food/craft/material sprites; scoped review candidates only.
Every family/variant is assigned explicitly. No random pixels, imported reference art,
image downsampling or changes to the live project. Palette ramps are discrete shapes.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,math
D=Path(__file__).resolve().parent;ROOT=D.parents[3];S=ROOT/'src/main/resources/assets/dynasty';A=D/'candidate/assets/dynasty'
P={'ink':'#332d2a','bread':'#d6ae6d','cream':'#f0d7a0','white':'#eee5c8','toast':'#a7703c','brown':'#76503b','dark':'#493b30',
 'red':'#b6533e','rose':'#dd8973','redlight':'#edb197','redshade':'#773933','leaf':'#688747','leaflight':'#94ad62','leafdark':'#3d6040',
 'gold':'#cba361','goldlight':'#e8c888','goldshade':'#85603c','blue':'#5e8292','bluelight':'#a4bdc0','bluedark':'#344f61',
 'jade':'#68a485','jadelight':'#aed1aa','jadedark':'#365e50','purple':'#8a6aab','purplelight':'#c2a2d5','purpleshade':'#503c6e',
 'steel':'#7e9199','steellight':'#bac7c4','steelshade':'#465562','cloth':'#8f7a65','clothlight':'#bca386'}
def color(c):return P.get(c,c)
class Art:
 def __init__(self):self.im=Image.new('RGBA',(32,32));self.d=ImageDraw.Draw(self.im)
 def poly(self,p,c,o=None):self.d.polygon(p,fill=color(c),outline=color(o) if o else None)
 def rect(self,b,c,o=None):self.d.rectangle(b,fill=color(c),outline=color(o) if o else None)
 def line(self,p,c,w=1):self.d.line(p,fill=color(c),width=w)
 def dot(self,p,c):self.d.point(p,fill=color(c))
 def oval(self,b,c,o=None):self.d.ellipse(b,fill=color(c),outline=color(o) if o else None)
 def gem(self,x,y,r,base='jade',hi='jadelight',lo='jadedark'):
  self.poly([(x,y-r),(x+r,y-1),(x+r-1,y+r-2),(x,y+r),(x-r,y+2),(x-r+1,y-2)],base,'ink')
  self.poly([(x,y-r+1),(x+1,y),(x-r+1,y+1)],hi)
  self.poly([(x+1,y),(x+r-1,y),(x,y+r-1)],lo)
 def seal(self,x,y,c='red'):
  self.rect((x,y,x+5,y+5),c);self.line([(x+1,y+1),(x+3,y+1),(x+3,y+3),(x+1,y+3)],'cream')

SPEC={}
def add(names,family,**kw):
 for name in names.split():SPEC[name]={'family':family,**kw}

add('bronze_ingot silver_ingot refined_steel','ingot')
add('jade cinnabar dragon_crystal','mineral')
add('dragon_scale dragon_king_scale qinglong_scale scale_plate','scale')
add('phoenix_feather sky_feather sun_feather zhuque_feather crane_feather immortal_crane_feather night_heron_feather','feather')
add('deer_antler baihu_fang ivory_tusk rhino_horn qilin_horn tiger_claw','horn')
add('fox_tail leopard_tail','tail')
add('turtle_shell xuanwu_shell','shell')
add('emperor_bone tiger_crest snake_gall','organ')
add('raw_silk silk brocade roof_tile','craft')
add('bamboo_slip talisman_paper blueprint exam_paper edict dynasty_guide dynasty_manual','paper')
add('ink_stick ink_brush inkstone','ink')
add('roast_duck cured_meat bear_paw','meat')
add('bamboo_rice zongzi','wrapped_food')
add('dumpling tangyuan sesame_ball dragon_beard_candy','pale_food')
add('immortal_peach peach_bun dried_persimmon candied_hawthorn','fruit_food')
add('lotus_cake osmanthus_cake mooncake niangao sweet_soup_cake','cake')
add('eight_treasure_porridge longevity_noodles hotpot','bowl')
add('baijiu wine chrysanthemum_wine','wine')
add('tea tea_cup','tea')

def draw(name,spec):
 a=Art();f=spec['family']
 if f=='ingot':
  base,hi,lo={'bronze_ingot':('gold','goldlight','goldshade'),'silver_ingot':('steel','white','steelshade'),'refined_steel':('steelshade','steel','bluedark')}[name]
  a.poly([(5,15),(10,9),(23,9),(28,15),(24,23),(7,23),(3,19)],lo,'ink')
  a.poly([(6,15),(11,10),(22,10),(26,15),(22,18),(7,18)],base)
  a.line([(9,14),(12,11),(22,11)],hi);a.poly([(7,19),(22,19),(24,17),(23,22),(8,22)],base)
  a.line([(8,20),(20,20)],hi)
  if name=='refined_steel':a.line([(10,16),(22,16)],lo);a.rect((12,19,16,21),'steelshade')
 elif f=='mineral':
  if name=='dragon_crystal':
   for x,y,r in [(10,20,6),(21,19,7),(16,12,9)]:a.gem(x,y,r,'purple','purplelight','purpleshade')
   a.line([(16,5),(16,14)],'white');a.line([(21,15),(22,18)],'purplelight')
  elif name=='jade':
   a.poly([(8,8),(16,5),(25,11),(27,19),(21,26),(9,25),(4,18)],'jadedark','ink')
   a.poly([(8,9),(16,6),(23,11),(21,17),(10,18),(5,17)],'jade')
   a.poly([(9,10),(15,7),(17,11),(12,15),(7,15)],'jadelight')
   a.poly([(12,19),(20,18),(23,23),(19,25),(10,24)],'jade')
  else:
   a.poly([(6,16),(11,8),(19,6),(26,12),(27,21),(20,26),(10,25),(4,21)],'redshade','ink')
   a.poly([(11,9),(18,7),(23,12),(19,17),(8,18)],'red');a.poly([(10,11),(16,9),(18,12),(12,15)],'rose')
   a.poly([(12,19),(21,18),(25,21),(19,25),(12,24)],'red')
 elif f=='scale':
  base,hi,lo={'dragon_scale':('purple','purplelight','purpleshade'),'dragon_king_scale':('blue','bluelight','bluedark'),'qinglong_scale':('jade','jadelight','jadedark'),'scale_plate':('steel','steellight','steelshade')}[name]
  a.poly([(9,5),(21,5),(27,12),(25,21),(16,28),(6,21),(4,12)],lo,'ink')
  a.poly([(10,7),(20,7),(24,12),(22,19),(16,24),(9,19),(7,12)],base)
  a.line([(10,8),(20,8),(23,12)],hi);a.line([(8,15),(13,18),(19,18),(23,15)],hi)
  a.line([(10,21),(16,25),(21,21)],base)
  if name=='dragon_king_scale':a.poly([(16,3),(19,7),(16,12),(13,7)],'gold','goldshade');a.dot((16,5),'goldlight')
  elif name=='scale_plate':
   for p in [(9,10),(21,10),(10,20),(21,20)]:a.rect((p[0],p[1],p[0]+1,p[1]+1),'goldshade')
  elif name=='qinglong_scale':a.line([(16,9),(13,13),(16,15),(19,13)],hi)
 elif f=='feather':
  # Each feather is drawn directly at 32px: pinions, crest plumes and down
  # deliberately have different silhouettes and barbs, not color-only swaps.
  if name=='crane_feather':
   a.poly([(5,29),(8,22),(9,14),(14,7),(24,3),(25,8),(20,17),(15,23),(9,25)],'steel','ink')
   a.poly([(10,21),(11,14),(16,8),(23,5),(22,10),(18,17),(14,21)],'white')
   a.line([(6,28),(13,20),(22,7)],'cloth');a.line([(13,18),(13,13)],'cream');a.line([(16,14),(17,9)],'cream')
   a.poly([(22,5),(24,4),(24,8),(21,12),(20,11)],'steelshade')
  elif name=='night_heron_feather':
   a.poly([(8,29),(10,24),(10,15),(16,7),(24,3),(26,5),(23,11),(18,20),(13,25)],'ink')
   a.poly([(12,22),(12,15),(17,9),(24,5),(21,12),(17,19)],'bluedark')
   a.line([(9,28),(16,17),(24,6)],'steel');a.line([(14,18),(14,13),(17,10)],'blue');a.line([(17,19),(21,15)],'steelshade')
  elif name=='sky_feather':
   a.poly([(4,26),(9,20),(8,14),(11,8),(17,7),(24,3),(26,7),(22,14),(18,20),(11,24)],'bluedark','ink')
   a.poly([(10,20),(10,15),(13,10),(17,10),(23,6),(22,11),(18,17),(13,21)],'blue')
   a.poly([(12,11),(15,8),(17,8),(16,12),(11,17)],'bluelight')
   a.line([(5,26),(13,20),(23,7)],'cream');a.line([(15,17),(19,16),(21,13)],'white');a.line([(10,23),(16,23),(20,19)],'bluelight')
  elif name=='immortal_crane_feather':
   a.poly([(4,28),(9,21),(9,14),(14,8),(26,3),(27,6),(24,10),(24,14),(19,21),(12,26)],'blue','ink')
   a.poly([(11,21),(11,15),(16,10),(25,5),(22,11),(22,14),(18,19),(13,22)],'white')
   a.line([(5,27),(14,19),(24,6)],'goldshade');a.line([(13,17),(14,12),(19,8)],'bluelight')
   a.poly([(13,24),(19,20),(22,16),(21,20),(17,24)],'bluelight');a.line([(7,24),(10,26),(12,26)],'gold')
  elif name=='phoenix_feather':
   a.poly([(4,29),(9,21),(8,15),(11,9),(17,5),(25,2),(26,6),(23,10),(24,13),(21,19),(16,23),(10,26)],'redshade','ink')
   a.poly([(10,21),(10,15),(14,10),(22,5),(24,4),(21,11),(21,15),(17,20),(12,23)],'red')
   a.poly([(14,14),(17,10),(21,8),(19,14),(15,19),(12,20)],'gold')
   a.line([(5,28),(14,18),(23,5)],'goldshade');a.line([(15,15),(18,11)],'goldlight',2)
   a.line([(12,23),(17,22),(21,18)],'rose');a.line([(10,17),(11,12)],'rose')
  elif name=='sun_feather':
   a.poly([(5,28),(9,21),(7,17),(10,10),(16,8),(21,3),(26,3),(27,8),(22,15),(17,22),(10,25)],'red','ink')
   a.poly([(10,21),(10,15),(14,11),(19,10),(24,5),(25,8),(19,16),(15,21)],'gold')
   a.poly([(12,15),(14,12),(18,12),(17,16),(14,18)],'cream')
   a.line([(6,27),(14,19),(24,6)],'goldshade');a.line([(13,23),(17,23),(21,19)],'goldlight');a.line([(10,18),(9,16),(11,12)],'rose')
  else: # Vermilion bird: split trailing vanes and a narrow dark central eye.
   a.poly([(5,29),(8,22),(7,17),(10,11),(18,5),(26,2),(27,6),(23,10),(24,15),(21,21),(17,23),(13,26),(9,25)],'redshade','ink')
   a.poly([(10,22),(9,17),(12,12),(20,7),(25,4),(23,8),(20,12),(21,16),(17,21)],'rose')
   a.line([(6,28),(14,18),(24,5)],'toast');a.poly([(14,15),(18,10),(21,8),(19,13),(16,17)],'red')
   a.line([(11,16),(13,12),(17,9)],'redlight');a.line([(13,23),(17,22),(21,18)],'gold');a.dot((18,11),'cream')
 elif f=='horn':
  if name=='deer_antler':
   for pts in [[(10,28),(15,20),(17,10),(18,4)],[(14,20),(7,16),(6,10)],[(16,16),(23,12),(26,6)],[(10,17),(11,10),(9,6)],[(17,11),(13,7),(14,3)]]:
    a.line(pts,'dark',4);a.line(pts,'bread',2)
   a.line([(11,26),(15,20),(16,12)],'cream')
  elif name=='tiger_claw':
   for x,y in [(7,10),(14,6),(22,11)]:
    a.poly([(x,y),(x+5,y+1),(x+4,y+9),(x,y+14),(x+1,y+8)],'toast','dark')
    a.line([(x+1,y+2),(x+3,y+3),(x+2,y+8)],'cream')
   a.rect((9,25,22,28),'brown');a.line([(10,25),(20,25)],'bread')
  else:
   variant={'baihu_fang':0,'ivory_tusk':1,'rhino_horn':2,'qilin_horn':3}[name]
   pts=[[(9,25),(10,17),(17,11),(23,4),(24,12),(21,20),(16,27)],[(6,22),(12,24),(20,20),(25,10),(25,4),(28,12),(25,23),(17,28),(8,28)],[(7,26),(10,16),(14,11),(15,4),(20,12),(25,26)],[(8,26),(13,19),(15,10),(19,4),(19,15),(23,11),(25,7),(25,17),(18,23),(14,28)]][variant]
   a.poly(pts,'bread','dark');a.line(pts[1:4],'cream',2)
   if name=='qilin_horn':a.line([(12,23),(16,22),(18,19)],'goldshade');a.line([(13,17),(17,17)],'goldshade')
 elif f=='tail':
  base,hi,lo=('white','cream','toast') if name=='fox_tail' else ('bread','goldlight','brown')
  a.poly([(5,27),(6,20),(8,12),(13,6),(21,4),(27,7),(27,13),(24,20),(17,26),(9,28)],lo,'ink')
  a.poly([(8,23),(9,13),(15,7),(22,6),(25,10),(23,16),(17,22)],base)
  a.poly([(13,8),(20,6),(24,9),(20,10),(17,9)],hi)
  if name=='leopard_tail':
   for x,y in [(12,12),(18,16),(10,21),(22,9)]:a.line([(x,y),(x+2,y),(x+2,y+2)],'brown')
  else:a.poly([(6,26),(8,20),(12,24),(17,23),(13,27)],'cream')
 elif f=='shell':
  base,hi,lo=('leaf','leaflight','leafdark') if name=='turtle_shell' else ('jadedark','jade','bluedark')
  a.poly([(12,4),(20,4),(26,10),(28,18),(24,25),(17,28),(8,25),(4,18),(6,9)],lo,'ink')
  a.poly([(12,6),(19,6),(24,11),(25,18),(21,24),(12,25),(7,19),(8,11)],base)
  a.poly([(12,10),(19,9),(23,16),(19,21),(12,20),(9,15)],lo)
  a.poly([(13,11),(18,11),(21,16),(18,19),(13,18),(11,15)],hi)
  for pts in [[(12,10),(10,6)],[(19,9),(22,7)],[(23,16),(26,17)],[(19,21),(22,25)],[(12,20),(9,24)],[(9,15),(5,15)]]:a.line(pts,lo)
 elif f=='organ':
  if name=='emperor_bone':
   a.poly([(5,22),(8,18),(12,19),(21,10),(20,6),(24,3),(28,6),(27,10),(24,12),(15,23),(15,27),(11,29),(7,27)],'cloth','dark')
   a.line([(8,23),(11,22),(23,9)],'white',3);a.line([(10,26),(13,26)],'cream')
  elif name=='snake_gall':
   a.line([(17,4),(17,9),(20,13)],'leafdark',3)
   a.poly([(12,12),(20,11),(26,17),(24,25),(17,29),(9,25),(7,18)],'leafdark','ink')
   a.poly([(12,14),(18,13),(21,17),(18,22),(10,22),(9,18)],'leaf');a.line([(12,15),(16,14)],'leaflight',2)
  else:
   a.poly([(7,10),(15,5),(26,8),(25,18),(19,17),(17,23),(9,27),(5,22)],'goldshade','ink')
   a.poly([(8,11),(15,7),(23,9),(21,14),(16,13),(13,19),(8,23)],'gold');a.line([(10,12),(13,10),(13,13)],'goldlight');a.line([(17,10),(20,11)],'dark')
 elif f=='craft':
  if name=='raw_silk':
   a.oval((8,5,24,25),'cream','brown');a.oval((10,7,21,23),'white');a.line([(14,7),(12,11),(12,18),(16,22),(19,18),(19,10)],'bread');a.line([(16,25),(16,28),(8,28),(6,25)],'cream')
  elif name in ('silk','brocade'):
   base,hi,lo=('red','rose','redshade') if name=='silk' else ('blue','bluelight','bluedark')
   a.poly([(5,7),(23,5),(27,9),(27,25),(9,28),(5,24)],lo,'ink');a.poly([(7,8),(22,7),(25,10),(24,23),(9,25),(7,23)],base)
   a.line([(8,11),(22,9),(24,11)],hi);a.line([(10,21),(21,19)],hi)
   a.poly([(7,24),(10,26),(25,24),(23,27),(9,29)],hi,'ink')
   if name=='brocade':
    for x,y in [(11,13),(18,15)]:a.line([(x,y+3),(x,y),(x+3,y),(x+3,y+2),(x+1,y+2)],'gold')
  else:
   for x,y in [(5,15),(10,11),(16,7)]:
    a.poly([(x,y),(x+8,y-1),(x+12,y+8),(x+8,y+12),(x+2,y+12),(x-1,y+3)],'jadedark','ink');a.poly([(x+1,y+1),(x+7,y),(x+9,y+8),(x+5,y+10),(x+2,y+8)],'jade');a.line([(x+2,y+2),(x+6,y+1),(x+7,y+4)],'jadelight')
 elif f=='paper':
  if name=='bamboo_slip':
   for x,y in [(6,6),(10,5),(14,5),(18,6),(22,8)]:
    a.rect((x,y,x+3,26),'leaf','dark');a.line([(x+1,y+2),(x+1,23)],'leaflight')
   a.line([(6,11),(25,12)],'brown');a.line([(6,22),(25,23)],'brown')
  elif name in ('dynasty_guide','dynasty_manual'):
   base,hi,lo=('red','gold','redshade') if name=='dynasty_guide' else ('blue','bluelight','bluedark')
   a.poly([(6,6),(22,4),(27,8),(27,25),(10,28),(5,24)],lo,'ink');a.poly([(10,25),(25,23),(25,26),(10,29),(6,25)],'cream','brown');a.poly([(7,7),(22,5),(25,8),(25,22),(10,25),(7,23)],base)
   a.line([(10,7),(10,23)],'goldshade');a.rect((14,11,21,18),hi);a.seal(15,12,lo)
  elif name=='edict':
   a.rect((6,7,26,24),'bread','brown');a.rect((8,8,24,22),'cream');a.rect((3,5,7,27),'redshade','ink');a.rect((24,5,28,27),'redshade','ink');a.line([(4,7),(4,24)],'red')
   a.line([(11,12),(20,12)],'toast');a.line([(11,15),(19,15)],'toast');a.seal(14,17)
  else:
   base,hi,lo=('blue','bluelight','bluedark') if name=='blueprint' else ('cream','white','toast')
   a.poly([(7,4),(24,4),(24,25),(20,28),(7,28)],base,'brown');a.poly([(8,5),(22,5),(22,25),(8,25)],hi)
   if name=='blueprint':
    a.line([(11,20),(19,9)],'blue',2);a.line([(11,16),(16,20)],'blue');a.line([(11,8),(18,8)],'blue');a.line([(10,24),(20,24)],'blue')
   elif name=='exam_paper':
    for y,l in [(9,10),(13,9),(17,7),(21,10)]:a.line([(10,y),(10+l,y)],'brown')
    a.seal(18,21)
   else:a.line([(11,8),(20,8)],'toast');a.line([(16,10),(13,14),(19,14),(15,18),(18,20),(12,22)],'red',2)
 elif f=='ink':
  if name=='ink_brush':
   a.line([(7,25),(24,5)],'ink',4);a.line([(9,22),(23,6)],'gold',2);a.line([(21,7),(23,4)],'cream')
   a.poly([(8,20),(12,24),(6,29),(3,29),(4,25)],'cream','ink');a.poly([(4,26),(7,28),(3,29)],'ink');a.line([(9,21),(11,23)],'red')
  elif name=='ink_stick':
   a.poly([(10,4),(21,4),(24,8),(21,28),(9,28),(7,24)],'ink','dark');a.poly([(11,6),(19,6),(20,24),(11,25)],'steelshade');a.line([(12,8),(17,8)],'gold');a.line([(13,12),(17,12),(15,16),(17,19),(12,19)],'gold')
  else:
   a.poly([(6,9),(24,7),(28,12),(27,23),(22,27),(6,25),(3,20)],'ink','dark');a.poly([(7,10),(23,9),(25,12),(24,21),(7,23),(5,20)],'steelshade');a.oval((9,12,22,21),'ink');a.line([(8,10),(21,9)],'steel');a.line([(12,19),(18,19)],'bluedark')
 elif f=='meat':
  if name=='roast_duck':
   a.poly([(7,20),(4,16),(4,12),(8,10),(11,7),(20,7),(25,11),(27,18),(24,24),(16,27),(8,24)],'toast','dark')
   a.oval((8,9,23,23),'bread');a.poly([(9,20),(14,18),(15,23),(11,26),(6,26),(5,23)],'toast','brown');a.poly([(22,19),(26,21),(26,26),(22,28),(19,26),(20,23)],'toast','brown')
   a.line([(10,10),(16,9),(20,11)],'goldlight',2);a.poly([(20,7),(21,3),(24,3),(25,5),(23,8)],'toast','dark');a.line([(5,23),(3,24)],'cream',2)
  elif name=='cured_meat':
   for x,y in [(7,5),(14,8),(20,5)]:
    a.line([(x+3,y),(x+3,y+4)],'brown');a.poly([(x,y+4),(x+5,y+3),(x+6,y+16),(x+3,y+21),(x-1,y+18)],'redshade','dark');a.line([(x+1,y+7),(x+4,y+9),(x+1,y+13),(x+4,y+16)],'bread',2)
  else:
   a.oval((8,13,25,28),'brown','dark')
   for x,y in [(6,9),(12,5),(19,5),(25,10)]:a.oval((x,y,x+5,y+10),'brown','dark');a.dot((x+2,y+1),'cream')
   a.oval((12,18,21,25),'toast');a.line([(12,15),(18,14)],'bread')
 elif f=='wrapped_food':
  if name=='bamboo_rice':
   a.poly([(6,11),(19,5),(26,8),(25,24),(13,29),(6,25)],'leafdark','ink');a.poly([(8,13),(20,8),(24,10),(23,23),(13,27),(8,24)],'leaf');a.poly([(9,11),(18,7),(23,8),(21,13),(12,17),(8,15)],'cream','toast')
   for x,y in [(12,12),(16,10),(19,10),(14,14)]:a.line([(x,y),(x+1,y)],'white')
   a.line([(9,21),(13,23),(23,19)],'leaflight');a.line([(12,18),(12,25)],'leafdark')
  else:
   a.poly([(16,4),(28,22),(19,28),(4,22)],'leafdark','ink');a.poly([(16,6),(24,21),(18,25),(6,21)],'leaf');a.poly([(16,6),(15,20),(7,21)],'leaflight');a.line([(8,14),(23,24)],'cream',2);a.line([(8,24),(22,15)],'bread',2);a.line([(17,20),(25,27),(28,25)],'cream')
 elif f=='pale_food':
  if name=='dumpling':
   a.poly([(4,20),(7,13),(12,8),(18,8),(25,13),(28,20),(24,25),(8,25)],'bread','brown');a.poly([(6,19),(9,13),(14,10),(18,10),(24,14),(26,20),(22,23),(10,23)],'cream')
   for pts in [[(10,12),(12,19)],[(14,10),(15,18)],[(18,11),(19,18)],[(22,14),(22,20)]]:a.line(pts,'toast')
   a.line([(9,22),(22,22)],'white')
  elif name=='dragon_beard_candy':
   a.oval((5,10,27,25),'bread','toast');a.oval((7,11,25,22),'white')
   for x in (10,14,18,22):a.line([(x,13),(x-2,18),(x,21)],'cream')
   a.oval((12,14,21,20),'toast');a.line([(14,16),(19,17)],'brown')
  else:
   for x,y,r in ([(10,20,7),(21,18,7),(16,9,6)] if name=='sesame_ball' else [(10,19,7),(21,19,7),(16,10,6)]):
    a.oval((x-r,y-r,x+r,y+r),'bread' if name=='sesame_ball' else 'cream','toast');a.oval((x-r+2,y-r+1,x+r-2,y+r-4),'cream' if name=='sesame_ball' else 'white')
    if name=='sesame_ball':
     for dx,dy in [(-2,-1),(2,-3),(3,2),(-3,3)]:a.line([(x+dx,y+dy),(x+dx+1,y+dy)],'white')
 elif f=='fruit_food':
  if name=='candied_hawthorn':
   a.line([(10,29),(21,3)],'brown',2)
   for x,y in [(12,23),(16,15),(20,7)]:a.oval((x-5,y-5,x+4,y+4),'redshade','dark');a.oval((x-4,y-4,x+2,y+2),'red');a.line([(x-2,y-3),(x,y-3)],'cream')
  elif name=='dried_persimmon':
   a.oval((4,10,27,26),'toast','brown');a.poly([(9,12),(16,9),(23,13),(25,20),(20,24),(10,23),(6,19)],'bread');a.poly([(12,10),(14,6),(17,9),(22,8),(19,12),(22,15),(16,13),(12,16)],'brown');a.line([(10,19),(15,21),(21,18)],'cream')
  else:
   a.poly([(16,9),(21,6),(26,10),(28,18),(24,25),(17,28),(8,25),(4,18),(6,10),(11,7)],'rose' if name=='immortal_peach' else 'cream','toast')
   a.poly([(8,10),(12,9),(16,12),(16,23),(11,23),(7,18)],'redlight' if name=='immortal_peach' else 'white')
   a.line([(17,11),(20,16),(19,22)],'red' if name=='immortal_peach' else 'rose');a.poly([(16,7),(17,2),(24,3),(22,6),(18,8)],'leafdark');a.line([(18,6),(22,4)],'leaflight')
 elif f=='cake':
  if name=='lotus_cake':
   for pts in [[(16,4),(22,13),(17,20),(11,13)],[(5,10),(13,11),(16,23),(8,21)],[(27,10),(19,11),(16,23),(24,21)],[(6,21),(15,18),(18,25),(12,28)],[(26,21),(17,18),(14,25),(20,28)]]:a.poly(pts,'rose','toast');a.line(pts[:2],'cream')
  elif name=='mooncake':
   a.oval((4,8,28,27),'toast','brown');a.oval((5,6,27,23),'bread','brown');a.oval((8,9,24,21),'toast');a.oval((10,11,22,19),'gold');a.line([(12,13),(19,13),(19,16),(14,16)],'brown');a.line([(6,19),(7,23)],'cream')
  elif name=='sweet_soup_cake':
   a.oval((4,10,28,25),'toast','brown');a.oval((6,9,26,21),'bread');a.poly([(10,11),(20,10),(24,14),(19,15),(16,20),(10,18),(8,15)],'gold');a.line([(11,12),(17,11)],'cream')
  else:
   for x,y in ([(5,15),(13,10),(19,16)] if name=='osmanthus_cake' else [(5,14),(14,9)]):
    a.poly([(x,y),(x+8,y-2),(x+10,y+2),(x+10,y+10),(x+2,y+12),(x,y+8)],'bread','toast');a.poly([(x+1,y+1),(x+8,y-1),(x+9,y+2),(x+2,y+4)],'white');a.line([(x+2,y+5),(x+2,y+9)],'cream')
    if name=='osmanthus_cake':a.dot((x+5,y+1),'goldshade');a.dot((x+6,y+2),'gold')
 elif f=='bowl':
  if name=='hotpot':
   a.line([(4,18),(2,17),(2,13),(4,12)],'dark',2);a.line([(27,18),(29,17),(29,13),(27,12)],'dark',2)
  a.poly([(4,15),(28,15),(26,24),(22,28),(10,28),(6,24)],'bluedark' if name!='hotpot' else 'brown','ink');a.poly([(7,18),(25,18),(24,23),(21,25),(11,25),(8,22)],'blue' if name!='hotpot' else 'toast');a.oval((4,8,28,20),'steelshade' if name=='hotpot' else 'cream','brown');a.oval((7,10,25,17),'redshade' if name=='hotpot' else 'bread')
  if name=='longevity_noodles':
   for x in (10,15,20):a.line([(x,11),(x+2,13),(x-1,15),(x+1,16)],'cream')
   a.line([(21,7),(25,3)],'brown');a.line([(23,8),(28,3)],'brown')
  elif name=='hotpot':a.rect((14,5,18,15),'steelshade','ink');a.oval((13,3,19,7),'steel','ink');a.dot((10,13),'leaflight');a.line([(20,12),(22,13)],'cream')
  else:
   for x,y,c in [(10,13,'redshade'),(15,11,'dark'),(20,14,'red'),(17,15,'cream'),(12,16,'white')]:a.rect((x,y,x+1,y+1),c)
 elif f=='wine':
  body,hi,lo={'baijiu':('bluelight','white','blue'),'wine':('toast','bread','brown'),'chrysanthemum_wine':('leaf','leaflight','leafdark')}[name]
  a.rect((12,3,19,7),'redshade','dark');a.line([(13,4),(18,4)],'red');a.rect((12,8,19,12),body,'dark');a.poly([(12,11),(19,11),(24,16),(25,24),(21,29),(9,29),(6,24),(7,17)],lo,'dark');a.poly([(12,13),(18,13),(21,17),(21,25),(18,27),(11,27),(9,24),(10,17)],body);a.line([(12,15),(10,19),(10,23)],hi,2);a.rect((13,18,21,25),'cream','toast')
  if name=='chrysanthemum_wine':
   for p in [(16,19),(18,21),(16,23),(14,21)]:a.rect((*p,p[0]+1,p[1]+1),'gold')
   a.dot((16,21),'toast')
  else:a.seal(14,19)
 elif f=='tea':
  if name=='tea':
   a.poly([(6,10),(15,5),(25,10),(27,19),(23,27),(11,28),(5,23)],'leafdark','ink');a.poly([(8,11),(15,7),(23,11),(23,23),(12,25),(7,22)],'leaf');a.rect((10,13,22,21),'cream','toast');a.poly([(14,18),(15,14),(20,14),(17,18)],'leafdark');a.line([(8,10),(13,12),(22,10)],'bread')
  else:
   a.oval((5,22,28,28),'blue','bluedark');a.line([(25,13),(29,13),(29,19),(25,20)],'blue',2);a.poly([(6,12),(25,12),(23,24),(10,24),(7,20)],'blue','bluedark');a.poly([(8,14),(21,14),(21,21),(11,22)],'bluelight');a.oval((6,7,25,15),'white','bluedark');a.oval((8,9,23,13),'brown');a.line([(10,10),(18,10)],'toast')
 return a.im

def build(allowed):
 records=[];(D/'previews').mkdir(exist_ok=True)
 for name,spec in SPEC.items():
  if name not in allowed:continue
  src=S/'textures/item'/f'{name}.png';out=A/'textures/item'/src.name;out.parent.mkdir(parents=True,exist_ok=True)
  before=D/'before'/src.name;before.parent.mkdir(exist_ok=True)
  if not before.exists():shutil.copy2(src,before)
  assert src.read_bytes()==before.read_bytes()
  im=draw(name,spec);alpha=set(im.getchannel('A').tobytes());assert alpha<={0,255} and im.size==(32,32)
  bbox=im.getbbox();assert bbox and bbox[0]>=1 and bbox[1]>=1 and bbox[2]<=31 and bbox[3]<=31,(name,bbox)
  im.save(out)
  model=json.loads((S/'models/item'/f'{name}.json').read_text())
  records.append({'id':'dynasty:'+name,'family':spec['family'],'path':str(out.relative_to(D)),
   'source':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
   'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size':[32,32],'colors':len({p[:3] for p in im.getdata() if p[3]}),'alpha':sorted(alpha),'model_parent':model.get('parent'),'status':'candidate_not_installed'})
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
 for page in range((len(records)+19)//20):
  c=Image.new('RGB',(1120,880),'#e8e9df');d=ImageDraw.Draw(c)
  for j,r in enumerate(records[page*20:page*20+20]):
   name=r['id'].split(':')[1];x=16+j%5*222;y=16+j//5*218;d.text((x,y),name,font=font,fill='#263831')
   for xx,base in [(x,D/'before'),(x+104,A/'textures/item')]:
    im=Image.open(base/(name+'.png')).convert('RGBA');z=im.resize((96,96),Image.Resampling.NEAREST);c.paste(z,(xx,y+30),z);c.paste(im,(xx,y+143),im)
   d.text((x,y+186),'Before / After | native 32',font=font,fill='#64715d')
  c.save(D/'previews'/f'contact-{page+1:02}.png')
 (D/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 print('Core candidates',len(records))

if __name__=='__main__':
 import sys
 allowed=set(json.loads(Path(sys.argv[1]).read_text()))
 build(allowed)

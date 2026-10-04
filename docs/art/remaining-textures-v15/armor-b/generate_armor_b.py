"""Native pixel-authored armor B candidates. Never writes outside this directory.
32px equipment icons and separately authored standard 64x32 humanoid atlases.
No image scaling is used for asset authoring; nearest scaling is preview-only.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse, json, hashlib, shutil, types

HERE=Path(__file__).resolve().parent
ROOT=Path('/Users/a15356015027/Desktop/dynasty')
SOURCE=ROOT/'src/main/resources/assets/dynasty'
CANDIDATE=HERE/'candidate/assets/dynasty'
PIECES=('helmet','chestplate','leggings','boots')
SETS={
 'dark_iron':('玄铁重铠','heavy riveted steel / bronze bindings / small jade clasps',
 '172029 263440 3c5060 596e7c 81959c afbcbc 493b2c 83653f b6965a dfc98b 204547 347d78 74bca9 d0dfc8'),
 'xuanwu':('玄武','overlapping hexagonal shell shields / low heavy profile',
 '142923 243d31 395440 547057 81977a adb797 443e2d 787347 aca468 d2ca90 203c35 347564 74ae89 c4dab2'),
 'zhuque':('朱雀','swept feather pauldrons / flame crest / tapered crimson lames',
 '321c25 562330 83303c b94f49 dc7863 efaa81 573423 9d552b cf873b f1c063 5b2635 963147 d95159 f5bc92'),
 'qinglong':('青龙','horned brow / three rows of scalloped scale armor',
 '122b30 1c4245 2c6261 4c8680 7aaba0 bed0b1 423f2c 7b7042 b1a56a d8cf97 163e49 286879 62adb2 b7dad2'),
 'baihu':('白虎','hook-shaped shoulder guards / ivory steel / short dark stripes',
 '242935 424959 697383 a1aaa9 ced1bb e8e4cd 49443b 817765 b6a88a d6c9a7 253951 395a80 779fc0 bed3d7'),
 'beidou':('北斗','faceted astral breastplate / seven restrained star studs',
 '191e35 283353 3c5079 5e739b 8d9fbd c0c9d1 343e54 667592 9eacc1 d5dacd 292953 4d4787 9188c0 d6d1e0'),
 'tiangang':('天罡','orthogonal Taoist lamellar panels / long central tab',
 '1b2836 2d4357 45647b 6a8da0 9fbcc0 d0d9cb 4c4230 83724a b7a570 ddce92 263b4f 416d8d 86b0c0 d6e1d5'),
 'disha':('地煞','bone inlays over dark iron / three rib plates / jawed greaves',
 '221d24 3c343a 5a5055 7c6d6b a99988 d1c3a7 49352e 765442 a98962 cdb387 3e2b32 6c3947 a56568 d4b8a0'),
 'taiyi':('太乙','pale celadon plates / bifurcated gold yoke / rounded jade fittings',
 '253b37 3f5c4c 62806b 8eaa8e b6c9a3 dfe3bd 544931 8f7746 b9a66b e1ce8d 2c514c 4d897c 8ab8a3 d1dfc0'),
 'ziwei':('紫微','three-point crown / imperial overlapping shoulder and skirt panels',
 '291e35 482d51 6d4375 966397 bd92b4 dac2ca 554035 926b45 c09d64 e3cc92 3b2c60 62478c a086bf d5c7db'),
 'hunyuan':('混元','interlocking curved black-jade plates / quiet green core',
 '172525 283b37 3e574b 5e7562 90a08a c2ccb1 423e30 77704c aba575 d1cca2 193e3f 306762 6faaa0 b8d6c4'),
 'hongmeng':('鸿蒙','tiered crown and shoulders / obsidian-violet core / ivory-gold edge hierarchy',
 '191b2b 2c2c43 44465f 646b88 969eb5 c8cbce 4d3e37 897046 b79b68 decd9a 2e3b58 4d7791 8bb1c2 d0dad4'),
}
KEYS=('o','d','s','m','l','h','bd','b','g','gg','ad','a','al','ah')
def palette(s):return {k:tuple(bytes.fromhex(v))+(255,) for k,v in zip(KEYS,SETS[s][2].split())}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class Pixel:
 def __init__(self,size,p):self.im=Image.new('RGBA',size);self.d=ImageDraw.Draw(self.im);self.p=p
 def r(self,box,c):self.d.rectangle(box,fill=self.p[c])
 def l(self,pts,c,w=1):self.d.line(pts,fill=self.p[c],width=w)
 def q(self,pts,c,edge=None):self.d.polygon(pts,fill=self.p[c],outline=self.p[edge] if edge else None)
 def dot(self,xy,c):self.d.point(xy,fill=self.p[c])
 def clear(self,box):self.d.rectangle(box,fill=(0,0,0,0))
 def gem(self,x,y,c='a'):
  self.q([(x,y-2),(x+2,y),(x,y+2),(x-2,y)],'bd');self.q([(x,y-1),(x+1,y),(x,y+1),(x-1,y)],c);self.dot((x,y-1),'ah')
 def shield(self,box,c='m'):
  x,y,w,h=box;self.q([(x,y),(x+w-1,y),(x+w-1,y+h-3),(x+w//2,y+h-1),(x,y+h-3)],c,'o');self.l([(x+1,y+1),(x+w-2,y+1)],'l')
 def scale(self,x,y,c='m'):
  self.q([(x,y),(x+4,y),(x+4,y+2),(x+2,y+3),(x,y+2)],c,'d');self.l([(x+1,y),(x+3,y)],'l')
 def feather(self,x,y,flip=False,c='m'):
  dx=-1 if flip else 1;self.q([(x,y),(x+3*dx,y+1),(x+4*dx,y+6),(x+dx,y+4)],c,'o');self.l([(x+dx,y+1),(x+2*dx,y+4)],'g')

def helmet(s,p):
 a=Pixel((32,32),p)
 shapes={
 'dark_iron':[(6,7),(10,4),(21,4),(25,7),(26,24),(22,27),(21,17),(10,17),(9,27),(5,24)],
 'xuanwu':[(4,10),(7,6),(12,4),(19,4),(24,6),(27,10),(27,25),(23,27),(21,18),(10,18),(8,27),(4,25)],
 'zhuque':[(6,10),(10,7),(12,5),(13,2),(16,5),(18,2),(20,7),(25,10),(26,23),(23,26),(21,17),(10,17),(8,25),(5,22)],
 'qinglong':[(3,4),(6,5),(8,9),(11,6),(20,6),(23,9),(25,4),(28,3),(27,11),(25,14),(26,24),(22,27),(21,18),(10,18),(9,27),(5,24),(6,14),(3,10)],
 'baihu':[(5,4),(9,6),(12,5),(19,5),(22,6),(26,4),(26,11),(27,24),(22,27),(21,17),(10,17),(9,27),(4,24),(5,11)],
 'beidou':[(6,9),(10,6),(11,3),(14,6),(17,6),(20,3),(22,7),(25,9),(26,24),(22,26),(21,17),(10,17),(9,26),(5,24)],
 'tiangang':[(7,7),(12,7),(12,3),(19,3),(19,7),(24,7),(26,11),(25,26),(21,27),(21,16),(10,16),(10,27),(6,26),(5,11)],
 'disha':[(6,7),(11,4),(20,4),(25,7),(26,12),(25,26),(21,28),(20,17),(11,17),(10,28),(6,26),(5,12)],
 'taiyi':[(6,10),(10,7),(13,7),(15,2),(17,7),(21,7),(25,10),(25,24),(22,26),(21,18),(10,18),(9,26),(6,24)],
 'ziwei':[(5,6),(9,9),(11,4),(14,7),(16,2),(18,7),(21,4),(23,9),(27,6),(26,23),(22,27),(21,18),(10,18),(9,27),(5,23)],
 'hunyuan':[(5,10),(9,6),(13,4),(18,4),(22,6),(26,10),(26,25),(21,27),(21,18),(10,18),(10,27),(5,25)],
 'hongmeng':[(3,4),(6,4),(8,8),(11,7),(12,3),(15,6),(17,6),(20,3),(21,7),(24,8),(26,4),(28,4),(27,13),(25,16),(26,25),(22,28),(21,18),(10,18),(9,28),(5,25),(6,16),(4,13)]}
 a.q(shapes[s],'s','o');a.q([(8,10),(11,8),(20,8),(23,10),(23,14),(8,14)],'m');a.l([(8,12),(10,10),(20,10),(23,12)],'l')
 # The opening is transparent, not a black face painted into an equipment icon.
 a.clear((11,17,20,28));a.clear((10,19,21,25))
 if s=='hongmeng':
  a.l([(4,5),(5,10),(8,13),(11,12)],'g',2);a.l([(27,5),(26,10),(23,13),(20,12)],'b',2)
  a.l([(12,5),(14,8),(17,8),(19,5)],'gg');a.r((9,14,22,16),'bd');a.l([(9,14),(14,15)],'gg');a.l([(17,15),(22,14)],'g');a.gem(15,12)
  a.q([(6,17),(9,18),(8,25),(6,24)],'m');a.q([(23,18),(25,17),(25,24),(23,26)],'d');a.l([(7,18),(7,24)],'g');a.l([(24,18),(24,24)],'b')
 elif s=='xuanwu':
  a.shield((10,6,12,10),'m');a.l([(6,13),(10,15),(21,15),(25,13)],'b',2);a.shield((5,17,5,9),'m');a.shield((22,17,5,9),'s');a.r((13,8,18,9),'l');a.l([(13,11),(15,13),(18,11)],'d');a.l([(12,7),(15,7)],'g');a.dot((12,7),'gg')
 elif s=='zhuque':
  a.q([(13,4),(16,8),(18,4),(19,11),(15,14),(12,10)],'g','bd');a.l([(14,6),(15,10),(17,8)],'gg');a.feather(6,13);a.feather(25,13,True);a.l([(10,15),(15,16),(21,15)],'g');a.l([(9,10),(10,9)],'h')
 elif s=='qinglong':
  a.l([(4,5),(5,9),(8,11)],'gg',2);a.l([(27,5),(26,9),(23,11)],'g',2)
  for x,y in [(9,10),(14,9),(19,10),(6,17),(22,17)]:a.scale(x,y)
  a.l([(9,15),(14,16),(17,16),(22,15)],'b');a.gem(15,13)
 elif s=='baihu':
  a.q([(6,6),(8,7),(9,10),(6,11)],'h');a.q([(23,7),(25,6),(25,11),(22,10)],'l');a.l([(9,10),(12,12)],'d',2);a.l([(22,10),(19,12)],'d',2);a.l([(10,15),(21,15)],'h');a.l([(6,18),(8,20),(6,22)],'d');a.l([(25,18),(23,20),(25,22)],'d');a.gem(15,12)
 elif s=='beidou':
  a.q([(15,7),(19,11),(15,15),(11,11)],'l','d');a.dot((15,10),'ah');a.l([(7,14),(10,16),(21,16),(24,14)],'h');a.l([(7,18),(8,23)],'b');a.l([(24,18),(23,23)],'b');a.dot((11,5),'h');a.dot((20,5),'h')
 elif s=='tiangang':
  a.r((13,4,18,9),'b');a.r((14,5,17,8),'g');a.r((7,13,24,16),'d');a.l([(8,14),(23,14)],'g');a.r((7,18,9,24),'m');a.r((22,18,24,24),'m');a.gem(15,12)
 elif s=='disha':
  a.q([(8,10),(12,8),(19,8),(23,10),(22,14),(18,12),(13,12),(9,14)],'h','d');a.l([(7,17),(9,20),(8,25)],'l',2);a.l([(24,17),(22,20),(23,25)],'l',2);a.r((14,8,17,9),'s');a.dot((15,7),'g');a.dot((14,7),'gg')
 elif s=='taiyi':
  a.q([(15,4),(17,8),(20,9),(19,13),(15,15),(11,13),(10,9),(13,8)],'g','bd');a.gem(15,10);a.l([(7,15),(10,16),(21,16),(24,15)],'gg');a.l([(8,19),(8,24)],'g');a.l([(23,19),(23,24)],'g')
 elif s=='ziwei':
  a.l([(6,8),(9,11),(12,7),(15,10),(17,10),(20,7),(23,11),(26,8)],'g',2);a.r((7,13,24,16),'bd');a.l([(8,14),(23,14)],'gg');a.gem(15,13);a.l([(7,18),(8,24)],'g');a.l([(24,18),(23,24)],'g')
 elif s=='hunyuan':
  a.q([(8,9),(13,6),(18,6),(21,9),(17,11),(12,12),(8,14)],'l','d');a.q([(23,10),(20,12),(15,13),(10,15),(21,16),(24,14)],'m','d');a.gem(16,11);a.l([(7,18),(9,24)],'b');a.l([(24,18),(22,24)],'b')
 else:
  a.r((7,13,24,16),'b');a.l([(8,14),(23,14)],'g');a.r((14,6,17,12),'d');a.l([(14,6),(14,11)],'l');a.gem(15,12);a.l([(7,18),(7,25)],'g');a.l([(24,18),(24,25)],'b')
 return a.im

def chest(s,p):
 if s=='dark_iron':
  im=Image.open(ROOT/'docs/art/armor-sample-v14/candidate/assets/dynasty/textures/item/dark_iron_chestplate.png').convert('RGBA')
  # Preserve accepted sample structure; refine breastplate joints and lames only.
  d=ImageDraw.Draw(im);d.line([(10,14),(11,14)],fill=p['l']);d.point((20,15),fill=p['m']);d.line([(11,22),(13,22)],fill=p['s']);d.point((19,24),fill=p['l']);return im
 a=Pixel((32,32),p)
 shapes={
 'xuanwu':[(2,7),(5,4),(11,5),(12,8),(19,8),(20,5),(26,4),(29,7),(29,15),(25,17),(24,27),(21,29),(10,29),(7,27),(6,17),(2,15)],
 'zhuque':[(2,3),(7,5),(11,6),(12,9),(19,9),(20,6),(24,5),(29,3),(28,11),(25,17),(23,17),(23,23),(19,27),(16,30),(12,27),(8,23),(8,17),(6,17),(3,11)],
 'qinglong':[(3,6),(7,3),(11,6),(12,9),(19,9),(21,5),(25,3),(28,6),(28,14),(25,16),(24,26),(20,29),(11,29),(7,26),(6,16),(3,14)],
 'baihu':[(2,4),(6,4),(9,7),(11,5),(12,9),(19,9),(20,5),(23,7),(25,4),(29,4),(28,11),(25,15),(24,15),(24,25),(21,28),(10,28),(7,25),(7,15),(6,15),(3,11)],
 'beidou':[(3,5),(9,4),(12,8),(19,8),(22,4),(28,5),(29,12),(25,16),(23,16),(23,26),(19,29),(12,29),(8,26),(8,16),(6,16),(2,12)],
 'tiangang':[(5,5),(10,5),(12,8),(19,8),(21,5),(26,5),(28,9),(27,14),(24,14),(24,25),(21,28),(17,28),(17,30),(14,30),(14,28),(10,28),(7,25),(7,14),(4,14),(3,9)],
 'disha':[(3,8),(5,5),(10,4),(12,8),(19,8),(21,4),(26,5),(28,8),(28,14),(24,16),(23,25),(20,29),(11,29),(8,25),(7,16),(3,14)],
 'taiyi':[(4,8),(7,5),(11,5),(13,9),(18,9),(20,5),(24,5),(27,8),(27,13),(24,16),(23,25),(20,28),(11,28),(8,25),(7,16),(4,13)],
 'ziwei':[(2,7),(6,3),(10,4),(12,8),(19,8),(21,4),(25,3),(29,7),(28,15),(24,17),(24,25),(21,29),(10,29),(7,25),(7,17),(3,15)],
 'hunyuan':[(3,8),(6,4),(11,6),(13,9),(18,9),(20,6),(25,4),(28,8),(27,14),(24,16),(24,24),(21,28),(10,28),(7,24),(7,16),(4,14)],
 'hongmeng':[(1,7),(4,3),(9,3),(12,8),(19,8),(22,3),(27,3),(30,7),(29,15),(26,17),(24,17),(24,25),(22,29),(9,29),(7,25),(7,17),(5,17),(2,15)]}
 a.q(shapes[s],'s','o');a.q([(9,10),(12,10),(14,12),(17,12),(19,10),(22,10),(22,24),(20,27),(11,27),(9,24)],'m','d')
 a.l([(11,6),(12,9),(15,11),(17,11),(19,9),(20,6)],'g')
 if s=='hongmeng':
  for x,flip in [(3,False),(28,True)]:
   dx=-1 if flip else 1
   a.q([(x,7),(x+2*dx,4),(x+5*dx,4),(x+8*dx,9),(x+6*dx,12),(x+dx,11)],'b','o')
   a.l([(x+dx,7),(x+3*dx,5),(x+5*dx,5),(x+7*dx,8)],'gg')
   a.q([(x,11),(x+6*dx,12),(x+8*dx,10),(x+7*dx,14),(x+2*dx,15)],'m','d');a.l([(x+dx,12),(x+5*dx,13)],'g')
  a.q([(9,12),(12,12),(15,16),(12,19),(9,17)],'l','d');a.q([(22,12),(19,12),(16,16),(19,19),(22,17)],'s','d')
  a.l([(10,13),(12,13),(14,15)],'h');a.l([(21,13),(19,13),(17,15)],'l');a.gem(15,16)
  for y,w in [(20,10),(23,8)]:a.q([(15-w//2,y),(15+w//2,y),(15+w//2,y+1),(15,y+3),(15-w//2,y+1)],'s','d');a.l([(15-w//2+1,y),(15+w//2-1,y)],'l')
  a.r((9,26,22,27),'b');a.l([(10,26),(21,26)],'gg');a.r((14,25,17,28),'bd');a.r((15,26,16,27),'al');a.dot((15,26),'ah')
 elif s=='xuanwu':
  a.shield((3,6,8,10),'m');a.shield((21,6,8,10),'s');a.shield((10,11,12,10),'m');a.shield((8,21,7,7),'s');a.shield((16,21,7,7),'s');a.l([(13,14),(18,14)],'l');a.l([(12,17),(15,19),(19,17)],'g');a.gem(15,12)
 elif s=='zhuque':
  for x,y in [(4,5),(7,7),(9,10)]:a.feather(x,y);a.feather(31-x,y,True,'s')
  a.q([(12,12),(15,15),(19,12),(21,16),(18,19),(15,23),(12,19),(10,16)],'g','bd');a.l([(12,13),(15,17),(19,13)],'gg');a.gem(15,17)
  for y in (21,24):a.l([(10,y),(15,y+3),(21,y)],'b');a.l([(11,y),(15,y+2)],'l')
 elif s=='qinglong':
  a.q([(4,7),(8,4),(11,8),(9,12),(4,12)],'b','o');a.q([(20,8),(24,4),(27,7),(27,12),(22,12)],'b','o')
  for y in (11,15,19):
   for x in (9,14,19):a.scale(x,y,'m' if x<19 else 's')
  a.l([(5,14),(9,15)],'g');a.l([(22,15),(26,14)],'g');a.r((9,24,22,25),'b');a.gem(15,25)
 elif s=='baihu':
  a.q([(3,5),(6,5),(10,10),(9,14),(6,12),(4,9)],'h','d');a.q([(25,5),(28,5),(27,9),(25,12),(22,14),(21,10)],'l','d')
  a.q([(10,12),(14,12),(15,17),(13,20),(9,17)],'h','s');a.q([(17,12),(21,12),(22,17),(18,20),(16,17)],'l','s');a.l([(10,14),(12,15)],'d',2);a.l([(21,14),(19,15)],'d',2);a.gem(15,16)
  a.r((9,22,22,23),'d');a.l([(10,24),(21,24)],'l');a.r((9,26,22,26),'b')
 elif s=='beidou':
  a.q([(3,7),(9,5),(12,10),(8,14),(3,12)],'l','d');a.q([(22,5),(28,7),(28,12),(23,14),(20,10)],'m','d')
  a.q([(15,11),(22,16),(19,22),(15,25),(11,22),(9,16)],'s','b');a.l([(11,15),(14,17),(17,16),(19,18),(17,21),(14,21),(12,23)],'m')
  for xy in [(11,15),(14,17),(17,16),(19,18),(17,21),(14,21),(12,23)]:a.dot(xy,'h')
  a.r((10,26,21,27),'b');a.dot((15,26),'ah')
 elif s=='tiangang':
  for x in (5,22):a.r((x,6,x+4,12),'b');a.r((x+1,7,x+3,10),'l');a.l([(x,13),(x+4,13)],'g')
  for x in (9,17):
   for y in (12,16,20):a.r((x,y,x+5,y+2),'s');a.l([(x+1,y),(x+4,y)],'l')
  a.r((14,11,16,27),'bd');a.l([(15,12),(15,26)],'g');a.r((14,27,16,29),'m');a.gem(15,15)
 elif s=='disha':
  a.q([(4,8),(6,6),(9,6),(11,11),(9,13),(4,12)],'l','d');a.q([(21,11),(23,6),(26,6),(27,8),(27,12),(22,13)],'h','d')
  for y in (12,16,20):a.l([(10,y),(12,y+2),(14,y+2)],'h',2);a.l([(21,y),(19,y+2),(17,y+2)],'l',2)
  a.r((15,12,16,23),'d');a.r((9,25,22,26),'b');a.gem(15,25,'a')
 elif s=='taiyi':
  a.q([(5,8),(8,6),(10,7),(11,12),(8,15),(5,12)],'l','b');a.q([(21,7),(23,6),(26,8),(26,12),(23,15),(20,12)],'m','b')
  a.l([(10,12),(15,17),(21,12)],'gg',2);a.l([(15,18),(15,24)],'g',2);a.q([(10,15),(13,18),(13,22),(10,23),(9,19)],'l');a.q([(21,15),(17,18),(17,22),(21,23),(22,19)],'s');a.gem(15,16);a.r((10,26,21,26),'g')
 elif s=='ziwei':
  for x,dx in [(3,1),(28,-1)]:
   a.q([(x,8),(x+3*dx,4),(x+7*dx,5),(x+9*dx,10),(x+7*dx,13),(x+dx,13)],'b','o');a.l([(x+dx,8),(x+3*dx,6),(x+6*dx,6)],'gg');a.l([(x+dx,14),(x+7*dx,15)],'g')
  a.q([(15,11),(21,15),(20,20),(15,24),(10,20),(9,15)],'b','bd');a.q([(15,13),(19,16),(18,20),(15,22),(12,20),(11,16)],'m');a.gem(15,17)
  a.r((9,25,22,26),'g');a.l([(10,27),(13,28)],'b');a.l([(18,28),(21,27)],'b')
 elif s=='hunyuan':
  a.q([(4,8),(7,5),(10,8),(10,12),(6,14),(4,12)],'m','b');a.q([(21,8),(24,5),(27,8),(27,12),(23,14),(21,12)],'s','b')
  a.q([(10,11),(15,13),(18,18),(16,23),(11,23),(9,20),(12,17)],'l','d');a.q([(20,12),(22,16),(20,21),(15,23),(13,20),(17,18),(15,15)],'s','d');a.l([(11,12),(14,14),(15,17)],'g');a.l([(20,14),(20,18),(17,21)],'b');a.gem(15,17)
  a.r((9,25,22,26),'b');a.l([(11,27),(20,27)],'m')
 return a.im

def leggings(s,p):
 a=Pixel((32,32),p)
 # Cut differs per suit: hips, split depth, thigh width, and knee/ankle taper.
 configs={'dark_iron':(6,25,4,13,10,22,28),'xuanwu':(4,27,4,15,10,22,29),'zhuque':(7,24,3,12,9,23,29),'qinglong':(5,26,4,14,10,22,28),'baihu':(6,25,3,12,9,23,28),'beidou':(5,26,5,14,11,21,29),'tiangang':(7,24,3,15,10,22,29),'disha':(6,25,4,13,10,22,30),'taiyi':(7,24,4,12,9,23,28),'ziwei':(5,26,3,15,11,21,29),'hunyuan':(6,25,5,14,10,22,29),'hongmeng':(4,27,3,15,11,21,29)}
 left,right,top,split,li,ri,bottom=configs[s]
 a.q([(left,top),(right,top),(right,11),(right-2,bottom),(18,bottom),(17,split),(14,split),(13,bottom),(left+2,bottom),(left,11)],'s','o')
 a.r((left+1,top+1,right-1,top+3),'b');a.l([(left+2,top+1),(right-2,top+1)],'g');a.r((14,top,17,top+4),'bd');a.r((15,top+1,16,top+2),'al')
 a.q([(left+2,top+5),(13,top+5),(12,bottom-2),(left+3,bottom-2)],'m');a.q([(18,top+5),(right-2,top+5),(right-3,bottom-2),(19,bottom-2)],'m')
 if s=='hongmeng':
  for x,dx in [(5,1),(26,-1)]:
   a.q([(x,8),(x+6*dx,9),(x+7*dx,14),(x+4*dx,17),(x+dx,15)],'b','d');a.l([(x+dx,9),(x+5*dx,10)],'gg');a.shield((min(x+dx,x+5*dx),18,5,8),'l')
  a.r((8,26,12,27),'b');a.r((19,26,23,27),'b');a.l([(9,20),(10,23)],'h');a.l([(21,20),(21,23)],'l')
 elif s=='xuanwu':
  for x in (6,18):a.shield((x,9,8,10),'m');a.shield((x+1,20,6,7),'s');a.l([(x+2,12),(x+5,12)],'l')
 elif s=='zhuque':
  for x,flip in [(9,False),(22,True)]:
   for y in (8,13,18):a.feather(x,y,flip)
  a.l([(9,26),(12,27)],'g');a.l([(19,27),(22,26)],'g');a.l([(10,9),(10,10)],'h');a.l([(21,9),(21,10)],'h')
 elif s=='qinglong':
  for y in (9,13,17,21):
   a.scale(7,y);a.scale(19,y,'s')
  a.l([(8,26),(12,26)],'g');a.l([(19,26),(23,26)],'g')
 elif s=='baihu':
  a.q([(8,9),(12,10),(12,16),(9,18),(7,15)],'h','d');a.q([(19,10),(23,9),(24,15),(21,18),(19,16)],'l','d')
  for y in (11,15,22):a.l([(8,y),(11,y+1)],'d');a.l([(23,y),(20,y+1)],'d')
  a.shield((8,19,5,7),'l');a.shield((19,19,5,7),'m')
 elif s=='beidou':
  for x in (10,21):a.q([(x,10),(x+3,14),(x,18),(x-3,14)],'l','d');a.gem(x,21);a.l([(x-2,26),(x+1,26)],'g')
 elif s=='tiangang':
  for x in (8,18):
   for y in (9,14,19):a.r((x,y,x+5,y+3),'s');a.l([(x+1,y),(x+4,y)],'l')
  a.r((14,8,17,14),'bd');a.l([(15,9),(15,13)],'g')
 elif s=='disha':
  for x in (9,21):a.l([(x-1,10),(x+1,13),(x,16)],'h',2);a.shield((x-2,18,5,7),'l');a.l([(x,20),(x,23)],'d')
 elif s=='taiyi':
  a.l([(9,9),(12,12),(11,18)],'gg');a.l([(22,9),(19,12),(20,18)],'g')
  for x in (10,21):a.shield((x-2,18,5,7),'l');a.gem(x,20)
 elif s=='ziwei':
  a.q([(7,8),(13,9),(13,16),(10,19),(7,16)],'b','d');a.q([(18,9),(24,8),(24,16),(21,19),(18,16)],'b','d');a.l([(8,9),(11,10),(11,16)],'g');a.l([(23,9),(20,10),(20,16)],'g')
  for x in (10,21):a.shield((x-2,20,5,7),'m');a.dot((x,21),'al')
 elif s=='hunyuan':
  a.q([(8,10),(13,12),(12,17),(9,20),(7,17)],'l','d');a.q([(23,10),(18,12),(19,17),(22,20),(24,17)],'s','d');a.l([(8,12),(10,15),(9,18)],'b');a.l([(23,12),(21,15),(22,18)],'g')
  for x in (9,21):a.r((x-1,22,x+2,26),'s');a.l([(x,22),(x+1,22)],'l')
 else:
  for x in (8,19):
   for y in (9,13,17):a.r((x,y,x+4,y+2),'s');a.l([(x+1,y),(x+3,y)],'l')
   a.shield((x,21,5,6),'m');a.dot((x+2,22),'g')
 return a.im

def boots(s,p):
 a=Pixel((32,32),p)
 conf={'dark_iron':(4,9,27,5),'xuanwu':(3,10,28,4),'zhuque':(6,8,28,3),'qinglong':(5,9,27,4),'baihu':(4,10,27,5),'beidou':(5,9,28,6),'tiangang':(6,8,29,4),'disha':(4,9,29,5),'taiyi':(6,8,27,4),'ziwei':(4,10,28,3),'hunyuan':(5,9,27,5),'hongmeng':(3,10,29,3)}
 x,w,bottom,top=conf[s]
 for mirror in (False,True):
  def pts(v):return [(31-xx if mirror else xx,yy) for xx,yy in v]
  a.q(pts([(x,top),(x+w-1,top),(x+w-1,bottom-3),(x+w-2,bottom),(x-1,bottom),(x-2,bottom-2),(x-2,bottom-5),(x,bottom-7)]),'s','o')
  a.q(pts([(x+1,top+3),(x+w-2,top+3),(x+w-2,bottom-5),(x,bottom-4)]),'m')
  a.l(pts([(x,top+1),(x+w-2,top+1)]),'g');a.l(pts([(x-1,bottom-1),(x+w-2,bottom-1)]),'d',2)
  if s=='hongmeng':
   for y in (top+3,top+7):a.q(pts([(x,y),(x+w-1,y),(x+w-2,y+3),(x+1,y+3)]),'b','d');a.l(pts([(x+1,y),(x+w-2,y)]),'gg')
   a.q(pts([(x+2,15),(x+6,15),(x+6,22),(x+4,24),(x+1,22)]),'l','d');a.l(pts([(x+2,16),(x+4,16)]),'h');a.l(pts([(x-1,bottom-4),(x+w-2,bottom-4)]),'g')
  elif s=='xuanwu':
   a.q(pts([(x+1,top+4),(x+7,top+4),(x+7,top+11),(x+4,top+14),(x+1,top+11)]),'m','d');a.l(pts([(x+2,top+6),(x+6,top+6)]),'l');a.l(pts([(x,23),(x+7,23)]),'b',2)
  elif s=='zhuque':
   for y in (top+4,top+9,top+14):a.q(pts([(x+1,y),(x+5,y-1),(x+5,y+3),(x+2,y+5)]),'g','bd')
   a.l(pts([(x-1,bottom-3),(x+5,bottom-4)]),'gg')
  elif s=='qinglong':
   for y in (top+4,top+9,top+14):a.q(pts([(x+1,y),(x+6,y),(x+6,y+2),(x+3,y+4),(x+1,y+2)]),'m','d');a.l(pts([(x+2,y),(x+5,y)]),'l')
   a.dot(pts([(x+1,bottom-3)])[0],'gg');a.dot(pts([(x+4,bottom-3)])[0],'g')
  elif s=='baihu':
   a.q(pts([(x+1,top+4),(x+7,top+4),(x+7,top+12),(x+5,top+16),(x+1,top+13)]),'l','d')
   for y in (top+5,top+10,top+15):a.l(pts([(x+1,y),(x+4,y+1)]),'d',2)
   a.l(pts([(x-1,bottom-4),(x+6,bottom-4)]),'h');a.dot(pts([(x+3,bottom-3)])[0],'d')
  elif s=='beidou':
   a.q(pts([(x+4,top+4),(x+7,top+8),(x+4,top+12),(x+1,top+8)]),'l','d');a.dot(pts([(x+4,top+7)])[0],'ah');a.l(pts([(x+1,22),(x+6,22)]),'g');a.l(pts([(x-1,bottom-3),(x+5,bottom-3)]),'l')
  elif s=='tiangang':
   for y in (top+5,top+10,top+15):a.l(pts([(x+1,y),(x+5,y+2)]),'g',2)
   a.l(pts([(x+2,top+3),(x+2,top+17)]),'d');a.l(pts([(x-1,bottom-3),(x+5,bottom-3)]),'l')
  elif s=='disha':
   a.q(pts([(x+2,top+4),(x+5,top+4),(x+6,top+8),(x+4,top+11),(x+5,top+16),(x+2,top+16)]),'l','d');a.l(pts([(x+3,top+5),(x+3,top+8)]),'h');a.l(pts([(x-1,bottom-4),(x+6,bottom-4)]),'h')
  elif s=='taiyi':
   a.q(pts([(x+2,top+4),(x+5,top+4),(x+6,top+8),(x+5,top+15),(x+2,top+16),(x+1,top+8)]),'l','b');a.l(pts([(x+3,top+6),(x+4,top+10)]),'h');a.l(pts([(x-1,bottom-3),(x+5,bottom-3)]),'g')
  elif s=='ziwei':
   a.r((0,0,-1,-1),'s') if False else None
   a.q(pts([(x,top+3),(x+8,top+3),(x+7,top+8),(x+4,top+10),(x+1,top+8)]),'b','d');a.l(pts([(x+1,top+4),(x+7,top+4)]),'gg');a.l(pts([(x+2,top+11),(x+2,top+19)]),'g');a.l(pts([(x-1,bottom-4),(x+7,bottom-4)]),'b')
  elif s=='hunyuan':
   a.q(pts([(x+1,top+5),(x+4,top+3),(x+7,top+6),(x+5,top+10),(x+2,top+11)]),'l','d');a.q(pts([(x+5,top+10),(x+7,top+13),(x+4,top+19),(x+1,top+16)]),'s','d');a.l(pts([(x+2,top+6),(x+4,top+8)]),'g');a.l(pts([(x-1,bottom-3),(x+6,bottom-3)]),'b')
  else:
   for y in (top+5,top+10,top+15):a.l(pts([(x+1,y),(x+6,y)]),'l');a.l(pts([(x+1,y+2),(x+6,y+2)]),'d')
   a.l(pts([(x-1,bottom-4),(x+6,bottom-4)]),'b')
  # Short cuff light and toe-joint shadow are coherent material planes, not noise.
  a.l(pts([(x+1,top+2),(x+3,top+2)]),'h');a.l(pts([(x-1,bottom-5),(x+1,bottom-5)]),'bd')
 return a.im

def tile(p,w,h,base='s'):
 a=Pixel((w,h),p);a.r((0,0,w-1,h-1),base);return a

def armor_atlases(s,p):
 """Independent native UV patterns. No inventory pixels are sampled here."""
 one=Image.new('RGBA',(64,32));two=Image.new('RGBA',(64,32))
 def put(im,x,y,t):im.paste(t.im if isinstance(t,Pixel) else t,(x,y))
 # Each set has its own compact breastplate construction, authored at 8x12.
 fronts={
 'dark_iron':['bdoooodb','slgbbgls','mllggmms','mllaalms','smmhalms','obmaamdo','ssmggmss','mllssmms','osssssso','mllssmms','bggaaggb','osssssso'],
 'xuanwu':['bsoooosb','blmmmmgb','smllllms','smlddlms','smlddlms','osmmmmso','bsmmmsgb','mldoodlm','smdoodms','osmmmmso','bggggggb','dssddssd'],
 'zhuque':['bdoooodb','glsddslg','mglddlgm','smgllgms','dsmggmsd','mdsggsdm','lmdggdml','slmggmls','dslgglsd','mdsggsdm','sggllggs','odsmmsdo'],
 'qinglong':['bsoooosb','gmsbbsmg','smllmlms','dsmsmssd','mllmllml','smsmsmsm','dsmsmssd','smllmlms','dsmsmssd','mllmllml','bggggggb','osssssso'],
 'baihu':['ldoooodl','hlsddsll','hhlddlhh','mdhmmdlm','mmhmmdmm','dlmllmld','slmaamls','dlmllmld','mhmdmhml','mmhddhmm','bggggggb','osssssso'],
 'beidou':['lsoooosl','mlsddsmm','smlmmlms','dsmllmsd','smhmmsms','mlmmhmlm','slhmlmms','dslmhlsd','sdhmhmsd','dsmmmlsd','bggggggb','odssssdo'],
 'tiangang':['bsoooosb','gmsggsmg','smmbbmms','sllgglls','oddbbddo','smmbbmms','sllgglls','oddbbddo','smmbbmms','sllgglls','bggbbggb','dsdggdsd'],
 'disha':['lsoooosl','hmlddlmh','dhml lmhd'.replace(' ',''),'sdhmmhds','lmdssdmh','dhmddmhd','sdhmmhds','lmdssdmh','dhmddmhd','sdhmmhds','bggggggb','dssddssd'],
 'taiyi':['gsoooosg','glsddslg','mlgddglm','lmlgglml','sllgglls','dmlaalmd','slmhalms','slmggmls','smlgglms','mllggllm','bggggggb','odssssdo'],
 'ziwei':['bsoooosb','ggsddsgg','mlgbbglm','slgmmgls','dgmllmgd','gmlaalmg','dgmhalgd','slgmmgls','mlgbbglm','dsggggsd','bggggggb','dsbssbsd'],
 'hunyuan':['bsoooosb','mlsddsmg','mllsdslm','smllmdlm','dsmlaaml','slmaamld','mllamlds','mlmsldss','smlldsms','dsmmmlsd','bggggggb','odssssdo'],
 'hongmeng':['bsoooosb','ggsddsgg','mlgbbglm','hmlgglms','slmaalms','dsmhalmd','gmsggsmg','dlmssmld','sllgglls','dsmllmsd','bggalggb','dsbssbsd'],
 }
 rows=fronts[s];assert all(len(x)==8 for x in rows),(s,rows)
 def rows_tile(rows):
  t=Image.new('RGBA',(len(rows[0]),len(rows)));t.putdata([p[c] if c!='.' else (0,0,0,0) for row in rows for c in row]);return t
 put(one,20,20,rows_tile(rows))
 # Back plates differ by construction, and remain quieter than the chest.
 back=tile(p,8,12,'s');back.l([(0,0),(7,0)],'b');back.l([(1,1),(6,1)],'m');back.l([(0,10),(7,10)],'g')
 if s in ('xuanwu','hongmeng','ziwei'):
  back.shield((1,2,6,7),'m');back.l([(2,3),(5,3)],'l');back.l([(1,8),(6,8)],'b')
 elif s=='qinglong':
  for y in (2,5,8):back.scale(0,y);back.scale(4,y,'s')
 elif s=='zhuque':
  for y in (2,5,8):back.l([(1,y),(3,y+2),(6,y)],'g')
 elif s=='disha':
  for y in (2,5,8):back.l([(1,y),(3,y+1),(6,y)],'l');back.l([(3,2),(3,9)],'d')
 elif s=='beidou':
  back.q([(3,2),(6,5),(3,8),(1,5)],'m','d');back.dot((3,4),'h')
 elif s=='hunyuan':
  back.q([(1,2),(4,2),(6,5),(4,8),(1,7),(3,5)],'m','d');back.dot((3,4),'a')
 else:
  for y in (3,6,8):back.l([(1,y),(6,y)],'m');back.l([(1,y+1),(6,y+1)],'d')
 put(one,32,20,back)
 side=tile(p,4,12,'s');side.l([(0,0),(3,0)],'b');side.l([(0,10),(3,10)],'g')
 for y in (3,6,8):side.l([(0,y),(3,y)],'d');side.l([(1,y+1),(2,y+1)],'m')
 put(one,16,20,side);put(one,28,20,side.im.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
 top=tile(p,8,4,'s');top.l([(0,0),(7,0)],'b');top.l([(0,1),(7,1)],'m');put(one,20,16,top);put(one,28,16,tile(p,8,4,'d'))
 # Shared arm UV is mirrored by the vanilla left-arm cube. No second hand atlas.
 arm=tile(p,4,12,'s');arm.l([(0,0),(3,0)],'g');arm.r((1,1,2,2),'l')
 if s in ('hongmeng','ziwei'):arm.l([(0,3),(3,3)],'b');arm.l([(0,4),(3,4)],'g');arm.r((1,5,2,6),'m')
 elif s=='xuanwu':arm.q([(0,1),(3,1),(3,4),(1,5),(0,4)],'m','d');arm.r((1,2,2,3),'l')
 elif s=='zhuque':
  for y in (2,5,8):arm.l([(0,y),(2,y+2),(3,y)],'g')
 elif s=='qinglong':
  for y in (2,5,8):arm.q([(0,y),(3,y),(3,y+1),(1,y+2),(0,y+1)],'m','d')
 elif s=='baihu':arm.r((0,2,3,6),'l');arm.l([(0,3),(2,4)],'d');arm.l([(0,6),(2,7)],'d')
 elif s=='disha':arm.r((1,2,2,5),'l');arm.dot((1,2),'h');arm.l([(0,7),(2,8)],'l')
 elif s=='beidou':arm.q([(1,2),(3,4),(1,6),(0,4)],'l','d');arm.dot((1,3),'h')
 elif s=='hunyuan':arm.l([(0,2),(2,3),(1,5),(3,6)],'l')
 elif s=='taiyi':arm.r((1,2,2,5),'l');arm.l([(0,6),(3,6)],'g')
 else:
  for y in (3,6,8):arm.l([(0,y),(3,y)],'d');arm.l([(1,y+1),(2,y+1)],'m')
 arm.l([(0,10),(3,10)],'g');arm.l([(0,11),(3,11)],'d')
 for x in (40,44,48,52):put(one,x,20,arm)
 cap=tile(p,4,4,'m');cap.l([(0,0),(3,0),(3,3),(0,3),(0,0)],'b');cap.r((1,1,2,2),'l');put(one,44,16,cap);put(one,48,16,tile(p,4,4,'d'))
 # Helmet standard head island: clear central face; cheeks stay on side columns.
 hf=tile(p,8,8,'s');hf.r((0,0,7,1),'m');hf.l([(0,2),(7,2)],'g');hf.r((1,0,6,0),'l');hf.clear((2,3,5,7));hf.clear((1,4,6,7));hf.l([(0,3),(0,6)],'b');hf.l([(7,3),(7,6)],'b')
 if s in ('hongmeng','ziwei'):hf.r((2,0,5,0),'b');hf.dot((3,1),'al');hf.dot((4,1),'a');hf.dot((1,1),'gg');hf.dot((6,1),'g')
 elif s=='baihu':hf.l([(0,0),(2,1)],'d');hf.l([(7,0),(5,1)],'d')
 elif s=='zhuque':hf.q([(3,0),(5,2),(2,2)],'gg')
 elif s=='qinglong':hf.dot((1,0),'gg');hf.dot((6,0),'g');hf.dot((3,1),'al')
 elif s=='disha':hf.l([(0,1),(2,2)],'h');hf.l([(7,1),(5,2)],'l')
 elif s=='beidou':hf.dot((2,1),'h');hf.dot((5,0),'h')
 elif s=='hunyuan':hf.l([(1,0),(3,1),(5,0)],'l');hf.dot((4,1),'al')
 else:hf.dot((3,1),'al');hf.dot((4,1),'a')
 put(one,8,8,hf)
 for x in (0,16,24):
  ht=tile(p,8,8,'s');ht.l([(0,2),(7,2)],'b');ht.l([(1,1),(6,1)],'m');ht.l([(0,7),(7,7)],'d');ht.r((2,4,5,5),'m')
  if s in ('hongmeng','ziwei','qinglong'):ht.l([(3,0),(3,6)],'b')
  if s=='baihu':ht.l([(2,3),(4,5),(3,6)],'d')
  put(one,x,8,ht)
 ht=tile(p,8,8,'m');ht.r((1,1,6,6),'s');ht.l([(2,1),(5,1)],'l')
 if s in ('hongmeng','ziwei','tiangang'):ht.l([(3,0),(3,7)],'b');ht.l([(4,0),(4,7)],'g')
 elif s=='qinglong':ht.scale(1,1);ht.scale(2,4)
 elif s=='hunyuan':ht.q([(2,1),(5,2),(6,5),(3,6),(1,4)],'m','d')
 put(one,8,0,ht);put(one,16,0,tile(p,8,8,'d'))
 # Leggings inner layer: body visible only at the waist; full shared mirrored legs.
 waist=Pixel((8,12),p);waist.r((0,8,7,11),'s');waist.l([(0,8),(7,8)],'g');waist.r((3,8,4,9),'a');put(two,20,20,waist)
 wb=Pixel((8,12),p);wb.r((0,8,7,11),'s');wb.l([(0,8),(7,8)],'b');put(two,32,20,wb)
 ws=Pixel((4,12),p);ws.r((0,8,3,11),'s');ws.l([(0,8),(3,8)],'b');put(two,16,20,ws);put(two,28,20,ws)
 leg=tile(p,4,12,'s');leg.l([(0,0),(3,0)],'b');leg.r((1,1,2,4),'m')
 if s=='hongmeng':leg.l([(0,2),(3,2)],'g');leg.q([(0,4),(3,4),(3,7),(1,8),(0,7)],'l','d');leg.dot((1,5),'h')
 elif s=='ziwei':leg.r((0,2,3,7),'b');leg.r((1,3,2,6),'m');leg.l([(0,2),(2,2)],'g');leg.dot((1,8),'a')
 elif s=='xuanwu':leg.q([(0,2),(3,2),(3,6),(1,8),(0,6)],'m','d');leg.r((1,3,2,4),'l')
 elif s=='zhuque':
  for y in (1,4,7):leg.l([(0,y),(2,y+2),(3,y)],'g')
 elif s=='qinglong':
  for y in (1,4,7):leg.q([(0,y),(3,y),(3,y+1),(1,y+2),(0,y+1)],'m','d')
 elif s=='baihu':leg.r((0,2,3,8),'l');leg.l([(0,3),(2,4)],'d');leg.l([(0,6),(2,7)],'d')
 elif s=='disha':leg.r((1,2,2,6),'l');leg.l([(0,7),(3,7)],'h');leg.dot((1,3),'h')
 elif s=='beidou':leg.q([(1,2),(3,4),(1,7),(0,4)],'l','d');leg.dot((1,4),'h')
 elif s=='taiyi':leg.r((1,2,2,7),'l');leg.l([(0,5),(3,5)],'g')
 elif s=='hunyuan':leg.l([(0,2),(2,3),(1,5),(3,7)],'l');leg.l([(0,8),(3,8)],'b')
 elif s=='tiangang':leg.r((0,2,1,7),'m');leg.r((2,2,3,7),'s');leg.l([(1,1),(1,8)],'g');leg.l([(0,4),(3,4)],'d')
 else:
  for y in (2,5,8):leg.l([(0,y),(3,y)],'l');leg.l([(0,y+1),(3,y+1)],'d')
 leg.l([(0,10),(3,10)],'d')
 for x in (0,4,8,12):put(two,x,20,leg)
 put(two,4,16,tile(p,4,4,'s'));put(two,8,16,tile(p,4,4,'d'))
 # Boots outer layer uses leg island only from calf to sole, upper thigh clear.
 boot=Pixel((4,12),p);boot.r((0,5,3,11),'s');boot.l([(0,5),(3,5)],'g');boot.r((1,6,2,9),'m');boot.l([(0,10),(3,10)],'l');boot.l([(0,11),(3,11)],'d')
 if s in ('hongmeng','ziwei'):boot.l([(0,7),(3,7)],'b');boot.r((1,8,2,9),'l')
 elif s=='baihu':boot.r((0,6,3,9),'l');boot.l([(0,7),(2,8)],'d')
 elif s=='zhuque':boot.l([(0,6),(2,8),(3,7)],'g')
 elif s=='qinglong':boot.q([(0,6),(3,6),(3,7),(1,8),(0,7)],'l','d')
 elif s=='disha':boot.r((1,6,2,9),'l')
 elif s=='beidou':boot.dot((1,7),'h')
 elif s=='hunyuan':boot.l([(0,6),(2,7),(1,9)],'l')
 for x in (0,4,8,12):put(one,x,20,boot)
 put(one,8,16,tile(p,4,4,'d'))
 return one,two

def backup(s):
 records=[]
 paths=[f'textures/item/{s}_{piece}.png' for piece in PIECES]+[f'textures/models/armor/{s}_layer_{n}.png' for n in (1,2)]+[f'models/item/{s}_{piece}.json' for piece in PIECES]
 for rel in paths:
  src=SOURCE/rel;dest=HERE/'before'/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():shutil.copy2(src,dest)
  assert sha(src)==sha(dest),f'Source changed since backup; stop instead of replacing: {rel}'
  records.append({'source':str(src),'backup':str(dest.relative_to(HERE)),'sha256':sha(src)})
 return records

def full_preview(one,two,eye):
 path=ROOT/'docs/art/armor-sample-v14/qa/render_chestplate.py'
 # Execute the already-reviewed local renderer in memory; don't emit __pycache__ there.
 m=types.ModuleType('armor_v14_reference_renderer');m.__file__=str(path);exec(compile(path.read_text(),str(path),'exec'),m.__dict__)
 def scene(atlases):
  first,second=atlases;neutral=Image.new('RGBA',(64,32),(128,131,131,255));quads=[]
  parts=[((0,0),(-4,-8,-4),(8,8,8),(0,0,0),False,0),((16,16),(-4,0,-2),(8,12,4),(0,0,0),False,0),((40,16),(-3,-2,-2),(4,12,4),(-5,2,0),False,.1),((40,16),(-1,-2,-2),(4,12,4),(5,2,0),True,-.1),((0,16),(-2,0,-2),(4,12,4),(-1.9,12,0),False,0),((0,16),(-2,0,-2),(4,12,4),(1.9,12,0),True,0)]
  for uv,start,size,off,mirror,angle in parts:quads+=m.cube(uv,start,size,0,off,mirror,angle,neutral)
  for i in (1,4,5):
   uv,start,size,off,mirror,angle=parts[i];quads+=m.cube(uv,start,size,.5,off,mirror,angle,second)
  for uv,start,size,off,mirror,angle in parts:quads+=m.cube(uv,start,size,1,off,mirror,angle,first)
  return quads
 m.scene=scene;return m.render((one,two),eye,size=(220,260),scale=6)

def font(n):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',n)
def previews(s,icons,one,two):
 out=HERE/'previews';out.mkdir(parents=True,exist_ok=True)
 page=Image.new('RGB',(1200,1080),'#e6e5dc');d=ImageDraw.Draw(page)
 d.text((24,16),SETS[s][0]+' / '+s+' · native pixel armor',font=font(25),fill='#28383b')
 d.text((24,53),'32×32 flat icons · 64×32 independent humanoid UV · OFFLINE, not in game',font=font(17),fill='#5c6969')
 for i,(piece,im) in enumerate(icons.items()):
  x=24+i*290;d.text((x,90),piece,font=font(19),fill='#27383b');old=Image.open(HERE/f'before/textures/item/{s}_{piece}.png').convert('RGBA')
  for dx,tex,label in [(0,old,'before'),(136,im,'candidate')]:
   d.rectangle((x+dx,120,x+dx+127,247),fill='#3a4446');big=tex.resize((128,128),Image.Resampling.NEAREST);page.paste(big,(x+dx,120),big);d.text((x+dx,253),label,font=font(14),fill='#546366')
  page.paste(im,(x,289),im);small=im.resize((16,16),Image.Resampling.NEAREST);page.paste(small,(x+52,297),small);d.text((x+81,294),'1× + UI 16',font=font(14),fill='#546366')
 views=[('front',(0,0,-1)),('back',(0,0,1)),('three-quarter',(-1,.2,-1.6))]
 for i,(name,eye) in enumerate(views):
  r=full_preview(one,two,eye);r.save(out/f'{s}-worn-{name}.png');d.rectangle((24+i*280,342,280+i*280,674),fill='#c7cecb');r=r.resize((264,312),Image.Resampling.NEAREST);page.paste(r,(24+i*280,355),r);d.text((36+i*280,345),name,font=font(14),fill='#3d5052')
 d.text((880,356),'Shared mirrored limbs',font=font(16),fill='#3d5052');d.text((880,388),'Open helmet face',font=font(16),fill='#3d5052');d.text((880,420),'Layer 2: waist + legs',font=font(16),fill='#3d5052');d.text((880,452),'No geometry changes',font=font(16),fill='#3d5052');d.text((880,484),'No emissive / animation',font=font(16),fill='#3d5052')
 for i,atlas in enumerate((one,two)):
  x=24+i*584;d.text((x,712),f'Layer {i+1} / 64×32',font=font(18),fill='#2d4043');d.rectangle((x,748,x+511,1003),fill='#bfcac5');big=atlas.resize((512,256),Image.Resampling.NEAREST);page.paste(big,(x,748),big)
 d.text((24,1030),'Native texels only. Icons and body UV authored separately. Source assets backed up; candidate not installed.',font=font(16),fill='#4d6160');page.save(out/f'{s}-overview.png')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--only',choices=list(SETS));args=ap.parse_args();selected=[args.only] if args.only else list(SETS)
 entries=[]
 for s in selected:
  original=backup(s);p=palette(s);icons={piece:fun(s,p) for piece,fun in zip(PIECES,(helmet,chest,leggings,boots))};one,two=armor_atlases(s,p);assets=[]
  for piece,im in icons.items():
   assert im.size==(32,32);assert set(im.getchannel('A').getdata())=={0,255};box=im.getchannel('A').getbbox();assert min(box[0],box[1],32-box[2],32-box[3])>=1,(s,piece,box)
   rel=f'textures/item/{s}_{piece}.png';path=CANDIDATE/rel;path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
   model=json.loads((SOURCE/f'models/item/{s}_{piece}.json').read_text());assert model['textures']['layer0']==f'dynasty:item/{s}_{piece}'
   assets.append({'id':f'dynasty:{s}_{piece}','path':str(path.relative_to(HERE)),'size':[32,32],'colors':len({c[:3] for c in im.getdata() if c[3]}),'alpha':[0,255],'bbox':box,'sha256':sha(path),'model':str(SOURCE/f'models/item/{s}_{piece}.json'),'model_parent':model['parent']})
  for n,im in enumerate((one,two),1):
   assert im.size==(64,32) and set(im.getchannel('A').getdata())=={0,255}
   rel=f'textures/models/armor/{s}_layer_{n}.png';path=CANDIDATE/rel;path.parent.mkdir(parents=True,exist_ok=True);im.save(path);assets.append({'armor_material':f'dynasty:{s}','path':str(path.relative_to(HERE)),'size':[64,32],'alpha':[0,255],'sha256':sha(path),'layer':n})
  previews(s,icons,one,two)
  entries.append({'set':s,'name':SETS[s][0],'construction':SETS[s][1],'baseline':original,'assets':assets,'source_files_unchanged':all(sha(Path(b['source']))==b['sha256'] for b in original)})
  print(s,'created',len(assets),'assets',flush=True)
 manifest={'sets':entries,'status':'review_candidates_not_installed','set_count':len(entries),'asset_count':sum(len(e['assets']) for e in entries),'native_icon_size':[32,32],'native_atlas_size':[64,32],'why32':'Existing project armor icon resource specification is 32x32; this retains native grid for distinct equipment silhouette and material layering. Assets authored directly at final grid size.','source_evidence':'No dedicated later art-remaster or approval record for these 12 sets in project docs; dark_iron has v14 chestplate sample. General/jade/sky/bronze/xuantian protected.','uv':'Vanilla HumanoidArmorModel 64x32: layer1 head/body/shared mirrored arms/boots; layer2 waist/shared mirrored legs. Helmet central face open.','preview_renderer':'Read-only import of armor-sample-v14/qa/render_chestplate.py ModelPart cube UV and raster routines, full armor slot scene composed here.','game_tested':False,'emissive':False,'animation':False}
 (HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()

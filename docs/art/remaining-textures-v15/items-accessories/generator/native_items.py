"""Original native 32x32 pixel artwork. No external image sampling, resize or noise in asset creation."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json, hashlib, math, argparse, collections
R=Path('/Users/a15356015027/Desktop/dynasty'); OUT=R/'docs/art/remaining-textures-v15/items-accessories'
P={
'g':['#433729','#705234','#9f733b','#cb9a51','#edcc87'],
's':['#252e38','#405463','#6c8390','#a0b4b8','#d9e0d2'],
'j':['#203e35','#2d6451','#559675','#8cc399','#d0dfb7'],
'r':['#442c32','#76373f','#af514c','#d58a65','#ecd6a0'],
'b':['#25384b','#365d77','#558d9b','#91c4bf','#d2e2c5'],
'v':['#322e49','#51446b','#826294','#b28db3','#ddd0da'],
'n':['#3e352f','#706354','#a99a7a','#d7c8a1','#f1e4bf'],
'w':['#3b2e29','#654531','#996640','#bd9060','#dbc295'],
'y':['#4a412f','#726743','#a6a069','#cbd19b','#e3e7b9']}
class Art:
 def __init__(self):self.im=Image.new('RGBA',(32,32));self.d=ImageDraw.Draw(self.im)
 def poly(self,pts,m='g',i=2):self.d.polygon(pts,fill=P[m][i] if isinstance(i,int) else i)
 def rect(self,b,m='g',i=2):self.d.rectangle(b,fill=P[m][i] if isinstance(i,int) else i)
 def line(self,pts,m='g',i=2,w=1):self.d.line(pts,fill=P[m][i] if isinstance(i,int) else i,width=w)
 def dot(self,x,y,m='g',i=2):self.rect((x,y,x,y),m,i)
 def hole(self,b):self.d.rectangle(b,fill=(0,0,0,0))
 def ellipse(self,b,m='g',i=2):self.d.ellipse(b,fill=P[m][i])
 def box(self,b,m='g'):
  x,y,X,Y=b;self.rect(b,m,0);self.rect((x+1,y+1,X-1,Y-1),m,2);self.line([(x+1,Y-1),(x+1,y+1),(X-1,y+1)],m,3);self.line([(X-1,y+2),(X-1,Y-1),(x+2,Y-1)],m,1)
 def cord(self,pts,m='r',w=3):self.line(pts,m,0,w);self.line(pts,m,2,max(1,w-2))
 def bail(self,x=15,y=2,m='g'):self.poly([(x-2,y+1),(x-1,y),(x+1,y),(x+2,y+1),(x+2,y+4),(x-2,y+4)],m,0);self.rect((x-1,y+1,x+1,y+3),m,3);self.hole((x,y+1,x,y+2))
 def gem(self,x,y,w,h,m='j'):
  pts=[(x+w//3,y),(x+2*w//3,y),(x+w,y+h//3),(x+w,y+2*h//3),(x+2*w//3,y+h),(x+w//3,y+h),(x,y+2*h//3),(x,y+h//3)]
  self.poly(pts,m,0);self.poly([(x+w//3,y+1),(x+2*w//3,y+1),(x+w-1,y+h//3),(x+w-1,y+2*h//3),(x+w//2,y+h-1),(x+1,y+2*h//3),(x+1,y+h//3)],m,2)
  self.poly([(x+w//3,y+2),(x+2*w//3,y+2),(x+w//2,y+h//2),(x+2,y+2*h//3),(x+2,y+h//3)],m,3)
  self.poly([(x+w//2,y+h//2),(x+w-2,y+h//3),(x+w-2,y+2*h//3),(x+w//2,y+h-2)],m,1)
  self.line([(x+w//3,y+2),(x+2*w//3-1,y+2)],m,4)
 def disc(self,x,y,w,h,m='g'):
  self.ellipse((x,y,x+w,y+h),m,0);self.ellipse((x+1,y+1,x+w-1,y+h-1),m,2);self.d.arc((x+2,y+2,x+w-2,y+h-2),185,280,fill=P[m][4],width=1);self.d.arc((x+2,y+2,x+w-2,y+h-2),10,100,fill=P[m][1],width=2)
 def tassel(self,x,y,length=10,m='r',spread=4):
  self.box((x-2,y,x+2,y+3),'g')
  for dx,end in [(-spread,-1),(0,1),(spread,0)]:self.cord([(x+dx//2,y+4),(x+dx,y+length-2),(x+dx+end,y+length)],m,3)
 def glyph(self,name,x,y,m='g',tone=3,width=1):
  paths={
   'bolt':[[(x+5,y),(x+1,y+5),(x+5,y+5),(x+2,y+11)]],
   'flame':[[(x+4,y),(x+3,y+4),(x+1,y+5),(x,y+9),(x+3,y+11),(x+6,y+8),(x+5,y+5)]],
   'wind':[[(x,y+2),(x+4,y),(x+6,y+1),(x+6,y+3),(x+3,y+4)],[(x,y+7),(x+4,y+5),(x+5,y+6),(x+4,y+9),(x+1,y+10)]],
   'wall':[[(x,y+10),(x,y+3),(x+2,y+3),(x+2,y),(x+4,y),(x+4,y+3),(x+6,y+3),(x+6,y+10)],[(x+1,y+6),(x+5,y+6)]],
   'eye':[[(x,y+5),(x+3,y+2),(x+6,y+5),(x+3,y+8),(x,y+5)],[(x+3,y+3),(x+3,y+7)]],
   'mountain':[[(x,y+10),(x+2,y+4),(x+3,y+6),(x+5,y),(x+7,y+10),(x,y+10)]],
   'wave':[[(x,y+3),(x+3,y),(x+6,y+3),(x+3,y+6),(x,y+3)],[(x,y+9),(x+3,y+7),(x+6,y+9)]],
   'gate':[[(x,y+10),(x,y),(x+6,y),(x+6,y+10)],[(x+2,y+10),(x+2,y+4),(x+4,y+4),(x+4,y+10)]],
   'wing':[[(x,y+10),(x+2,y+4),(x+6,y),(x+5,y+5),(x+2,y+8)],[(x+2,y+7),(x+5,y+7)]],
   'oath':[[(x+3,y),(x+3,y+10)],[(x,y+3),(x+6,y+3)],[(x,y+7),(x+6,y+7)]],
   'star':[[(x+3,y),(x+4,y+4),(x+7,y+5),(x+4,y+6),(x+3,y+10),(x+2,y+6),(x,y+5),(x+2,y+4),(x+3,y)]],
   'spiral':[[(x,y+10),(x+6,y+10),(x+6,y),(x,y),(x,y+6),(x+3,y+6),(x+3,y+3)]]}
  for pts in paths[name]:self.line(pts,m,tone,width)

def coins(id,cfg):
 a=Art();m=cfg['m'];kind=cfg['v']
 if kind=='square':a.box((4,5,27,27),m);a.box((8,9,23,23),m);a.hole((13,14,18,19));a.line([(8,7),(23,7)],m,4)
 elif kind=='dragon':
  a.poly([(10,2),(22,2),(29,9),(29,21),(22,29),(10,29),(2,21),(2,9)],m,0);a.poly([(10,4),(21,4),(27,10),(27,20),(21,27),(10,27),(4,20),(4,10)],m,2);a.line([(6,10),(11,5),(20,5)],m,4);a.glyph('spiral',12,10,m);a.line([(10,9),(8,12),(10,15)],m,1);a.dot(19,8,m,4)
 else:
  a.disc(3,3,25,25,m);a.disc(6,6,19,19,m)
  if kind=='hole':a.box((11,11,20,20),m);a.hole((13,13,18,18));a.line([(7,10),(10,7)],m,4);a.line([(22,21),(20,24)],m,1)
  elif kind=='sun':
   a.gem(11,10,10,11,m)
   for x,y in [(15,6),(24,15),(15,24),(6,15)]:a.rect((x,y,x+1,y+1),m,4)
  else:a.poly([(16,8),(23,16),(16,23),(8,16)],m,1);a.poly([(16,10),(21,16),(16,21),(11,16)],m,3);a.dot(15,14,m,4)
 return a

def pearl(id,cfg):
 a=Art();m=cfg['m'];v=cfg['v']
 if v=='clam':
  a.poly([(3,23),(3,14),(7,7),(12,4),(20,4),(25,8),(29,16),(28,23),(23,28),(9,28)],'n',0)
  a.poly([(5,20),(5,14),(9,8),(13,6),(19,6),(23,9),(27,16),(26,21),(22,24),(10,24)],'n',2)
  for pts in [[(8,11),(12,17),(15,23)],[(13,7),(15,16),(16,24)],[(20,8),(18,16),(16,24)],[(25,14),(21,18),(17,24)]]:a.line(pts,'n',1,2)
  a.line([(7,13),(10,9),(13,7)],'n',3,2);a.line([(22,10),(25,15)],'n',3)
  a.poly([(5,23),(10,20),(22,20),(27,23),(23,28),(9,28)],'n',3);a.gem(10,10,12,12,m);a.line([(9,26),(22,26)],'n',4)
 elif v=='pair':
  a.disc(3,4,24,24,'g');a.poly([(16,6),(23,9),(25,15),(23,21),(16,26),(16,19),(10,17),(9,12),(12,8)],m,2);a.poly([(15,6),(9,8),(6,14),(8,22),(15,26),(16,20),(21,18),(22,13),(18,10)],'n',3);a.rect((11,12,13,14),m,1);a.rect((18,18,20,20),'n',4)
 elif v=='eclipse':
  a.bail(16,2,'s');a.disc(6,7,20,21,'v');a.poly([(18,9),(12,10),(9,15),(10,22),(15,25),(21,24),(17,26),(11,25),(7,20),(7,15),(10,10),(15,8)],'s',3);a.poly([(14,9),(10,12),(9,17),(11,22),(15,25),(12,25),(8,22),(7,17),(9,12),(12,9)],'s',3);a.dot(22,13,'s',4);a.line([(19,25),(20,28)],'g',3)
 elif v=='cloud':
  a.gem(7,4,19,19,m);a.poly([(3,22),(6,19),(10,20),(12,23),(19,22),(23,20),(27,22),(29,26),(25,28),(6,28),(2,26)],'v',0);a.line([(4,24),(7,22),(10,23),(11,25),(22,25),(25,23),(27,25)],'v',3,2)
 elif v=='net':
  a.bail(16,2);a.gem(8,8,16,16,m);a.cord([(7,8),(4,19),(8,26),(16,29),(24,26),(28,19),(25,8)],'w',2)
  for x in [8,13,18,23]:a.line([(x,12),(x+3,24)],'g',2)
  a.line([(6,18),(26,18)],'g',2);a.line([(8,24),(24,24)],'g',3)
 else:
  a.gem(5,5,22,22,m)
  if v=='cage':
   a.poly([(4,18),(7,18),(9,25),(14,27),(14,30),(8,28),(4,23)],'s',0);a.line([(5,19),(7,24),(13,28)],'s',2,2)
   a.poly([(27,18),(24,18),(23,25),(18,27),(18,30),(24,28),(28,23)],'s',0);a.line([(27,20),(24,25),(19,28)],'s',2,2);a.rect((13,2,18,5),'s',2)
  elif v=='blood':a.poly([(4,8),(8,8),(9,5),(13,3),(14,6),(10,9),(8,12),(4,12)],'g',2);a.poly([(19,25),(23,21),(27,22),(27,26),(24,29),(19,29)],'g',2);a.line([(21,27),(25,24)],'g',4)
  elif v=='dragon':a.poly([(3,13),(3,8),(7,3),(12,3),(12,6),(8,6),(6,10),(6,15)],'g',2);a.poly([(21,22),(25,19),(28,20),(28,25),(24,29),(18,29),(18,26),(22,26)],'g',2);a.dot(8,4,'g',4);a.line([(21,27),(25,24)],'g',4)
 return a

def rings(id,cfg):
 a=Art();m=cfg['m'];v=cfg['v']
 pts=[(8,9),(14,5),(22,6),(27,12),(28,21),(23,27),(15,29),(7,25),(3,19),(3,14)]
 a.poly(pts,m,0);a.poly([(9,10),(14,7),(21,8),(25,13),(26,20),(22,25),(15,27),(8,23),(5,18),(5,14)],m,2)
 a.poly([(10,12),(14,10),(20,11),(23,15),(23,20),(20,23),(14,24),(9,21),(8,17)],m,1);a.d.polygon([(11,13),(15,12),(19,13),(21,16),(21,20),(18,22),(14,22),(11,20),(10,16)],fill=(0,0,0,0));a.line([(6,13),(10,9),(14,8)],m,4,2);a.line([(13,26),(20,25),(24,21)],m,3)
 if v=='sun':
  a.gem(7,2,11,12,'g');a.line([(5,6),(3,5)],'g',3,2);a.line([(18,5),(21,3)],'g',3,2);a.line([(13,1),(13,3)],'g',3)
 elif v=='blood':a.gem(6,3,11,12,'r');a.line([(17,6),(19,8),(18,11)],m,3);a.line([(6,18),(8,20)],m,3)
 elif v=='night':a.gem(6,3,12,12,'v');a.poly([(13,5),(10,7),(10,10),(13,13),(9,12),(8,9),(9,6)],'s',3)
 elif v=='binding':
  a.gem(8,3,10,10,'v');a.box((4,17,10,20),'s');a.box((19,22,25,25),'s');a.line([(6,18),(8,18)],'s',4)
 elif v=='thumb':a.line([(7,13),(8,22),(13,26)],m,3,2);a.rect((8,9,12,13),m,4)
 return a

def seals(id,cfg):
 a=Art();m=cfg['m'];v=cfg['v'];accent=cfg.get('accent','r')
 # Flat-front sculpted stamp base with collar, top knob, and distinct tiers.
 a.poly([(6,18),(25,18),(28,22),(27,28),(4,28),(3,22)],m,0);a.rect((5,22,26,27),m,2);a.rect((6,23,25,24),m,3);a.line([(6,26),(24,26)],m,1);a.rect((9,19,22,21),m,3)
 if v in ['dragon','imperial']:
  a.poly([(8,17),(8,12),(11,9),(13,5),(18,5),(20,9),(24,10),(24,14),(21,15),(20,19),(11,19)],m,0)
  a.poly([(10,17),(11,12),(14,10),(14,7),(17,7),(19,11),(22,11),(22,13),(18,14),(18,18)],m,2);a.line([(11,14),(14,11),(16,11)],m,4);a.line([(12,6),(11,3)],m,3);a.line([(18,6),(20,3)],m,3);a.dot(20,11,accent,3)
  if v=='imperial':a.rect((3,23,5,25),'g',3);a.rect((26,23,28,25),'g',3);a.gem(12,22,8,5,accent)
 elif v=='tiger':
  a.poly([(8,18),(7,10),(10,6),(13,8),(19,8),(22,6),(25,10),(23,18)],m,0);a.poly([(10,17),(9,11),(12,9),(20,9),(23,11),(21,17)],m,2);a.line([(12,10),(13,12)],m,0);a.line([(20,10),(19,12)],m,0);a.rect((15,14,17,15),m,1);a.line([(14,17),(18,17)],m,4)
 elif v=='pair':
  a.box((6,8,13,19),m);a.box((18,5,25,19),m);a.rect((8,5,11,7),accent,2);a.rect((20,2,23,4),accent,3);a.line([(14,13),(17,13)],'g',3,2)
 elif v=='tower':
  a.box((9,9,22,19),m);a.poly([(7,10),(9,6),(22,6),(25,10)],m,0);a.rect((10,7,21,9),m,3);a.rect((13,3,18,6),m,2);a.rect((14,12,17,17),accent,2)
 elif v=='square':
  a.box((9,8,22,19),m);a.box((12,3,19,10),m);a.hole((14,5,17,7));a.rect((12,13,19,15),accent,2)
 elif v=='ring':
  a.disc(10,3,12,12,m);a.hole((14,7,18,11));a.rect((13,14,20,20),m,1);a.line([(14,15),(14,19)],m,4);a.rect((7,23,24,24),m,4);a.rect((10,25,21,26),m,1)
 elif v=='knot':
  a.bail(15,2,accent);a.poly([(7,13),(11,8),(20,8),(24,13),(21,19),(10,19)],accent,0);a.poly([(9,13),(12,10),(18,10),(22,13),(19,17),(12,17)],accent,2);a.line([(12,11),(19,16)],accent,4);a.line([(20,11),(12,17)],accent,1)
 elif v=='hoof':
  a.poly([(10,4),(21,4),(21,13),(24,18),(8,18),(11,13)],m,0);a.rect((12,5,19,13),m,2);a.poly([(11,14),(19,14),(22,17),(9,17)],m,3);a.line([(16,14),(16,18)],m,0)
 else:
  a.box((10,6,21,19),m);a.rect((12,3,19,6),accent,2);a.line([(12,8),(18,8)],m,4);a.glyph('oath',12,8,accent)
 if id=='sea_token':
  a.cord([(10,17),(6,15),(5,11),(7,8),(10,9)],'b',3);a.line([(7,24),(10,22),(13,24),(16,22),(19,24),(22,22),(25,24)],'b',3);a.rect((11,27,23,28),'b',1)
 if id=='diver_signet':
  a.poly([(8,18),(6,13),(8,9),(11,7),(12,10),(9,13),(11,17)],'j',1);a.line([(7,24),(24,24)],'b',2);a.rect((13,25,18,26),'b',3)
 return a

def bags(id,cfg):
 a=Art();m=cfg['m'];v=cfg['v'];accent=cfg.get('accent','g')
 if v!='box':a.cord([(12,6),(8,3),(8,6),(14,8),(21,4),(23,4),(21,7),(17,8)],accent,2)
 if v=='box':
  a.box((5,12,27,28),m);a.poly([(4,12),(5,7),(9,5),(24,5),(28,8),(29,13),(27,15),(5,15)],m,0);a.poly([(6,12),(7,8),(10,7),(23,7),(26,9),(27,12),(25,13),(7,13)],m,3);a.line([(9,8),(22,8)],m,4);a.rect((6,14,27,15),m,1);a.rect((8,13,10,16),'g',2);a.rect((23,13,25,16),'g',2);a.box((13,13,20,22),'g');a.rect((16,17,17,19),'g',0);a.line([(8,24),(24,24)],m,3);a.rect((7,27,10,29),accent,1);a.rect((23,27,26,29),accent,1)
 elif v=='mirror':
  a.poly([(7,10),(12,8),(20,8),(25,10),(28,20),(25,28),(7,28),(4,20)],m,0);a.poly([(8,12),(24,12),(26,20),(23,26),(9,26),(6,20)],m,2);a.disc(10,15,12,11,'g');a.disc(13,17,6,7,'b');a.line([(9,11),(22,11)],m,4)
 elif v=='ration':
  a.poly([(8,8),(24,8),(26,11),(25,17),(28,23),(25,28),(7,28),(4,23),(7,17),(6,11)],m,0);a.poly([(9,10),(22,10),(23,17),(25,23),(23,26),(9,26),(7,23),(9,17)],m,2);a.line([(10,12),(21,12)],m,3);a.cord([(16,8),(16,27)],accent,3);a.line([(9,20),(23,20)],accent,2,2);a.rect((11,14,14,16),'n',3)
 else:
  a.poly([(9,8),(23,8),(23,12),(27,19),(26,25),(22,28),(9,28),(5,24),(5,19),(10,12)],m,0);a.poly([(11,10),(21,10),(21,14),(25,20),(24,24),(21,26),(10,26),(7,23),(7,20),(12,13)],m,2);a.line([(11,13),(9,19),(9,23)],m,3,2);a.line([(22,19),(22,24),(19,25)],m,1,2);a.line([(10,10),(22,10)],accent,3,2)
  if v=='cinnabar':a.gem(13,16,7,8,'r');a.dot(12,24,'n',3)
  elif v=='cloud':a.line([(12,18),(14,16),(17,16),(19,18),(20,21),(12,21),(11,20)],'g',3,2)
  elif v=='veil':a.poly([(10,16),(17,14),(21,18),(19,24),(13,25)],'v',1);a.line([(12,18),(15,16),(18,16)],'v',3)
  else:a.glyph('wave',12,15,accent)
 return a

def token(id,cfg):
 a=Art();m=cfg['m'];v=cfg['v'];accent=cfg.get('accent','g')
 a.bail(15,2,accent)
 if v=='arrow':pts=[(8,8),(15,5),(23,8),(23,20),(16,29),(8,21)]
 elif v=='badge':pts=[(5,9),(10,7),(22,7),(27,10),(25,23),(19,28),(12,28),(6,22)]
 elif v=='wing':pts=[(3,9),(9,9),(12,6),(20,6),(23,9),(29,9),(26,17),(23,17),(22,26),(10,26),(9,17),(6,17)]
 elif v=='split':pts=[(8,7),(23,7),(23,29),(18,26),(15,29),(12,26),(8,29)]
 else:pts=[(10,6),(21,6),(25,10),(25,25),(21,29),(9,29),(6,25),(6,10)]
 a.poly(pts,m,0)
 inner=[(x+(1 if x<16 else -1),y+(1 if y<16 else -1)) for x,y in pts];a.poly(inner,m,2);a.line([(9,11),(11,8),(20,8)],m,3)
 if v=='tiger':
  a.poly([(10,14),(11,11),(15,13),(20,11),(22,15),(20,22),(12,22)],accent,1);a.line([(12,15),(14,16)],accent,4);a.line([(20,15),(18,16)],accent,4);a.rect((15,18,17,20),accent,0)
 elif v=='bird':
  a.poly([(9,22),(12,17),(11,13),(15,16),(18,18),(19,13),(17,12),(17,10),(20,10),(23,12),(20,12),(21,15),(20,20),(17,22),(13,21)],accent,3);a.poly([(11,14),(14,16),(16,19),(13,19)],accent,4);a.line([(17,21),(16,25),(14,25)],accent,2);a.line([(19,21),(20,24),(22,24)],accent,2);a.dot(20,10,accent,0)
 elif v=='eye':a.glyph('eye',12,12,accent)
 elif v=='arrow':a.glyph('bolt',12,10,accent);a.rect((12,25,18,26),m,3)
 elif v=='split':a.glyph('gate',12,12,accent)
 elif v=='wing':a.glyph('wing',12,11,accent)
 else:a.glyph(cfg.get('glyph','oath'),12,12,accent)
 return a

def talisman(id,cfg):
 a=Art();m=cfg['m'];accent=cfg['accent'];v=cfg['v'];g=cfg['glyph']
 if v=='scroll':
  a.box((7,7,25,26),m);a.box((5,5,27,9),'w');a.box((5,25,27,28),'w');a.line([(9,10),(9,23)],m,4);a.glyph(g,13,12,accent,2,2);a.rect((20,12,21,15),accent,2)
 elif v=='paired':
  a.poly([(5,6),(15,7),(14,27),(11,25),(7,28),(5,25)],m,0);a.poly([(6,7),(13,8),(12,25),(8,25)],m,3)
  a.poly([(17,6),(26,4),(28,24),(25,28),(19,27)],m,0);a.poly([(18,8),(24,7),(26,24),(23,26),(20,25)],m,3)
  a.glyph(g,8,12,accent,2,2);a.line([(21,11),(23,13),(21,16),(24,20)],accent,2);a.cord([(9,6),(16,3),(23,6)],'r',2)
 elif v=='folded':
  a.poly([(9,2),(23,5),(23,24),(19,29),(8,26),(7,8)],m,0);a.poly([(10,4),(21,6),(21,23),(18,27),(10,25),(9,8)],m,3);a.poly([(18,25),(22,22),(21,27)],m,1);a.line([(11,7),(19,8)],m,4);a.glyph(g,12,11,accent,2,2)
 elif v=='fan':
  a.poly([(2,9),(6,4),(14,3),(24,4),(29,10),(16,29)],m,0);a.poly([(4,10),(8,6),(15,5),(23,6),(27,11),(16,26)],m,3)
  a.line([(8,8),(16,25),(24,9)],m,1);a.line([(15,6),(16,25)],m,2);a.glyph(g,12,10,accent,2,2)
 else:
  a.bail(15,2,'r');a.poly([(9,6),(22,6),(24,10),(24,27),(20,26),(17,29),(13,27),(9,29),(7,26),(7,10)],m,0);a.poly([(10,8),(21,8),(22,11),(22,25),(19,24),(17,27),(13,25),(9,27),(9,11)],m,3);a.rect((10,9,21,10),accent,2);a.glyph(g,12,13,accent,2,2);a.rect((10,23,11,25),m,4)
 return a

def belt(id,cfg):
 a=Art();m=cfg['m'];accent=cfg['accent'];v=cfg['v']
 a.poly([(3,8),(9,5),(24,5),(29,9),(29,20),(24,25),(9,25),(3,21)],m,0);a.poly([(5,9),(10,7),(23,7),(27,10),(27,19),(23,23),(10,23),(5,20)],m,2);a.line([(5,9),(10,7),(23,7)],m,3);a.hole((9,11,23,18));a.poly([(8,17),(24,17),(26,20),(24,26),(9,26),(5,22)],m,0);a.rect((8,20,24,24),m,2);a.line([(9,21),(23,21)],m,3)
 if v=='buckle':a.box((10,16,23,27),accent);a.hole((13,19,20,24));a.line([(16,17),(16,24)],accent,3,2)
 elif v=='scales':
  for x in [8,14,20]:a.poly([(x,19),(x+5,19),(x+5,23),(x+2,26),(x,23)],accent,0);a.poly([(x+1,20),(x+4,20),(x+4,22),(x+2,24)],accent,2);a.dot(x+1,20,accent,3)
 else:
  a.box((12,17,21,27),accent)
  if v=='jade':a.gem(14,19,5,6,'j')
  elif v=='battle':a.glyph('eye',13,18,'s')
  else:a.rect((15,20,18,24),accent,4)
  a.rect((5,19,8,21),accent,2);a.rect((25,19,27,21),accent,2)
 return a

def tassels(id,cfg):
 a=Art();m=cfg['m'];v=cfg['v'];accent=cfg.get('accent','g')
 if v=='whisker':
  a.bail(16,2,'j');a.box((12,7,20,11),'g')
  for pts in [[(13,10),(9,14),(7,20),(8,25),(5,28)],[(16,10),(15,17),(17,23),(15,29)],[(19,10),(23,14),(24,21),(22,27)]]:a.cord(pts,m,3)
 elif v=='plume':
  a.poly([(10,28),(12,15),(8,10),(11,3),(16,2),(22,6),(24,12),(19,16),(19,28)],m,0);a.poly([(13,23),(14,13),(11,10),(13,5),(17,4),(21,7),(22,11),(17,16),(17,25)],m,2);a.line([(14,8),(16,6),(19,8)],m,3,2);a.box((10,24,21,29),'s')
 elif v=='qin':
  a.poly([(10,2),(15,2),(19,7),(18,12),(13,13),(9,8)],'j',0);a.poly([(11,4),(14,4),(17,8),(16,10),(13,11),(11,8)],'j',3);a.tassel(13,13,15,m,5);a.cord([(18,9),(23,13),(21,20)],m,2)
 else:
  a.cord([(13,3),(10,5),(12,9),(17,9),(21,5),(18,3),(15,6),(15,10)],m,3)
  a.box((11,10,20,14),accent)
  if v=='pike':a.poly([(12,15),(19,15),(25,24),(23,29),(18,25),(15,29),(10,27),(7,24)],m,0);a.poly([(13,16),(18,16),(22,24),(21,27),(17,23),(15,27),(10,25)],m,2);a.line([(15,16),(14,24)],m,3,2)
  else:a.tassel(15,14,15,m,5);a.dot(15,12,accent,4)
 return a
DESIGNS={}
def group(family, rows):
 for id,m,v,accent,detail in rows:DESIGNS[id]={'family':family,'m':m,'v':v,'accent':accent,'design':detail}
group('coins',[
('copper_coin','g','hole','g','厚铜钱、方孔、两段磨亮钱缘'),('silver_coin','s','diamond','s','八面银章、菱形浅浮雕与克制亮边'),('gold_coin','g','sun','g','双重金边与凸起八角中心'),('jade_coin','j','square','g','方圆玉币、宽方孔与浅色磨边'),('dragon_coin','g','dragon','j','切角龙币、独立回折龙纹与额角')])
group('pearl',[
('abyss_pearl','b','cage','s','深蓝切面珠与两侧铁爪托'),('dragon_blood_pearl','r','blood','g','暗红龙血珠，铜角抓箍与下方封帽'),('dragon_pearl','y','dragon','g','黄玉龙珠，卷角铜托，留净晶面'),('eclipse_bead','v','eclipse','s','暗紫蚀月珠，银色月弧与顶部挂环'),('hunyuan_pearl','j','pair','n','混元双面珠，温白/深玉双曲面嵌合'),('purple_qi_pearl','v','cloud','v','紫晶珠与下方连贯紫气云座'),('sea_pearl','b','clam','n','贝壳托住浅青避水珠，分扇贝纹'),('pearl_net_charm','n','net','g','暖白大珠装入收口绳网，外侧挂环')])
group('rings',[
('lifedrain_ring','s','blood','r','宽钢环镶红榴石，偏置爪托'),('nether_binding_ring','s','binding','v','幽紫晶配两道钢束箍，开环孔'),('starless_night_ring','s','night','v','黑银戒环、暗紫石上的银月窄面'),('sun_chaser_ring','g','sun','g','金环顶托八角日石，短角日芒'),('jade_ring','j','thumb','j','较宽玉扳指，清楚透孔和厚壁')])
group('seals',[
('blood_oath_seal','s','knot','r','钢印台配红结钮，红誓结是轮廓重点'),('diver_signet','j','dragon','b','青玉潜蛟钮印，低浮雕鳍脊与青蓝印脊'),('dragon_emperor_seal','g','imperial','j','铜金帝印，高龙角钮与嵌玉封座'),('imperial_seal_charm','g','tower','j','金台阶御印与青玉柄钮'),('official_seal','g','square','r','方官印、透空方环钮与红印脊'),('jade_seal','j','imperial','g','厚玉传国印、双角龙钮和金护角'),('gold_seal_charm','g','ring','g','圆环金印钮与窄立颈，厚台面两层刻边'),('seal_charm','w','knot','r','木印章悬红绳结，下部朱砂印台'),('seal_of_two_heavens','s','pair','b','双高低印柱共享银底座，各有蓝玉端'),('scholar_ink_badge','j','tower','n','墨玉印坠，浅骨印钮与窄金封边'),('tomb_warden_seal','s','tower','j','层级铁陵印，厚檐盖与深玉门窗'),('war_deity_signet','g','tiger','r','虎面金战印，独立耳部与鼻脊'),('sea_token','j','dragon','b','龙宫青玉印，外卷水龙尾、蛟龙钮与波纹印座')])
group('bags',[
('cinnabar_pouch','r','cinnabar','g','朱砂红囊、紧束铜口与朱砂晶标记'),('cloud_brocade','b','cloud','g','蓝锦鼓囊，宽绣云团和上方系绳'),('dusk_veil_charm','v','veil','s','暮紫帷囊，折叠布盖与银系绳'),('iron_ration_charm','w','ration','s','鼓肚粮包，十字束带和谷袋角'),('mirror_pouch','r','mirror','g','红绸镜袋露出小铜框，袋口与镜面分离'),('scroll_case_charm','w','box','g','有木盖、铜扣与底角的长方书箱'),('silk_pouch','j','silk','r','青锦收口囊，红绳与一簇压褶'),('trinket_box','r','box','g','漆红妆匣、宽翻盖、铜锁片与护角')])
group('token',[
('armor_piercer_token','s','arrow','g','下尖钢符牌，单条穿甲折刃纹'),('dusk_raider_badge','s','eye','r','切角夜袭徽，红色眼形缺口纹'),('eunuch_token','g','tablet','r','内廷铜令牌，悬环、连笔竖横浅纹'),('iron_waist_token','s','split','g','双缺口玄铁腰牌，门字结构与悬环'),('mandarin_rank_badge','b','bird','g','宽蓝补子官徽，金鸟剪影与悬扣'),('merit_badge','g','badge','r','功牌盾形底，宽肩收腰轮廓'),('sky_token','s','wing','b','天将令，展开短翼侧耳与青蓝羽纹'),('thunder_token','s','arrow','b','雷部令，下尖长形与单条蓝雷纹'),('tiger_token','g','tiger','r','虎头令，双耳虎鼻与宽铜牌底')])
group('belt',[
('belt_buckle','w','buckle','g','皮带与中空铜方扣、真实穿带孔'),('blood_iron_sash','r','battle','s','暗红宽带，铁扣与短钢护片'),('cavalry_sash','w','battle','s','棕革骑兵带，横向宽钢扣和侧铆片'),('dragon_robe_sash','r','jade','g','锦红腰带，金包玉扣与两侧铜铰'),('dragon_scale_sash','b','scales','j','蓝底龙鳞腰带，三块独立玉鳞下缘')])
group('tassels',[
('dragon_whisker','y','whisker','j','玉环束起三根弯曲龙须，末端错开'),('guqin_tassel','b','qin','g','偏置玉琴钮与三股蓝穗'),('iron_helmet_plume','r','plume','s','铁缨座、红色折羽与高羽冠'),('pike_tassel','r','pike','g','枪缨铜箍与宽分叉红缨扇'),('saber_tassel','r','saber','g','双结红刀穗，铜节与三束分明穗尾')])
# Paper/cinnabar marks are original geometric signs, not copied calligraphy or third-party glyphs.
for id,m,v,accent,g,detail in [
('deathbed_talisman','n','folded','r','gate','卷角暖纸符，红色门形封灵纹'),('disha_talisman','r','paired','n','mountain','双张暗红地符，浅骨山纹'),
('edict_of_dragon','n','scroll','g','spiral','金轴龙威敕令，回折龙纹和朱砂印'),('edict_of_dread','v','scroll','r','eye','紫色威慑敕令，红眼形令纹'),('edict_of_iron','n','scroll','s','wall','骨白铁壁敕令，垛墙结构墨纹'),('edict_of_loyalty','r','scroll','n','oath','朱红忠诚敕令，贯穿纵横誓纹'),('edict_of_mandate','n','scroll','g','star','宽金轴天命敕令，菱星图案'),('edict_of_swift','b','scroll','n','wind','青蓝疾风敕令，两簇旋风纹'),
('fire_talisman','n','paper','r','flame','暖黄纸火符，中央红火苗形符记'),('internal_injury_talisman','n','folded','r','oath','折角内伤符，深红断续封伤线'),('return_talisman','n','paired','j','gate','两张归乡叠符，青色门纹'),('soul_talisman','v','paper','n','eye','紫色摄魂符，骨白眼形封印'),('stealth_talisman','s','folded','b','wind','蓝灰折符，低亮青色隐形回旋纹'),('thunder_seal_charm','s','paired','g','bolt','铁灰双联雷印符，铜雷记'),('thunder_talisman','n','paper','b','bolt','暖纸雷符，单一蓝色阶梯雷纹'),('tiangang_talisman','b','paper','n','star','青色天罡符，白色星杓状符心'),('turtle_blood_charm','r','folded','n','wall','暗血符纸与白色龟甲格纹'),('vajra_talisman','y','fan','g','wall','宽扇金刚符，金色护壁与收拢符尾'),('wind_talisman','j','paper','n','wind','青纸风符，两段骨白回风纹')]:
 DESIGNS[id]={'family':'talisman','m':m,'v':v,'accent':accent,'glyph':g,'design':detail}
FIRST24=['copper_coin','silver_coin','jade_coin','abyss_pearl','sea_pearl','eclipse_bead','lifedrain_ring','jade_ring','dragon_emperor_seal','official_seal','seal_of_two_heavens','sea_token','cinnabar_pouch','cloud_brocade','trinket_box','armor_piercer_token','mandarin_rank_badge','sky_token','fire_talisman','edict_of_iron','disha_talisman','dragon_scale_sash','pike_tassel','dragon_whisker']

def render(id):
 cfg=DESIGNS[id];return globals()[cfg['family']](id,cfg).im

def validate(im):
 colors={p for p in im.get_flattened_data() if p[3]};alpha=set(im.getchannel('A').get_flattened_data());bbox=im.getchannel('A').getbbox()
 assert im.size==(32,32) and alpha<= {0,255}
 assert bbox and bbox[0]>=1 and bbox[1]>=1 and bbox[2]<=31 and bbox[3]<=31,bbox
 return {'size':[32,32],'opaque_colors':len(colors),'alpha':sorted(alpha),'bbox':list(bbox),'original_grid':True}
def preview(names,prefix):
 fontp=next(p for p in [Path('/System/Library/Fonts/PingFang.ttc'),Path('/System/Library/Fonts/STHeiti Light.ttc'),Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')] if p.exists())
 font=ImageFont.truetype(str(fontp),17);small=ImageFont.truetype(str(fontp),12)
 lang=json.loads((R/'src/main/resources/assets/dynasty/lang/zh_cn.json').read_text())
 for start in range(0,len(names),20):
  sub=names[start:start+20];rows=math.ceil(len(sub)/4);sheet=Image.new('RGB',(1120,58+rows*218),'#e7e6dc');d=ImageDraw.Draw(sheet)
  d.text((14,12),'原生 32×32 物品候选｜左：当前源图　右：新绘最近邻 4×　下：1×新图',font=font,fill='#233b35')
  for k,id in enumerate(sub):
   x=12+k%4*278;y=52+k//4*218;before=Image.open(OUT/'before'/f'{id}.png').convert('RGBA');new=Image.open(OUT/'candidate/assets/dynasty/textures/item'/f'{id}.png')
   d.text((x,y),lang.get('item.dynasty.'+id,id),font=font,fill='#233b35');d.text((x,y+22),id,font=small,fill='#59625c')
   for xx,sz in [(x,64),(x+82,128)]:
    for a in range(sz//8):
     for b in range(sz//8):d.rectangle((xx+a*8,y+43+b*8,xx+a*8+7,y+43+b*8+7),fill='#c8cebf' if (a+b)%2 else '#dde0d5')
   old=before.resize((64,64),Image.Resampling.NEAREST);sheet.paste(old,(x,y+43),old);large=new.resize((128,128),Image.Resampling.NEAREST);sheet.paste(large,(x+82,y+43),large)
   sheet.paste(new,(x,y+173),new);d.text((x+39,y+181),f'1× / {validate(new)["opaque_colors"]}色',font=small,fill='#566054')
  sheet.save(OUT/'previews'/f'{prefix}-{start//20+1:02}.png')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--first',action='store_true');args=ap.parse_args();allowed=json.loads((OUT/'allowed.json').read_text());names=FIRST24 if args.first else allowed
 missing=set(names)-set(DESIGNS);assert not missing,missing
 rows=[];existing=json.loads((OUT/'manifest/baseline.json').read_text());base={x['id']:x for x in existing};lang=json.loads((R/'src/main/resources/assets/dynasty/lang/zh_cn.json').read_text())
 for id in names:
  assert id in allowed;im=render(id);stats=validate(im);dest=OUT/'candidate/assets/dynasty/textures/item'/f'{id}.png';im.save(dest)
  rows.append({'id':id,'name':lang.get('item.dynasty.'+id,id),**DESIGNS[id],**stats,'status':'candidate_not_installed','path':str(dest.relative_to(OUT)),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_sha256':base[id]['source_sha256'],'model_layer0':base[id]['layer0'],'source_unchanged':hashlib.sha256((R/base[id]['source']).read_bytes()).hexdigest()==base[id]['source_sha256']})
 (OUT/'manifest'/('first24.json' if args.first else 'all-items.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');preview(names,'first24' if args.first else 'all');print('generated',len(rows),'max colors',max(x['opaque_colors'] for x in rows),'all source unchanged',all(x['source_unchanged'] for x in rows))
exec((OUT/'generator/custom_structures.py').read_text(), globals())
if __name__=='__main__':main()

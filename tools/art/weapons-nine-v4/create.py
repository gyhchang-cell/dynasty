"""Exact-grid local review sprites. Bow variants edit vanilla pixels, never redraw its mask."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, zipfile, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/art/weapons-nine-v4'
OUT.mkdir(parents=True,exist_ok=True)
TEX=OUT/'textures';TEX.mkdir(exist_ok=True)
JAR=Path('/Users/a15356015027/Public/.minecraft/versions/1.20.1/1.20.1.jar')
def vanilla(name):
 import io
 with zipfile.ZipFile(JAR) as z:return Image.open(io.BytesIO(z.read('assets/minecraft/textures/item/'+name+'.png'))).convert('RGBA')
def rgb(h):return tuple(bytes.fromhex(h))+(255,)
def recolor(im,changes):
 out=im.copy()
 for y in range(16):
  for x in range(16):
   c=im.getpixel((x,y))
   if c[:3] in changes and c[3]:out.putpixel((x,y),rgb(changes[c[:3]]))
 return out
bow_palette=[(73,54,21),(137,103,39),(104,78,30),(40,30,11)]
# Original neutral bow string (68,68,68) remains unchanged in every frame.
bow_schemes={
 'hunter_bow':(['493615','896727','684E1E','281E0B'],['633728','A76B45','D1AB77']),
 'copper_bow':(['483020','A57943','785331','281C15'],['75402D','BE754B','E1A66E']),
 'bamboo_bow':(['414B24','9AAB54','6C7F38','25301C'],['63452C','A87B48','D0B278'])}
checks=[];sprites={}
for name,(wood,bindings) in bow_schemes.items():
 for frame in ['bow','bow_pulling_0','bow_pulling_1','bow_pulling_2']:
  src=vanilla(frame)
  changes=dict(zip(bow_palette,wood));changes.update(dict(zip([(107,107,107),(150,150,150)],bindings[:2])))
  # White arrow tip and gray string must not be recolored in drawn frames.
  im=src.copy()
  for y in range(16):
   for x in range(16):
    c=src.getpixel((x,y));k=c[:3]
    if not c[3]:continue
    if k in bow_palette:im.putpixel((x,y),rgb(changes[k]))
    elif k in [(107,107,107),(150,150,150)] and x<=6 and 4<=y<=8:im.putpixel((x,y),rgb(changes[k]))
  # End collars are painted only over existing wood, in corresponding endpoint regions.
  if name=='copper_bow':
   for y in range(16):
    for x in range(16):
     c=src.getpixel((x,y))
     if c[:3] in bow_palette[:3] and c[3] and ((x>=12 and y<=3) or (x<=3 and y==13)):
      im.putpixel((x,y),rgb(bindings[bow_palette[:3].index(c[:3])%3]))
  if name=='bamboo_bow':
   for y in range(16):
    for x in range(16):
     c=src.getpixel((x,y))
     if c[:3] in bow_palette[1:3] and c[3] and ((x==9 and y<=4) or (y==11 and x<=4)):
      im.putpixel((x,y),rgb('B7AA69'))
  same_mask=im.getchannel('A').tobytes()==src.getchannel('A').tobytes()
  string=[(x,y) for y in range(16) for x in range(16) if src.getpixel((x,y))==(68,68,68,255)]
  same_string=all(im.getpixel(p)==src.getpixel(p) for p in string)
  assert same_mask and same_string
  dest=name+('' if frame=='bow' else frame.replace('bow',''))
  im.save(TEX/(dest+'.png'))
  checks.append({'file':dest+'.png','base':frame,'alpha_identical':same_mask,'string_pixels_identical':same_string,'modified_pixels':sum(a!=b for a,b in zip(src.getdata(),im.getdata()))})
  if frame=='bow':sprites[name]=im
# Vanilla compact iron sword geometry with distinct material and grip treatments.
base=vanilla('iron_sword')
metal=[(68,68,68),(255,255,255),(24,24,24),(190,190,190),(216,216,216),(107,107,107),(150,150,150)]
variants={
 'copper_jian':(['683B2B','F2C49B','362820','BF794D','D99565','855039','A66843'],['49301F','765033','A77948','291E18']),
 'iron_jian':(['404950','F4F5ED','20292F','AEBBBF','D6DFDC','657078','8F9C9D'],['3C2B23','70513A','A27A4B','241C19']),
 'red_jian':(['3D4C56','EEF2E9','202C33','A5BAC3','CFDDE0','647B85','8EA0A5'],['52282A','8D3E39','BD6650','301C21'])}
for name,(steel,wood) in variants.items():
 im=recolor(base,dict(zip(metal,steel))|dict(zip(bow_palette,wood)))
 if name=='red_jian':
  for p,c in {(2,6):'675139',(3,6):'B59652',(2,7):'B59652',(3,7):'D2BA78',(4,8):'B59652',(6,10):'B59652',(7,11):'D2BA78',(8,12):'B59652',(1,13):'B59652',(1,14):'D2BA78'}.items():
   if im.getpixel(p)[3]:im.putpixel(p,rgb(c))
 # Add thickness to the grip on its two lower staircase segments, not to the whole blade.
 for x,y in [(3,13),(2,14)]:
  if not im.getpixel((x,y))[3]:im.putpixel((x,y),rgb(wood[0]))
 im.save(TEX/(name+'.png'));sprites[name]=im
# Original 16x16 masks: separate functional silhouettes, no copied mod sprite.
pal={'.':(0,0,0,0),'o':rgb('30363A'),'s':rgb('68767B'),'m':rgb('AAB8B5'),'h':rgb('E1E5D3'),'d':rgb('34291F'),'w':rgb('785037'),'l':rgb('B48A50'),'b':rgb('CEB281')}
grids={'stone_ge': ['................', '..oo............', '..ohhoo.........', '..osmmhoo.......', '....osmmhoo.....', '......osmmbdo...', '........olbdo...', '........lwdo....', '.......lwdo.....', '......lwdo......', '.....lwdo.......', '....lwdo........', '...lwdo.........', '..lwdo..........', '.lwdo...........', '..do............'], 'harvest_sickle': ['................', '..oooooo........', '.ohhhhmmhoo.....', '.osssssssmhoo...', '..ooooooosmmho..', '..........osbo..', '..........lbdo..', '.........lwdo...', '........lwdo....', '.......lwdo.....', '......lwdo......', '.....lwdo.......', '....lwdo........', '...lwdo.........', '..lwdo..........', '...do...........'], 'chisel_hammer': ['................', '.........oo.....', '........ohmo....', '.......ohmmso...', '......ohmmmsso..', '......osmmmsso..', '.......osmsso...', '........lbso....', '.......lwdoo....', '......lwdo......', '.....lwdo.......', '....lwdo........', '...lwdo.........', '..lwdo..........', '.lwdo...........', '..do............']}
for name,lines in grids.items():
 assert len(lines)==16 and all(len(x)==16 for x in lines),(name,[len(x) for x in lines])
 im=Image.new('RGBA',(16,16))
 for y,row in enumerate(lines):
  for x,c in enumerate(row):im.putpixel((x,y),pal[c])
 im.save(TEX/(name+'.png'));sprites[name]=im
(OUT/'pixel-sources.json').write_text(json.dumps({'tool_grids':grids,'tool_palette':{k:list(v) for k,v in pal.items()},'bow_schemes':bow_schemes,'sword_palettes':variants},indent=2))
# Review at identical scale, never interpolate.
order=['copper_jian','iron_jian','red_jian','hunter_bow','copper_bow','bamboo_bow','stone_ge','harvest_sickle','chisel_hammer']
labels=['铜剑','铁剑','赤柄钢剑','猎弓','铜箍弓','青竹弓','石戈','割草镰','铁凿锤']
fontfile='/System/Library/Fonts/STHeiti Medium.ttc'
font=ImageFont.truetype(fontfile,23);small=ImageFont.truetype(fontfile,16)
canvas=Image.new('RGB',(960,1020),'#22282e');d=ImageDraw.Draw(canvas)
for i,name in enumerate(order):
 x=i%3*320;y=i//3*340
 d.rounded_rectangle((x+10,y+10,x+310,y+330),12,fill='#343e46')
 im=sprites[name];large=im.resize((224,224),Image.Resampling.NEAREST);canvas.paste(large,(x+48,y+24),large)
 d.text((x+24,y+260),labels[i],font=font,fill='#f0dfba')
 d.text((x+24,y+296),'16×16 · 原尺寸像素',font=small,fill='#b4c2c5')
 mini=im.resize((32,32),Image.Resampling.NEAREST);canvas.paste(mini,(x+260,y+270),mini)
canvas.save(OUT/'nine-review.png')
vanilla('bow').save(OUT/'vanilla-bow-reference.png')
canvas=Image.new('RGB',(960,280),'#343e46');d=ImageDraw.Draw(canvas)
for i,(name,im) in enumerate([('原版弓',vanilla('bow'))]+[(labels[order.index(k)],sprites[k]) for k in ['hunter_bow','copper_bow','bamboo_bow']]):
 large=im.resize((192,192),Image.Resampling.NEAREST);canvas.paste(large,(i*240+24,16),large);d.text((i*240+24,228),name,font=font,fill='#f0dfba')
canvas.save(OUT/'bow-comparison.png')
for p in TEX.glob('*.png'):
 im=Image.open(p).convert('RGBA');assert im.size==(16,16);assert set(im.getchannel('A').getdata())<={0,255}
(OUT/'validation.json').write_text(json.dumps({'status':'static_checks_passed_not_game_tested','unique_items':9,'png_count':len(list(TEX.glob('*.png'))),'all_dimensions':[16,16],'alpha_binary':True,'bows':checks,'runtime_assets_modified':False},ensure_ascii=False,indent=2))
print('Created 9 items + 9 drawn bow frames; 12 exact bow mask/string checks passed.')

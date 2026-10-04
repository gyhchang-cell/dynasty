"""Original integer-grid 16px notice board. Texture-only cube substitution."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib, shutil, zipfile, io
D=Path(__file__).resolve().parent
ROOT=D.parents[3]
S=ROOT/'src/main/resources/assets/dynasty'
A=D/'candidate/assets/dynasty'
P={'dark':'#594633','seam':'#71533a','shade':'#896445','wood':'#a27d50','light':'#bc975e','end':'#c6a36e',
   'paper':'#d9c391','paperlight':'#e9d5a4','papershade':'#bca173','ink':'#796746','seal':'#a7523c','pin':'#667071'}
def wood(kind):
 im=Image.new('RGB',(16,16),P['wood']); d=ImageDraw.Draw(im)
 if kind in ('back','bottom'):
  for y in (0,5,10):
   d.line((0,y,15,y),fill=P['seam']); d.line((0,y+1,15,y+1),fill=P['light'])
  for x,y,w in [(2,3,4),(11,3,3),(7,8,5),(0,13,4),(10,14,3)]:d.line((x,y,x+w,y),fill=P['shade'])
  d.line((7,1,7,4),fill=P['shade']);d.line((12,6,12,9),fill=P['shade']);d.line((5,11,5,15),fill=P['shade'])
 elif kind=='side':
  for x in (0,5,10,15):d.line((x,0,x,15),fill=P['seam'])
  for x in (1,6,11):d.line((x,0,x,15),fill=P['light'])
  for x,y,h in [(3,2,4),(8,10,4),(13,4,5)]:d.line((x,y,x,y+h),fill=P['shade'])
 else:
  d.rectangle((0,0,15,15),outline=P['shade']);d.rectangle((1,1,14,14),outline=P['light'])
  d.line((5,2,5,13),fill=P['seam']);d.line((10,2,10,13),fill=P['seam'])
  d.line((3,4,3,9),fill=P['shade']);d.line((8,7,8,11),fill=P['light']);d.line((12,3,12,8),fill=P['shade'])
 if kind!='bottom':
  d.rectangle((0,0,15,1),fill=P['dark']);d.line((0,0,15,0),fill=P['light'])
  d.rectangle((0,14,15,15),fill=P['shade']);d.line((0,14,15,14),fill=P['light'])
 return im
def draw_front():
 im=wood('back');d=ImageDraw.Draw(im)
 d.rectangle((0,0,1,15),fill=P['dark']);d.rectangle((14,0,15,15),fill=P['shade'])
 d.line((0,0,0,15),fill=P['light']);d.line((14,1,14,13),fill=P['light'])
 d.rectangle((3,3,8,11),fill=P['papershade']);d.rectangle((3,3,7,10),fill=P['paper'])
 d.line((3,3,7,3),fill=P['paperlight']);d.point((5,3),fill=P['pin'])
 d.line((4,5,6,5),fill=P['ink']);d.line((4,7,6,7),fill=P['ink']);d.point((4,9),fill=P['seal']);d.point((5,9),fill=P['seal'])
 d.rectangle((9,5,12,12),fill=P['papershade']);d.rectangle((9,5,11,11),fill=P['paperlight'])
 d.point((10,5),fill=P['pin']);d.line((10,7,11,7),fill=P['ink']);d.point((10,9),fill=P['seal'])
 return im
def main():
 (A/'textures/block').mkdir(parents=True,exist_ok=True);(A/'models/block').mkdir(parents=True,exist_ok=True)
 for rel in ['models/block/bounty_board.json','models/item/bounty_board.json','blockstates/bounty_board.json']:
  before=D/'before'/rel;before.parent.mkdir(parents=True,exist_ok=True)
  if not before.exists():shutil.copy2(S/rel,before)
  assert before.read_bytes()==(S/rel).read_bytes()
 records=[]
 for face in ['front','back','side','top','bottom']:
  im=draw_front() if face=='front' else wood(face)
  out=A/'textures/block'/f'bounty_board_{face}.png';im.save(out)
  records.append({'id':'dynasty:bounty_board','face':face,'candidate':str(out.relative_to(D)),'size':[16,16],
    'colors':len(im.getcolors()),'alpha':'fully_opaque','sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
 model={'parent':'minecraft:block/cube','textures':{'particle':'dynasty:block/bounty_board_back',
  'north':'dynasty:block/bounty_board_front','south':'dynasty:block/bounty_board_back',
  'east':'dynasty:block/bounty_board_side','west':'dynasty:block/bounty_board_side',
  'up':'dynasty:block/bounty_board_top','down':'dynasty:block/bounty_board_bottom'}}
 (A/'models/block/bounty_board.json').write_text(json.dumps(model,indent=2)+'\n')
 (D/'manifest.json').write_text(json.dumps({'status':'candidate_not_installed','id':'dynasty:bounty_board','files':records,
  'evidence':'docs/content/bounty-board-v1.md:178 explicitly says temporary bookshelf and no artwork generated',
  'geometry':'unchanged full 16x16x16 cube; parent switches cube_all to cube solely to map existing faces',
  'orientation':'Front remains fixed north because current blockstate has no facing property. No code added.',
  'connected':'blockstates/bounty_board -> block/bounty_board -> five native textures; item inherits same block model',
  'not_added':['facing property','custom shape','collision','interaction code','animation','emissive']},ensure_ascii=False,indent=2)+'\n')
 (D/'previews').mkdir(exist_ok=True)
 c=Image.new('RGB',(1080,670),'#e8e9df');d=ImageDraw.Draw(c);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
 d.text((20,15),'BOUNTY BOARD / native 16px + nearest 8x + 3x3 repeat / candidate only',fill='#263831',font=font)
 for j,face in enumerate(['front','back','side','top','bottom']):
  im=Image.open(A/'textures/block'/f'bounty_board_{face}.png');x=20+j*210
  d.text((x,60),face,fill='#263831',font=font);c.paste(im,(x,90));c.paste(im.resize((128,128),Image.Resampling.NEAREST),(x,125))
  tile=Image.new('RGB',(48,48))
  for xx in range(3):
   for yy in range(3):tile.paste(im,(16*xx,16*yy))
  c.paste(tile.resize((192,192),Image.Resampling.NEAREST),(x,280))
  tile.save(D/'previews'/f'{face}-3x3.png')
 # Vanilla reference is read locally for the before comparison only; never packed.
 jar=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client-extra.jar')
 with zipfile.ZipFile(jar) as z:
  old=Image.open(io.BytesIO(z.read('assets/minecraft/textures/block/bookshelf.png'))).convert('RGB')
 old.save(D/'before/bookshelf-reference.png');c.paste(old,(20,540));c.paste(old.resize((80,80),Image.Resampling.NEAREST),(60,540))
 d.text((160,552),'Before: vanilla bookshelf temporarily used on every face.',fill='#263831',font=font)
 d.text((160,583),'After: notices / timber side / top / base. Existing full-cube geometry.',fill='#263831',font=font)
 c.save(D/'previews/bounty-board-comparison.png')
if __name__=='__main__':main()

"""Reference analysis sheets only. Original source PNG bytes unchanged."""
from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw
ROOT=Path.cwd()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sheets(b,paths,stem):
 pages=[]
 for off in range(0,len(paths),6):
  chunk=paths[off:off+6];out=Image.new('RGB',(1080,math.ceil(len(chunk)/3)*310),(81,87,91));d=ImageDraw.Draw(out)
  for i,p in enumerate(chunk):
   im=Image.open(p).convert('RGBA');x=i%3*360;y=i//3*310;d.text((x+8,y+4),p.name,(255,255,255));d.text((x+8,y+20),str(im.size),(255,255,255));s=max(1,min(344//im.width,264//im.height));im=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);out.paste(im,(x+8,y+40),im)
  p=b/f'{stem}-{off//6+1:02}.png';out.save(p);pages.append({'path':str(p),'sha256':sha(p)})
 save(b/(stem+'-index.json'),{'pages':pages,'originals':[{'path':str(p),'sha256':sha(p),'size':Image.open(p).size}for p in paths],'integer_nearest_neighbor':True,'game_capture':False});return pages
if __name__=='__main__':
 b=ROOT/'docs/art/armor-wanderer-whole-20261112';r=b/'source/src/main/resources/assets/atum';paths=[r/f'textures/item/wanderer_{s}.png'for s in ['helmet','chest','legs','boots']]+sorted((r/'textures/models/armor').glob('*.png'));print(sheets(b,paths,'active-native'))

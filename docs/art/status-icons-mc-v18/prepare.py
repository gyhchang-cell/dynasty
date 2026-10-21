"""Preserve generated original pixels; only trim alpha margins and add2px alpha pad."""
from pathlib import Path
import json,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parent;R=D.parents[2];A=R/'src/main/resources/assets/dynasty'
# D=repo/docs/art/batch => repo is parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 rows=json.loads((D/'selection.json').read_text());report=[];(D/'runtime').mkdir(exist_ok=True)
 for r in rows:
  p=D/'sources'/f"{r['id']}.png";im=Image.open(p).convert('RGBA');box=im.getbbox();assert box
  assert im.getextrema()[3][0]==0,'Opaque background: '+r['id']
  crop=im.crop(box);side=max(crop.width,crop.height)+4;offset=((side-crop.width)//2,(side-crop.height)//2);out=Image.new('RGBA',(side,side));out.paste(crop,offset);q=D/'runtime'/p.name;out.save(q)
  assert out.crop((offset[0],offset[1],offset[0]+crop.width,offset[1]+crop.height)).tobytes()==crop.tobytes()
  report.append({'id':r['id'],'sourceSha256':sha(p),'runtimeSha256':sha(q),'sourceSize':list(im.size),'runtimeSize':list(out.size),'crop':list(box),'pasteOffset':list(offset),'alphaPixels':sum(v==0 for v in out.getchannel('A').getdata()),'partialAlphaPixels':sum(0<v<255 for v in out.getchannel('A').getdata()),'originalRgbPreserved':True})
 (D/'source-validation.json').write_text(json.dumps(report,indent=2)+'\n')
 font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',19)
 # Only review thumbnails are resized. Production PNGs remain original resolution.
 for mode in ('comparison','after'):
  w=1200;cellh=190 if mode=='comparison' else 150;out=Image.new('RGB',(w,60+((len(rows)+5)//6)*cellh),'#555c61');d=ImageDraw.Draw(out);d.text((16,12),'实际运行资源预览 · 原稿像素保留 · 非游戏截图',font=font,fill='white')
  for i,r in enumerate(rows):
   x=i%6*200;y=60+i//6*cellh
   new=Image.open(D/'runtime'/f"{r['id']}.png").convert('RGBA');small=new.resize((18,18),Image.Resampling.NEAREST)
   if mode=='comparison':
    old=Image.open(D/'before'/f"{r['id']}.png").convert('RGBA').resize((54,54),Image.Resampling.NEAREST);out.paste(old,(x+12,y+10),old);s=small.resize((72,72),Image.Resampling.NEAREST);out.paste(s,(x+100,y),s);d.text((x+20,y+76),'旧',font=font,fill='#bbbbbb');d.text((x+115,y+76),'新',font=font,fill='white');dy=108
   else:
    s=small.resize((90,90),Image.Resampling.NEAREST);out.paste(s,(x+55,y),s);dy=94
   d.text((x+10,y+dy),r['name'],font=font,fill='white')
  out.save(D/f'{mode}.png')
 print('Prepared',len(rows),'originals, no production resampling')
if __name__=='__main__':prepare()

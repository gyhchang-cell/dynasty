import av,json
from PIL import Image,ImageDraw
from pathlib import Path
root=Path(__file__).parent
manifest=[]
for tag in ['22.43.13','22.44.39','22.45.54']:
 path=Path('/Users/a15356015027/Desktop')/f'录屏2026-10-31 {tag}.mov'
 out=root/tag;out.mkdir(exist_ok=True)
 thumbs=[];samples=[]
 with av.open(str(path)) as c:
  s=c.streams.video[0];duration=c.duration/1e6
  for target in range(0,int(duration),3):
   c.seek(int(target/float(s.time_base)),stream=s)
   for f in c.decode(s):
    if f.time+1e-6<target:continue
    im=f.to_image();im.thumbnail((480,311));thumbs.append(im)
    samples.append({'time':float(f.time),'page':(len(thumbs)-1)//12+1})
    break
 for start in range(0,len(thumbs),12):
  sheet=Image.new('RGB',(1920,3*340),(24,24,28));draw=ImageDraw.Draw(sheet)
  for k,im in enumerate(thumbs[start:start+12]):
   x=k%4*480;y=k//4*340;sheet.paste(im,(x,y));draw.text((x+8,y+315),f'{tag}  t={samples[start+k]["time"]:.3f}s',fill='white')
  sheet.save(out/f'overview-{start//12+1}.jpg',quality=90)
 manifest.append({'file':str(path),'duration':duration,'sampling':'one frame per 3 seconds, overview only','samples':samples})
(root/'overview.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Overview pages generated')

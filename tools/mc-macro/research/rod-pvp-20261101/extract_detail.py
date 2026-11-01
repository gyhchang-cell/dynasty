import av,json,argparse
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('tag');p.add_argument('start',type=float);p.add_argument('end',type=float);p.add_argument('--fps',type=float,default=4);a=p.parse_args()
root=Path(__file__).parent;out=root/a.tag/f'detail-{a.start:g}-{a.end:g}-{a.fps:g}';out.mkdir(parents=True,exist_ok=True)
path=Path('/Users/a15356015027/Desktop')/f'录屏2026-10-31 {a.tag}.mov';thumbs=[];samples=[];next_time=a.start
with av.open(str(path)) as c:
 s=c.streams.video[0];c.seek(int(a.start/float(s.time_base)),stream=s)
 for f in c.decode(s):
  t=float(f.time)
  if t+1e-6<a.start:continue
  if t>=a.end-1e-6:break
  if a.fps and t+1e-6<next_time:continue
  im=f.to_image();im.thumbnail((600,388));thumbs.append(im);samples.append({'time':t,'page':(len(thumbs)-1)//9+1})
  next_time+=1/a.fps if a.fps else 0
for start in range(0,len(thumbs),9):
 sheet=Image.new('RGB',(1800,3*418),(20,20,24));d=ImageDraw.Draw(sheet)
 for k,im in enumerate(thumbs[start:start+9]):
  x=k%3*600;y=k//3*418;sheet.paste(im,(x,y));d.text((x+10,y+391),f'{a.tag}  {samples[start+k]["time"]:.4f}s | frame {start+k}',fill='white')
 sheet.save(out/f'page-{start//9+1:02}.jpg',quality=92)
(out/'manifest.json').write_text(json.dumps({'source':str(path),'sampling':'every decoded frame' if not a.fps else f'{a.fps} fps sample','start':a.start,'end_exclusive':a.end,'frames':samples},indent=2))
print(out,len(samples))

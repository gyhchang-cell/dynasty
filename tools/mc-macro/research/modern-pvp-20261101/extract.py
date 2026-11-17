import argparse, json
from pathlib import Path
import av
from PIL import Image,ImageDraw

p=argparse.ArgumentParser()
p.add_argument('source');p.add_argument('start',type=float);p.add_argument('end',type=float)
p.add_argument('--step',type=float,default=0)
p.add_argument('--tag',required=True)
a=p.parse_args()
out=Path(__file__).parent/a.tag;out.mkdir(exist_ok=True)
frames=[];images=[];next_time=a.start
with av.open(a.source) as container:
    stream=container.streams.video[0]
    container.seek(int(a.start/float(stream.time_base)),stream=stream)
    fps=str(stream.average_rate)
    for f in container.decode(stream):
        t=float(f.time)
        if t<a.start-0.0001:continue
        if t>=a.end-0.0001:break
        if a.step and t<next_time-0.0001:continue
        im=f.to_image();im.thumbnail((640,360))
        images.append(im);frames.append({'time':t,'pts':f.pts,'page':(len(images)-1)//12+1})
        if a.step:next_time=t+a.step
for start in range(0,len(images),12):
    page=Image.new('RGB',(1920,4*385),(20,20,24));d=ImageDraw.Draw(page)
    for k,im in enumerate(images[start:start+12]):
        x=k%3*640;y=k//3*385;page.paste(im,(x,y))
        d.text((x+8,y+363),f'{frames[start+k]["time"]:.4f}s | frame {start+k}',fill='white')
    page.save(out/f'page-{start//12+1:02}.jpg',quality=93)
(out/'manifest.json').write_text(json.dumps({'source':a.source,'fps':fps,'mode':'every decoded frame' if not a.step else f'sampled every {a.step}s','start':a.start,'end':a.end,'frames':frames},indent=2))
print(a.tag,len(frames),fps,flush=True)

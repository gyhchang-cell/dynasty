import av,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
out=Path(__file__).parent;src=Path('/Users/a15356015027/Desktop/吃屎');records=[];seen={}
for i,p in enumerate(sorted(src.glob('*.mov'))):
 h=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
 if h in seen:
  records.append({'file':str(p),'duplicate_of':seen[h],'sha256':h});continue
 seen[h]=str(p)
 with av.open(str(p)) as c:
  s=c.streams.video[0];duration=c.duration/1e6;times=[duration*(j+.5)/12 for j in range(12)]
  page=Image.new('RGB',(1920,1760),(20,20,24));draw=ImageDraw.Draw(page);frames=[]
  for j,t in enumerate(times):
   c.seek(int(t/float(s.time_base)),stream=s)
   for f in c.decode(s):
    if float(f.time)>=t:break
   im=f.to_image();im.thumbnail((640,414));x=j%3*640;y=j//3*440;page.paste(im,(x,y));draw.text((x+6,y+418),f'{i:02d}  {float(f.time):.3f}s',fill='white');frames.append(float(f.time))
  path=out/f'overview-{i:02d}.jpg';page.save(path,quality=90)
  records.append({'file':str(p),'sha256':h,'duration':duration,'fps':str(s.average_rate),'sheet':str(path),'sample_times':frames})
  print(p.name,path,flush=True)
(out/'inventory.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))

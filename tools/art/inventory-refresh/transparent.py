"""Remove only edge-connected pure-white export matte from approved legacy icons.
No artwork is drawn or recolored; enclosed foreground white is retained.
"""
from pathlib import Path
from collections import deque
import json,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];DOC=ROOT/'docs/art/inventory-refresh-v1';A=ROOT/'src/main/resources/assets/dynasty'
def cleanup_white():
 changed=[]
 for ident in json.loads((DOC/'white-backgrounds.json').read_text()):
  path=A/'textures/item'/f'{ident}.png';im=Image.open(path).convert('RGBA');px=im.load();w,h=im.size
  queue=deque([(x,y) for x in range(w) for y in (0,h-1)]+[(x,y) for y in range(h) for x in (0,w-1)]);seen=set();removed=[]
  while queue:
   x,y=queue.popleft()
   if (x,y) in seen or not(0<=x<w and 0<=y<h):continue
   seen.add((x,y))
   if px[x,y]!=(255,255,255,255):continue
   removed.append((x,y));queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
  if not removed:continue
  dest=DOC/'before'/path.relative_to(A);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():shutil.copy2(path,dest)
  for pos in removed:px[pos]=(255,255,255,0)
  im.save(path);changed.append({'id':ident,'backgroundPixelsRemoved':len(removed)})
 if changed:(DOC/'transparency-report.json').write_text(json.dumps(changed,indent=2)+'\n')
 print('Removed white matte:',len(changed))
if __name__=='__main__':cleanup_white()

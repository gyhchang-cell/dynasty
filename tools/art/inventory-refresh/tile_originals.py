"""Lossless vanilla unstitch regions; preserve front/back and alpha-contour item thickness."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from block_atlas_sources import with_model_sprites
import json,zipfile
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-originals-v4';A=R/'src/main/resources/assets/dynasty';SIZE=256

def generate():
 rows=json.loads((D/'selection.json').read_text());ids=[r['id'] for r in rows]
 sources=[{'type':'minecraft:filter','pattern':{'namespace':'^dynasty$','path':'^item/('+ '|'.join(ids)+')$'}}]
 with zipfile.ZipFile(Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar') as z:display=json.loads(z.read('assets/minecraft/models/item/generated.json'))['display']
 report=[]
 for id in ids:
  im=Image.open(A/'textures/item'/f'{id}.png').convert('RGBA');w,h=im.size;mask=np.asarray(im)[:,:,3]>0;regions=[];elements=[];textures={};tiles={}
  for y in range(0,h,SIZE):
   for x in range(0,w,SIZE):
    tw,th=min(SIZE,w-x),min(SIZE,h-y);key=f't{x}_{y}';sprite=f'dynasty:item/original_tiles/{id}/{key}';tiles[x,y]=(key,tw,th)
    regions.append({'sprite':sprite,'x':x,'y':y,'width':tw,'height':th});textures[key]=sprite
    elements.append({'from':[16*x/w,16*(h-y-th)/h,7.5],'to':[16*(x+tw)/w,16*(h-y)/h,8.5],'shade':False,'faces':{'south':{'uv':[0,0,16,16],'texture':'#'+key},'north':{'uv':[16,0,0,16],'texture':'#'+key}}})
  # Only genuine alpha boundaries extrude. Tile boundaries introduce no extra edges.
  for direction in ['up','down','west','east']:
   neighbor=np.zeros_like(mask)
   if direction=='up':neighbor[1:,:]=mask[:-1,:]
   if direction=='down':neighbor[:-1,:]=mask[1:,:]
   if direction=='west':neighbor[:,1:]=mask[:,:-1]
   if direction=='east':neighbor[:,:-1]=mask[:,1:]
   edge=mask & ~neighbor;horizontal=direction in ('up','down');scan=edge if horizontal else edge.T
   for anchor,line in enumerate(scan):
    points=np.flatnonzero(line)
    if not len(points):continue
    groups=np.split(points,np.flatnonzero(points[:-1]//SIZE!=points[1:]//SIZE)+1)
    for g in groups:
     lo,hi=int(g[0]),int(g[-1])+1;x,y=(lo,anchor) if horizontal else (anchor,lo);tx,ty=x//SIZE*SIZE,y//SIZE*SIZE;key,tw,th=tiles[tx,ty]
     if horizontal:
      plane=anchor+(direction=='down');fr=[16*lo/w,16*(h-plane)/h,7.5];to=[16*hi/w,fr[1],8.5];uv=[16*(lo-tx)/tw,16*(anchor-ty)/th,16*(hi-tx)/tw,16*(anchor+1-ty)/th]
     else:
      plane=anchor+(direction=='east');fr=[16*plane/w,16*(h-hi)/h,7.5];to=[fr[0],16*(h-lo)/h,8.5];uv=[16*(anchor-tx)/tw,16*(hi-ty)/th,16*(anchor+1-tx)/tw,16*(lo-ty)/th]
     elements.append({'from':fr,'to':to,'shade':False,'faces':{direction:{'uv':uv,'texture':'#'+key}}})
  textures['particle']=textures[tiles[(w//2)//SIZE*SIZE,(h//2)//SIZE*SIZE][0]]
  model={'gui_light':'front','ambientocclusion':False,'display':display,'textures':textures,'elements':elements}
  (A/'models/item'/f'{id}.json').write_text(json.dumps(model,separators=(',',':'))+'\n')
  sources.append({'type':'minecraft:unstitch','resource':'dynasty:item/'+id,'divisor_x':w,'divisor_y':h,'regions':regions})
  report.append({'id':id,'regions':len(regions),'elements':len(elements),'size':[w,h]})
 p=R/'src/main/resources/assets/minecraft/atlases/blocks.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'sources':with_model_sprites(sources)},indent=2)+'\n')
 (D/'tile-report.json').write_text(json.dumps(report,indent=2));print('Tiled originals:',len(report),'items;',sum(x['regions'] for x in report),'regions')
if __name__=='__main__':generate()

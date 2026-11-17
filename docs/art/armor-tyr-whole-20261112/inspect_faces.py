"""Read original texture rectangles only; no production output."""
from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('source_geometry',B/'static_uv_analysis.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
page=Image.new('RGB',(1080,1340),'#50565a');d=ImageDraw.Draw(page);d.text((5,5),'ORIGINAL SOURCE UV / MIRROR IN WHOLE VIEW / SOFTWARE NOT GAME',fill='white');rows=[]
for row,box in enumerate(m.boxes):
 _,rects=m.cube_faces(box);d.text((5,row*130+25),f'{box[0]} L{box[6]} inflate={box[5]} mirror={box[4]}',fill='white');entry={'part':box[0],'layer':box[6],'faces':{}}
 for col,(face,r) in enumerate(rects.items()):
  u,v,U,V=r;rect=(int(min(u,U)),int(min(v,V)),int(max(u,U)),int(max(v,V)));assert 0<=rect[0]<=rect[2]<=64 and 0<=rect[1]<=rect[3]<=32
  crop=m.textures[box[6]].crop(rect);a=list(crop.getchannel('A').get_flattened_data());entry['faces'][face]={'rect':r,'area':len(a),'nonzero_alpha':sum(x>0 for x in a),'opaque_alpha':sum(x==255 for x in a)}
  im=crop.resize((crop.width*5,crop.height*5),Image.Resampling.NEAREST);page.paste(im,(col*180+5,row*130+60),im);d.text((col*180+5,row*130+45),face+' '+str(r),fill='white')
 rows.append(entry)
page.save(B/'raw-uv-faces.png');(B/'uv-alpha-measurements.json').write_text(json.dumps(rows,indent=2)+'\n')
models=[]
for p in sorted((B/'source/src/generated/resources/assets/forbidden_arcanus/models/item').glob('*.json')):
 data=json.loads(p.read_text());assert data['parent']=='minecraft:item/generated';assert list(data['textures'])==['layer0'];tex=B/'source/src/main/resources/assets/forbidden_arcanus/textures'/(data['textures']['layer0'].split(':')[1]+'.png');assert tex.exists();models.append({'model':str(p.resolve()),'json':data,'texture':str(tex.resolve())})
(B/'item-model-resolution.json').write_text(json.dumps(models,indent=2)+'\n')
print('faces',sum(len(x['faces']) for x in rows),'models',len(models))

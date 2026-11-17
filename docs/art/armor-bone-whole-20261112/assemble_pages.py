"""Analysis pages only. Original and production PNGs remain read-only."""
from pathlib import Path
from PIL import Image,ImageDraw
import importlib.util,json
B=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('bone_context',B/'static_uv_analysis.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
page=Image.new('RGB',(1320,1400),'#4b5155');d=ImageDraw.Draw(page)
for row,suffix in enumerate(['','_aqua','_crimson','_green']):
 m.textures={i:Image.open(m.T/f'bone{suffix}_{i}.png').convert('RGBA') for i in [1,2]}
 for col,(a,mode) in enumerate([(0,'texture'),(45,'texture'),(90,'texture'),(180,'texture'),(0,'silhouette'),(45,'gray')]):
  page.paste(m.render(a,mode),(col*220,row*350+25));d.text((col*220+3,row*350+5),f'{suffix or "BASE"} {a} {mode}',fill='white')
 d.text((5,row*350+330),'SOURCE SOFTWARE UV / NO GAME / NO LIGHT, POSE, GEM OBTAINABILITY OR SEAM ACCEPTANCE',fill='white')
page.save(B/'whole-all-variants.png')
raw=Image.new('RGB',(960,1320),'#50565a');d=ImageDraw.Draw(raw);d.text((5,5),'BONE RAW SOURCE FACE RECTS / legacy mirrored on whole view / NOT GAME',fill='white');m.textures={i:Image.open(m.T/f'bone_{i}.png').convert('RGBA') for i in [1,2]}
for row,box in enumerate(m.boxes):
 _,rects=m.cube_faces(box);d.text((5,row*130+25),f'{box[0]} L{box[6]} inflate={box[5]} mirror={box[4]}',fill='white')
 for col,(face,r) in enumerate(rects.items()):
  u,v,U,V=r;im=m.textures[box[6]].crop((int(min(u,U)),int(min(v,V)),int(max(u,U)),int(max(v,V))));im=im.resize((im.width*5,im.height*5),Image.Resampling.NEAREST);raw.paste(im,(col*160+5,row*130+60),im);d.text((col*160+5,row*130+45),face+' '+str(r),fill='white')
raw.save(B/'raw-uv-faces.png')
page=Image.new('RGB',(800,480),'#565d61');d=ImageDraw.Draw(page);models=B/'source/src/main/resources/assets/thebetweenlands/models/item';tex=B/'source/src/main/resources/assets/thebetweenlands/textures'
for i,p in enumerate(sorted(models.glob('bone*.json'))):
 model=json.loads(p.read_text());im=Image.open(tex/(model['textures']['layer0'].split(':')[1]+'.png')).convert('RGBA').resize((96,96),Image.Resampling.NEAREST);x=i%4*200;y=i//4*120;page.paste(im,(x+35,y),im);d.text((x+4,y+103),p.stem,fill='white')
page.save(B/'native-all-icons.png')

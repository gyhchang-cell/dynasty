from pathlib import Path
import json,sys
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).parent));from inspect_reference import sha,save
r=Path.cwd();b=r/'docs/art/armor-wanderer-whole-20261112';p=r/'docs/art/armor-mortem-whole-20261112/raw-standard-uv.json';ctx=json.loads(p.read_text());rows=[]
for i,name in enumerate(['wanderer_armor_1','wanderer_armor_1_overlay','wanderer_armor_2','wanderer_armor_2_overlay']):
 im=Image.open(b/f'source/src/main/resources/assets/atum/textures/models/armor/{name}.png').convert('RGBA');parts=ctx['rows'][0 if '_1' in name else 2]['parts'] if len(ctx['rows'])>2 else ctx['rows'][0 if '_1' in name else 1]['parts'];print(name,[v['part']for v in parts]);out=Image.new('RGB',(900,len(parts)*95),(81,87,91));d=ImageDraw.Draw(out)
 for j,part in enumerate(parts):
  d.text((5,j*95+4),part['part'],fill='white')
  for k,rect in enumerate(part['rectangles']):
   crop=im.crop(rect);crop=crop.resize((crop.width*5,crop.height*5),Image.Resampling.NEAREST);out.paste(crop,(120+k*120,j*95+18),crop);d.text((120+k*120,j*95),str(rect),fill='white')
 out.save(b/(name+'-context-uv.png'));rows.append({'texture':name,'parts':parts})
save(b/'context-uv-correspondence.json',{'standard_context_source':str(p),'sha256':sha(p),'rows':rows,'exact_1_20_4_vanilla_geometry_read':False,'oriented_final_faces_or_seams_accepted':False,'crops_are_raw_rectangles':True})

"""Offline textured cuboid review, explicitly not a game screenshot."""
from pathlib import Path
import json,zipfile,importlib.util
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-refresh-v1';A=R/'src/main/resources/assets'
spec=importlib.util.spec_from_file_location('render_forge',R/'docs/art/native16-rework-v11/qa/render_forge.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
vanilla=D/'qa-cache/assets';jar=Path.home()/'.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar'
with zipfile.ZipFile(jar) as z:
 for name in z.namelist():
  if name.startswith('assets/minecraft/textures/block/') and name.endswith('.png'):
   target=D/'qa-cache'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(name))
assets=mod.Assets([A,vanilla]);models=json.loads((D/'site-models.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/Monaco.ttf',10);views=[(0,.15,-1),(1,.65,-1),(1,.15,0),(0,.15,1),(0,1,0)]
for start in range(0,len(models),5):
 sheet=Image.new('RGB',(1176,5*174),'#777777');dr=ImageDraw.Draw(sheet)
 for j,row in enumerate(models[start:start+5]):
  dr.text((5,j*174),row['id']+' / offline resource render',font=font,fill='white')
  for k,eye in enumerate(views):
   pic=mod.render(assets,'dynasty:block/'+row['id'],eye,size=(168,148),scale=7);sheet.paste(pic,(k*168,j*174+22),pic)
  profile=mod.render(assets,'dynasty:block/'+row['id'],views[1],size=(168,148),scale=7)
  black=Image.new('RGBA',profile.size,(0,0,0,0));black.paste((0,0,0),mask=profile.getchannel('A'));sheet.paste(black,(840,j*174+22),black)
  from PIL import ImageOps
  gray=ImageOps.grayscale(profile).convert('RGBA');gray.putalpha(profile.getchannel('A'));sheet.paste(gray,(1008,j*174+22),gray)
 sheet.save(D/f'sites-{start//5+1}.png')
print('Rendered 15 sites: front,45,side,back,top 45 silhouette and gray material view; not in-game acceptance')

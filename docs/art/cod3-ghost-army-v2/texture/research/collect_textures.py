from pathlib import Path
import json,hashlib,zipfile,io
from PIL import Image,ImageDraw
R=Path.cwd();B=R/'docs/art/cod3-ghost-army-v2';D=B/'texture/research';F=D/'source-textures';F.mkdir(exist_ok=True)
prior=json.loads((B/'references/prior-manifests.json').read_text());ex=set(prior['hashes'])|{r['sha256'] for r in json.loads((B/'references/selected-100.json').read_text())}
jar=next(Path('/Users/a15356015027/Public/.minecraft/versions').glob('*/mods/epic-knights-1.20.1-forge-10.11.jar'));rows=[];seen=set()
with zipfile.ZipFile(jar) as z:
 names=[n for n in z.namelist() if '/textures/models/armor/' in n and n.endswith('.png') and 'layer' in n and not any(s in Path(n).name for s in ['overlay','crown','gold_','winged','ceremonialarmet'])]
 for n in names:
  raw=z.read(n);hv=hashlib.sha256(raw).hexdigest()
  if hv in ex|seen:continue
  p=F/Path(n).name;p.write_bytes(raw);im=Image.open(io.BytesIO(raw)).convert('RGBA');rows.append({'kind':'actual armor atlas','project':'Epic Knights','page':'https://modrinth.com/mod/epic-knights-shields-armor-and-weapons','jar':str(jar),'entry':n,'file':str(p.relative_to(D)),'sha256':hv,'decodedRgbaSha256':hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest(),'size':list(im.size)});seen.add(hv)
  if len(rows)==42:break
assert len(rows)==42
jar=Path('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar')
with zipfile.ZipFile(jar) as z:
 for name in ['terracotta','light_gray_terracotta','gray_terracotta','brown_terracotta','stone','andesite','smooth_stone','clay']:
  n=f'assets/minecraft/textures/block/{name}.png';raw=z.read(n);hv=hashlib.sha256(raw).hexdigest();assert hv not in ex|seen;seen.add(hv);p=F/(name+'.png');p.write_bytes(raw);im=Image.open(io.BytesIO(raw)).convert('RGBA');rows.append({'kind':'actual clay/stone surface texture','project':'Minecraft Java1.20.1','jar':str(jar),'entry':n,'file':str(p.relative_to(D)),'sha256':hv,'decodedRgbaSha256':hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest(),'size':list(im.size)})
(D/'texture-candidates.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
for start in range(0,50,10):
 canvas=Image.new('RGB',(1440,1080),'#444b50');d=ImageDraw.Draw(canvas)
 for i,row in enumerate(rows[start:start+10]):
  im=Image.open(D/row['file']).convert('RGBA');factor=max(1,min(600//im.width,160//im.height));im=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST);x=i%2*720;y=i//2*215;canvas.paste(im,(x+10,y+10),im);d.text((x+10,y+180),f"T{start+i+1:02} {Path(row['entry']).name}",fill='white')
 canvas.save(D/f'texture-sheet-{start//10+1:02}.png')
print('50 genuine source textures prepared, all SHA unique outside prior/model references; not yet marked viewed')

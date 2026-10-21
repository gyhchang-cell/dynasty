from pathlib import Path
from PIL import Image
import zipfile,json,io
R=Path(__file__).resolve().parents[3];out=[]
for p in (R/'src/main/resources/assets/dynasty/textures').glob('*/*.png'):
 if p.parent.name not in ('item','block'):continue
 with Image.open(p) as im:w,h=im.size
 if p.with_suffix('.png.mcmeta').exists():
  a=json.loads(p.with_suffix('.png.mcmeta').read_text()).get('animation',{});w=a.get('width',w);h=a.get('height',min(w,h))
 out.append((f'dynasty:{p.parent.name}/{p.stem}',w,h))
z=zipfile.ZipFile('/Users/a15356015027/.gradle/caches/forge_gradle/minecraft_repo/versions/1.20.1/client.jar')
for name in z.namelist():
 if not name.endswith('.png') or not name.startswith(('assets/minecraft/textures/item/','assets/minecraft/textures/block/')):continue
 with Image.open(io.BytesIO(z.read(name))) as im:w,h=im.size
 if name+'.mcmeta' in z.namelist():
  a=json.loads(z.read(name+'.mcmeta')).get('animation',{});w=a.get('width',w);h=a.get('height',min(w,h))
 out.append(('minecraft:'+name.split('/textures/')[1][:-4],w,h))
(R/'docs/art/inventory-originals-v3/atlas-sizes.tsv').write_text('\n'.join('\t'.join(map(str,r)) for r in out))
print(len(out),'atlas entries')

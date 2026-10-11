#!/usr/bin/env python3
"""Archive native evidence, prove runtime/resource parity, and delete only verified secret-12 rows."""
import argparse,gzip,hashlib,json,re,shutil,zipfile
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'docs/art/cod3-white-deer-v1';B=ROOT/'build/cod3-white-deer-20261011'
p=argparse.ArgumentParser();p.add_argument('--run',default='deer-v9');p.add_argument('--frozen',default='white-deer-v9');p.add_argument('--clean-prompts',action='store_true');args=p.parse_args()
O=B/'results'/args.run;F=ROOT/'build/blueprint-client/frozen'/args.frozen
assert (O/'PASS.txt').is_file() and not (O/'FAIL.txt').exists(),'Native acceptance must pass first'
checks=(O/'PASS.txt').read_text().splitlines();poses=json.loads((O/'poses.json').read_text());assert len(poses)==10
assert {v['state'] for v in poses}=={'idle','walk','graze','look_back','startled'}
for state in {v['state'] for v in poses}:
 rows=[v for v in poses if v['state']==state];assert len(rows)==2 and rows[-1]['poseDelta']>1e-5
 assert all(abs(v['herbDistance']-(25.25**.5)/16)<.001 for v in rows)
manifest=json.loads((F/'runtime-manifest.json').read_text())
resource_paths=['assets/dynasty/geo/cod3/white_deer.geo.json','assets/dynasty/animations/cod3/white_deer.animation.json','assets/dynasty/textures/entity/cod3/white_deer.png','assets/dynasty/textures/item/white_deer_token.png','assets/dynasty/models/item/white_deer_token.json','assets/dynasty/models/item/white_deer_spawn_egg.json','data/dynasty/dimension/white_deer_grotto.json','data/dynasty/dimension_type/white_deer_grotto.json','data/dynasty/forge/biome_modifier/white_deer.json','data/dynasty/loot_tables/entities/white_deer.json']
def digest(v):return hashlib.sha256(v).hexdigest()
def frozen(path):
 found=[Path(tree['runtime'])/path for tree in manifest['trees'] if (Path(tree['runtime'])/path).is_file()];assert len(found)==1,path;return found[0]
jar=B/'compiled/libs/dynasty-1.4.0.jar';report=[]
with zipfile.ZipFile(jar) as z:
 assert not any('WhiteDeerQa' in name for name in z.namelist()),'QA must not ship'
 for path in resource_paths:
  raw=(ROOT/'src/main/resources'/path).read_bytes();assert raw==frozen(path).read_bytes()==z.read(path),path;report.append({'path':path,'sha256':digest(raw)})
 for tree in manifest['trees']:
  if not tree['source'].endswith('/classes/java/main'):continue
  for entry in tree['entries']:
   path=entry['path'];name=Path(path).name
   if name.startswith(('WhiteDeerContent','WhiteDeerEntity','WhiteDeerTrail','WhiteDeerSanctuary','WhiteDeerRenderer')) and name.endswith('.class'):
    assert (B/'compiled/classes/java/main'/path).read_bytes()==(Path(tree['runtime'])/path).read_bytes(),path;assert path in z.namelist()
 for lang in ['zh_cn','en_us']:
  path=f'assets/dynasty/lang/{lang}.json';a=json.loads((ROOT/'src/main/resources'/path).read_text());b=json.loads(frozen(path).read_text());c=json.loads(z.read(path))
  keys=[k for k in a if '.deer.' in k or 'white_deer' in k];assert len(keys)==9
  assert {k:a[k] for k in keys}=={k:b[k] for k in keys}=={k:c[k] for k in keys}
N=D/'native';N.mkdir(parents=True,exist_ok=True)
frames=sorted(O.glob('*.png'));assert len(frames)>=17
for source in frames:shutil.copy2(source,N/source.name)
shutil.copy2(O/'PASS.txt',N/'checks.txt');shutil.copy2(O/'poses.json',N/'poses.json')
with gzip.open(N/'client.log.gz','wb') as out:out.write((O/'client.log').read_bytes())
# Native framebuffer views must include the whole model, and black means actual zero-RGB pixels.
names=['deer-180','deer-135','deer-90','deer-0','deer-silhouette'];contact=Image.new('RGB',(1500,340),'white');draw=ImageDraw.Draw(contact)
for i,name in enumerate(names):
 im=Image.open(N/(name+'.png')).convert('RGB');bg=im.getpixel((0,0));mask=ImageChops.difference(im,Image.new('RGB',im.size,bg));bounds=mask.getbbox();assert bounds and min(bounds[:2])>=12 and bounds[2]<=im.width-12 and bounds[3]<=im.height-12,(name,bounds)
 if 'silhouette' in name:
  assert set(im.getdata())=={bg,(0,0,0)},'Silhouette must be pure black'
 contact.paste(im.resize((300,300),Image.Resampling.NEAREST),(i*300,32));draw.text((i*300+8,8),name,fill='black')
contact.save(D/'overview.png')
tex=Image.new('RGB',(640,360),'white');draw=ImageDraw.Draw(tex)
for i,rel in enumerate(['assets/dynasty/textures/entity/cod3/white_deer.png','assets/dynasty/textures/item/white_deer_token.png']):
 im=Image.open(ROOT/'src/main/resources'/rel).convert('RGB');tex.paste(im.resize((256,256),Image.Resampling.NEAREST),(i*320+32,40));draw.text((i*320+32,16),Path(rel).name,fill='black')
tex.save(D/'textures-review.png')
world=B/'client'/args.run/'saves/cod3-white-deer';garden=world/'dimensions/dynasty/white_deer_grotto/data/dynasty_white_deer_garden.dat';assert garden.exists() and b'\x01\x00\x05Built\x01' in gzip.decompress(garden.read_bytes())
players=list((world/'playerdata').glob('*.dat'));assert any(White in gzip.decompress(p.read_bytes()) for p in players for White in [b'minecraft:overworld:secret_12']), 'Actual player receipt must reach disk'
shutil.copy2(garden,N/'garden.dat');shutil.copy2(jar,B/'dynasty-1.4.0-cod3-white-deer.jar')
verification={'run':args.run,'frozen':args.frozen,'independentChecks':len(set(checks)),'nativeFrames':len(frames),'states':len(set(v['state'] for v in poses)),'poseSamples':len(poses),'resourceParity':report,'jarSha256':digest(jar.read_bytes()),'qaInJar':False,'actualSavedGarden':True,'actualSavedPlayerReceipt':True,'limitations':['Five-minute threshold uses accelerated disposable server time; AI and animation samples run at real server time.','One integrated client with server FakePlayers; no second network peer and no full process restart.','Earlier failed diagnostic launches are retained under build; only this run supplies acceptance.']}
(D/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
if args.clean_prompts:
 source=Path('/Users/a15356015027/Desktop/code x提示词/cod3.txt');mirror=ROOT/'docs/cod3/remaining-tasks.txt';before=source.read_bytes();assert before==mirror.read_bytes()
 lines=before.decode().splitlines(keepends=True);expected=['| 12 | 衔草白鹿 | 白鹿口中灵芝 | 竹林晨雾 | 铃响 | 击杀/骑乘 | 静步跟随 5 分钟 | 玩家级 | 洞天福地 | 一次 |\n','| 12 | 主世界 | 竹林晨雾 | 静步跟白鹿 5min | 无 | 洞天福地 | player | 玩家级 | 无 |\n'];assert all(lines.count(s)==1 for s in expected)
 logpath=ROOT/'docs/cod3/deletions-20261010.json';log=json.loads(logpath.read_text());assert log['current_sha256']==digest(before)
 removed=[{'line_in_previous_version':i+1,'text':line} for i,line in enumerate(lines) if line in expected];after=''.join(line for line in lines if line not in expected).encode();assert len(removed)==2
 (B/'prompt-before-cleanup.txt').write_bytes(before)
 # Recheck both live inputs immediately before the small local deletion.
 assert source.read_bytes()==mirror.read_bytes()==before
 source.write_bytes(after);mirror.write_bytes(after);log['batches'].append({'tasks':['C3-SECRET-WHITE-DEER-12'],'evidence':str(D.relative_to(ROOT)/'verification.json'),'removed':removed});log['current_sha256']=digest(after);logpath.write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks':verification['independentChecks'],'nativeFrames':len(frames),'jarSha256':verification['jarSha256'],'removedRows':2 if args.clean_prompts else 0},ensure_ascii=False))

from pathlib import Path
import json,hashlib,collections
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;root=B/'sources/lucs789__forge-1.20.1-narrowzone/src/main/resources/assets/narrowzone';pngs=sorted((root/'textures/item').glob('repeating_crossbow*.png'));models=sorted((root/'models/item').glob('repeating_crossbow*.json'));stats=[]
def sheet(items,name):
 im=Image.new('RGB',(1280,((len(items)+3)//4)*290),(29,39,45));d=ImageDraw.Draw(im)
 for i,(title,img) in enumerate(items):
  x=i%4*320+18;y=i//4*290+45;d.text((x,y-30),title.replace('repeating_crossbow','rep'),fill='white');s=12;large=img.resize((img.width*s,img.height*s),Image.Resampling.NEAREST);im.paste(large,(x,y),large)
 im.save(B/name)
items=[]
for p in pngs:
 img=Image.open(p).convert('RGBA');stats.append(dict(path=str(p.relative_to(B)),size=list(img.size),alpha_histogram={str(k):v for k,v in collections.Counter(img.getchannel('A').get_flattened_data()).items()},sha256=hashlib.sha256(p.read_bytes()).hexdigest()));items.append((p.stem,img))
sheet(items,'actual-pngs-12x.png')
items=[];resolved=[]
for p in models:
 d=json.loads(p.read_text());layers={}
 # Single fixed custom parent; all referenced children inherit base transforms, not its overrides.
 if d.get('parent')=='narrowzone:item/repeating_crossbow':layers.update(json.loads((p.parent/'repeating_crossbow.json').read_text())['textures'])
 layers.update(d.get('textures',{}));out=Image.new('RGBA',(16,16));paths=[]
 for k,t in sorted(layers.items()):
  if not k.startswith('layer'):continue
  tex=root/'textures'/(t.split(':',1)[1]+'.png');assert tex.exists(),tex;img=Image.open(tex).convert('RGBA');assert img.size==(16,16);out=Image.alpha_composite(out,img);paths.append(str(tex.relative_to(B)))
 items.append((p.stem,out));resolved.append(dict(model=str(p.relative_to(B)),parent=d.get('parent'),actual_layers=paths))
sheet(items,'actual-model-layers-12x.png');(B/'texture-inspection.json').write_text(json.dumps(dict(kind='ACTUAL_PNG_AND_JSON_LAYER_INSPECTION_NOT_GAME',pngs=stats,models=resolved,source_pngs_modified=False,new_reference_credit=0,limitations=['纯PNG层叠，不是3D挤出/游戏截图/持物矩阵','pulling_3 PNG在当前重复弩JSON引用中未见，不当作运行帧']),ensure_ascii=False,indent=2)+'\n');print('PNGs',len(pngs),'JSON layer combinations',len(models))

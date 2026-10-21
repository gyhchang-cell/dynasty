"""Verify original pixel fidelity and compose labeled contact sheets (not screenshots)."""
from pathlib import Path
import json,hashlib,zipfile,math
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];D=R/'docs/art/inventory-originals-v4';A=R/'src/main/resources/assets/dynasty'
def check():
 if (Path(__file__).resolve().parents[3]/'docs/art/original-runtime-v7/published.json').exists():
  import runpy
  return runpy.run_path(str(Path(__file__).with_name('check_original_runtime.py')))['check']()

 m=json.loads((R/'docs/art/inventory-refresh-v1/generated-manifest.json').read_text());rows=sum(m.values(),[]);ids={r['id'] for r in rows};errors=[];details=[]
 with zipfile.ZipFile(R/'build/libs/dynasty-1.4.0.jar') as z:
  for r in rows:
   p=A/'textures/item'/f"{r['id']}.png";src=Image.open(R/r['source']).convert('RGBA');im=Image.open(p).convert('RGBA');bounds=src.getbbox();original=src.crop(bounds)
   if im.size!=(original.width+4,original.height+4) or im.crop((2,2,im.width-2,im.height-2)).tobytes()!=original.tobytes():errors.append(r['id']+': source pixels differ')
   model=A/'models/item'/f"{r['id']}.json"
   tiled_ids={x['id'] for x in json.loads((D/'tile-report.json').read_text())} if (D/'tile-report.json').exists() else set()
   if r['id'] not in tiled_ids and json.loads(model.read_text()).get('textures',{}).get('layer0')!='dynasty:item/'+r['id']:errors.append(r['id']+': model reference')
   for file in (p,model):
    if z.read('assets/dynasty/'+str(file.relative_to(A)))!=file.read_bytes():errors.append(r['id']+': jar mismatch')
   details.append({'id':r['id'],'sourceSize':list(src.size),'runtimeSize':list(im.size),'sourceBounds':bounds,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 protected=0
 for rel,sha in json.loads((D/'baseline.json').read_text()).items():
  if Path(rel).stem in ids:continue
  protected+=1
  if hashlib.sha256((R/rel).read_bytes()).hexdigest()!=sha:errors.append(rel+': nonselected changed')
 result={'count':len(rows),'protected':protected,'errors':errors,'sprites':details,'pixelPolicy':'Original RGBA pixels; only transparent external margins trimmed plus 2px border; no resampling or quantization','clientVisualTest':'NOT_RUN','atlasScope':'CPU Stitcher: Dynasty + vanilla item/block, excludes other mods; 16384 GPU capability still required'}
 (D/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('Original pixels/JAR/protected check:',len(rows),protected,'errors',errors);assert not errors
 if (D/'tile-report.json').exists():
  import runpy
  runpy.run_path(str(R/'tools/art/inventory-refresh/check_tiles.py'))['check']()
 return result

def gallery():
 m=json.loads((R/'docs/art/inventory-refresh-v1/generated-manifest.json').read_text());lang=json.loads((A/'lang/zh_cn.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20)
 for name,rows,cols in [('all',sum(m.values(),[]),6),('accessories',m['accessories'],5),('materials',m['materials'],6)]:
  cell=200;h=208;canvas=Image.new('RGB',(cols*cell,math.ceil(len(rows)/cols)*h+55),'#565c61');draw=ImageDraw.Draw(canvas)
  draw.text((12,10),'运行贴图原稿 · 缩略总览 · 非游戏截图',font=font,fill='white')
  for i,r in enumerate(rows):
   im=Image.open(A/'textures/item'/f"{r['id']}.png").convert('RGBA');im.thumbnail((174,166),Image.Resampling.NEAREST);x=(i%cols)*cell;y=55+(i//cols)*h;canvas.paste(im,(x+(cell-im.width)//2,y+(170-im.height)//2),im)
   label=lang.get('item.dynasty.'+r['id'],r['id']);draw.text((x+8,y+174),label,font=font,fill='white')
  canvas.save(D/f'{name}-overview.png')
if __name__=='__main__':check();gallery()

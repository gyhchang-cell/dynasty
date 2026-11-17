"""Read native reference pixels and preserve project artwork; diagnostic outputs only."""
from pathlib import Path
import json,hashlib,subprocess,sys
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;R=D.parents[2];sha=lambda b:hashlib.sha256(b).hexdigest()
def save(n,d):(D/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert not (D/'native-png-index.json').exists()
baseline=json.loads((R/'docs/art/armor-ars-reference-20261111/source-baseline.json').read_text())
priority=json.loads((R/'docs/art/armor-space-whole-20261112/current-dynasty-targets.json').read_text())['targets']
baseline.update({p:h for t in priority for p,h in t['files'].items()});assert all(sha((R/p).read_bytes())==h for p,h in baseline.items());save('protected-before.json',baseline)
subprocess.run([sys.executable,str(R/'tools/art/snapshot_texture_requirements.py'),'--batch-dir',str(D),'--targets',*[f'thermal:beekeeper_{s}' for s in ['helmet','chestplate','leggings','boots']],
 '--application','D77：完整养蜂服参考，四槽图标/穿戴图实图观察、专用头胸模型与继承UV来源核查，去重先前防化服/旧防护服族。不复制为原创、不新画、不改289保护和70优先、不启动Java或游戏、不改主清单。'],check=True)
A=D/'source/src/main/resources/assets/thermal'
icons=[A/'textures/item'/f'beekeeper_{s}.png' for s in ['helmet','chestplate','leggings','boots']]
worn=[A/'textures/models/armor'/f'beekeeper_layer_{i}.png' for i in [1,2]]
rows=[]
for p in icons+worn:
 im=Image.open(p).convert('RGBA');rows.append({'path':str(p.relative_to(D)),'size':im.size,'sha256':sha(p.read_bytes()),'rgba_sha256':sha(im.tobytes()),'alpha_bbox':im.getchannel('A').getbbox(),'visible_colors':len({v for v in im.get_flattened_data() if v[3]>0})})
save('native-png-index.json',rows)
def sheet(paths,cols,cell,title):
 out=Image.new('RGB',(cols*cell[0],40+((len(paths)+cols-1)//cols)*cell[1]),'#555b60');dr=ImageDraw.Draw(out);dr.text((8,8),title,fill='white')
 for j,p in enumerate(paths):
  im=Image.open(p).convert('RGBA');scale=min((cell[0]-12)//im.width,(cell[1]-35)//im.height);im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);x=j%cols*cell[0];y=40+j//cols*cell[1];out.paste(im,(x+(cell[0]-im.width)//2,y),im);dr.text((x+8,y+cell[1]-25),p.stem,fill='white')
 return out
sheet(icons,4,(200,210),'NATIVE FOUR SLOT ICONS / integer enlargement / NOT GAME').save(D/'native-icons.png')
sheet(worn,2,(600,330),'NATIVE WORN ATLASES / integer enlargement / NOT GAME').save(D/'native-atlases.png')
models=[]
for s in ['helmet','chestplate','leggings','boots']:
 p=D/'source/src/main/generated/assets/thermal/models/item'/f'beekeeper_{s}.json';m=json.loads(p.read_text());assert m['textures']['layer0']==f'thermal:item/beekeeper_{s}'
 models.append({'id':f'thermal:beekeeper_{s}','model':str(p.relative_to(D)),'declaration':m,'expected_base_worn':f'thermal:textures/models/armor/beekeeper_layer_{2 if s=="leggings" else 1}.png',
 'geometry':'ArmorFullSuitModel' if s in ['helmet','chestplate'] else 'default supplied armor model','full_runtime_consumer_closed':False})
save('static-bindings.json',models)
ctx=R/'docs/art/armor-mortem-whole-20261112/raw-standard-uv.json';parts={}
for row in json.loads(ctx.read_text())['rows']:
 for part in row['parts']:parts.setdefault(part['part'],part['rectangles'])
out=Image.new('RGB',(1000,1040),'#555b60');dr=ImageDraw.Draw(out);dr.text((8,8),'RAW UV RECTANGLES / inherited context only / NOT GAME OR EXACT POSE',fill='white');measure=[]
for j,(p,part) in enumerate((p,part) for p in worn for part in parts):
 im=Image.open(p).convert('RGBA');dr.text((8,40+j*100),p.stem+' / '+part,fill='white')
 for k,rect in enumerate(parts[part]):
  crop=im.crop(rect);measure.append({'texture':p.name,'part':part,'bounds':rect,'nonzero_alpha':sum(v>0 for v in crop.getchannel('A').get_flattened_data())});crop=crop.resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST);out.paste(crop,(300+k*110,40+j*100),crop);dr.text((300+k*110,104+j*100),str(rect),fill='white')
out.save(D/'raw-uv-context.png');save('raw-uv-context.json',{'rectangles_source':str(ctx),'sha256':sha(ctx.read_bytes()),'measurements':measure,'head_hat_custom_deformation':'outer.extend(0.5), arms outer.extend(-0.5); exact outer constant/dependency binary not verified','exact_1_20_4_modelpart_faces_read':False,'no_static_crown_missing_claim_from_UP_label':True})
prior=json.loads((R/'docs/art/armor-hazmat-whole-20261114/combined-semantic-ledger.json').read_text());group=next(g for g in prior['groups'] if g['semantic_group']=='hazmat_yellow_dark_suit')
save('dedup-input.json',{'prior_group':group,'new_candidate':'thermal:beekeeper','already_named': 'thermal:beekeeper' in prior['case_to_group'],'relation':'Closed fabric work suit; compare veil, fasteners and material regions against previously studied hazmat/protective suits before independent credit','new_credit':0})
print('Prepared6 native PNG,4 model refs,60 raw rectangles and3 visual pages')

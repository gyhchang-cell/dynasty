from pathlib import Path
import json,hashlib,zipfile,subprocess,shutil
from PIL import Image,ImageDraw
r=Path.cwd();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();idx=r/'docs/art/armor-imperial-v24/research/index.json';index=json.load(open(idx))
def collect(batch,ns,key,classes,wearpred):
 b=r/f'docs/art/armor-{key.replace("_","-")}-whole-20261114';b.mkdir(exist_ok=False)
 prior=r/'docs/art/armor-troll-hide-whole-20261114'
 for k in ['protected','priority']:
  a=json.load(open(prior/f'{k}-after.json'));assert all(H(r/p)==v for p,v in a.items());(b/f'{k}-before.json').write_text(json.dumps(a,indent=2)+'\n')
 for f,n in [(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),'requirements-global.md'),(r/'docs/art/USER_TEXTURE_REQUIREMENTS.md','requirements-project.md')]:shutil.copyfile(f,b/n)
 rows=[e for e in index if f'/{ns}/' in e['entry'] and key+'_' in Path(e['entry']).name and any('_'+s+'.png' in e['entry'] for s in ['helmet','chestplate','leggings','boots'])]
 anchor=r/'docs/art'/('armor-ironwood-whole-20261114' if ns=='twilightforest' else 'armor-wooden-whole-20261114')/'provenance.json';fixed=json.load(open(anchor));jar=Path(fixed['archive']);assert H(jar)==fixed['archive_sha256'];rows=[e for e in rows if e['jar']==str(jar)];z=zipfile.ZipFile(jar);entries=[]
 for n in z.namelist():
  name=Path(n).name
  if n in [f'assets/{ns}/textures/item/{key}_{s}.png' for s in ['helmet','chestplate','leggings','boots']] or n in [f'assets/{ns}/models/item/{key}_{s}.json' for s in ['helmet','chestplate','leggings','boots']] or (n.startswith(f'data/{ns}/recipes/') and name in [f'{key}_{s}.json' for s in ['helmet','chestplate','leggings','boots']]) or wearpred(n) or n in classes or n in ['META-INF/mods.toml','META-INF/MANIFEST.MF']:entries.append(n)
 prov=[]
 for n in entries:
  f=b/'source'/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(n));e={'entry':n,'local':str(f.relative_to(b)),'sha256':H(f)}
  if n.endswith('.class'):
   o=b/'decode'/(n.replace('/','__')+'.json');o.parent.mkdir(exist_ok=True);o.write_bytes(subprocess.check_output(['python3','/tmp/dynasty-class-read-bootstrap.py',str(f)]));e.update(python_decode=str(o.relative_to(b)),decode_sha256=H(o))
  prov.append(e)
 for e in rows:assert hashlib.sha256(z.read(e['entry'])).hexdigest()==e['sha256']
 (b/'provenance.json').write_text(json.dumps({'batch':batch,'case':ns+':'+key,'archive':str(jar),'archive_sha256':H(jar),'entries':prov,'old_index':str(idx),'old_index_sha256':H(idx),'old_index_icon_rows':rows,'java_starts':0,'game_starts':0,'network':False},ensure_ascii=False,indent=2)+'\n')
 shutil.copyfile('/tmp/dynasty-class-read-bootstrap.py',b/'read-class-python.py')
 imgs=[e for e in prov if e['entry'].endswith('.png')];page=Image.new('RGB',(1200,((len(imgs)+3)//4)*280+40),(78,84,88));d=ImageDraw.Draw(page);d.text((10,8),batch+' OTHER AUTHOR '+ns+':'+key+' / NATIVE NN / NOT DYNASTY OR GAME',fill='white');views=[]
 for i,e in enumerate(imgs):
  f=b/e['local'];im=Image.open(f).convert('RGBA');sc=min(8,240//max(im.size));sc=max(sc,1);u=im.resize((im.width*sc,im.height*sc),Image.Resampling.NEAREST);xy=(12+(i%4)*300,40+(i//4)*280);page.paste(u,xy,u);d.text((xy[0],xy[1]+u.height+6),Path(e['entry']).name,fill='white');views.append({'source':e['local'],'size':im.size,'scale':sc,'sha256':H(f)})
 page.save(b/'source-study.png');(b/'native-image-inventory.json').write_text(json.dumps(views,indent=2)+'\n');print(batch,b,len(entries),len(imgs))
 return b
if __name__=='__main__':
 import sys
 if sys.argv[1]=='101':collect('D101','immersive_armors','wooden',[f'immersive_armors/{n}.class' for n in ['Items','ItemsClient','item/ExtendedArmorItem','item/ExtendedArmorMaterial','mixin/MixinArmorFeatureRenderer','client/render/entity/piece/Piece','client/render/entity/piece/ModelPiece','client/render/entity/piece/LayerPiece','client/render/entity/piece/UpperBodyLayerPiece','client/render/entity/piece/MiddleBodyLayerPiece','client/render/entity/piece/UpperLeggingsLayerPiece','client/render/entity/piece/MiddleLeggingsLayerPiece','client/render/entity/model/ShoulderModel']],lambda n:n.endswith('.png') and ('textures/models/armor/wooden/' in n or 'textures/models/armor/wooden_layer_' in n))
 if sys.argv[1]=='102':collect('D102','twilightforest','ironwood',[f'twilightforest/{n}.class' for n in ['init/TFItems','item/IronwoodArmorItem','enums/TwilightArmorMaterial']],lambda n:n in ['assets/twilightforest/textures/armor/ironwood_1.png','assets/twilightforest/textures/armor/ironwood_2.png'])
 if sys.argv[1]=='103':collect('D103','divinerpg','seng_fur',[f'divinerpg/{n}.class' for n in ['registries/ItemRegistry','items/base/ItemDivineArmor','enums/ArmorStats','enums/ArmorStats$1']],lambda n:n.startswith('assets/divinerpg/textures/models/armor/seng_fur') and n.endswith('.png'))

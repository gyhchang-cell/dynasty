from pathlib import Path
import json,hashlib,zipfile,subprocess,shutil
from PIL import Image,ImageDraw
r=Path.cwd();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();lp=r/'docs/art/armor-aquamirae-three-bolt-whole-20261114/combined-semantic-ledger.json';ledger=json.loads(lp.read_text());idx=r/'docs/art/armor-imperial-v24/research/index.json';rows=json.loads(idx.read_text());jar=Path(next(x['jar'] for x in rows if '/aether/' in x['entry']));jarsha=H(jar)
with zipfile.ZipFile(jar) as z:
 names=z.namelist()
 for key,num in [('gravitite',122),('obsidian',123),('zanite',124)]:
  case='aether:'+key;assert case not in ledger['case_scope_followups'];assert not any(case in x for x in ledger['reviewed_pending_whole_keys']);group=ledger['case_to_group'][case]
  b=r/'docs/art'/('armor-'+key+'-whole-20261114');assert not b.exists()
  classes=['com/aetherteam/aether/item/AetherItems.class','com/aetherteam/aether/item/combat/AetherArmorItem.class','com/aetherteam/aether/item/combat/AetherArmorMaterials.class']
  ability='com/aetherteam/aether/item/combat/abilities/armor/'+key.title()+'Armor.class'
  if ability in names:classes.append(ability)
  assert all(n in names for n in classes)
  requested=classes+['META-INF/mods.toml','META-INF/MANIFEST.MF']
  requested += [n for n in names if (n.startswith('assets/aether/textures/item/armor/'+key+'_') or n.startswith('assets/aether/models/item/'+key+'_') or n.startswith('assets/aether/textures/models/armor/'+key+'_')) and n.endswith(('.json','.png','.mcmeta')) and not any(x in n for x in ['gloves','cape'])]
  requested += [n for n in names if n.startswith('data/aether/') and n.endswith('.json') and any(x in n for x in ['loot_tables','recipes']) and key in n and any(s in n for s in ['helmet','chestplate','leggings','boots'])]
  assert len([n for n in requested if '/textures/item/armor/' in n and n.endswith('.png')])==4
  for e in rows:
   if e['jar']==str(jar) and e['entry'] in requested:assert hashlib.sha256(z.read(e['entry'])).hexdigest()==e['sha256']
  b.mkdir(exist_ok=False);entries=[]
  for n in sorted(set(requested)):
   assert n in names,n;f=b/'source'/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(n));e={'entry':n,'local':str(f.relative_to(b)),'sha256':H(f)}
   if n.endswith('.class'):
    dec=b/'decode'/(n.replace('/','__')+'.json');dec.parent.mkdir(exist_ok=True);dec.write_bytes(subprocess.check_output(['python3','/tmp/dynasty-class-read-bootstrap.py',str(f)]));e.update(python_decode=str(dec.relative_to(b)),decode_sha256=H(dec))
   entries.append(e)
  put=lambda n,x:(b/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
  put('provenance.json',{'batch':'D'+str(num),'case':case,'archive':str(jar),'archive_sha256':jarsha,'entries':entries,'old_index':str(idx),'old_index_sha256':H(idx),'scope':'base/default native resources only, optional classic packs and accessory gloves/cape not this armor design','java_starts':0,'game_starts':0})
  put('precollection-dedup.json',{'case':case,'family':group,'near_family_aliases':[k for k,v in ledger['case_to_group'].items() if v==group],'prior_ledger':str(lp),'prior_sha256':H(lp),'existing_family_whole_followups':{k:v for k,v in ledger['case_scope_followups'].items() if ledger['case_to_group'].get(k)==group},'new_validated_credit':0,'not_independent_units':['four equipment parts','two wear atlases','classic pack variants','accessory gloves']})
  for k in ['protected','priority']:
   p=r/'docs/art/armor-aquamirae-three-bolt-whole-20261114'/(k+'-after.json');a=json.loads(p.read_text());assert all(H(r/f)==h for f,h in a.items());shutil.copyfile(p,b/(k+'-before.json'))
  for p,n in [(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),'requirements-global.md'),(r/'docs/art/USER_TEXTURE_REQUIREMENTS.md','requirements-project.md')]:shutil.copyfile(p,b/n)
  shutil.copyfile('/tmp/dynasty-class-read-bootstrap.py',b/'read-class-python.py');shutil.copyfile('/tmp/armor-collect122.py',b/'exclusive-collection-script.py')
  imgs=[e for e in entries if e['entry'].endswith('.png')];page=Image.new('RGB',(1200,40+280*((len(imgs)+3)//4)),(78,84,88));d=ImageDraw.Draw(page);d.text((10,8),'D'+str(num)+' OTHER AUTHOR '+case+' / NATIVE NN / NOT DYNASTY OR GAME',fill='white');inv=[]
  for i,e in enumerate(imgs):
   im=Image.open(b/e['local']).convert('RGBA');s=max(1,min(8,240//max(im.size)));u=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);x=12+(i%4)*300;y=40+(i//4)*280;page.paste(u,(x,y),u);d.text((x,y+u.height+6),Path(e['entry']).name,fill='white');inv.append({'source':e['local'],'size':im.size,'scale':s,'sha256':e['sha256']})
  page.save(b/'source-study.png');put('native-image-inventory.json',inv);subprocess.run(['python3','/tmp/armor-raw-study-head.py',str(b)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True);print(num,len(entries),len(imgs))

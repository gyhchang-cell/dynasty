from pathlib import Path
import json,hashlib,zipfile,subprocess,shutil
from PIL import Image,ImageDraw
r=Path.cwd();H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();lp=r/'docs/art/armor-neptune-whole-20261114/combined-semantic-ledger.json';ledger=json.loads(lp.read_text());idx=r/'docs/art/armor-imperial-v24/research/index.json';rows=json.loads(idx.read_text());jar=Path(next(x['jar'] for x in rows if '/aquamirae/' in x['entry']));sha=H(jar)
with zipfile.ZipFile(jar) as z:
 for key,num,cl,parts in [('abyssal',119,'Abyssal',['heaume','brigantine','leggings','boots','tiara']),('terrible',120,'Terrible',['helmet','chestplate','leggings','boots']),('three_bolt',121,'ThreeBolt',['helmet','suit','leggings','boots'])]:
  case='aquamirae:'+key;assert case not in ledger['case_scope_followups'];assert not any(case in x for x in ledger['reviewed_pending_whole_keys']);group=ledger['case_to_group'][case];b=r/'docs/art'/('armor-aquamirae-'+key.replace('_','-')+'-whole-20261114');assert not b.exists();names=z.namelist()
  requested=[n for n in names if n.endswith('.class') and (n.startswith('com/obscuria/aquamirae/common/items/armor/'+cl+'ArmorItem') or (cl=='Abyssal' and n.startswith('com/obscuria/aquamirae/common/items/armor/AbyssalArmorExtraItem')) or n=='com/obscuria/aquamirae/client/models/armor/Model'+cl+'Armor.class' or n=='com/obscuria/aquamirae/registry/AquamiraeItems.class')]
  assert any(n.endswith('/Model'+cl+'Armor.class') for n in requested)
  requested += [n for n in names if any(n==f'assets/aquamirae/{kind}/{key}_{part}.{ext}' for part in parts for kind,ext in [('textures/item','png'),('textures/entity/armor','png'),('models/item','json')])]
  # three_bolt chest icon is suit, native worn texture name is chestplate.
  if key=='three_bolt':requested += ['assets/aquamirae/textures/entity/armor/three_bolt_chestplate.png']
  requested += ['META-INF/mods.toml','META-INF/MANIFEST.MF']
  ids=['aquamirae:'+key+'_'+p for p in parts]
  requested += [n for n in names if n.startswith('data/aquamirae/') and n.endswith('.json') and ('/recipes/' in n or '/loot_tables/' in n) and any(i.encode() in z.read(n) for i in ids)]
  requested=sorted(set(requested));assert all(n in names for n in requested)
  for e in rows:
   if e['jar']==str(jar) and e['entry'] in requested:assert hashlib.sha256(z.read(e['entry'])).hexdigest()==e['sha256']
  b.mkdir(exist_ok=False);es=[]
  for n in requested:
   f=b/'source'/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(n));e={'entry':n,'local':str(f.relative_to(b)),'sha256':H(f)}
   if n.endswith('.class'):
    d=b/'decode'/(n.replace('/','__')+'.json');d.parent.mkdir(exist_ok=True);d.write_bytes(subprocess.check_output(['python3','/tmp/dynasty-class-read-bootstrap.py',str(f)]));e.update(python_decode=str(d.relative_to(b)),decode_sha256=H(d))
   es.append(e)
  put=lambda n,x:(b/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n');put('provenance.json',{'batch':'D'+str(num),'case':case,'archive':str(jar),'archive_sha256':sha,'entries':es,'old_index':str(idx),'old_index_sha256':H(idx),'java_starts':0,'game_starts':0,'scope':'native armor slots; alternate abyssal tiara stays same family'})
  put('precollection-dedup.json',{'case':case,'family':group,'near_family_aliases':[k for k,v in ledger['case_to_group'].items() if v==group],'prior_ledger':str(lp),'prior_sha256':H(lp),'case_scope_absent':True,'new_validated_credit':0,'same_family_followups':{k:v for k,v in ledger['case_scope_followups'].items() if ledger['case_to_group'].get(k)==group}})
  for k in ['protected','priority']:
   p=r/'docs/art/armor-neptune-whole-20261114'/(k+'-after.json');a=json.loads(p.read_text());assert all(H(r/f)==h for f,h in a.items());shutil.copyfile(p,b/(k+'-before.json'))
  for p,n in [(Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md'),'requirements-global.md'),(r/'docs/art/USER_TEXTURE_REQUIREMENTS.md','requirements-project.md')]:shutil.copyfile(p,b/n)
  shutil.copyfile('/tmp/dynasty-class-read-bootstrap.py',b/'read-class-python.py');shutil.copyfile('/tmp/armor-collect119.py',b/'exclusive-collection-script.py')
  imgs=[e for e in es if e['entry'].endswith('.png')];pg=Image.new('RGB',(1200,40+300*((len(imgs)+3)//4)),(78,84,88));d=ImageDraw.Draw(pg);d.text((10,8),'D'+str(num)+' OTHER AUTHOR '+case+' / NATIVE NN / NOT DYNASTY OR GAME',fill='white');inv=[]
  for i,e in enumerate(imgs):
   im=Image.open(b/e['local']).convert('RGBA');s=max(1,min(8,240//max(im.size)));u=im.resize((im.width*s,im.height*s),Image.Resampling.NEAREST);x=12+(i%4)*300;y=40+(i//4)*300;pg.paste(u,(x,y),u);d.text((x,y+u.height+6),Path(e['entry']).name,fill='white');inv.append({'source':e['local'],'size':im.size,'scale':s,'sha256':e['sha256']})
  pg.save(b/'source-study.png');put('native-image-inventory.json',inv);subprocess.run(['python3','/tmp/armor-raw-study-head.py',str(b)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True);print(num,len(es),len(imgs))

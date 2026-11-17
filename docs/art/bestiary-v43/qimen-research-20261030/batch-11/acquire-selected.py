from pathlib import Path
import ast,json,re,zipfile,hashlib,subprocess,datetime,os
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((R/'batch-09/native-source-manifest.json').read_text())
fn=next(n for n in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'exact-patch-only','exec'),ns)
symbols={}
for line in Path(m['mapping_cache']).read_text().splitlines():
 if line.startswith('\t') and not line.startswith('\t\t'):
  v=line.split()
  if len(v)>1 and re.fullmatch(r'[mf]_\d+_',v[0]):symbols[v[0]]=v[-1]
archive=R/'batch-08/source-archives/neoforge-47.1.64-sources.zip';assert hashlib.sha1(archive.read_bytes()).hexdigest()=='940788030f83e1d56d8fbe49712643c469962488'
files=[];framework=[]
with zipfile.ZipFile(m['base_source_cache']) as base,zipfile.ZipFile(archive) as z:
 for path in ['net/minecraft/client/renderer/entity/TippableArrowRenderer.java','net/minecraft/client/renderer/entity/ArrowRenderer.java','net/minecraft/world/entity/projectile/Arrow.java','net/minecraft/world/item/ArrowItem.java']:
  raw=base.read(path);data=raw.decode();patch='patches/'+path+'.patch';hunks=[];pp=None
  if patch in z.namelist():
   pr=z.read(patch);p=B/'patches/neoforge-47.1.64'/patch;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(pr);pp=str(p.relative_to(B));data,hunks=ns['patch_exact'](data,pr.decode())
  else:data='\n'.join(data.splitlines())+'\n'
  syms={s:symbols[s] for s in set(re.findall(r'\b[mf]_\d+_\b',data)) if s in symbols};view=re.sub(r'\b[mf]_\d+_\b',lambda x:syms.get(x[0],x[0]),data)
  f=dict(id=Path(path).stem,version='neoforge-47.1.64',path=path,base_entry_sha256=hashlib.sha256(raw).hexdigest(),patch=pp,patch_hunks=hunks,symbols=syms,read_status='EXTRACTED_NOT_REVIEWED',reviewed_ranges=[],lines=len(view.splitlines()))
  for k,t in [('srg',data),('reading_view',view)]:
   p=B/'native/neoforge-47.1.64'/k/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);f[k]=str(p.relative_to(B));f[k+'_sha256']=hashlib.sha256(t.encode()).hexdigest()
  files.append(f)
 for path in ['net/minecraftforge/network/NetworkHooks.java','net/minecraftforge/network/PlayMessages.java','net/minecraftforge/entity/IEntityAdditionalSpawnData.java']:
  data=z.read(path);p=B/'framework/neoforge-47.1.64'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);framework.append(dict(id=Path(path).stem,archive_entry=path,local=str(p.relative_to(B)),sha256=hashlib.sha256(data).hexdigest(),lines=len(data.decode().splitlines()),reviewed_ranges=[],read_status='EXTRACTED_NOT_REVIEWED'))
tree=json.loads((R/'batch-06/baileyholl__Ars-Nouveau-fixed-tree.json').read_text());selected=[]
paths=['src/main/java/com/hollingsworth/arsnouveau/api/spell/ISpellCaster.java','src/main/java/com/hollingsworth/arsnouveau/api/spell/SpellCaster.java','src/main/java/com/hollingsworth/arsnouveau/api/spell/Spell.java','src/main/java/com/hollingsworth/arsnouveau/api/spell/SpellContext.java','src/main/java/com/hollingsworth/arsnouveau/setup/registry/ModEntities.java','src/main/resources/assets/ars_nouveau/textures/item/spell_crossbow.png']
commit='2c74064bc753600d9b6600f102f8163e2d6764dd'
for path in paths:
 e=next(v for v in tree['tree'] if v['path']==path);old=R/'batch-06/sources/baileyholl__Ars-Nouveau'/path;p=B/'sources/baileyholl__Ars-Nouveau'/path;url='https://raw.githubusercontent.com/baileyholl/Ars-Nouveau/'+commit+'/'+path
 if old.exists():p=old;data=p.read_bytes()
 elif p.exists():data=p.read_bytes()
 else:
  response=subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--location','--max-time','30',url],check=True,capture_output=True);data=response.stdout;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 digest=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert digest==e['sha'] and len(data)==e['size']
 selected.append(dict(id=Path(path).stem,path=path,repo='baileyholl/Ars-Nouveau',commit=commit,url=url,local=os.path.relpath(p,B),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=digest,lines=None if path.endswith('.png') else len(data.decode().splitlines()),reviewed_ranges=[],read_status='ACQUIRED_NOT_REVIEWED'))
report=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),base_source_cache=m['base_source_cache'],mapping_cache=m['mapping_cache'],mapping_sha256=m['mapping_sha256'],base_stage=m['base_stage'],source_archive='../batch-08/source-archives/neoforge-47.1.64-sources.zip',source_sha1='940788030f83e1d56d8fbe49712643c469962488',source_url='https://maven.neoforged.net/releases/net/neoforged/forge/1.20.1-47.1.64/forge-1.20.1-47.1.64-sources.jar',native=files,framework=framework,mod_sources=selected,new_reference_credit=0)
(B/'acquisition.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(B/'progress.json').write_text(json.dumps(dict(started_utc=report['created_utc'],deadline='2026-10-31T12:09:23+08:00',status='IN_PROGRESS_ARS_SPECIAL_ARROW_AND_RENDER',new_source_families=0,new_accepted_gate_credit=0,production_changes=False,java_game_started=False),ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(native=len(files),framework=len(framework),mod_sources=len(selected))))

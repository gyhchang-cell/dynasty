from pathlib import Path
import json,zipfile,hashlib,io,ast,shutil,os
R=Path(__file__).resolve().parents[3];O=R/'docs/art/axe-study-v12';B=O/'install-backup';A=R/'src/main/resources/assets/dynasty'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(B/'source-originals.zip') as z:
 originals={'assets/dynasty/'+n.split('assets/dynasty/')[1]:z.read(n) for n in z.namelist()}
patch={n:(R/'src/main/resources'/n).read_bytes() for n in originals}
node=next(n for n in ast.parse((Path(__file__).with_name('deploy.py')).read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='patch_zip')
records=[];cache={};exec(compile(ast.Module(body=[node],type_ignores=[]),'recover','exec'))
base=Path('/Users/a15356015027/Public/.minecraft')
paths=[R/'build/libs/dynasty-1.4.0.jar',R/'modpack/mods/dynasty-1.4.0.jar',R/'整合包实例/mods/dynasty-1.4.0.jar',base/'mods/dynasty-1.4.0.jar',Path('/Users/a15356015027/Desktop/导出/Dynasty模组/dynasty-1.4.0.jar')]
paths += [d/'mods/dynasty-1.4.0.jar' for d in (base/'versions').iterdir() if d.is_dir() and 'Dynasty' in d.name]
paths += [root/name for root in [R/'dist',Path('/Users/a15356015027/Desktop/导出/Dynasty整合包')] for name in ['dynasty-1.4.0.mrpack','dynasty-1.4.0-modrinth.mrpack','dynasty-modpack-1.4.0.zip']]
verified=[]
for p in paths:
 if not p.exists():continue
 outer=sha(p)
 if p.suffix=='.jar':
  with zipfile.ZipFile(p) as z:assert all(z.read(n)==v for n,v in patch.items()),p
 else:
  key='overrides/mods/dynasty-1.4.0.jar'
  with zipfile.ZipFile(p) as z:blob=z.read(key)
  with zipfile.ZipFile(io.BytesIO(blob)) as z:
   todo={n:v for n,v in patch.items() if z.read(n)!=v}
   for n in todo:assert z.read(n)==originals[n],('Concurrent weapon resource edit',str(p),n)
  if todo:
   temp=B/('recovery-'+hashlib.sha256(blob).hexdigest()+'.jar');temp.write_bytes(blob);patch_zip(temp,todo)
   assert sha(p)==outer
   patch_zip(p,{key:temp.read_bytes()})
  with zipfile.ZipFile(p) as z,zipfile.ZipFile(io.BytesIO(z.read(key))) as jar:assert all(jar.read(n)==v for n,v in patch.items()),p
 verified.append({'path':str(p),'sha256':sha(p),'verified_resource_entries':len(patch)})
 print('Verified',p,flush=True)
(O/'deployment.json').write_text(json.dumps({'existing_ids':[r[0] for r in json.loads((R/'docs/art/weapon-tier-v11/manifest.json').read_text())],'source_files':{n:hashlib.sha256(v).hexdigest() for n,v in patch.items()},'archives':verified,'recovery_operations':records,'note':'Concurrent export change caught before overwrite; reopened current archive, required old/new resource bytes, preserved its unrelated members. Original backups retained.','java_started':False,'game_tested':False,'github_pushed':False},ensure_ascii=False,indent=2))

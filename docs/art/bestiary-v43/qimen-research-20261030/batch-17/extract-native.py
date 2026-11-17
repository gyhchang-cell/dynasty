from pathlib import Path
import re,json,zipfile,hashlib,ast,datetime
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((R/'batch-09/native-source-manifest.json').read_text());symbols={}
for line in Path(m['mapping_cache']).read_text().splitlines():
 if line.startswith('\t') and not line.startswith('\t\t'):
  v=line.split()
  if len(v)>1 and re.fullmatch(r'[mf]_\d+_',v[0]):symbols[v[0]]=v[-1]
fn=next(x for x in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
rows=[]
with zipfile.ZipFile(m['base_source_cache']) as z,zipfile.ZipFile(B/'source-archives/forge-47.1.0-sources.zip') as f:
 for name in ['ItemOverride','ItemOverrides','ItemModelGenerator','BlockModel','ItemRenderer']:
  path=('net/minecraft/client/renderer/entity/' if name=='ItemRenderer' else 'net/minecraft/client/renderer/block/model/')+name+'.java';raw=z.read(path);patchpath='patches/'+path+'.patch';patch=f.read(patchpath).decode() if patchpath in f.namelist() else '';data,n=ns['patch_exact'](raw.decode(),patch) if patch else ('\n'.join(raw.decode().splitlines())+'\n',0)
  syms={s:symbols[s] for s in set(re.findall(r'\b[mf]_\d+_\b',data)) if s in symbols};view=re.sub(r'\b[mf]_\d+_\b',lambda x:syms.get(x[0],x[0]),data)
  row=dict(id=name,path=path,base_entry_sha256=hashlib.sha256(raw).hexdigest(),patch_hunks=n,symbols=syms,reviewed_ranges=[],lines=len(view.splitlines()),status='EXTRACTED_NOT_REVIEWED')
  for k,t in [('srg',data),('reading_view',view),('patch',patch)]:
   p=B/'native/forge-47.1.0'/k/(path+('.patch' if k=='patch' else ''));p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);row[k]=str(p.relative_to(B));row[k+'_sha256']=hashlib.sha256(t.encode()).hexdigest()
  rows.append(row)
(B/'native-consumers.json').write_text(json.dumps(dict(base_source_cache=m['base_source_cache'],mapping_cache=m['mapping_cache'],mapping_sha256=m['mapping_sha256'],forge_source_archive='source-archives/forge-47.1.0-sources.zip',forge_source_sha1='a1481dc60f93c78f257f8e755385897a3ca85bb1',version='Minecraft1.20.1+Forge47.1.0',files=rows,new_reference_credit=0),ensure_ascii=False,indent=2)+'\n');print([(x['id'],x['lines'],x['patch_hunks']) for x in rows])

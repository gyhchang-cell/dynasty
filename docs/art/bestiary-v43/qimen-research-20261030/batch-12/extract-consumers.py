from pathlib import Path
import ast,re,json,zipfile,hashlib
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((R/'batch-09/native-source-manifest.json').read_text());fn=next(n for n in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
sym={}
for line in Path(m['mapping_cache']).read_text().splitlines():
 if line.startswith('\t') and not line.startswith('\t\t'):
  v=line.split()
  if len(v)>1 and re.fullmatch(r'[mf]_\d+_',v[0]):sym[v[0]]=v[-1]
archive=R/'batch-08/source-archives/forge-47.3.0-sources.zip';assert hashlib.sha1(archive.read_bytes()).hexdigest()=='c5626b71a9e9c1f2f061ceeb2d8cb5cc961ee42a'
paths=['net/minecraft/client/renderer/ShaderInstance.java','com/mojang/blaze3d/shaders/BlendMode.java','com/mojang/blaze3d/vertex/BufferUploader.java','com/mojang/blaze3d/vertex/VertexBuffer.java','com/mojang/blaze3d/platform/GlStateManager.java','com/mojang/blaze3d/systems/RenderSystem.java','net/minecraft/client/renderer/LevelRenderer.java','net/minecraft/client/renderer/GameRenderer.java','net/minecraft/client/multiplayer/ClientLevel.java']
rows=[]
with zipfile.ZipFile(m['base_source_cache']) as base,zipfile.ZipFile(archive) as z:
 for path in paths:
  raw=base.read(path);data=raw.decode();pn='patches/'+path+'.patch';patch=None;hunks=[]
  if pn in z.namelist():
   pr=z.read(pn);p=B/'patches/forge-47.3.0'/pn;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(pr);patch=str(p.relative_to(B));data,hunks=ns['patch_exact'](data,pr.decode())
  else:data='\n'.join(data.splitlines())+'\n'
  syms={s:sym[s] for s in set(re.findall(r'\b[mf]_\d+_\b',data)) if s in sym};view=re.sub(r'\b[mf]_\d+_\b',lambda x:syms.get(x[0],x[0]),data);e=dict(id=Path(path).stem,path=path,version='forge-47.3.0',base_entry_sha256=hashlib.sha256(raw).hexdigest(),patch=patch,patch_hunks=hunks,symbols=syms,lines=len(view.splitlines()),reviewed_ranges=[],status='EXTRACTED_NOT_REVIEWED')
  for k,t in [('srg',data),('reading_view',view)]:
   p=B/'native/forge-47.3.0'/k/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);e[k]=str(p.relative_to(B));e[k+'_sha256']=hashlib.sha256(t.encode()).hexdigest()
  rows.append(e)
v=dict(base_source_cache=m['base_source_cache'],base_stage=m['base_stage'],mapping_cache=m['mapping_cache'],mapping_sha256=m['mapping_sha256'],source_archive='../batch-08/source-archives/forge-47.3.0-sources.zip',source_sha1='c5626b71a9e9c1f2f061ceeb2d8cb5cc961ee42a',source_url='https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.3.0/forge-1.20.1-47.3.0-sources.jar',files=rows,new_reference_credit=0)
(B/'native-consumers.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print([(e['id'],e['lines'],len(e['patch_hunks'])) for e in rows])

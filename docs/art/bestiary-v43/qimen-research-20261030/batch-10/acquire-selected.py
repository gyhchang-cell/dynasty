from pathlib import Path
import ast,json,re,zipfile,hashlib,subprocess,datetime
B=Path(__file__).resolve().parent;R=B.parent
manifest=json.loads((R/'batch-09/native-source-manifest.json').read_text())
fn=next(n for n in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='patch_exact')
ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'exact-patch-only','exec'),ns)
paths=['net/minecraft/network/syncher/SynchedEntityData.java','net/minecraft/network/protocol/game/ClientboundSetEntityDataPacket.java','net/minecraft/client/model/geom/ModelPart.java','net/minecraft/client/model/geom/builders/CubeDefinition.java','net/minecraft/client/model/geom/builders/LayerDefinition.java','net/minecraft/client/renderer/entity/EntityRenderDispatcher.java','net/minecraft/client/renderer/entity/EntityRenderer.java','com/mojang/blaze3d/vertex/PoseStack.java','net/minecraft/client/model/geom/builders/PartDefinition.java','net/minecraft/network/syncher/EntityDataSerializers.java','net/minecraft/client/multiplayer/ClientPacketListener.java','net/minecraft/client/renderer/RenderType.java','net/minecraft/client/renderer/RenderStateShard.java','com/mojang/blaze3d/vertex/VertexConsumer.java','net/minecraft/client/renderer/texture/AbstractTexture.java','net/minecraft/client/renderer/texture/SimpleTexture.java','net/minecraft/client/renderer/texture/TextureManager.java']
symbols={}
for line in Path(manifest['mapping_cache']).read_text().splitlines():
 if line.startswith('\t') and not line.startswith('\t\t'):
  v=line.split()
  if len(v)>=2 and re.fullmatch(r'[mf]_\d+_',v[0]): symbols[v[0]]=v[-1]
files=[]
with zipfile.ZipFile(manifest['base_source_cache']) as base,zipfile.ZipFile(R/'batch-08/source-archives/forge-47.3.0-sources.zip') as forge:
 for path in paths:
  raw=base.read(path);data=raw.decode();patch='patches/'+path+'.patch';hunks=[];localpatch=None
  if patch in forge.namelist():
   pr=forge.read(patch);pp=B/'patches/forge-47.3.0'/patch;pp.parent.mkdir(parents=True,exist_ok=True);pp.write_bytes(pr);localpatch=str(pp.relative_to(B));data,hunks=ns['patch_exact'](data,pr.decode())
  else:data='\n'.join(data.splitlines())+'\n'
  syms={s:symbols[s] for s in set(re.findall(r'\b[mf]_\d+_\b',data)) if s in symbols}
  view=re.sub(r'\b[mf]_\d+_\b',lambda x:syms.get(x[0],x[0]),data)
  f=dict(version='forge-47.3.0',path=path,base_entry_sha256=hashlib.sha256(raw).hexdigest(),patch=localpatch,patch_hunks=hunks,symbols=syms,reviewed_ranges=[],read_status='EXTRACTED_NOT_REVIEWED',lines=len(view.splitlines()))
  for k,t in [('srg',data),('reading_view',view)]:
   p=B/'native/forge-47.3.0'/k/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);f[k]=str(p.relative_to(B));f[k+'_sha256']=hashlib.sha256(t.encode()).hexdigest()
  files.append(f)
assets=[];tree=json.loads((R/'batch-06/dercodeKoenig__marvins-minecraft-mods-fixed-tree.json').read_text())
selected=['aw_vehicles/src/main/resources/assets/aw_vehicles/textures/entity/arrow_wood.png','aw_vehicles/src/main/resources/assets/aw_vehicles/textures/entity/ballista_stand_3.png','aw_vehicles/src/main/java/Vehicles/Main.java']
commit='20d02ec1300ff6011683d9fd43ef76fd47256234'
for path in selected:
 entry=next(f for f in tree['tree'] if f['path']==path)
 url='https://raw.githubusercontent.com/dercodeKoenig/marvins-minecraft-mods/'+commit+'/'+path
 cached=B/'reference-assets'/path
 if cached.exists():data=cached.read_bytes()
 else:
  response=subprocess.run(['/usr/bin/curl','--fail','--silent','--show-error','--location','--max-time','30',url],check=True,capture_output=True);data=response.stdout
 gitsha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert gitsha==entry['sha'] and len(data)==entry['size']
 p=B/'reference-assets'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 assets.append(dict(repo='dercodeKoenig/marvins-minecraft-mods',commit=commit,path=path,url=url,git_blob_sha1=gitsha,sha256=hashlib.sha256(data).hexdigest(),local=str(p.relative_to(B)),review_status='ACQUIRED_NOT_VIEWED_OR_READ',production_copy=False))
out=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),base_source_cache=manifest['base_source_cache'],base_stage=manifest['base_stage'],mapping_cache=manifest['mapping_cache'],mapping_sha256=manifest['mapping_sha256'],forge_source_archive='../batch-08/source-archives/forge-47.3.0-sources.zip',forge_source_sha1=manifest['forge_source_sha1'],files=files,assets=assets,new_reference_credit=0,method='Exact fixed Forge47.3.0 source patches and pinned Git blob verified assets; extraction/acquisition does not imply review. No Java/game execution.')
(B/'acquisition.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
(B/'progress.json').write_text(json.dumps(dict(started_utc=out['created_utc'],deadline='2026-10-31T12:09:23+08:00',status='IN_PROGRESS_EXISTING_BALLISTA_RENDER_SYNC',new_source_families=0,new_accepted_gate_credit=0,production_changes=False,java_game_started=False),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(native=len(files),assets=len(assets),patch_hunks=sum(len(f['patch_hunks']) for f in files))))

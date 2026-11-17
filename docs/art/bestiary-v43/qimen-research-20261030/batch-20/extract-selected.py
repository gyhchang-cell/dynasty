from pathlib import Path
import zipfile,json,hashlib
B=Path(__file__).resolve().parent;rows=[]
selected={'ToffysHooks.java','ToffysHooksClient.java','HookEntity.java','HookItem.java','HookClawItem.java','PlayerMixin.java','ModEntities.java','ModItems.java','PlayerWithHookData.java','HookRenderer.java','gradle.properties','build.gradle','fabric.mod.json','toffys_hooks.mixins.json'}
with zipfile.ZipFile(B/'source-archives/toffys-hooks-fixed.zip') as z:
 for n in z.namelist():
  if n.endswith('/'):continue
  p=n.split('/',1)[1]
  if Path(p).name not in selected and not ('/models/item/' in p and Path(p).name in ['grappling_hook.json','grappling_hook_extended.json','hook.json']) and not ('/textures/' in p and Path(p).name in ['hook_rope.png','grappling_hook.png','grappling_hook_extended.png','hook.png']):continue
  data=z.read(n);out=B/'sources/FloffyToffyToolBox__Toffys_Hooks'/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
  rows.append(dict(path=p,local=str(out.relative_to(B)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),read_ranges=[],status='EXTRACTED_NOT_REVIEWED'))
(B/'selected-source-manifest.json').write_text(json.dumps(dict(repo='FloffyToffyToolBox/Toffys_Hooks',commit='92b160f2a6e2fb80d0a440d5ff748b219940ad20',branch_observed='1.20.1-fabric',archive='source-archives/toffys-hooks-fixed.zip',archive_sha256=hashlib.sha256((B/'source-archives/toffys-hooks-fixed.zip').read_bytes()).hexdigest(),independent_tree_blob_comparison=False,files=rows,new_reference_credit=0),ensure_ascii=False,indent=2)+'\n')
for x in rows:
 if not x['path'].endswith('.png'):print(x['path'],len((B/x['local']).read_text().splitlines()))

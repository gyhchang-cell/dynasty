from pathlib import Path
import zipfile,json,hashlib
B=Path(__file__).resolve().parent;rows=[]
names={'gradle.properties','build.gradle','LICENSE','NarrowZone.java','RepeatingCrossbowItem.java','ModItems.java','ModItemProperties.java','ModClientEvents.java','ModClientGameplayEvents.java','ModGameplayEvents.java','UseStopHandler.java','ModRangedEnchantmentEffects.java','mods.toml'}
with zipfile.ZipFile(B/'narrowzone-fixed-source.zip') as z:
 for n in z.namelist():
  if n.endswith('/'):continue
  path=n.split('/',1)[1]
  if Path(path).name not in names and not ('repeating_crossbow' in path and path.endswith(('.json','.png'))):continue
  data=z.read(n);p=B/'sources/lucs789__forge-1.20.1-narrowzone'/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);row=dict(path=path,archive_entry=n,local=str(p.relative_to(B)),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),bytes=len(data),status='EXTRACTED_NOT_REVIEWED',new_reference_credit=0);rows.append(row)
(B/'selected-source-manifest.json').write_text(json.dumps(dict(archive='narrowzone-fixed-source.zip',archive_sha256=hashlib.sha256((B/'narrowzone-fixed-source.zip').read_bytes()).hexdigest(),files=rows,independent_tree_blob_comparison=False,new_reference_credit=0),ensure_ascii=False,indent=2)+'\n');print('extracted',len(rows))
for x in rows:
 if x['path'].endswith('.java') or Path(x['path']).name in ['gradle.properties','build.gradle','mods.toml']:print(x['path'],len((B/x['local']).read_bytes().decode('latin1').splitlines()))

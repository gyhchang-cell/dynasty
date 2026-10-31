from pathlib import Path
import re,json,zipfile,hashlib,ast
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((R/'batch-09/native-source-manifest.json').read_text());symbols={}
for line in Path(m['mapping_cache']).read_text().splitlines():
 if line.startswith('\t') and not line.startswith('\t\t'):
  v=line.split()
  if len(v)>1 and re.fullmatch(r'[mf]_\d+_',v[0]):symbols[v[0]]=v[-1]
fn=next(x for x in ast.parse((R/'batch-09/extract-selected-native.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='patch_exact');ns={'re':re};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'patch-only','exec'),ns)
paths=['world/item/CrossbowItem.java','world/entity/LivingEntity.java','client/Minecraft.java','client/multiplayer/MultiPlayerGameMode.java','client/player/LocalPlayer.java','server/network/ServerGamePacketListenerImpl.java','world/item/ItemStack.java','server/level/ServerPlayerGameMode.java','world/item/Item.java'];rows=[]
with zipfile.ZipFile(m['base_source_cache']) as z,zipfile.ZipFile(B/'source-archives/forge-47.4.9-sources.zip') as f:
 for path in paths:
  path='net/minecraft/'+path;raw=z.read(path);pn='patches/'+path+'.patch';patch=f.read(pn).decode() if pn in f.namelist() else '';data,n=ns['patch_exact'](raw.decode(),patch) if patch else ('\n'.join(raw.decode().splitlines())+'\n',0);syms={s:symbols[s] for s in set(re.findall(r'\b[mf]_\d+_\b',data)) if s in symbols};view=re.sub(r'\b[mf]_\d+_\b',lambda x:syms.get(x[0],x[0]),data);row=dict(id=Path(path).stem,path=path,base_entry_sha256=hashlib.sha256(raw).hexdigest(),patch_hunks=n,symbols=syms,reviewed_ranges=[],status='EXTRACTED_NOT_REVIEWED',lines=len(view.splitlines()))
  for k,t in [('srg',data),('reading_view',view),('patch',patch)]:
   p=B/'native/forge-47.4.9'/k/(path+('.patch' if k=='patch' else ''));p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);row[k]=str(p.relative_to(B));row[k+'_sha256']=hashlib.sha256(t.encode()).hexdigest()
  rows.append(row)
archive=B/'source-archives/forge-47.4.9-sources.zip';(B/'native-consumers.json').write_text(json.dumps(dict(version='Minecraft1.20.1+Forge47.4.9',base_source_cache=m['base_source_cache'],mapping_cache=m['mapping_cache'],mapping_sha256=m['mapping_sha256'],forge_source_archive=str(archive.relative_to(B)),forge_source_sha1=hashlib.sha1(archive.read_bytes()).hexdigest(),files=rows,new_reference_credit=0),ensure_ascii=False,indent=2)+'\n');print([(x['id'],x['lines'],len(x['patch_hunks']) if isinstance(x['patch_hunks'],list) else 0) for x in rows])

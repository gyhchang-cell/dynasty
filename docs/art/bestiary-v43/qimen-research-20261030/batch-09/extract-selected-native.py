from pathlib import Path
from datetime import datetime,timezone
import zipfile,json,hashlib,re
B=Path(__file__).resolve().parent;P=B.parent/'batch-08'
prior=json.loads((P/'native-reconstruction.json').read_text());cache=Path(prior['base_source_cache']);mapping=Path(prior['mapping_cache']);symbols={}
for l in mapping.read_text().splitlines():
 if l.startswith('\t') and not l.startswith('\t\t'):
  v=l.split()
  if len(v)>=2 and re.fullmatch(r'[mf]_\d+_',v[0]):
   assert v[0] not in symbols or symbols[v[0]]==v[-1];symbols[v[0]]=v[-1]
def patch_exact(data,patch):
 original=data.splitlines();lines=patch.splitlines();out=[];pos=0;hunks=[];i=0
 while i<len(lines):
  h=re.match(r'@@ -(\d+)(?:,(\d+))? \+([\d_]+)(?:,(\d+))? @@',lines[i])
  if not h:i+=1;continue
  oldstart,oldcount,newcount=int(h[1]),int(h[2] or 1),int(h[4] or 1);i+=1;old=[];new=[]
  while i<len(lines) and not lines[i].startswith('@@'):
   l=lines[i]
   if l.startswith(' '):old.append(l[1:]);new.append(l[1:])
   elif l.startswith('-'):old.append(l[1:])
   elif l.startswith('+'):new.append(l[1:])
   elif l.startswith('\\'):pass
   else:break
   i+=1
  assert len(old)==oldcount and len(new)==newcount
  at=oldstart-1
  if original[at:at+oldcount]!=old:
   found=[n for n in range(pos,len(original)-oldcount+1) if original[n:n+oldcount]==old];assert len(found)==1;(at,)=found
  assert at>=pos
  out+=original[pos:at]+new;pos=at+oldcount;hunks.append({'old_start':oldstart,'actual_start':at+1,'exact_context':True})
 assert len(hunks)==sum(l.startswith('@@ ') for l in lines)
 return '\n'.join(out+original[pos:])+'\n',hunks
forge=['net/minecraft/server/level/ServerChunkCache.java','net/minecraft/server/level/ServerEntity.java','net/minecraft/server/level/ChunkMap.java','net/minecraft/world/level/EntityGetter.java','net/minecraft/world/level/Level.java','net/minecraft/world/entity/Entity.java','net/minecraft/world/entity/EntityType.java','net/minecraft/world/level/chunk/storage/EntityStorage.java','net/minecraft/world/level/entity/EntityPersistentStorage.java','net/minecraft/world/level/entity/EntityLookup.java','net/minecraft/world/level/entity/EntitySectionStorage.java','net/minecraft/world/level/entity/EntitySection.java','net/minecraft/world/level/entity/LevelEntityGetterAdapter.java']
vanilla=['net/minecraft/server/level/ServerChunkCache.java','net/minecraft/server/level/ChunkMap.java','net/minecraft/client/multiplayer/ClientLevel.java','net/minecraft/world/level/entity/TransientEntitySectionManager.java','net/minecraft/world/damagesource/DamageSources.java','net/minecraft/server/level/ServerLevel.java','net/minecraft/world/level/entity/LevelEntityGetterAdapter.java','net/minecraft/world/level/entity/EntityLookup.java','net/minecraft/world/entity/Entity.java','net/minecraft/world/entity/EntityType.java','net/minecraft/world/entity/projectile/FireworkRocketEntity.java','net/minecraft/server/level/ServerEntity.java','net/minecraft/network/protocol/game/ClientboundAddEntityPacket.java','net/minecraft/client/multiplayer/ClientPacketListener.java']
fs=next(a for a in json.loads((P/'native-source-provenance.json').read_text())['artifacts'] if a['version']=='forge-47.3.0' and a['local'].endswith('-sources.zip'))
assert hashlib.sha1((P/fs['local']).read_bytes()).hexdigest()==fs['sha1']
result=[]
with zipfile.ZipFile(cache) as base,zipfile.ZipFile(P/fs['local']) as patches:
 for version,paths in [('forge-47.3.0',forge),('vanilla-mcp-1.20.1',vanilla)]:
  for path in paths:
   raw=base.read(path);data=raw.decode();patchname='patches/'+path+'.patch';patchpath=None;hunks=[]
   if version=='forge-47.3.0' and patchname in patches.namelist():
    pr=patches.read(patchname);out=B/'patches'/version/patchname;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(pr);patchpath=str(out.relative_to(B));data,hunks=patch_exact(data,pr.decode())
   else:data='\n'.join(data.splitlines())+'\n'
   syms={s:symbols[s] for s in set(re.findall(r'\b[mf]_\d+_\b',data)) if s in symbols};view=re.sub(r'\b[mf]_\d+_\b',lambda m:syms.get(m[0],m[0]),data)
   entry={'version':version,'path':path,'base_entry_sha256':hashlib.sha256(raw).hexdigest(),'patch':patchpath,'patch_hunks':hunks,'symbols':syms,'reviewed_ranges':[],'read_status':'EXTRACTED_NOT_REVIEWED','lines':len(view.splitlines())}
   for key,text in [('srg',data),('reading_view',view)]:
    target=B/'native'/version/key/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text);entry[key]=str(target.relative_to(B));entry[key+'_sha256']=hashlib.sha256(text.encode()).hexdigest()
   result.append(entry)
report={'created_utc':datetime.now(timezone.utc).isoformat(),'base_source_cache':str(cache),'base_stage':prior['base_stage'],'mcp_coordinate':prior['mcp_coordinate'],'mapping_cache':str(mapping),'mapping_sha256':hashlib.sha256(mapping.read_bytes()).hexdigest(),'forge_source_archive':'../batch-08/'+fs['local'],'forge_source_sha1':fs['sha1'],'source_artifact':fs['artifact'],'method':'新增选择类；既有MCP source基底＋准确47.3.0官方源码补丁，所有补丁全文精确匹配，不执行Java或代码生成。vanilla仅Fabric基线，不是实际Mixin合并运行时。','files':result,'new_reference_credit':0}
(B/'native-source-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'selected_classes':len(result),'exact_patch_hunks':sum(len(f['patch_hunks']) for f in result),'not_read_automatically':True}))

from pathlib import Path
from datetime import datetime,timezone
import subprocess,json,zipfile,hashlib,concurrent.futures
B=Path(__file__).resolve().parent
versions={
 'forge-47.3.0':'https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.3.0/forge-1.20.1-47.3.0',
 'neoforge-47.1.64':'https://maven.neoforged.net/releases/net/neoforged/forge/1.20.1-47.1.64/forge-1.20.1-47.1.64'}
selected=['net/minecraft/nbt/CompoundTag.java','net/minecraft/world/entity/projectile/ProjectileUtil.java','net/minecraft/world/entity/projectile/AbstractArrow.java','net/minecraft/world/item/ArrowItem.java','net/minecraft/world/item/CrossbowItem.java','net/minecraft/world/item/ItemStack.java','net/minecraft/world/entity/LivingEntity.java','net/minecraft/server/level/ServerLevel.java','net/minecraft/world/level/entity/PersistentEntitySectionManager.java','net/minecraft/world/damagesource/DamageSource.java']

def fetch(job):
 key,base,kind=job;url=base+'-'+kind+'.jar';out=B/'source-archives'/f'{key}-{kind}.zip';out.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run(['curl','-fLsS','--retry','1','--max-time','45',url,'-o',str(out)],check=True)
 expected=subprocess.check_output(['curl','-fLsS','--max-time','25',url+'.sha1']).decode().strip().split()[0];sha=hashlib.sha1(out.read_bytes()).hexdigest();assert sha==expected,(url,sha,expected)
 row=dict(version=key,artifact=url,sha1=sha,local=str(out.relative_to(B)),executed=False,selected=[])
 with zipfile.ZipFile(out) as z:
  if kind=='userdev':
   data=z.read('config.json');p=B/f'{key}-userdev-config.json';p.write_bytes(data);row['mcp']=json.loads(data)['mcp'];row['config']=p.name
  else:
   names=set(z.namelist())
   for path in selected:
    patch='patches/'+path+'.patch'
    if patch in names:
     data=z.read(patch);p=B/(key+'-patches')/patch;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);row['selected'].append(dict(path=patch,local=str(p.relative_to(B)),sha256=hashlib.sha256(data).hexdigest(),lines=len(data.decode().splitlines())))
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(fetch,[(k,v,kind) for k,v in versions.items() for kind in ['sources','userdev']]))
(B/'native-source-provenance.json').write_text(json.dumps(dict(acquired_utc=datetime.now(timezone.utc).isoformat(),purpose='仅官方源码补丁与userdev配置读取，不是共享/游戏Jar检查，不执行编译或Java。',artifacts=rows,selected_native_classes=selected),indent=2,ensure_ascii=False)+'\n')
for r in rows:print(r['version'],r.get('mcp'),len(r['selected']))

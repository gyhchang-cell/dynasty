from pathlib import Path
import re,json,zipfile,hashlib,datetime
B=Path(__file__).resolve().parent;R=B.parent;m=json.loads((R/'batch-09/native-source-manifest.json').read_text());symbols={}
for line in Path(m['mapping_cache']).read_text().splitlines():
 if line.startswith('\t') and not line.startswith('\t\t'):
  v=line.split()
  if len(v)>1 and re.fullmatch(r'[mf]_\d+_',v[0]):symbols[v[0]]=v[-1]
paths=['net/minecraft/client/renderer/ItemInHandRenderer.java','net/minecraft/client/renderer/entity/layers/ItemInHandLayer.java','net/minecraft/client/model/HumanoidModel.java','net/minecraft/client/renderer/entity/ItemRenderer.java','net/minecraft/client/renderer/block/model/ItemTransform.java','net/minecraft/world/entity/LivingEntity.java','net/minecraft/world/entity/projectile/AbstractArrow.java','net/minecraft/world/entity/projectile/Projectile.java'];rows=[]
with zipfile.ZipFile(m['base_source_cache']) as z:
 for path in paths:
  raw=z.read(path);data='\n'.join(raw.decode().splitlines())+'\n';syms={s:symbols[s] for s in set(re.findall(r'\b[mf]_\d+_\b',data)) if s in symbols};view=re.sub(r'\b[mf]_\d+_\b',lambda x:syms.get(x[0],x[0]),data);e=dict(id=Path(path).stem,path=path,base_entry_sha256=hashlib.sha256(raw).hexdigest(),symbols=syms,lines=len(view.splitlines()),reviewed_ranges=[],status='EXTRACTED_NOT_REVIEWED',variant='VANILLA_MCP_BEFORE_FORGE_NOT_FABRIC_MERGED')
  for k,t in [('srg',data),('reading_view',view)]:
   p=B/'native/vanilla-mcp-1.20.1'/k/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t);e[k]=str(p.relative_to(B));e[k+'_sha256']=hashlib.sha256(t.encode()).hexdigest()
  rows.append(e)
v=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),base_source_cache=m['base_source_cache'],base_stage=m['base_stage'],mapping_cache=m['mapping_cache'],mapping_sha256=m['mapping_sha256'],source_limit='同版本原版基线，仅比较控制流与矩阵；不是Fabric合并后源码，不认证Mixin ordinal/locals成功。',files=rows,new_reference_credit=0)
(B/'native-consumers.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');(B/'progress.json').write_text(json.dumps(dict(status='IN_PROGRESS_DUAL_PARRY_PROJECTILE_AND_POSE',deadline='2026-10-31T12:09:23+08:00',new_source_families=0,new_accepted_credit=0,production_changed=False),ensure_ascii=False,indent=2)+'\n');print([(r['id'],r['lines']) for r in rows])

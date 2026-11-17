from pathlib import Path
from datetime import datetime,timezone
import json,zipfile,hashlib,re
B=Path(__file__).resolve().parent
prior=json.loads((B.parent/'batch-05/native-reconstruction.json').read_text());prov=json.loads((B/'native-source-provenance.json').read_text())
source=Path(prior['base_source_cache']);mapping=Path(prior['mapping_cache']);syms={}
for l in mapping.read_text().splitlines():
 if l.startswith('\t') and not l.startswith('\t\t'):
  p=l.split()
  if len(p)>=2 and re.fullmatch(r'[mf]_\d+_',p[0]):
   if p[0] in syms:assert syms[p[0]]==p[-1]
   syms[p[0]]=p[-1]

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
   elif not l:break
   else:break
   i+=1
  assert len(old)==oldcount and len(new)==newcount,(h[0],len(old),len(new))
  at=oldstart-1
  if original[at:at+oldcount]!=old:
   found=[n for n in range(pos,len(original)-oldcount+1) if original[n:n+oldcount]==old];assert len(found)==1,(h[0],found);at=found[0]
  assert at>=pos
  out.extend(original[pos:at]);out.extend(new);pos=at+oldcount;hunks.append(dict(old_start=oldstart,actual_start=at+1,exact_context=True))
 assert hunks or '@@' not in patch, 'Patch headers were not consumed'
 out.extend(original[pos:]);return '\n'.join(out)+'\n',hunks

res=[]
with zipfile.ZipFile(source) as z:
 for path in prov['selected_native_classes']:
  raw=z.read(path);base=raw.decode();basehash=hashlib.sha256(raw).hexdigest()
  for version in ['vanilla-mcp-1.20.1','forge-47.3.0','neoforge-47.1.64']:
   if version!='vanilla-mcp-1.20.1':
    config=json.loads((B/f'{version}-userdev-config.json').read_text());assert config['mcp']==prior['mcp_from_official_userdev_config']
   p=B/(version+'-patches')/'patches'/ (path+'.patch');applied,hunks=patch_exact(base,p.read_text()) if p.exists() else ('\n'.join(base.splitlines())+'\n',[])
   symbols={s:syms[s] for s in set(re.findall(r'\b[mf]_\d+_\b',applied)) if s in syms};view=re.sub(r'\b[mf]_\d+_\b',lambda m:symbols.get(m[0],m[0]),applied)
   srg=B/'native'/version/'srg'/path;rd=B/'native'/version/'reading-view'/path;srg.parent.mkdir(parents=True,exist_ok=True);rd.parent.mkdir(parents=True,exist_ok=True);srg.write_text(applied);rd.write_text(view)
   res.append(dict(version=version,path=path,base_entry_sha256=basehash,patch=str(p.relative_to(B)) if p.exists() else None,patch_hunks=hunks,srg=str(srg.relative_to(B)),reading_view=str(rd.relative_to(B)),srg_sha256=hashlib.sha256(applied.encode()).hexdigest(),reading_view_sha256=hashlib.sha256(view.encode()).hexdigest(),lines=len(view.splitlines()),symbols=symbols,reviewed_ranges=[],read_status='RECONSTRUCTED_NOT_REVIEWED'))
(B/'native-reconstruction.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),base_source_cache=str(source),base_stage=prior['base_stage'],mcp_coordinate=prior['mcp_from_official_userdev_config'],mapping_cache=str(mapping),mapping_sha256=hashlib.sha256(mapping.read_bytes()).hexdigest(),method='复用已有MCP源码基底；按官方准确版本补丁精确上下文应用，SRG原文保留并另外映射成员名阅读。没有Java/反编译/编译/游戏。',limitations=['基底未独立重新生成；不代表原版/Fabric运行时Mixin合并结果。','未列阅读行号的文件仅还原，不能声称全文研究；所有引擎上下文计新参考0。'],files=res),indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'reconstructed_files':len(res),'versions':sorted(set(x['version'] for x in res))}))

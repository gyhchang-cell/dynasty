"""Read-only comparison of five historical Gradle seeds to retained tooling."""
from pathlib import Path
import ast, os, stat, hashlib, json, datetime

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/maintenance/storage-cleanup-20261116/remaining-review'
assert not (OUT/'cache-duplicate-selection.json').exists()
tree_ast=ast.parse((OUT.parent/'delete_repeated_forge_cache.py').read_text())
fn=next(n for n in tree_ast.body if isinstance(n,ast.FunctionDef) and n.name=='tree')
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<read-only-tree>','exec'))
KEEP=ROOT/'tools/cod4/ecology-acceptance/.work/gradle-home/caches'
COPIES=[ROOT/p/'caches' for p in [
 'tools/cod4/ecology-acceptance/.work/client-build/gradle-home',
 'tools/cod4/ecology-acceptance/.work/cross-build/gradle-home',
 'tools/cod4/interaction-acceptance/.work/gradle-home',
 'tools/cod4/mob-load-acceptance/.work/gradle-home',
 'tools/cod4/armor-acceptance/.work/gradle-home']]
parts=['modules-2/files-2.1','jars-9','8.8','8.12.1','9.7.1']
patterns={str((cr/part).relative_to(ROOT)):[] for cr in COPIES for part in parts}
needles={s:(s.encode(),s.replace('/','\\/').encode()) for s in patterns}
ref_count=0
for name in (OUT/'fresh-gradle-reference-files.txt').read_text().splitlines():
 p=ROOT/name
 if not p.is_file(): continue
 found=set();tail=b''
 try:
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):
    data=tail+block
    for s,ns in needles.items():
     if s not in found and any(n in data for n in ns):found.add(s)
    tail=data[-2048:]
 except OSError:raise
 for s in found:patterns[s].append(name)
 ref_count+=1
 if ref_count%250==0: print('reference_files_streamed',ref_count,flush=True)
def reference_hits(p):
 s=str(p.relative_to(ROOT))
 # Selected descendants are considered only when their whole base has no hits.
 return patterns.get(s,[])
selection=[];preserved=[];keepers={}
for part in parts:
 kr=KEEP/part;kr_rows=tree(kr); keepers[part]=kr_rows
 kd={r['path']:r for r in kr_rows}
 for cr in COPIES:
  base=cr/part
  if not base.is_dir():continue
  hits=reference_hits(base)
  if hits:
   preserved.append({'path':str(base),'reason':'Bound reference path','hits':hits});continue
  rows=tree(base)
  def identical_subset(prefix):
   subset=[r for r in rows if not prefix or r['path']==prefix or r['path'].startswith(prefix+'/')]
   return bool(subset) and all(kd.get(r['path'])==r for r in subset)
  # Prefer whole equal trees, otherwise consider immediate child directories only.
  # Unknown, different and unique data are never selected.
  choices=[''] if identical_subset('') else [r['path'] for r in rows if '/' not in r['path'] and r['type']=='directory' and identical_subset(r['path'])]
  selected_prefixes=[]
  for prefix in choices:
   p=base/prefix if prefix else base
   if reference_hits(p):continue
   current=tree(p)
   if not any(r['type']=='file' and r.get('bytes',0)>0 for r in current):continue
   selection.append({'path':str(p),'keeper':str(kr/prefix if prefix else kr),'rows':current,'bytes':sum(r.get('bytes',0) for r in current),'part':part})
   selected_prefixes.append(prefix)
  preserved.append({'path':str(base),'reason':'Distinct entries and/or non-selected entries retained','selected_prefixes':selected_prefixes,'all_rows':len(rows)})
  print(json.dumps({'path':str(base),'selected':len(selected_prefixes),'selected_bytes':sum(s['bytes'] for s in selection if s['path']==str(base) or s['path'].startswith(str(base)+'/'))}),flush=True)
plan={'at':datetime.datetime.now().astimezone().isoformat(),'keeper':str(KEEP),'reference_files_read':ref_count,'selected':selection,'preserved':preserved,'keeper_manifests':keepers,'streamed_reference_hits':patterns}
with (OUT/'cache-duplicate-selection.json').open('x') as f:json.dump(plan,f,indent=2)
print('TOTAL',len(selection),sum(s['bytes'] for s in selection),flush=True)

"""Read-only comparison of five seeded cache copies against a retained project copy."""
from pathlib import Path
import datetime, hashlib, json, os, stat, time

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/maintenance/storage-cleanup-20261116'
KEEP=ROOT/'tools/cod4/ecology-acceptance/.work/gradle-home/caches/minecraftforge'
COPIES=[ROOT/p/'caches/minecraftforge' for p in [
 'tools/cod4/ecology-acceptance/.work/client-build/gradle-home',
 'tools/cod4/ecology-acceptance/.work/cross-build/gradle-home',
 'tools/cod4/interaction-acceptance/.work/gradle-home',
 'tools/cod4/mob-load-acceptance/.work/gradle-home',
 'tools/cod4/armor-acceptance/.work/gradle-home']]

def sig(p):
 s=p.lstat();return [s.st_dev,s.st_ino,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns]

def tree(root):
 assert root.resolve()==root and root.is_dir()
 rows=[]; logical=allocated=0; newest=0
 for base,dirs,files in os.walk(root,followlinks=False):
  for name in sorted(dirs+files):
   p=Path(base)/name;s=p.lstat();before=sig(p)
   row={'path':str(p.relative_to(root)),'mode':stat.S_IMODE(s.st_mode)}
   if stat.S_ISLNK(s.st_mode):row.update(type='symlink',target=os.readlink(p))
   elif stat.S_ISDIR(s.st_mode):row.update(type='directory')
   elif stat.S_ISREG(s.st_mode):
    h=hashlib.sha256()
    with p.open('rb') as f:
     for b in iter(lambda:f.read(1048576),b''):h.update(b)
    assert sig(p)==before
    row.update(type='file',bytes=s.st_size,sha256=h.hexdigest())
    logical+=s.st_size;allocated+=s.st_blocks*512;newest=max(newest,s.st_mtime)
   else:raise ValueError(str(p))
   rows.append(row)
 rows.sort(key=lambda r:r['path'])
 content=json.dumps(rows,sort_keys=True,separators=(',',':')).encode()
 return {'root':str(root),'rows':rows,'tree_sha256':hashlib.sha256(content).hexdigest(),'logical_bytes':logical,'allocated_bytes':allocated,'newest_file_mtime':newest}

assert not (OUT/'repeated-forge-cache-plan.json').exists()
ref_review=json.loads((OUT/'minecraftforge-path-reference-review.json').read_text())
bound_roots=set()
for f in ref_review['hits']:
 text=(ROOT/f).read_text(errors='replace')
 for candidate in COPIES:
  if str(candidate.relative_to(ROOT)) in text:
   bound_roots.add(str(candidate))
canonical=tree(KEEP)
with (OUT/'retained-forge-cache-tree.json').open('x') as f:json.dump(canonical,f,separators=(',',':'))
print(json.dumps({'keeper':str(KEEP),'files':len(canonical['rows']),'bytes':canonical['logical_bytes'],'tree_sha256':canonical['tree_sha256']}),flush=True)
results=[]
for i,p in enumerate(COPIES,1):
 if str(p) in bound_roots:
  results.append({'root':str(p),'decision':'KEEP_ENTIRE_REFERENCE_BOUND_CACHE','reason':'Existing source research explicitly binds files inside this copy; retain the complete copy conservatively.'})
  print(json.dumps(results[-1]),flush=True)
  continue
 d=tree(p)
 manifest=OUT/f'forge-cache-copy-{i:02d}-tree.json'
 with manifest.open('x') as f:json.dump(d,f,separators=(',',':'))
 equal=d['rows']==canonical['rows']
 result={k:v for k,v in d.items() if k!='rows'}
 result.update(equal_to_retained=equal,retained=str(KEEP),manifest=str(manifest),older_than_seven_days=time.time()-d['newest_file_mtime']>7*86400)
 results.append(result)
 print(json.dumps(result),flush=True)
plan={'at':datetime.datetime.now().astimezone().isoformat(),'mode':'READ_ONLY_PLAN','retained':str(KEEP),'retained_manifest':str(OUT/'retained-forge-cache-tree.json'),'copies':results,'reference_scan':ref_review,'purpose':'Only redundant Gradle caches/minecraftforge seeds cloned by historical prepare.py cp -cR; no source/QA snapshots/worlds, forge_gradle pinned sources, metadata, receipts or current outputs in deletion scope.'}
with (OUT/'repeated-forge-cache-plan.json').open('x') as f:json.dump(plan,f,indent=2)

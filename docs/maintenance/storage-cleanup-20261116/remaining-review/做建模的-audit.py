from pathlib import Path
import os,json,hashlib,datetime
R=Path('/Users/a15356015027/Desktop/dynasty');O=R/'docs/maintenance/storage-cleanup-20261116/remaining-review'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def meta(p):
 s=p.stat();return dict(path=str(p.relative_to(R)),bytes=s.st_size,allocated_bytes=s.st_blocks*512,inode=s.st_ino,links=s.st_nlink,sha256=digest(p))
B=R/'build/bestiary-v43/packaging-20261030/snapshot';snap=json.loads((R/'docs/art/bestiary-v43/build-verification-20261030/snapshot-inputs.json').read_text())['sha256']
rows=[];unique=[]
for p in sorted((B/'build/resources/main').rglob('*')):
 if not p.is_file() or p.is_symlink():continue
 rel=p.relative_to(B/'build/resources/main');original=B/'src/main/resources'/rel
 v=meta(p);v['retained_original']=str(original.relative_to(R));v['source_present']=original.is_file()
 if original.is_file() and not original.is_symlink():
  v['source_sha256']=digest(original);v['same_bytes']=v['sha256']==v['source_sha256'];v['snapshot_input_sha256']=snap.get(str(original.relative_to(B)));v['source_matches_fixed_input']=v['source_sha256']==v['snapshot_input_sha256']
 if not (v.get('same_bytes') and v.get('source_matches_fixed_input')):unique.append(v)
 rows.append(v)
report=dict(date='2026-11-16',purpose='Read-only per-file comparison of historical generated resources against preserved exact source snapshot; no production/build activity',resource_files=len(rows),logical_bytes=sum(v['bytes'] for v in rows),allocated_bytes=sum(v['allocated_bytes'] for v in rows),exact_fixed_source_matches=sum(bool(v.get('same_bytes') and v.get('source_matches_fixed_input')) for v in rows),unique_or_unproven=unique,files=rows)
(O/'做建模的-resource-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['files','unique_or_unproven']},ensure_ascii=False));print('unproven',len(unique),[v['path'] for v in unique[:8]])
jar=[meta(B/'build/reobfJar/output.jar'),meta(B/'build/libs/dynasty-1.4.0.jar')]
(O/'做建模的-jar-comparison.json').write_text(json.dumps(dict(files=jar,byte_identical=jar[0]['sha256']==jar[1]['sha256'],retained='build/libs/dynasty-1.4.0.jar',artifact_record='docs/art/bestiary-v43/build-verification-20261030/report.json'),ensure_ascii=False,indent=2)+'\n')

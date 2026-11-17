from pathlib import Path
import json,hashlib,subprocess,os,zipfile,datetime
R=Path('/Users/a15356015027/Desktop/dynasty');O=R/'docs/maintenance/storage-cleanup-20261116/remaining-review'
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def disk():
 s=os.statvfs(R);return dict(available_bytes=s.f_bavail*s.f_frsize,free_bytes=s.f_bfree*s.f_frsize)
def put(n,j):(O/n).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
def safe(p):
 assert p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(R)
 for a in p.parents:
  if a==R:break
  assert not a.is_symlink()
refs=json.loads((O/'做建模的-reference-check.json').read_text());assert refs['returncode']==1 and not refs['matches'] and not refs['stderr']
res=json.loads((O/'做建模的-resource-comparison.json').read_text());jar=json.loads((O/'做建模的-jar-comparison.json').read_text());assert jar['byte_identical']
keep=R/jar['files'][1]['path'];expected=jar['files'][1]['sha256'];safe(keep);assert digest(keep)==expected
reportpath=R/'docs/art/bestiary-v43/build-verification-20261030/report.json';buildreport=json.loads(reportpath.read_text());assert buildreport['artifact']['sha256']==expected and buildreport['artifact']['path']==str(keep)
rows=[dict(path=jar['files'][0]['path'],sha256=expected,bytes=jar['files'][0]['bytes'],allocated_bytes=jar['files'][0]['allocated_bytes'],retained_original=str(keep.relative_to(R)),source_sha256=expected,kind='byte-identical reobfuscation intermediate')]
for v in res['files']:
 if v.get('same_bytes') and v.get('source_matches_fixed_input'):
  rows.append(dict(v,kind='generated resource byte-identical to fixed preserved snapshot source'))
# Complete package also retains every duplicate resource, checked by decompressed entry SHA.
with zipfile.ZipFile(keep) as z:
 for v in rows[1:]:
  rel=Path(v['path']).relative_to('build/bestiary-v43/packaging-20261030/snapshot/build/resources/main').as_posix()
  assert hashlib.sha256(z.read(rel)).hexdigest()==v['sha256'],rel
for v in rows:
 p=R/v['path'];q=R/v['retained_original'];safe(p);safe(q)
 s=p.stat();assert s.st_size==v['bytes'] and digest(p)==v['sha256']==digest(q)
 v['inode']=s.st_ino;v['mtime_ns']=s.st_mtime_ns
handles=[]
for args in [['lsof','-nP','--',str(R/rows[0]['path']),str(keep)],['lsof','-nP','+D',str(R/'build/bestiary-v43/packaging-20261030/snapshot/build/resources/main')]]:
 p=subprocess.run(args,capture_output=True,text=True,timeout=30);rec=dict(command=args,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr);handles.append(rec)
 assert p.returncode==1 and not p.stdout.strip() and not p.stderr.strip(),rec
before=disk();put('做建模的-deletion-plan.json',dict(authorized_scope='2026-11-16 delegated model/bestiary derived cache cleanup only; production/research remains paused',files=rows,total_logical_bytes=sum(v['bytes'] for v in rows),total_allocated_bytes=sum(v['allocated_bytes'] for v in rows),retained_artifact_sha256=expected,artifact_record=str(reportpath.relative_to(R)),reference_check='做建模的-reference-check.json',handles=handles,space_before=before))
# Re-check each candidate and original immediately before permanent unlink; never recurse into a directory.
journal=O/'做建模的-deleted.jsonl';assert not journal.exists()
with journal.open('x') as log:
 for v in rows:
  p=R/v['path'];q=R/v['retained_original'];s=p.stat()
  assert s.st_ino==v['inode'] and s.st_mtime_ns==v['mtime_ns'] and s.st_size==v['bytes'] and digest(p)==v['sha256']==digest(q)
  p.unlink();assert not p.exists()
  log.write(json.dumps(dict(path=v['path'],bytes=v['bytes'],sha256=v['sha256'],retained_original=v['retained_original'],permanently_unlinked=True),ensure_ascii=False)+'\n');log.flush()
assert digest(keep)==expected
for v in rows:assert not (R/v['path']).exists() and digest(R/v['retained_original'])==v['sha256']
after=disk();receipt=dict(deleted_files=len(rows),logical_bytes_removed=sum(v['bytes'] for v in rows),allocated_bytes_before_unlink=sum(v['allocated_bytes'] for v in rows),space_before=before,space_after=after,observed_available_change_bytes=after['available_bytes']-before['available_bytes'],space_caveat='Concurrent coordinator cleanup and APFS snapshots/clones mean volume free-space delta cannot be attributed solely to this batch.',retained_jar=str(keep.relative_to(R)),retained_jar_sha256=expected,all_retained_originals_rehashed=True,preserved_unproven_resources=res['unique_or_unproven'],production_or_worlds_modified=False,java_build_game_network_run=False,trash_accessed=False,mainlists_modified=False,complete='This bounded cleanup only; outstanding model work remains paused')
put('做建模的-cleanup-receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False))

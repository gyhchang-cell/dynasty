"""Drop old packs only after every packed object is covered by verified new packs."""
from pathlib import Path
import datetime,hashlib,json,os,re,shlex,shutil,subprocess

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
OUT=ROOT/'docs/maintenance/storage-cleanup-20261116/continued'
PACK=ROOT/'.git/objects/pack'
assert ROOT.resolve()==ROOT and PACK.resolve()==PACK
assert not (OUT/'git-compaction-report.json').exists()

def run(args,timeout=300):
 return subprocess.run(args,cwd=ROOT,capture_output=True,text=True,timeout=timeout)

def oid_set():
 r=run(['git','cat-file','--batch-all-objects','--batch-check=%(objectname)'])
 assert r.returncode==0,r.stderr
 ids=set(r.stdout.splitlines());assert all(re.fullmatch('[0-9a-f]{40}',s) for s in ids)
 return ids

def pack_ids(p):
 with p.with_suffix('.idx').open('rb') as f:r=subprocess.run(['git','show-index'],stdin=f,capture_output=True,text=True,cwd=ROOT)
 assert r.returncode==0,r.stderr
 return {line.split()[1] for line in r.stdout.splitlines()}

def file_sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

start=json.loads((OUT/'repack-start.json').read_text())
prepared=json.loads((OUT/'repack-prepared.json').read_text())
supp=json.loads((OUT/'supplemental-pack-result.json').read_text())
assert json.loads((OUT/'verify-new-pack-result.json').read_text())['exit']==0
assert json.loads((OUT/'verify-supplemental-pack-result.json').read_text())['exit']==0
new_packs=[Path(r['path']) for r in prepared['new_packs']]+[Path(supp['path'])]
assert len(new_packs)==2 and len(set(new_packs))==2
new_ids=set()
for p in new_packs:
 assert p.parent==PACK and re.fullmatch(r'pack-[0-9a-f]{40}\.pack',p.name)
 new_ids.update(pack_ids(p))
old_packs=[Path(r['path']) for r in start['old_packs']]
old_ids=set()
for p in old_packs:
 assert p.parent==PACK and p not in new_packs and p.is_file()
 old_ids.update(pack_ids(p))
assert old_ids<=new_ids, f'{len(old_ids-new_ids)} historical objects not covered'
assert not list(PACK.glob('*.keep')) and not list(PACK.glob('*.promisor'))
assert not (PACK/'multi-pack-index').exists()
assert not list(PACK.glob('multi-pack-index-*'))
assert file_sha(ROOT/'.git/index')==start['index_sha256']
all_before=oid_set();baseline=set((OUT/'all-object-ids-before.txt').read_text().splitlines())
assert baseline<=all_before
refs_before=run(['git','show-ref','--head']);assert refs_before.returncode==0
families=[]
for p in old_packs:
 for ext in ['.bitmap','.rev','.idx','.pack']:
  q=p.with_suffix(ext)
  if q.exists():
   assert q.is_file() and not q.is_symlink() and q.resolve()==q
   s=q.stat();families.append({'path':str(q),'bytes':s.st_size,'stat':[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]})
opened=run(['/usr/sbin/lsof','-nP','-Fpn']);assert opened.returncode==0
targets={r['path'] for r in families}
open_targets=[s[1:] for s in opened.stdout.splitlines() if s.startswith('n') and s[1:] in targets]
assert not open_targets,open_targets
assert not (ROOT/'.git/index.lock').exists() and not (ROOT/'.git/gc.pid').exists()
proof={'old_packs':len(old_packs),'new_packs':[str(p) for p in new_packs],'old_unique_packed_objects':len(old_ids),'new_unique_packed_objects':len(new_ids),'all_old_packed_objects_covered':True,'all_objects_before':len(all_before),'old_pack_family_files_to_delete':families,'pack_contents_verified_by_git_verify_pack':True}
with (OUT/'git-final-delete-proof.json').open('x') as f:json.dump(proof,f,indent=2)
free_before_delete=shutil.disk_usage(ROOT).free
for r in families:
 p=Path(r['path']);s=p.stat();assert [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns]==r['stat']
 p.unlink()
assert all(p.is_file() for p in new_packs)
# Only prune loose copies already represented in validated packs. Never expire objects.
dry=run(['git','prune-packed','-n']);assert dry.returncode==0,dry.stderr
(OUT/'prune-packed-dry-run.txt').write_text(dry.stdout)
loose=[]
for line in dry.stdout.splitlines():
 parts=shlex.split(line);assert parts[:2]==['rm','-f'] and len(parts)==3,line
 p=Path(parts[2]);p=p if p.is_absolute() else ROOT/p
 assert p.parent.parent==ROOT/'.git/objects'
 oid=p.parent.name+p.name;assert re.fullmatch('[0-9a-f]{40}',oid) and oid in new_ids
 loose.append({'path':str(p),'oid':oid,'bytes':p.stat().st_size})
prune=run(['git','prune-packed']);assert prune.returncode==0,prune.stderr
update=run(['git','update-server-info']);assert update.returncode==0,update.stderr
all_after=oid_set();assert all_before<=all_after
assert file_sha(ROOT/'.git/index')==start['index_sha256']
refs_after=run(['git','show-ref','--head']);assert refs_after.returncode==0
assert refs_after.stdout==refs_before.stdout,'Refs changed during operation; inspect concurrent edits'
connect=run(['git','fsck','--connectivity-only','--no-dangling'])
(OUT/'git-connectivity-final.stdout').write_text(connect.stdout)
(OUT/'git-connectivity-final.stderr').write_text(connect.stderr)
assert connect.returncode==0,connect.stderr
count=run(['git','count-objects','-v']);assert count.returncode==0
(OUT/'git-count-after-compaction.txt').write_text(count.stdout)
report={'at':datetime.datetime.now().astimezone().isoformat(),'old_packs_removed':len(old_packs),'old_pack_family_files_removed':len(families),'old_pack_family_bytes_removed':sum(r['bytes'] for r in families),'validated_new_pack_bytes':sum(p.stat().st_size+p.with_suffix('.idx').stat().st_size for p in new_packs),'loose_duplicate_objects_removed':len(loose),'loose_duplicate_compressed_bytes_removed':sum(r['bytes'] for r in loose),'net_object_storage_bytes_reduction':sum(r['bytes'] for r in families)+sum(r['bytes'] for r in loose)-sum(p.stat().st_size+p.with_suffix('.idx').stat().st_size for p in new_packs),'all_objects_before':len(all_before),'all_objects_after':len(all_after),'no_old_object_id_lost':True,'all_old_refs_and_index_unchanged':True,'connectivity_check_passed':True,'new_pack_full_integrity_checks_passed':True,'history_expiry_or_unreachable_prune_performed':False,'free_before_initial_repack':start['free_before'],'free_before_delete':free_before_delete,'free_after':shutil.disk_usage(ROOT).free,'permanent_delete_no_trash':True}
with (OUT/'loose-duplicate-objects-removed.json').open('x') as f:json.dump(loose,f,separators=(',',':'))
with (OUT/'git-compaction-report.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(report),flush=True)

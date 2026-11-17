from pathlib import Path
import json,hashlib,struct,importlib.util,subprocess,os,zipfile
R=Path('/Users/a15356015027/Desktop/dynasty');O=R/'docs/maintenance/storage-cleanup-20261116/remaining-review';H=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();put=lambda n,x:(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# Scope is only texture-owned importer caches and whole-armor study helpers.
dirs=[R/'tools/art/inventory-refresh/__pycache__']+list((R/'docs/art').glob('armor-*/__pycache__'))
cs=[];held=[]
for d in dirs:
 for f in sorted(d.glob('*.pyc')):
  if f.is_symlink():continue
  stem=f.name.split('.cpython-')[0];s=d.parent/(stem+'.py');row={'path':str(f),'logical_bytes':f.stat().st_size,'allocated_bytes_observed':f.stat().st_blocks*512,'sha256':H(f),'source':str(s)}
  if not s.is_file() or s.is_symlink():row['reason']='no regular retained source';held.append(row);continue
  row['source_sha256']=H(s);head=f.read_bytes()[:16];flags=struct.unpack('<I',head[4:8])[0];valid=False
  if len(head)==16 and head[:4]==importlib.util.MAGIC_NUMBER:
   if flags==0:valid=struct.unpack('<II',head[8:16])==(int(s.stat().st_mtime)&0xffffffff,s.stat().st_size&0xffffffff)
   elif flags in (1,3):valid=head[8:16]==importlib.util.source_hash(s.read_bytes())
  if not valid:row['reason']='source/cache header is not an exact current interpreter/source match; keep uncertain historical bytecode';held.append(row);continue
  row['regeneration_proof']='matching CPython magic and source timestamp+size or source hash; retained original .py, no recompilation performed';cs.append(row)
patterns=[]
for x in cs:patterns.extend([str(Path(x['path']).relative_to(R)),Path(x['path']).name,x['sha256']])
pat=O/'做贴图的-cache-reference-patterns.txt';pat.write_text('\n'.join(patterns)+'\n')
cmd=['rg','-n','-l','-F','-f',str(pat),'--hidden','--glob','!.git/**','--glob','!tools/cod4/**','--glob','!docs/maintenance/storage-cleanup-20261116/**','--glob','!**/.venv/**','--glob','!**/gradle-home/**','--glob','*.json','--glob','*.jsonl','--glob','*.md','--glob','*.txt','--glob','*.py','--glob','*.log','--glob','*.xml','--glob','*.gradle','--glob','*.properties','.']
z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);put('做贴图的-cache-reference-scan.json',{'command':cmd,'returncode':z.returncode,'stdout':z.stdout,'stderr':z.stderr,'scope_exclusions':'main-owned tools/cod4, .git, maintenance reports and dependency environments intentionally excluded; uncertainty => HOLD'})
assert z.returncode in (0,1),z.stderr
hits={}
for n in z.stdout.splitlines():
 p=R/n;raw=p.read_text(errors='replace')
 for x in cs:
  if any(v in raw for v in [str(Path(x['path']).relative_to(R)),Path(x['path']).name,x['sha256']]):hits.setdefault(x['path'],[]).append(str(p))
eligible=[]
for x in cs:
 if x['path'] in hits:x['reason']='explicit path/hash reference';x['references']=hits[x['path']];held.append(x)
 else:x['references']=[];eligible.append(x)
# lsof selects named candidates; no process actions.
ls=['/usr/sbin/lsof','-nP','-Fpn','--']+[x['path'] for x in eligible];z=subprocess.run(ls,capture_output=True,text=True);put('做贴图的-cache-open-handles.json',{'command':ls,'returncode':z.returncode,'stdout':z.stdout,'stderr':z.stderr})
if z.returncode!=1 or z.stdout.strip() or z.stderr.strip():
 for x in eligible:x['reason']='open-handle audit not unequivocally empty';held.append(x)
 eligible=[]
put('做贴图的-cache-plan.json',{'mode':'PREPARED_ONLY_NOT_DELETED','candidates':eligible,'held':held,'candidate_count':len(eligible),'logical_bytes':sum(x['logical_bytes'] for x in eligible),'allocated_bytes_observed':sum(x['allocated_bytes_observed'] for x in eligible),'production_or_build_executed':False})
# Deep historical deployment comparison: central directory fields, not CRC treated as SHA equality.
backups=[]
for ver in [28,29]:
 ps=sorted((R/f'docs/art/armor-foundations-v{ver}/deployment-before').glob('*/dynasty-1.4.0.jar'));base=None;baseline_path=None
 delivery=R/f'docs/art/armor-foundations-v{ver}/DELIVERY.json';delivery_text=delivery.read_text()
 for p in ps:
  with zipfile.ZipFile(p) as ar:q={i.filename:(i.CRC,i.file_size) for i in ar.infolist()};meta={i.filename:(i.date_time,i.compress_type,i.external_attr) for i in ar.infolist()}
  if base is None:base=q;baseline_path=str(p)
  changed=sorted(n for n in base.keys()&q.keys() if base[n]!=q[n]);different_sha=[]
  if changed:
   with zipfile.ZipFile(baseline_path) as za,zipfile.ZipFile(p) as zb:
    for n in changed:
     ha=hashlib.sha256(za.read(n)).hexdigest();hb=hashlib.sha256(zb.read(n)).hexdigest();assert ha!=hb;different_sha.append({'entry':n,'baseline_member_sha256':ha,'member_sha256':hb})
  h=H(p);row={'path':str(p),'sha256':h,'logical_bytes':p.stat().st_size,'allocated_bytes_observed':p.stat().st_blocks*512,'nlink':p.stat().st_nlink,'baseline':baseline_path,'central_member_count':len(q),'central_payload_crc_size_changed_count':len(changed),'added_members':sorted(q.keys()-base.keys()),'missing_members':sorted(base.keys()-q.keys()),'actual_changed_member_hashes':different_sha,'historical_binding':{'record':str(delivery),'record_sha256':H(delivery),'before_sha_found':h in delivery_text},'decision':'KEEP','reason':'historical exact beforeSha256 rollback identity; identical CRC/size is not byte identity, and distinct build has actual class/resource differences; no deletion or renormalization','retained_original':str(p)};backups.append(row)
put('做贴图的-historical-archive-deep-review.json',{'files':backups,'protected_logical_bytes':sum(x['logical_bytes'] for x in backups),'no_archive_deletion':True})
print('cache candidates',len(eligible),sum(x['logical_bytes'] for x in eligible),'held',len(held),'archives kept',len(backups))

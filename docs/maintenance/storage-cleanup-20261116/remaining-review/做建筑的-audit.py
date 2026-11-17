"""Read-only snapshot/reference audit. No producer, game, compilation, network, or deletion."""
from pathlib import Path
import json,hashlib,collections,subprocess,re,shutil,os
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PREFIX='做建筑的-'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def save(n,d):(OUT/(PREFIX+n)).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
fr=ROOT/'build/blueprint-client/frozen';records=[];groups=collections.defaultdict(list)
for p in sorted(fr.iterdir()):
 if not p.is_dir() or p.is_symlink():continue
 m=p/'runtime-manifest.json';d=json.loads(m.read_text());trees=[];signature=[]
 for t in d['trees']:
  es=sorted((e['path'],e['sha256']) for e in t['entries']);digest=hashlib.sha256(json.dumps(es,separators=(',',':')).encode()).hexdigest()
  trees.append({'runtime':t['runtime'],'source':t['source'],'entries':len(es),'manifest_claimed_content_signature':digest,'source_directory_exists':Path(t['source']).is_dir()})
  signature.append((Path(t['runtime']).name,es))
 s=hashlib.sha256(json.dumps(sorted(signature),separators=(',',':')).encode()).hexdigest();groups[s].append(p.name)
 records.append({'path':str(p),'identity':p.name,'manifest_sha256':sha(m),'file_entries':sum(t['entries'] for t in trees),'trees':trees,'manifest_claimed_whole_signature':s,'decision':'KEEP_RUN_BOUND_SNAPSHOT_UNLESS_SEPARATE_LIFECYCLE_PROOF','actual_full_payload_rehashed':False})
pat=OUT/(PREFIX+'snapshot-reference-patterns.txt');pat.write_text('\n'.join(r['identity'] for r in records)+'\n')
args=['rg','--json','--hidden','-F','-f',str(pat),'docs','tools','src','.run','-g','*.json','-g','*.md','-g','*.py','-g','*.txt','-g','*.sh','-g','!docs/maintenance/**','-g','!tools/cod4/**']
a=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);assert a.returncode in [0,1],a.stderr
refs=collections.defaultdict(list)
matcher=re.compile(r'(?<![A-Za-z0-9_.-])('+ '|'.join(re.escape(r['identity']) for r in sorted(records,key=lambda x:-len(x['identity'])))+r')(?![A-Za-z0-9_.-])')
for line in a.stdout.splitlines():
 o=json.loads(line)
 if o['type']!='match':continue
 d=o['data'];text=d['lines']['text'];ids=set(matcher.findall(text))
 for id in ids:refs[id].append({'path':str(ROOT/d['path']['text']),'line':d['line_number'],'excerpt':text.strip()[:360]})
for r in records:r['external_reference_hits']=refs[r['identity']]
# Inspect only manifest differences for relevant structure QA snapshots; no full payload rescanning claimed.
comparison=[]
for left,right in [('cod3-dragon-palace-20261020-v2','cod3-dragon-palace-20261020-v3'),('cod3-ghost-ship-20261020-v1','cod3-ghost-ship-20261020-v3')]:
 def index(name):
  d=json.loads((fr/name/'runtime-manifest.json').read_text());return {(Path(t['runtime']).name,e['path']):e['sha256'] for t in d['trees'] for e in t['entries']}
 x=index(left);y=index(right);different=[{'tree':k[0],'path':k[1],'left':x.get(k),'right':y.get(k)} for k in sorted(x.keys()|y.keys()) if x.get(k)!=y.get(k)]
 selected=[]
 for q in different[:3]:
  ev={'path':q['path']}
  for label,name in [('left',left),('right',right)]:
   pp=fr/name/q['tree']/q['path'];ev[label]={'path':str(pp),'actual_sha256':sha(pp) if pp.is_file() else None,'expected':q[label]}
  selected.append(ev)
 comparison.append({'left':str(fr/left),'right':str(fr/right),'manifest_differences':len(different),'first_differences':different[:12],'actual_hash_selected_proof':selected,'decision':'KEEP_UNIQUE_HISTORICAL_BYTES'})
# Same manifest inputs are a triage signal only; launch/run evidence can still be distinct.
dups=[{'manifest_signature':k,'identities':v,'external_refs':{n:refs[n] for n in v},'decision':'KEEP_NOT_PROVEN_USELESS; no payload deletion based on manifest equality'} for k,v in groups.items() if len(v)>1]
save('snapshot-audit.json',{'scope':'184 blueprint frozen run identities only, manifest metadata and business references; avoid .git and tools/cod4 caches','snapshot_count':len(records),'manifest_entry_count':sum(r['file_entries'] for r in records),'whole_manifest_signature_groups':len(groups),'same_manifest_groups':dups,'snapshot_records':records,'selected_structure_version_differences':comparison,'reference_scan':{'args':args,'returncode':a.returncode,'stderr':a.stderr,'limits':'Only docs/tools(excludingcod4)/src/.run text; no result is proof of globally unreferenced or useless. Launch self-bindings additionally remain.'},'disk_observation':shutil.disk_usage(ROOT)._asdict(),'deletions':[]})
# Tiny generated .pyc cache candidates. Source retained, every candidate and source separately SHA-bound.
candidates=[]
for base in [ROOT/'tools/architecture',ROOT/'docs/architecture']:
 for p in sorted(base.rglob('*.pyc')):
  if p.is_symlink():continue
  src=p.parent.parent/(p.name.split('.cpython-')[0]+'.py')
  candidates.append({'path':str(p),'sha256':sha(p),'logical_bytes':p.stat().st_size,'allocated_bytes':p.stat().st_blocks*512,'retained_source':str(src),'source_exists':src.is_file(),'source_sha256':sha(src) if src.is_file() else None,'source_bytes':src.stat().st_size if src.is_file() else None})
# Cache exact-basename references, excluding only our new audit which intentionally names them.
cachepat=OUT/(PREFIX+'cache-reference-patterns.txt');cachepat.write_text('\n'.join(Path(c['path']).name for c in candidates)+'\n')
a=subprocess.run(['rg','--json','--hidden','-F','-f',str(cachepat),'docs','tools','src','.run','-g','*.json','-g','*.md','-g','*.py','-g','*.txt','-g','*.sh','-g','!docs/maintenance/**','-g','!tools/cod4/**'],cwd=ROOT,capture_output=True,text=True)
for c in candidates:c['reference_scan_result']='NO_EXACT_CACHE_BASENAME_HITS_IN_SCANNED_BUSINESS_TEXT' if a.returncode==1 else 'HOLD_SCAN_HAS_HITS_OR_ERROR'
try:
 l=subprocess.run(['lsof','-nP','--']+[c['path'] for c in candidates],capture_output=True,text=True,timeout=30)
 handles={'returncode':l.returncode,'stdout':l.stdout,'stderr':l.stderr,'clear':l.returncode==1 and not l.stdout and not l.stderr}
except Exception as e:handles={'clear':False,'error':str(e)}
save('cache-candidates.json',{'candidates':candidates,'reference_scan_returncode':a.returncode,'reference_scan_stdout':a.stdout,'reference_scan_stderr':a.stderr,'reference_scope_limits':'Business docs/tools except cod4/src/.run; exact cache name search; all research evidence protected. No source or result file is a deletion candidate.','open_handle_check':handles,'decision':'AUDIT_ONLY_CANDIDATES_NOT_YET_DELETED','total_logical_bytes':sum(c['logical_bytes'] for c in candidates),'total_allocated_bytes':sum(c['allocated_bytes'] for c in candidates)})
print(json.dumps({'snapshots':len(records),'entries':sum(r['file_entries'] for r in records),'signaturegroups':len(groups),'sameinput_groups':len(dups),'externally_referenced_identities':sum(bool(r['external_reference_hits']) for r in records),'selected_diffs':[(r['left'].split('/')[-1],r['manifest_differences']) for r in comparison],'cache_count':len(candidates),'cache_bytes':sum(c['logical_bytes'] for c in candidates),'cache_scan':a.returncode,'handles_clear':handles.get('clear'),'report':str(OUT)},ensure_ascii=False))

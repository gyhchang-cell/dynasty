"""Verify source integrity and seal configured actual-reading boundaries in this batch only."""
import json,hashlib,math,sys
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def get(n):return json.loads((OUT/n).read_text())
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def restore(v):
 if isinstance(v,dict):
  if set(v)=={'__original_nbt_byte_array_hex__'}:return bytes.fromhex(v['__original_nbt_byte_array_hex__'])
  return {k:restore(w)for k,w in v.items()}
 if isinstance(v,list):return [restore(w)for w in v]
 return v
checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():check('retained '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
cfg=get('review-config.json');screen=get('pre-render-history-screen.json');ctx=get('source-context.json');cases=[];functional=[];context=[]
for a,r,rv in zip(get('sources.json')['candidates'],get('raw-source-audit.json')['candidates'],cfg['cases']):
 ident=a['id'];check(ident+' review ID',ident==r['id']==rv['id']);sr=next(x for x in screen['rows']if x['id']==ident)
 check(ident+' pre-render history/alias/exact exclusion',sr['eligible_for_new_source_study']and not any(sr[k]for k in ['known_history','historical_exact_matches','within_batch_exact_matches']))
 check(ident+' unchanged fixed archive',bind(a['source_archive'])==sr['fixed_archive'])
 with ZipFile(a['source_archive'])as z:
  b=z.read(a['member']);d=read(b);pal=d['palette'];mp={tuple(x['pos']):pal[x['state']]for x in d['blocks']};counts=Counter(pal[x['state']]['Name']for x in d['blocks'])
  check(ident+' lossless original NBT',hashlib.sha256(b).hexdigest()==a['nbt_sha256']==r['nbt_sha256']and d==restore(r['nbt_decoded_original']))
  check(ident+' unique positions and all bounds',len(mp)==len(d['blocks'])and all(0<=x['state']<len(pal)and all(0<=x['pos'][i]<d['size'][i]for i in range(3))for x in d['blocks']))
  check(ident+' full original material count',dict(counts)==r['material_counts']and sum(counts[n]for n in AIR)==r['air']and len(d['blocks'])-r['air']==r['nonair'])
  actual=[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])];check(ident+' expected source stats',actual==rv['source_stats'])
  for alias in sr['same_bytes_aliases']:check(ident+' samebyte alias excluded '+alias,z.read(alias)==b)
  for n,expected in rv.get('expected_counts',{}).items():check(ident+' material '+n,counts[n]==expected)
  for expected in rv.get('expected_states',[]):check(ident+' state '+str(expected['pos']),mp.get(tuple(expected['pos']))==expected['state'])
  for expected in rv.get('expected_block_entities',[]):check(ident+' BE '+str(expected['pos']),next(x.get('nbt')for x in d['blocks']if x['pos']==expected['pos'])==expected['nbt'])
  c=next(x for x in ctx['candidates']if x['id']==ident)
  for m in [x for x in ctx['metadata']if x['id']==ident]:check(ident+' metadata '+m['member'],hashlib.sha256(z.read(m['member'])).hexdigest()==m['sha256']and z.read(m['member']).decode()==m['original_text'])
  for cc in c['contexts']:check(ident+' original JSON '+cc['member'],hashlib.sha256(z.read(cc['member'])).hexdigest()==cc['sha256']and json.loads(z.read(cc['member']))==cc['json'])
  for n in c['missing']:check(ident+' missing only single archive '+n,n not in z.namelist())
  root=next(x['json']for x in c['contexts']if '/worldgen/structure/'in x['member']);pool=next(x['json']for x in c['contexts']if x['member'].endswith(rv.get('selected_pool_suffix','/houses.json')));selected=[e for e in pool['elements']if e.get('element',{}).get('location')==c['location']]
  check(ident+' actual selected pool original',selected==rv['selected'])
  for k,v in rv['root_fields'].items():check(ident+' original root '+k,root.get(k)==v)
  for k in rv.get('root_absent',[]):check(ident+' original root absent '+k,k not in root)
  ims=[bind(OUT/(ident+'-'+n+'.png'))for n in rv['viewed']]
  for im in ims:
   with Image.open(im['path'])as pic:pic.verify()
   check('actual viewed image '+im['path'],True)
  functional.append({'id':ident,'source_stats':actual,'omitted_positions':math.prod(d['size'])-len(d['blocks']),'original_entities':d['entities'],'functional_states':[{'pos':x['pos'],'state':pal[x['state']],'original_block_entity':x.get('nbt')}for x in d['blocks']if x.get('nbt')or any(t in pal[x['state']]['Name']for t in ['door','furnace','smithing','grindstone','bed','lava','water','stairs','ladder','anvil','smoker'])]})
  cases.append({**a,'screening_observations':rv['observations'],'saved_written_comparisons':rv['written_comparisons'],'images_actually_viewed':ims,'actual_full_reference_study_complete':False,'credit_proposal_maximum':0,'formal_credit_added':0,'status':cfg['status'],'native_acceptance':False})
  context.append({'id':ident,'root_context':root,'actual_selected':selected,'single_archive_missing_not_environment_missing':c['missing'],'reading':rv['context_reading']})
viewed=[x for c in cases for x in c['images_actually_viewed']];seen={x['path']for x in viewed};unviewed=[bind(p)for p in sorted(OUT.glob('*.png'))if str(p)not in seen]
check('actual generated/viewed/unviewed boundaries',[len(list(OUT.glob('*.png'))),len(viewed),len(unviewed)]==cfg['image_counts'])
check('history pairs not semantic credit',screen['history_unique_archive_member_pairs']==cfg['history_pairs'])
check('fixed prefilter binding',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
bindings(get('latest-independent-admissions.json'));bindings(cfg)
prev=ROOT/f"docs/architecture/research-20261104-smithy-{cfg['batch']-1:03d}"
carry=json.loads((prev/'carried-forward-pending.json').read_text());carry['previous_batch_receipt']=bind(prev/'RECEIPT.json');carry['current_batch_new_pending']=0
check('098101 already zero104 no renewed pending',not carry['prior_pending']and carry['098F01_resolved_zero_once_104']and carry['101F01_resolved_zero_once_104'])
put('carried-forward-pending.json',carry);bindings(carry)
put('task-scope-boundary.json',json.loads((prev/'task-scope-boundary.json').read_text()))
put('functional-evidence.json',{'candidates':functional,'original_states_preserved':True,'native_function_not_verified':True})
put('manual-review.json',{'scope':cfg['scope'],'cases':cases,'source_bodies_visually_screened':len(cases),'complete_whole_reference_studies':0,'generated_current_png':len(viewed)+len(unviewed),'actual_current_images_viewed':len(viewed),'unviewed_png':len(unviewed),'pending_maximum':0,'held_zero':len(cases),'formal_credit_added':0,'no_independent_self_admission':True})
put('visual-reading-boundary.json',{'viewed':viewed,'not_viewed_generated':unviewed,'unviewed_not_observations_or_references':True,'generic_class_fullcell_not_textures_collision_entities':True,'all_layers_and_navigation_reviewed':False})
put('source-context-reading.json',{'cases':context,'limits':cfg['limits'],'prior':'095F02 first097 accepted1，097F01 first100 accepted1；098/101F01 Main有界用途0首次104，本批全部carry0。旧其他pending不取消。COD4仍153/1000差847。'})
put('verification.json',{'status':'PASS_CURRENT_BOUNDED_SCREENING_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'all_tasks_complete':False})
session={'batch':cfg['batch'],'status':cfg['status'],'source_bodies_visually_screened':len(cases),'complete_whole_reference_studies':0,'actual_images_viewed':len(viewed),'generated_png':len(viewed)+len(unviewed),'unviewed_generated':len(unviewed),'pending_maximum':0,'held_zero':len(cases),'formal_credit_added':0,'prior_admissions_current_increment':0,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':cfg['next']}
put('session.json',session);put('active-checkpoint.json',{**session,'verification':bind(OUT/'verification.json'),'next_batch':cfg['batch']+1})
(OUT/'HANDOFF.md').write_text(cfg['handoff']+'\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{**session,'checks_passed':len(checks),'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks':len(checks),'actual_views':len(viewed),'complete_studies':0,'pending':0,'credit':0},ensure_ascii=False))

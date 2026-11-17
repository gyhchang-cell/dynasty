"""Seal exact-byte alias exclusion only; no source decoding or whole study."""
import json,hashlib
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;prev=P.parent/'research-20261104-smithy-162'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
checks=[]
def check(n,ok):
 assert ok,n
 checks.append({'name':n,'passed':True})
s=get(P/'pre-render-history-screen.json');r=s['rows'][0]
check('new source study correctly blocked',r['eligible_for_new_source_study']is False)
alias='data/kaisyn/structures/outpost/camps/sparse_jungle/side/workshop.nbt'
check('one known historical alias',r['same_bytes_aliases']==[alias]and len(r['known_history'])==1 and r['known_history'][0]['member']==alias)
check('three fingerprint matches only exclusion no credit',len(r['historical_exact_matches'])==1 and set(r['historical_exact_matches'][0]['exact_keys'])=={'nbt_sha256','role_sha256','occupancy_sha256'})
check('fixed archive unchanged',bind(Path(r['source_archive']))==r['fixed_archive'])
with ZipFile(r['source_archive'])as z:
 new=z.read(r['member']);old=z.read(alias)
 check('machine byte equality of alias',new==old and hashlib.sha256(new).hexdigest()==r['nbt_sha256'])
for f in get(P/'protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(Path(f['path']))==f)
check('no images generated',not list(P.glob('*.png')))
check('no original source decoding performed',not (P/'raw-source-audit.json').exists())
carry=get(prev/'carried-forward-pending.json');carry['previous_batch_receipt']=bind(prev/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
check('only157NPC05/158NPC01 unresolved proposals retained',sorted((x['batch'],x['id'])for x in carry['carried_unresolved_whole_reference_proposals'])==[(157,'W01'),(158,'F01')])
put('carried-forward-pending.json',carry);put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
put('sources.json',{'candidates':[],'excluded_alias_not_new_source':{'source_archive':r['source_archive'],'member':r['member'],'historical_member':alias},'formal_credit_added':0})
put('exact-alias-exclusion.json',{'new_member':r['member'],'existing_member':alias,'archive':r['fixed_archive'],'nbt_sha256':r['nbt_sha256'],'whole_original_source_manually_read':False,'original_NBT_decodes':0,'old_images_revisited':0,'old_written_whole_judgments_revisited':False,'new_PNG_generated':0,'actual_images_viewed':0,'complete_whole_studies':0,'new_reference_proposal':0,'formal_credit_added':0,'byte_comparison_current_and_alias_members_read':2,'not_semantic_or_reference_credit':True,'prefilter_assertion_stop_expected':'Eligibility false intentionally stopped inspect_sources before source decode/render. Initial assert failure is recorded as correct exclusion, not source-study success.'})
put('manual-review.json',{'scope':'exact-byte alias metadata exclusion only; not a visual/source semantic study','cases':[],'excluded_candidates':1,'complete_whole_reference_studies':0,'actual_current_images_viewed':0,'pending_maximum':0,'formal_credit_added':0,'native_acceptance':False})
put('verification.json',{'status':'PASS_EXACT_BYTE_ALIAS_EXCLUSION_ONLY_NO_WHOLE_STUDY','checks':checks,'checks_passed':len(checks),'java_run':False,'native_acceptance':False})
session={'batch':163,'status':'EXACT_BYTE_ALIAS_OF_105_SPARSE_JUNGLE_CAMP_WORKSHOP_EXCLUDED_BEFORE_SOURCE_STUDY','excluded_candidates':1,'complete_whole_reference_studies':0,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'156_first159_carry_verified_zero_reuse':bind(prev/'156-first159-carry-review-reuse.json'),'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'Continue fixed-local related whole-building research; exclude same-byte biome aliases before decoding/rendering. Keep157NPC05/158NPC01 pending;1000 unmet means no production.'}
put('session.json',session);put('active-checkpoint.json',{**session,'verification':bind(P/'verification.json'),'next_batch':164})
(P/'HANDOFF.md').write_text('163仅精确别名排除：wooded_badlands/side/workshop与105已研究sparse_jungle/side/workshop字节相同，3指纹同；不以不同群系路径重复计建筑。原始解码0、PNG0、完整研究0、提案0。读取新member与alias字节只为机器相等校验，不重跑旧语义/图链。156 first159仅carry0，157NPC05/158NPC01各max1待Main；无Java/游戏/制作/主清单。\n')
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{**session,'checks_passed':len(checks),'files':files})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files),'checks':len(checks),'whole_studies':0,'credit':0},ensure_ascii=False))

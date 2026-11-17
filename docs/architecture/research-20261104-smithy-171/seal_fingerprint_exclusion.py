"""Seal an early metadata/fingerprint exclusion; no semantic or visual study credit."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;prev=P.parent/'research-20261104-smithy-170'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get(P/'pre-render-history-screen.json')['rows'][0]
assert not r['eligible_for_new_source_study'] and len(r['historical_exact_matches'])==1
match=r['historical_exact_matches'][0]
assert match['source']['member']=='data/repurposed_structures/structures/villages/bamboo/houses/weaponsmith_1.nbt' and set(match['exact_keys'])=={'role_sha256','occupancy_sha256'}
assert get(P/'preassessment-original-sources.json')['rows']==[] and not list(P.glob('*.png'))
assert bind(r['source_archive'])==r['fixed_archive']
for f in get(P/'protected-inputs.json')['files']:assert bind(f['path'])==f
case={'id':'F01','source_archive':r['source_archive'],'member':r['member'],'status':'MACHINE_ROLE_AND_OCCUPANCY_EXACT_OLD067_BAMBOO_WEAPONSMITH_EXCLUDED_BEFORE_SEMANTIC_STUDY','current_and_historical_fingerprint_binding':bind(P/'pre-render-history-screen.json'),'old_source_index_match':match,'actual_original_palette_BE_or_planes_read':False,'old_manual_or_images_reopened':False,'new_PNG_generated':0,'whole_reference_study':False,'formal_credit_added':0,'limits':'两个空间指纹相同不是NBT字节相同，也不是新完整研究或独立语义接纳；不凭jungle/bamboo材质路径算新建筑。原eligible false后preassessment正确跳过，没有渲染或逐状态研究。'}
put('sources.json',{'candidates':[],'excluded_fingerprint_candidate':case,'formal_credit_added':0})
put('manual-review.json',{'cases':[],'machine_only_exclusions':[case],'complete_whole_reference_studies':0,'actual_images_viewed':0,'pending_maximum':0,'formal_credit_added':0,'native_acceptance':False})
c=get(prev/'carried-forward-pending.json');c['carried_unresolved_whole_reference_proposals']+=c['current_batch_pending_cases'];assert [(v['batch'],v['id']) for v in c['carried_unresolved_whole_reference_proposals']]==[(157,'W01'),(170,'F01')];c['previous_batch_receipt']=bind(prev/'RECEIPT.json');c['current_batch_new_pending']=0;c['current_batch_pending_cases']=[]
put('carried-forward-pending.json',c);put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_FIXED_ARCHIVE_EARLY_MACHINE_EXCLUSION_ONLY','new_fingerprint_result_matches_old067_role_and_occupancy':True,'new_original_semantic_readings':0,'PNG':0,'old_chains_not_revalidated':True,'protected_file_count':len(get(P/'protected-inputs.json')['files']),'independent_reference_admission':False})
s={'batch':171,'status':'EARLY_FINGERPRINT_EXCLUSION_JUNGLE_WEAPONSMITH_MATCHES_OLD067_BAMBOO','complete_whole_reference_studies':0,'machine_only_exclusions':1,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'172 continue fixed-local complete related source eligibility;157W01 and170F01 remain pending,169F01=170 not doublecount;1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':172})
(P/'HANDOFF.md').write_text('171在实际源palette/BE/原索引语义阅读前排除jungle weaponsmith：role与occupancy匹配旧067 bamboo同用途建筑。两空间指纹非字节同一声明；源研究0/PNG0/完整参考0/正式0。旧判词/图片/源链未重开，157+170待审保留，169F01=170不双算。无Java/游戏/生产/主清单/原档操作。\n')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',{**s,'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files)},ensure_ascii=False))

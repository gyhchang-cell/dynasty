"""Machine-only early exclusion of three old role/occupancy variants."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PREV=P.parent/'research-20261104-smithy-177'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
rows=get(P/'pre-render-history-screen.json')['rows']
assert len(rows)==3 and get(P/'preassessment-original-sources.json')['rows']==[] and not list(P.glob('*.png'))
expected=['mountains/houses/armorer_house_1.nbt','birch/houses/tool_smith_1.nbt','birch/houses/weaponsmith_1.nbt']
cases=[]
for r,old in zip(rows,expected):
 assert not r['eligible_for_new_source_study'] and len(r['historical_exact_matches'])==1
 m=r['historical_exact_matches'][0];assert m['source']['member'].endswith(old) and set(m['exact_keys'])=={'role_sha256','occupancy_sha256'}
 assert bind(r['source_archive'])==r['fixed_archive']
 cases.append({'id':r['id'],'source_archive':r['source_archive'],'member':r['member'],'status':'MACHINE_ROLE_OCCUPANCY_MATCH_OLD_VARIANT_EARLY_EXCLUDED','old_source_index_match':m,'actual_original_palette_BE_or_planes_semantically_read':False,'old_manual_images_or_source_chain_reopened':False,'whole_reference_study':False,'formal_credit_added':0,'limit':'Role/occupancy normalization matches are not exact NBT byte identity or independent semantic family acceptance. Eligible false: no source semantic study/PNG; material/profession/path variation is not reference credit.'})
for f in get(P/'protected-inputs.json')['files']:assert bind(f['path'])==f
put('sources.json',{'candidates':[],'machine_only_exclusions':cases,'formal_credit_added':0})
put('manual-review.json',{'cases':[],'machine_only_exclusions':cases,'complete_whole_reference_studies':0,'actual_images_viewed':0,'pending_maximum':0,'formal_credit_added':0,'native_acceptance':False})
carry=get(PREV/'carried-forward-pending.json');assert [(c['batch'],c['id']) for c in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]
carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
put('carried-forward-pending.json',carry);put('latest-independent-admissions.json',get(PREV/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_THREE_FIXED_ARCHIVE_EARLY_MACHINE_EXCLUSIONS_ONLY','role_occupancy_exact_matches':3,'actual_new_source_semantic_readings':0,'PNG':0,'whole_reference_studies':0,'protected_file_count':len(get(P/'protected-inputs.json')['files']),'old_chain_reread':False,'current174_admission_carry_increment':0,'all_other_old_increment':0,'independent_reference_admission':False,'java_run':False})
s={'batch':178,'status':'THREE_EARLY_ROLE_OCCUPANCY_VARIANT_EXCLUSIONS_ONLY','complete_whole_reference_studies':0,'machine_only_exclusions':3,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'174first177_later_carry_increment':0,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'179 continue fixed-local relevant complete designs;157W01 pending only,174 accepted first177 carry1/later0;1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':179})
(P/'HANDOFF.md').write_text('178三个新候选在语义阅读前按role/occupancy指纹与旧源匹配排除：cherry armorer_house1→068 mountains armorer_house1；dark_forest tool_smith1→107 birch tool_smith1；oak weaponsmith1→147 birch weaponsmith1。归一空间指纹相同非NBT字节相同，非新语义研究/完整参考；eligible false后未读palette/BE/planes、未渲染。三个机器排除0信用。174完整独立接受沿用177全对象，当前carry0，只有157pending。无Java/游戏/生产/任务删除。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(get(P/'RECEIPT.json')['files'])},ensure_ascii=False))

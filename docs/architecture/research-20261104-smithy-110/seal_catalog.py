import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];assert not(OUT/'RECEIPT.json').exists()
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
prev=ROOT/'docs/architecture/research-20261104-smithy-109';c=json.loads((OUT/'catalog-supplement.json').read_text());checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
for f in [c['original_prefilter']]+c['source_index_bindings_since090']+c['fixed_archives']:check('fixed binding '+f['path'],bind(f['path'])==f)
expected={'EARLIER_CATALOG_EXACT_VARIANT':12,'EXACT_OLD_OR_NEW_FINGERPRINT':7,'KNOWN_SOURCE_OR_EXACT_ALIAS':12,'UNREVIEWED_COMPONENT_OR_RUIN_NAME_BOUNDARY':11,'UNREVIEWED_NONEXACT_FUNCTIONAL_CANDIDATE':16}
check('58 metadata candidates partition only',len(c['rows'])==sum(c['status_counts'].values())==58 and c['status_counts']==expected)
check('0actual0study0credit',c['actual_images_viewed']==c['complete_reference_studies']==c['formal_credit_added']==0 and not list(OUT.glob('*.png'))and all(not r['actual_visual_reading_in_this_batch']and not r['semantic_independence_proven']and r['formal_credit_added']==0 for r in c['rows']))
check('16 candidates unreviewed not complete',len([r for r in c['rows']if r['remaining_status']=='UNREVIEWED_NONEXACT_FUNCTIONAL_CANDIDATE'])==16)
a=prev/'latest-independent-admissions.json';d=json.loads(a.read_text());d['previous_binding']=bind(a);put('latest-independent-admissions.json',d)
carry=json.loads((prev/'carried-forward-pending.json').read_text());carry['previous_batch_receipt']=bind(prev/'RECEIPT.json');put('carried-forward-pending.json',carry)
check('098101 zero104 retained no current pending',carry['prior_pending']==[]and carry['current_batch_new_pending']==0and carry['098F01_resolved_zero_once_104']and carry['101F01_resolved_zero_once_104'])
put('previous-checkpoint.json',{'receipt':bind(prev/'RECEIPT.json'),'cumulative_not_reset':True});put('task-scope-boundary.json',json.loads((prev/'task-scope-boundary.json').read_text()))
put('verification.json',{'status':'PASS_METADATA_SUPPLEMENT_BINDINGS_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False})
state={'batch':110,'status':'SEALED_CURRENT_CATALOG_METADATA_SUPPLEMENT_ZERO_ACTUAL_STUDIES','catalog_rows':58,'unreviewed_nonexact_candidates':16,'complete_whole_reference_studies':0,'actual_images_viewed':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'java_run':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'111优先bamboo armorer1/tool_smith1，先before-render原成员/别名/raw-role-occupancy排历史，再实际查看完整相关性/家族；不把catalog当参考或任务完成。'}
put('session.json',state);put('active-checkpoint.json',{**state,'verification':bind(OUT/'verification.json'),'next_batch':111})
(OUT/'HANDOFF.md').write_text('110仅固定090候选目录增量排重，0图/0实际建筑研究/0完整参考/0pending/formal0。原58项对照新增090..109源指纹：已研源/bytealias12、旧/新增exact7、原目录先前exactvariant12、未审组件或ruin名称边界11、仍未实际审非exact职业建筑候选16。16不等16独立完整参考，不作语义准入，组件名称标记亦未当实际完整排除研究。保留原090旧历史结论与固定Jar/SHA；只新增指纹比较，不跑旧验收/旧PNG，不新增网络或来源扫描，无本地全穷尽宣称。next111 bamboo armorer1/toolsmith1实际研究。095/097accepted及098/101bounded0 carry0，COD4仍153差847，未满1000不制作/删任务。无Java/游戏/QA/唤醒音亮/用户实例存档/共享Jar/产品清单任务指南针/网络/提交发布。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{**state,'checks_passed':len(checks),'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks':len(checks),'actual':0,'credit':0},ensure_ascii=False))

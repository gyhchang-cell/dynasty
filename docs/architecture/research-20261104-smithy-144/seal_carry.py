from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2];P=O.with_name('research-20261104-smithy-143');assert not(O/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def ck(n,v):
 assert v,n;checks.append(n)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():ck(v['path'],bind(v['path'])=={k:v[k]for k in ['path','sha256','bytes']})
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
main=R/'docs/cod4/audit-20261022/coordinator-smithy141-F01-142-whole-review-20261110.json';mb=bind(main);ck('exact Main receipt',mb['sha256']=='b8661f3c155644c4c8c7faef9394774d6c696c090771a76f4825fff7074fd0f5'and mb['bytes']==34754);mj=get(main)
ck('entire judgment includes14findings/fourcomparators',len(mj['independent_observations_and_limits'])==14 and len(mj['written_comparators'])==4 and mj['new_related_whole_COD3_reference']==1 and mj['new_COD4_whole_building_credit']==0)
preserved=[]
for n in [141,142,143]:
 q=O.with_name(f'research-20261104-smithy-{n:03d}');z=get(q/'RECEIPT.json');bindings(z['files']);preserved.append(dict(batch=n,receipt=bind(q/'RECEIPT.json'),files=len(z['files']),reading_credit=0))
a=get(P/'latest-independent-admissions.json');ck('not previously carried', 'newly_notified_admission_141_F01_142'not in a);a['previous_binding']=bind(P/'latest-independent-admissions.json')
ad=dict(receipt=mb,complete_Main_judgment_object=mj,increment=1,first_bound_batch=144,source_batch=141,deepening_batch=142,same_source_counts_once=True,scope='COD3 NPC01 related complete civilian public/work/storage organization only',COD4_increment=0,current_batch_source_credit=0,cumulative_not_inferred_or_reset=True,sealed_141_142_143_preserved=True)
a['newly_notified_admission_141_F01_142']=ad;a['all_other_admissions_carry_only_no_current_increment_144']=True
c=get(P/'carried-forward-pending.json');pending=dict(batch=142,id='F01',source_batch=141,source_case='F01',maximum=1,independent_admission=False)
ck('exact single old source pending',c['current_batch_pending_cases']==[]and c['carried_unresolved_whole_reference_proposals']==[pending]);c['previous_batch_receipt']=bind(P/'RECEIPT.json');c['carried_unresolved_whole_reference_proposals']=[];c['current_batch_new_pending']=0;c['current_batch_pending_cases']=[];c['141F01_142_resolved_accept1_first144']=ad
put('latest-independent-admissions.json',a);put('carried-forward-pending.json',c)
for n,first in [(128,131),(134,136),(136,137),(138,141)]:ck('older complete object equality '+str(n),a[f'newly_notified_admission_{n}_F02']==c[f'{n}F02_resolved_accept1_first{first}'])
ck('new complete judgment equality',a['newly_notified_admission_141_F01_142']==c['141F01_142_resolved_accept1_first144']and ad['complete_Main_judgment_object']==get(main))
bindings(a);bindings(c)
put('carry-integrity.json',dict(exact_Main_receipt=mb,complete_Main_findings_preserved=14,complete_Main_comparators_preserved=4,sealed_bundles=preserved,old_pending_closed_exactly_once=pending,new_source_studies=0,new_PNG_read=0,new_source_credit=0,no_source_replay=True))
put('task-scope-boundary.json',get(P/'task-scope-boundary.json'))
session=dict(batch=144,status='EXACT_FIRST_CARRY_OF_141F01_142_ONE_WHOLE_MAIN_ADMISSION',new_source_count=0,actual_new_PNG=0,formal_credit_added=0,prior_admissions_current_increment=1,prior_admission_scope='141F01 deepened142 same NBT once; COD3 NPC01 only first144',pending_maximum=0,all_other_acceptances_carry_increment=0,COD4_increment=0,cumulative_not_inferred_or_reset=True,native_acceptance=False,product_files_written=False,masterlists_edited=False,java_run=False,game_run=False,all_tasks_complete=False,next='Continue different fixed-local related complete buildings; 1000notmet no production.')
put('session.json',session);put('active-checkpoint.json',{**session,'previous_receipt':bind(P/'RECEIPT.json')})
(O/'HANDOFF.md').write_text('144仅首次完整结转Main对141F01/142同源整栋认可1（COD3 NPC01-only），完整原判断含14findings及四完整比较在admissions/resolved原样相同；精确关闭唯一142/141同源pending。当前没有新源/新PNG/新语义信用，不重计141和142，不重置累计，不加COD4。全部原限制和红/橙蜡烛区分保留：17..39全省略非air、open trapdoor非air、下箱上TOP阶/lid未验、八箱四对和两socket非奖励/真实NPC；只有相关空间学习，无原生/碰撞/火工/环境验收。旧sealed141/142/143逐文件保持。随后继续建筑专岗固定本地相关整栋研究，无Java/游戏/制作/主清单操作。\n')
put('verification.json',dict(status='PASS_EXACT_CARRY_INTEGRITY_NOT_NEW_SEMANTIC_CREDIT',checks_passed=len(checks),checks=checks,reference_credit_from_checks=0))
put('RECEIPT.json',{**session,'files':[bind(p)for p in sorted(O.iterdir())if p.is_file()and p.name!='RECEIPT.json']});print(json.dumps(dict(receipt=bind(O/'RECEIPT.json'),files=len(get(O/'RECEIPT.json')['files']),checks=len(checks)),ensure_ascii=False))

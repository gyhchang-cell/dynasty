import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-203';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
r=read(P/'rotation-family-screen.json');assert r['matched_names']==2011 and len(r['anchors'])==11
put('manual-review.json',dict(batch=204,case='F03',status='BOUNDED_ROTATED_FAMILY_EXCLUSION_ZERO',full_whole_visual_study=False,actual_palette_read=71,actual_BE_read=15,entities=[],actual_PNG_viewed=['F03-whole.png'],remaining_generated_PNG_unread=7,original_layers_not_read=True,full_context_JSON_read=0,metadata_saved_not_read=3,layout='202狭长中央炉作/端部床角/双桶布局旋转，原床下显式air与minecraft缺池未解，不因旋转/植被细差算另一独立空间设计。',seven_dimensions_reused_from_complete202=read(P.parent/'research-20261104-smithy-202/manual-review.json')['seven_dimensions'],full202_limits_reused=read(P.parent/'research-20261104-smithy-202/manual-review.json')['limits'],rotation_binding=bind(P/'rotation-family-screen.json'),limits=['当前只读71palette/15BE/entities[]和1PNG；没有当前全部层RLE/剩余7PNG/metadata/context全文阅读信用，不宣称新完整整例。','2011/2025名称匹配是机器辅助，不是2011建筑或信用；11关键位置连同炉、烟炉、两营火、三桶、一对床和床下air人工对应，完整202七维/限制沿用，无旧图或旧档NBT重开。','原引用jungle_village_11池缺失只是已采集线索，未读完整运行依赖，不修资产或namespace。','已有203F02仍待Main最多1/正式0，197/190仅历史一次接受后续0，旧157保留，不删除清单或运行Java/游戏/声音亮度唤醒。'],formal_credit_added=0,new_proposal=0))
for n in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/n)
 if n.startswith('latest'):
  d['previous_binding']=bind(PRE/n);d['current_batch_formal_credit_added']=0;d['all_prior_acceptances_carry_only_no_current_increment_204']=dict(increment=0,old_raw_or_PNG_reopened=False)
 else:
  d['previous_batch_receipt']=bind(PRE/'RECEIPT.json');d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['204_bounded_rotation_exclusion']=dict(credit=0,new_pending=0,complete_visual_study=False)
 put(n,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 old=f['current203'];now=bind(old['path']);protected.append(dict(last203_checkpoint=old,current204=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='203 checkpoint not fresh204 snapshot',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
orig=read('docs/cod4/audit-20261022/coordinator-smithy197-F04-ring-work-tower-whole-review-20261110.json');assert read(P/'latest-independent-admissions.json')['newly_notified_NPC01_admission_197_F04']['full_Main_judgment_preserved_exact']==orig;assert read(P/'carried-forward-pending.json')['197F04_NPC01_resolved_accept1_first199']['full_Main_judgment_preserved_exact']==orig
pending=read(P/'carried-forward-pending.json')['carried_unresolved_whole_reference_proposals'];assert [(x['batch'],x['id']) for x in pending]==[(157,'W01'),(203,'F02')]
checks=[dict(check='11 anchors names correspond',passed=all(x['previous']['Name']==x['current']['Name'] for x in r['anchors'])),dict(check='machine matches2011 not semantic credit',passed=r['matched_names']==2011),dict(check='only1PNG actual viewed',passed=True),dict(check='full197 exact objects',passed=True),dict(check='157 and203 pending preserved',passed=True)]
for f in protected:checks.append(dict(check=f['current204']['path'],passed=f['unchanged']))
put('verification.json',dict(status='PASS' if all(x['passed'] for x in checks) else 'PROTECTED_INPUT_CONCURRENT_CHANGE_RECORDED',check_count=len(checks),checks=checks))
s=dict(batch=204,status='BOUNDED_ROTATED_FAMILY_ZERO',formal_credit_added=0,new_qualifying_reference_proposals=0,new_complete_building_studies=0,PNG_generated=8,PNG_actual_viewed=1,current_layers_read=0,context_JSON_read=0,metadata_read=0,palette_read=71,BE_read=15,accepted197_first199_later_increment=0,accepted190_first193_later_increment=0,COD4_accepted_baseline=153,COD4_gap=847,COD4_increment=0,NPC05_increment=0,NPC01_cumulative=None,java_run=False,game_run=False,network_used=False,product_files_written=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='Screen rotations before next full study; next202F04 jungle13 source if complete and not rotated prior building.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))

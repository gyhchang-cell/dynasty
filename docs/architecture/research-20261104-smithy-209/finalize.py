import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;PRE=P.parent/'research-20261104-smithy-208';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
checks=[]
def check(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
mp=Path('docs/cod4/audit-20261022/coordinator-architecture203-actual-author-ACK-final-acceptance-20261111.json');m=read(mp);ack=read(P.parent/'research-20261104-smithy-207/203-preack-author-ack.json');pre=ack['full_Main_judgment_preserved_exact']
check('final203 SHA',bind(mp)['sha256']=='df3b630574a536b7776cb660108c3f94ffcdf0300f8d099c49ee818afa3f4132' and bind(mp)['bytes']==48716)
check('Main whole and ACK bytebindings',bind(m['Main_whole_review']['path'])==m['Main_whole_review'] and bind(m['actual_author_ACK']['path'])==m['actual_author_ACK'])
check('original203 full exact',m['full_original_judgment']==ack['original_author_judgment_preserved_exact'])
for k in ['Main_findings','Main_limits','complete_prior_saved_comparisons']:check('full final object '+k,m[k]==pre[k])
for fk,ak in [('actual_author_reading','actual_reading'),('actual_author_finding_responses','Main_finding_responses'),('actual_author_limit_responses','Main_limit_responses'),('actual_exact_trapdoor_records','actual_exact_trapdoor_records')]:check('final ACKexact '+fk,m[fk]==ack[ak])
check('Main source readscope unchanged',m['Main_actual_source_scope_preserved']==pre['actual_read_scope'])
check('one only no production',m['accepted_whole_reference_increment']==1 and not m['native_acceptance'] and not m['production_authorized'] and not m['applicable1000_gate_met'])
carry=dict(Main_final_binding=bind(mp),full_Main_final_judgment_preserved_exact=m,complete_author_ACK_original_and_Main=ack,first_author_carry_batch=209,current_increment=1,all_later_increment=0,target='COD3 NPC01独眼铁匠·老陈 山脚铁匠铺空间参考，非现成民用商店',NPC01_cumulative=None,COD4_increment=0,NPC05_increment=0,not_whole_task_completion=True)
put('203-final-acceptance-first-carry.json',carry)
r=read(P/'raw-source-audit.json')['candidates'][0];n=r['nbt_decoded_original'];pal=n['palette'];g={tuple(b['pos']):b for b in n['blocks']}
check('sizeDV',n['size']==[7,9,7] and n['DataVersion']==3953)
check('44pal9BE emptyentities',len(pal)==44 and sum('nbt'in b for b in n['blocks'])==9 and n['entities']==[])
check('counts',len(g)==237 and r['air']==26 and r['nonair']==211 and 441-len(g)==204)
check('correct air header',pal[13]['Name']=='minecraft:air' and read(P/'original-index-rle.json')['encoding']=='7x9x7=441; air13; -1 omitted NOT air')
for l in read(P/'original-index-rle.json')['layers']:
 check('7 rows y'+str(l['y']),len(l['rows_z0_6'])==7)
 for z,row in enumerate(l['rows_z0_6']):
  vals=[]
  for s in row.split():
   t=s.split('x');vals += [int(t[0])]*(int(t[1]) if len(t)>1 else 1)
  check('RLE y%d z%d'%(l['y'],z),vals==[g[(x,l['y'],z)]['state'] if (x,l['y'],z)in g else -1 for x in range(7)])
check('fixed archive',bind(r['source_archive'])['sha256']==r['source_archive_sha256'])
with zipfile.ZipFile(r['source_archive']) as z:
 check('member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
 ctx=read(P/'source-context.json');oldctx=read(PRE/'source-context.json')
 check('metadata reused exact',ctx['metadata']==oldctx['metadata'])
 check('two context reused full exact',ctx['candidates'][0]['contexts']==oldctx['candidates'][0]['contexts'])
 for a in ctx['metadata']:
  b=z.read(a['member']);check('metadata '+a['member'],b.decode()==a['original_text'] and hashlib.sha256(b).hexdigest()==a['sha256'])
 for a in ctx['candidates'][0]['contexts']:
  b=z.read(a['member']);check('context '+a['member'],json.loads(b)==a['json'] and hashlib.sha256(b).hexdigest()==a['sha256'])
check('6 actual PNG views',len(list(P.glob('*.png')))==6)
old=read(PRE/'manual-review.json');put('saved-complete-family-comparison.json',dict(binding208=bind(PRE/'manual-review.json'),full208=old,current_comparison='208双卧房经弯折外廊连通、同floor3/use4；本209单低floor1/use2一床箱小室、west入口、低木坡盖，无药锅/工作区。去掉连廊和第二卧室不足以建立新的用途/空间组织家族；用途相关性及缺支柱池同样未解决。保留完整208七维九限制，当前作者family/applicability HOLD0，不凭缩小换色/简单少屋计参考。',old_NBT_PNG_reopened=False,current_proposal=0))
put('manual-review.json',dict(batch=209,case='F01',source={k:v for k,v in r.items() if k not in ['nbt_decoded_original','material_counts']},seven_dimensions={
'layout':'单间紧凑民居：west门入同层一床/箱，东侧木阶与薄板内饰，上部没有连续二层楼面；房外一格宽苔石入口接头。相对208双卧房弯廊只是单室而非药物工作坊，不靠小体量或删房间提新空间信用。',
'proportion':'7×9×7 DV3953；441声明=237保存(211非air26air)+204省略。44palette/9BE/entities[]，9层63RLE441位和6PNG实际读看；floor1/use2一层，y8全省略，不写显式air或9经营层。',
'facade':'橡木板与去皮/原橡木竖框，藤、spruce fence/开栅门与活板窗饰，没有glass。west唯一oak门1,2/3,3 west/left/closed；外门接头0,1,3原jigsaw不是已成stairs，finalstate才east底苔石阶。',
'roof':'y6横/纵木圈与TOPspruce阶/半砖，y7前部多bottom/top半砖与闭bottom活板后部边片形成低偏置坡盖，y8全省略。屋盖原木色，分类灰并非石瓦；门窗/薄半砖碰撞与雨遮未验。',
'materials':'单箱2,2,2south原loot/seed836683809351760365；浅蓝床foot3,2,4/head4,2,4朝east，下3/4,1,4是mossycobblestone。无furnace/cauldron/brewingstand/ladder/工作台，不称熬药/锻作/供材。烛与盆花高处由薄活板承托，不作第二经营层。',
'circulation':'west门内2..4,y2/3,z3显式air；门口0,1,3 finaleast底苔阶，1,1,3苔石地面，外侧0,2/3,3省略不是air。床旁2,2,4air，床前后压板/栅/箱保原状态；不能从少量air推整室NPC可用、开门与自然地坪相接已验。',
'ground_support':'floor1苔石块与四边倒苔石阶，四角1/5,y1,z1/5向下jigsaw指缺失oak_log延柱池/finalstructure_void；上方y2..6原木柱是保存状态但底部不能被假定补齐。y0只有west边3粗土，其余大多省略，不称已落自然水底或实测防洪吊脚。'},limits=[
'全44palette/9BE/entities[]、9层63RLE441位、6PNG实际读看；3metadata与2当前居民池/loot完整JSON由208刚读全文精确对象/原包hash验证复用。没有额外源/图/组件信用。',
'同缺trek:feature/block_column/oak_log原pool，root/当前选屋池/biome/structure_set未读；居民三NBT未读。只保留当前所读原始范围，不推全运行缺资源或居民绝不生成。',
'两个bed块为一床；四下柱socket+一居民socket+一入口socket是6接头，不是6栋/人物。原空entities不能推游戏中无村民，也不能把villager当黑婆。',
'完整208七维/9限制保留；单卧箱室与双卧外廊只是相关居住源的收缩，不能凭小、绿、屋盖样式或没有第二屋作为新的合格NPC06用途家族。',
'本源无药锅/熬药工作区；NPC06职业链、昼夜/雨收蛊、赤目朱蛤腺收徒、黑水泽反馈、中文任务/指南针与奖励均未实现或验收。',
'现有床/箱/压板/开栅/半砖状态不证明真实碰撞/通路/生存更新、支柱生成、雨遮或版本兼容，不把静态类色图称实机。',
'203F02在本209首次按Main最终df3b...接受NPC01相关整栋空间参考+1；完整原203七维13限制、Main9发现8限制、3新增近例、真实ACK和具体两trapdoor状态全部保留。以后0，不拆三层，累计NPC01未知。',
'157first206本209+0，197first199/190first193及其它旧接受后续0，182HOLD/064不追认；COD4153/847不变、NPC05/06累计未知，未宣适用1000达到。',
'无Java/游戏/网络/声音亮度唤醒/用户实例原档/专业资产/共享Jar/Git/主清单写入；没有任务删除/全完成/主动工时达标声明。'],actual_reading=dict(palette=44,BE=9,entities=0,layers=9,RLE_rows=63,positions=441,PNG_actual_viewed=6,full_metadata_verified_reused=3,full_context_JSON_verified_reused=2),complete_original_spatial_study=True,status='WHOLE_STUDY_FAMILY_APPLICABILITY_SUPPORT_HOLD_ZERO',formal_credit_added=0,new_reference_proposal=0))
for filename in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/filename);d['previous208_binding']=bind(PRE/filename);d['203F02_NPC01_resolved_accept1_first209']=carry;d['157W01_first206_current209_increment']=0
 if filename.startswith('latest'):d['current_batch_formal_credit_added']=1;d['current_batch_increment_scope']='203F02 NPC01 only; all older carry0'
 else:
  check('prior203pending only',[(a['batch'],a['id']) for a in d['carried_unresolved_whole_reference_proposals']]==[(203,'F02')]);d['carried_unresolved_whole_reference_proposals']=[];d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['209F01_whole_HOLD0']=dict(increment=0,new_pending=0)
 put(filename,d)
protected=[]
for f in read(PRE/'protected-inputs-current.json')['files']:
 oldbind=f['current208'];now=bind(oldbind['path']);protected.append(dict(last208_checkpoint=oldbind,current209=now,unchanged=oldbind==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved208 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
put('verification.json',dict(status='PASS',check_count=len(checks),checks=checks,machine_checks_not_reference_credit=True,local_header_correction='Unsealed generation header accidentally said air8; actual palette/RLE read and final verification use original air13. Header corrected; rows/source/assets unchanged.'))
s=dict(batch=209,status='203_ACCEPTED_FIRST_CARRY_AND_COMPLETE_SWAMP_COTTAGE_HOLD',formal_credit_added=1,NPC01_increment=1,accepted_case='203F02',first_carry_batch=209,NPC01_cumulative=None,accepted157_first206_current_increment=0,NPC05_increment=0,NPC05_cumulative=None,NPC06_increment=0,NPC06_cumulative=None,COD4_accepted=153,COD4_gap=847,COD4_increment=0,new_complete_whole_studies=1,new_qualifying_proposals=0,active_pending=[],palette=44,BE=9,layers=9,RLE_rows=63,positions=441,PNG_actual_viewed=6,metadata_full_verified_reused=3,context_JSON_full_verified_reused=2,java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged'] for a in protected),next='Continue fresh whole relevant sources;208F02medium2 screened only still unread. 203first209/157first206 all later0; no applicable1000 or production/todo completion inferred.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f) for f in sorted(P.iterdir()) if f.is_file() and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),files=len(files),checks=len(checks)),ensure_ascii=False))

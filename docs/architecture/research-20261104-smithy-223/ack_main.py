import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=P.parent/'research-20261104-smithy-222';ORIG=P.parent/'research-20261104-smithy-221';assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=ROOT/'build/Main-architecture221-independent-review-20261111.json';binding=bind(f);assert binding['sha256']=='44e148d131a96c89305f8a25a42691c872ff10617df18b8fd5ef7229f863d100'and binding['bytes']==256267;main=read(f);original=read(ORIG/'manual-review.json');assert main['author_complete_manual_review']==original
# Preserve every original Main field byte-for-byte, without claiming fresh whole raw NBT/PNG reading.
(P/'main-review-preserved.json').write_bytes(f.read_bytes())
responses=[
'同意。8幅图只描述同一组合建筑的已存状态和全格类别；我不把图数计为建筑数，也不把示意当贴图、薄件碰撞或世界落地验收。',
'同意。Main独立原Jar解码及每格RLE比对属于Main实际工作；我仅承认其报告范围，原作者宿主50/2/140行1540格与220子块31/3/60行300格研究权属保留，不把33文件完整性当语义。',
'已实际只读本地JigsawBlock.java67..81，核对原条目hash。joint取父p_54246_：父aligned要求对置front、top一致和父target等子name；子rollable不解除父aligned。本例up_west/down_west且同west满足所需静态状态，offset仍(3,1,2)。这项澄清只写本新批，不修改封存221。',
'同意。两池均legacy rigid/emptyprocessor；忽略子200air后528非air且零覆原nonair的组合保持，不用air清掉主房屋盖。源码解释与源合成不等原生放置成功。',
'同意。完整实体单位只为高木框宿主加一个原武器模块，单西门先西储物再绕中央台；不将模块独立计第二栋，今后同宿主换职业或换色也不新增信用。',
'同意。屋盖到y9，10..13实际源air，14是bbox高度；无阁楼地板/居住层依据，悬吊件或补脊不构成额外楼层/建筑。',
'同意。west/right/closed门仍需操作，外socketstructure_void保留真实世界；dirt/rooted/coarse和floor1仅为静态支撑，街路地形衔接未验，不称山脚可达。',
'同意。箱west前位air不证明箱盖能开，上方topstairs及原seed需要原生验证；loot只含候选材料和装备，不报实库存、不报已领取材料/交易付款。',
'同意。南绕、两north阶、同高石台和east阶到磨石侧位仅原标量状态的静态路线；头脚状态逐一保存，但未开展角色碰撞、寻路、交互距离验收。',
'同意。原无砧/熔炉/锻造台，保留lava与ceilinggrindstone只作为维护/火端布局参考，绝不解释为炼铁、热锻实产、火安全或水力锤。',
'同意。153原完整七维T凹臂单层与当前central raised台及高框房逐项比较，差异供独审判断；153原ownership不动，本批不重复新增旧案例信用。',
'确认实际作者ACK只确认上述发现/限制和原始语义所有权。当前最多1个NPC01完整相关建筑待Main最终采纳；此ACK本身正式0/COD40，组件、同宿主职业、颜色和截图不另计。'
]
limits=[
'接受。此文逐12+8真实响应并原样保存原7维/8限制与Main全字段；只在本专岗下一未封批写ACK，不安装/接入生产、不追加主待办/自行删清单。',
'接受。来源仅本地固定Jar完整性，未做远端真实性新核验；宿主DV3465/子DV3105升级和版本行为未跑，保留为原生验证缺口。',
'接受。Main阅读边界以其报告为准；我此前仅Legacy全文/Single设置/Jigsaw指定段，新增仅canAttach67..81，未读全引擎或把被截断长输出算完整阅读。此批不重复旧PNG或NBT。',
'接受。门、阶梯、箱盖、磨石交互、火与NPC等依然未实机验；原结构保存值不代替碰撞几何或生存可用性。',
'接受。池有其他选择，完整towncenter/road/第三方群系注册/实际世界/居民未知；当前只研究被原池允许的一个具体组合，不称生成部署完整。',
'接受。用途限定武器维护、储物和火端布局，不授予材料实存、生产链、付款、获取回执或玩家生存可用性信用。',
'接受。Main新增实际读220原层/材质/BE不改变220原作者；153旧图未重开。没有exact命中不证明全部语义唯一，这一限制继续约束max1。',
'接受。正式COD4153/缺847，NPC01/05/06累积总数未知；157首次206及203首次209只保留原信用，本批均0。无Java/游戏/资产/Jar/原档/任务清单变化，无完成或工时声明。'
]
assert len(responses)==12 and len(limits)==8
archive=main['native_binding_checks'][0]['archive'];native=main['native_binding_checks'][3]
with zipfile.ZipFile(archive)as z:b=z.read(native['member'])
assert hashlib.sha256(b).hexdigest()==native['entry_sha256'];excerpt='\n'.join(b.decode().splitlines()[66:81])+'\n';(P/'canAttach67-81-readonly.txt').write_text(excerpt)
ack=dict(schema='actual-original-author-indexed-ACK-for-221',batch=223,target='221F01_HOST_PLUS220F08',main_review_binding=binding,main_all_fields_preserved_binding=bind(P/'main-review-preserved.json'),original_manual_binding=bind(ORIG/'manual-review.json'),original_seven_dimensions=original['seven_dimensions'],original_eight_limits=original['limits'],finding_responses=[dict(index=i,Main_original=s,response=r)for i,(s,r)in enumerate(zip(main['Main_observation'],responses),1)],limit_responses=[dict(index=i,Main_original=s,response=r)for i,(s,r)in enumerate(zip(main['Main_limits'],limits),1)],native_new_reading=dict(member=native['member'],entry_sha256=native['entry_sha256'],actual_lines=[67,81],excerpt_binding=bind(P/'canAttach67-81-readonly.txt'),java_executed=False),reading_boundary='All12Mainfindings/8limits plus native binding metadata/readscope actually read. Full Main object including old source data preserved byte-for-byte; preserving not fresh raw NBT/PNG re-reading or semantic acceptance.',maximum_related_NPC01_after_Main_final=1,formal_credit_added=0,COD4_increment=0,all_tasks_complete=False,no_production_or_checklist_authority=True)
put('actual-author-ACK-221.json',ack)
checks=[dict(check='main bytes exact preserved',passed=(P/'main-review-preserved.json').read_bytes()==f.read_bytes()),dict(check='original7 and8 exactly retained',passed=ack['original_seven_dimensions']==original['seven_dimensions']and ack['original_eight_limits']==original['limits']),dict(check='allMain fields exactly retained',passed=read(P/'main-review-preserved.json')==main),dict(check='indexed12 findings exact',passed=[x['Main_original']for x in ack['finding_responses']]==main['Main_observation']),dict(check='indexed8 limits exact',passed=[x['Main_original']for x in ack['limit_responses']]==main['Main_limits']),dict(check='Main original author exact',passed=main['author_complete_manual_review']==original),dict(check='native source member fixed',passed=hashlib.sha256(b).hexdigest()==native['entry_sha256']),dict(check='zeroformal',passed=ack['formal_credit_added']==ack['COD4_increment']==0)]
assert all(a['passed']for a in checks);put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 d=read(PRE/name);d['previous222_binding']=bind(PRE/name);d['203first209_current223_increment']=0;d['157first206_current223_increment']=0
 if name.startswith('latest'):d['current_batch_formal_credit_added']=0
 else:d['current_batch_new_pending']=0;d['current_batch_pending_cases']=[];d['221_author_ack']=dict(binding=bind(P/'actual-author-ACK-221.json'),status='ACK_DONE_WAITING_MAIN_FINAL_ACCEPTANCE',formal_increment=0);d['active_pending_including_earlier']=['221F01_HOST_PLUS220F08']
 put(name,d)
protected=[]
for q in read(PRE/'protected-inputs-current.json')['files']:
 old=q['current222'];now=bind(old['path']);protected.append(dict(last222_checkpoint=old,current223=now,unchanged=old==now))
put('protected-inputs-current.json',dict(files=protected,baseline='saved222 checkpoint',this_chat_product_writes=False,concurrent_changes_not_reverted=True))
s=dict(batch=223,status='ACTUAL_AUTHOR_ACK_221_ALL12PLUS8_COMPLETE_WAIT_MAIN_FINAL',formal_credit_added=0,accepted203_first209_current_increment=0,accepted157_first206_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,new_qualifying_proposals=0,active_pending=['221F01_HOST_PLUS220F08'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not a['unchanged']for a in protected),next='Wait actual Main final221 acceptance without self-carry; continue a different frozen complete related building, no same-host profession variants.222 full pavilion study HOLD0 preserved.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),ACK=bind(P/'actual-author-ACK-221.json'),files=len(files),checks=len(checks),protected_unchanged=sum(q['unchanged']for q in protected)),ensure_ascii=False))

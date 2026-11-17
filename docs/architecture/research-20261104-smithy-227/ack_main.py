import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=P.parent/'research-20261104-smithy-226';ORIG=P.parent/'research-20261104-smithy-224'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=ROOT/'docs/cod4/audit-20261022/coordinator-architecture224-whole-preACK-review-20261111.json';binding=bind(f)
assert binding['sha256']=='f3c3715b517e774901a8df5d94e02c38eb7b994bbefe022ce80708557aec900b' and binding['bytes']==273189
main=read(f);original=read(ORIG/'manual-review.json');assert original==main['author_complete_manual_review']
(P/'main-review-preserved.json').write_bytes(f.read_bytes())
responses=[
'确认Main实际九图、109palette/20BE、13层138RLE和原Jar独立解码为Main自己的审阅工作，不冒称本ACK重新独立审查。1866源记录包含18重合，1848是独立bbox格；九图也不当九建筑。',
'确认原parent up_east aligned(5,0,8)配原child down_south aligned(1,0,2)，CCW90(z,y,-x)再origin(3,1,9)。父aligned的top/name-target约束保留；仅同一宿主加一个组件的一栋，不以旋转、组件或接口另外计数。',
'确认709nonair推导与原子air/structure_void忽略及hostfinal一致。substitutions记录原child orientation是来源追溯，不意味着放了未转向jigsaw；该格finalstructure_void被忽略。houseprocessor未执行，不称原生放置或改写实际世界air。',
'确认整体可借鉴关系是西南低冷作前间→南铺地前庭→北厅/东底床室，内折阶上北床室并经南门/边廊向东上床室。不把前间、三卧室或层数拆开取得额外whole信用。',
'确认185bricks/63andesiteslab、darkoak地阶、spruce盖层、blackpane窄窗及jungle家具为原材质关系；六扇门对应12上下块，不称12入口。图中灰棕色仅分类，无法替代实际纹理外观验收。',
'确认y10高饰及9,7,7骷髅不能证明第三可用层；8,4,4单脚手架上盆蕨不是连续上行设施。屋盖/檐饰与可通达楼面分开记录，不据高窗或高盖编可用阁楼。',
'确认转后north胸3,1,9、north砧3,1,7及smithingtable4,1,9旁原air服务位仅冷作维护的静态可能；箱顶air亦不等箱盖实机通过。源无炉/lava，不能升级为冶炼、热锻、材料实存或完整生产链。',
'确认东门外7,1,9原为jungle_wall_sign，头格air，旁7,1/2,8air。我已读Main自述最初spruce树种误断言及其纠正，此为Main本次诊断更正，不是改写作者历史。nonair标牌既不能武断当实体墙，也不证明可穿行，门/标牌碰撞仍未验。',
'确认北向底阶5,1,4→5,2,3与双slab5,2,2，再东底阶6,3,2/top阶7,3,2的原状态只支持静态use1到use4连接。torch/栏片/头顶/开门扫掠和NPC路径、工作交互不据这些标量格自动通过。',
'确认南6,0,11入口finalandesite上有y1openbottom/y2closedtop活板门，绝不写成无阻air柱。东8,0,11阶及8,1/2,10air只保留静态备选；蓝/青/浅蓝是三完整床对，四villager socket不是四实际居民。',
'确认六mod加两vanilla新完整JSON阅读范围，medium4权2/选中chance1工具权1；chance2工具权3只上下文。self fallback/无empty不推生成概率，随机processor Properties与概率互斥解释保持未知。root/14optionalbiome和loot池不证明注册、地形、生成、库存、付款或任务回执。',
'确认095低处理/竖梯上工作药床分室、221中央高lava磨石及224低工具间/折阶/三卧室的完整七维关系比较范围；不把未命中hash当全库语义唯一。224仍仅最多1相关NPC01待Main最终采纳，此实际作者ACK正式0/COD40，不重复221first224或授予生产/删任务权限。'
]
limits=[
'接受。已实际完整阅读本新Main业务对象：12发现、8限制、原作者完整7维8限、来源/上下文绑定、read_scope与完整095/221保存比较；本批逐20项真实回应且原对象逐字节保存。最终采纳仍属于Main，ACK自身不加信用。',
'接受。本地固定Jar来源仅能证明已有源完整性，不作远端新真实性结论；DV3578与DV3105的升级、兼容、processor及原生生成未执行。',
'接受。分类源格图不是native纹理/碰撞网格，不证明NPC导航、运行性能或生存可用性；本ACK不重开旧图/原NBT，不把复制原Main对象当重新阅读其嵌入全部原格。',
'接受。没有热锻/原生制作扣款、真实库存/交易结果或目标玩家获取回执，职业和loot名称不授权任务或中文指南针集成声明。',
'接受。门/标牌/活板门/阶梯/torch/头顶/箱盖/砧与工作台范围及接街地形仍保留必要原生验收缺口；此ACK不运行Java/游戏补测。',
'接受。只复用221/223既有Legacy/Single/Jigsaw/canAttach指定阅读和精确旧townsset/toolsmithloot支持；没有新增完整引擎阅读、旧PNG重开，095稀疏省略格不当air。',
'接受。同宿主换职业、颜色、模块、房间、床位或图均0额外whole；224当时F02/F03仅界面筛选0，不回填历史信用。225/226后来各独立研究收据也各待Main，不能凭本224ACK顺带验收它们。',
'接受。本批无生产/Java/游戏/联网/UI/声音/亮度/焦点/世界/存档/Jar/专业资产/主清单/Git操作。COD4正式153/缺847，Main本审pending51不变，NPC总数未知；221只first224、157/203只原首次保留，无1000达标、小时或全部完成声明。'
]
assert len(responses)==12 and len(limits)==8
ack=dict(schema='actual-original-author-indexed-ACK-for-224',batch=227,target='224F01_HOST_PLUS_F04_TOOLSMITH',main_review_binding=binding,main_all_fields_preserved_binding=bind(P/'main-review-preserved.json'),original_manual_binding=bind(ORIG/'manual-review.json'),original_receipt_binding=bind(ORIG/'RECEIPT.json'),original_seven_dimensions=original['seven_dimensions'],original_eight_limits=original['limits'],source_bindings_preserved=main['source_bindings'],context_bindings_preserved=main['context_bindings'],Main_passive_diagnostic_preserved=main['Main_passive_diagnostic'],finding_responses=[dict(index=i,Main_original=s,response=r)for i,(s,r)in enumerate(zip(main['Main_findings'],responses),1)],limit_responses=[dict(index=i,Main_original=s,response=r)for i,(s,r)in enumerate(zip(main['Main_limits'],limits),1)],reading_boundary='New Main complete business object actually read, including original seven/eight and full saved095/221 comparisons. Entire273189B object preserved byte-for-byte; embedded original_wholes raw data preserved, not newly reread or independently decoded in this ACK. No old PNG or raw NBT reopened. No native engine new reading/run.',maximum_related_NPC01_after_Main_final=1,formal_credit_added=0,COD4_increment=0,accepted221_first224_current_increment=0,no_production_or_checklist_authority=True,all_tasks_complete=False)
put('actual-author-ACK-224.json',ack)
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
ck('Main bytes exact preserved',(P/'main-review-preserved.json').read_bytes()==f.read_bytes())
ck('all Main fields preserved',read(P/'main-review-preserved.json')==main)
ck('original author entire object exact',main['author_complete_manual_review']==original)
ck('original seven/eight exact',ack['original_seven_dimensions']==original['seven_dimensions']and ack['original_eight_limits']==original['limits'])
ck('12indexed findings exact',[a['Main_original']for a in ack['finding_responses']]==main['Main_findings'])
ck('8indexed limits exact',[a['Main_original']for a in ack['limit_responses']]==main['Main_limits'])
ck('author receipt binding exact',bind(ORIG/'RECEIPT.json')==main['author_receipt'])
ck('source binding to saved author records',all(any(r['member']==b['member']and r['nbt_sha256']==b['entry_sha256']and r['source_archive_sha256']==b['archive']['sha256']for r in read(ORIG/'sources.json')['candidates'])for b in main['source_bindings']))
ck('all20 indexed responses present',all(a['response'].strip() for a in ack['finding_responses']+ack['limit_responses']))
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 o=dict(previous226_binding=bind(PRE/name),older_history_retained=True,current_batch_formal_credit_added=0,accepted221_first224_current227_increment=0,accepted157_first206_current227_increment=0,accepted203_first209_current227_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None)
 if name.startswith('carried'):o.update(active_pending_including_earlier=read(PRE/'session.json')['active_pending'],current_batch_new_pending=0,current_batch_pending_cases=[],author224_ACK=dict(binding=bind(P/'actual-author-ACK-224.json'),status='ACK_DONE_WAIT_MAIN_FINAL',formal_increment=0),not_master_todo_backup=True)
 put(name,o)
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current226'];now=bind(b['path']);protected.append(dict(last226_checkpoint=b,current227=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('eight protected unchanged',len(protected)==8 and all(o['unchanged']for o in protected));ck('ACK formal and COD4 zero',ack['formal_credit_added']==ack['COD4_increment']==0)
put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
s=dict(batch=227,status='ACTUAL_AUTHOR_ACK_224_ALL12PLUS8_WAIT_MAIN_FINAL',formal_credit_added=0,accepted221_first224_current_increment=0,accepted157_first206_current_increment=0,accepted203_first209_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,new_qualifying_proposals=0,active_pending=read(PRE/'session.json')['active_pending'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,protected_input_concurrent_changes=sum(not o['unchanged']for o in protected),next='Wait Main final224;225/226 still pending.Continue different related complete whole, not variants;221 already first224 future0.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),ACK=bind(P/'actual-author-ACK-224.json'),files=len(files),checks=len(checks),protected_unchanged=sum(o['unchanged']for o in protected)),ensure_ascii=False))

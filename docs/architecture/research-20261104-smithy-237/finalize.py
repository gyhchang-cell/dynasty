import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];PRE=P.parent/'research-20261104-smithy-236';OLD=P.parent/'research-20261104-smithy-226';M=R/'docs/cod4/audit-20261022/coordinator-architecture226-whole-preACK-review-20261112.json'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
assert bind(M)['sha256']=='182076f8b934743f59061a3fe5587b8a7d02a21f04835121d24d6faf9a9870f0'
m=read(M);author=read(OLD/'manual-review.json');assert m['author_complete_manual_review']==author;assert len(author['seven_dimensions'])==7 and len(author['limits'])==8;assert len(m['Main_findings'])==12 and len(m['Main_limits'])==8
findings=[
'确认Main实际8分类PNG/88palette/24BE/唯一clock实体/135RLE2295宿主格的审阅与原Jar独立解码相等；本作者本批只读完整审阅意见及原七维八限，不声称重新看8图或重新读原NBT。旧模块18格6行复用两次仍1旧源，新增模块信用0，文件检查不作语义信用。',
'确认两个up_east/aligned父口5,0,3与6,0,11，childdown_south经CCW90(z,y,-x)到down_east；两origin3,1,4与4,1,12及两不相交内含box保留，静态无原nonair碰撞不等原生生成通过。',
'确认final_state必须保留doubleandesiteslab属性，Legacy忽略air/structurevoid；2331源布置记录不等独立格数，2295unique/920nonair及Main独立重建全部routecells相等。house随机processor未执行，不当世界实际结果。',
'确认完整组织是西两独立低工具间朝南北错层中庭，西中/东北抬高床室与东南低双床室另门向庭。与224内折阶上卧室、225北梯上书室区别是水平分散工住与院落联系；只有限固定近族比较，不称全历史穷尽唯一，不拆模块/房间。',
'确认原砖197/andesiteslab157/darkoak48/spruce94板170slab88trapdoor与21black+1graypane、5门对/空白牌记录保留。y8薄屋盖非9经营层；分类图不验证原生光照、精细材质或材料来源。',
'确认箱3,1,4与4,1,12north，砧3,1,2与4,1,10north，smith4,1,4与5,1,12。NW操作air横带和箱顶air仅静态；SW必须从x6,z10折向z11，7,1,11为实砖不得直穿。门/箱盖/工具侧向距离/NPC/付款未验。',
'确认两工作间east闭门6,1/2,2与7,1/2,10，抬高西门6,2/3,6east、东北10,2/3,5west、东南11,1/2,9west原状态保留。局部air、台阶与double板不能替代全门净空、错层落脚或居民移动验收。',
'确认东南实际两张lightblue完整床（四head/foot块），加西中一blue与东北一cyan共四张床；Main“two lightbluebeds/southeastpair”按两张床理解，不写成仅一对床方块或六床。六villagersocket不等六居民。无连续内部上楼链、炉/lava热锻链或实存库存。',
'确认唯一clock框relative13.5,3.5,10.96875与原NBT绝对-11.5,-55.5,2038.96875属不同坐标域，保留原Pos/UUID，不改写为活体位置或播放声音。两原宿主箱savannahouse候选loot及signed long seed保留，非目标玩家已获得库存。',
'确认南接路8,0,14finalandesite上8,1,14openbottomtrapdoor非air；8,2,11悬灯不能忽略。分类图省略原纹理/薄形碰撞/地形/动画，不称中庭无阻或已天然接路。',
'确认Main所读4紧凑上下文含16housechoices/large1权3、12chance2/toolsmith权3与12chance1/toolsmith权1及4processor规则，权重与Properties按源保留。作者226使用224完整固定上下文复用、原newfullJSON0不改成新阅读；vanilla/root复用非本批新JSON/实际概率。',
'确认至多1相关NPC01冷作工住整栋待最终独立验收，保留原作者七维八限全文；第二模块、变体、布局切片、截图均不加信用。本237只实际作者ACK，formal/COD4增量0，不删任务、不称1000达成或游戏制作完成。'
]
limits=[
'已由原建筑作者聊天实际读取并逐条回应12发现8限制；本文件不是Main代写的作者ACK。仍只是preACK最多1NPC01整栋，正式0，等独立最终验收，不自己授予。',
'保留宿主DV3578/旧模块DV3105固定源，只确认限定静态证据；无DataVersion升级、nativejigsaw、随机processor、worldgen、远端新鲜度或完整引擎证明。',
'8分类PNG及精确格状态仅源研究；原生材质/光照/碰撞/寻路/地形/性能/生存均未验，不将精确重建当游戏验收。',
'所有门、错层台阶、悬灯、open接路trapdoor、箱盖与工作站作用范围仍待原生验；不保证NPC路线/居民床位入住或相互操作。',
'仅冷工具维护工住空间，不宣称热锻炉链、材料库存、交易付款、玩家领取或任务中文指南针接入。clock原框不触发声音或当玩法验收。',
'旧224child/context新增源0；2331placement记录不等2295unique。组件/旋转/床数/palette/文件不计建筑，完整近族对照范围有限，无穷尽全目录新颖性。',
'至多1整栋pending；224first228/225first231/221first224及203first209/157first206全部不重复，COD4153gap847、pending51原样，NPC累计未知。1000门槛未满足，继续研究不能提前制作。',
'仅本地Python研究证据写入；不运行Java/游戏/联网/UI/进程操作/声音亮度/焦点唤醒，不碰实例存档/生产/共享Jar/专业资产/主清单/Git；主动工时null/allcompletefalse。'
]
ack=dict(schema='dynasty.architecture226.actual-author-ACK.v1',actual_author_thread='01a12515-f16a-7be3-b79a-bd5500f7ccd4',Main_preACK_binding=bind(M),original_author_review_binding=bind(OLD/'manual-review.json'),original_author_review_full=author,Main_findings_responses=[dict(index=i,Main_original=s,author_actual_response=v)for i,(s,v)in enumerate(zip(m['Main_findings'],findings),1)],Main_limits_responses=[dict(index=i,Main_original=s,author_actual_response=v)for i,(s,v)in enumerate(zip(m['Main_limits'],limits),1)],actual_reading_scope='Full12Mainfindings8Mainlimits and original7dimensions8limits actually read; sourcebindings/provenance checked. Embedded full NBT/comparison huge body in first output truncated, not claimed full fresh reading. No old NBT/PNG reread, no new whole study.',preformal_maximum_NPC01=1,formal_credit_added=0,COD4_added=0,final_independent_admission_pending=True,all_tasks_complete=False)
put('226-actual-author-ACK.json',ack)
checks=[]
def ck(k,v):
 checks.append(dict(check=k,passed=bool(v)));assert v,k
ck('12specific findings and8specific limits',len(ack['Main_findings_responses'])==12 and len(ack['Main_limits_responses'])==8 and all(x['author_actual_response']for k in ['Main_findings_responses','Main_limits_responses']for x in ack[k]))
ck('original7dimensions8limits exactly retained',ack['original_author_review_full']==m['author_complete_manual_review']==read(OLD/'manual-review.json'))
old=read(OLD/'RECEIPT.json');ck('original226receipt exact Main binding',bind(OLD/'RECEIPT.json')==m['author_receipt'])
ck('all original226 sealed files unchanged',all(bind(x['path'])==x for x in old['files']))
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current236'];now=bind(b['path']);protected.append(dict(last236_checkpoint=b,current237=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False));ck('8protected unchanged',len(protected)==8 and all(x['unchanged']for x in protected))
put('previous-checkpoint.json',dict(receipt=bind(PRE/'RECEIPT.json'),cumulative_not_reset=True));s=dict(batch=237,status='226_ACTUAL_AUTHOR_ACK_12_FINDINGS_8_LIMITS_FINAL_ADMISSION_PENDING',formal_credit_added=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,active_pending=read(PRE/'session.json')['active_pending'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='226 actualACK done wait independent final no selfcredit;235pending/236zero unchanged; continue new genuinely related complete source. No repeat224/225/221/203/157firstcarry.')
for f in ['session.json','active-checkpoint.json','latest-independent-admissions.json','carried-forward-pending.json']:put(f,{**s,'previous236_binding':bind(PRE/f),'old_accepted_carries_added':0,'not_master_todo_backup':True})
put('verification.json',dict(status='PASS',checks=checks));files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),ack=bind(P/'226-actual-author-ACK.json'),files=len(files),checks=len(checks)),ensure_ascii=False))

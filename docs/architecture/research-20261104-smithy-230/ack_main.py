import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2];PRE=P.parent/'research-20261104-smithy-229';ORIG=P.parent/'research-20261104-smithy-225'
assert not(P/'RECEIPT.json').exists()
def read(p):return json.loads(Path(p).read_text())
def put(n,o):(P/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
f=ROOT/'docs/cod4/audit-20261022/coordinator-architecture225-whole-preACK-review-20261111.json';binding=bind(f)
assert binding['sha256']=='4fdcec5eb3ec8d8a6c3c374595fa492b8566fc34914a4c19d107a8ef27157d7c' and binding['bytes']==216921
main=read(f);original=read(ORIG/'manual-review.json');assert original==main['author_complete_manual_review']
(P/'main-review-preserved.json').write_bytes(f.read_bytes())
responses=[
'确认Main本人实际看8最终图、70新palette/13BE/entities空、9层99RLE及独立原始解码；这是Main的工作，不冒称本ACK又做一次。1503源记录有18重合，只1485独立格，RLE/图/组件均不额外算whole。',
'确认parent up_south/aligned11,0,7与child down_south/aligned1,0,2，同bottom target/name，按up邻格相减得不旋转origin10,1,5，box10..12/1..2/5..7内含且原nonair零覆盖。只一个宿主加模块的整体。',
'确认两村民接口final必须保存andesite_slab的Properties.type=double，不能当含方括号名称。Legacy忽略air/structure_void后的541nonair、1485推导格和304关键路格是静态结果，house随机processor未执行，不冒称实际世界成屋。',
'确认整体南中通道分开西南低单床间与东低工具间，北底青床/箱室经北内竖梯上书架/空唱片机小室。其上下层用途及通道关系才是对224折阶卧室、095上三分处理/药/床、221中央热台的有限比较；不按房间拆数。',
'确认砖129/andesiteslab63/深橡木板20与TOPslab、13黑窗片及四扇上下门对的原材质关系，8门块不等8入口；分类图颜色不是MC原纹理。',
'确认spruce56板/101slab/1stairs/50trapdoor/8gates形成侧低北高盖，只use1与4，y8薄盖不等第三层或九层；3chain/6lantern不当支撑结构或经营楼层。',
'确认胸10,1,5east、砧12,1,5east、工作台10,1,6；内11,1/2,7→6→5及砧南12,1/2,6、胸顶10,2,5原air仅静态服务可能。无炉/lava，不称完整热锻、库存或已付款制作。',
'确认工具西门9,1/2,7west/right与南门11,1/2,8south/left原closed，北门7,1/2,5south/left；空脚头采样不等已执行开门、路径寻找、梯攀爬或薄件碰撞验证。',
'确认梯7,y1..4,z2south连续、上7,5,2air、南上出口7,4/5,3air且floor7,3,3TOPdarkoak，西6,4/5,3有同高板。只支持第二使用小室静态关系，非保证NPC爬梯；6,1,2脚手架上6,2,2盆杜鹃不另成楼梯。',
'确认南入口6,0,10finalandesite上6,1,10openbottomtrapdoor非air，东8,1/2,10和中7,1/2,9只是静态备选。两完整床对/三villager socket不是实际居民数，jukebox5,4,3has_recordfalse/IsPlaying0，不播放、不编上层酿药/锻造。',
'确认houses medium6权2，实际chance1toolsmith权1，非chance2权3。224/222/221完整旧上下文与loot支持精确复用，新全文JSON0；pool/职业/loot名不证明材料/库存/扣款/目标玩家回执或指南针。',
'确认已实际读本Main保存224完整七维八限及其095/221完整保存七维比较，保留原作者225七维八限不改。最多一个相关NPC01冷作工住整体仍待Main最终决定，不证全库语义唯一；228作者HOLD0近225不变，不因本ACK顺带计它。COD4增量0。'
]
limits=[
'接受。已实际完整读本新Main业务字段、12发现/8限、225原7维8限、来源/范围绑定和完整224比较及保存095/221七维文本，20项逐项实际回应。完整216921B逐字节保留；ACK本身formal0，Main最终采纳另行处理。',
'接受。仅本地固定来源完整性，不证明远端最新；宿主DV3578与组件DV3105兼容/升级、processor和native jigsaw放置未运行。',
'接受。8分类源格图不是MC原纹理/碰撞、地形生成、性能/生存/NPC路径验收。本ACK不重开旧图或旧原始NBT，嵌入raw whole仅完整保留不冒称重新解码/阅读1503格。',
'接受。门/标牌/活板/梯出口/悬灯/箱盖及砧台范围与接近碰撞均未原生验；连续梯和上出口air不保证居民攀爬。',
'接受。无热锻/酿药链、真实库存、扣款交易、制作/获取原生回执或中文任务指南针接入；两床/三socket不是实际入住清点。',
'接受。旧组件/上下文/源码片段复用零新增源或语义信用；不宣称全引擎阅读、旧PNG重开、新JSON阅读或历史全库语义去重。095省略格仍不当air。',
'接受。同宿主换职业/色/旋转/模块/房间/床/图全部零额外whole。224first228必须由Main另外独立核验，230及以后不重复；225此ACK仍formal0，不预先carry。',
'接受。本批无Java/游戏/联网/UI/唤醒/声音亮度/焦点/实例存档/生产/Jar/专业资产/主清单/Git操作。COD4153/gap847、Main审阅pending51不变，NPC总未知，1000未达不制作，无小时或全部完成声明。'
]
ack=dict(schema='dynasty.architecture.actual-author-ACK.v1',batch=230,target='225F01_HOST_PLUS_REUSED224F04',main_review_binding=binding,main_all_fields_preserved_binding=bind(P/'main-review-preserved.json'),original_manual_binding=bind(ORIG/'manual-review.json'),original_receipt_binding=bind(ORIG/'RECEIPT.json'),original_seven_dimensions=original['seven_dimensions'],original_eight_limits=original['limits'],source_bindings_preserved=main['source_bindings'],saved_complete_comparison_preserved=main['saved_complete_comparison'],source_read_scope_preserved=main['source_read_scope'],finding_responses=[dict(index=i,Main_original=s,response=r)for i,(s,r)in enumerate(zip(main['Main_findings'],responses),1)],limit_responses=[dict(index=i,Main_original=s,response=r)for i,(s,r)in enumerate(zip(main['Main_limits'],limits),1)],reading_boundary='Entire new Main business object actually read, original225seven/eight and saved224seven/eight, complete saved095/221 seven-dimensional comparison read. Entire216921B object preserved byteexact; embedded original_wholes raw cells preserved only, not newly reread or decoded in230. No old PNG/raw NBT reopened, no new engine reading/run.',maximum_related_NPC01_after_Main_final=1,formal_credit_added=0,COD4_increment=0,accepted224_first228_current_increment=0,accepted221_first224_current_increment=0,no_production_or_checklist_authority=True,all_tasks_complete=False)
put('actual-author-ACK-225.json',ack)
checks=[]
def ck(k,v):checks.append(dict(check=k,passed=bool(v)));assert v,k
ck('Main216921 bytes exact',(P/'main-review-preserved.json').read_bytes()==f.read_bytes());ck('all fields exact',read(P/'main-review-preserved.json')==main);ck('author original entire exact',main['author_complete_manual_review']==original);ck('original7/8 exact',ack['original_seven_dimensions']==original['seven_dimensions']and ack['original_eight_limits']==original['limits']);ck('all12findings exact',[a['Main_original']for a in ack['finding_responses']]==main['Main_findings']);ck('all8limits exact',[a['Main_original']for a in ack['limit_responses']]==main['Main_limits']);ck('all20 real responses',len(responses)==12 and len(limits)==8 and all(x.strip()for x in responses+limits));ck('original225 receipt bound',bind(ORIG/'RECEIPT.json')==main['author_receipt']);ck('formal0',ack['formal_credit_added']==ack['COD4_increment']==0)
for name in ['latest-independent-admissions.json','carried-forward-pending.json']:
 o=dict(previous229_binding=bind(PRE/name),older_history_retained=True,current_batch_formal_credit_added=0,accepted224_first228_current230_increment=0,accepted221_first224_current230_increment=0,accepted157_first206_current230_increment=0,accepted203_first209_current230_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None)
 if name.startswith('carried'):o.update(active_pending_including_earlier=read(PRE/'session.json')['active_pending'],current_batch_new_pending=0,author225_ACK=dict(binding=bind(P/'actual-author-ACK-225.json'),status='ACK_DONE_WAIT_MAIN_FINAL',formal_increment=0),not_master_todo_backup=True)
 put(name,o)
protected=[]
for o in read(PRE/'protected-inputs-current.json')['files']:
 b=o['current229'];now=bind(b['path']);protected.append(dict(last229_checkpoint=b,current230=now,unchanged=b==now))
put('protected-inputs-current.json',dict(files=protected,this_chat_product_writes=False,concurrent_changes_not_reverted=True));ck('eightprotectedunchanged',len(protected)==8 and all(o['unchanged']for o in protected))
put('verification.json',dict(status='PASS',checks=checks,check_count=len(checks),machine_checks_not_reference_credit=True))
s=dict(batch=230,status='ACTUAL_AUTHOR_ACK_225_ALL12PLUS8_WAIT_MAIN_FINAL',formal_credit_added=0,accepted224_first228_current_increment=0,accepted221_first224_current_increment=0,COD4_accepted=153,COD4_gap=847,NPC01_total=None,NPC05_total=None,NPC06_total=None,new_complete_whole_studies=0,new_qualifying_proposals=0,active_pending=read(PRE/'session.json')['active_pending'],java_run=False,game_run=False,network_used=False,production=False,masterlists_edited=False,all_tasks_complete=False,actual_active_work_hours=None,next='225 actual ACK complete waiting Main final;226/229 still pending,228 authorHOLD0.Continue semantically different related whole, no samehost variants.224first228 and221first224 later0.')
put('session.json',s);put('active-checkpoint.json',s);files=[bind(f)for f in sorted(P.iterdir())if f.is_file()and f.name!='RECEIPT.json'];put('RECEIPT.json',dict(**s,files=files,verification_checks=len(checks)));print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),ACK=bind(P/'actual-author-ACK-225.json'),files=len(files),checks=len(checks)),ensure_ascii=False))

"""Seal this private offline research batch once. No shared state writes."""
import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not (P/'RECEIPT.json').exists(), 'sealed batch is immutable'
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def ld(p):return json.loads(Path(p).read_text())
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
s=ld(P/'source.json');d=ld(P/'original-all-source.json');previous=P.parent/'research-20261104-smithy-286'
obs={
 'layout':'同一栋三使用层木框长住宅：南短门颈西门进下层家务/工作台区，北中央木柱周围两段回转阶通中层公共书架/讲台厅及西侧三床阁层；中层东门通同屋侧平台。实际当前16PNG全看，原始167状态完整Properties、11BE、entities[]及300阶井矩阵读。与旧165 large_house_rework同一完整设计，不能增1。',
 'proportion':'声明25×40×18/DV3578共18000格，8315存=2329非air5986显式air，9685省略unknown。实际非air仅y0..17；y18有402air/48unknown，y19..39每层450unknown。主要floor1/use2、floor6/use7、floor10/use11，不是40层建筑。薄件/坡阶/侧台/三床不能拆建筑数。',
 'facade':'oaklog161、去皮spruce78、去皮oak73木架，lime/green terracotta55/18与混石灰粉材及67白玻璃板。南颈oak门13,2/3,12 west/left/closed；中东spruce门17,7/8,9 east/right/closed。不凭类色灰图把绿陶土或木坡叫石瓦；无中文招牌或人物实体。',
 'roof':'长向高双坡、前后短凸盖、局部小窗和侧低盖；301spruce阶、152spruce半砖含屋面/结构陈设。顶脊y17含木薄件，未保存真实厚雪盖；大部分声明高空是unknown。屋盖轮廓与165完全沿用，长脊/侧檐不独立计数；本体无营火或独立烟囱。',
 'materials':'普通炉13,2,3 east/unlit，Items[]、三计时0、RecipesUsed{}；炉上13,3,3 TOP半砖及13,4,3 east底阶在楼梯角，不是贯通烟道。工作台8,2,6；中讲台11,7,9 north/has_bookfalse，无书；brown旗3Patterns cs4/hhb12/mc4。三对west红床7/8,11,z6/7/8，其中中床occupiedtrue但entities[]，上各白/红carpet不是床可用验收。无箱桶loot/砧/高炉/锻台/砂轮/水熔岩；侧日照检测power0/灯litfalse区别旧165保存power9/littrue，不构成新设计。',
 'circulation':'阶井x11..15/z2..6/y1..12共300原索引实际读：首段12,2,5north→12,3,4north→13,4,3east→14,5,4south→13,6,5west；第二段12,7,4north→13,8,3east→14,9,4south→13,10,5west，中间含TOP/double半砖与TOP阶，不写全程碰撞通过。两门前后四格air已查；炉east服务面14,2/3,3air，下14,1,3灰混凝土粉；侧门外18,7/8,9air且18/19,6,9木板、20,6,9oaklog。床底TOP阶/半砖，上carpet保留。未跑玩家/NPC通行、睡眠、交互或承重。',
 'terrain_and_dedup':'本原件实际houses池精确weight2/single/rigid/empty，fallbackempty；唯一道路socket9,1,17 south_up/aligned name&targetentrance、poolfortified/roads、finalair。root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue，starts empty权1与castle权3，biometag7条含alpine_highlands但不证明大雪山狩猎场景。旧165rework在其当时选读池没有精确entry，两者不能相互套生成权重。实际当前/旧165原格态差242位置/16组全读：草土地裙/植物、air与省略、道路socket、灯/日照功率；三层房体及交通未形成新设计。旧272已作此别名有界检查，本轮是补充实际全变体视觉/源态与去重记录，新增不同完整建筑0。'
}
limits=[
 '同设计排除：当前原source变体完成空间复核1，新增不同完整建筑0/相关提议0/formal0/carry0。旧165本来pending的用途/家族状态不因本次复核转已接受。',
 '20条较大houses只是固定metadata中选定历史索引未登记行的功能预筛；其中很多以前已有机器有界记录。不是20个新建筑或新语义研究；无声称固定源穷尽。两条damaged_anvil来自Trek fletching_table/smoker，不能自动升级锻造工坊；070/093原工住菌屋近族判断保留。',
 '选择索引不含所有机器预筛来源；此次666缓存命中本source源于272，进一步定位165同设计。以后选题必须同时查历史实际source/语义比较/机器别名记录，索引缺失及声明高度改变都不证明新建筑。',
 '先读270/275各自7维与全部10/9限制保存，之后读165 own7维内的全部限制；旧165嵌套比较仅原样保留未宣新全文阅读。272大原差分最初有截断，本轮另从两原NBT实际生成242差分16无损分组并全读，不冒称截断原输出已全读。',
 '本轮16PNG实看：whole/low/3cuts/10页40层/vertical。low cut17与whole实构相同，既非新视角设计亦不多算建筑；vertical仅y0..18标示，40层另完整投影。图是类别色整块近似，不是MC原材质/薄件碰撞/实机防雨验收。',
 '167palette逐条Properties、11原BE、entities[]实际读。8315保存块原JSON完整捕获，不宣逐格人工语义全读；实际读300阶井索引及33服务/床探针，重叠不合成独立点信用。40层unknown分开保存。',
 '原source普通工住住宅不是铁匠铺或猎户夜烤火任务。三床/讲台/普通空炉不证明营业AI、取暖、捕猎、夜宿NPC或任务付款，不据此提新用途信用；不转NPC12茶馆/驿站身份。',
 'houses21条完整字段、root/starts/tag全文实际读；道路/城堡NBT及外部biome实现未读拼，不证明出生或坡地衔接。source原finalair无namespace保留，不修改原archive。',
 '269只first277 NPC06辅助1；后续本轮复用0。273/275等候Main独立审阅，当前无其新增接受。COD4仍153缺847，NPC累计null，1000未达不制作、不删未验清单。',
 '仅本地Python -B研究，不运行Java/游戏/Gradle/网络/UI/进程查询，不改声音亮度/唤醒焦点/用户实例存档/共享Jar/正式资产/Git/主清单；无任何session写入。无新建聊天/自动化/总工时或全部完成声明。'
]
images=[bind(p) for p in sorted(P.glob('*.png'))]
save('manual-review.json',dict(batch=287,source={k:s[k]for k in ['source_archive','source_archive_sha256','member','nbt_sha256','size','DataVersion']},seven_dimensions=obs,limits=limits,images_actually_viewed=images,current_source_variant_spatial_review_complete=True,new_distinct_whole_studies=0,new_reference_proposal_maximum=0,formal_credit_added=0,first_carry_added=0,status='SAME_165_DESIGN_ALREADY_BOUNDED_272_EXCLUDED_ZERO',native_acceptance=False))
old=ld(previous/'protected-inputs-current.json');protected=[]
for a in old['files']:
 before=a['current286'];after=bind(before['path']);protected.append(dict(previous286=before,current287=after,unchanged=before==after,this_chat_wrote_file=False))
save('protected-inputs-current.json',dict(files=protected,cod5_missing_not_invented=True,this_chat_product_writes=0))
save('active-checkpoint.json',dict(batch=287,status='SAME_165_DESIGN_EXCLUDED_ZERO',previous_receipt=bind(previous/'RECEIPT.json'),manual_review=bind(P/'manual-review.json'),new_distinct_whole_studies=0,current_source_variant_spatial_review_complete=True,new_reference_proposal_maximum=0,formal_credit_added=0,first_carry_added=0,old269_carry_added=0,old269_first_carry_batch=277,COD4_accepted=153,COD4_gap=847,NPC_cumulative=None,all_tasks_complete=False,tasks_deleted=0,no_session_written=True,next='选题先查缓存与所有有界别名：generic_big4=165 rework近同设计，272已有判断；不要重做本完整房体或20条机器预筛。继续其他固定本地直接适用且语义未读完整建筑；累计未知不编。'))
checks=[]
def ck(n,b):
 assert b,n
 checks.append(n)
with ZipFile(s['source_archive']) as z:
 raw=z.read(s['member']);ck('fixed raw source sha',hashlib.sha256(raw).hexdigest()==s['nbt_sha256']);ck('lossless full capture',read(raw)==d)
ck('palette167',len(d['palette'])==167)
ck('BE11 entities empty',len(s['block_entities'])==11 and d['entities']==[])
ck('stored unique8315',len(d['blocks'])==len({tuple(b['pos'])for b in d['blocks']})==8315)
co=Counter('air'if d['palette'][b['state']]['Name']in AIR else 'nonair'for b in d['blocks'])
ck('counts2329/5986/9685',co=={'nonair':2329,'air':5986} and 18000-len(d['blocks'])==9685)
ck('all40layers',len(ld(P/'layer-counts.json'))==40)
ck('16PNG actual review registry',len(images)==16)
ck('300stairs matrix',sum(len(r)*len(r[0])for a in ld(P/'stair-matrix-300.json')for r in [a['z2to6_x11to15']])==300)
ck('33service probes',len(ld(P/'service-and-bedroom-probes.json'))==33)
cmp=ld(P/'actual-165-same-design-comparison.json')
ck('242diff16groups',len(cmp['current_actual_differences'])==16 and sum(a['count']for a in cmp['current_actual_differences'])==242)
ck('screen20 potential2',len(ld(P/'larger-house-device-screen.json')['rows'])==20 and sum(a['potential_smith_signature']for a in ld(P/'larger-house-device-screen.json')['rows'])==2)
ck('0new semantic credit',cmp['credit']==0)
ck('previous286 immutable',bind(previous/'RECEIPT.json')['sha256']=='636fd12b7f2689a585945c7f82e08a004af8f6450fa8d7a7e276b3ca769a5610')
ck('no sessions in new batch',not list(P.glob('*session*')))
save('verification.json',dict(status='PASS_OFFLINE_RESEARCH_BINDINGS_ONLY',checks=checks,not_independent_acceptance=True,protected_changes=[a['current287']['path']for a in protected if not a['unchanged']]))
save('RECEIPT.json',dict(batch=287,status='SEALED_SAME_DESIGN_EXCLUDED_ZERO',files=[bind(p)for p in sorted(P.iterdir())if p.is_file()],checks=len(checks),formal_credit_added=0,new_distinct_whole_studies=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual_review=bind(P/'manual-review.json'),checks=len(checks),protected_unchanged=all(a['unchanged']for a in protected)),ensure_ascii=False))

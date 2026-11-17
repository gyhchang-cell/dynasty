"""Seal source study with no semantic credit presumed."""
import json,hashlib,sys,math
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
b=ld(P/'source-binding.json');d=ld(P/'source-original.json');c=ld(P/'source-counts.json')
ck('fixed original archive',bind(b['archive']['path'])==b['archive'])
with ZipFile(b['archive']['path'])as z:
 raw=z.read(b['member']);ck('original source matches',hashlib.sha256(raw).hexdigest()==b['raw_sha256']and read(raw)==d)
 for row in ld(P/'source-context.json')['resources']:
  raw=z.read(row['member']);ck('original context '+row['member'],hashlib.sha256(raw).hexdigest()==row['sha256']and raw.decode()==row['text']and json.loads(raw)==row['json'])
ck('source accounting',c['stored']==615 and c['nonair']==569 and c['air']==46 and c['omitted']==4553 and c['stored']+c['omitted']==math.prod(d['size']))
ck('61palette 25BE no source entities',len(d['palette'])==61 and len(ld(P/'all-BE-original.json'))==25 and not d['entities'])
ck('five source images',len(list(P.glob('*.png')))==5)
ck('bounded exact-name history no hits',not ld(P/'history-screen.json')['hits'])
comparisons=[]
for n in (266,273):
 p=R/f'docs/architecture/research-20261104-smithy-{n}/manual-review.json';old=ld(p)
 comparisons.append(dict(binding=bind(p),seven_dimensions=old['seven_dimensions'],limits=old['limits'],formal_credit_added=old['formal_credit_added'],reading='Full seven dimensions already actually read in this continued turn; old images not reopened. No new credit for old camps.'))
put('prior-whole-comparisons.json',dict(camps=comparisons,boundary='Purpose/layout comparison does not prove global novelty or establish current formal acceptance.'))
m={tuple(x['pos']):d['palette'][x['state']]for x in d['blocks']}
xz=[(8,11),(8,12),(10,11),(9,10),(9,11),(9,12),(9,13),(9,14),(9,15),(12,5),(13,5),(14,5),(15,5),(16,5),(17,5),(18,5),(8,5)]
probes=[dict(pos=[x,y,z],state=m.get((x,y,z),'OMITTED'))for x,z in xz for y in range(4)]
put('actually-read-source-probes.json',dict(count=len(probes),cells=probes,all615_positions_individually_read=False))
ck('original mob sockets',sum(x['state']['Name']=='minecraft:jigsaw'for x in ld(P/'all-BE-original.json'))==4)
status='SEALED_COMPACT_PAIRED_BED_SHELTERS_SOURCE_STUDY_RELEVANCE_AND_NEAR_FAMILY_HOLD_ZERO_CREDIT'
review=dict(batch=295,status=status,source=b,new_source_whole_studies=1,new_distinct_qualifying_buildings_confirmed=0,new_qualifying_reference_proposals=0,formal_credit_added=0,tasks_deleted=0,native_acceptance=False,
 actual_reading=dict(images_actually_viewed=5,images=[bind(p)for p in sorted(P.glob('*.png'))],plan_layers_actually_viewed=16,full_height_section_planes_actually_viewed=2,palette_states_actually_read=61,BE_payloads_actually_read=25,context_JSON_actually_read=3,selected_coordinate_cells_actually_read=len(probes),all615_positions_individually_read=False),
 seven_dimensions=dict(
 layout='完整camp4一处：东x12..18,z3..7东西向短棚，南x7..11,z10..16南北向短棚，两座为同族转向双床棚；各有两张绿床和炉/货桶，围中间露天混土工作区。西南x3..4,z11..13集中桶堆，西北独立针叶树，中北火位(8,1,5)。树、双棚、四床、十桶不拆参考。',
 proportion='19×16×17，569nonair/46air/4553省略，61palette/25BE/entities[]。生活设施集中y0..3、棚盖延至y5、局部木饰y6；y7..15主体仅树冠，不能当16层房屋或高楼。棚内两床夹窄中轴，不按存储bbox扩大经营净空。',
 facade='oak slab42、oak trapdoor18、oak fence36配lime terracotta91，暖木细构件和实体绿色坡面，不是彩毛帐篷。无普通门、楼梯或玻璃窗，薄活板端饰/侧栏不能当完整实墙或自动可开门。4灯含挂灯与落地灯，未运行光照。',
 roof='两座短双坡棚转向相邻，石陶实体坡面搭木脊/活板收边，y3中轴局部薄件与挂灯，层图显示y4/5收窄。green leaf102来自西北大树，不能并入棚盖面积；叶persistent false/distance1..5并非防腐不落叶保证。防雨未实机验收。',
 materials='四完整green beds：南8/10,z11foot至12head facingsouth；东13head/14foot,z4/6 facingwest。2furnace emptyItems、Cook/Burn/Total0、RecipesUsed{}。4棚内桶引用camp_barrels，6外桶引用street_barrels，各原seed完整保留；本批未读这两loot表，不称实际库存/收款。唯一lit south campfire空Items/计时0。',
 circulation='已实际读68格：南轴x9,z10..12,y1/2air，z11/12,y0是mob接头、final oak_slab；z13,y0 closed底活板、z14/15,y0air不保证脚下支撑。东轴z5,x12..14,y1/2air，x13/14,y0接头；x15,y0closed底活板、x16/17,y0air，入口外x18,y1..3省略。床脚上有top closed活板，不能据空气图断睡眠/站位。火上y2/3省略，不称畅通烟道。未证明全营地跨区动线或安全入口。',
 terrain='root #trek:forest/spruce/is_spruce_forest_no_snow、WORLD_SURFACE_WG、start0、size2/max64/beardthin/expansionfalse/spawn_overrides{}；自身pool single rigid weight1 emptyprocessor。4up接头连taiga unemployed mob池，该池8unemployed/1nitwit/1baby、empty fallback。未读三mobNBT或biome tag，未装配或运行，因此不保证4村民出现，也不能替代固定百宝金UUID或任务/指南针注册。y-1未给、地面省略不补实土。'),
 dedup='没有在所查legacy review键台账和manual找到camp4直接名称，但不是全局语义独特证明。旧266单窄拱货棚北桶南床/外火，本源两转向短双床棚/集中外桶/公共露天场。旧273同样多帐围场，虽规模/材料/床位与工作台配置不同，不仅凭这些差异立新族；近族是否过度相似及百宝金整体适用性保留HOLD0。不得把两转向棚算两个。',
 applications=['针对营地把睡卧、货储、公共火位分开观察；先检查棚入口和每个工作位的地板支撑，再讨论NPC路线。','树高不决定建筑层数，单层棚盖要按床位净空和屋脊高度分配比例。','普通村民mob接头不能充当专属商人；商品来源、交易付款、获取回执及中文任务/指南针仍需原生链验证。'],
 limits=['本源整营地图层研究1，不等新增独立有效建筑，正式和候选入账均0；Main未看图/独立审查，不先承诺可计1。','5图为类别色和全格薄件近似，非原生材质/模型/碰撞；68格逐格读不等615格全部逐格读。','四接头final_state只配置，未加载mobNBT/落地/随机loot/下雨/灯光/路径/碰撞；不能声称NPC或游戏任务完成。','未达1000有效相关完整建筑，未制作或删除清单。仅写295research目录，不改主session/pending/ownership/共享Jar/专业资产，不碰音亮唤醒焦点实例存档，不运行Java或游戏，不上网/Git/自动化。'],all_tasks_complete=False,NPC_cumulative=None)
put('manual-review.json',review)
previous=ld(R/'docs/architecture/research-20261104-smithy-294/protected-current.json');protected=[]
for row in previous['files']:
 before=row['after'];after=bind(before['path']);protected.append(dict(last294_observation=before,current=after,unchanged=before==after,this_chat_wrote_file=False))
put('protected-current.json',dict(files=protected,boundary='Compared with previous294 end observation, not fabricated295 start measurement; concurrent changes never overwritten.'))
ck('shared jar unchanged since294',all(x['unchanged']for x in protected if x['current']['path'].endswith('.jar')))
cp=ld(P/'active-checkpoint.json');cp.update(status=status,images_actually_viewed=5,new_source_whole_studies=1,new_distinct_qualifying_buildings_confirmed=0,formal_credit_added=0,next='近族与相关性HOLD0；不能将四普通村民接头当百宝金接入。另筛不同完整相关建筑继续研究。');put('active-checkpoint.json',cp)
put('verification.json',dict(passed=True,count=len(checks),checks=checks,java_run=False,game_run=False,independent_acceptance=False))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=295,status=status,files=files,checks=len(checks),new_source_whole_studies=1,formal_credit_added=0,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_unchanged=sum(x['unchanged']for x in protected)),ensure_ascii=False))

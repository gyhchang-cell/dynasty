import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2]
assert not(P/'RECEIPT.json').exists()
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
protected=[R/'docs/cod4/audit-20261022'/x for x in ['active-workstreams.json','pending-tasks.json','continuation-20261028/session.json']]+[Path('/Users/a15356015027/Desktop/code x提示词')/x for x in ['cod1.txt','cod2.txt','cod3.txt']]+[R/f'docs/architecture/research-20261104-smithy-{n}/RECEIPT.json'for n in [296,297]]
before=[bind(p)for p in protected]
m=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';mm=ld(m);terms=['chinese','chinatown','huipai','huizhou','teahouse','inn','oriental']
hits=[e for e in mm['entries']if len(e.get('size',[]))==3 and min(e['size'])>=6 and any(t in e['member'].lower()for t in terms)]
actual=[e for e in hits if 'inner'not in e['member']]
assert len(hits)==17 and len(actual)==4
olds={
'data/ati_structures/structures/villager_inn.nbt':('research-20261101-dungeons-004','旧整栋，268亦已排除重复；不是新增中式客栈证明。'),
'data/kaisyn/structures/outpost/towers/exclusives/oriental/base_plate.nbt':('research-20261101-dungeons-011','旧整栋东方塔，不据oriental命名当徽派客栈。'),
'data/kaisyn/structures/village/snowy_slopes_inn/town_centers/snowy_slopes_meeting_point_1.nbt':('research-20261104-smithy-245','旧雪坡客栈，不迁入严格徽派鬼城信用。'),
'data/simply_houses/structures/taiga_inn/taiga_inn.nbt':('research-20261101-dungeons-004','旧整栋针叶客栈，不以inn文件名当中国古建。')}
prior_main=R/'docs/cod4/audit-20261022/coordinator-building297-actual-six-PNG-two-storey-dwelling-auxiliary-HOLD0-20261114.json'
put('DUN05-bounded-local-gap.json',dict(batch=298,scope='cod2 DUN05 徽派鬼城狭巷/商铺/客栈/屋顶衔接',metadata=bind(m),terms=terms,min_each_axis=6,total_substring_hits=len(hits),false_positive_inner_hits=[e for e in hits if e not in actual],substantive_name_hits=[dict(source=e,prior_whole_review=bind(R/'docs/architecture'/olds[e['member']][0]/'manual-review.json'),assessment=olds[e['member']][1])for e in actual],prior297_main_actual_HOLD0=bind(prior_main),decision='BOUNDED_PASS_FOUND_NO_NEW_UNREAD_QUALIFIED_CHINESE_WHOLE',strict_credit_added=0,limits=['名称筛选只覆盖固定索引及指定词，未穷尽所有本地来源，不等于所有本地建筑均无合格项。','13个inner误命中不算客栈或完整建筑；四个有效名称候选亦均旧整栋。','沿用297主协调独立实际阅读HOLD0；日式双层住宅与西式296住宅不作为徽派客栈替代信用。','不为补数改名/重复制图/换材/拆组件；没有网络搜索或下载。'],next='转向既有cod3 NPC13大雪山木屋用途，独立审查相关整栋，不转移DUN05缺口。'))
oldcomparisons=[]
for n in [249,252,254,256]:
 f=R/f'docs/architecture/research-20261104-smithy-{n}/manual-review.json';v=ld(f);obs=v['seven_dimensions']if 'seven_dimensions'in v else next(s for s in v['studies']if s['id']=='F03')['seven_dimensions'];oldcomparisons.append(dict(binding=bind(f),case='F03'if n==252 else'whole',seven_dimensions_actually_read=obs,boundary='复用旧完整七维文字；本批没有重开旧NBT/PNG，不增旧信用。'))
put('whole-comparison.json',dict(comparisons=oldcomparisons,assessment='比252F03覆土包裹/高门槛内降阶，本栋同层入口、框架双坡与3×3紧凑小室；但与249同单床/箱/侧桌单室生活组织，差别可能主要在屋盖/材质/陈设，不能自动获得独立信用。254/256有内梯与上下生活分配，本栋没有夹层。',new_whole_study=1,formal_credit_added=0,decision='AUTHOR_HOLD0_PENDING_INDEPENDENT_RELEVANCE_AND_SEMANTIC_REVIEW'))
src=ld(P/'source-binding.json');counts=ld(P/'source-counts.json')
seven=dict(
 layout='一座西门同层进入的3×3单室雪地小木屋。东北一east蓝床，东中顶阶紫晶台、东南west箱；中西短活动带。没有内梯/夹层/炉房，不拆床箱屋顶成多个实例。',
 proportion='9×8×7/DV3337，29palette/5BE/entities[]；504声明格268保存=236nonair32air、236省略unknown。floor0/use1；8层56行504位置与5PNG实际读看。y5实木屋盖、y6板阶、y7底半砖/端活板不是上层居室；床2块合1床。',
 facade='76spruce板与16多轴log构成木墙/四角框架，西2,1/2,3闭门朝west，东6,2,3一薄玻璃窗。外7,2,4east顶open活板为单侧装饰，非另一入口。两悬灯0,4,3与5,4,3照外檐/内室；类别立方图不代表原材质纹理、阶与薄件实际体积。',
 roof='沿x向单主脊，64spruce阶由北z0,y2→z1,y4→z2,y6，南z6,y2→z5,y4→z4,y6逐级收至z3,y7七个bottom半砖。x0/8两端bottom闭活板、端阶形成檐尖；y4,x2/6的axisz横梁与前挑x向log不当楼板。21snow全layers1仅基缘薄雪，无snow_block；灰类图木阶不是石瓦或厚积雪。未验防雨/雪载/热工。',
 materials='床4,1,2foot→5,1,2head/east；箱5,1,4west原vanilla snowy_house loot/seed3087418628579865941，表未在本批解析/开箱，非库存。5,1,3east顶spruce阶台上5,2,3up紫晶簇，是陈设不是火塘/供暖设备。没有炉、烟熏炉或营火；两灯不能完成NPC13夜烤火。',
 circulation='外0,0,3path上0,1,3west_up入口jigsaw最终structure_void，而0,y2/3,3省略unknown；内前1,0,3path上y1..4air。西2,1/2,3闭门下木板；内3/4,z3,y1..3air，3,0,3村民口最终木板。床脚西3,1/2/3,2air，上4顶north阶；箱西前4,1/2/3,4air，上4顶south阶。侧桌/紫晶与内部高悬灯保留，不抹成全air；静态分段不证闭门/转身/床箱操作/NPC全程路线。',
 ground_support='floor0木地及dirt/21snowytrue草缘，源下与边界外世界未知。up_west村民口引用vanilla snowy villagers，源entities[]不等已入住NPC。houses24项本栋weight1/single_pool_element/rigid/emptyprocessor，root minecraft:jigsaw size6/max80/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue，biome只引用vanilla village_snowy未读tag体。startpool三自有权98/49/149与三vanilla僵尸legacy权2/1/3只是配置；中心NBT、道路、terminator、村民/loot未读未拼，不证明自然雪山生成/地形衔接。')
limits=['本批完整原源空间研究1，不等新增有效参考1；作者主动HOLD0，待独立整栋语义/相关性审查。','NPC13雪山木屋居住/雨避仅辅助相关，缺夜间供暖；不能借雪地名称当功能已完成。','无hash命中与无exact-member历史manual命中不证明语义唯一；与249近单室住宅必须审查。','PNG为原源分类全立方可视化，非原生游戏/贴图/碰撞/天气验收；显式air和省略unknown区别保留。','1000适用参考门槛未达；COD4历史153/缺847不在本批改变；NPC13累计unknown，不相加猜数。','主清单/外部提示词/pending/ownership任务未删；没有生产/中文任务/指南针同步完成，全部任务未完成。','仅本地Python -B读取固定文件与自身研究目录；没有Java/Gradle/游戏/网络/UI/唤醒/声音亮度/焦点/用户实例存档/共享Jar/专业资产/Git/自动化操作。']
put('manual-review.json',dict(batch=298,source=src,counts=counts,scope='cod3 NPC13 巴图 大雪山木屋：居住/雨避辅助，不迁作DUN05',seven_dimensions=seven,limits=limits,actual_reading=dict(PNGs=['whole.png','cut-02.png','cut-04.png','layers.png','sections.png'],images=5,full_layers=8,full_plan_rows=56,full_declared_cells=504,sections=2,palette=29,BE=5,entities=0,JSON_contexts=3,selected_probes=65,old_seven_dimensions_read=[249,'252F03',254,256]),complete_original_spatial_study=True,new_complete_whole_studies=1,new_reference_proposals_maximum=0,formal_credit_added=0,status='AUTHOR_HOLD0_SIMILAR_SINGLE_ROOM_DWELLING',native_acceptance=False,prior297_correction=bind(P/'prior297-wording-correction.json'),prior297_main_actual_HOLD0=bind(prior_main)))
# Source checks are data validation, not acceptance or semantic credit.
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};check=[]
def ck(n,v):
 assert v,n
 check.append(dict(check=n,passed=True))
ck('counts_declaration',counts==dict(size=[9,8,7],DataVersion=3337,stored=268,nonair=236,air=32,omitted=236,palette=29,BE=5,entities=0,materials=counts['materials']))
ck('all_declared_cells',math.prod(d['size'])==268+236)
ck('29_palette_5_BE',len(pal)==29 and sum('nbt'in b for b in d['blocks'])==5)
ck('all8plans56rows',len(ld(P/'all-layers-state-index.json')['layers'])==8 and sum(len(v['rows_z'])for v in ld(P/'all-layers-state-index.json')['layers'])==56)
ck('65probes',len(ld(P/'route-probes.json'))==65)
ck('no_heating_equipment',not any(any(t in s['Name']for t in ['furnace','smoker','campfire'])for s in pal))
ck('21single_layer_snow',counts['materials']['minecraft:snow']==21 and all(s.get('Properties',{}).get('layers')=='1'for s in pal if s['Name']=='minecraft:snow'))
ck('bed_one_pair',sum(pal[b['state']]['Name']=='minecraft:blue_bed'for b in bs.values())==2)
ck('outer_upper_unknown',(0,2,3)not in bs and (0,3,3)not in bs)
ck('three_context_JSON',len(ld(P/'source-context.json')['resources'])==3)
ck('no_nonair_fingerprint_match',not ld(P/'historical-fingerprint-check.json')['matches'])
ck('four_true_name_hits_13inner_falsepositive',len(actual)==4 and len(hits)-len(actual)==13)
ck('prior297_main_HOLD0_current_hash',bind(prior_main)['sha256']=='c2a3238a4beddbcfef6a4aacce5c6e279c14c4f6e81346fd0c6946bce24c60c9')
ck('297_erratum_immutable',bind(P/'prior297-wording-correction.json')['sha256']=='dd52d673747d3a27b75294d41034eafa35dcb134dc05e189ebaea73b47a345f0')
put('validation.json',dict(checks=check,boundary='Data checks only; no native/semantic acceptance.'))
put('active-checkpoint.json',dict(batch=298,status='SNOW_HUT_WHOLE_ACTUALLY_READ_AUTHOR_HOLD0_AND_DUN05_BOUNDED_GAP_SAVED',new_complete_whole_studies=1,formal_credit_added=0,DUN05_credit_added=0,NPC13_cumulative=None,tasks_deleted=0,manual=bind(P/'manual-review.json'),gap=bind(P/'DUN05-bounded-local-gap.json'),next='Main独立审查；以后继续不同完整且适用来源，不重做本批/旧252F03/249，未达1000不制作。'))
after=[bind(p)for p in protected];assert before==after
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=298,status='SEALED_RESEARCH_ONLY_AUTHOR_HOLD0',files=files,checks=check,protected_before=before,protected_after=after,protection_boundary='只核对本次封存过程前后，非整段墙钟并发修改审计。',new_complete_whole_studies=1,formal_credit_added=0,tasks_deleted=0,prior297_main_actual_HOLD0=bind(prior_main),native_acceptance=False,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),gap=bind(P/'DUN05-bounded-local-gap.json'),files=len(files),data_checks=len(check),protected_stable=len(after)),ensure_ascii=False))

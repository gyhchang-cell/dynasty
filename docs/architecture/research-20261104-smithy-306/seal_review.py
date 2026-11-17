import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
protected=[R/'docs/cod4/audit-20261022'/v for v in ['active-workstreams.json','pending-tasks.json','continuation-20261028/session.json']]+[R/f'docs/architecture/research-20261104-smithy-{n}/RECEIPT.json'for n in [301,302,304,305]]+[Path('/Users/a15356015027/Desktop/code x提示词/cod3.txt')];before=[bind(p)for p in protected]
main301=R/'docs/cod4/audit-20261022/coordinator-building301-actual-fivePNG-whole-spatial-HOLD0-review-20261114.json';m=ld(main301);assert bind(main301)['sha256']=='0d5f9caa48c115bb469667255b6bb552b5b58ca13ed645600bc742edc564d3bf'
put('Main301-actual-review-carry0.json',dict(binding=bind(main301),actual_reading='完整Main_independent_judgments八项及新增0/门槛false已读；没有宣称逐条读Main2270数据check。',judgments=m['Main_independent_judgments'],accepted_new_effective_buildings=m['accepted_new_effective_buildings'],applicable_gate_met=m['applicable_gate_met'],carry_credit_added=0,preserved_corrections=['298全屋8床','302不误称同9×9主基'],limits='Main实际阅读301不是306独立审查或文化资格；旧guard失败不归因作者缺源。'))
seven=dict(
 layout='完整紧凑矩形小居：西门进北侧短活动区，南单床，东低阶/半砖/closed活板坐台陈设，西高架箱/盆栽；东北四格墙梯上通盖内top阶/半砖平台及另一箱。床室和储物平台一栋，不拆梯、两箱、竹子或屋盖计数；上层是储物用途，不称第二客房。',
 proportion='9×10×11/DV3953，990声明格557保存=481nonair76显式air，433省略unknown。81palette/8BE/entities[]；10层110行990格索引、7PNG/2sections已实际读看。主要floor0/use1居住与floor5/use6储物，局部底层bottom oak半砖坐台半格抬高；y7..9斜顶空腔不是三/四层居室。单床2块合1床，外竹/挑檐不等9格净房宽。',
 facade='40cherry log、13stripped spruce log/2wood与39calcite填墙、低石砖/木地；西2,1/2,4一cherry闭门，木栅窗/活板细件保留，不发明玻璃窗。外44bamboo与oak/cherry leaves绕原草土podzol边，按实体竹植而非namespace看林居语境；分类图默认灰柱可能是竹/木/叶，非纯石房。4普通lantern(1standing/3hanging)与2hanging soul灯非六个建筑。黑骷髅旗保留作者原语境，无中文屋名或中国文化资格证明。',
 roof='一套沿z长脊高双坡：y5外挑stone brick半砖/檐下open fencegate及横梁，中间3×5 top spruce阶/三top半砖为储物平台；y6外圈stone slab/两侧deepslate brick阶，y7两侧坡向x4收，y8两侧x3/5阶夹中空，y9 x4,z2..8 bottom deepslate brick半砖及z1/9端阶封脊。76深砖阶/36石砖半砖/13深砖半砖为材频，不拆参考数；不是茅草顶，也未证雪载/防雨/全檐可达。',
 materials='4,1,6foot→4,1,7head/south粉床，5,1,7south陶罐仅id。西3,4,3east箱原cherry_house seed-8543576423172916878，下3,3,3top closed活板；上5,6,5west箱同表seed5299416499089540302，下5,5,5top east spruce阶。东5,1,z4/6底阶、y1 bottom oak半砖及y2三closed活板为低坐台/陈设，无茶具棋盘实证。3,6,3bamboo mosaic与5,7,6dried kelp block不当库存/茶食品；无炉/营火，不做猎户烤火结论。',
 circulation='西0,1,4原入口jigsaw最终structure_void，上0,y2/3,4均省略unknown；1,y1/2/3,4实air，2,y1/2,4闭门，内3,1/2,4air而3,3,4top闭活板不是air。东北5,y1..4,3四west梯，东6,y2..4,3calcite背墙；5,5,3top west活板openfalse封梯顶，上5,y6/7,3air。拟上踏4,5,3top north阶，接4,5,z4/5top spruce半砖，其y6/7air；需要开梯盖并验碰撞，未称原态全程通行。上箱西前4,6/7/8,5air，箱上5,7,5air但5,8,5west底深砖阶；西高箱东前4,4,3air但4,5,3顶阶、下4,3,3air无该标高楼面，不冒称西箱已正常可取。床脚前4,1,5bottom半砖，床/门/箱/NPC未运行验收。',
 terrain='原低草土podzol裙与石砖入口随整体保存，源下y-1和边界外未知，竹生长/叶衰减不当实际运行状态。唯一up_west村民口4,0,4最终oak板，原entities[]不等已经入住/永不生成。五context JSON与304已全文实际读资源逐对象完全一致，只复用不重计参考；本屋houses22项selected weight2/single_pool/rigid/empty，root size6/max80/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue，3towncenter各1、optional cherry_grove。原loot十项3..8roll表复用，未roll/发放/付费；villager池、中心/街道/终止件NBT未读未拼，不能冒称自然竹林生境/中文任务指南针或入住AI已验。')
limits=['本批完整原源研究1，最多提出1个竹林小居/储物交通的辅助候选，正式信用0，待Main独立用途/整栋语义审查；不是严格中国茅屋或徽派合格。','与249无梯隐桶低木居/301小方室无上交通已实际比较；小居/瓦木架同作者家族风险保留，单加梯/箱/竹色不足独立信用。','上下生活/储物组织与297双层四床、304三层客栈用途不同，不重做旧PNG/原源；Main301独立HOLD0及298/302更正只carry0。','全81palette Properties/8BE/10原层/7分类图已读；半砖、阶、梯、活板和竹植在cube图被立方化，不是原纹理/原生碰撞或视觉验收。','433省略不是air；特别入口头格unknown不能延伸内部air抹平。梯盖关闭是源状态，没有为参考擅改模型/关卡或判运行bug。','适用1000未达，旧累计不清零；COD4历史153/缺847本批不增加，各NPC主题总量unknown。未删任务/未完成总体。','只本地Python -B读固定资料、自身306写；无Java/Gradle/游戏/网络/UI/唤醒/声音亮度/焦点/用户实例原档/共享Jar/专业资产/主清单/session/Git/自动化操作。']
put('manual-review.json',dict(batch=306,source=ld(P/'source-binding.json'),counts=ld(P/'source-counts.json'),task_source=bind(Path('/Users/a15356015027/Desktop/code x提示词/cod3.txt')),scope='NPC03竹林茅屋：林居/夜回屋/雨避及储物交通辅助，不声明茅草/棋茶/中国文化资格',seven_dimensions=seven,limits=limits,pre_render_family_check=bind(P/'pre-render-family-check.json'),context_reuse=bind(P/'context-reuse.json'),actual_reading=dict(PNGs=['whole.png','cut-02.png','cut-04.png','cut-06.png','layers-00.png','layers-05.png','sections.png'],images=7,layers=10,rows=110,declared_cells=990,palette=81,BE=8,entities=0,selected_probes=96,full_contexts_reused_unchanged_from_prior_actual_reading=5,new_context_selected_entry_actually_read=True,old249_whole_seven_dimensions=True),complete_original_spatial_study=True,new_complete_whole_studies=1,broad_dwellings_reference_proposal_maximum=1,formal_credit_added=0,strict_Chinese_reference_credit_added=0,status='HOLD0_PENDING_INDEPENDENT_RELEVANCE_AND_SEMANTIC_REVIEW',native_acceptance=False))
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};checks=[]
def ck(n,v):
 assert v,n
 checks.append(dict(check=n,passed=True))
ck('990range557stored433unknown',math.prod(d['size'])==990 and len(bs)==557 and 990-len(bs)==433)
ck('481nonair76air',sum(pal[b['state']]['Name']!='minecraft:air'for b in bs.values())==481)
ck('81palette8BE',len(pal)==81 and sum('nbt'in b for b in bs.values())==8)
ck('10plans110rows',len(ld(P/'all-layers-state-index.json')['layers'])==10 and sum(len(v['rows_z'])for v in ld(P/'all-layers-state-index.json')['layers'])==110)
ck('96probes2unknown',len(ld(P/'route-probes.json'))==96 and sum(v['state']is None for v in ld(P/'route-probes.json'))==2)
ck('four_ladder_exact',all(pal[bs[5,y,3]['state']]['Name']=='minecraft:ladder'for y in range(1,5)))
ck('ladder_cap_closed_top',pal[bs[5,5,3]['state']]['Properties']==dict(half='top',waterlogged='false',powered='false',facing='west',open='false'))
ck('loft_twohigh_at_selected_landing',all(pal[bs[4,y,z]['state']]['Name']=='minecraft:air'for y in [6,7]for z in [3,4,5]))
ck('one_south_bed_pair',pal[bs[4,1,6]['state']]['Properties']['part']=='foot'and pal[bs[4,1,7]['state']]['Properties']['part']=='head'and pal[bs[4,1,7]['state']]['Properties']['facing']=='south')
ck('ordinary4_soul2_lights',sum(pal[b['state']]['Name']=='minecraft:lantern'for b in bs.values())==4 and sum(pal[b['state']]['Name']=='minecraft:soul_lantern'for b in bs.values())==2)
ck('5identical_contexts_reused',ld(P/'source-context.json')==ld(R/'docs/architecture/research-20261104-smithy-304/source-context.json'))
ck('Main301carry0',m['accepted_new_effective_buildings']==0 and not m['applicable_gate_met'])
put('validation.json',dict(checks=checks,boundary='Data checks only; no native or semantic credit.'))
put('active-checkpoint.json',dict(batch=306,status='COMPLETE_DWELLING_SOURCE_ACTUALLY_READ_PENDING_INDEPENDENT_REVIEW',new_complete_whole_studies=1,broad_dwellings_reference_proposal_maximum=1,formal_credit_added=0,strict_Chinese_reference_credit_added=0,tasks_deleted=0,manual=bind(P/'manual-review.json'),Main301_actual_review=bind(main301),next='不重复301/305/306或把梯/层/箱拆计。后续先审相近完整本地源的用途/原家族，文化资格不足不强行增信用；未达1000不生产。'))
after=[bind(p)for p in protected];assert before==after
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',dict(batch=306,status='SEALED_COMPLETE_DWELLING_STUDY_PENDING_INDEPENDENT_REVIEW',files=files,data_checks=checks,protected_before=before,protected_after=after,protection_boundary='本次封存前后稳定性，不冒称整段并发墙钟审计。',new_complete_whole_studies=1,broad_dwellings_reference_proposal_maximum=1,formal_credit_added=0,strict_Chinese_reference_credit_added=0,tasks_deleted=0,native_acceptance=False,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_stable=len(after)),ensure_ascii=False))

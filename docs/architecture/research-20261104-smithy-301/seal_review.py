import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
protected=[R/'docs/cod4/audit-20261022'/x for x in ['active-workstreams.json','pending-tasks.json','continuation-20261028/session.json']]+[R/f'docs/architecture/research-20261104-smithy-{n}/RECEIPT.json'for n in [297,298,299,300]]+[Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt')];before=[bind(p)for p in protected]
old=R/'docs/architecture/research-20261101-dungeons-007/manual-review.json';F04=next(x for x in ld(old)['entries']if x['id']=='F04');old297=R/'docs/architecture/research-20261104-smithy-297/manual-review.json';corr=R/'docs/architecture/research-20261104-smithy-298/prior297-wording-correction.json';s297=ld(old297)['seven_dimensions'].copy();s297['proportion']=s297['proportion'].replace('底层8床块','全屋8床块')
put('whole-comparison.json',dict(prior007F04=dict(binding=bind(old),seven_dimensions_actually_read=F04['observations'],old_status=F04['status'],formal_credit=F04['formal_credit_added']),prior297=dict(binding=bind(old297),prior_wording_correction=bind(corr),seven_dimensions_actually_read=s297),comparison='本栋和007F04同9×9主基/四外柱/西2,2,4门/内3×3小室/浅墙深檐家族。本栋少叠层，换白床与灯台，东添单个分级灌溉菜地；不能凭住房用途、减屋盖、外接菜地或不同hash自动加独立建筑。297是真双生活层且有内梯，本栋只floor1/use2，屋顶空腔没有内梯或可用上层。',decision='AUTHOR_HOLD0_PRIOR_FAMILY_RISK_NO_INDEPENDENT_REFERENCE_PROPOSAL',new_complete_whole_studies=1,new_reference_proposals_maximum=0,formal_credit_added=0,limits='只复用已读旧完整七维文字，不重开旧NBT/PNG、不新增旧信用。'))
put('purpose-qualification.json',dict(source=ld(P/'source-binding.json'),task=bind(Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt')),original_scope='cod2 DUN05 外郭鬼市：废弃民居瓦顶/古代街巷的建筑空间辅助学习',qualification_basis=['实际完整住宅：一对同向白床、唯一西门、独立小室与低石基；不是床/门/屋盖组件。','实际浅色calcite填墙、spruce柱梁、深板瓦半砖/阶收束屋盖、挑檐外柱，按实体形态可作广义东亚小住宅辅助空间研究。','东侧八格不同标高耕地及水渠为附属种植空间，未围合院落、无店铺柜台或客栈功能。'],pre_render_evidence='尺寸/完整材料频次/4BE先读，床门支持住宅候选；再通过5PNG/全层核读确认，未仅按namespace授资格。',qualification='QUALIFIED_FOR_BROAD_EAST_ASIAN_DWELLING_SPATIAL_STUDY_ONLY',strict_gate='NOT_QUALIFIED_AS_STRICT_HUI_GHOST_CITY_RESIDENCE_OR_INDEPENDENT_DESIGN_CREDIT',limits=['没有徽派马头墙、中华密集商街/相连屋顶路线与鬼城经营语境证明，不能充中国建筑1000门槛。','原源是具体作者村落住宅，学习布局/比例/材质组织，不复制接入生产，不改名冒充原创。'],formal_credit_added=0))
seven=dict(
 layout='完整单室民宅，西闭门入3×3小室，南east白单床，北东顶半砖灯台/白地毯；东外单个分级菜地连水渠。菜地不与室内直通，非第二房、围合院落、店铺或客栈；整体仅一源实例。',
 proportion='12×8×9/DV3105；864范围全部保存=286nonair578显式air，0省略。60palette/4BE/entities[]；8层72行864源状态索引、5PNG和2剖面全读看。floor1/use2单生活层，y4九个top birch半砖封顶，y5以上木梁/栏/瓦盖不称阁楼。外菜地伸长x方向不等12格居室宽；床两块合一床。',
 facade='31calcite白填墙、26多轴spruce log配石基/木地，四外柱1/7,z1/7由石墙/栅撑檐；西2,2/3,4一闭birch门，北/南4,3,z2/6与东6,3,4为木栅窗格，没有玻璃窗。三灯：室内5,3,3standing与菜地9,2,z2/6standing，不是悬灯。图是原源分类立方可视化，不是原生材质/薄件形状。',
 roof='同一主室四向收束深色屋盖：y4北/南檐带top tile/brick半砖、檐下closed fencegate与tile墙端，y5内收tile板和bottom檐缘半砖；y6四向阶含inner角连接，y7bottom brick半砖形成x1..7/z4与x4/z2..6交叉顶饰。房内y4 top birch半砖封顶，上方中心空腔不是可住二层；角柱不拆四栋、檐门不当十个住宅入口。未验防雨/结构承载/原生外观。',
 materials='4,2,5foot→5,2,5head/east白床；5,2,3top spruce半砖台上5,3,3standing灯，4,2,3白地毯。无箱/炉/营火，不需要为住宅研究强套猎户烤火，但不能声称居住行为/供暖已验。8farmland全moisture7、8wheat全age7，6water保留level0/1/2/8，不称六块水源或已实际收成。原无loot容器，不能伪造材料获取/交易回执。',
 circulation='西0,1,4west_up接街jigsaw最终structure_void；其上y2/3/4源air，下0,0,4cobble。1,1,4east底cobble阶上y2/3air，接2,1,4cobble门槛、2,y2/3,4闭门；内3..5,z4,y2/3air。床脚西3,2/3,5air、上3,4,5top birch半砖；北4,2,3地毯非air，灯台占东北。东6,2,4calcite且6,3,4fence，无后门；不能从室内直接走菜地水渠或凭邻air声称床操作/NPC路网走通。',
 terrain='主体floor1木地/村民口贴低石基和dirt，西外梯接街接口未读取邻街；四外撑脚与菜地原标高保留。东x7/8,z3/5耕地y1，x9/10,z3/5耕地y0；渠源7,1,4level0向8/9,y1及10,0延展，两处y0level8保留，不能当天然河岸/已运行流体。源y-1与边界外未知。唯一up_west村民口4,1,4最终birch板、vanilla plains villagers未解析，entities[]不等已入住居民。houses28项本栋weight4/legacy_single/rigid/mossify10，root size6/max116/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue，towncenter50/25及花林+15optional biome配置不等生成现场；街道/中心NBT、处理器体未读未拼。')
limits=['完整原源空间研究1，不是新增独立有效参考1；同007F04家族风险作者主动HOLD0，不提出独立信用。','用途已通过真实卧室/入户/木构白墙深檐判断为广义东亚民居辅助，不充严格徽派/中国建筑1000。','无主清单删除/生产/中文任务或指南针接入验收；总体任务未完成。','保留旧适用研究，不每批清零；COD4历史153/缺847不在本批改变，其他主题累计unknown。','全范围显式air与世界外unknown区分，薄件/液体/门状态未以cube图片替换原值。','静态资料/PNG不等原生游戏视觉、碰撞、天气、行为或获取回执。','只本地Python -B读固定归档与旧研究、自身301目录写；无Java/Gradle/游戏/UI/网络/声音亮度唤醒焦点/用户实例原存档/共享Jar/专业资产/主清单/session/Git/自动化变更。']
put('manual-review.json',dict(batch=301,source=ld(P/'source-binding.json'),counts=ld(P/'source-counts.json'),purpose_qualification=bind(P/'purpose-qualification.json'),seven_dimensions=seven,limits=limits,actual_reading=dict(PNGs=['whole.png','cut-03.png','cut-05.png','layers.png','sections.png'],images=5,full_layers=8,full_rows=72,full_declared_cells=864,sections=2,palette=60,BE=4,entities=0,JSON_contexts=4,selected_probes=78,old_full_observations=['007F04','297seven with298erratum']),complete_original_spatial_study=True,new_complete_whole_studies=1,new_reference_proposals_maximum=0,formal_credit_added=0,status='AUTHOR_HOLD0_PRIOR_DESIGN_FAMILY_AUXILIARY_STUDY_ONLY',native_acceptance=False))
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};checks=[]
def ck(n,v):
 assert v,n
 checks.append(dict(check=n,passed=True))
ck('864stored_noomitted',len(bs)==math.prod(d['size'])==864)
ck('286nonair578air',sum(pal[b['state']]['Name']!='minecraft:air'for b in bs.values())==286)
ck('60palette4BE',len(pal)==60 and sum('nbt'in b for b in bs.values())==4)
ck('8layers72rows',len(ld(P/'all-layers-state-index.json')['layers'])==8 and sum(len(v['rows_z'])for v in ld(P/'all-layers-state-index.json')['layers'])==72)
ck('78probes',len(ld(P/'route-probes.json'))==78)
ck('one_bed_pair',sum(pal[b['state']]['Name']=='minecraft:white_bed'for b in bs.values())==2)
ck('8wheat8farmland6water',all(ld(P/'source-counts.json')['materials']['minecraft:'+n]==k for n,k in [('wheat',8),('farmland',8),('water',6)]))
ck('eastwall_notdoor',pal[bs[(6,2,4)]['state']]['Name']=='minecraft:calcite')
ctx=ld(P/'source-context.json')['resources'];ck('4JSONcontexts_28houseentries',len(ctx)==4 and len(ctx[1]['json']['elements'])==28)
ck('5images_exist',all((P/f).is_file()for f in ['whole.png','cut-03.png','cut-05.png','layers.png','sections.png']))
ck('prior007F04_old0',F04['formal_credit_added']==0)
ck('old297_erratum_preserved',bind(corr)['sha256']=='dd52d673747d3a27b75294d41034eafa35dcb134dc05e189ebaea73b47a345f0')
put('validation.json',dict(checks=checks,boundary='Only data checks, not semantic/native acceptance.'))
put('active-checkpoint.json',dict(batch=301,status='COMPLETE_EAST_ASIAN_DWELLING_SOURCE_ACTUALLY_READ_AUTHOR_HOLD0',new_complete_whole_studies=1,new_reference_proposals_maximum=0,formal_credit_added=0,tasks_deleted=0,manual=bind(P/'manual-review.json'),next='Main独立实际空间/相关性/同族审查；本栋不重做，不把住宅床/菜地/层图当多参考；未达1000不制作。'))
after=[bind(p)for p in protected];assert before==after
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',dict(batch=301,status='SEALED_COMPLETE_WHOLE_STUDY_AUTHOR_HOLD0',files=files,data_checks=checks,protected_before=before,protected_after=after,protection_boundary='本次封存过程前后稳定性，不声称审计整段并发墙钟。',new_complete_whole_studies=1,new_reference_proposals_maximum=0,formal_credit_added=0,tasks_deleted=0,native_acceptance=False,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),data_checks=len(checks),protected_stable=len(after)),ensure_ascii=False))

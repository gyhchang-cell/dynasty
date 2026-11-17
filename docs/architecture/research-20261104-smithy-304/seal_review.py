import json,hashlib,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
def ld(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
protected=[R/'docs/cod4/audit-20261022'/v for v in ['active-workstreams.json','pending-tasks.json','continuation-20261028/session.json']]+[R/f'docs/architecture/research-20261104-smithy-{n}/RECEIPT.json'for n in [297,301,302,303]]+[Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt')];before=[bind(p)for p in protected]
seven=dict(
 layout='完整长矩形旅宿楼：底层双门迎客通公共座椅/三桌区，北部有一道oak门分隔的陈设小间，东侧长直阶到中层后转西继续向高睡层；中层北三张粉床、顶层北三张红床。原吊牌front Traveller\'s/Inn/OPEN，back CLOSED，是原旅宿用途证据，不是仅从文件名推断。两排床不是六独立客房，三个标高/边檐/装饰盆不拆建筑。',
 proportion='13×15×18/DV3953，3510声明格=2027保存(1487nonair540air)+1483省略unknown。138palette/37BE/12独特payload/entities[]；15层270行3510原索引、8PNG及2section已实际读。实际使用有地层floor0/use1、中层floor5/oak top半砖及局部y6 bottom半砖、上层floor9/spruce top半砖及局部y10 bottom半砖；不是整层统一高度。床底y6和y10，两处各三床，共12床块6床；y11..14斜顶空腔不另算生活层。',
 facade='165cherry log及82多轴stripped oak log配48calcite白填墙、低石裙与竹植/木格窗，底层外西2,1/2,z8/9成对cherry门，东10,1/2,4单cherry门朝west；6,1/2,4是室内分隔oak门。共4门扇而非4外入口。14lantern/5decorated pot、黄红纹/黑白骷髅纹/白底红圆旗与英语招牌保留作者原语境，不能称中文招牌或据浅墙深盖宣称徽派建筑。',
 roof='上下两大檐与一条沿z长主脊：y4外圈top deepslate brick slab，y5内圈bottom brick slab/砖带；上部y9梁檐、y10宽tile/brick半砖环带收至y11..13两侧deepslate brick阶及端tile阶，y14 x6,z3..14 bottom tile半砖封脊、z2/15端阶。175brick slab/86tile slab/72brick stair/32tile stair是屋盖与其他细构件总材频，不等全为独立瓦构。屋顶腔内上三床确有交通意图，不把整个高盖当额外阁楼或檐环已可跑酷。',
 materials='三粉床x5/6/7,y6,z4head→z5foot/north；三红床同x/z但y10。三桌：3/5,1,13与7,1,10的fence脚上y2 oak pressureplate、各南北底阶座。北死珊瑚扇仅装饰，不当残羹或黑饭。三箱9,1,10south、4,11,4south、8,11,9west均cherry_house loot，seed分别-156941198724378421/-6630783505281658004/-2081777572412565994；5pots只有id，未声称食物/交易库存。源无炉/营火，烛/灯不等制作台或供暖。',
 circulation='西0,1,8原jigsaw最终air，0,y2/3与1,y1/2/3,8实air；2,y1/2,z8/9闭双门，内3,1/2,8air而y3顶闭活板。南向阶8,1,8→8,2,9→8,3,10→8,4,11→8,5,12，接8,5,13木台；转west 7,6,13→6,7,13→5,8,13→4,9,13，每阶自上两格源air。中层与上层分别有半砖叠面，顶落脚4,9,12top spruce上y10/11air，邻5,10,12fence不当任意全空。床脚前6,6,6/6,10,6为bottom半砖，非air，保留半格过渡。高箱下4,10,4double spruce与8,10,9scaffolding，南前4,11,5/西前7,11,9air但斜顶原阶压低；选格4,13,4/5及8,13,9省略unknown。静态路段不证门动作、转身/碰撞、床箱使用或NPC全路径。',
 terrain='源低石/草土podzol裙、底木地与竹植边缘保存，y-1及边界外未知；地层不是落地实机地形。5jigsaw为1西入口+4村民口：4,0,z7/9最终stripped_oak_log[axis=x]，6,9,z9/10最终top spruce slab，非已生成住客。root minecraft:jigsaw size6/max80/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue，houses22项本栋weight8/single_pool/rigid/emptyprocessor；三towncenter各权1，biome只optional cherry_grove。loot3..8roll十种原物品表及random_sequence原拼写vilage保留，未开箱未证明付费来源。中心/街道/终止件NBT和原vanilla villagers池未读未拼，JSON不等自然生成/客栈营业或任务中文同步。')
limits=['完整原源空间学习1；广义东亚旅宿/公共厅—两睡层组织可提出最多1候选，正式信用0，待Main独立用途/整栋语义审查。','严格DUN05中式志怪/徽派客栈仍HOLD0；没有马头墙、鬼市密巷与连通屋顶/黑饭或纸扎人。不得拿日本语境/床数/三层/材质或不同文件hash补中国建筑1000。','与007F01同作者长框白墙深盖相似性保留，但该旧书屋无内梯可达上层；与297双层四床小方室、301小单室菜地、165中央柱双折转工住层分配实际比较先于render。','138palette全部Properties/37BE与12payload/15原层索引/8分类原源PNG实际读；PNG把半砖/台阶/薄件画成类别立方，不是原贴图或原生游戏验收。','固定Jar身份与DataVersion3953仅原源证据，不声称当前运行兼容性；无Java/Gradle/游戏/网络/UI/唤醒/声音亮度/焦点/实例/存档/共享Jar/专业资产/主清单/session/Git/自动化操作。','保留旧累计，COD4历史153缺847不在本批增加，广义客栈/其他主题累计unknown；门槛未达不制作、不删提示词/镜像/pending/ownership。']
put('manual-review.json',dict(batch=304,source=ld(P/'source-binding.json'),counts=ld(P/'source-counts.json'),task_source=bind(Path('/Users/a15356015027/Desktop/code x提示词/cod2.txt')),task_scope='DUN05客栈桌饭/民居瓦顶：广义东亚旅宿空间辅助，严格徽派未合格',pre_render_family_check=bind(P/'pre-render-family-check.json'),seven_dimensions=seven,limits=limits,actual_reading=dict(PNGs=['whole.png','cut-03.png','cut-07.png','cut-11.png','layers-00.png','layers-05.png','layers-10.png','sections.png'],images=8,layers=15,rows=270,declared_cells=3510,palette=138,BE=37,unique_payloads=12,entities=0,JSON_contexts=5,selected_probes=128,old_whole_observations=['007F01','165F01','297 with298erratum','301 with302erratum']),complete_original_spatial_study=True,new_complete_whole_studies=1,broad_inn_reference_proposal_maximum=1,strict_Hui_reference_credit_added=0,formal_credit_added=0,status='HOLD0_PENDING_INDEPENDENT_RELEVANCE_AND_SEMANTIC_REVIEW',native_acceptance=False))
d=ld(P/'source-original.json');pal=d['palette'];bs={tuple(b['pos']):b for b in d['blocks']};checks=[]
def ck(n,v):
 assert v,n
 checks.append(dict(check=n,passed=True))
ck('3510declared2027stored1483unknown',math.prod(d['size'])==3510 and len(bs)==2027 and 3510-len(bs)==1483)
ck('1487nonair540air',sum(pal[b['state']]['Name']!='minecraft:air'for b in bs.values())==1487)
ck('138palette37BE',len(pal)==138 and sum('nbt'in b for b in bs.values())==37)
ck('12payloads',len(ld(P/'BE-payload-reading-index.json')['payloads'])==12)
ck('15layers270rows',len(ld(P/'all-layers-state-index.json')['layers'])==15 and sum(len(v['rows_z'])for v in ld(P/'all-layers-state-index.json')['layers'])==270)
ck('128probes3unknown',len(ld(P/'route-probes.json'))==128 and sum(v['state']is None for v in ld(P/'route-probes.json'))==3)
ck('6beds_correct_pairs',all(pal[bs[(x,y,4)]['state']]['Properties']['part']=='head'and pal[bs[(x,y,5)]['state']]['Properties']['part']=='foot'for y in [6,10]for x in [5,6,7]))
ck('9stair_pairs_headroom',all(pal[bs[(x,y+h,z)]['state']]['Name']=='minecraft:air'for x,y,z in [(8,1,8),(8,2,9),(8,3,10),(8,4,11),(8,5,12),(7,6,13),(6,7,13),(5,8,13),(4,9,13)]for h in [1,2]))
ck('3tables_and_no_heating',sum(v['Name']=='minecraft:oak_pressure_plate'for v in pal)==1 and not any(any(t in v['Name']for t in ['furnace','smoker','campfire'])for v in pal))
ctx=ld(P/'source-context.json')['resources'];ck('5JSON22houses',len(ctx)==5 and len(ctx[1]['json']['elements'])==22)
ck('one_selected_house_weight8',sum(v.get('weight',0)for v in ctx[1]['json']['elements']if v['element'].get('location')=='trek:village/cherry/houses/cherry_big_house_1')==8)
ck('no_historical_fingerprint_match',not ld(P/'historical-fingerprint-check.json')['matches'])
put('validation.json',dict(checks=checks,boundary='Data checks only, no self semantic/native acceptance.'))
put('active-checkpoint.json',dict(batch=304,status='COMPLETE_ORIGINAL_INN_ACTUALLY_READ_PENDING_INDEPENDENT_REVIEW',new_complete_whole_studies=1,broad_inn_reference_proposal_maximum=1,formal_credit_added=0,strict_Hui_reference_credit_added=0,tasks_deleted=0,manual=bind(P/'manual-review.json'),next='先独立审查本候选。下一明确范围：RS bamboo medium_house_1先主题/旧家族核查，不默认bamboo命名即中国古建；不重计本栋/小方屋/同族覆雪。'))
after=[bind(p)for p in protected];assert before==after
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',dict(batch=304,status='SEALED_COMPLETE_INN_SOURCE_STUDY_PENDING_INDEPENDENT_REVIEW',files=files,data_checks=checks,protected_before=before,protected_after=after,protection_boundary='本次封存前后稳定性，不冒称整段并发墙钟审计。',new_complete_whole_studies=1,broad_inn_reference_proposal_maximum=1,formal_credit_added=0,strict_Hui_reference_credit_added=0,tasks_deleted=0,all_tasks_complete=False,native_acceptance=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),data_checks=len(checks),protected_stable=len(after)),ensure_ascii=False))

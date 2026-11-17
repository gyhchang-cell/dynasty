"""Seal a single author complex study, not nine reference credits."""
import json,hashlib,sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
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
inventory=ld(P/'source-inventory.json');graph=ld(P/'source-socket-graph.json');counts=ld(P/'assembled-source-counts.json')
ck('fixed archive unchanged',bind(inventory['archive']['path'])==inventory['archive'])
ck('fixed metadata index unchanged',bind(inventory['source_index']['path'])==inventory['source_index'])
with ZipFile(inventory['archive']['path'])as z:
 for row in inventory['templates']:
  raw=z.read(row['member']);ck('original9 '+row['key'],hashlib.sha256(raw).hexdigest()==row['raw_nbt_sha256'] and bind(row['binding']['path'])==row['binding'] and read(raw)==ld(row['binding']['path']))
 for row in ld(P/'source-context.json')['resources']:
  raw=z.read(row['member']);ck('full source context '+row['member'],hashlib.sha256(raw).hexdigest()==row['sha256'] and raw.decode()==row['text'] and json.loads(raw)==row['json'])
ck('one source graph nine placements seven templates eight edges',len(graph['placements'])==9 and len({p['key']for p in graph['placements']})==7 and len(graph['edges'])==8)
ck('all exact target-name relations',all(e['name_target_match']and e['parent_socket']['nbt']['target']==e['child_socket']['nbt']['name']for e in graph['edges']))
ck('source boxes disjoint, no cell overwrite',graph['box_intersections']==[] and graph['stored_cell_overlap_count']==0)
ck('graph source accounting',counts['size']==[94,39,94]and counts['stored_cells']==133074 and counts['nonair_cells']==42766 and counts['unknown_cells']==211530)
ck('nine source drawings and nine actual view boundary',len(list(P.glob('*.png')))==9 and ld(P/'active-checkpoint.json')['images_actually_viewed']==9)
history=ld(P/'history-own-record-search.json');ck('278 bounded own histories no match',len(history['paths'])==278 and history['hits']==[])
for prior in ld(P/'prior-whole-comparisons.json')['prior']:ck('old whole preserved '+Path(prior['binding']['path']).parent.name,bind(prior['binding']['path'])==prior['binding'])
BE=ld(P/'all-BE-lossless-groups.json');entities=ld(P/'all-entity-originals.json');palette=ld(P/'all-palette-properties.json')
ck('source payload position counts',len(BE)==22 and sum(len(g['positions'])for g in BE)==58 and len(entities)==17 and len(palette)==32)
status='SEALED_AUTHOR_NINE_PLACEMENT_SINGLE_COMPLEX_STUDY_DUN07_PARTIAL_HOLD0'
review=dict(
 batch=292,status=status,source=inventory['archive'],source_identity='legendary_monsters:cloudy_temple root jigsaw → cloudy_temple/start JSON → cloudy_temple_arena, 4 radial wings, 4 repeated mini placements',source_author_attribution='Creativejan is preserved verbatim in source CORNER structure-block author fields; no outside author-profile or website verification claimed.',
 new_complete_whole_studies=1,new_qualifying_reference_proposals=0,formal_credit_added=0,source_templates_used=7,source_placements=9,source_component_credit=0,
 scope='cod2 DUN07 冲霄隐仙观：宗教建筑群的中央场所—四翼厅廊—附属亭台布局原则。尚不足作为前岛水池—中岛炼丹天阙—后岛八卦绝顶与悬空云桥的完整相关参考入账。',
 author_connection_reading=[
  '实际根start_pool选arena；同名cloudy_temple.nbt无jigsaw，不是本次根。cloudy_temple.txt仅作为原文本阅读，不能把它当成被根引用的JSON池。part455未被已读part4池引用，禁止替换真正part4或另算一设计。',
  '8条父pool→唯一weight候选→子name精确关系均读取，front相向、joint rollable、rigid/empty处理器；最大树深2，不把size7写成7个建筑。part4池weight2且只有单候选，不会生成两座part4。',
  '原始arena放0,0,0；part3偏移(-27,0,7)、part4(6,0,-27)、part2(7,0,40)、part1(40,0,7)；附属mini2在part3处转90度、mini1在part2处转180度，其他0。每条原口、期望相邻口、偏移与包围盒完整保存。',
  '九份placement包围盒互不相交，原存坐标无覆盖；整个源格包围94×39×94。只做研究坐标复原，未生成新NBT、游戏建筑或执行生成器。方块facing/shape、实体yaw仍保留原局部状态，图仅类别立方体，不能当旋转后游戏状态。'
 ],
 observations=dict(
  layout='中央近圆形高祭坛/竞技围场，四个径向长厅廊接其四面，外翼再接小亭/方池式附属构筑，形成十字主轴与角部附属节点。四翼高度、顶部小亭与室内陈设不全相同，但它们属于一座既有组合建筑群，不拆为9例；两mini重复安放不增设计。',
  proportion='源格整体94×39×94；中央arena保存40×39×40，东西翼较高、南北翼较低、附属亭台更低。主体实际空间从低部约y3平台开始，中央高台约y19支承、Boss源位置y20；保存最高y38为空气，不能误称39层塔。',
  facade='多列独立白石柱与通透侧廊形成外围节奏，青绿与浅色玻璃带夹在厚水平板层间；中央环形立柱、尖饰比四翼外廊更密。原模组柱、楼梯、墙和薄板实际轮廓需原生材质/模型，分类图不证明精细柱身或透明遮挡效果。',
  roof='侧翼宽低坡阶状厚檐盖上，东西两翼另叠小型上亭，中央是高环形开放围场/冠状构件，不是中式八卦亭的完整有顶屋面。y14玻璃连续带、y18/19厚平台与高柱之间区别保存，不能把所有实心平面称可达屋顶。',
  materials='主体polished_diorite与diorite/台阶/半砖，legendary_monsters:polished_diorite_pillar三轴原状态，dark_prismarine、white/gray/light_gray/black stained_glass、sea_lantern，以及少量铁金钻紫晶、书架和水。32材料组及其原属性全部读；没有将玻璃填料称真实云雾、将原柱ID猜成Dynasty注册ID。',
  circulation='四主接口全在y4，脚下arena y3为bottom dark_prismarine_stairs、厅廊y3为polished_diorite，两侧y5/6为显式air；源接头final air。64条足/接头/头部单元均读，但不等于整个门宽/侧障碍验收。附属四接口在y0或y1，有未存的脚下/上方单元，不能据jigsaw成功就称通路安全。所有7用模板无门/梯/脚手架；四翼>=3连续直阶主要只在y1..3，mini2有0..4阶，arena无>=3直阶且缺大量中间阶级。不能宣称已有通到y20 Boss的连续楼梯；也不能只因直段算法没找到就证明不存在跳跃/特殊机制路径。',
  terrain='原tag含山地、meadow/cherry_grove等与可选aether:skyroot_meadow，但根仍WORLD_SURFACE_WG、absolute0、beard_box。名称cloudy和透明填料不证明实际悬空岛群；九模板根下外部入场、山体穿插、实际生成边界及维度/群系注册未验。原spacing70/separation50/salt443951123只记配置，不推导玩家找到位置或实际稀有度。'
 ),
 actual_reading=dict(
  png_actually_viewed=[bind(p)for p in sorted(P.glob('*.png'))],current_png_actually_viewed=9,plan_layers_actually_viewed=[0,1,3,4,5,7,10,14,18,22,26,30,34,35,37,38],full_height_section_planes=['x20','z19'],whole_or_cut_isometric_sheets=4,
  source_context='12 complete JSON/text resources read, including biome+locate tag, root, structure_set and7 referenced pools plus unused .txt; source loot JSON and advancement not read.',
  palette='All32 used-template unique material/property groups read. Local directional properties retained, not transformed to native final states.',
  BE='All22 unique payloads read covering58 placed positions:16 lecterns with blank writable books,14 loot-reference chests,6 empty barrels,16jigsaws and6 CORNER structure blocks. Position grouping is lossless; not58 independent interaction tests.',
  entities='All17 placed identity/position/health/persistence/held/armor profiles read, not all full attributes or capabilities: cloud_golem1, hovering_hurricane4, stratling12. Repeated source templates repeat original records; no runtime spawn, UUID handling, balance or model acceptance claimed.',
  routes='All8 graph edge definitions and64 exact source floor/head states read; bottom-stair y histograms and direction/height/length groups read, with selected runs. All89 individual long flights not each manually inspected, and flights/components count0.',
  history='278 own/manual/proposal/scope/candidate/full-building source records checked, no direct current family entry found. Does not cover all semantic aliases or all chat images. Full previous291 seven observations/limits and old002F09 own seven observations/limits read, no old image reopening.'
 ),
 comparison='Central circular arena with four radial colonnaded wings and repeated corner annexes differs from291 asymmetric stacked halls/side stair tower and old002F09 axial lower hall/central upper pavilion. Family and whole layout are distinct in the bounded record search. Mini1/mini2 duplicates and mirrored/repeated motifs remain ONE complex; novelty is not inferred from file count or hashes.',
 relevance_decision='HOLD0：完成原作者一组建筑群的完整空间研究，保留中央—四翼—附属节点原则。但目标DUN07的三岛先后、环炉主殿、八卦终台与空中进出/回程未被本源证明，且本源实际按地表heightmap定位。不能提前把9placement计9，也不自动计1合格目标参考。',
 applications=[
  '门槛满足后可参考中央地标与有差异的四向支翼形成方位识别；附属亭台尺度收小，不与主殿争夺重心。',
  '把檐盖、玻璃带、上层平台和实际可用行走面分开设计；上下层动线必须有明确路线，不以Boss保存位置冒充玩家可达证据。',
  '接头配对解决来源组合关系，现场坡地、缺失脚下、入口和回程另验。目标使用中国古代风格时学习组织方法，不复制作者希腊式柱廊、模板或纹理。'
 ],
 limits=[
  '原主start/part1..4/mini1..2完整fixed source graph，9placement7used，另2unused模板只做提取/头部机器核查，不计完整独立研究或参考。',
  '未运行Java、游戏、生成器、碰撞、实体AI或模型/材质检查；原CORNER标记、jigsaw替换、旋转状态/实体Yaw、处理器与实际heightmap均未执行。',
  '无声光/唤醒/焦点/用户实例与存档操作；未修改共享Jar、资产、模型、贴图、任务逻辑或中文指南针。',
  '通路只核源接口，附属接口脚下omitted不是air也不是可靠地板；上层可达、迷路/跳跃/战斗回程和自然地形均待证。',
  '源箱仅loot引用，未读loot定义或实抽/领取；敌对实体静态保存记录不是实际战斗/材料来源/交易付款/任务回执。',
  '1000门槛未达，不生产建筑，不删除清单。COD4已接受153/缺847只是旧观察，NPC累计null；本批参考正式增量0，旧221/269重复carry0。',
  '主协调接收本收据元数据不是实际看图/读源码或最终验收。检查是自有源码一致性，不冒充独立检查。',
  '只写292私有目录，不写shared session/master/pending/ownership；旧291等sealed文件未更改，主协调之外的工作不计入本聊天主动工时。'
 ],
 source_counts=counts,source_entity_types=dict(Counter(x['nbt']['id']for x in entities)),tasks_deleted=0,all_tasks_complete=False,COD4_accepted_old_observation=153,COD4_gap_old_observation=847,NPC_cumulative=None
)
put('manual-review.json',review)
protected=[]
for row in ld(P/'protected-before.json')['files']:
 b=row['before292'];after=bind(b['path']);protected.append(dict(before=b,after=after,unchanged=after==b,this_chat_wrote_file=False))
put('protected-current.json',dict(files=protected,boundary='Read-only shared-state observation. Concurrent differences do not authorize overwriting other work.'))
ck('shared production Jar unchanged',all(x['unchanged']for x in protected if x['before']['path'].endswith('.jar')))
ck('credit and deletion remain zero',review['formal_credit_added']==review['new_qualifying_reference_proposals']==review['tasks_deleted']==0)
cp=ld(P/'active-checkpoint.json');cp.update(status=status,whole_studies_completed=1,new_qualifying_reference_proposals=0,formal_credit_added=0,next='继续未完整阅读的冻结本地完整相关建筑；本原群DUN07部分原则HOLD0，不按9模板/placement加参考，不制作、不删除任务。');put('active-checkpoint.json',cp)
put('verification.json',dict(passed=True,checks=checks,count=len(checks),java_run=False,game_run=False,independent_acceptance=False))
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json']
put('RECEIPT.json',dict(batch=292,status=status,files=files,checks=len(checks),new_complete_whole_studies=1,new_qualifying_reference_proposals=0,formal_credit_added=0,tasks_deleted=0,all_tasks_complete=False))
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(files),checks=len(checks),protected_unchanged=sum(x['unchanged']for x in protected),protected_total=len(protected)),ensure_ascii=False))

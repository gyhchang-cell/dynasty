import json,hashlib,math
from pathlib import Path
p=Path(__file__).resolve().parent
assert not (p/'RECEIPT.json').exists()
def bind(f):
 f=f.resolve();b=f.read_bytes();return {'path':str(f),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def put(n,v):(p/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
raw=json.loads((p/'raw-source-audit.json').read_text())['candidates'];ct=json.loads((p/'source-context.json').read_text())
comps=[bind(p.parent/f'research-20261104-smithy-{n:03d}/manual-review.json') for n in [59,60,61,66,68,84,85,91,104]]
obs=[{
'layout':'7×7单间，西门到东侧单blast，无院、侧功能翼、储物和工住分区。与081/104单blast小房同用途家族；材质屋顶变化不构成新完整相关信用。只做有界排除，不重验旧建筑。',
'proportion':'DV3465，声明343格/195已存=167非air+28显式air，148省略不当air。地面0/使用1，屋顶4..6无上使用层。',
'facade_roof_materials':'泥砖墙、竹地板及36竹楼梯屋盖、黄陶与橙釉陶细部。楼梯主要屋面非登楼；不是贴图与碰撞验收。',
'circulation':'西门1,1/2,3west/right/closed到东炉4,1,3west/unlit/empty，0,1,3west_up入口pool empty/finalstructure_void。无储物磨砧smith床梯或岩浆，炉未运行。'
},{
'layout':'一个封闭中央冷作工间，加南北相对的两处带篷草地小廊。中央西门进屋，北门/南门各通一廊；不把三扇门数作三间铺、不把两廊编成独立冷热工区。申请上限1仅针对完整建筑三向工间—相对双廊的布局候选，待主协调判定；也可因增门增廊的家族边界被判0。',
'proportion':'7×7×11，DV3465声明539，存280=243非air+37显式air，259省略。中央地板y0、使用y1，中央盖y5..6，南北低廊盖y4；无床梯、第二楼层或 raised platform。小廊草地面与中央竹地板同标高。',
'facade':'东墙5,2,5玻璃板，北南连接true，5,1,5泥砖。三门闭合。北南外围各成对竹栅栏柱在x2/4,z1/9、y1..2，连接属性全false，不是连续封闭围栏庭院。',
'roof':'中央较高闭合盖与两端低小廊盖。3,4,2及3,4,8为TOP竹半砖；36竹楼梯大多为屋盖，4,1,4和4,1,6的east/bottom直楼梯是低陈设，不通楼层。14面黄挂旗均y4/Patterns[]，为廊檐饰物，不是14商户或NPC。',
'materials_terrain':'55草方块、9泥、48竹板、29泥砖、26蕨草；中央竹地板、双廊草地。西0,0,5土径，0,1/2,5显式air。南3,1,8是蕨草、3,2,8显式air；3,1/2,9省略非air。未执行地形拼装，不宣称全路径清空。',
'circulation_function':'西0,1/2,5显式air→1,1/2,5西门→2,1/2,5air→3,1/2,5中央通道，smith4,1,5。中央北经3,1/2,4air、3,1/2,3北门→3,1/2,2air到北廊；南经3,1/2,6air、3,1/2,7南门→3,1,8蕨草/上air到南廊。不是原生寻路或顾客交易验收。无箱桶炉blast磨砧岩浆床梯、entities0，故无额外工位/储物/住区。',
'dedup_and_application':'059F02封闭主厅→有磨箱的单东工作翼；061F03抬高踏步→单前方无盖功能平台→后工间；066F01双前磨→门→后储室；060F03多侧实际热/磨/箱工区；084F02连续L冷工区；085F01多工位仍单共同室。当前两相对低廊都没有独立工位，差异仅整体相对双廊与三向中央穿行，未证明新的冷热或工住生产链。设计借鉴可为中央可见工作面和两个低檐缓冲入口，实际任务是否需要须由主协调结合需求评定；不因竹材、14旗、三门或无exact就自动录入。'
}]
rows=[]
for r,c,o in zip(raw,ct['candidates'],obs):
 d=r['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):pal[b['state']] for b in d['blocks']};f1=r['id']=='F01'
 positions=([[1,1,3],[1,2,3],[4,1,3]] if f1 else [[1,1,5],[1,2,5],[3,1,3],[3,2,3],[3,1,7],[3,2,7],[4,1,5],[0,1,5],[0,2,5],[3,1,2],[3,2,2],[3,1,8],[3,2,8],[3,4,2],[3,4,8],[4,1,4],[4,1,6]])
 selected=[e for x in c['contexts'] if x['member'].endswith('/houses.json') for e in x['json']['elements'] if e.get('element',{}).get('location')==c['location']]
 rows.append({'id':r['id'],'source_stats':[d['DataVersion'],math.prod(d['size']),len(d['blocks']),r['nonair'],r['air'],len(pal),len(d['entities'])],'expected_counts':{'minecraft:smithing_table':0 if f1 else 1,'minecraft:blast_furnace':1 if f1 else 0,**{f'minecraft:{n}':0 for n in ['chest','barrel','furnace','grindstone','anvil','lava','ladder']}},'expected_states':[{'pos':pos,'state':mp[tuple(pos)]} for pos in positions],'expected_absent_positions':[] if f1 else [[3,1,9],[3,2,9]],'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']} for b in d['blocks'] if b.get('nbt')],'selected':selected,'root_fields':{'type':'repurposed_structures:generic_jigsaw_structure','size':8,'valid_biome_radius_check':1,'terrain_height_radius_check':2,'allowed_terrain_height_range':22,'start_height':{'absolute':0},'project_start_to_heightmap':'WORLD_SURFACE_WG','terrain_adaptation':'beard_thin','use_bounding_box_hack':True,'step':'surface_structures','spawn_overrides':{}},'root_absent':['max_distance_from_center','use_expansion_hack'],'viewed':['whole','cutaway','y0'] if f1 else ['whole','cutaway','y0','y2','y4','y6','vertical'],'observations':o,'written_comparisons':comps,'full_study':not f1,'credit_proposal_maximum':0 if f1 else 1,'context_reading':'Bamboo root size8/check1/terrain2/range22，start0/WORLD_SURFACE_WG/beard_thin，selected houses legacy/rigid/mossify，armorer权1/toolsmith权3。mossify只有mud_bricks random_block_match .03→packed_mud，不是苔石。仅原文保留其它towncenters/zombify背景不套用，biome集合未展开；未执行processor/拼装/loot/NPC/原生碰撞。两源单empty入口/finalstructure_void，不据此新增房翼或NPC。'})
put('review-config.json',{'batch':111,'history_pairs':361,'status':'SEALED_ONE_WHOLE_LAYOUT_PROPOSAL_PENDING_INDEPENDENT_REVIEW','scope':'COD3 NPC01 small civilian cold smithy: one coarse family exclusion and one complete source-layout research proposal, not admitted reference.','cases':rows,'image_counts':[14,10,4],'limits':'F01只实际3/7图，F02实际全7图；图是NBT方块类别示意，不是游戏纹理/碰撞/寻路。F02完整布局研究不等参考入账；三门双廊不自动视为独立家族。无Java/游戏/声音亮度唤醒/用户实例/新制作/专业资产/任务中文指南针/主清单/网络/提交发布。','next':'112继续固定本地小型民用功能建筑，等111F02独立语义裁定，继续避免单冷室材质变体。','handoff':'111已核对两竹林铺：F01单blast房有界初筛0；F02中央冷工间西入口+南北相对低盖草地小廊，完整布局研究候选上限1待独立审查，当前formal0。两廊只有成对独立栅栏柱并非封闭院，无额外工位储物。14PNG生成/10实际/4未看；F02全7图及7项观察，原NBT/BE/metadata/context与历史361pairs去重均绑定。三门/双廊/竹材不能自动入账；与059/060/061/066/068/084/085/091/104书面差异已存，不重看旧PNG或重跑验收。098/101零裁定first104照旧carry，旧其它pending不取消。COD4仍153差847。无Java/游戏/音亮唤醒/用户实例/新制作/产品或主清单修改。'})
# Source-bound route observations include absent positions explicitly; not a collision test.
r=raw[1]['nbt_decoded_original'];pal=r['palette'];mp={tuple(b['pos']):pal[b['state']] for b in r['blocks']}
routes={'west_to_center':[[x,y,5] for x in range(4) for y in [1,2]],'north_to_center':[[3,y,z] for z in range(2,6) for y in [1,2]],'south_to_center':[[3,y,z] for z in range(5,10) for y in [1,2]]}
put('F02-route-matrix.json',{'source':bind(p/'sources.json'),'routes':{k:[{'pos':v,'state':mp.get(tuple(v)),'stored':tuple(v) in mp} for v in vs] for k,vs in routes.items()},'closed_doors_and_fern_not_air':True,'omitted_not_air':True,'native_navigation_verified':False})

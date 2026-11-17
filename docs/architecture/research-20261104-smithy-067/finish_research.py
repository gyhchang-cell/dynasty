import json,hashlib,math
from pathlib import Path
from zipfile import ZipFile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
sources=json.loads((OUT/'sources.json').read_text())['candidates'];raw=json.loads((OUT/'raw-source-audit.json').read_text())['candidates']
with ZipFile(sources[0]['source_archive'])as z:
 m='data/repurposed_structures/tags/worldgen/biome/collections/bamboos.json';b=z.read(m);biome={'member':m,'sha256':hashlib.sha256(b).hexdigest(),'json':json.loads(b)}
put('biome-collection-context.json',[biome]);print('BIOME',json.dumps(biome,ensure_ascii=False))
functional=[]
for a in raw:
 d=a['nbt_decoded_original'];pal=d.get('palette')or d['palettes'][0];items=[]
 for b in d['blocks']:
  s=pal[b['state']]
  if b.get('nbt')or any(w in s['Name']for w in ['door','grindstone','lava','stairs','pressure_plate','slab']):items.append({'pos':b['pos'],'state':s,'original_block_entity':b.get('nbt')})
 functional.append({'id':a['id'],'stored_records':len(d['blocks']),'declared_volume':math.prod(d['size']),'omitted_positions':math.prod(d['size'])-len(d['blocks']),'explicit_air':a['air'],'nonair':a['nonair'],'entities_original':d.get('entities',[]),'functional_states':items})
put('functional-evidence.json',{'candidates':functional,'sparse_omission_not_air':True,'native_function_not_verified':True})
obs=[
{'layout':'8×9占地，西侧窄单冷加工室，东向门接带围栏小院；砂轮(2,1,6)实际在室内南端，不因初看等轴图把它写成户外工作位。','proportion':'8×6×9声明体积432，仅存248=201非空气+47air，184位置省略；单层低室，四周宽檐不当二层。','facade':'mud_bricks44/packed_mud5围室，西墙两glass_pane；东门(4,1,4)lower/east/closed，配两空图案yellow_wall_banner(5,3,3/5)east，不编造中文营业招牌。','roof':'bamboo_stairs41与bamboo_planks28形成纵向宽檐、收进顶部；通用分类图把竹楼梯画灰，并非石瓦屋面。无梯床，屋盖空腔非可住阁楼。','materials':'grass40、dirt13、bamboo_fence9、fern8；砂轮floor/south，脚下mud_bricks、上方y2/3显式air。没有热源、箱、锻造台或炉，不虚构完整热工链。','circulation':'东入口socket(7,1,4)经院内x5,z4显式air到东门，再向南进入室内磨工位；门内(3,1/2,4)显式air。原生门/围栏碰撞仍未验。','terrain':'草土基裙、短dirt_path接东院，入口empty池final structure_void，无未接室翼；WORLD_SURFACE_WG与可选竹林标签不证明真实山脚承托或NPC昼夜行为。'},
{'layout':'9×13占地，西凹口作业前场、北端泥砖岩浆热台接东侧长冷加工室，南端向西扩成箱储室；一扇门分内外，原整体不拆成多个建筑计数。','proportion':'9×7×13体积819，存522=377非空气+145air，297省略。地板y1、工作位y2，宽长低单层；L形高檐不是二层或塔。','facade':'竹方块101围长室，三glass_pane配iron_bars8，泥砖51围热端；门(4,2,6)west/closed，西前场砂轮(2,2,6)east，无床或住居翼。','roof':'bamboo_stairs62围L形低坡宽檐、bamboo_planks28/bamboo_mosaic20补屋面及地面；通用灰色不代表石顶，真实半块和防雨未运行。','materials':'岩浆(3,2,3)level0，四邻泥砖；室内壁装砂轮(5,2,3)face=wall/facing=east，前场floor砂轮另1。没有熔炉或铁砧，木竹相邻火源的安全尚未验。','circulation':'西socket(0,1,6)final bottom smooth_stone_slab到y1泥砖前场；(3,2,6)air→门→(5,2/3,6)air长室，南西箱(2,2,9)east保留原weaponsmith loot/seed。原碰撞与火源可达未验。','terrain':'y0土基72+grass1、smooth_stone_slab16过渡街面；empty入口无必需外接房翼，原村池rigid与size8/terrain_range22不等同实际山脚布置通过。'}]
comparisons=[
'与066F01正门北双外砂轮+后储室不同，本例东侧围院门入室、唯一砂轮在窄室内，原不设箱；与061F03抬高后室+南长工作栏台/西外阶不同，院不是工作露台且磨工位在室内。与063F01上下作业/双床和双侧阶不同，本例无上层。小冷室通用性仍需独立家族审查，不能以竹材/门转向单独记信用。',
'与056F01已研究L形主住居翼+支翼床区、外侧热台不同，本例不含住居翼而以西作业凹口/北端热台/东长冷室/南箱区分区；与057经典前棚后室不同，工作前场在长室侧凹口、室内又有壁装砂轮。L形外轮廓本身不够，提出最多1由主协调独立复核。']
bindings=[bind(next((ROOT/'docs/architecture').glob(f'research-*smithy-{n}/manual-review.json')))for n in ['056','057','061','063','066']]
cases=[]
for a,o,c in zip(sources,obs,comparisons):
 cases.append({**a,'observations':o,'images_actually_viewed':[bind(p)for p in sorted(OUT.glob(a['id']+'-*.png'))],'whole_boundary':'完整原稀疏源体、整体现图/切层/纵剖已读；empty入口无必接屋翼，原源包含基础、围护、屋盖和功能位。未存位置不冒充显式air，原生装配/碰撞未验。','semantic_family_comparison':{'comparison':c,'saved_existing_judgments_reused_not_reaccepted':bindings,'proposal_maximum':1},'credit_proposal_maximum':1,'formal_credit_added':0,'status':'PENDING_INDEPENDENT_SCOPE_AND_FAMILY_ADMISSION','native_acceptance':False})
put('manual-review.json',{'cases':cases,'source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':13,'manual_observations':14,'pending_maximum':2,'formal_credit_added':0,'no_independent_self_admission':True})
put('source-context-reading.json',{'metadata':'沿用同一固定Jar原metadata：RepurposedStructures7.1.19+1.20.1-forge，TelepathicGrunt，声明LGPLv3；完整credits保留，不转移原建筑到产品。','house_entries':'两个weaponsmith各weight3、rigid、minecraft:legacy_single_pool_element，实际指定bamboo/mossify。houses共32条并非32研究信用，towncenters8条非8新建筑。','root':'自定义generic_jigsaw_structure，start_pool bamboo/town_centers，size8，valid_biome_radius1，terrain_height_radius2，allowed_range22，WORLD_SURFACE_WG，beard_thin，start_height0；仅原村参数。','processor':'实际mossify仅mud_bricks随机.03→packed_mud规则；额外zombify/crop来自同池别的条目，不冒充当前正常铺的运行状态。未声称逐条实际阅读17条僵尸规则。','connectors':'两源各一empty入口，不需要补全房翼；F01有两banner原方块实体且Patterns空；F02箱loot原版定义不在modJar，保留缺依赖记录。','biome_collection':biome,'not_runtime_or_native_acceptance':True})
put('applicable-principles.json',{'principles':['先按坐标/原状态确定砂轮在室内还是院外，再组织铺门和对客动线。','L形应对应冷热加工与储箱分区；轮廓或竹材替换不是独立建筑信用。','熔岩与木竹邻接、防雨、壁装砂轮服务面及入口半砖都需后续原生验收。','完整相关1000参考并验收前不开始原创建筑，不复制原结构。'],'implemented_product':False})
put('task-scope-boundary.json',{'target':'COD3 NPC01 老陈 山脚铁匠铺空间研究','original_line':1122,'implemented':False,'outstanding':['适用完整不同建筑参考1000与独立复核','原创制作','材料→任务前置→付款→获取回执','中文指南针','昼夜/雨/危险/水锤世界状态','原生最终验收'],'COD4_ledger':{'accepted':153,'target':1000,'gap':847,'increment':0},'masterlist_deletions':0,'cod5_missing_not_invented':True})
put('session.json',{'batch':67,'status':'MANUAL_STUDY_COMPLETE_VERIFICATION_PENDING','source_bodies_studied':2,'actual_images_viewed':13,'pending_maximum':2,'formal_credit_added':0,'cumulative_not_reset':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'对尚未实际研究的相关smithy原源继续完整性与家族筛查，不把同体换材/池组件计独立建筑。'})
print('Saved 14 specific observations/13 actually viewed images/2 pending/0 formal credit')

"""Supplement the mechanical index with explicitly bounded source review; never edit production."""
from pathlib import Path
import json,hashlib,re
O=Path(__file__).resolve().parent;R=O.parents[3]
def load(n):return json.loads((O/n).read_text())
def put(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
inputs=load('input-sha256.json')
def evidence(path,needle=None):
 p=R/path;s=p.read_text();h=hashlib.sha256(p.read_bytes()).hexdigest();inputs[path]=h
 hits=[{'line':n,'text':l.strip()} for n,l in enumerate(s.splitlines(),1) if needle and needle in l]
 if needle:assert hits,(path,needle)
 return {'path':path,'sha256':h,'matches':hits}
J='src/main/java/com/dynasty/';D='src/main/resources/data/dynasty/'
# Preserve actual structure placements and recursive tags, rather than equating a name in Java with encounter availability.
struct={p.stem:json.loads(p.read_text()) for p in (R/(D+'worldgen/structure')).glob('*.json')}
sets={p.stem:json.loads(p.read_text()) for p in (R/(D+'worldgen/structure_set')).glob('*.json')}
structure_records=[]
for name,v in sorted(struct.items()):
 paths=[D+'worldgen/structure/'+name+'.json'];bindings=[]
 for sn,sv in sets.items():
  if any(a['structure']=='dynasty:'+name for a in sv.get('structures',[])):
   paths.append(D+'worldgen/structure_set/'+sn+'.json');bindings.append({'id':sn,'definition':sv})
 biome=v.get('biomes');tags=[]
 if isinstance(biome,str) and biome.startswith('#dynasty:'):
  tp=D+'tags/worldgen/biome/'+biome.split(':',1)[1]+'.json'
  if (R/tp).exists():paths.append(tp);tags.append(json.loads((R/tp).read_text()))
 structure_records.append({'id':'dynasty:'+name,'definition':v,'structure_sets':bindings,'biome_tag_definitions':tags,'evidence':[evidence(p) for p in paths],'limits':'Placement configuration exists; no generated world, search time or survival encounter is certified.'})
put('structure-placement-index.json',structure_records)
# Missing provider indexes are parser omissions, not automatically missing gameplay sources.
manual={}
def add(items,condition,refs):
 for item in items.split():manual['dynasty:'+item]={'condition':condition,'evidence':[evidence(J+p,n) for p,n in refs]}
add('ancient_coin_rust','Headless general at existing battlefield elite encounter; alternate yinbing_guizu structure ghost group. Night/light/loaded/collision/caps/death ledger conditions apply.', [('blueprint/elite/EliteEncounters.java','EliteContent.HEADLESS'),('blueprint/BlueprintSpawns.java','BlueprintEntities.YINBING_GUIZU')])
add('ancient_stele_rubbing bixi_bronze_shell sturdy_bronze_rivet','Kill juli_bixi_kuilei at authored imperial_tomb bixi position; real structure tag, loaded position/collision and persisted encounter conditions.', [('blueprint/BlueprintSpawns.java','spawnBixi')])
add('broken_jade_hairpin cold_palanquin_curtain white_silk_strip','Kill yinyang_zhijiao_youhun: authored imperial_tomb or underworld stone_grove palanquin positions, palanquinHour and loaded/collision conditions; also ruined-village ecology rule. Not unconditional overworld spawn.', [('blueprint/BlueprintSpawns.java','spawnPalanquin'),('blueprint/EcologyRules.java','ruined_village')])
add('gorilla_cast_plate','BronzeGorilla encounter at loaded high mountain ruined portal or battlefield; additionally snow_peak ecology rule. Defeat actual mob; collision, time/cap and ledger checks.', [('blueprint/elite/EliteEncounters.java','spawnBronzeGorilla'),('blueprint/EcologyRules.java','snow_peak')])
add('high_grade_mechanism_plan','Existing chensha_xuangong dungeon supplies chest; weighted loot entry, not guaranteed every chest.', [('dungeon/ChenshaPiece.java','dynasty:dungeons/chensha_artisan_supplies'),('dungeon/ChenshaStructure.java','ChenshaPiece')])
add('longyin_zhanma_duanyue_dao','Existing marshal_courtyard boss defeated; real memorial and eligible first-reward player; living survival main hand empty within4 blocks and unclaimed. Not recipe or free registry grant.', [('blueprint/artifact/MarshalBladeMemorial.java','ArtifactContent.LONGYIN'),('blueprint/boss/MarshalCourtyards.java','confirmedDeath')])
add('marshal_broken_horse_cleaver marshal_broken_wing_helmet','Defeat real gongsun_wuwang in existing marshal_courtyard; socket-triggered summon, non-peaceful, loaded space and unique boss UUID. Loot table source retained separately.', [('blueprint/boss/MarshalCourtyards.java','public static boolean summon'),('blueprint/boss/MarshalCourtyardPiece.java','SOCKET')])
add('marshal_last_city_oath','Confirmed arena boss death grants to first eligible nearby living noncreative nonspectator players; max16 per confirmed death,24block radius; persistent firstRewarded set.', [('blueprint/boss/MarshalCourtyards.java','confirmedDeath')])
add('painted_cinnabar','zhiren_jianke entity loot; actual paper swordsman dungeon encounter positions, plus ruined village night ecology. Weighted/chance loot not guaranteed.', [('blueprint/BlueprintSpawns.java','spawnPaperSwordsman'),('blueprint/EcologyRules.java','ruined_village')])
add('refined_cold_iron','yinbing_jiedao event success rewardTable; existing plains event,17700..18300 start window, distance from spawn>=512, rarity40/cooldown72000, participants/world-once policy. dependencies names validate registry resources, not item payments.', [('worldevent/DynastyWorldEventManager.java','reserveRewards')])
add('suanni_copper_gear','Existing imperial_tomb western vault fixed BronzeSuanni encounter; one cleared SavedData slot per structure; loaded/collision checks, defeat mob.', [('blueprint/elite/EliteEncounters.java','spawnBronzeSuanni')])
add('taoyan_bronze_cauldron_ear','Existing cauldron pit; three real bone offerings to distinct authored altars, central socket summon, defeat boss; nonpeaceful and loaded arena conditions.', [('blueprint/boss/CauldronPits.java','pit.ritualMask!=7'),('blueprint/boss/CauldronPits.java','Items.BONE')])
add('waterproof_ink_silk','Existing Tiangong inner-vault approach fixed InkAssassin encounter; loaded structures, collision and persisted respawn ledger, defeat actual mob.', [('blueprint/elite/EliteEncounters.java','spawnInkAssassin')])
add('zhanlu_rendao_bamian_jian','Existing taiqing_hidden_temple real registered sword case; survival3 ordered native trials within1800ticks; actual damage/logout/dimension changes cancel. Empty mainhand/free slot/unclaimed within4blocks to claim.', [('blueprint/artifact/ZhanluTrialRewards.java','public static boolean claim'),('blueprint/artifact/ZhanluTrialRewards.java','completeStage'),('blueprint/artifact/TaiqingTrials.java','completeStage')])
leafs=load('nonrecipe-material-sources.json');loot=load('loot-provider-index.json');reviews=[]
for row in leafs:
 item=row['item'];entry={'item':item,'mechanical_index_status':row['status'],'source':row['source'],'survival_verified':False}
 entry['loot_definitions']=[loot[t['id']] for t in row['source']['loot_tables']]
 if item in manual:entry.update(manual[item]);entry['review_status']='ACTUAL_CONDITIONAL_PROVIDER_FOUND_STATIC_ONLY'
 else:entry['review_status']='CONDITIONAL_PROVIDER_ALREADY_INDEXED_STATIC_ONLY'
 reviews.append(entry)
assert len(manual)==19 and all(i in {r['item'] for r in leafs} for i in manual)
put('nonrecipe-provider-review.json',{'denominator':len(reviews),'initial_index_omissions':21,'biome_index_resolutions':2,'targeted_provider_resolutions':len(manual),'unproven_unobtainable_items':[],'physical_encounter_or_six_stage_survival_proven':False,'items':reviews,'event_catalog':evidence(D+'world_events/catalog.json','"id": "dynasty:yinbing_jiedao"'),'structure_tag_sources':[evidence(str(p.relative_to(R))) for p in sorted((R/(D+'tags/worldgen/structure')).rglob('*.json'))]})
q=load('quest-graph.json');recipes=load('recipes.json')
def qa(qid):
 seen=set();todo=[qid]
 while todo:
  x=todo.pop()
  if x not in seen:seen.add(x);todo.extend(q[x]['dependencies'])
 return [q[x] for x in sorted(seen)]
findings=[
 {'id':'F01','status':'CONFIRMED_OBJECTIVE_ORDER_RISK_NOT_RECIPE_GATE','title':'木矛主任务在铁镐与水桶之后','facts':{'quest':'1000000000000000','mandatory_ancestors':['1000000000010020','1000000000010021'],'infrastructure_iron_ingots':6,'wood_spear_recipe':recipes['dynasty:mu_mao'],'quest_path':qa('1000000000000000')},'meaning':'提交/提示时点晚于早期铁基础设施；玩家仍可提前合成木矛。不能据此证明第一次获得即淘汰或违反2–3小时目标。'},
 {'id':'F02','status':'CONFIRMED_COST_AND_SINGLE_NPC_STOCK_CONSTRAINT','title':'布衣不是免费开局装，竹甲递进保留布衣成本','facts':{'raw_silk_string':3,'silk_raw_silk':3,'cloth_chest_silk':8,'cloth_chest_string_recipe_only':72,'cloth_set_silk':24,'cloth_set_string_recipe_only':216,'bamboo_chest_string_recipe_only':81,'baibao_jin_silk_base_coins_each':12,'baibao_jin_silk_max_uses':8,'cloth_chest_base_coins':96,'bamboo_chest_silk_total':9},'evidence':[evidence(D+'recipes/'+n+'.json') for n in ['raw_silk','silk','cloth_chestplate','cloth_helmet','cloth_leggings','cloth_boots','bamboo_chestplate']]+[evidence(J+'cod3/DynastyNpcEntity.java','updateTrades')],'meaning':'单个初始8库存丝绸报价只够布衣胸甲，不够同路继续竹甲的第9匹。该NPC类未见补货逻辑；不可无证假设睡一觉补货。可另寻NPC/宝箱/九尾狐/线合成，故不是永久断链。96为基础报价，实际需求/折扣可能改变付款。'},
 {'id':'F03','status':'CONFIRMED_LATE_TASK_CREDIT_PHYSICAL_USE_UNGATED','title':'旧武器架与废兵工坊的任务时间不能充当首次获取时间','facts':{'rack_quest':'1000000000c40026','armory_quest':'1000000000c40024','rack_reward':'tie_jian at75% damage','rack_duration_ticks':600,'armory_reward':'qimen_gear x1','armory_duration_ticks':3600,'rack_quest_path':qa('1000000000c40026'),'armory_quest_path':qa('1000000000c40024')},'evidence':[evidence(J+'expansion/SmallInteractions.java','case "old_weapon_rack"'),evidence(J+'expansion/SmallInteractions.java','case "abandoned_armory"'),evidence(J+'structure/TravelSitePiece.java','String[][] sites')],'meaning':'两者交互代码不查FTB前置。结构随机位置和遇见时间未实测，不能因任务链晚就宣称物品必然晚到或刚拿即废。'},
 {'id':'F04','status':'CONFIRMED_DIMENSION_ENTRY_COST_NOT_UNOBTAINABILITY','title':'凤凰羽与麒麟角来源要计入维度入口','facts':{'jade_portal_recipe':recipes['dynasty:jade_portal'],'jade_block_equivalent_jade':72,'portal_output_count':2},'evidence':[evidence(J+'DynastyBlocks.java','CELESTIAL_DYNASTY'),evidence(J+'block/DynastyPortalBlock.java','ServerLevel destination'),evidence(D+'dimension/celestial_dynasty.json'),evidence(D+'worldgen/biome/celestial_sea.json','dynasty:phoenix'),evidence(D+'worldgen/biome/jade_forest.json','dynasty:qilin')],'meaning':'有真实群系刷怪定义，不能只因无主世界biome_modifier判不可得。玉门配方需8玉块+1龙晶，计入后段成本；刷怪上限/落点/战斗与遇见耗时未验收。'},
 {'id':'F05','status':'CONFIRMED_PREDECESSOR_CONSUMPTION_NOT_INSTANT_OBSOLESCENCE','title':'中后期旧件有明确升级成本，不能跳过前驱计价','facts':{'recipes':[recipes['dynasty:'+n] for n in ['sword_silver','sword_jade','jade_chestplate','xuantian_chestplate','hongmeng_chestplate','evolve_guard_3']]},'meaning':'官银剑原料为玉笛而非自行猜测青铜剑；玉甲用将军甲；鸿蒙胸甲同时消耗龙皇胸甲与混元胸甲。成本/替代时点必须保留全部分支；并未新增NBT继承契约。'}]
put('findings.json',findings)
# Exact existing interaction contracts, no repeat runtime/food test and no invented play time.
sites=[['wayside_shrine','soul_incense',600,1],['nameless_tomb','#minecraft:flowers',1200,1],['old_weapon_rack',None,600,1],['sword_scar_wall',None,2400,3],['herb_spot',None,1200,1],['abandoned_armory',None,3600,1],['puzzle_box',None,600,1],['battlefield_remnant',None,1200,3],['broken_stele','minecraft:paper',600,1],['mortuary_room','minecraft:milk_bucket',2400,1],['ghost_market_boat','context soul_incense',2400,1],['wayside_tea_stall','minecraft:milk_bucket',2400,1],['old_bellows','minecraft:charcoal + nearby eligible furnace',600,1],['broken_waterwheel','dynasty:qimen_cable',1200,1],['ancient_well',None,600,1]]
put('interaction-route-constraints.json',{'denominator':15,'source':evidence(J+'expansion/SmallInteractions.java'),'placement':evidence(J+'structure/TravelSitePiece.java'),'sites':[{'site':n,'required_held_or_context':mat,'configured_duration_ticks':dur,'required_completions':cnt,'quest_records':[v for v in q.values() if any(n in (t.get('advancement') or '') for t in v['tasks'])],'limits':'configured cooldown/steps only; no elapsed survival travel/action proof; battlefield additionally requires3 distinct locations.'} for n,mat,dur,cnt in sites],'placement_structures':[x for x in structure_records if x['definition'].get('type')=='dynasty:travel_site']})
put('input-sha256.json',inputs)
print(json.dumps({'reviewed_nonrecipe_leaves':len(reviews),'manual_omission_resolutions':len(manual),'findings':len(findings),'structures':len(structure_records),'interaction_sites':15},ensure_ascii=False))
# Bind original 31 obtain/craft +15 interaction entries to CURRENT nodes, never use old chapter names as truth.
idxpath='docs/cod4/quest-nodes.json';evidence(idxpath);idx=json.loads((R/idxpath).read_text());source_index=load('item-source-index.json');entries=[]
for x in idx:
 item='dynasty:'+x['item'];node=q[x['id']];s=source_index.get(item,{});extra=[]
 if x['item']=='jade_crown':extra=[evidence(J+'expansion/ContentProgress.java','jade_crown')]
 entries.append({'item':item,'interaction':x['interaction'],'quest':node,'ancestor_chain':qa(x['id']),'source_index':s,'additional_conditional_source':extra,'limits':'Only current prerequisite/source association, not natural acquisition or elapsed survival verification.'})
assert len(entries)==46 and sum(not x['interaction'] for x in entries)==31
put('cod4-46-entry-paths.json',{'denominator':46,'obtain_craft':31,'interaction':15,'entries':entries})
summary=load('summary.json');summary['provider_review']={'path':'nonrecipe-provider-review.json','reviewed_leaves':44,'initial_mechanical_provider_omissions':21,'biome_index_resolutions':2,'targeted_actual_provider_resolutions':19,'proven_unobtainable_items':0,'meaning':'Providers have conditional static bindings. Not a full runtime path/encounter proof.'};summary['cod4_entry_current_paths']=46;summary['six_stage_sample_items']=sum(len(x['items']) for x in load('six-stage-paths.json'));summary['report']='REPORT.md';put('summary.json',summary)
evidence('docs/cod4/request.txt');evidence('docs/cod4/content-task-map.tsv');put('input-sha256.json',inputs)

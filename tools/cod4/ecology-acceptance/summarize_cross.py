"""Summarize bounded native cross-dimension observations; never infer absence globally."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3]
D=R/'docs/cod4/audit-20261022/ecology-acceptance'
T=R/'tools/cod4/ecology-acceptance'
frozen=T/'.work/cross-build/frozen'
manifest=json.loads((D/'cross-dimension-run1/frozen-source-sha256.json').read_text())
current={str(p.relative_to(frozen)):hashlib.sha256(p.read_bytes()).hexdigest() for p in frozen.rglob('*') if p.is_file()}
runs=[]
for num in (1,2,3,4,5):
 d=D/f'cross-dimension-run{num}'; s=json.loads((d/'observations.json').read_text())
 receipt={'status':s['status'],'native_server_exit_success':'BUILD SUCCESSFUL' in (d/'server.log').read_text(),'seed':s['seed'],'source_snapshot':'../cross-dimension-run1/frozen-source-sha256.json','frozen_source_unchanged':manifest==current,'frozen_file_count':len(manifest),'observations_sha256':hashlib.sha256((d/'observations.json').read_bytes()).hexdigest(),'independent_home_cache_output_world':True,'player_journey_tested':False,'no_artificial_pieces_biomes_actors_time_weather':True}
 (d/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 rows=s['observations'];candidates=[r for r in rows if r['kind']=='native_candidate_generation_point']
 runs.append({'run':d.name,'receipt':receipt,'locates':[r for r in rows if r['kind']=='native_locate'],'explicit_candidate_denominator':len(candidates),'candidate_generation_points_accepted':sum(r['production_findValidGenerationPoint_present'] for r in candidates),'candidate_relief_at_most_24':sum(max(r['ocean_floor_WG_3x3'])-min(r['ocean_floor_WG_3x3'])<=24 for r in candidates),'natural_city_observed':s.get('natural_wangsi_observed',False),'natural_underworld_control':[r for r in rows if r['kind'] in ['native_control_locate','natural_control_start']],'terrain_ok_with_reserved_slots':sum(max(r['ocean_floor_WG_3x3'])-min(r['ocean_floor_WG_3x3'])<=24 and bool(r.get('read_only_reserved_slot_conflicts')) for r in candidates)})
s=json.loads((D/'cross-dimension-run5/observations.json').read_text()); rows=s['observations']
biomes=[r for r in rows if r['kind']=='underworld_biome'];positions=[r for r in rows if r['kind']=='native_position']
evidence={'status':'READ_ONLY_NATIVE_CROSS_DIMENSION_AUDIT_COMPLETED_WITH_GAPS','seed':20261023,'building_presence':'Existing Wangsi physical ghost-market production source chain is confirmed. No new building requested or produced. Bounded locate did not find a natural Wangsi start; no global absence claim.','architecture_reference':'docs/architecture/continuation-20261022/ecology-scene-entry-audit-20261023.json','native_runs':runs,'distinct_candidate_denominator':625,'denominator_note':'Run5 expands to 625 actual candidates in [-12,12]^2, including previous 81. Across five runs, deduplicated once as 625, not 706 or repeated totals. Native locate radius is placement-region rings, not block radius and not guaranteed generated FULL chunks. No world-exhaustive claim.','underworld_biomes':[{ 'id':b['biome'],'secondary_species_denominator':len(b['species']),'matching_biome_tags':sum(x['biome_tag'] for x in b['species']),'nonempty_secondary_spawn_lists':sum(bool(x['spawn_entries']) for x in b['species'])} for b in biomes],'actual_callback_positions':[{ 'pos':p['pos'],'biome':p['biome'],'species_denominator':len(p['results']),'production_eligible_true':sum(r['production_eligible'] for r in p['results']),'native_NATURAL_callback_true':sum(r['native_NATURAL_callback'] for r in p['results'])} for p in positions],'ecology_gap':'SecondarySpawnHooks.eligible rejects underworld dimension before biome/habitat/physical checks for all 30 species. Both real underworld biomes additionally have zero matching secondary biome tags and zero secondary spawn entries. Wangsi is absent from ghost_sites and secondary/ruins. Physical ghost market existence does not establish COD4 natural ecology access.','entry_chain':{'registered_portal':'dynasty:underworld_portal','production_entry':'DynastyPortalBlock.use -> server.getLevel(UNDERWORLD) -> findArrival -> ServerPlayer.teleportTo','recipe':'src/main/resources/data/dynasty/recipes/underworld_portal.json','verification':'Source chain only; no player portal or full survival resource route claimed. Native server confirmed registered dimension exists. Did not invoke fallback landing builder or place a fixture portal.'},'unchanged_open_scene_requirements':['Overworld dedicated abandoned village','Overworld complete mortuary','Overworld surface graveyard','Naturally generated Wangsi city现场 plus player entrance journey'],'production_changes':[],'legacy_save_root_progress':'Assigned to Kepler; not inspected or changed by this QA.'}
(D/'cross-dimension-audit.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
text='''跨维度自然生态只读复核（固定种子20261023）

地府枉死城包含既有实体鬼市的注册、生成、48列piece和实体布局代码链。不能用主世界ghost_sites仅有古战场，推断整个游戏没有鬼市；未新建、删除或修改建筑。

原生结果：独立Forge正常噪声世界实际加载dynasty:underworld。其两个生物群系underworld_wastes/soul_river，各检查30种小怪：匹配secondary biome标签0/30，实际刷怪条目0/30。真实已加载位置(0,80,0)的生产eligible与NATURAL回调均0/30；源码维度门槛直接排除地府，结论不依赖该位置地面是否适合。

自然城址：native locate半径1、4、16放置区域均未找到；半径不是方块距离。run5另对[-12,12]×[-12,12]的625个真实随机散布候选调用生产findValidGenerationPoint，0/625通过。496处3×3原地形高度差>24；其余129处高度差<=24，但129处均另有现有保留地标槽位冲突（见只读原生placement派生的具体set/chunk清单）。多重条件可同时失败，不冒充逐支插桩。run5的625处包括run2/run3/run4的81处，去重只计625。未手放piece、未改biome、未人工建实体、未改时间天气；不是全世界穷尽，也不是枉死城不存在的证明。

原生阳性对照：run4找到既有legacy_ghost_gate，native locate=(112,0,112)，正常FULL区块得到有效自然StructureStart、1piece、bbox=(72,91,72)..(192,193,192)。鬼门关不计完整鬼市，也不替代枉死城现场。

入口：underworld_portal配方及DynastyPortalBlock.use跨维度传送链存在；原生世界确认目标维度已加载。未声称走完生存采集/制作/传送/找城流程，也未调用可能搭建落地平台的入口函数。

保留缺口：主世界荒村、完整义庄、地表墓园仍待自然现场证明；地府鬼市的COD4生态接入被当前维度及biome/结构标签条件阻断。已有建筑不应因此重做或删除。旧档根进度由Kepler处理，本QA不干预。

证据：cross-dimension-run1~5/observations.json、server.log、receipt.json；cross-dimension-audit.json。5862个独立冻结输入哈希一致，缓存、输出、Gradle home和世界均隔离，五次原生服务端正常退出。
'''
(D/'cross-dimension-audit.txt').write_text(text)
print(json.dumps({'native_runs':len(runs),'all_successful':all(r['receipt']['native_server_exit_success'] for r in runs),'frozen_unchanged':manifest==current,'distinct_candidate_denominator':625,'secondary_underworld_spawn_entries':0,'global_absence_claim':False}))

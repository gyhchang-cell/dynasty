"""Seal private research, explicitly preserving relevance and acceptance holds."""
import json,hashlib,sys
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
source=ld(P/'F02-source.json');counts=ld(P/'F02-source-counts.json');ctx=ld(P/'original-context.json');ar=ctx['archive']
assert bind(ar['path'])==ar
meta=ld(R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json');inventory=ld(meta['fixed_archive_inventory']['path'])
assert next(v['sha256']for v in inventory['archives']if v['path']==ar['path'])==ar['sha256']
resources=ctx['resources']+ld(P/'additional-context.json')
with ZipFile(ar['path'])as z:
 raw=z.read(source['member']);assert hashlib.sha256(raw).hexdigest()==source['nbt_sha256'];assert read(raw)==ld(P/'F02-original.json')
 for a in resources:
  raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['sha256'];assert len(raw)==a['bytes'];assert raw.decode()==a['text'];assert json.loads(raw)==a['json']
 road=ld(P/'road-interface-context.json');raw=z.read(road['member']);assert hashlib.sha256(raw).hexdigest()==road['sha256'];assert read(raw)==ld(P/'road-interface-original.json')
fish=ld(P/'candidate-history-screen.json');fa=fish['source'];far=bind(fa['source_archive'])
assert far['sha256']==next(v['sha256']for v in inventory['archives']if v['path']==far['path'])
with ZipFile(far['path'])as z:
 raw=z.read(fa['member']);assert hashlib.sha256(raw).hexdigest()==fa['nbt_sha256'];assert read(raw)==ld(P/'F01-original.json')
put('prefilter-only-not-whole.json',dict(case='F01',archive=far,member=fa['member'],nbt_sha256=fa['nbt_sha256'],basis='Palette/material and block-entity machine screening only, no PNG or whole semantic study. Sand/water/vegetation with campfire and barrels is insufficient evidence of a complete relevant workshop or ferry building.',actual_visual_reading=False,whole_building_credit=0,new_whole_study=0,qualifying_reference_proposal=0))
prior=[]
for b,ident,note in [
 (63,'F01','同为8×8×8但旧下层冷作坊+上双床卧室，双路正面外阶；当前地面围栏畜栏+上层床/热加工/织布/箱共室，北侧单路升阶与一门。差异在功能层位/交通，不能仅凭设备或职业名作新家族。'),
 (85,'F01','旧8×6×8单层一室冷石工加高炉，双门，无床院；当前上层混用室下有围栏院并北外阶，均保留多职业不拆计数。旧单室家族HOLD不变。'),
 (115,'F02','旧小主室加南外作业坪，只完成有界初筛，full=false/proposal0，即使status名称含完整proposal也不能改变事实。当前是上下叠置院与混用房，未把旧初筛冒充完整研究。'),
 (128,'F02','旧例已有下畜栏/上热工房/侧外阶的大类；其西低盖公共接待带、东高工作室与南梯组成横向展开，当前8×8紧凑单体无独立低盖接客翼，上层还混床/织布。此是最接近的家族边界，尚不认定足够独立新家族。')]:
 path=P.parent/f'research-20261104-smithy-{b:03d}'/'manual-review.json';a=next(a for a in ld(path)['cases']if a['id']==ident)
 prior.append(dict(batch=b,case=ident,binding=bind(path),preserved_complete_case_record=a,actual_reading='Own observations/screening_observations and own limits/status fully read this turn. Historical PNG/NBT not reopened; nested old comparisons merely preserved, not newly read or accepted.',current_comparison=note,recount=0))
put('prior-whole-comparison.json',dict(comparisons=prior,old_status_and_limitations_preserved=True,independent_new_family_claim=False))
original=ld(P/'F02-original.json');pal=original['palette'];bs={tuple(b['pos']):b for b in original['blocks']}
checks={
 'frozen_archive_and_source_binding':True,
 'nine_context_jsons_bound':len(resources)==9,
 'full_source_512_no_omission':counts['stored']==512 and counts['unknown']==0 and len(bs)==512,
 'palette_46_and_11_BE':len(pal)==46 and len(counts['block_entities'])==11,
 '213_nonair_299_air':counts['nonair']==213 and counts['air']==299,
 'full_state_matrix_equal':all(v['rows']==[[bs[(x,v['y'],z)]['state']for x in range(8)]for z in range(8)]for v in ld(P/'F02-all-512-state-matrix.json')),
 'road54_state_matrix_equal':all(v['rows']==[[next(b['state']for b in ld(P/'road-interface-original.json')['blocks']if b['pos']==[x,v['y'],z])for x in range(9)]for z in range(3)]for v in ld(P/'road-connection-reading.json')['matrix']),
 'source_entities_empty':original.get('entities')==[],
 'no_cached_exact_match':ld(P/'shop-history-screen.json')['rows'][0]['historical_cached_matches']==[],
 'original_smoker_empty_unlit':next(b for b in counts['block_entities']if b['pos']==[5,4,4])['nbt']['Items']==[] and pal[bs[(5,4,4)]['state']]['Properties']['lit']=='false',
 'loom_front_has_chest':pal[bs[(2,4,2)]['state']]['Properties']['facing']=='south' and pal[bs[(2,4,3)]['state']]['Name']=='minecraft:chest',
 'one_complete_bed_not_two':sum(pal[b['state']]['Name']=='minecraft:green_bed'for b in bs.values())==2,
}
protected=[]
for a in ld(P/'protected-before.json')['files']:
 before=a['before289'];after=bind(before['path']);protected.append(dict(before=before,after=after,unchanged=before==after,this_chat_wrote_file=False))
put('protected-after.json',dict(files=protected,all_unchanged=all(a['unchanged']for a in protected),no_session_written=True))
checks['eight_protected_inputs_unchanged']=len(protected)==8 and all(a['unchanged']for a in protected)
images=[bind(p)for p in sorted(P.glob('*.png'))];checks['five_current_images_actually_viewed']=len(images)==5
put('actual-image-reading.json',dict(images=images,actually_viewed=5,whole_layers_read=8,render_correction='Initial lower/upper isometric previews clipped below frame; corrected unsealed projection height, reopened both corrected files before sealing. Full original 512-state matrix and two layer sheets also actually read.',limits='Class color/full cube approximations, not original textures or collision. Roof oak slab not stone. Images never count as separate buildings.'))
review=dict(batch=289,status='FULL_ORIGINAL_SHOP_SPATIAL_READING_HOLD_RELEVANCE_AND_CLOSE_128_FAMILY_ZERO',
 scope='继续真实完整生产/服务建筑参考。当前完整原始工住店屋可研究上下空间与外阶；对COD3 NPC01铁匠铺只有民用作坊组织辅助意义，无完整锻造工艺。不是完成NPC或新增建筑资产。',
 case='F02 sparse_jungle_butcher_and_shepherd_1',source=source,source_counts=counts,
 seven_dimensions=dict(
 layout='8×8紧凑单体，地层y0草/泥径与动物接头，上y1围栏院；北侧单路外阶升至y3楼板，y4室内把织布机、烟熏炉、床、箱混合布置。没有独立第二工作室/低盖服务翼，不把上下层/两职业/接头拆成多个建筑。',
 proportion='8×8×8/DV3105，512位置全部保存=213非air+299air，省略0。46palette/11BE/entities空。地院使用y1，上室使用y4，屋盖y6..7；8高不是8层，两个green_bed块为一张东西向完整床。',
 facade='剥皮云杉木26、云杉板8、橡木板20作围护/楼面；北侧唯一jungle_door(4,4/5,1)north/right/closed是两半一门。西/南4个开启jungle_trapdoor是窗饰，不是四个新增入口。地院8个closed spruce_fence_gate分布北/南与东西两侧，与旧085高位窗栏不同，不能统一当窗饰。空白木牌不是中文招牌。',
 roof='y6边缘bottom oak_slab、oak_planks及内圈top oak_slab，y7十字形bottom slab上收；39橡木板片与20木板形成完整小屋盖，不称灰石瓦。smoker上方两段andesite_wall(5,5/6,4)只表明原排烟构件，未验真正烟路/耐火/雨天行为。',
 materials='loom(2,4,2)south；shepherd箱(2,4,3)east；东smoker(5,4,4)west/unlit/Items空且Burn/Cook/Total=0；高butcher箱(5,5,3)west。床head(2,4,5)/foot(3,4,5)west，卧息与加工共室。没有铁砧、锻造台、高炉、熔炉、水/岩浆/淬火点，不能当完整铁匠生产范例。原箱仅loot引用无seed/Items，未生材料或交易付款。',
 circulation='北外阶bottom east依次(1,1,0)→(2,2,0)→(3,3,0)，相邻TOP west承托(2,1,0)/(3,2,0)/(4,3,0)，上端绕向门(4,4/5,1)，内侧(4,4/5,2)显式air且下为TOP spruce_slab。室内至smoker西侧(4,4/5,4)为空，未做寻路。loom正南(2,4,3)被箱占，东邻(3,4,2)是bottom stair，不能声称正面无阻的工作动线。高箱顶(5,6,3)TOP oak_slab，只记状态，不推箱盖可开。地院多方向门均关闭，无实际人畜生成/通行验收。',
 terrain='单NBT含草地基础、围院、外阶、楼板、房间与屋顶，无缺失房翼接口。五jigsaw中两个animal最终grass，两个村民最终air/顶部spruce_slab，一个north_up空入口最终air；村民池原为jungle_tribal，保留原引用。屋池精确weight4/legacy_single/rigid/street_polynesian。原straight_01道路south_up(3,1,2)匹配屋north_up(4,1,0)，零旋转屋偏移(-1,0,3)，包围盒沿z相邻不重叠；只为代数核查，不是地形/原生碰撞验收。'),
 context_reading=dict(full_jsons=9,road_template='straight_01: 9×2×3, all 54 state indices, 7 palette and 9 connector NBT read; interface context only, credit0',
 root='village_sparse_jungle: WORLD_SURFACE_WG/start0/size5/max116/beard_thin/expansiontrue/spawn_overrides{}',
 pools='houses17条含empty weight15；streets9条各weight1/terrain_matching/fallbackterminators；terminators1条；town_centers1条rigid；decor火炬weight1与empty5；jungle_tribal villagers三条weight1 nitwit/1 baby/10 unemployed，权重不是生成12人。',
 processors='street_polynesian五有序规则以yellow_concrete为输入：水位条件转jungle_planks，随机.2 rooted_dirt/.3 coarse_dirt/.4 packed_mud，最后block_match还带probability.1，忠实保留语法不擅写10%随机。当前屋无yellow_concrete；道路有标记，未执行处理器或重算全域概率。',
 external_unread='原版animal pool与shepherd/butcher loot只保存引用，未在本批读取其外部资源。村民/火炬/其他房屋/城镇中心NBT未展开，不把JSON中候选当读过完整建筑。'),
 history=dict(cache_pairs=666,exact_matches=[],machine_only_prior=198,comparison='063F01和085F01全自身七维/边界、115F02/128F02全自身观察及限制实际读；整条旧case保留，nested不计新读。128已有下院上热工外阶大类，当前是否足够语义不同仍HOLD。'),
 learned_principles=['院落与加工房可垂直叠放减少占地，外阶可分开日常居住与原料照看；地院气味/烟火/疏散与真实动线必须另验。','紧凑混用工作室必须检查每台设备正面站位；出现箱子占织布机正面时，不用设备名称或完整外壳替代可操作证据。','道路接口应保存朝向、目标池与相对偏移，同时分别说明terrain_matching路面和rigid房体之间尚未执行的贴地处理。'],
 actual_reading=dict(full_source_state_indices=512,all_layers=8,palette_states=46,all_BE=11,entities_empty=True,functional_probes=25,images_actually_viewed=5,context_jsons_fully_read=9,road_indices=54,old_source_images_reopened=False),
 limits=['本轮首次完整阅读此源房体，不等于足够独立的新空间家族。128近似家族和非锻造用途均HOLD，新相关参考提案0，正式信用0。','F01仅机器预筛，无图无完整建筑学习信用；F02房体最多一处，路段、层、床、设备、接头及五图全不拆分计数。','没有运行Java/游戏/Gradle、原生生成、processor、寻路、生产、箱盖、掉落、付款/原生获取、任务/中文指南针或NPC状态机验收。','没有改变声音/亮度/焦点/唤醒或游戏实例/原存档，没有编辑Jar、专业模型/贴图/建筑、主清单/pending/ownership、共享session或Git。','原记录有些status概括词与case实际full/proposal不一致，按实际case保留，例如115F02 fullfalse/proposal0，不借名称当验收。','未达到1000门槛，不新制作、不删待办、不自授独立Main验收，不重计269/277、217/192。COD4旧观察153/缺847，NPC累计未知。'],
 new_source_whole_spatial_readings=1,new_qualifying_reference_proposal=0,formal_credit_added=0,old269_carry_added=0,tasks_deleted=0,all_tasks_complete=False)
put('manual-review.json',review)
put('active-checkpoint.json',dict(batch=289,status=review['status'],manual_review=bind(P/'manual-review.json'),previous_receipt=bind(P.parent/'research-20261104-smithy-288/RECEIPT.json'),new_source_whole_spatial_readings=1,new_qualifying_reference_proposal=0,formal_credit_added=0,COD4_accepted_old_observation=153,COD4_gap=847,NPC_cumulative=None,tasks_deleted=0,no_session_written=True,next='避开已全面筛过的smith名称/换材原版屋、288实验室与289动物院上加工房家族；需要真正直接相关且明显不同完整工坊，不把弱相关用途或原设备凑数。保留主协调独立审查。'))
assert all(checks.values()),checks
put('verification.json',dict(checks=checks,passed=len(checks),native_tests_run=False))
put('RECEIPT.json',dict(batch=289,status='SEALED_COMPLETE_SOURCE_READING_RELEVANCE_FAMILY_HOLD_ZERO',files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'],checks=len(checks),new_source_whole_spatial_readings=1,new_qualifying_reference_proposal=0,formal_credit_added=0,all_tasks_complete=False))
for a in ld(P/'RECEIPT.json')['files']:assert bind(a['path'])==a
print(json.dumps(dict(receipt=bind(P/'RECEIPT.json'),manual=bind(P/'manual-review.json'),files=len(ld(P/'RECEIPT.json')['files']),checks=len(checks)),ensure_ascii=False))

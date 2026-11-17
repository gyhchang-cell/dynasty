"""Hold one raw-record side-pen family candidate without claiming visual study."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-159'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get(P/'raw-source-audit.json')['candidates'][0];d=r['nbt_decoded_original'];pal=d['palette'];mp={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
positions={tuple(b['pos'])for b in d['blocks']if b.get('nbt')or any(t in pal[b['state']]['Name']for t in ['door','smoker','stairs','pressure_plate'])}
positions.update((x,y,5)for x in range(9)for y in range(5))
queried=[{'pos':list(p),'state':mp[p]}for p in sorted(positions)];put('critical-original-states.json',{'states':queried,'native_collision_verified':False})
comparisons=[]
for n,ident in [(59,'F02'),(81,'F02')]:
 f=R/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json';old=next(x for x in get(f)['cases']if x['id']==ident)
 comparisons.append({'binding':bind(f),'case':ident,'complete_saved_observations_actually_read':old.get('screening_observations',old.get('observations')),'complete_original_comparison_preserved':old.get('saved_written_comparisons',old.get('semantic_family_comparison')),'original_proposal_and_status_preserved':{k:old[k]for k in ['credit_proposal_maximum','formal_credit_added','status']if k in old},'old_images_not_revisited':True,'current_raw_only_comparison':'旧为封闭炉房接通透侧作业棚且有隔门，本源是单小工作室东侧低位无门动物栏，地面高差与屋顶覆草不同；这些区别仍不足在原记录预筛证明独立新整屋空间机制，不认精确复制，也不以换职业/覆草/侧院标签凑参考。当前0只表示保守不提出新增信用，历史结论保留。'})
obs={
'layout':'原记录预筛：西抬起的单工作间，北角桌椅/南烟熏箱，唯一西门；东侧较低的三边围栏动物院以房基为第四边，无内通院门/无栅栏门。对059F02和081F02封闭热室接侧开敞围栏空间家族保守不足0，不称机械精确复制。0PNG/0完整视觉建筑研究。',
'proportion':'9×9×11/DV3105，891位置全存=387非air504air、零省略，56palette、9原状态层、6BE、entities[]实际读。西屋floor2/use3、东院floor0/use1，室内x2..4/z3..7；y5局部TOPbirch slab夹屋顶空腔，源无梯/床/使用二层。9高不是9层。',
'facade':'mangroveplanks43、calcite18、z轴strippedbirchlog27、whitepane3；仅darkoakdoor1,3/4,5west/left/closed。东院darkoakfence10在z3/z7与x8边，源palette无fencegate，不能补一扇院门。室内低darkoakstairs3与fence/pressureplate为桌椅线索而非楼梯或控制机关已验。',
'roof':'原层y5两侧stonebrickstairs主屋檐与向东小挑檐，y6中间strippedbirchlog/边grass，y7大幅grass铺坡顶、y8草花上下半tallgrass延伸。只能称原索引覆草屋面，不冒充看过整图的质感评审。roof无梯/入口，草屋顶不可据此作农田/可达经营二楼或计成另一栋。',
'materials':'smoker3,3,7north/unlit且Cook/Burn/Total0/Items[]/RecipesUsed{}；chest2,4,7north/single/dry，butcherlootseed-8804915956173623749，高箱可达/开盖未验。stone_slab108全double，grassblock52包含地面与屋盖，不作52农业产出。无水/熔岩/砧/锻台/床。3挂/立灯、花盆及未触发木压板是静态装饰。',
'circulation':'西外石阶0,1,3 BOTTOMsouth、0,1,4 TOPnorth、0,2,4 BOTTOMsouth、0,2,5 TOPnorth近西门，入口0,1,5最终air；原门前0,3/4,5air，但转折/半块步进与生成后地形未运行。动物socket6,1,5up_east/animals/finalair，不是已有牲畜；两NPCsocket3,1,0up_east与7,1,1up_north最终air。东院比西屋低两格、房基侧无开门，不能宣称室内可直入照料院/已实现收摊路。',
'terrain_and_dedup':'五完整context JSON实际读：root size4/max116/start0/surface/beardthin/expansiontrue；houses15项含empty权10，本屋权2legacy/rigid/emptyprocessor。center唯一权1挂street_swedish处理器，本屋未挂；中心规则stone在水变darkoakplanks及随机.2变grass，原Properties键Snowy大写保留不修，未运行不投射到本屋double石板。17optional biome不是17建筑，单Jar缺taiga villagers/common animals/butcherloot不是全环境缺。当前原记录家族不足0，未生成图也不计原状态/花草/屋面组件为独立建筑，156首次159已接受今后只carry0，157/158仍待Main。'
}
put('raw-family-exclusion.json',{'scope':'raw original record family sufficiency screen only','original_palette_read':56,'original_planes_read':9,'original_BE_read':6,'original_entities':[],'stored_records':891,'omitted_not_air':0,'observations':obs,'comparisons':comparisons,'generated_png':0,'images_actually_viewed':0,'complete_whole_visual_studies':0,'proposal':0,'formal_credit':0})
c=get(P/'source-context.json')['candidates'][0];pool=next(x for x in c['contexts']if x['member'].endswith('/houses.json'));root=c['contexts'][0]['json']
rv={'id':'F01','source_stats':[3105,891,891,387,504,56,0],'expected_counts':r['material_counts'],'expected_states':queried,'expected_block_entities':[{'pos':b['pos'],'nbt':b['nbt']}for b in d['blocks']if b.get('nbt')],'selected_pool_member':pool['member'],'selected':[e for e in pool['json']['elements']if e.get('element',{}).get('location')==c['location']],'root_fields':root,'viewed':[],'observations':obs,'written_comparisons':comparisons,'full_study':False,'credit_proposal_maximum':0,'target':'COD3 NPC01 related workshop original-record prefilter','context_reading':'五完整JSON实际读，emptyprocessor本屋与center处理器区分；0PNG/0完整视觉研究/0提案。'}
put('review-config.json',{'batch':160,'history_pairs':get(P/'pre-render-history-screen.json')['history_unique_archive_member_pairs'],'status':'RAW_ONLY_SINGLE_WORKROOM_WITH_LOWER_SIDE_ANIMAL_PEN_INSUFFICIENT_FAMILY_DISTINCTNESS','scope':'COD3 NPC01 original-record family sufficiency prefilter only','cases':[rv],'image_counts':[0,0,0],'raw_family_screen':bind(P/'raw-family-exclusion.json'),'limits':'0新图/0完整视觉参考。原状态判断侧院高差/覆草差异不足新整屋机制，不声称exact重复。156NPC05 first159已接纳仅carry0，不推累计；157NPC05/158NPC01待Main各最多1，COD4维持153差847。无Java/游戏/制作/主清单。','next':'继续固定本地用途相关完整建筑的原记录择优，避免单工作间/侧院变体凑数；1000不足不制作。','handoff':'160 swedish_butcher1原记录预筛：9×9×11 DV3105，891全存387非air504air，56palette/9原层/6BE/entities[]与5context实际读。单工作间西门/低东无门动物栏与覆草石坡顶，对059F02/081F02完整七观察及原比较保存，保守不足0，非exact复制判定。0PNG/0完整视觉研究/0提案。156 first159仅carry0，157NPC05与158NPC01各max1待Main；无Java/游戏/制作/主清单。'})
put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
s=(R/'docs/architecture/research-20261104-smithy-158/seal_screening.py').read_text()
s=s.replace('docs/architecture/research-20261104-smithy-157/latest-independent-admissions.json','docs/architecture/research-20261104-smithy-159/latest-independent-admissions.json')
s=s.replace("check('prior156 and157 pending exactly once',sorted((x['batch'],x['id'])for x in carry['carried_unresolved_whole_reference_proposals'])==[(156,'F01'),(157,'W01')])", "check('157NPC05 and158NPC01 remain pending exactly once',sorted((x['batch'],x['id'])for x in carry['carried_unresolved_whole_reference_proposals'])==[(157,'W01'),(158,'F01')])\ncheck('156 resolved first159 exact carry only',carry['156F01_NPC05_resolved_accept1_first159']==get('latest-independent-admissions.json')['newly_notified_NPC05_admission_156_F01'])")
s=s.replace("'source_bodies_visually_screened':len(cases)","'source_bodies_visually_screened':0,'raw_only_source_screens':len(cases)")
s=s.replace("'PASS_COMPLETE_ORIGINAL_SOURCE_READING_INTEGRITY_NOT_SEMANTIC_ADMISSION'","'PASS_RAW_ONLY_SOURCE_FAMILY_SCREEN_INTEGRITY_NO_VISUAL_STUDY'")
s=s.replace("'all_generated_projections_actually_viewed':True","'all_generated_projections_actually_viewed':False,'no_projections_generated_or_viewed':True")
s=s.replace('当前158 NPC01最多1待独立判定；153已first156接受仅carry0；156F01与157W01仅NPC05待审各最多1不重送','当前160原记录0；156F01 NPC05已first159接受仅carry0；153已first156接受仅carry0；157W01 NPC05与158F01 NPC01各最多1待审不重送')
(P/'seal_screening.py').write_text(s)
print('Prepared160 raw-only family sufficiency hold0; no PNG, no credit,156 carry0')

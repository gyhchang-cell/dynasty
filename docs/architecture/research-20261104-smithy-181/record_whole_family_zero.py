"""Complete fixed-local wetland workshop study, conserved existing-family zero."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PREV=P.parent/'research-20261104-smithy-180'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
screen=get(P/'pre-render-history-screen.json')['rows'];assert len(screen)==2
known=screen[0];assert not known['eligible_for_new_source_study'] and known['known_history'] and known['member'].endswith('merchant_campsite_tent_1.nbt')
machine={'id':'F01','source_archive':known['source_archive'],'member':known['member'],'status':'ALREADY_INDEXED_109_SAME_ORIGINAL_SOURCE_MACHINE_SKIP','known_history':known['known_history'],'historical_exact_matches':known['historical_exact_matches'],'original_source_semantically_reread':False,'old_images_or_manual_judgment_reopened':False,'whole_reference_study':False,'formal_credit_added':0}
r=get(P/'preassessment-original-sources.json')['rows'][0];assert r['id']=='F02';d=r['original'];pal=d['palette'];cells={tuple(b['pos']):b for b in d['blocks']}
source=get(P/'sources.json')['candidates'][0]
old_path=P.parent/'research-20261104-smithy-153/manual-review.json';old=get(old_path)['cases'][0]
observations={
 'layout':'一体单层作坊，西短门颈接x3..5/z3..5共用厅，北x4/5,z2狭凹位放切石台与低阶，南x4/5,z6狭凹位为低阶陈设，东6,2,4炉和砖烟构同源。南北凹位均直接向厅开放，不是独立冷热房/卧室；无床/储箱/独立访客厅。',
 'proportion':'9×12×9/DV3465，972声明格只存577原记录=506非air+71显式air，395省略不当空气。地板y1/use2，中央高空腔延伸至y6，y7起收合屋盖/顶到y10，y11为烟帽；没有梯、上层楼板或第二经营层，12高不是12楼。',
 'facade':'mangrove_wood71围门颈和臂端，泥砖东炉服务面突出，外层muddy_mangrove_roots263与mangrove_roots112构宽厚悬挑收进轮廓。西门2,2/3,4 east/right/closed，仅一扇；两底vines接口不是住户/门或独立楼翼。图灰只是通用分类，不称灰石墙/瓦或原生精细造型。',
 'roof':'宽大多级根系壳盖在窄T工作核心上方收进，外表全块近似显得厚重，不能据此判断原生根系透明/碰撞/纹理效果。东砖烟构y3/4墙、y5/6 double泥砖slab、上砖与slab延伸至y11墙帽，非已验通烟；悬灯4,7,4上方壳不代表阁楼。',
 'materials':'切石台4,2,2 north，北侧4,2,1为mangrove_wood，实际接近空间在南4,2,3显式air；东炉6,2,4 west/unlit/Items[]/CookBurnTotal0/RecipesUsed{}，前5,2/3,4为air。南4/5,2,6 mudbrick bottom阶south、北5,2,2 bottom阶north均低陈设，不当上楼梯。原无水/熔岩/铁砧/锻造台/床/箱，切石+炉是加工空间参考，不是完整铁匠制造流水线。',
 'circulation':'西socket0,1,4 west_up/empty/final mangrove_stairs[facing=east]原仅facing明确；旁0,1,z3/5为east/bottom干红树阶。经西门到中央厅，北/南凹位从同层厅分流，东炉留前一格原air；公众和工人共享这条工作通路，无独立私人区。门/半块/根系/vine新增后的实际净空与NPC路径未在游戏验证。',
 'terrain':'源包含自身底基、T地板、围护、宽壳和东炉服务构件，非任一屋顶碎片；不要求另接房翼。两floor vines接头3,2,5 up_east及5,2,3 up_south均真实vines池/finalair，非empty；feature池仅1feature条目，底饰不算两栋。原基底泥根和屋盖需山脚承托/排水再设计，未落世界。'
}
comparison={
 'status':'COMPLETE_RELATED_WHOLE_STUDY_EXISTING_T_WORKSHOP_FAMILY_ZERO',
 'complete_saved_153_original_written_record_preserved':old,
 'old153_seven_screening_observations_and_all_four_complete_saved_comparisons_actually_read':True,
 'old153_image_bindings_preserved_not_new_image_viewings':True,
 'old_binding':bind(old_path),
 'comparison':'与已完整保存的153巨型针叶林masons_house2相比，181的use整体上抬一格，但西2,z4门→中央x3..5/z3..5共厅→北4/5,z2切石/阶、南4/5,z6阶、东6,z4炉的组织相同。两源壳盖材质、加厚根系、烟构高度和vines接口变化没有形成新工作/公共/私密分流。相关且整栋已实际研究，仍保守家族0；不把换色、职业、屋高或指纹不完全相同当新颖证明，也不声称逐NBT字节完全同一。',
 'prior153_independent_admission_reused_not_reaccepted':'Existing latest-independent-admissions.json /newly_notified_admission_153_F01; first bound156, all later carry0',
 'new_images_or_sourcechains_of_old153_reopened':False,
 'proposal_maximum':0,'formal_credit_added':0
}
put('saved-family-comparison.json',comparison)
images=[bind(p) for p in sorted(P.glob('*.png'))];assert len(images)==7
case={**source,'observations':observations,'images_actually_viewed':images,
 'whole_boundary':'完整单源地板/围护/壳盖/门厅及东炉服务端；既有单层T共用厅家族。Vine装饰与入口不强制另屋翼；原生碰撞/生成/使用安全未验。',
 'semantic_family_comparison':comparison,'actual_full_reference_study_complete':True,
 'credit_proposal_maximum':0,'status':'COMPLETE_RELATED_T_WORKSHOP_ALREADY_EXISTING_FAMILY_ZERO','native_acceptance':False}
put('manual-review.json',{'cases':[case],'machine_only_exclusions':[machine],'complete_whole_reference_studies':1,'generated_current_png':7,'actual_current_images_viewed':7,'pending_maximum':0,'formal_credit_added':0,'no_independent_self_admission':True})
ss=get(P/'sources.json');ss['machine_only_exclusions']=[machine];put('sources.json',ss)
contexts=get(P/'source-context.json')
put('actual-reading-boundary.json',{'id':'F02','actual_images_viewed':images,'original_index_grids_actually_read':[{'y':y,'z_rows_x_indices':[[cells.get((x,y,z),{}).get('state','?') for x in range(9)] for z in range(9)]} for y in range(12)],'declared_grid_positions_read':972,'stored_original_state_indices_actually_read':577,'omitted_positions_not_air':395,'all_palette_entries_actually_read':24,'all_complete_BE_actually_read':4,'all_entities_actual_read':[],'complete_source_context_JSON_actually_read':[c['member'] for c in contexts['candidates'][0]['contexts']],'complete_metadata_text_actually_read':[c['member'] for c in contexts['metadata']],'F01_original_semantic_reread':False,'not_read_or_verified':['vine configured feature implementation and actual growth/placement','zombie fallback terminators and entire village/root/biome chains','runtime processor execution, paths, collision, door/headroom/fire/terrain behavior','native-material visual rendering or production assets'],'new_reference_credit':0})
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('577stored972volume395omitted',d['size']==[9,12,9] and d['DataVersion']==3465 and len(d['blocks'])==len(cells)==577 and 972-len(cells)==395)
ck('24palette4BE0entities',len(pal)==24 and sum('nbt'in b for b in d['blocks'])==4 and d.get('entities',[])==[])
ck('air71_nonair506',r['material_counts']['minecraft:air']==71)
ck('cutter4_2_2north',cells[(4,2,2)]['state']==11 and pal[11]['Properties']['facing']=='north')
ck('cutter_north_solid_south_air',cells[(4,2,1)]['state']==2 and cells[(4,2,3)]['state']==9)
ck('furnace6_2_4west_empty_unlit',cells[(6,2,4)]['state']==23 and cells[(6,2,4)]['nbt']=={'CookTime':0,'BurnTime':0,'Items':[],'id':'minecraft:furnace','CookTimeTotal':0,'RecipesUsed':{}} and pal[23]['Properties']=={'lit':'false','facing':'west'})
ck('one_door_two_halves',cells[(2,2,4)]['state']==10 and cells[(2,3,4)]['state']==14)
ck('central_ground_hall_original_air',all(cells[(x,y,z)]['state'] in [9,21,22] for x in range(3,6) for y in (2,3) for z in range(3,6)))
ck('north_south_bare_recess_no_extra_rooms',cells[(5,2,2)]['state']==13 and all(cells[(x,2,6)]['state']==12 for x in (4,5)))
ck('two_vine_sockets_true_pool_finalair',all(cells[p]['nbt']['pool']=='repurposed_structures:villages/swamp/vines' and cells[p]['nbt']['final_state']=='minecraft:air' for p in [(3,2,5),(5,2,3)]))
ck('entrance_empty_not_actualstreet',cells[(0,1,4)]['nbt']['pool']=='minecraft:empty' and cells[(0,1,4)]['nbt']['final_state']=='minecraft:mangrove_stairs[facing=east]')
ck('no_beds_ladder_chests',not any(any(k in p['Name'] for k in ['bed','ladder','chest','barrel']) for p in pal))
ck('5fullcontext2metadata',len(contexts['candidates'][0]['contexts'])==5 and len(contexts['metadata'])==2)
ck('old153_full7_and4_saved_comparisons',len(old['screening_observations'])==7 and len(old['saved_written_comparisons'])==4 and all(len(c['complete_saved_observations_actually_read'])==7 for c in old['saved_written_comparisons']))
ck('7generated7viewed',len(images)==7)
for s in screen:ck(s['id']+'_fixed_archive',bind(s['source_archive'])==s['fixed_archive'])
for g in get(P/'protected-inputs.json')['files']:ck('protected_unchanged_'+g['path'],bind(g['path'])==g)
carry=get(PREV/'carried-forward-pending.json');carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
ck('157pending_preserved',[(p['batch'],p['id']) for p in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')])
put('carried-forward-pending.json',carry);put('latest-independent-admissions.json',get(PREV/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_COMPLETE_WHOLE_STUDY_CONSERVATIVE_EXISTING_FAMILY_ZERO','checks':checks,'check_count':len(checks),'machine_assertions_not_credit':True,'java_run':False,'native_acceptance':False})
s={'batch':181,'status':'COMPLETE_WETLAND_T_WORKSHOP_STUDIED_EXISTING153_FAMILY_ZERO','complete_whole_reference_studies':1,'machine_only_exclusions':1,'actual_images_viewed':7,'generated_png':7,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'174first177_later_carry_increment':0,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'182 prioritize truly related complete designs and whole work/public/private organization;157W01 pending only.1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':182})
(P/'HANDOFF.md').write_text('181 F02完整湿地T作坊全栋研究：7PNG实际看完，12全原索引层577已存/395省略、24pal/4BE/entities[]全读，5完整JSON+2metadata全文读；完整7维观察、源绑定、原始阅读范围与旧153完整7观察/4个原比较均保存。西门颈→共厅→北切石凹位/南阶凹位/东炉，与旧153同工作组织；抬高一层和根系厚壳无新分流，保守family0，不是未读或非整栋。源本身完整相关但0新增信用，不制作。F01 merchant tent1为旧109相同源机器排除，无旧语义/图重读。仅157pending；174首次177+1后carry0。未读vine feature具体实现/zombie fallback等不冒称完整村落生成，不Java/游戏/资产/清单操作。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(get(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))

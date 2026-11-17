"""Three machine exclusions plus one bounded original-state weaponsmith family screen."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PREV=P.parent/'research-20261104-smithy-179'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
screen=get(P/'pre-render-history-screen.json')['rows'];excluded=screen[:3]
expected=['bamboo/houses/armorer_1.nbt','birch/houses/armorer_house_1.nbt','crimson/houses/armorer_house_1.nbt']
machines=[]
for r,member in zip(excluded,expected):
 assert not r['eligible_for_new_source_study'] and len(r['historical_exact_matches'])==1
 m=r['historical_exact_matches'][0];assert m['source']['member'].endswith(member) and set(m['exact_keys'])=={'role_sha256','occupancy_sha256'}
 machines.append({'id':r['id'],'source_archive':r['source_archive'],'member':r['member'],'historical_exact_match':m,'status':'EARLY_MACHINE_ROLE_OCCUPANCY_EXCLUSION_ONLY','actual_palette_BE_planes_semantically_read':False,'whole_reference_study':False,'formal_credit_added':0,'limit':'Normalized space fingerprints, not NBT-byte identity; no new semantic family credit.'})
r=get(P/'preassessment-original-sources.json')['rows'][0];assert r['id']=='F04' and screen[3]['eligible_for_new_source_study']
d=r['original'];pal=d['palette'];cells={tuple(b['pos']):b for b in d['blocks']}
saved_path=P.parent/'research-20261104-smithy-172/saved-family-comparison.json';saved=get(saved_path)
comparison={'saved172_complete_written_comparison_reused_after_previous_actual_reading':saved,'binding':bind(saved_path),'old067_057_images_NBT_or_sourcechains_reopened':False,'old_manual_observations_newly_recounted':False,'current_comparison':'F04北前开放工作棚接南单门后共同室，东北岩浆/西砂轮/中央双炉竖叠，东凹箱与后室共用；仍在067/057及172已经完整保存比较的前棚→后共同室/凹箱家族，不按darkforest材质、高度、屋盖细节或双炉数量新增。不同原状态不是断言NBT完全重复；不声称穷尽全球家族。','credit_proposal_maximum':0}
put('saved-family-comparison.json',comparison)
note='9×8×11/DV3465，476原存=373非air+103显式air，另316省略不当air。北棚西grindstone(2,1,1)floor/east，东北lava(6,1,z1/2)level0，中央竖炉(4,2/3,3)west/unlit/Items[]/allcookburn0；南门(2,1/2,6)south/right/closed进后共同室，东凹箱(6,1,4)south/vanillaweaponsmith seed-5946595825149811903；不是两家铺或两层工作地。原floor y0、use y1，高双炉非上层；屋盖darkoakstairs64和smoothstonebottomslab15，烟柱至y6不证通烟。8原索引全层/34pal/4完整BE/entities[]及两selectedpool片段实际读，0PNG/0全context/0整栋视觉研究。入口(0,0,3)west_up指向真实dark_forest/streets，finalgranite阶east/bottom/straight/dry；normal/zombie各weight2、legacy/rigid对应mossify/zombify处理器，处理器全文未读不推演替换。'
case={'id':'F04','source_archive':r['source_archive'],'member':r['member'],'status':'RAW_EXISTING_FRONT_SHED_REAR_COMMON_ROOM_FAMILY_ZERO','observations_bounded_not_full_visual_study':note,'semantic_family_comparison':comparison,'images_actually_viewed':[],'credit_proposal_maximum':0,'formal_credit_added':0,'native_acceptance':False}
put('sources.json',{'candidates':[{k:r[k] for k in ('id','source_archive','member')}],'machine_only_exclusions':machines,'metadata_not_reference_credit':True})
put('manual-review.json',{'cases':[case],'machine_only_exclusions':machines,'complete_whole_reference_studies':0,'formal_credit_added':0,'pending_maximum':0})
put('actual-reading-boundary.json',{'id':'F04','all_original_index_planes_actually_read':[{'y':y,'z_rows_x_indices':[[cells.get((x,y,z),{}).get('state','?') for x in range(9)] for z in range(11)]} for y in range(8)],'declared_grid_positions_read':792,'stored_original_indices_actually_read':476,'omitted_positions_not_air':316,'all_palette_entries_actually_read':34,'all_complete_BE_actually_read':4,'all_entities_actual_read':[],'selected_pool_snippets_only_read':r['selected_pool_snippets'],'full_context_or_metadata_read':False,'actual_images_viewed':0,'whole_visual_study':False,'F01_F02_F03_actual_original_semantic_readings':0})
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('four_screen_rows_three_exclusions_one_eligible',len(screen)==4 and [x['eligible_for_new_source_study'] for x in screen]==[False,False,False,True])
ck('sizeDV',d['size']==[9,8,11] and d['DataVersion']==3465)
ck('476stored_unique316omitted',len(d['blocks'])==len(cells)==476 and 792-len(cells)==316)
ck('34pal4BE0entities',len(pal)==34 and sum('nbt'in b for b in d['blocks'])==4 and d.get('entities',[])==[])
ck('air103_nonair373',r['material_counts']['minecraft:air']==103)
ck('grind2_1_1',cells[(2,1,1)]['state']==11)
ck('two_lava_cells',all(cells[(6,1,z)]['state']==14 for z in (1,2)))
ck('stacked_furnaces_empty',all(cells[(4,y,3)]['state']==33 and cells[(4,y,3)]['nbt']=={'CookTime':0,'BurnTime':0,'Items':[],'id':'minecraft:furnace','CookTimeTotal':0,'RecipesUsed':{}} for y in (2,3)))
ck('south_closed_door',all(cells[(2,y,6)]['state']==s for y,s in [(1,12),(2,16)]))
ck('south_chest_seed',cells[(6,1,4)]['state']==32 and cells[(6,1,4)]['nbt']['LootTableSeed']==-5946595825149811903)
ck('entrance_actual_darkforest_street',cells[(0,0,3)]['nbt']['pool']=='repurposed_structures:villages/dark_forest/streets')
ck('no_ladder_beds_anvil_smithtable',not any(any(k in p['Name'] for k in ['ladder','bed','anvil','smithing_table']) for p in pal))
ck('two_selectedpool_snippets',len(r['selected_pool_snippets'])==2)
for row in screen:ck(row['id']+'_fixed_archive',bind(row['source_archive'])==row['fixed_archive'])
for g in get(P/'protected-inputs.json')['files']:ck('protected_unchanged_'+g['path'],bind(g['path'])==g)
ck('no_png',not list(P.glob('*.png')))
carry=get(PREV/'carried-forward-pending.json');carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
ck('157pending_only',[(p['batch'],p['id']) for p in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')])
put('carried-forward-pending.json',carry);put('latest-independent-admissions.json',get(PREV/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_THREE_EARLY_EXCLUSIONS_AND_ONE_BOUNDED_RAW_FAMILY_ZERO','checks':checks,'check_count':len(checks),'machine_assertions_not_reference_credit':True,'java_run':False,'native_acceptance':False,'initial_unsealed_lookup_error':'Jungle member initially used armorer_house_1; fixed against existing metadata to actual armorer_1 before successful screen; failed lookup produced no sealed result or source semantic claim.'})
s={'batch':180,'status':'THREE_MACHINE_VARIANT_EXCLUSIONS_ONE_RAW_WEAPONSMITH_EXISTING_FAMILY_ZERO','complete_whole_reference_studies':0,'machine_only_exclusions':3,'raw_original_sources_bounded_screened':1,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'174first177_later_carry_increment':0,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'181 continue fixed-local truly related distinct complete architectural references;157W01 pending only.1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':181})
(P/'HANDOFF.md').write_text('180：3机器早排0(jungle armorer1→旧bamboo、oak armorerhouse1→旧birch、warped armorerhouse1→旧crimson)，无这些源palette/BE/planes语义阅读。F04 darkforest weaponsmith1全8原索引层476已存/316省略、34pal/4BE/空实体、2selectedpool片段实际读；0PNG/0全context/0whole，前工作棚→后共同室凹箱既有家族0。旧067/057完整实际阅读及比较复用172保存全对象，不重开旧图源链或新计阅读。174首次177+1后当前carry0，仅157pending。无Java/游戏/资产/主清单改动。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(get(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))

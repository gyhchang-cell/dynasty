"""No-credit raw ocean armorer family screen plus saved Main carry verification."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[2];PREV=P.parent/'research-20261104-smithy-175'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
r=get(P/'preassessment-original-sources.json')['rows'][0];d=r['original'];pal=d['palette'];cells={tuple(b['pos']):b for b in d['blocks']}
old_path=P.parent/'research-20261104-smithy-068/manual-review.json';old=next(c for c in get(old_path)['cases'] if c['id']=='F01')
main_path=R/'docs/cod4/audit-20261022/coordinator-smithy170-first173-zero-carry-review-20261110.json';main=get(main_path)
assert bind(main_path)['sha256']=='a43f8ab8ce86cf1af67bab04a58c6d6bc2f53920bdba0abb7c1359d11934461f' and bind(main_path)['bytes']==6849
put('Main173-carry-integrity-only.json',{'receipt':bind(main_path),'complete_Main_verification_object_actually_read':main,'current_increment':0,'no_old_source_or_images_reopened':True})
comparison={'complete_saved_068F01_actual_read':old,'binding':bind(old_path),'current_observation':'本源西两格无门开口进单室，北东8smooth_stone同折台、南中同north高炉/砖后烟柱；相对068F01主要抬高一格、水/含水与上下滴水石及材料改变，未形成独立工作组织。水环境和滴水石增加通行/功能疑点，但不能凭环境换皮申报新家族，也不伪称NBT/角色/占位完全相同。','proposal_maximum':0,'old_images_sources_or_context_reopened':False,'old_admission_increment':0}
put('saved-family-comparison.json',comparison)
note='海洋甲匠屋9×9×8/DV3465，362原记录、无显式air、51water，其余311非water；286省略不当air或water。西开口z3/4，北东smooth_stone8台、南中(4,2,5)north未点燃空高炉，后砖/墙烟柱至y8。无门/床/梯/箱/其他锻造工位。35pointed_dripstone包括y2上尖与y5/6下尖，原waterlogged true，工作地带并非清空；不运行验证可达/溺水/机器燃烧。屋盖80oak_stairs/3slab原均含水，不据分类图认全石盖。selected ocean house pool weight2/legacy/rigid，入口empty/final含水cobble阶；randomize处理器及全池/metadata未读。原单室折台后炉工作组织与068F01相同家族，保守0。'
put('manual-review.json',{'cases':[{'id':'F01','source_archive':r['source_archive'],'member':r['member'],'status':'RAW_EXISTING_SINGLE_ROOM_RETURN_COUNTER_REAR_BLAST_FAMILY_ZERO','observations_bounded_not_full_visual_study':note,'semantic_family_comparison':comparison,'images_actually_viewed':[],'credit_proposal_maximum':0,'formal_credit_added':0,'native_acceptance':False}],'complete_whole_reference_studies':0,'formal_credit_added':0})
put('actual-reading-boundary.json',{'original_index_grids_actually_read':[{'y':y,'z_rows_x_indices':[[cells.get((x,y,z),{}).get('state','?') for x in range(9)] for z in range(8)]} for y in range(9)],'declared_grid_positions_read':648,'stored_original_indices_read':362,'omitted_positions_not_air':286,'all_palette_entries_actually_read':29,'all_BE_actually_read':2,'all_entities_actual_read':[],'selected_pool_snippets_read':r['selected_pool_snippets'],'full_context_or_metadata_read':False,'actual_images_viewed':0,'whole_visual_study':False})
put('sources.json',{'candidates':[{k:r[k] for k in ('id','source_archive','member')}],'metadata_not_reference_credit':True})
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('size_DV',d['size']==[9,9,8] and d['DataVersion']==3465)
ck('stored362_unique_omitted286',len(d['blocks'])==len(cells)==362 and 648-len(cells)==286)
ck('29palette_2BE_noentities',len(pal)==29 and sum('nbt'in b for b in d['blocks'])==2 and d.get('entities',[])==[])
ck('water51_air0',r['material_counts']['minecraft:water']==51 and r['material_counts'].get('minecraft:air',0)==0)
ck('dripstone35_smoothstone8',r['material_counts']['minecraft:pointed_dripstone']==35 and r['material_counts']['minecraft:smooth_stone']==8)
ck('blast_exact_pos_and_empty',cells[(4,2,5)]['state']==28 and cells[(4,2,5)]['nbt']=={'CookTime':0,'BurnTime':0,'Items':[],'id':'minecraft:blast_furnace','CookTimeTotal':0,'RecipesUsed':{}})
ck('entrance_empty_not_actual_road',cells[(0,1,4)]['nbt']['pool']=='minecraft:empty' and 'waterlogged=true' in cells[(0,1,4)]['nbt']['final_state'])
ck('no_beds_doors_ladders_storage',not any(any(k in p['Name'] for k in ['bed','door','ladder','chest','barrel']) for p in pal))
ck('old7observations_and_fullcomparison',len(old['observations'])==7 and bool(old['semantic_family_comparison']))
for g in get(P/'protected-inputs.json')['files']:ck('protected_unchanged_'+g['path'],bind(g['path'])==g)
ck('no_png',not list(P.glob('*.png')))
ad=get(PREV/'latest-independent-admissions.json');ad['170first173_Main_carry_integrity_only']=get(P/'Main173-carry-integrity-only.json');put('latest-independent-admissions.json',ad)
carry=get(PREV/'carried-forward-pending.json');carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
ck('pending157_174_preserved',[(c['batch'],c['id']) for c in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01'),(174,'F01')])
put('carried-forward-pending.json',carry);put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_RAW_FAMILY_SCREEN_AND_EXACT_MAIN_CARRY_INTEGRITY_OBJECT','checks':checks,'check_count':len(checks),'java_run':False,'machine_assertions_not_credit':True,'native_acceptance':False})
s={'batch':176,'status':'OCEAN_ARMORER_RAW_EXISTING_FAMILY_ZERO_AND_MAIN173_INTEGRITY_CARRY','complete_whole_reference_studies':0,'raw_original_sources_bounded_screened':1,'actual_images_viewed':0,'generated_png':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'native_acceptance':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'177 continue fixed-local distinct complete relevant source study;157W01/174F01 pending,1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':177})
(P/'HANDOFF.md').write_text('176 ocean armorer_house_1：9原始全索引层362已存/286省略、29palette/2BE/空实体及1selectedpool片段实际阅读，0PNG/0fullcontext。单室北东折台/南中高炉原工作组织与068F01同家族，水/滴水石不构成新参考，0信用。068F01完整7观察和原family比较实际读取保存，未重开旧图或源链。Main173carry完整核验6849B全文实际读并原样保存在Main173-carry-integrity-only.json及admissions，当前carry0；173遗留relevance字样以完整family-zero判词为准。157与174仍pending，无Java/产品/清单变动。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'checks':len(checks),'files':len(get(P/'RECEIPT.json')['files'])},ensure_ascii=False))

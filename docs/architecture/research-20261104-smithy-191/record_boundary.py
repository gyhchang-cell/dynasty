import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parent;OLD=P.parent/'research-20261104-smithy-190'
assert not (P/'RECEIPT.json').exists()
def read(p):return json.loads(p.read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=p.resolve();b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
d=read(P/'pre-render-history-screen.json');a=read(P/'preassessment-original-sources.json')['rows'][0];r=a['original'];src={k:d['rows'][1][k] for k in ['id','source_archive','member','nbt_sha256']}
observations={
'layout':'F02单体小石工屋原状态：西侧开口x2/z3，室内x3..5/z2..6；切石(4,2,6)north，水68格与clay13、向上滴水石tip5占据工作室，没有独立卧室、箱储、分厅或附楼。不是新工居复合布局。',
'proportion':'8×8×9/DV3465，576声明343存，全部为非air，显式air0、省略233。完整读8原索引层/28palette/1BE/entities[]；只作有界原状态预筛，未生成图或完成整栋视觉研究。',
'facade':'去皮橡木柱x2/6与cyan_terracotta墙，小型西开口无door；y2西北外缘seagrass和海泡菜、栅栏全waterlogged=true。水下状态明确，不称干燥可用工作间。',
'roof':'y4 z0/8、y5 z1/7、y6 z2/6、y7 z3/5楼梯逐层收拢至y7 z4橡木板脊，所有屋面楼梯waterlogged=true；梁下水及倒向滴水石不作上层房间或楼梯。',
'materials':'dirt47/cobble41/oakplanks10/strippedoaklog22/cyanterracotta47/clay13/terracotta2/water68/pointeddripstone8/oakstairs68。唯一切石(4,2,6)north，下(4,1,6)cobble，上(4,3,6)water，北(4,2,5)clay，未形成新净空作业路线；不把水当空气。',
'circulation':'(0,1,3)west_up/aligned单jigsaw为building_entrance，pool原repurposed_structures:villages/ocean/streets，最终waterlogged=true的east/bottom/straight cobble阶。西开口入同室，无门/内梯/私区；水中浮游与NPC导航未验，不声称可用。',
'terrain':'y0实际dirt台基及y1cobble/少量planks底板保留，233省略不当air。该源仅原状态边界研究；1个street入口不代表缺房翼，但完整外界道路/水体/root及处理器未读取，未构造干燥地形或修源。'}
old188=P.parent/'research-20261104-smithy-188/manual-review.json';prior=read(old188)['cases'][0]['semantic_family_comparison']['complete_old085F01_original_saved_comparison_reused']
put('manual-review.json',{'cases':[{'id':'F01','member':d['rows'][0]['member'],'status':'KNOWN_172_ROLE_AND_OCCUPANCY_EXACT','actual_original_semantic_read':False,'PNG':0,'formal_credit_added':0},{'id':'F02','source':src,'observations':observations,'semantic_boundary':{'prior085_full_saved_case_preserved':prior,'reuse_binding':bind(old188),'actual_reading':'本批实际读188保存的完整085七项记录；未重开旧NBT/PNG/上下文；仅复用不加旧信用。','verdict':'BOUNDED_SINGLE_ROOM_UNDERWATER_OBSTRUCTED_VARIANT_ZERO','reason':'小单共同切石室，与085共用工间家族相比没有公共/私区或作业动线分层。68水、13clay、8滴水石及水淹立面屋面为状态/破损变化，不凭水下职业名新增语义建筑。非原NBT等同的断言。','proposal_maximum':0},'actual_full_reference_study_complete':False,'formal_credit_added':0,'native_acceptance':False},{'id':'F03','member':d['rows'][2]['member'],'status':'KNOWN_112_169_ROLE_AND_OCCUPANCY_EXACT','actual_original_semantic_read':False,'PNG':0,'formal_credit_added':0}],'generated_png':0,'actual_images_viewed':0,'complete_whole_reference_studies':0,'pending_maximum':0,'formal_credit_added':0})
put('actual-reading-boundary.json',{'new_original_sources_actual_semantic_read':['F02'],'original_layers_actual_read':list(range(8)),'declared_grid_positions_read':576,'saved_blocks':343,'explicit_air':0,'omitted_not_air':233,'palette_actual_read':28,'BE_full_actual_read':1,'entities_actual_read':[],'PNG_generated':0,'PNG_viewed':0,'full_context_JSON_actual_read':0,'full_metadata_actual_read':0,'selected_pool_snippets_machine_saved_not_read':True,'F01_F03_fingerprint_filter_only':True,'complete_whole_reference_studies':0,'formal_credit_added':0})
put('sources.json',{'candidates':[src],'fingerprint_only_exclusions':[d['rows'][i] for i in [0,2]],'machine_index_not_semantic_credit':True})
for n in ['latest-independent-admissions.json','carried-forward-pending.json']:
 v=read(OLD/n)
 if n=='carried-forward-pending.json':
  v['previous_batch_receipt']=bind(OLD/'RECEIPT.json');v['carried_unresolved_whole_reference_proposals']+=v['current_batch_new_pending'];v['current_batch_new_pending']=[];v['current_batch_pending_cases']=[]
 put(n,v)
ss={'batch':191,'status':'TWO_KNOWN_FINGERPRINT_EXCLUSIONS_ONE_RAW_UNDERWATER_ROOM_BOUNDARY_ZERO','formal_credit_added':0,'prior_admissions_current_increment':0,'186first187_later_carry_increment':0,'actual_new_original_semantic_source_studies':1,'complete_new_whole_reference_studies':0,'current_PNG':0,'COD4_accepted_baseline':153,'COD4_gap':847,'COD4_increment':0,'NPC05_increment':0,'NPC01_cumulative_not_inferred':True,'java_run':False,'game_run':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'190F01与157W01继续等独立审查；后续完整生产/生活案例优先，已知小室/构件/换材不凑数，1000未满不开始建筑制作。'}
put('session.json',ss);checks=[]
def check(n,b):checks.append({'name':n,'passed':bool(b)})
check('F01_F03_known_exact',not d['rows'][0]['eligible_for_new_source_study'] and not d['rows'][2]['eligible_for_new_source_study'])
check('F02_only_new_source',len(read(P/'preassessment-original-sources.json')['rows'])==1 and a['id']=='F02')
check('size_blocks_palette',r['size']==[8,8,9] and len(r['blocks'])==343 and len(r['palette'])==28)
check('noair_emptyentities_oneBE',not r['entities'] and sum('nbt'in b for b in r['blocks'])==1 and not any(r['palette'][b['state']]['Name']=='minecraft:air'for b in r['blocks']))
with zipfile.ZipFile(src['source_archive'])as z:check('source_NBT_hash',hashlib.sha256(z.read(src['member'])).hexdigest()==src['nbt_sha256'])
for f in read(P/'protected-inputs.json')['files']:check('protected:'+f['path'],bind(Path(f['path']))==f)
carry=read(P/'carried-forward-pending.json');check('190_pending_retained',any(x['batch']==190 and x['id']=='F01'for x in carry['carried_unresolved_whole_reference_proposals']));check('157_pending_retained',any(x['batch']==157 and x['id']=='W01'for x in carry['carried_unresolved_whole_reference_proposals']))
for k in ['182F01_NPC01_resolved_initial_review_HOLD0_first184','186F04_NPC01_resolved_accept1_first187']:check('carry_exact:'+k,carry[k]==read(OLD/'carried-forward-pending.json')[k])
check('noPNG',not list(P.glob('*.png')))
v={'status':'PASS'if all(c['passed']for c in checks)else'FAIL','checks':checks,'check_count':len(checks),'machine_assertions_not_credit':True};put('verification.json',v);put('active-checkpoint.json',{**ss,'verification':v['status']})
(P/'HANDOFF.md').write_text('191：F01 warped weaponsmith=172结构角色/占位exact，F03 cherry armorer house2=112/169 exact；均0语义阅读/0PNG。F02 ocean mason8×8×9，343非air/233省略/28pal1BE0entity，8原索引层全部实际读，水/黏土/滴水石占据共同小工间，085完整旧记录复用，预筛family0。0完整整例/0PNG/0context，不新增pending。190F01及157W01待审保留，既往接受/HOLD全文承接本批0；只写191，无Java/游戏/产品/清单变更。\n')
assert v['status']=='PASS'
put('RECEIPT.json',{**ss,'files':[bind(f)for f in sorted(P.iterdir())if f.is_file() and f.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(read(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))

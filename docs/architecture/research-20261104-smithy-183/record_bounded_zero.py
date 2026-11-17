import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PREV=P.parent/'research-20261104-smithy-182'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
r=get(P/'preassessment-original-sources.json')['rows'][0];d=r['original'];cells={tuple(b['pos']):b for b in d['blocks']};pal=d['palette']
obs={'layout':'原名称mason house但全部245格及整源四向图显示为露天材料堆/切石场：西北灰陶土堆、东北白陶土堆，切石4,1,4，箱2,2,4嵌西堆；无室内工作室、围护屋体或屋盖。用途相关但不能按完整相关建筑计数。','proportion':'7×5×7/DV3105，245全存79非air166air、0省略；19palette/3BE/entities[]均实际读。y4仅一花盆和东南灯杆横臂，不是屋顶/二楼。','facade':'开放边缘、散置材料体与一根darkoakfence灯杆，不存在四面建筑立面；分类灰色不是灰石材证明。','roof':'没有遮蔽作业台/箱区的屋盖，无完整屋壳；不把材料顶面和横灯臂当棚顶。','materials':'各陶土/黏土堆旁有切石台west与单箱east、vanilla village_mason seed-1213458977264315725；土18草14、原石1，三花盆、一吊灯。没有炉/床/砧/水/熔岩，不能说成砖窑或热锻坊。','circulation':'中央x3/z1..5多数y1/2原air形成露天堆间空隙；南3,1,6 entrance empty/finalair不补后屋。原地面y0有多个air，实际步进和NPC路径未验，不能从air等同可走。','terrain':'基底土草及材料台一并在源内，3,0,3村民池finalgrass是接口不是额外房翼。可视为完整独立露天场地设计，但不符合1000完整相关建筑要求，0新增。'}
images=[bind(P/'F01-whole.png')];generated=[bind(p) for p in sorted(P.glob('*.png'))];ctx=get(P/'source-context.json')
case={**get(P/'sources.json')['candidates'][0],'observations':obs,'images_actually_viewed':images,'actual_full_reference_study_complete':False,'status':'OPEN_MATERIAL_YARD_NOT_COMPLETE_BUILDING_ZERO','credit_proposal_maximum':0,'formal_credit_added':0,'native_acceptance':False}
put('manual-review.json',{'cases':[case],'complete_whole_building_reference_studies':0,'actual_images_viewed':1,'generated_current_png':7,'pending_maximum':0,'formal_credit_added':0})
put('actual-reading-boundary.json',{'original_index_grids_actually_read':[{'y':y,'z_rows_x_indices':[[cells[(x,y,z)]['state'] for x in range(7)] for z in range(7)]} for y in range(5)],'stored_original_indices_actually_read':245,'palette_entries_actually_read':19,'complete_BE_actually_read':3,'entities_actually_read':[],'actual_images_viewed':images,'generated_not_viewed':[f for f in generated if f['path']!=images[0]['path']],'context_status':'2 JSON and 3 metadata machine saved only, NOT manually read; no full-context claim','saved_context_JSON_members':[x['member'] for x in ctx['candidates'][0]['contexts']],'missing_members':ctx['candidates'][0]['missing'],'not_verified':['whole related building requirement not met','pool/processor/metadata texts unread','native render/terrain/collision/path/generation'],'formal_credit_added':0})
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('245dense19pal3BE0entity',d['size']==[7,5,7] and len(cells)==245 and len(pal)==19 and sum('nbt'in b for b in d['blocks'])==3 and d['entities']==[])
ck('166air79nonair',sum(pal[b['state']]['Name']=='minecraft:air' for b in d['blocks'])==166)
ck('cutter4_1_4west',pal[cells[(4,1,4)]['state']]['Name']=='minecraft:stonecutter' and pal[cells[(4,1,4)]['state']]['Properties']['facing']=='west')
ck('chest_seed',cells[(2,2,4)]['nbt']['LootTableSeed']==-1213458977264315725)
ck('no_roof_blocks_door_or_bed',not any(any(s in v['Name'] for s in ['door','bed','stairs','slab','planks']) for v in pal))
ck('7generated1actuallyviewed',len(generated)==7 and len(images)==1)
for a in get(P/'pre-render-history-screen.json')['rows']:
 b=Path(a['source_archive']).read_bytes();ck('fixed_archive_'+a['id'],len(b)==a['fixed_archive']['bytes'] and hashlib.sha256(b).hexdigest()==a['fixed_archive']['sha256'])
for g in get(P/'protected-inputs.json')['files']:ck('protected_'+g['path'],bind(g['path'])==g)
carry=get(PREV/'carried-forward-pending.json');ck('pending157and182',[(x['batch'],x['id']) for x in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01'),(182,'F01')]);carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[];put('carried-forward-pending.json',carry)
put('latest-independent-admissions.json',get(PREV/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_BOUNDED_OPEN_YARD_ZERO','checks':checks,'check_count':len(checks),'java_run':False})
s={'batch':183,'status':'BOUNDED_SOURCE_AND_ONE_WHOLE_DIAGRAM_OPEN_YARD_NOT_BUILDING_ZERO','formal_credit_added':0,'pending_maximum':0,'actual_images_viewed':1,'generated_png':7,'complete_whole_building_reference_studies':0,'COD4_accepted_baseline':153,'COD4_gap':847,'prior_admissions_current_increment':0,'java_run':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'157W01和182F01待独立审查；下一候选先原状态分辨完整屋体，再生成所需图。1000未达不制作。'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json')});(P/'HANDOFF.md').write_text('183F01 birch_forest_mason_1原名house实际露天材料堆/切石场，无屋壳/屋顶，0信用不交新待审。原5层245索引/19pal/3BE/entities[]全读，仅1整源四向PNG实际看，生成7其余6未看；2contextJSON/3metadata仅机器保存未读。完整建筑研究数0，不以完整露天场地偷换1000建筑。182已封存待独立审查；157仍pending。无Java/游戏/资产/Jar/主清单操作。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(get(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))

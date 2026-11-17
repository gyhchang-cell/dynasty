"""Record actual whole source reading; independent semantic admission still required."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;PREV=P.parent/'research-20261104-smithy-181'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
r=get(P/'preassessment-original-sources.json')['rows'][0];d=r['original'];pal=d['palette'];cells={tuple(b['pos']):b for b in d['blocks']};source=get(P/'sources.json')['candidates'][0]
obs={
'layout':'完整9×6×9冷加工住屋及外缘布置；主体围护x3..7/z3..7、内3×3空腔，西门3,0/1,5进起居储藏小室，东北箱5,0,4，东侧床6,0,z5/6，西南top阶4,0,6上置墙4,1,6。唯一切石台3,0,1位于屋体北西外侧，与床/箱分隔在屋壳两边；室内无工作台/炉，无第二专门工房。',
'proportion':'9×6×9/DV3465共486位置全部存储，109非air377显式air、0省略；28palette/5BE/entities[]全读。低矮单层小屋，y2厚檐框、y3..4收进屋盖、y5单slab顶帽；无梯、上层板或上使用层。室内地面使用块在y0，源未含y-1连续承托，不能把y0空格说成有实际地板。',
'facade':'packed_mud19与mangrove_wood46构短厚围护、外挑框檐；四角spruce_fence在y0/1重复，北南东中窗为open/top jungle_trapdoor，西单门open/west/left。门与活板原属性实际读，通用分类图把薄件画满格不能当封墙或碰撞证明。',
'roof':'y2木框外挑，y3大木盖以9个spruce_slab围边/顶帽，y4木十字与4个closed/bottom east spruce_trapdoor收进，y5单slab收尖；没有阁楼或可行走露台。木色/灰色是类别示意，不是原生屋面贴图验收。',
'materials':'北外石工台3,0,1 facingwest，附近andesite3,0,0和5,0,z1/2及棕烛/竹苗是零散布置，不叫完整连续加工院。箱5,0,4 south/single/非水，原名mason、vanilla village_mason loot seed5024059179709504184；床6,0,5 foot与6,0,6 head south。无熔岩/炉/砧/锻造台/水洗槽，不宣称热锻流水线。',
'circulation':'西门直接进同一3×3生活室，箱床共享内部空隙，无第二门/内部公私隔间。外切石台不经私室即可接近；从门外绕西北侧到外台的组织可研究，但源y0外侧多air、y-1不存，地面承托/步进/实际NPC路径未验，不能用空索引证明可行走。',
 'terrain':'单源完整围护/屋盖/床箱/外切石布置，不是单屋顶或房间碎片；1,0,4 up_west villager socket为真实savanna/villagers池、finalair，4,0,4 down_south building_floor empty/finalair是锚点而非补屋翼。当前Jar未找到含该location的template_pool JSON，vanilla村民池和loot也不在固定Jar内；配置注入、生成位置、基础承托与整村链未读未运行。'
}
oldpath=P.parent/'research-20261104-smithy-060/manual-review.json';old=get(oldpath)['cases'][2]
comparison={'old060_F03_binding':bind(oldpath),'old060_F03_complete_saved_case_preserved':old,'actual_new_reading':'当前实际读其完整7维书面观察；旧图/旧NBT/旧上下文未重开；并复用181已读153及其完整四比较的历史知识，不声称新读这些源。','comparison':'060F03维京屋室内冷工、北热台、东外砂轮，且无床；182是唯一切石台全在屋外，单门后仅床/箱生活室，没有室内加工及热台。与153/181共享T工作厅及162单冷工作室也不同。潜在语义差异是工作完全外置、生活与储藏同室，不是木材换色或屋盖变化；但单台室外是否足够区别所有既有家族须Main独立全案比较，不自行入账。','proposal_maximum':1,'formal_credit_added':0,'not_proof_of_global_novelty':True}
put('saved-family-comparison.json',comparison)
images=[bind(p) for p in sorted(P.glob('*.png'))];assert len(images)==7
case={**source,'observations':obs,'images_actually_viewed':images,'actual_full_reference_study_complete':True,'whole_boundary':'完整单源低屋体和外切石布置，不含低于y0的承托；完整建筑研究不等于完整世界生成链/路径验收。','semantic_family_comparison':comparison,'credit_proposal_maximum':1,'formal_credit_added':0,'status':'WHOLE_RELATED_OUTDOOR_COLDWORK_LIVING_COTTAGE_PENDING_INDEPENDENT_REVIEW','native_acceptance':False}
put('manual-review.json',{'cases':[case],'complete_whole_reference_studies':1,'actual_current_images_viewed':7,'generated_current_png':7,'pending_maximum':1,'formal_credit_added':0,'independent_review_required':True})
ctx=get(P/'source-context.json')
put('actual-reading-boundary.json',{'id':'F01','actual_images_viewed':images,'original_index_grids_actually_read':[{'y':y,'z_rows_x_indices':[[cells[(x,y,z)]['state'] for x in range(9)] for z in range(9)]} for y in range(6)],'stored_original_state_indices_actually_read':486,'omitted_positions':0,'palette_entries_actually_read':28,'complete_BE_actually_read':5,'entities_actually_read':[],'complete_context_JSON_actually_read':[],'metadata_texts_actually_read':[x['member'] for x in ctx['metadata']],'not_read_or_verified':['vanilla villager pool and loot absent from fixed Jar','location injection/root village/biome chain not established','terrain below source y0; native visuals/collision/NPC path/production/transactions'],'formal_credit_added':0})
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('dense486_6planes_no_omission',d['size']==[9,6,9] and d['DataVersion']==3465 and len(cells)==len(d['blocks'])==486)
ck('28palette5BE0entities',len(pal)==28 and sum('nbt' in b for b in d['blocks'])==5 and d['entities']==[])
ck('377air109nonair',sum(pal[b['state']]['Name']=='minecraft:air' for b in d['blocks'])==377)
ck('outside_northcutter_west',pal[cells[(3,0,1)]['state']]=={'Name':'minecraft:stonecutter','Properties':{'facing':'west'}})
ck('single_west_open_door_two_halves',all(pal[cells[(3,y,5)]['state']]['Name']=='minecraft:jungle_door' and pal[cells[(3,y,5)]['state']]['Properties']['open']=='true' for y in (0,1)))
ck('bed_south_foothead',all(pal[cells[(6,0,z)]['state']]['Properties']['part']==v for z,v in [(5,'foot'),(6,'head')]))
ck('chest_loot_seed',cells[(5,0,4)]['nbt']['LootTableSeed']==5024059179709504184)
ck('no_hotwork_no_ladder',not any(any(k in e['Name'] for k in ['furnace','lava','anvil','smithing_table','ladder']) for e in pal))
ck('3metadata_0contexts_2missing',len(ctx['metadata'])==3 and not ctx['candidates'][0]['contexts'] and len(ctx['candidates'][0]['missing'])==2)
ck('old060_F03_sevenobservations',len(old['observations'])==7)
for a in get(P/'pre-render-history-screen.json')['rows']:ck('fixed_archive_'+a['id'],bind(a['source_archive'])==a['fixed_archive'])
for g in get(P/'protected-inputs.json')['files']:ck('protected_'+g['path'],bind(g['path'])==g)
carry=get(PREV/'carried-forward-pending.json');ck('prior157only',[(p['batch'],p['id']) for p in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]);proposal={'batch':182,'id':'F01','scope':'COD3 NPC01 complete outdoor coldwork/living cottage','proposal_maximum':1,'formal_credit_added':0,'manual_review':bind(P/'manual-review.json'),'status':'PENDING_INDEPENDENT_WHOLE_SEMANTIC_REVIEW'}
carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=1;carry['current_batch_pending_cases']=[proposal];carry['carried_unresolved_whole_reference_proposals'].append(proposal);put('carried-forward-pending.json',carry)
put('latest-independent-admissions.json',get(PREV/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_RECORDED_ACTUAL_STUDY_NOT_ADMISSION','checks':checks,'check_count':len(checks),'java_run':False,'native_acceptance':False})
s={'batch':182,'status':'COMPLETE_WHOLE_STUDY_SAVED_PENDING_MAIN','complete_whole_reference_studies':1,'actual_images_viewed':7,'formal_credit_added':0,'pending_maximum':1,'prior_admissions_current_increment':0,'174first177_later_carry_increment':0,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'Main独立审查182F01是否与旧家族不同；157W01保持pending，1000未达不制作。'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json')})
(P/'HANDOFF.md').write_text('182F01完整nilotic mason小屋实际研究完成：7PNG全看、6层486原索引、28pal/5BE/entities[]、3metadata全文读。0contextJSON，vanilla池/loot缺失及注入/root链未读。北西外切石台；西单门后床/箱生活室，没有内部工作台/热作。与060F03七维原观察完整比较并保留，潜在工作全外置/生活内置差异，提交最大1待Main独立语义全案判断，正式0。不靠名字/材质/指纹判新颖。157W01仍pending、历史174first177后carry0。未Java/游戏/资产/Jar/主清单。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(get(P/'RECEIPT.json')['files']),'checks':len(checks)},ensure_ascii=False))

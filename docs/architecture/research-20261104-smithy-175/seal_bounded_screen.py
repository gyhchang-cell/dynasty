"""Seal bounded original-state relevance screens; none is a credited whole study."""
import json, hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
PREV=P.parent/'research-20261104-smithy-174'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(Path(p).read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
rows=get(P/'preassessment-original-sources.json')['rows']
planes=[(10,11,12),(12,13,14,15),(17,18,19,20)]
notes=[
 '法师屋局部：最高y12仅铁砧(14,12,7)east，下面y11该点为east/bottom石砖阶，周围最高层全air；y10/11为石砖/阶/墙围合顶部构件，中央另有(15,11,5)lit空soul_campfire；原梯止y9。下部酿药台原两药水含swiftness/strong_leaping tag。未证明屋顶铁砧为可使用锻造工作空间，不凭铁砧计相关整屋；不擅称原作者装饰意图或实际掉落结果。',
 '旧蘑菇村屋局部：y12云杉top板夹双梯至y12；y13内层北两个桶夹lit空soul_campfire，东一对黑床，南侧scaffolding/loom与(5,13,6)west damaged_anvil，y14局部cyan_carpet装饰、y15收盖。砧与生活/织布家具同处紧凑层，未证明独立工艺/作坊分流；既不以床否定一切工作可能，也不凭砧+营火认定锻造作坊。无selected_pool命中，jigsaw原池/structure_void非empty事实保留，完整性仍未全查。',
 '奇怪房屋局部：y17木层接y18两扇south闭合门，内部灰/黑毯、红石线、桶、无播放记录的jukebox。南侧砂轮(7,18,9)floor/south，东邻(8,18,9)spruce_stairs top/south及(9,18,9)cauldron，上方(8,19,9)potted_brown_mushroom；其组合不能自动证明冷作业区，家具用途未由更完整来源证实。无炉/砧/锻造台/岩浆marker不等于整屋用途已判明。原3spawners与红石仅机器清单未读完整BE且未运行；省略不当air。'
]
readings=[];cases=[]
for r,ys,note in zip(rows,planes,notes):
 d=r['original'];pal=d['palette'];c={tuple(b['pos']):b for b in d['blocks']};used=sorted({b['state'] for b in d['blocks'] if b['pos'][1] in ys})
 grids=[{'y':y,'z_rows_x_indices':[[c.get((x,y,z),{}).get('state','?') for x in range(d['size'][0])] for z in range(d['size'][2])]} for y in ys]
 readings.append({'id':r['id'],'original_index_grids_actually_read':grids,'full_palette_entries_actually_read_for_those_grids':{str(i):pal[i] for i in used},'original_stored_indices_read':sum(b['pos'][1] in ys for b in d['blocks']),'full_BE_in_read_planes_actually_read':[b for b in d['blocks'] if b['pos'][1] in ys and 'nbt'in b],'functional_positions_read':[{**b,'state_original':pal[b['state']]} for b in d['blocks'] if any(k in pal[b['state']]['Name'] for k in ['ladder','anvil','grindstone','campfire','brewing_stand','jigsaw','bed'])],'selected_pool_snippets_only':r['selected_pool_snippets'],'full_context_or_metadata_read':False,'whole_image_read':False,'all_palette_or_BE_or_entities_read':False})
 cases.append({'id':r['id'],'source_archive':r['source_archive'],'member':r['member'],'size':d['size'],'DataVersion':d['DataVersion'],'status':'BOUNDED_RELEVANCE_UNPROVEN_ZERO_NO_WHOLE_STUDY','observations_bounded_not_seven_whole_dimensions':note,'formal_credit_added':0,'credit_proposal_maximum':0,'images_actually_viewed':[],'native_acceptance':False})
put('actual-reading-boundary.json',{'rows':readings,'scope':'Bounded relevance screen, not whole-building studies. Initial combined display clipped 2 tokens in F02 anvil entry; exact entry independently reprinted. Other full palette/BE outside selected planes remain unread, entities unread. No claim that all source content was read.','generated_png':0,'actual_images_viewed':0,'formal_credit_added':0})
put('sources.json',{'candidates':[{k:r[k] for k in ('id','source_archive','member')} for r in rows],'machine_metadata_not_whole_credit':True})
put('manual-review.json',{'cases':cases,'complete_whole_reference_studies':0,'formal_credit_added':0,'pending_maximum':0,'no_independent_self_admission':True})
checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('three_eligible_originals',len(rows)==3 and all(r['eligible_for_new_source_study'] for r in get(P/'pre-render-history-screen.json')['rows']))
ck('actual_stored_index_bounds',[r['original_stored_indices_read'] for r in readings]==[660,324,513])
ck('actual_full_used_palette_bounds',[len(r['full_palette_entries_actually_read_for_those_grids']) for r in readings]==[17,23,51])
for r in rows:
 d=r['original'];ck(r['id']+'_distinct_positions',len(d['blocks'])==len({tuple(b['pos']) for b in d['blocks']}))
 dnames=[p['Name'] for p in d['palette']];ck(r['id']+'_no_additional_forge_marker',not any(any(k in name for k in ['furnace','smithing_table','lava']) for name in dnames))
for g in get(P/'protected-inputs.json')['files']:ck('protected_unchanged_'+g['path'],bind(g['path'])==g)
ck('zero_png',not list(P.glob('*.png')))
carry=get(PREV/'carried-forward-pending.json');carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
ck('157_and174_preserved',[(c['batch'],c['id']) for c in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01'),(174,'F01')])
put('carried-forward-pending.json',carry)
put('latest-independent-admissions.json',get(PREV/'latest-independent-admissions.json'))
put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_BOUNDED_NO_CREDIT_SCREEN','checks':checks,'check_count':len(checks),'machine_assertions_not_reference_credit':True,'java_run':False,'native_acceptance':False})
s={'batch':175,'status':'THREE_NAME_NEGATIVE_LOCAL_RELEVANCE_SCREENS_ZERO','complete_whole_reference_studies':0,'raw_original_sources_bounded_screened':3,'generated_png':0,'actual_images_viewed':0,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'COD4_accepted_baseline':153,'COD4_gap':847,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'actual_active_work_hours':None,'next':'176 continue fixed-local genuinely relevant complete designs;157W01 and174F01 remain pending,1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':176})
(P/'HANDOFF.md').write_text('175复用092名字阴性索引，3个新源先有界检查再决定是否全图研究：法师屋顶砧、旧蘑菇居住/织布层砧、奇怪房屋砂轮邻top阶/锅/盆栽均未建立独立锻造工作组织，保守0；不声称不存在任何用途或完整性已经证毕。实际原始局部11层/1497已存索引(1816声明格含319省略)，对应91个不同palette条目按源分别17/23/51全读；只这些层BE与额外功能位原文/selectedpool片段，不是全palette/全BE/实体/全上下文。0PNG、0完整整屋研究、0新提议和正式信用。157/174继续pending。原3spawner/redstone不运行，不Java，不清单删项、不产品写入。\n')
put('RECEIPT.json',{**s,'files':[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'checks':len(checks),'files':len(get(P/'RECEIPT.json')['files'])},ensure_ascii=False))

"""Record actual original-source review; open set-dressing earns no whole-building credit."""
import json, hashlib
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent
PREV=P.parent/'research-20261104-smithy-165'
assert not (P/'RECEIPT.json').exists()
def get(p): return json.loads(p.read_text())
def put(n,v): (P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p); b=p.read_bytes()
 return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
checks=[]
def check(n,v):
 assert v,n
 checks.append({'name':n,'passed':True})
r=get(P/'pre-render-history-screen.json')['rows'][0]
a=get(P/'raw-source-audit.json')['candidates'][0]; d=a['nbt_decoded_original']; pal=d['palette']
check('no exact historical or within-batch alias',r['eligible_for_new_source_study'] and not r['historical_exact_matches'] and not r['within_batch_exact_matches'])
check('fixed archive binding',bind(r['source_archive'])==r['fixed_archive'])
with ZipFile(r['source_archive']) as z:
 check('original member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
check('source stats',d['size']==[11,8,9] and d['DataVersion']==3465 and len(d['blocks'])==792 and a['air']==664 and a['nonair']==128 and len(pal)==31)
check('all positions unique and stored no omissions',len({tuple(x['pos']) for x in d['blocks']})==792)
check('all block entities and no entities',len([x for x in d['blocks'] if 'nbt' in x])==3 and d['entities']==[])
cells={tuple(x['pos']):x for x in d['blocks']}
critical=[([5,1,5],'minecraft:barrel'),([5,1,8],'minecraft:jigsaw'),([9,2,7],'minecraft:campfire'),([9,1,7],'minecraft:hay_block'),([6,1,1],'minecraft:redstone_wire'),([4,1,3],'minecraft:redstone_wire'),([4,7,5],'minecraft:iron_bars'),([8,5,1],'minecraft:iron_bars'),([8,4,4],'minecraft:iron_bars'),([1,0,7],'minecraft:air'),([2,0,7],'minecraft:air'),([2,3,7],'minecraft:oak_slab')]
for pos,name in critical: check('original '+str(pos),pal[cells[tuple(pos)]['state']]['Name']==name)
check('no ordinary doors ladders stairs beds forge or machine',not any(any(k in s['Name'] for k in ['_door','ladder','stairs','_bed','furnace','smoker','anvil','smithing_table','grindstone','water','lava']) for s in pal))
check('all seven diagram files exist',len(list(P.glob('*.png')))==7)
ctx=get(P/'source-context.json'); cs=ctx['candidates'][0]['contexts']
check('three exact JSON and three metadata no missing',len(cs)==3 and len(ctx['metadata'])==3 and not ctx['candidates'][0]['missing'])
location=ctx['candidates'][0]['location']; selected=[e for c in cs if '/template_pool/' in c['member'] for e in c['json']['elements'] if e['element']['location']==location]
check('selected whole-member pool record weight1 rigid legacy',len(selected)==1 and selected[0]['weight']==1 and selected[0]['element']['projection']=='rigid' and selected[0]['element']['element_type']=='minecraft:legacy_single_pool_element')
for f in get(P/'protected-inputs.json')['files']: check('protected unchanged '+f['path'],bind(f['path'])==f)
observations=[
 '完整读取11×8×9全部8层原始索引、31个palette状态、3个BE及空entities；792格全部存储，128非空气664空气，无遗漏格。大小或文件名不证明完整建筑。',
 'y0仅44块黑色陶瓦组成偏东不规则地面；西侧x1..3,z6..8围栏圈下面源格仍为空气，必须依赖外部地形。没有把这片局部地面或围栏计成独立建筑。',
 '北侧x1/4/8,z1骨块柱与x2..3,z1的三层TOP橡木半砖形成架体，x4,z5另有高柱；上方仅零散木半砖、栅栏和铁栏尖端，没有连续遮雨屋顶或可使用上层。灰色分类图中的木半砖不是石屋顶。',
 '西南x1..3,z6..8两层围栏和y3活板门/中央BOTTOM半砖组成小型遮盖围栏装饰，内部下方源格无铺地；没有门、床或楼梯，不能算工住附屋。',
 '东侧9,2,7点燃营火位于9,1,7干草上，signal_fire=true，Items空且四组烹饪时间为0；周围打开金合欢活板门是装饰，不称可运行锻炉、水锤或生产链。',
 '5,1,5朝南储桶只绑定原生战利品表；5,1,8朝南jigsaw final_state=air,pool=minecraft:empty，是单个入口接点而非需拼接楼屋。两个散置红石线power0，不证明实际机械。没有实体、普通门、床、梯、熔炉或铁砧。',
 '所读houses池精确成员weight1/rigid/legacy，处理器把黑陶瓦按水环境或顺序随机规则转木板、各岩石或砂砾，不能把模板44陶瓦当最终44陶瓦地面。储桶表含鞍/金物/皮革/肉等随机奖励，仅为原作者表，不是本项目材料或交易回执。'
]
reading={'source_complete_original_index_planes_read':list(range(8)),'palette_entries_actually_read':31,'block_entities_actually_read':3,'original_entities':[],'actual_PNG_generated_and_viewed':7,'all_8_classified_source_layers_viewed':True,'full_context_JSON_actually_read':3,'metadata_actually_read':3,'old_images_or_written_whole_judgments_reopened':False,'machine_critical_assertions_are_not_reference_credit':True,'native_acceptance':False}
put('actual-reading-boundary.json',reading)
put('manual-review.json',{'batch':166,'cases':[{'id':'F01','source':get(P/'sources.json')['candidates'][0],'observations':observations,'eligibility_decision':'EXCLUDE_OPEN_BUTCHERY_SET_DRESSING_NOT_COMPLETE_RELATED_SHOP_BUILDING','reason':'整体是露天架体、围栏、储桶与营火场景布置；即使作者保存为独立模板且池有完整成员，也不具备本任务完整相关店屋的围合、屋顶或工住动线。并非声称原作者文件损坏。无需以旧风格替换比较强行放行为新建筑。','whole_building_reference_proposal':0,'family_comparison_needed_for_credit':False,'formal_credit_added':0}],'complete_original_source_studies':1,'complete_whole_reference_studies':0,'actual_images_viewed':7,'pending_maximum':0,'native_acceptance':False})
carry=get(PREV/'carried-forward-pending.json')
old=carry['carried_unresolved_whole_reference_proposals']
current=carry['current_batch_pending_cases']
check('previous bounded proposals retained',len(old)==1 and old[0]['batch']==157 and len(current)==1)
carry['carried_unresolved_whole_reference_proposals']=old+current
carry['previous_batch_receipt']=bind(PREV/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
put('carried-forward-pending.json',carry)
put('latest-independent-admissions.json',get(PREV/'latest-independent-admissions.json'))
put('task-scope-boundary.json',get(PREV/'task-scope-boundary.json'))
put('source-context-reading.json',{'actual_read_all_saved_JSON':True,'contexts':[c['member'] for c in cs],'metadata':[c['member'] for c in ctx['metadata']],'selected_member_pool_elements':selected,'no_world_generation_or_compatibility_claim':True})
put('verification.json',{'status':'PASS_STATIC_PROVENANCE_AND_EXCLUSION_ONLY','checks':checks,'checks_passed':len(checks),'not_native_or_semantic_admission':True})
session={'batch':166,'status':'OPEN_BUTCHERY_SET_DRESSING_EXCLUDED_FROM_COMPLETE_RELATED_BUILDINGS','complete_original_source_studies':1,'complete_whole_reference_studies':0,'generated_png':7,'actual_images_viewed':7,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'carried_pending':['157W01_NPC05','165F01_NPC01_relevance_pending'],'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'Continue fixed-local complete related building designs; original set dressing not counted as whole houses;1000 unmet means no production.'}
put('session.json',session);put('active-checkpoint.json',{**session,'verification':bind(P/'verification.json'),'next_batch':167})
(P/'HANDOFF.md').write_text('166原始研究完成但建筑信用0：piglin_butchery_3是露天骨架/围栏/桶/营火布置，不计完整相关工坊。实际7PNG、8原始索引层、31palette、3BE、3JSON+3metadata全读，entities空。固定来源、保护文件核验；保留157W01及165F01待主协调，158首164承接后增量0。无Java、游戏、制作及清单删除。\n')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json']
put('RECEIPT.json',{**session,'checks_passed':len(checks),'files':files})
print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files),'checks':len(checks)},ensure_ascii=False))

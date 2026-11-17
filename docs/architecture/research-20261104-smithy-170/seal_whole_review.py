"""Complete169F01's visual/context study once; independent bounded admission remains pending."""
import json,hashlib
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-169'
assert not (P/'RECEIPT.json').exists()
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
checks=[]
def check(n,v):
 assert v,n
 checks.append({'name':n,'passed':True})
r=get(P/'pre-render-history-screen.json')['rows'][0];a=get(P/'raw-source-audit.json')['candidates'][0];d=a['nbt_decoded_original'];pal=d['palette'];cell={tuple(x['pos']):x for x in d['blocks']}
check('fixed archive unchanged',bind(r['source_archive'])==r['fixed_archive'])
with ZipFile(r['source_archive']) as z:check('original member SHA',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
pre=get(prev/'preassessment-original-sources.json')['rows'][0]
check('exact original169F01 same study not second design',pre['original']==d and pre['member']==r['member'])
check('preassessment had zero whole reference proposal',get(prev/'manual-review.json')['pending_maximum']==0)
check('source stats',d['size']==[11,6,8] and d['DataVersion']==3465 and len(d['blocks'])==279 and len(cell)==279 and a['nonair']==229 and a['air']==50 and len(pal)==21)
check('4BE entities empty',len([x for x in d['blocks'] if 'nbt' in x])==4 and d['entities']==[])
critical=[([2,1,2],'minecraft:smithing_table'),([6,1,3],'minecraft:chest'),([5,1,6],'minecraft:spruce_door'),([5,2,6],'minecraft:spruce_door'),([5,1,4],'minecraft:spruce_door'),([5,2,4],'minecraft:spruce_door'),([5,1,5],'minecraft:air'),([5,2,5],'minecraft:air'),([5,3,5],'minecraft:air'),([5,4,5],'minecraft:stone'),([5,1,3],'minecraft:air'),([5,2,3],'minecraft:air'),([5,3,3],'minecraft:wall_torch'),([5,4,3],'minecraft:air'),([5,5,3],'minecraft:spruce_log'),([8,1,2],'minecraft:stone_brick_stairs'),([8,1,3],'minecraft:stone_brick_stairs'),([1,0,7],'minecraft:jigsaw'),([9,0,7],'minecraft:jigsaw'),([5,1,7],'minecraft:jigsaw')]
for pos,name in critical:check('original '+str(pos),pal[cell[tuple(pos)]['state']]['Name']==name)
check('no heat beds ladder upper use',not any(any(k in x['Name'] for k in ['furnace','campfire','lava','water','_bed','ladder','anvil','grindstone']) for x in pal))
check('six source PNG',len(list(P.glob('*.png')))==6)
ctx=get(P/'source-context.json');c=ctx['candidates'][0];extra=get(P/'additional-context.json')['rows']
check('4 primary JSON 2metadata 6 extra JSON one missing row',len(c['contexts'])==4 and len(ctx['metadata'])==2 and sum('json' in x for x in extra)==6 and len(extra)==7)
selected=[e for q in c['contexts'] if q['member'].endswith('/houses.json') for e in q['json']['elements'] if e.get('element',{}).get('location')==c['location']]
check('precise pool weight3 rigid legacy mossify',len(selected)==1 and selected[0]['weight']==3 and selected[0]['element']['projection']=='rigid' and selected[0]['element']['processors']=='repurposed_structures:villages/mountains/mossify')
oldrows=get(prev/'saved-family-reading.json')['records'];olds=[x for x in oldrows if x['batch'] in [68,90]];check('two complete saved whole comparisons actually read',len(olds)==2 and all(len(x['complete_saved_record_actually_read']['observations'])==7 for x in olds))
put('whole-family-comparison.json',{'complete_saved_records':olds,'169_reading_reused_no_old_images_or_chains_reopened':True,'comparison':'068F02西南双门同一入口臂折向北连续L冷工室，无内隔门；090F01西单门直接进入共同炉箱室。当前南外门—单格门颈—南内门—北横向冷工厅，由中央缓冲再东西共用工/储两端，不是并列双客门或两个独立店。共同厅内仅一smith和箱，绝不以增门/换工位/原木屋盖自动算新；入口缓冲与横厅的整体关系最多1待Main，也可因公共室家族差异不足或纯冷作用途不足判0。','credit_proposal_maximum':1,'formal_credit_added':0,'old_decisions_preserved':True})
obs={
 'layout':'完整单层冷作工具匠屋：南突出单格门颈两道普通门串联进北东西横厅，西smith台、东箱与同高低阶陈设，北厅无隔墙，未虚构两店/住区/热翼。最多1 NPC01相关完整冷作空间待Main整体家族和用途审查。',
 'proportion':'11×6×8/DV3465声明528/存279=229非air50显式air，249省略不当air。floor0/use1，北横厅上y4尚有高空腔但y5双排原木收脊，无上楼板或梯，6高非6层。原6层索引/21palette/4BE/entities[]在169完整读，本批精确等值复用且结合6PNG完成整栋研究，不重复两个批次计建筑。',
 'facade':'stonebricks79/stone17、sprucelog77构体，grayglasspane5和sprucetrapdoor8窗饰。只有南外/内两扇门在5,1/2,z6及z4，原都north/right/closed，朝向属性不写成地理北门。全源没有床或居民实体，decor/cat socket不当已生成角色。',
 'roof':'北长屋东西脊配南门颈短凸盖，原木axisX/Z整块阶状坡面、宽挑檐，不是77层木阶或石瓦。主体x0..10挑盖包屋，原图仅分类全格近似，木门窗/檐口实际碰撞及避雨未验。',
 'materials':'smith2,1,2是真冷作工位，箱6,1,3north原toolsmithloot/seed5437563504828205063；原无炉砧磨、水或熔岩，绝不称完整锻造产线。8,1,z2/3east bottomstonebrickstairs同高靠东陈设，非两级登楼。六walltorch静态照明不当营业AI。',
 'circulation':'5,1/2,6外门→5,1/2,5air→5,1/2,4内门→5,1/2,3air入横厅；门颈y3,z5仍air但4,z5stone盖。门间只有一格源净空，不称已验气闸、双门同时开闭安全或NPC寻路。横厅共享左右工/储端，内外门不分别对应两个商户。入口5,1,7south_up/aligned/empty/finalstructure_void，两个向上decor/cat接点不是缺房翼。',
 'terrain_and_dedup':'四主JSON+六附加JSON及两metadata全文已读：精确house权3legacy/rigid/mossify五规则；decor仅附件，pillar1属于decor并非本屋补柱。root genericjigsaw size6/start0/WORLD_SURFACE_WG/beardthin、radius1、boundinghack与中心normal50/50,zombie1/1保留原语境，中心路径随机/弱金化不挂本屋也不当产矿。biome jaggedpeaks/hills，原版cat/loot/is_hill只在本modJar缺，不推全环境缺失；optional forge/c标签未解析。与完整068L冷室及090直接入单室完整七观察/原比较已读并保留，旧图/源链不重跑；纯加门或换材不保证新家族。'
}
put('manual-review.json',{'cases':[{'id':'F01',**get(P/'sources.json')['candidates'][0],'observations':obs,'credit_proposal_maximum':1,'formal_credit_added':0,'status':'COMPLETE_COLD_WORKSHOP_SERIAL_DOOR_NECK_TO_TRANSVERSE_COMMON_HALL_PENDING_MAIN','native_acceptance':False}],'complete_whole_reference_studies':1,'actual_current_images_viewed':6,'generated_current_png':6,'pending_maximum':1,'formal_credit_added':0})
put('actual-reading-boundary.json',{'current_generated_and_viewed_PNG':6,'classified_source_layers_viewed':6,'complete_original_planes_0_to5_palette21_BE4_entities_empty_actual_read_169_then_reused':bind(prev/'preassessment-original-sources.json'),'precise_same_original_root_verified':True,'primary_context_JSON_actually_read':4,'additional_context_JSON_actually_read':6,'metadata_actually_read':2,'source_omissions_not_air':249,'old_complete_written_comparisons_read_and_reused':[68,90],'all_native_claims':False})
put('source-context-reading.json',{'full_primary_JSON_read':[x['member'] for x in c['contexts']],'full_additional_JSON_read':[x['member'] for x in extra if 'json' in x],'metadata_read':[x['member'] for x in ctx['metadata']],'selected_pool':selected,'missing_only_in_this_modJar':c['missing']+[x['member'] for x in extra if 'json' not in x],'optional_forge_c_hill_tags_not_resolved':True,'not_actual_generation_or_compatibility':True})
carry=get(prev/'carried-forward-pending.json');check('prior pending157 preserved',[(x['batch'],x['id']) for x in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]);carry['previous_batch_receipt']=bind(prev/'RECEIPT.json');carry['current_batch_new_pending']=1;carry['current_batch_pending_cases']=[{'batch':170,'id':'F01','maximum':1,'independent_admission':False,'target':'COD3 NPC01 complete cold workshop serial entry buffer/transverse common hall'}]
put('carried-forward-pending.json',carry);put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
for f in get(P/'protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
put('verification.json',{'status':'PASS_SOURCE_INTEGRITY_ONLY_NOT_MAIN_ADMISSION','checks':checks,'checks_passed':len(checks),'java_run':False,'native_acceptance':False})
s={'batch':170,'status':'COMPLETE_COLD_WORKSHOP_TWO_SERIAL_DOOR_NECK_TRANSVERSE_HALL_PENDING_MAIN','complete_whole_reference_studies':1,'actual_images_viewed':6,'generated_png':6,'pending_maximum':1,'formal_credit_added':0,'prior_admissions_current_increment':0,'same_169F01_preassessment_not_second_reference':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'171 continue truly related fixed-local whole building research;157 and170 bounded pending,1000 unmet no production.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':171})
(P/'HANDOFF.md').write_text('170续169F01完成整屋研究一次：南两串门单格门颈→北横向共同冷作厅，完整原木阶状屋盖，无热翼/卧室/上层。6PNG全看；源6原层/21palette/4BE/空实体沿用169实际全读且根逐值相等；4+6完整JSON/2metadata本批全读。与完整068F02/090F01七观察及原比较比较，max1仅NPC01用途/整家族待Main，门数本身不计信用，Main可判0。157原待核保留；165首167判0全文沿用0。无Java/游戏/生产/清单/共享Jar。\n')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',{**s,'checks_passed':len(checks),'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files),'checks':len(checks)},ensure_ascii=False))

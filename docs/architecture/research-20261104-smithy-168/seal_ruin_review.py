"""Keep full ruin study and zero complete-workshop credit without reconstructing lost architecture."""
import json,hashlib
from pathlib import Path
from zipfile import ZipFile
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-167'
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
check('fixed archive',bind(r['source_archive'])==r['fixed_archive'])
with ZipFile(r['source_archive']) as z:check('source member hash',hashlib.sha256(z.read(r['member'])).hexdigest()==r['nbt_sha256'])
check('no exact source aliases eligible for original review',r['eligible_for_new_source_study'] and not r['historical_exact_matches'] and not r['same_bytes_aliases'])
check('stats',d['size']==[9,8,8] and d['DataVersion']==3120 and len(d['blocks'])==576 and len(cell)==576 and a['nonair']==109 and a['air']==467 and len(pal)==15)
check('3BE entities empty',len([x for x in d['blocks'] if 'nbt' in x])==3 and d['entities']==[])
critical=[([0,0,4],'minecraft:jigsaw'),([6,0,3],'minecraft:chest'),([4,1,6],'minecraft:blast_furnace'),([4,2,6],'minecraft:bricks'),([4,5,6],'minecraft:cobblestone'),([4,6,6],'minecraft:cobblestone'),([4,7,6],'minecraft:mossy_cobblestone_wall'),([4,4,5],'minecraft:mossy_cobblestone_stairs'),([3,2,7],'minecraft:mossy_cobblestone_stairs'),([4,2,7],'minecraft:mossy_cobblestone_stairs'),([5,2,7],'minecraft:mossy_cobblestone_stairs'),([3,1,3],'minecraft:air'),([3,2,3],'minecraft:air'),([3,3,3],'minecraft:air'),([3,4,3],'minecraft:air')]
for pos,name in critical:check('original '+str(pos),pal[cell[tuple(pos)]['state']]['Name']==name)
check('no beds ladders ordinary doors wood roof or forging tables',not any(any(w in s['Name'] for w in ['_bed','ladder','_door','_planks','_log','smithing_table','anvil','grindstone']) for s in pal))
check('7 generated diagrams',len(list(P.glob('*.png')))==7)
ctx=get(P/'source-context.json');c=ctx['candidates'][0];selected=[e for e in c['contexts'][0]['json']['elements'] if e.get('element',{}).get('location')==c['location']]
check('one saved pool exact weight1 rigid legacy',len(c['contexts'])==1 and len(selected)==1 and selected[0]['weight']==1 and selected[0]['element']['projection']=='rigid' and selected[0]['element']['element_type']=='minecraft:legacy_single_pool_element')
check('two vanilla contexts missing only in mod jar',set(c['missing'])=={'data/minecraft/loot_tables/chests/village/village_armorer.json','data/minecraft/worldgen/processor_list/mossify_70_percent.json'})
metap=R/'docs/architecture/research-20261104-smithy-166/source-context.json'
check('exact saved metadata reused from actual166 reading',ctx['metadata']==get(metap)['metadata'])
oldp=R/'docs/architecture/research-20261104-smithy-057/manual-review.json';old=get(oldp)
check('old classic complete seven fields retained',len(old['reviews'][0]['observations'])==7)
put('whole-family-comparison.json',{'old_manual_binding':bind(oldp),'old_complete_record_actually_read':old['reviews'][0],'old_entire_original_semantic_comparison_actually_read':old['semantic_dedup_comparison'],'other_old057F02F03_written_records_also_read_no_new_credit':old['reviews'][1:],'old_images_and_source_chains_not_reopened':True,'current_comparison':'旧057经典整体为低平统一石盖/开放热棚/木围储物后室，并有熔岩双炉；当前原稿仅低石围/西缺口/南北朝高炉及烟道残柱/地层箱，无连续屋盖和后室。此差异主要是遗址残存，不把破损或苔化当独立完整铁匠工住组织；未证明是经典源的精确变体，也不自行复原丢失屋形。','credit_proposal_maximum':0})
obs={
 'layout':'9×8×8原完整保存遗址模板，石底/低围界单一开敞残室，西入口缺口通低工作坪，南高炉和烟道残柱，东北较低箱。是整份遗址设计，非字节损坏，但不足一栋可研究完整工住组织的相近铁匠屋；不补画原屋。',
 'proportion':'DV3120，576位置全部存储=109非air+467air，无遗漏格。最高y7仅4,7,6苔石墙烟道帽，其下y5/6各只同位一块石；8格高不是8层，也不是可经营塔楼。',
 'facade':'cobblestone83/grass8/bricks2/smoothstone5及苔阶7/苔墙1，残墙在北z1及东x7保存较高，西墙多破口。图中绿块含草和苔阶，不是新屋顶；无门/窗/木构。',
 'roof':'y3/4仅散残墙和南侧烟道邻阶，内部上方均显式air，无连续屋盖/上层承台，无床和梯；不把南z7三阶装饰解释成通二楼楼梯。',
 'materials':'高炉4,1,6north/litfalse且Items空、Cook/Burn/Total0/RecipesUsed{}；上4,2,6brick、石烟道至y6与y7帽，不存在营火/熔岩或实际排烟回执。箱6,0,3west低于主要工作站位，原armorer loot及负seed保存，不写成已获取奖励。',
 'circulation':'0,0,4west_up入口jigsaw的pool空但final_state为east向BOTTOM苔石阶，不是air；相邻0,0,3已是east苔阶，可读西侧地面入口意图。室内3,1/2/3/4,3空气仅源状态，不保证最终jigsaw替换、角色落脚或地形承托。无必需续接房翼，不把empty接头算缺屋。',
 'terrain_and_relevance':'已读forest_ruins houses完整31项池，精确armorer weight1 rigid legacy、mossify_70_percent；所读modJar缺两原版loot/processor不等整个环境缺失或生成失败，未另开原版Jar补推结果。它能示范烟道/工位遗址识别，不能凭高炉和armorer名计相近完整铁匠建筑，也不能混成NPC05磨坊参考。'
}
put('manual-review.json',{'batch':168,'cases':[{'id':'F01','observations':obs,'status':'STUDIED_COMPLETE_SAVED_RUIN_NOT_CREDITED_AS_COMPLETE_RELATED_WORKSHOP','credit_proposal_maximum':0,'formal_credit_added':0,'native_acceptance':False}],'complete_original_source_studies':1,'complete_whole_reference_studies':0,'actual_images_viewed':7,'pending_maximum':0,'formal_credit_added':0})
put('actual-reading-boundary.json',{'current_PNG_generated_and_viewed':7,'all_source_classified_layers_viewed':8,'complete_original_index_planes_actually_read':list(range(8)),'palette_entries_actually_read':15,'block_entities_actually_read':3,'entities':[],'complete_saved_current_JSON_read':1,'metadata_exact_reuse_binding':bind(metap),'metadata_reread_not_claimed':True,'old057_complete_written_records_read':3,'old057_original_comparison_read':True,'old_images_source_chains_not_reopened':True,'native_acceptance':False})
put('source-context-reading.json',{'complete_JSON_read':[q['member'] for q in c['contexts']],'metadata_exact_reuse':bind(metap),'selected_pool_entry':selected,'missing_in_modJar_not_whole_environment':c['missing'],'no_runtime_or_generation_claim':True})
carry=get(prev/'carried-forward-pending.json');check('only157 pending preserved',[(v['batch'],v['id']) for v in carry['carried_unresolved_whole_reference_proposals']]==[(157,'W01')]);carry['previous_batch_receipt']=bind(prev/'RECEIPT.json');carry['current_batch_new_pending']=0;carry['current_batch_pending_cases']=[]
put('carried-forward-pending.json',carry);put('latest-independent-admissions.json',get(prev/'latest-independent-admissions.json'));put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
for f in get(P/'protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
put('verification.json',{'status':'PASS_SOURCE_INTEGRITY_STATIC_REVIEW_AND_ZERO_PROPOSAL','checks':checks,'checks_passed':len(checks),'semantic_admission_not_claimed':True,'java_run':False})
s={'batch':168,'status':'FOREST_ARMORER_RUIN_ORIGINAL_STUDIED_COMPLETE_WORKSHOP_CREDIT_ZERO','complete_original_source_studies':1,'complete_whole_reference_studies':0,'generated_png':7,'actual_images_viewed':7,'pending_maximum':0,'formal_credit_added':0,'prior_admissions_current_increment':0,'165_first167_zero_decision_carried_exactly_later0':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'169 continue fixed-local genuinely complete related workshops; preserve157 pending; no production before1000.'}
put('session.json',s);put('active-checkpoint.json',{**s,'verification':bind(P/'verification.json'),'next_batch':169})
(P/'HANDOFF.md').write_text('168原始遗址研究已做，信用保守0：forest_armorer_1低残室/北朝高炉/烟道残柱/低箱，缺完整屋盖和工住空间组织，不补造原屋，也未证明与旧经典铁匠源精确同族。实际7PNG、8原索引层、15palette、3BE/空entities、1完整31项池已读；metadata精确复用166实际阅读。原版loot与mossify处理器仅在所读modJar中缺失，不推全环境缺失。057三旧完整七观察和原比较已读但旧图源未重跑。165首167判0整对象沿用0，157待审，三范围0，无Java或生产/清单操作。\n')
files=[bind(p) for p in sorted(P.iterdir()) if p.is_file() and p.name!='RECEIPT.json'];put('RECEIPT.json',{**s,'checks_passed':len(checks),'files':files});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files),'checks':len(checks)},ensure_ascii=False))

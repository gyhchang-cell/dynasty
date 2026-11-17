"""Seal one joint-derived whole mill study; retain limits and all original source evidence."""
import json,hashlib,sys,math
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
from PIL import Image
P=Path(__file__).resolve().parent;R=P.parents[2];prev=P.parent/'research-20261104-smithy-156';assert not(P/'RECEIPT.json').exists();sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def get(p):return json.loads(p.read_text())
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=Path(p).read_bytes();return {'path':str(Path(p).resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
screen=get(P/'pre-render-history-screen.json');top=get(P/'source-topology.json');original=get(P/'original-two-part-source.json');mp={};sources=[]
for i,(s,part,t) in enumerate(zip(screen['rows'],original['parts'],top['parts'])):
 check('source eligible '+str(i),s['eligible_for_new_source_study']and not s['known_history']and not s['historical_exact_matches']and not s['within_batch_exact_matches']);check('archive binding '+str(i),bind(s['source_archive'])==s['fixed_archive'])
 with ZipFile(s['source_archive'])as z:
  b=z.read(s['member']);d=read(b);check('original source bytes and full decoded equality '+str(i),hashlib.sha256(b).hexdigest()==s['nbt_sha256']==t['nbt_sha256']and d==part['nbt_decoded_original']);pal=d['palette'];c=Counter(pal[b['state']]['Name']for b in d['blocks']);check('material inventory '+str(i),dict(c)==t['material_counts']);check('bounds and unique positions '+str(i),len({tuple(b['pos'])for b in d['blocks']})==len(d['blocks'])and all(all(0<=b['pos'][k]<d['size'][k]for k in range(3))for b in d['blocks']));check('stats '+str(i),[d['DataVersion'],d['size'],len(d['blocks']),sum(c[n]for n in AIR),len(pal),len(d['entities'])]==[3120,[48,32,34],t['stored'],t['air'],t['palette_count'],0]);check('omitted not air '+str(i),t['omitted']==math.prod(d['size'])-len(d['blocks']))
  if i==0:
   for cc in top['contexts']:check('original context '+cc['member'],hashlib.sha256(z.read(cc['member'])).hexdigest()==cc['sha256']and json.loads(z.read(cc['member']))==cc['json'])
  for b in d['blocks']:
   x,y,zz=b['pos'];pos=(x,y+32*i,zz);check('disjoint source part boundary '+str(i),pos not in mp) if pos in mp else None;mp[pos]=pal[b['state']]
 sources.append({'id':s['id'],'source_archive':s['source_archive'],'source_archive_sha256':s['fixed_archive']['sha256'],'member':s['member'],'nbt_sha256':s['nbt_sha256'],'size':[48,32,34],'DataVersion':3120,'purpose':'COD3 NPC05 废村磨坊 whole study fragment only; not separate building','whole_building_id':'W01','formal_credit_added':0})
check('total composite declaration/stored/nonair/air/omitted',[104448,len(mp),sum(p['nonair']for p in top['parts']),sum(p['air']for p in top['parts']),sum(p['omitted']for p in top['parts'])]==[104448,20437,10362,10075,84011])
lo,hi=[p['main_connector']for p in top['parts']];check('exact opposed aligned source connector',lo['pos']==[0,31,33]and hi['pos']==[0,0,33]and lo['state']['Properties']['orientation']=='up_south'and hi['state']['Properties']['orientation']=='down_south'and lo['nbt']['joint']==hi['nbt']['joint']=='aligned'and lo['nbt']['target']==hi['nbt']['name']and hi['nbt']['target']==lo['nbt']['name']);check('only research translation without production',top['derived_upper_translation']==[0,32,0]and top['assembly_not_executed_in_game'])
for x in get(P/'queried-original-states.json')['expected_states']:check('critical original state '+str(x['pos']),mp.get(tuple(x['pos']))==x['state'])
for cc in get(prev/'protected-inputs.json')['files']:
 if '/code x提示词/'in cc['path']:check('external prompt unchanged '+cc['path'],bind(cc['path'])==cc)
images=[bind(P/f'assembly-{n}.png')for n in ['whole','cutaway','vertical']+[f'y{y:02}'for y in range(0,64,4)]]
check('nineteen current views actually inspected',len(images)==len(list(P.glob('*.png')))==19)
for im in images:
 with Image.open(im['path'])as pic:pic.verify()
 check('valid viewed PNG '+Path(im['path']).name,True)
obs={
'layout':'一座上下两源片段合成的高磨坊塔，而非两栋或两个可替代设计。下为宽石质底室及东西对向外升阶，y9作业环面以上为狭高石木轴井；西内长梯穿过源分界上至高处储物环室，南北/四角撑木、上放大高帽与北立面四叶斜置风轮属同栋。两主接头target/name互配、up_south/down_south且aligned，原identity旋转上段抬32，原始SAVE标记也存48×32×34；不凭文件名随意拼接。完整主体空间研究1，向NPC05用途相关提案最多1，Main可依规模/语义判0。',
'proportion':'每段48×32×34/DV3120，合研究盒48×64×34；原part0 11955存=6185非air5770air/40269省略/177pal/110BE，part1 8482存=4177非air4305air/43742省略/96pal/24BE。合20437存=10362非air10075显式air，84011省略不可补air。两entities[]；全部273原palette条及134BE按完整相同NBT/状态分组连坐标实际读，19PNG含全部64层分类剖平面实际看；没有声称全20437格逐一语义或64整幅原索引逐格读过。最大64高包括轮梢而非64层。',
'facade':'andesite2828/cobble1021/polishedandesite374构高收分石壳/基座，darkoakwood640和strippeddarkoaklog253等作竖框/跨梁。两侧宽石台阶向同一环状下作业面收拢，高部木室向外放大，连续竖向石条/木柱强调塔体。无普通door/fencegate/床；原ominous banners5、空实体、spawner接头不等村民/阿吉，Termination英文牌不当中文任务或已触发机关。',
'roof':'上层acaciawood429配crimsonplanks701、oakplanks134等构大挑帽/层层收尖木盖，非分类图全棕色spruce或纯石顶；实体封盖中心y51为crimsonplanks，y52边框、y53零散高边，不当额外楼面。北外轮跨至y63，轴/轮含andesite、石墙、木骨和深色陈设，不是156白羊毛十字轮，也未观察到风轮旋转。高帽、外轮四片与脚柱不拆建筑，不复制产品资产。',
'materials_and_function':'主体除41hay和13barrels/3chests，还原有TNT63、note_block11、piston5/stickypiston2、redstoneblock2、comparator3、hopper22/dispenser3/dropper1等机械/陷阱式陈设。下22,1,9 disabled/east漏斗实际1diamond Slot1，22,1,8比较器poweredtrue/OutputSignal1；其余大多空库存、poweredfalse状态。四damagedanvil、满watercauldron4(level3)/空cauldron5不证明可研磨或安全锻造；无furnace/grindstone/stonecutter。三箱原windmill_treasure、11桶windmill_barrels loot，另外2桶Items[]；无LootTableSeed，不编。两loot JSON此前选择输出曾截断，本批未全文实际读，不将原随机候选当已获取奖励。所有都未运行，不触发游戏或声音。',
'circulation':'东西外阶在z17/18可读主线：西5,3→6,4→7,5→8,6→9,7→10,8→11,9 BOTTOM/east（东43→42→41→40→39→38→37对称west），部分相邻z宽随阶变化，转角11/37,z16/20不同facing/outer形态不冒全齐平宽梯。内唯一长梯x19,z18 east/dry y1..34连续34状态，跨y31/32源缝不中断；floor9邻20,9,18cobble、20,10,18air，下梯起于floor0/use1。梯背x18,y11..16/19..21/25..27是原DATA structureblocks，原生处理后能否支梯未验，不能称承托实木墙。梯顶y35、近19,35,z17/18/19及20,35,18全air，不把顶端直通y35环板作为已证净空落脚；34梁和环室的具体转接仍需原生复核。中段y18/y27木框/轴饰不是满铺中楼层，无中途独立房。',
'context_terrain_and_dedup':'root jigsaw size7/max114/start-2/WORLD_SURFACE_WG/expansionfalse/adapt_noisefalse，无擅补terrain_adaptation。start仅part0权1，main列part0/part1各1/single/rigid/empty，但name/target筛选表明两主端上下拼同栋，不当随机两座整磨坊。fields五terrain_matching权1/1/5/3/4只是周边田组件未实际研究NBT；spawners权20/1/1为pillager/vindicator/witch小件未读其NBT，不作三栋或实际生成32敌。两个池文件内name均原main，保留原文不修源。69jigsaw=两主拼口+周边田/角色，空structureblocks13为原作者TheCatsKing标记，后处理未执行。对012F04围院小塔/分段短梯与156低储平台/短梯高空壳，当前下宽双侧外阶环面—狭高轴井长梯—高处放大储物环室/大挑帽的整体分层不同；对源片段、轮片、田、机制不拆计。用途以磨坊空间/高低储料作业为相关，不认它已是废村避难NPC场景或1000达标。'
}
comparison=[]
for directory,ident,key in [('research-20261101-dungeons-012','F04','entries'),('research-20261104-smithy-156','F01','cases')]:
 f=P.parent/directory/'manual-review.json';v=next(c for c in get(f)[key]if c['id']==ident);comparison.append({'binding':bind(f),'case':ident,'complete_saved_observations_actually_read':v.get('observations',v.get('screening_observations')),'old_images_revisited_in_this_batch':False,'prior_status_preserved':v['status']})
put('sources.json',{'candidates':sources,'parts_are_not_building_counts':True})
put('manual-review.json',{'scope':'COD3 NPC05 阿吉 废村磨坊用途相关完整建筑空间研究','whole_case':'W01','source_parts':[s['id']for s in sources],'observations':obs,'complete_whole_reference_studies':1,'actual_current_images_viewed':19,'original_palette_entries_actually_read':273,'original_BE_actually_read_grouped_losslessly':134,'original_entities':[],'all64_class_color_layer_projections_actually_viewed':True,'all64_original_index_grids_read':False,'critical_original_states_actually_read':271,'written_comparisons':comparison,'images_actually_viewed':images,'credit_proposal_maximum':1,'formal_credit_added':0,'native_acceptance':False,'status':'JOINT_DERIVED_ONE_WHOLE_MILL_REFERENCE_PROPOSAL_PENDING_MAIN','limits':['Derived original joint assembly is research, no native structure generation/collision/processor verification.','64 class projections plus complete palettes/BE and critical states are reading boundary; not every original index cell read individually.','134 BE include originals grouped by identical full NBT/state plus exact positions, not omitted duplicate rows.','Large illager industrial/trap building is only spatial relatedness, not current civilian gameplay or copied assets.','No current original image/material texture acceptance; all diagrams generic fullcell colors.']})
carry=get(prev/'carried-forward-pending.json');carry['previous_batch_receipt']=bind(prev/'RECEIPT.json');carry['carried_unresolved_whole_reference_proposals']=carry.get('carried_unresolved_whole_reference_proposals',[])+carry['current_batch_pending_cases'];carry['current_batch_pending_cases']=[{'batch':157,'id':'W01','maximum':1,'independent_admission':False,'target':'COD3 NPC05 阿吉 废村磨坊','source_fragments_not_separate_references':True}];carry['current_batch_new_pending']=1
check('153 accepted first156 exact carry0',carry['153F01_resolved_accept1_first156']==get(prev/'first-carry-153-independent-admission.json'));put('carried-forward-pending.json',carry)
a=get(prev/'latest-independent-admissions.json');a['previous_binding']=bind(prev/'latest-independent-admissions.json');a['153F01_first_bound156_carry_only_no_current_increment_157']=True;put('latest-independent-admissions.json',a);put('task-scope-boundary.json',get(prev/'task-scope-boundary.json'))
put('verification.json',{'status':'PASS_ORIGINAL_INTEGRITY_AND_RECORDED_READING_BOUNDARIES_NOT_MAIN_ADMISSION','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'masterlists_edited':False})
session={'batch':157,'status':'ONE_JOINT_DERIVED_COMPLETE_MILL_STUDY_PENDING_MAIN','complete_whole_reference_studies':1,'source_parts':2,'actual_images_viewed':19,'generated_png':19,'unviewed_png':0,'credit_proposal_maximum':1,'formal_credit_added':0,'newly_carried_admission':0,'NPC01_153_first156_carry_only':True,'COD4_accepted':153,'COD4_gap':847,'java_run':False,'game_started':False,'product_files_written':False,'masterlists_edited':False,'all_tasks_complete':False,'next':'Main独立判定156F01/157W01仅NPC05；继续原固定本地建筑语义研究，1000未满不制作，NPC01/COD4不混数。'}
put('session.json',session);put('active-checkpoint.json',{**session,'verification':bind(P/'verification.json'),'next_batch':158});(P/'HANDOFF.md').write_text('157：同一DAillager windmill两上下源经原主接头/池推identity+32合整屋，一栋研究最多1待Main，只NPC05。19投影全看含64层，273palette/134BE按原相同状态NBT分组及精确坐标读、271关键状态读；不是64完整原索引逐格读。外双侧升阶下环作业面、34连续梯跨源缝/高窄轴井、上放大储物环室和大木帽/北斜四叶轮。梯背原DATA结构块/顶部落脚未实机，原TNT/音符/机关不复制不运行。153已first156接受，仅carry0；唯一旧pending156 NPC05+当前157W01，COD4不变153/gap847。未生产/实机/删清单。\n')
files=[bind(p)for p in sorted(P.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{**session,'files':files,'checks_passed':len(checks)});print(json.dumps({'receipt':bind(P/'RECEIPT.json'),'files':len(files),'checks':len(checks)},ensure_ascii=False))

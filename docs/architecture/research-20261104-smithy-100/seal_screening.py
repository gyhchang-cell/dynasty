"""Seal current preliminary boundary exclusions; no product/game or historical acceptance writes."""
import json,hashlib,math,sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR
def get(n):return json.loads((OUT/n).read_text())
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def restore(v):
 if isinstance(v,dict):
  if set(v)=={'__original_nbt_byte_array_hex__'}:return bytes.fromhex(v['__original_nbt_byte_array_hex__'])
  return {k:restore(w)for k,w in v.items()}
 if isinstance(v,list):return [restore(w)for w in v]
 return v
checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
reasons=[{
 'purpose':'林地村民前哨中心：中央多层宿住/共用楼，外围不同职业摊棚/岗位。低东侧blast/grind/anvil/smith并不把整个村庄中心变成单栋铁匠工坊。',
 'whole_boundary':'只初筛整体/低层用途与计数边界。未逐间/逐层证明完整独立相关工坊，不按13床对/19jigsaw/岗位或摊棚数拆成多个参考；整中心也不直接提出1个相关通过。',
 'evidence':'25×15×21/DV3120；7875全格=1733非air6142显式air，无省略/原实体。smith23,1,10/anvil23,1,9/grind20,1,3floor north/blast22,1,2south empty unlit；smoker21,1,17north empty unlit。原26床state共13对分y1/6/12，occupied=true只是原state不是已有人住。165palette全保存，未逐状态人工解读或验多层步行。'
},{
 'purpose':'向日葵农场中心：分置的大木棚/住棚及热作业院场，包含牲畜/村民/风车/街道接口，非单栋铁匠铺。北侧smith/grind/blast/lava不使整农场各房间自动适用。',
 'whole_boundary':'只初筛整源及低层工作岗位。没有分别研究每座独立棚屋完整边界、上下路线与语义家族，整源/床数/盔甲架/接头均不算多个完整相关建筑，当前0。',
 'evidence':'18×10×25/DV3120；4500全格=1458非air3042显式air，无省略。smith10,1,8/grind12,1,6floor north/blast15,1,8west empty unlit；lava14,1,4level0和watercauldron12,1,10level2不同。3棕床对y5，真门4,1/2,16north open；5原实体=1itemframe+4armorstand，不当5人形/5NPC或新模型。145palette保存未逐状态解读。'
}]
raw=get('raw-source-audit.json')['candidates'];ctx=get('source-context.json');screen=get('pre-render-history-screen.json');cases=[];functional=[];context_notes=[]
for a,r,why in zip(get('sources.json')['candidates'],raw,reasons):
 ident=a['id'];sr=next(x for x in screen['rows']if x['id']==ident)
 check(ident+' pre-render member/alias/raw/role/occupancy passed',sr['eligible_for_new_source_study']and not any(sr[k]for k in ['known_history','historical_exact_matches','within_batch_exact_matches','same_bytes_aliases']))
 check(ident+' fixed archive unchanged',bind(a['source_archive'])==sr['fixed_archive'])
 with ZipFile(a['source_archive'])as z:
  b=z.read(a['member']);d=read(b);pal=d['palette'];counts=Counter(pal[x['state']]['Name']for x in d['blocks']);mp={tuple(x['pos']):pal[x['state']]for x in d['blocks']}
  check(ident+' original NBT lossless bind',hashlib.sha256(b).hexdigest()==a['nbt_sha256']==r['nbt_sha256']and d==restore(r['nbt_decoded_original']))
  check(ident+' unique all positions and state bounds',len(mp)==len(d['blocks'])==math.prod(d['size'])and all(0<=x['state']<len(pal)and all(0<=x['pos'][i]<d['size'][i]for i in range(3))for x in d['blocks']))
  check(ident+' full material and explicit air counts',dict(counts)==r['material_counts']and sum(counts[n]for n in AIR)==r['air']and len(d['blocks'])-r['air']==r['nonair'])
  f={'id':ident,'declared_volume':math.prod(d['size']),'stored_records':len(d['blocks']),'explicit_air':r['air'],'nonair':r['nonair'],'omitted_positions':math.prod(d['size'])-len(d['blocks']),'entities_original':d['entities'],'functional_states':[{'pos':x['pos'],'state':pal[x['state']],'original_block_entity':x.get('nbt')}for x in d['blocks']if x.get('nbt')or any(t in pal[x['state']]['Name']for t in ['door','furnace','smoker','smithing','grindstone','bed','lava','water','stairs','ladder','anvil','loom','cartography','crafting','stonecutter','cauldron'])]};functional.append(f)
  for m in [m for m in ctx['metadata']if m['id']==ident]:check(ident+' metadata '+m['member'],hashlib.sha256(z.read(m['member'])).hexdigest()==m['sha256']and z.read(m['member']).decode()==m['original_text'])
  c=next(c for c in ctx['candidates']if c['id']==ident)
  for cc in c['contexts']:check(ident+' context '+cc['member'],hashlib.sha256(z.read(cc['member'])).hexdigest()==cc['sha256']and json.loads(z.read(cc['member']))==cc['json'])
  for missing in c['missing']:check(ident+' missing only single Jar '+missing,missing not in z.namelist())
  root=next(x['json']for x in c['contexts']if '/worldgen/structure/'in x['member']);pool=next(x['json']for x in c['contexts']if x['member'].endswith('/town_centers.json'))
  check(ident+' root original start0/beardthin/expansiontrue',root['start_height']=={'absolute':0}and root['project_start_to_heightmap']=='WORLD_SURFACE_WG'and root['terrain_adaptation']=='beard_thin'and root['use_expansion_hack']is True and root['spawn_overrides']=={})
  check(ident+' one legacy rigid emptyprocessor source not assembled whole village',len(pool['elements'])==1 and pool['elements'][0]=={'weight':1,'element':{'element_type':'minecraft:legacy_single_pool_element','projection':'rigid','location':c['location'],'processors':'minecraft:empty'}}and pool['fallback']=='minecraft:empty')
  check(ident+' all source work furnaces empty unlit zero cook',all(x['nbt']['Items']==[]and x['nbt']['BurnTime']==x['nbt']['CookTime']==0 and pal[x['state']]['Properties']['lit']=='false'for x in d['blocks']if pal[x['state']]['Name']in ['minecraft:blast_furnace','minecraft:smoker']))
  check(ident+' exactly1blast1grind1smith no ladder',counts['minecraft:blast_furnace']==counts['minecraft:grindstone']==counts['minecraft:smithing_table']==1 and counts['minecraft:ladder']==0)
  if ident=='F01':
   check('F01 exact dimensions/counts/palette and13paired beds',d['size']==[25,15,21]and r['nonair']==1733 and r['air']==6142 and len(pal)==165 and sum(v for n,v in counts.items()if n.endswith('_bed'))==26 and len([x for x in d['blocks']if pal[x['state']]['Name'].endswith('_bed')and pal[x['state']]['Properties']['part']=='head'])==13)
   check('F01 original occupied beds not actual entities',not d['entities']and all(pal[x['state']]['Properties']['occupied']=='true'for x in d['blocks']if pal[x['state']]['Name'].endswith('_bed')))
   check('F01 root7max80/19jigsaw different from assembled amount',root['size']==7 and root['max_distance_from_center']==80 and counts['minecraft:jigsaw']==19)
   check('F01 original workstation states',mp[23,1,10]['Name']=='minecraft:smithing_table'and mp[23,1,9]['Name']=='minecraft:chipped_anvil'and mp[20,1,3]['Properties']=={'facing':'north','face':'floor'}and mp[22,1,2]['Name']=='minecraft:blast_furnace')
  else:
   check('F02 exact dimensions/counts/palette/3bedpairs',d['size']==[18,10,25]and r['nonair']==1458 and r['air']==3042 and len(pal)==145 and counts['minecraft:brown_bed']==6 and all(mp[10,5,zz]['Properties']['part']=='foot'and mp[11,5,zz]['Properties']['part']=='head'for zz in [17,19,21]))
   check('F02 original4armorstands+frame not actual workers',Counter(e['nbt']['id']for e in d['entities'])==Counter({'minecraft:armor_stand':4,'minecraft:item_frame':1}))
   check('F02 root5max116/18jigsaw not5or18buildings',root['size']==5 and root['max_distance_from_center']==116 and counts['minecraft:jigsaw']==18)
   check('F02 lava separate watercauldron2',counts['minecraft:lava']==1 and mp[14,1,4]=={'Name':'minecraft:lava','Properties':{'level':'0'}}and mp[12,1,10]=={'Name':'minecraft:water_cauldron','Properties':{'level':'2'}})
  images=[bind(OUT/(ident+'-'+n+'.png'))for n in ['whole','cutaway','y0','y2']]
  for im in images:
   with Image.open(im['path'])as image:image.verify()
   check(ident+' actual viewed image valid '+Path(im['path']).name,bind(im['path'])==im)
  cases.append({**a,'screening_observations':why,'images_actually_viewed':images,'actual_full_reference_study_complete':False,'credit_proposal_maximum':0,'formal_credit_added':0,'status':'SCREENED_OUT_ZERO_PENDING_MULTIFUNCTION_SETTLEMENT_CENTER_NOT_SINGLE_WORKSHOP','native_acceptance':False})
  context_notes.append({'id':ident,'root_original':root,'selected_pool_original':pool,'original_jigsaw_sockets':[{'pos':x['pos'],'state':pal[x['state']],'original_block_entity':x['nbt']}for x in d['blocks']if pal[x['state']]['Name']=='minecraft:jigsaw'],'missing_only_in_single_fixed_archive':c['missing'],'world_assembly_spawn_loot_execution':False})
put('functional-evidence.json',{'candidates':functional,'original_states_preserved':True,'native_function_not_verified':True})
put('manual-review.json',{'scope':'Preliminary whole-boundary/relevance exclusions, not full complete related-building studies.','cases':cases,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_current_png':19,'actual_current_images_viewed':8,'unviewed_png':11,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'no_independent_self_admission':True})
viewed=[x for c in cases for x in c['images_actually_viewed']];paths={x['path']for x in viewed};unviewed=[bind(p)for p in sorted(OUT.glob('*.png'))if str(p)not in paths]
put('visual-reading-boundary.json',{'viewed':viewed,'not_viewed_generated':unviewed,'unviewed_not_references_or_observations':True,'no_claim_all_layers_or_navigation_reviewed':True,'generic_class_full_cell_diagrams_not_actual_textures_collision_or_entities':True})
put('source-context-reading.json',{'cases':context_notes,'metadata':'Towns and Towers Jar1.12/Forge原version ${file.jarVersion}/Fabric1.12/pack18；Kubek,Biban_Auriu,Cristelknight等原作者/CCBYNCSA4。Forge43+/MC1.19.3+/Cristellib1+与Fabric依赖原保存，不推当前兼容。NBT与pool为kaisyn，root/tag是towns_and_towers，不改namespace。','additional_pools':'实际保存waystone/decor/windmill/street引用；只阅元素数量和fallback，未研究其NB T/实际装配，不作额外完整建筑。','reading_limits':'只实际看8PNG，各whole/cutaway/y0/y2；11其余图未看。关键功能/原实体/床/门/jigsaw及root/pool/tag/meta实际查看；未称全层165/145palette逐项人工或完整家族/导航审，原loot未逐表执行/发奖。所有原NBT/BE/entities/hashcontext完整保留核对。','missing_scope':'vanilla村民/猫/铁傀儡/animal pools和各vanilla loot单Jar缺，不当环境缺或擅补。jigsaw不是已生NPC，source occupiedbed不是人在，盔甲架不当模型/人物。','admission':'097F01 Main已接受1，此100首次承接一次；095F02已097承接，本批只carry不重计。098F01最多1仍待Main独立审；旧pending不取消。COD4仍153 gap847。'})
prev=ROOT/'docs/architecture/research-20261104-smithy-099';put('task-scope-boundary.json',json.loads((prev/'task-scope-boundary.json').read_text()))
adm=get('latest-independent-admissions.json')['newly_notified_admission_097_F01'];put('carried-forward-admission-resolution.json',{'prior_pending_binding':bind(prev/'carried-forward-pending.json'),'resolved_once':{'batch':97,'id':'F01','accepted_increment':1,'first_bound_batch':100,'receipt':adm['receipt']},'095F02_already_resolved_097_no_new_increment':True,'old_sealed_files_not_edited':True,'COD4_increment':0,'not_total_cumulative':True})
p98=ROOT/'docs/architecture/research-20261104-smithy-098';put('carried-forward-pending.json',{'previous_batch_receipt':bind(prev/'RECEIPT.json'),'current_batch_new_pending':0,'prior_pending':[{'batch':98,'id':'F01','maximum':1,'manual':bind(p98/'manual-review.json'),'receipt':bind(p98/'RECEIPT.json')}],'097F01_resolved_once_100':True,'095F02_already_resolved_097_not_new_admission':True,'older_pending_not_cancelled':True,'not_master_todo_backup':True})
check('341 historical pairs not semantic credit',screen['history_unique_archive_member_pairs']==341);check('prior097prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
bindings(get('latest-independent-admissions.json'));bindings(get('carried-forward-admission-resolution.json'));bindings(get('carried-forward-pending.json'))
check('097F01 unique current first binding accepted1',adm['first_bound_batch']==100 and adm['increment']==1 and adm['receipt']['sha256']=='ec0115ecb09a420c46a60d3c5448d983d73b6bbe427afee81c5bb2acff7c7c97')
check('19generated8viewed11unviewed',len(list(OUT.glob('*.png')))==19 and len(viewed)==8 and len(unviewed)==11)
check('current0fullstudies0pending0credit',get('manual-review.json')['complete_whole_reference_studies']==get('manual-review.json')['pending_maximum']==get('manual-review.json')['formal_credit_added']==0)
put('verification.json',{'status':'PASS_CURRENT_PRELIMINARY_SCREENING_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'all_tasks_complete':False})
status='SEALED_TWO_SETTLEMENT_CENTER_BOUNDARY_EXCLUSIONS_ZERO_COMPLETE_STUDIES'
put('session.json',{'batch':100,'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_png':19,'actual_images_viewed':8,'unviewed_generated':11,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'new_prior097_F01_admission_first_bound_increment':1,'095F02_carry_only_increment':0,'prior098_F01_max1_pending_preserved':True,'latest_independent_admission_binding':bind(OUT/'latest-independent-admissions.json'),'cumulative_not_reset':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'101继续其他固定本地完整相关功能建筑；不重研本批村中心/原已验，不提前制作或删任务。'})
put('active-checkpoint.json',{'batch':100,'status':status,'actual_images_viewed':8,'complete_whole_reference_studies':0,'formal_credit_added':0,'java_run':False,'all_tasks_complete':False,'verification':bind(OUT/'verification.json'),'next_batch':101})
(OUT/'HANDOFF.md').write_text('100为两个村庄中心的初步用途/计数边界排除，生成19PNG只实际查看8（各whole/cutaway/y0/y2），11未看逐个绑定；0完整相关研究/0newpending/formal0。F01grove前哨中心25×15×21/DV3120，7875全格=1733非air6142air，13床对与外围多岗位/19jigsaw不是13/19个完整相关建筑，4个锻造marker不把整体改称铁匠铺。F02sunflower农场中心18×10×25/DV3120，4500全格=1458非air3042air，多棚/住处/院，3棕床对与5原实体（4armorstand+itemframe）不计建筑/工人。两源炉空unlit，原source/BE/entities/metadata/context全部保留核对，未称全部层/145或165palette/内外步行已人工验。\n\n渲染前341历史pair/同源别名/rawroleoccupancy排除；实际NBT/pool kaisyn、root/tag towns_and_towers；selected均1legacy rigid emptyprocessor。F01root7/max80，F02root5/max116，均start0/surface/beardthin/expansiontrue，source jigsaw与waystone/decor/windmill/streets未运行装配或当额外已研建筑，单Jar无vanilla pool/loot不当环境缺。\n\nMain097F01独立收据ec0115ecb09a420c46a60d3c5448d983d73b6bbe427afee81c5bb2acff7c7c97/33456B新增COD3NPC01空间参考1，在100第一次精确承接；095F02已097承接，本批只carry不重复。098F01最多1仍待独立适用/家族审，老pending保留；COD4仍153差847，无清单任务删除。研究不等原创制作/任务前置材料付款原生回执/中文指南针/最终验收。无Java/Gradle/游戏/QA/音量亮度唤醒/原存档实例/Jar/产品/建模贴图/网络/提交发布。下一101继续固定本地完整相关建筑。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'actual_current_images_viewed':8,'generated_png':19,'unviewed_png':11,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'prior097_F01_first_carried_admission_increment':1,'COD4_increment':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'actual_images_viewed':8,'complete_studies':0,'pending':0,'credit':0},ensure_ascii=False))

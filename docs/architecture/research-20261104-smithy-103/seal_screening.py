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
reasons=[{'purpose':'法师建筑群兵营/装备陈列房：单个磨具12,2,8与6实体（4pillager/2armorstand）并不证明独立锻造工坊。','whole_boundary':'仅whole/cutaway/y2三图初筛用途，未逐8视图/所有层与房间完整适用家族研究，不按装备架/敌人/4houses池元素计数，也不将整个magecomplex计作当前。','evidence':'18×10×13/DV3578；2340全格=805非air1535显式air，无省略，60palette完整保存未逐项人工解释。无炉/smith/anvil/lava/床，装备架原盔甲Items和4pillager原存不当制作新人物/已运行生成。'}, {'purpose':'猪灵村圆形中心广场与分散棚/院场，低西南2blast+lavacauldron，4个高处wallgrind在篷布吊构上，不当4可站岗位。','whole_boundary':'仅whole/cutaway/y2三图初筛完整工坊边界，未逐栋分开研究、整村或散棚未当一独立相关工坊/多建筑；当前0。','evidence':'32×15×33/DV3578；15840全格=1958非air13882显式air，无省略，158palette全存未逐状态人工解释。grind3,7,z12/14与17/19,7,29，下y5/6chain，上8air/9redwool；两blast8,1,25与9,2,26north空unlit，cauldron7,1,24lava不是water；原entities0，root猪灵配置不等实际工人。'}]
raw=get('raw-source-audit.json')['candidates'];ctx=get('source-context.json');screen=get('pre-render-history-screen.json');cases=[];functional=[];context_notes=[]
for a,r,why in zip(get('sources.json')['candidates'],raw,reasons):
 ident=a['id'];sr=next(x for x in screen['rows']if x['id']==ident)
 check(ident+' pre-render member/alias/raw/role/occupancy passed',sr['eligible_for_new_source_study']and not any(sr[k]for k in ['known_history','historical_exact_matches','within_batch_exact_matches','same_bytes_aliases']))
 check(ident+' fixed archive unchanged',bind(a['source_archive'])==sr['fixed_archive'])
 with ZipFile(a['source_archive'])as z:
  b=z.read(a['member']);d=read(b);pal=d['palette'];counts=Counter(pal[x['state']]['Name']for x in d['blocks']);mp={tuple(x['pos']):pal[x['state']]for x in d['blocks']}
  check(ident+' original NBT lossless bind',hashlib.sha256(b).hexdigest()==a['nbt_sha256']==r['nbt_sha256']and d==restore(r['nbt_decoded_original']))
  check(ident+' unique all positions and state bounds',len(mp)==len(d['blocks'])and all(0<=x['state']<len(pal)and all(0<=x['pos'][i]<d['size'][i]for i in range(3))for x in d['blocks']))
  check(ident+' full material and explicit air counts',dict(counts)==r['material_counts']and sum(counts[n]for n in AIR)==r['air']and len(d['blocks'])-r['air']==r['nonair'])
  f={'id':ident,'declared_volume':math.prod(d['size']),'stored_records':len(d['blocks']),'explicit_air':r['air'],'nonair':r['nonair'],'omitted_positions':math.prod(d['size'])-len(d['blocks']),'entities_original':d['entities'],'functional_states':[{'pos':x['pos'],'state':pal[x['state']],'original_block_entity':x.get('nbt')}for x in d['blocks']if x.get('nbt')or any(t in pal[x['state']]['Name']for t in ['door','furnace','smoker','smithing','grindstone','bed','lava','water','stairs','ladder','anvil','loom','cartography','crafting','stonecutter','cauldron'])]};functional.append(f)
  for m in [m for m in ctx['metadata']if m['id']==ident]:check(ident+' metadata '+m['member'],hashlib.sha256(z.read(m['member'])).hexdigest()==m['sha256']and z.read(m['member']).decode()==m['original_text'])
  c=next(c for c in ctx['candidates']if c['id']==ident)
  for cc in c['contexts']:check(ident+' context '+cc['member'],hashlib.sha256(z.read(cc['member'])).hexdigest()==cc['sha256']and json.loads(z.read(cc['member']))==cc['json'])
  for missing in c['missing']:check(ident+' missing only single Jar '+missing,missing not in z.namelist())
  root=next(x['json']for x in c['contexts']if '/worldgen/structure/'in x['member']);pool=next(x['json']for x in c['contexts']if x['member'].endswith('/mage/houses.json'if ident=='F01'else'/town_centers.json'))
  selected=[e for e in pool['elements']if e['element']['location']==c['location']]
  check(ident+' source DV3578/allcoords no omission',d['DataVersion']==3578 and len(d['blocks'])==math.prod(d['size'])and f['omitted_positions']==0)
  check(ident+' actual selected single related context not other bodies studied',len(selected)==1 and selected[0]['weight']==1 and selected[0]['element']['projection']=='rigid'and pool['fallback']=='minecraft:empty')
  check(ident+' root start0/surface/beardthin/80 original',root['start_height']=={'absolute':0}and root['project_start_to_heightmap']=='WORLD_SURFACE_WG'and root['terrain_adaptation']=='beard_thin'and root['max_distance_from_center']==80)
  if ident=='F01':
   check('F01 2340all/805nonair1535air/60palette',len(d['blocks'])==2340 and r['nonair']==805 and r['air']==1535 and len(pal)==60)
   check('F01 one grind no forge heat smith anvil beds',counts['minecraft:grindstone']==1 and mp[12,2,8]['Properties']=={'face':'floor','facing':'south'}and all(counts[n]==0 for n in ['minecraft:blast_furnace','minecraft:furnace','minecraft:smoker','minecraft:smithing_table','minecraft:anvil','minecraft:lava'])and not any(n.endswith('_bed')for n in counts))
   check('F01 original4pillager2armorstands',Counter(e['nbt']['id']for e in d['entities'])==Counter({'minecraft:pillager':4,'minecraft:armor_stand':2}))
   check('F01 housepool4 source not rootstart selected direct barracks',len(pool['elements'])==4 and pool['name']=='mage_hice'and root['start_pool']=='terralith:mage/complex_start'and root['size']==6 and root['use_expansion_hack']is False and selected[0]['element']['element_type']=='minecraft:single_pool_element'and selected[0]['element']['processors']=='terralith:mage/ground')
   ground=next(x['json']for x in c['contexts']if '/processor_list/'in x['member']);rule=ground['processors'][0]['rules'][0];check('F01 processor conditioned worldcalcite not allgrass transformed',len(ground['processors'][0]['rules'])==1 and rule['location_predicate']=={'predicate_type':'minecraft:block_match','block':'minecraft:calcite'}and rule['input_predicate']['block']=='minecraft:grass_block'and rule['input_predicate']['probability']==1 and rule['output_state']=={'Name':'minecraft:calcite'})
  else:
   check('F02 15840all/1958nonair13882air/158palette',len(d['blocks'])==15840 and r['nonair']==1958 and r['air']==13882 and len(pal)==158)
   high=[(3,7,12),(3,7,14),(17,7,29),(19,7,29)];check('F02 4wallgrind chain below wool above not4workrooms',counts['minecraft:grindstone']==4 and all(mp[p]['Name']=='minecraft:grindstone'and mp[p]['Properties']['face']=='wall'and mp[p[0],5,p[2]]['Name']==mp[p[0],6,p[2]]['Name']=='minecraft:chain'and mp[p[0],8,p[2]]['Name']=='minecraft:air'and mp[p[0],9,p[2]]['Name']=='minecraft:red_wool'for p in high))
   check('F02 2original empty unlit blast different coords',counts['minecraft:blast_furnace']==2 and all(x['nbt']['Items']==[]and x['nbt']['BurnTime']==x['nbt']['CookTime']==0 and pal[x['state']]['Properties']['lit']=='false'for x in d['blocks']if pal[x['state']]['Name']=='minecraft:blast_furnace'))
   check('F02 lava cauldron and0entities original',mp[7,1,24]['Name']=='minecraft:lava_cauldron'and d['entities']==[])
   check('F02 root2 expansiontrue selectedlegacy streetprocessor',root['size']==2 and root['use_expansion_hack']is True and selected[0]['element']['element_type']=='minecraft:legacy_single_pool_element'and selected[0]['element']['processors']=='kaisyn:village/exclusives/street_piglin')
   proc=next(x['json']for x in c['contexts']if '/processor_list/'in x['member']);rules=proc['processors'][0]['rules'];check('F02 6sequential streetrules no20percent equal outcomes assertion',len(rules)==6 and rules[0]['location_predicate']['block']=='minecraft:water'and rules[0]['output_state']['Name']=='minecraft:oak_planks'and all(rule['input_predicate']['probability']==0.2 for rule in rules[1:5])and rules[5]['output_state']['Name']=='minecraft:gravel')
  images=[bind(OUT/(ident+'-'+n+'.png'))for n in ['whole','cutaway','y2']]
  for im in images:
   with Image.open(im['path'])as image:image.verify()
   check(ident+' actual viewed PNG '+Path(im['path']).name,bind(im['path'])==im)
  cases.append({**a,'screening_observations':why,'images_actually_viewed':images,'actual_full_reference_study_complete':False,'credit_proposal_maximum':0,'formal_credit_added':0,'status':'PRELIMINARY_BARRACKS_OR_SETTLEMENT_CENTER_EXCLUSION_ZERO','native_acceptance':False})
  context_notes.append({'id':ident,'context_root_original_not_direct_source_selection_assumed':root,'actual_selected_pool_original':pool,'missing_only_single_archive':c['missing'],'world_assembly_spawn_loot_execution':False})
put('functional-evidence.json',{'candidates':functional,'original_states_preserved':True,'native_function_not_verified':True})
put('manual-review.json',{'scope':'Preliminary barracks/settlement-center relevance boundaries only, no full related-building studies.','cases':cases,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_current_png':19,'actual_current_images_viewed':6,'unviewed_png':13,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'no_independent_self_admission':True})
viewed=[x for c in cases for x in c['images_actually_viewed']];paths={x['path']for x in viewed};unviewed=[bind(p)for p in sorted(OUT.glob('*.png'))if str(p)not in paths]
put('visual-reading-boundary.json',{'viewed':viewed,'not_viewed_generated':unviewed,'unviewed_not_references_or_observations':True,'no_claim_all_layers_or_navigation_reviewed':True,'generic_class_fullcell_not_actual_textures_collision_entities':True})
put('source-context-reading.json',{'cases':context_notes,'reading_scope':'仅各whole/cutaway/y2共6实际图、关键功能state/原实体/位置/root/实际选中pool/processor/biome/meta信息；所有NBT/BE/entities/context原文核对，未称60/158palette逐项解释或13未看图为人工研究，loot只读池数未逐全部函数人工解析/执行。','F01_context_boundary':'实际barracks在mage/houses4元素之一，原pool name mage_hice保留；所存mage_complex root直接startpool mage/complex_start仅选mage/complex，不把其root6或主体另一NBT直接转给barracks为独立结构/已验证装配链。ground只在worldcalcite位置+inputgrass概率1时输出calcite，不把原所有grass变白；不研究/计其他houses/complex主体。biometag moonlight_grove/lavender_forest/amethyst_rainforest3mandatory。','F01_metadata':'Terralith2.5.4/Forge lowcodefml1/Stardust Labs License/署名Starmute,catter1,TheKingWhale,Apollounknowndev；pack15 supported15..41/按版本overlay原存，不推当前兼容/混用overlay改源。','F02_context_boundary':'T&T root2/max80/start0/beardthin/expansiontrue，monsterfullbox piglinw6/min6max8及brutew1/min2max3原存不等已生工人；原entities0。single实际legacy/街道piglin processor six sequential：worldwater黑tc→oakplanks，再四random0.2黑tc分别basalt/smoothbasalt/cobbleddeepslate/cobble，最后黑tc→gravel；非每材各20%且不执行。onlyoptional wythers:savanna_basaltic_incursions不是已安装/实际落地。hoglin/street引用只池元信息不研究或算其他完整建筑。','F02_metadata':'Towns and Towers固定1.12/Forge version原${file.jarVersion}/Fabric1.12/pack18，Kubek,Biban_Auriu,Cristelknight等/CCBYNCSA4原存，不修成一致/推运行兼容。','prior':'097F01已100首次承接1/095F02已097首次承接1，本批均carry0；098F01/101F01各旧max1待Main独立审，旧pending保留；COD4仍153差847。','limits':'无Java/Gradle/游戏/QA/唤醒音亮/用户实例存档/Jar/产品/任务指南针/人物建模贴图/主清单/网络/提交发布。'})
prev=ROOT/'docs/architecture/research-20261104-smithy-102';put('task-scope-boundary.json',json.loads((prev/'task-scope-boundary.json').read_text()))
put('carried-forward-pending.json',{'previous_batch_receipt':bind(prev/'RECEIPT.json'),'current_batch_new_pending':0,'prior_pending':[{'batch':n,'id':'F01','maximum':1,'manual':bind(ROOT/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json'),'receipt':bind(ROOT/f'docs/architecture/research-20261104-smithy-{n:03d}/RECEIPT.json')}for n in [98,101]],'097F01_accepted_first_100_carry_only':True,'095F02_accepted_first_097_carry_only':True,'older_pending_not_cancelled':True,'not_master_todo_backup':True})
check('347 history pairs not semanticcredit',screen['history_unique_archive_member_pairs']==347);check('prior097prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
bindings(get('latest-independent-admissions.json'));bindings(get('carried-forward-pending.json'))
check('097F01 first100 carryonly no repeat',get('latest-independent-admissions.json')['newly_notified_admission_097_F01']['first_bound_batch']==100 and get('latest-independent-admissions.json')['097F01_first_bound_100_carry_only_no_current_increment'])
check('19generated6actual13unviewed',len(list(OUT.glob('*.png')))==19 and len(viewed)==6 and len(unviewed)==13)
check('current0fullrelatedstudies0pending0formalcredit',get('manual-review.json')['complete_whole_reference_studies']==get('manual-review.json')['pending_maximum']==get('manual-review.json')['formal_credit_added']==0)
put('verification.json',{'status':'PASS_CURRENT_PRELIMINARY_SCREENING_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'all_tasks_complete':False})
status='SEALED_BARRACKS_AND_PIGLIN_CENTER_BOUNDARY_EXCLUSIONS_ZERO_COMPLETE_STUDIES'
put('session.json',{'batch':103,'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_png':19,'actual_images_viewed':6,'unviewed_generated':13,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'prior097_F01_first_bound_100_carry_only_increment':0,'095F02_carry_only_increment':0,'prior098_101_F01_max1_pending_preserved':True,'latest_independent_admission_binding':bind(OUT/'latest-independent-admissions.json'),'cumulative_not_reset':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'104继续其他固定本地完整相关功能建筑，本批0不反复，不提前制作/删任务。'})
put('active-checkpoint.json',{'batch':103,'status':status,'actual_images_viewed':6,'complete_whole_reference_studies':0,'formal_credit_added':0,'java_run':False,'all_tasks_complete':False,'verification':bind(OUT/'verification.json'),'next_batch':104})
(OUT/'HANDOFF.md').write_text('103用途/计数边界初筛两源0。F01 Terralith mage/barracks18×10×13/DV3578，2340全格=805非air1535air，原60palette；1floorgrind12,2,8与6原实体4pillager/2armorstand，不当完整锻造工坊/制作人物。实际mage/houses池四元素之一，原name mage_hice；所存mage_complex root直接startcomplex_start选mage/complex，不直接选本barracks/不验证全装配链。groundprocessor只有worldcalcite位置+inputgrass概率1→calcite，不全地草变白。\n\nF02 T&T piglinmeeting32×15×33/DV3578，15840全格=1958非air13882air，原158palette；圆形村中心分散院棚，西南2emptyunlitblast/1lavacauldron。四wallgrind在3,7,z12/14及17/19,7,29，下面y5/6chain，上8air/9redwool，是篷布吊构证据不是4可站磨具房。仅各whole/cutaway/y2共6实际PNG，19生成/13未看逐绑定；0完整相关研究/0newpending/formal0，不请求Main重复审。原source/meta/BE/entities/context全保留核对，未逐全部palette/全层导航或所有loot函数人工研究。\n\n347历史pair/同源别名/rawroleoccupancy先排渲染。F02root2/max80/start0/beardthin/expansiontrue，piglin/brute原monster配置不当已生工人；singlelegacy streetpiglin六规则按序，不各材独立20%/不执行；optionalWythers不推已安装。F01Terralith2.5.4/StardustLabsLicense/pack15 supports15..41版本overlay，F02T&T1.12/Forge原插值/Fabric1.12/pack18/CCBYNCSA4，均不推当前兼容。\n\n097F01已100首次承接/095F02已097首次承接，本批只carry0；098F01/101F01各max1待Main独立用途家族审保留。COD4仍153差847，无1000完成/产品制作/清单删除/原生任务材料付款回执或中文指南针通过宣称。无Java/Gradle/游戏/QA/唤醒音亮/用户存档实例/Jar/人物建模贴图/网络/提交发布。下一104继续固定本地完整相关来源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'actual_current_images_viewed':6,'generated_png':19,'unviewed_png':13,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'actual_images_viewed':6,'complete_studies':0,'pending':0,'credit':0},ensure_ascii=False))

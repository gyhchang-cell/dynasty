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
reasons=[{'purpose':'长体海上交易帆桨船，两座铁砧位于两侧木柱顶，不凭名字trade/两个anvil命中就当相关铁匠工坊。','whole_boundary':'只初步whole/cutaway/y8共3图用途排除，未研究全部23图/舱室层/航路；船、桅杆、帆、桨、4socket或4桶均不当完整相关建筑。','evidence':'41×39×19/DV3337；30381声明格/2618记录=1938非air680显式air/27763省略。128palette原存未逐state人工解释；两anvil8,8,z6/12下y6/7oaklog，上y9/10省略非air；无forge热炉/磨具/smith/床，原entities0。root实际ocean/deepocean/start-2/terrainnone，与山脚工坊用途未证。'}, {'purpose':'小型热带交易帆船，两个anvil位于14,5,z4/6木面上，不能仅据砧命中认定铁匠铺或加工链。','whole_boundary':'只初步whole/cutaway/y4共3图用途排除；帆/桅/梯/船体未作完整工坊空间家族研究，不将暖海岸贸易载具转称山脚作坊。','evidence':'20×22×11/DV3337；4840声明格/662记录=528非air134显式air/4178省略；61palette全保存未逐state人工解读。两anvil下4spruceplanks，6air，14,7,6greenwool；10梯/1原桶/1jigsaw/entities0，不当10层/1已生村民。无forge热炉/磨具/smith/床，rootwarmocean/start-2/terrainnone。'}]
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
  root=next(x['json']for x in c['contexts']if '/worldgen/structure/'in x['member']);pool=next(x['json']for x in c['contexts']if '/worldgen/template_pool/overworld/medium/'in x['member'])
  check(ident+' root original2/max64/start-2/ocean/terrainnone/false',root['size']==2 and root['max_distance_from_center']==64 and root['start_height']=={'absolute':-2}and root['terrain_adaptation']=='none'and root['use_expansion_hack']is False and root['project_start_to_heightmap']=='WORLD_SURFACE_WG'and root['spawn_overrides']=={})
  check(ident+' selectedsingle1/rigid/emptyprocessor/emptyfallback',pool['elements']==[{'weight':1,'element':{'element_type':'minecraft:single_pool_element','location':c['location'],'projection':'rigid','processors':'minecraft:empty'}}]and pool['fallback']=='minecraft:empty')
  check(ident+' two original anvils no forge heat/grind/smith/bed',counts['minecraft:anvil']==2 and all(counts[n]==0 for n in ['minecraft:blast_furnace','minecraft:furnace','minecraft:smoker','minecraft:grindstone','minecraft:smithing_table','minecraft:lava'])and not any(n.endswith('_bed')for n in counts))
  check(ident+' original0entities not NPCs',d['entities']==[])
  if ident=='F01':
   check('F01 original30381/2618/1938/680/27763/128palette',math.prod(d['size'])==30381 and len(d['blocks'])==2618 and r['nonair']==1938 and r['air']==680 and f['omitted_positions']==27763 and len(pal)==128)
   check('F01 two original pillar top anvils upper omitted',all(mp[8,8,zz]['Name']=='minecraft:anvil'and mp[8,6,zz]['Name']==mp[8,7,zz]['Name']=='minecraft:oak_log'and(8,9,zz)not in mp and(8,10,zz)not in mp for zz in [6,12]))
   check('F01 4barrels4villager sockets source',counts['minecraft:barrel']==counts['minecraft:jigsaw']==4)
  else:
   check('F02 original4840/662/528/134/4178/61palette',math.prod(d['size'])==4840 and len(d['blocks'])==662 and r['nonair']==528 and r['air']==134 and f['omitted_positions']==4178 and len(pal)==61)
   check('F02 anvil original platform/top airorwool',all(mp[14,5,zz]['Name']=='minecraft:anvil'and mp[14,4,zz]['Name']=='minecraft:spruce_planks'and mp[14,6,zz]['Name']=='minecraft:air'for zz in [4,6])and mp[14,7,6]['Name']=='minecraft:green_wool')
   check('F02 10ladder1barrel1socket source',counts['minecraft:ladder']==10 and counts['minecraft:barrel']==counts['minecraft:jigsaw']==1)
  images=[bind(OUT/(ident+'-'+n+'.png'))for n in ['whole','cutaway','y8'if ident=='F01'else'y4']]
  for im in images:
   with Image.open(im['path'])as image:image.verify()
   check(ident+' actual viewed PNG '+Path(im['path']).name,bind(im['path'])==im)
  cases.append({**a,'screening_observations':why,'images_actually_viewed':images,'actual_full_reference_study_complete':False,'credit_proposal_maximum':0,'formal_credit_added':0,'status':'PRELIMINARY_SHIP_NOT_RELATED_WORKSHOP_EXCLUSION','native_acceptance':False})
  context_notes.append({'id':ident,'root_original':root,'selected_pool_original':pool,'missing_only_in_single_fixed_archive':c['missing'],'world_assembly_spawn_loot_execution':False})
put('functional-evidence.json',{'candidates':functional,'original_states_preserved':True,'native_function_not_verified':True})
put('manual-review.json',{'scope':'Preliminary ships-purpose exclusions only, no complete related-building studies.','cases':cases,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_current_png':37,'actual_current_images_viewed':6,'unviewed_png':31,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'no_independent_self_admission':True})
viewed=[x for c in cases for x in c['images_actually_viewed']];paths={x['path']for x in viewed};unviewed=[bind(p)for p in sorted(OUT.glob('*.png'))if str(p)not in paths]
put('visual-reading-boundary.json',{'viewed':viewed,'not_viewed_generated':unviewed,'unviewed_not_references_or_observations':True,'no_claim_all_layers_or_navigation_reviewed':True,'generic_class_fullcell_not_actual_textures_collision_entities':True})
put('source-context-reading.json',{'cases':context_notes,'actual_scope':'只各3图/关键anvil上下state及原block counts/root/pool/tag/loot实际查看，未逐128/61palette或全层/舱内/所有梯路径人工审，不称2个完整工坊研究。原NBT/BE/entities及全部元信息/context逐SHA核对。','metadata':'复用固定Trek同Jar的Forge/fabric1-B0.6.1/hotsuop,Hugger,ALDgamer/MIT/pack10supports10..102原元信息；不推运行兼容。','roots_and_biomes':'两root size2/max64/start-2/WORLDSURFACEWG/terrainnone/expansionfalse/spawns{}；独立single1rigid空processor/fallbackempty。F01ocean/deepocean，F02warmocean，不当山脚地形落地参考。','villager_pools':'plains/jungle两池各unemployed8/nitwit1/baby1legacyrigid/empty，不是每socket10村民或已spawn；本源entities0，未取人形模型或贴图。','loot':'F01roll4bread/book1..2/whitewool各w1/paper1..4w2，roll1writablebook1..2w2，roll1enchantedbook(#minecraft:on_random_loot)/empty3。该enchant选项原值不修或猜运行。F02原jungle_treehouse表roll2emerald1..2，roll4cocoa3..6/sugarcane3/vine3..4均w2。原Seed/loot全留不当任务发奖/实际付款链，未执行。','prior':'097F01已100首次承接1/095F02已097首次承接1，本批均carry0；098F01/101F01各旧max1待Main独立审，旧pending保留；COD4仍153差847。','limits':'无Java/Gradle/游戏/QA/唤醒音亮/原存档实例/Jar/产品/任务指南针/建模贴图/清单/网络/提交发布。'})
prev=ROOT/'docs/architecture/research-20261104-smithy-101';put('task-scope-boundary.json',json.loads((prev/'task-scope-boundary.json').read_text()))
put('carried-forward-pending.json',{'previous_batch_receipt':bind(prev/'RECEIPT.json'),'current_batch_new_pending':0,'prior_pending':[{'batch':n,'id':'F01','maximum':1,'manual':bind(ROOT/f'docs/architecture/research-20261104-smithy-{n:03d}/manual-review.json'),'receipt':bind(ROOT/f'docs/architecture/research-20261104-smithy-{n:03d}/RECEIPT.json')}for n in [98,101]],'097F01_accepted_first_100_carry_only':True,'095F02_accepted_first_097_carry_only':True,'older_pending_not_cancelled':True,'not_master_todo_backup':True})
check('345 historical pairs not semanticcredit',screen['history_unique_archive_member_pairs']==345);check('prior097prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
bindings(get('latest-independent-admissions.json'));bindings(get('carried-forward-pending.json'))
check('097F01 first100 no new increment',get('latest-independent-admissions.json')['newly_notified_admission_097_F01']['first_bound_batch']==100 and get('latest-independent-admissions.json')['097F01_first_bound_100_carry_only_no_current_increment'])
check('37generated6actual31unviewed',len(list(OUT.glob('*.png')))==37 and len(viewed)==6 and len(unviewed)==31)
check('0currentfullstudies0pending0formalcredit',get('manual-review.json')['complete_whole_reference_studies']==get('manual-review.json')['pending_maximum']==get('manual-review.json')['formal_credit_added']==0)
put('verification.json',{'status':'PASS_CURRENT_PRELIMINARY_SCREENING_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'all_tasks_complete':False})
status='SEALED_TWO_TRADE_SHIP_RELEVANCE_EXCLUSIONS_ZERO_COMPLETE_STUDIES'
put('session.json',{'batch':102,'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'generated_png':37,'actual_images_viewed':6,'unviewed_generated':31,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'prior097_F01_first_bound_100_carry_only_increment':0,'095F02_carry_only_increment':0,'prior098_101_F01_max1_pending_preserved':True,'latest_independent_admission_binding':bind(OUT/'latest-independent-admissions.json'),'cumulative_not_reset':True,'java_run':False,'product_files_written':False,'masterlists_edited':False,'native_acceptance':False,'all_tasks_complete':False,'next':'103继续其他固定本地完整相关功能建筑，贸易船不反复/不计参考，不提前制作/删任务。'})
put('active-checkpoint.json',{'batch':102,'status':status,'actual_images_viewed':6,'complete_whole_reference_studies':0,'formal_credit_added':0,'java_run':False,'all_tasks_complete':False,'verification':bind(OUT/'verification.json'),'next_batch':103})
(OUT/'HANDOFF.md').write_text('102仅贸易帆船用途初筛排除：F01 dark_oak_trade41×39×19/DV3337，30381声明/2618记录=1938非air680air/27763省略；两anvil8,8,z6/12在木柱顶，上9/10省略不是air。F02 jungle_trade20×22×11/DV3337，4840声明/662记录=528非air134air/4178省略，两anvil14,5,z4/6位于木面，6air/14,7,6greenwool。两源无forge热炉/磨具/smith/床，海上船体/帆桅不当山脚工坊完整参考。37生成PNG只实际各whole/cutaway/相应anvil平面(y8/y4)共6，31未看逐绑定；0完整相关研究/0pending/formal0，不要求Main重复审。\n\n345历史pair/同源别名/rawroleoccupancy渲染前排除；原source/BE/entities/meta/context全保存核对，128/61palette非逐项人工/全舱全层导航研究。root均2/max64/start-2/surface/terrainnone/expansionfalse/spawns{}，各single1rigid空processor/emptyfallback；F01ocean/deepocean/F02warmocean。villagerpool8/1/1不是10已spawn，NBTentities0。loot原书/纸/羊毛和热带材料不当任务发奖/付款回执，未运行生成。\n\n097F01已100首次承接/095F02已097首次承接，本批只carry0；098F01/101F01各max1待Main独立用途/家族审保留。COD4仍153差847，无1000完成/制作/删清单宣称。无Java/Gradle/游戏/QA/唤醒音亮/原存档实例/Jar/产品/任务指南针/建模贴图/网络/提交发布。下一103继续其他固定本地完整相关来源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];put('RECEIPT.json',{'status':status,'source_bodies_visually_screened':2,'complete_whole_reference_studies':0,'actual_current_images_viewed':6,'generated_png':37,'unviewed_png':31,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'actual_images_viewed':6,'complete_studies':0,'pending':0,'credit':0},ensure_ascii=False))

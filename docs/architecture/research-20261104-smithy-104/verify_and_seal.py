import json,hashlib,sys,math
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
def write(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
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
sources=get('sources.json')['candidates'];raw=get('raw-source-audit.json')['candidates'];review=get('manual-review.json');ctx=get('source-context.json');screen=get('pre-render-history-screen.json');functional=get('functional-evidence.json')['candidates']
check('2 current sources aligned',len(sources)==len(raw)==len(review['cases'])==len(functional)==2 and [a['id']for a in sources]==[a['id']for a in raw]==[a['id']for a in review['cases']])
for a,r,f in zip(sources,raw,functional):
 ident=a['id'];sr=next(x for x in screen['rows']if x['id']==ident);check(ident+' fixed archive binding',bind(a['source_archive'])==sr['fixed_archive'])
 with ZipFile(a['source_archive'])as z:
  b=z.read(a['member']);d=read(b);pal=d.get('palette')or d['palettes'][0];pos=[tuple(x['pos'])for x in d['blocks']];count=Counter(pal[x['state']]['Name']for x in d['blocks'])
  check(ident+' original raw SHA',hashlib.sha256(b).hexdigest()==a['nbt_sha256']==r['nbt_sha256']);check(ident+' full decoded original including byte array',d==restore(r['nbt_decoded_original']));check(ident+' actual version size',d['DataVersion']==a['DataVersion']and d['size']==a['size']);check(ident+' unique positions',len(pos)==len(set(pos)));check(ident+' positions bounds',all(all(0<=p[i]<d['size'][i]for i in range(3))for p in pos));check(ident+' palette indices',all(0<=x['state']<len(pal)for x in d['blocks']));check(ident+' material counts',dict(count)==r['material_counts']);check(ident+' air nonair',sum(v for k,v in count.items()if k in AIR)==r['air']and len(pos)-r['air']==r['nonair']);check(ident+' sparse breakdown',f['stored_records']==len(pos)and f['declared_volume']==math.prod(d['size'])and f['omitted_positions']==math.prod(d['size'])-len(pos));check(ident+' all entities',f['entities_original']==d.get('entities',[]))
  expect=[{'pos':b['pos'],'state':pal[b['state']],'original_block_entity':b.get('nbt')}for b in d['blocks']if b.get('nbt')or any(w in pal[b['state']]['Name']for w in ['door','furnace','smoker','smithing','grindstone','bed','lava','water','stairs','ladder','anvil','loom','cartography','crafting','stonecutter','cauldron'])];check(ident+' all functional/BE original including bytes',expect==restore(f['functional_states']))
  for md in [m for m in ctx['metadata']if m['id']==ident]:
   bb=z.read(md['member']);check(ident+' metadata '+md['member'],hashlib.sha256(bb).hexdigest()==md['sha256']and bb.decode()==md['original_text'])
  c=next(c for c in ctx['candidates']if c['id']==ident)
  for cc in c['contexts']:
   bb=z.read(cc['member']);check(ident+' source context '+cc['member'],hashlib.sha256(bb).hexdigest()==cc['sha256']and json.loads(bb)==cc['json'])
  check(ident+' pre-render exclusion identity',sr['eligible_for_new_source_study']and not sr['known_history']and not sr['historical_exact_matches']and not sr['within_batch_exact_matches']and sr['nbt_sha256']==a['nbt_sha256'])
  cells={tuple(b['pos']):pal[b['state']]for b in d['blocks']};mat=get(ident+'-original-layer-matrices.json')
  state_map={tuple(b['pos']):b['state']for b in d['blocks']};expected=[{'y':y,'rows_z_increasing':[[state_map.get((x,y,zz),-1)for x in range(d['size'][0])]for zz in range(d['size'][2])]}for y in range(d['size'][1])]
  check(ident+' every original full state layer matrix',mat['all_original_layers']==expected and mat['state_legend']=={str(i):s for i,s in enumerate(pal)})
  route=get(ident+'-route-evidence.json')['selected_route_states'];check(ident+' selected routes original incl omission',all(cells.get(tuple(q['pos']),{'__omitted_original__':True})==q['state']for q in route))
  check(ident+' original DV3465 entities0 no ladder bed',d['DataVersion']==3465 and d['entities']==[]and count['minecraft:ladder']==0 and not any(n.endswith('_bed')for n in count))
  root=next(x['json']for x in c['contexts']if '/worldgen/structure/'in x['member']);pool=next(x['json']for x in c['contexts']if x['member'].endswith('/houses.json'));selected=[e for e in pool['elements']if e['element'].get('location')==c['location']]
  check(ident+' custom root1/2/range22/start0 no fabricated maxdistance',root['type']=='repurposed_structures:generic_jigsaw_structure'and root['valid_biome_radius_check']==1 and root['terrain_height_radius_check']==2 and root['allowed_terrain_height_range']==22 and root['start_height']=={'absolute':0}and root['project_start_to_heightmap']=='WORLD_SURFACE_WG'and root['terrain_adaptation']=='beard_thin'and root['use_bounding_box_hack']is True and'max_distance_from_center'not in root and'use_expansion_hack'not in root)
  check(ident+' actual selectedweight/projection/processor',len(selected)==1 and selected[0]['weight']==(2 if ident=='F01'else 3)and selected[0]['element']['projection']=='rigid'and selected[0]['element']['processors']=='repurposed_structures:villages/'+('swamp'if ident=='F01'else'jungle')+'/mossify')
  check(ident+' missing vanilla loot singleJar only',all(n not in z.namelist()for n in c['missing']))
  if ident=='F01':
   check('F01 exact616volume395stored/349nonair46air221omitted28palette',math.prod(d['size'])==616 and len(pos)==395 and r['nonair']==349 and r['air']==46 and f['omitted_positions']==221 and len(pal)==28)
   check('F01 source mud/root quantities',all(count[n]==v for n,v in [('minecraft:muddy_mangrove_roots',144),('minecraft:mud',99),('minecraft:mangrove_roots',62),('minecraft:mud_bricks',15),('minecraft:packed_mud',4)]))
   check('F01 1empty unlit blast5,2,3 and no grinders smith lava',count['minecraft:blast_furnace']==1 and cells[5,2,3]['Properties']=={'lit':'false','facing':'west'}and all(count[n]==0 for n in ['minecraft:grindstone','minecraft:smithing_table','minecraft:anvil','minecraft:lava']))
   furnace=next(x['nbt']for x in d['blocks']if pal[x['state']]['Name']=='minecraft:blast_furnace');check('F01 furnace empty original cook0',furnace['Items']==[]and furnace['BurnTime']==furnace['CookTime']==0)
   chest=next(x for x in d['blocks']if pal[x['state']]['Name']=='minecraft:chest');check('F01 solechest original seed/loot',count['minecraft:chest']==1 and chest['pos']==[2,2,4]and chest['nbt']['LootTable']=='minecraft:chests/village/village_armorer'and chest['nbt']['LootTableSeed']==-6361098966003354797)
   check('F01 westclosed door and actual inner/outer air',cells[1,2,3]['Name']=='minecraft:mangrove_door'and cells[1,2,3]['Properties']['open']=='false'and all(cells[x,2,3]['Name']=='minecraft:air'for x in [0,2,3,4]))
   jigs=[x for x in d['blocks']if pal[x['state']]['Name']=='minecraft:jigsaw'];check('F01 2vines notNPC/entrance finalonlyfacing',len(jigs)==3 and sum(x['nbt']['pool']=='repurposed_structures:villages/swamp/vines'and x['nbt']['final_state']=='minecraft:air'for x in jigs)==2 and next(x['nbt']for x in jigs if x['pos']==[0,1,3])['final_state']=='minecraft:mangrove_stairs[facing=east]')
   check('F01 root6/toplayer and selectedmodernsingle',root['size']==6 and root['step']=='top_layer_modification'and selected[0]['element']['element_type']=='minecraft:single_pool_element')
   proc=next(x['json']for x in c['contexts']if x['member'].endswith('/swamp/mossify.json'));check('F01 mossify5rules+structurevoid original not executed',len(proc['processors'])==2 and len(proc['processors'][0]['rules'])==5 and proc['processors'][1]['processor_type']=='repurposed_structures:structure_void_processor')
  else:
   check('F02 exact819volume522stored/376nonair146air297omitted37palette',math.prod(d['size'])==819 and len(pos)==522 and r['nonair']==376 and r['air']==146 and f['omitted_positions']==297 and len(pal)==37)
   check('F02 2grind differentface and1lava nofurnacesmithanvil',count['minecraft:grindstone']==2 and cells[2,2,6]['Properties']=={'face':'floor','facing':'east'}and cells[5,2,3]['Properties']=={'face':'wall','facing':'east'}and count['minecraft:lava']==1 and cells[3,2,3]['Properties']['level']=='0'and all(count[n]==0 for n in ['minecraft:furnace','minecraft:blast_furnace','minecraft:smoker','minecraft:anvil','minecraft:smithing_table']))
   check('F02 westopendoor and originalgrind blocks drawnstraightline',cells[4,2,6]['Name']=='minecraft:jungle_door'and cells[4,2,6]['Properties']['open']=='true'and cells[2,2,6]['Name']=='minecraft:grindstone'and all(cells[x,2,6]['Name']=='minecraft:air'for x in [0,1,3,5,6]))
   chest=next(x for x in d['blocks']if pal[x['state']]['Name']=='minecraft:chest');check('F02 solechest original seedloot source',count['minecraft:chest']==1 and chest['pos']==[2,2,9]and chest['nbt']['LootTable']=='minecraft:chests/village/village_weaponsmith'and chest['nbt']['LootTableSeed']==7377455085333377559)
   check('F02 root8/surface and actualselectedlegacy',root['size']==8 and root['step']=='surface_structures'and selected[0]['element']['element_type']=='minecraft:legacy_single_pool_element')
   proc=next(x['json']for x in c['contexts']if x['member'].endswith('/jungle/mossify.json'));rules=proc['processors'][0]['rules'];check('F02 selectedmossify6rules actualforcednorthbottom stair',len(rules)==6 and rules[3]['output_state']=={'Properties':{'waterlogged':'false','shape':'straight','half':'bottom','facing':'north'},'Name':'minecraft:mossy_cobblestone_stairs'})
for case,n in zip(review['cases'],[9,7]):
 check(case['id']+' 7actualobservations/full current images',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}and len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact viewed PNG binding',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' old written judgment retained '+f['path'],bind(f['path'])==f)
 check(case['id']+' family held0 noindependentcredit/runtime',case['credit_proposal_maximum']==case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
check('prior090 keyword prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
dedup=get('dedup-evidence.json');check('349 historical pairs not semanticcredit',screen['history_unique_archive_member_pairs']==dedup['historical_unique_local_archive_member_pairs']==349)
check('current nohistorical exact but family still0',all(not e['historical_exact_matches']and not e['loose_exact_matches']for e in dedup['entries'])and not dedup['within_batch_pairs'][0]['exact_keys'])
check('F02 saved bamboo067 near0.99735 notexact family0',dedup['entries'][1]['nearest_occupancy_only'][0]['member']=='data/repurposed_structures/structures/villages/bamboo/houses/weaponsmith_2.nbt'and dedup['entries'][1]['nearest_occupancy_only'][0]['occupancy_jaccard']==0.99735 and '067F02'in review['cases'][1]['observations']['layout'])
v=get('visual-reading-boundary.json');check('all16actual no unviewedgenerated credit',len(list(OUT.glob('*.png')))==review['generated_current_png']==review['actual_current_images_viewed']==len(v['viewed'])==16 and len(v['not_viewed_generated'])==review['unviewed_png']==0)
check('2fullrelatedstudies14obs bothfamily0',review['complete_whole_reference_studies']==2 and review['manual_observations']==14 and review['held_zero']==2 and review['pending_maximum']==review['formal_credit_added']==0)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
bindings(get('latest-independent-admissions.json'));bindings(get('carried-forward-pending.json'));bindings(get('carried-forward-admission-resolution.json'))
res=get('carried-forward-admission-resolution.json');check('098F01 bounded0 resolvedfirst104 once pending removed',res['resolved_once']['batch']==98 and res['resolved_once']['accepted_increment']==res['resolved_once']['pending_maximum_after_screen']==0 and res['resolved_once']['first_bound_batch']==104 and get('carried-forward-pending.json')['098F01_resolved_zero_once_104'])
check('101F01 bounded0 resolvedfirst104 once pending removed',res['also_resolved_once_101']['batch']==101 and res['also_resolved_once_101']['accepted_increment']==res['also_resolved_once_101']['pending_maximum_after_screen']==0 and res['also_resolved_once_101']['first_bound_batch']==104 and get('carried-forward-pending.json')['101F01_resolved_zero_once_104']and get('carried-forward-pending.json')['prior_pending']==[])
check('097F01 remainsfirst100 carry0/095F02carry0',get('latest-independent-admissions.json')['newly_notified_admission_097_F01']['first_bound_batch']==100 and get('session.json')['prior097_F01_admission_first_bound_100_carry_only_increment']==get('session.json')['095F02_carry_only_increment']==0)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
status='SEALED_TWO_SMALL_WORKSHOP_STUDIES_EXISTING_FAMILIES_HELD_ZERO'
session=get('session.json');session['status']=status;write('session.json',session)
write('active-checkpoint.json',{'batch':104,'status':status,'complete_whole_reference_studies':2,'actual_current_images_viewed':16,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'098_101_F01_Main_bounded_relevance0_first_carried104':True,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'next_batch':105,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('104 两座完整小型职业铺研究，全部16实际PNG/14观察，均既有空间家族hold0，无newpending/formal0。F01 RS swamp armorer_house_1 8×11×7/DV3465，616声明/395记录=349非air46air/221省略；西门单炉箱共室，无床梯/上阁/分翼，泥根盖不新家族。muddyroots144/mud99/roots62是真材，不把灰图当石墙；1emptyunlitblast/1原Seed箱、两vines接口不NPC。F02RSjungle weaponsmith2 9×7×13/DV3465，819声明/522记录=376非air146air/297省略；西北1lava热台/壁磨+前场floorgrind→西open门→东南L冷储一室。与067F02竹林weapon2Jaccard0.99735近同形，另081/085/088单室和091外热内冷书面原判断实际比较绑定，不重看旧PNG/重验收。2,2,6磨具占中线，路线不能直穿工位；无炉床梯、同标高L盖不二层。两源全28/37palette、原NBT/每层matrix/BE/entities/route/meta/context核对，原0entities/Seed/vanilla loot保持。\n\n渲染前349历史pairs/别名/rawroleoccupancy检查；本批改回复用090关键词固定筛选，未重机器扫描或把58候选信用。RS自定义root swamp6/jungle8/check1/2/range22/start0/beardthin/boundingboxhacktrue，无maxdistance/expansion字段不套别Jar。F01step top_layer_modification/selected权2single，F02surface/权3legacy；当前mossify原规则实际读不执行，towncenterpathrandomizer/zombify仅上下文不是本屋processor。nestedcollections/swamps/jungles未展开推环境；两个vanilla loot单Jar缺不环境缺。\n\nMain098F01用途0收据f70de08b359f3cac082875f85c808b01425c9786cd4b34f0485ea0a6a0f0be4d/4577B与101F01用途0收据81db3e56712773fef742d578cedc3bb260fe3359523bdb0f173edd7846ccecd9/10176B在未封104各首次承接0并移除这两pending；Main各仅3图，余09824/1018未看，并非原生/全层全palette路线验收，不要求补看凑数。097F01已100首次接受1/095F02已097首次接受1，本批carry0，原旧封存材料不改不删。COD4仍153差847，当前门槛未达，无制作/清单删除/任务材料前置付款原生回执或中文指南针通过宣称。无Java/Gradle/游戏/QA/唤醒音亮/用户存档实例/Jar/产品/建模贴图/网络/提交发布。下一105继续固定本地未研小型工住/接客院落相关源，避免换皮单室或一炉一磨凑数。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':status,'complete_whole_reference_studies':2,'actual_current_images_viewed':16,'generated_png':16,'unviewed_png':0,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'098_101_F01_bounded_Main0_first_carried104':True,'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':0,'formal_credit':0},ensure_ascii=False))

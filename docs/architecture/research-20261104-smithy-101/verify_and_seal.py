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
  check(ident+' original entities0 not spawned hostile count',d['entities']==[])
  root=next(x['json']for x in c['contexts']if '/worldgen/structure/'in x['member']);pool=next(x['json']for x in c['contexts']if '/worldgen/template_pool/overworld/medium/'in x['member'])
  check(ident+' root2/max64/start0/surface/beardthin/false',root['size']==2 and root['max_distance_from_center']==64 and root['start_height']=={'absolute':0}and root['project_start_to_heightmap']=='WORLD_SURFACE_WG'and root['terrain_adaptation']=='beard_thin'and root['use_expansion_hack']is False)
  selected=[e for e in pool['elements']if e['element']['location']==c['location']]
  check(ident+' selected1of2 variants not2references',len(pool['elements'])==2 and len(selected)==1 and selected[0]['weight']==1 and selected[0]['element']['element_type']=='minecraft:single_pool_element'and selected[0]['element']['projection']=='rigid'and pool['fallback']=='minecraft:empty')
  mob='husk'if ident=='F01'else'skeleton';check(ident+' source hostile override not NPC',root['spawn_overrides']=={'monster':{'bounding_box':'full','spawns':[{'type':'minecraft:'+mob,'minCount':1,'maxCount':1,'weight':1}]}})
  sockets=[x for x in d['blocks']if pal[x['state']]['Name']=='minecraft:jigsaw'];check(ident+' 4original hostile sockets unexecuted',len(sockets)==4 and all(x['nbt']['pool']=='trek:mobs/hostile/'+mob for x in sockets))
  check(ident+' all furnaces empty unlit zero cooking',all(x['nbt']['Items']==[]and x['nbt']['BurnTime']==x['nbt']['CookTime']==0 and pal[x['state']]['Properties']['lit']=='false'for x in d['blocks']if pal[x['state']]['Name']in ['minecraft:blast_furnace','minecraft:furnace','minecraft:smoker']))
  check(ident+' missing contexts single Jar only',all(n not in z.namelist()for n in c['missing']))
  if ident=='F01':
   check('F01 exact2145volume/1160stored/985omitted/786nonair374air',math.prod(d['size'])==2145 and len(pos)==1160 and f['omitted_positions']==985 and r['nonair']==786 and r['air']==374 and len(pal)==69)
   route=get('F01-route-evidence.json')['selected_route_states'];check('F01 all selected routes including omitted exactly original',all(cells.get(tuple(q['pos']),{'__omitted_original__':True})==q['state']for q in route))
   check('F01 true western opening but outside omitted',all(cells[3,y,5]['Name']=='minecraft:air'and(2,y,5)not in cells for y in [1,2]))
   check('F01 main ladder1 five west states/closed bottom trap',all(cells[9,y,3]['Name']=='minecraft:ladder'and cells[9,y,3]['Properties']['facing']=='west'for y in range(1,6))and cells[9,6,3]['Properties']['half']=='bottom'and cells[9,6,3]['Properties']['open']=='false')
   check('F01 first landing plank plus air/vine not both air',cells[8,5,3]['Name']=='minecraft:birch_planks'and cells[8,6,3]['Name']=='minecraft:air'and cells[8,7,3]['Name']=='minecraft:vine')
   check('F01 main ladder2 five west/roof landing and closed trap',all(cells[9,y,7]['Name']=='minecraft:ladder'and cells[9,y,7]['Properties']['facing']=='west'for y in range(6,11))and cells[9,11,7]['Properties']['half']=='bottom'and cells[9,11,7]['Properties']['open']=='false'and cells[8,10,7]['Name']=='minecraft:sandstone'and all(cells[8,y,7]['Name']=='minecraft:air'for y in [11,12,13]))
   check('F01 14ladderstates two5main/two2bunk',count['minecraft:ladder']==14 and all(cells[6,y,7]['Name']==cells[9,y,4]['Name']=='minecraft:ladder'for y in [6,7]))
   check('F01 four real whitebedpairs at2heights',count['minecraft:white_bed']==8 and all(cells[7,y,8]['Properties']['part']=='foot'and cells[8,y,8]['Properties']['part']=='head'and cells[7,y,8]['Properties']['facing']==cells[8,y,8]['Properties']['facing']=='east'and cells[10,y,5]['Properties']['part']=='foot'and cells[10,y,6]['Properties']['part']=='head'and cells[10,y,5]['Properties']['facing']==cells[10,y,6]['Properties']['facing']=='south'for y in [6,8]))
   check('F01 bunk TOPslab furniture not full3rdfloor',all(cells[x,7,zz]['Name']=='minecraft:oak_slab'and cells[x,7,zz]['Properties']['type']=='top'for x,zz in [(7,8),(8,8),(10,5),(10,6)]))
   check('F01 furnace1/smoker1/grind1 onwoodpedestal/no smith anvil lava true door',count['minecraft:blast_furnace']==count['minecraft:smoker']==count['minecraft:grindstone']==1 and cells[7,2,2]['Properties']=={'face':'floor','facing':'north'}and cells[7,1,2]['Name']=='minecraft:oak_planks'and all(count[n]==0 for n in ['minecraft:smithing_table','minecraft:anvil','minecraft:chipped_anvil','minecraft:damaged_anvil','minecraft:lava'])and not any(n.endswith('_door')for n in count))
   containers=[x for x in d['blocks']if pal[x['state']]['Name']in ['minecraft:barrel','minecraft:chest']];check('F01 3barrel4chest all7original seeds/ownloot preserved',len(containers)==7 and count['minecraft:barrel']==3 and count['minecraft:chest']==4 and all('LootTableSeed'in x['nbt']and x['nbt']['LootTable']=='trek:overworld/medium/tour_deserts'for x in containers))
   check('F01 original3birch1sandstone finals notNPC',Counter(x['nbt']['final_state']for x in sockets)==Counter({'minecraft:birch_planks':3,'minecraft:sandstone':1})and selected[0]['element']['processors']=='minecraft:empty')
  else:
   check('F02 exact2904volume/1577stored/1327omitted/829nonair748air',math.prod(d['size'])==2904 and len(pos)==1577 and f['omitted_positions']==1327 and r['nonair']==829 and r['air']==748 and len(pal)==79)
   check('F02 no grind anvil smith bed ladder original',all(count[n]==0 for n in ['minecraft:grindstone','minecraft:smithing_table','minecraft:anvil','minecraft:chipped_anvil','minecraft:damaged_anvil','minecraft:ladder'])and not any(n.endswith('_bed')for n in count))
   check('F02 source2different floor furnaces exactstates',count['minecraft:furnace']==count['minecraft:blast_furnace']==1 and cells[6,2,9]['Name']=='minecraft:furnace'and cells[6,12,9]['Name']=='minecraft:blast_furnace')
   proc=next(x['json']for x in c['contexts']if '/processor_list/'in x['member']);rules=proc['processors'][0]['rules'];check('F02 source mossify2rules only no execution',selected[0]['element']['processors']=='trek:mossify_20_percent'and len(rules)==2 and [x['input_predicate']['probability']for x in rules]==[0.2,0.2]and [x['input_predicate']['block']for x in rules]==['minecraft:cobblestone','minecraft:stone_bricks'])
for case,n in zip(review['cases'],[11,4]):
 check(case['id']+' actual images count',len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' unchanged viewed PNG',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 check(case['id']+' formal0 not native',case['formal_credit_added']==0 and case['native_acceptance']is False)
f01=review['cases'][0];check('F01 full7observations not F02 coarse',set(f01['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'}and not review['cases'][1]['actual_full_reference_study_complete']and 'screening_observations'in review['cases'][1])
for f in f01['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check('old written comparison retained '+f['path'],bind(f['path'])==f)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
check('prior097 prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
dedup=get('dedup-evidence.json');check('343 historical pairs not semanticcredit',dedup['historical_unique_local_archive_member_pairs']==screen['history_unique_archive_member_pairs']==343)
check('current no historical raw/role/occupancy/loose exact',all(not x['historical_exact_matches']and not x['loose_exact_matches']for x in dedup['entries'])and not dedup['within_batch_pairs'][0]['exact_keys'])
v=get('visual-reading-boundary.json');check('26generated15actual11unviewed',len(list(OUT.glob('*.png')))==review['generated_current_png']==26 and len(v['viewed'])==review['actual_current_images_viewed']==15 and len(v['not_viewed_generated'])==review['unviewed_png']==11)
check('all11F01viewed and F02other11explicitunviewed',sum(Path(x['path']).name.startswith('F01-')for x in v['viewed'])==11 and all(Path(x['path']).name.startswith('F02-')for x in v['not_viewed_generated']))
check('1fullstudy pendingmax1/1coarsehold0 noindependentcredit',review['complete_whole_reference_studies']==review['pending_maximum']==review['held_zero']==1 and [x['credit_proposal_maximum']for x in review['cases']]==[1,0]and review['formal_credit_added']==0)
def bindings(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():bindings(w)
 elif isinstance(v,list):
  for w in v:bindings(w)
bindings(get('latest-independent-admissions.json'));bindings(get('carried-forward-pending.json'))
check('097first100 currentcarry only no repeat',get('latest-independent-admissions.json')['newly_notified_admission_097_F01']['first_bound_batch']==100 and get('session.json')['prior097_F01_admission_first_bound_100_carry_only_increment']==0 and get('carried-forward-pending.json')['097F01_accepted_first_100_carry_only'])
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_AND_COARSE_SCREENING_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
status='SEALED_F01_FULL_STUDY_MAX1_PENDING_F02_COARSE_EXCLUSION_ZERO'
session=get('session.json');session['status']=status;write('session.json',session)
write('active-checkpoint.json',{'batch':101,'status':status,'complete_whole_reference_studies':1,'actual_current_images_viewed':15,'unviewed_png':11,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'next_batch':102,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('101混合批次：F01沙岩tour_desert_2实际看全部11PNG/7观察，最多1完整相关候选待Main适用性/整家族独立审，非作者自准入。F02石tour_2只初步看4PNG（whole/cutaway/y0/y2）用途排除0，另11未看逐个绑定，不称2完整研究/26实际图。总26generated/15actual/11unviewed。\n\nF0113×15×11/DV3337，2145声明/1160记录=786非air374air/985省略；底共同工作房含floor2北高台磨具/南空unlitblast+smoker/东3seed桶，西3,1/2,5air入口但外2,1/2,5省略非air。主梯9,y1..5,3west到closed底trap9,6,3，落脚8,5,3木板/6air/7vine不是两格air。上同一住室两组上下铺=4床对(y6/8)，y7TOPoakslab是床支撑非第三住层；两2格短梯供上铺。第二主梯9,y6..10,7west到closed底trap9,11,7，西落脚8,10,7砂岩、上11..13air，接开敞围垛塔顶双箱；非14格同竖梯/第三闭工房。地面→上单床室双上铺→另内梯顶储藏组合对比064/071/092/095/097旧完整书面判断，是否普通下工上住近族或工坊相关不足仍待Main，不以圆塔/砂色/炉数/梯数通过。无smith/anvil/lava/true door，原hostilehusk用途边界明确。原3桶4chest各Seed/同表，4jigsaw原husk池，实体0。\n\nF0211×24×11/DV3337，2904声明/1577记录=829非air748air/1327省略，中心高窄塔/环廊；底普通炉和高层blast不自动称铁匠铺，无磨砧smith床梯，4skeletonsocket不是NPC或实际怪。两root2/max64/start0/surface/beardthin/expansionfalse，池各两个等权single rigid只研究_2不计_1，desert空processor/stone两0.2mossify原存不执行。所有原NBT/BE/entities/meta/context/state全层矩阵核对，F01关键route逐格原证据，F02matrix机器不称24层人工审。\n\n343历史pair+同源别名/rawroleoccupancy先排渲染，近占用/Jaccard不代替语义判断。097F01已100首次承接，本批carry增0；095F02已097首次承接，本批carry0。098F01max1待Main旧pending保持。COD4仍153差847；0产品制作/清单删除/原生验收/任务材料付款回执/中文指南针。无Java/Gradle/游戏/QA/唤醒音亮/用户实例存档/Jar/模型贴图/网络/提交发布。下一102固定本地继续，不等消费。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':status,'complete_whole_reference_studies':1,'preliminary_exclusions':1,'actual_current_images_viewed':15,'generated_png':26,'unviewed_png':11,'manual_full_observations':7,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':1,'formal_credit':0},ensure_ascii=False))

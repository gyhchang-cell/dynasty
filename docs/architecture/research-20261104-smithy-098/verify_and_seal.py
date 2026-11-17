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
  expect=[{'pos':b['pos'],'state':pal[b['state']],'original_block_entity':b.get('nbt')}for b in d['blocks']if b.get('nbt')or any(w in pal[b['state']]['Name']for w in ['door','furnace','smithing','grindstone','bed','lava','water','stairs','ladder','anvil','loom','cartography','crafting','stonecutter','cauldron'])];check(ident+' all functional/BE original including bytes',expect==restore(f['functional_states']))
  for md in [m for m in ctx['metadata']if m['id']==ident]:
   bb=z.read(md['member']);check(ident+' metadata '+md['member'],hashlib.sha256(bb).hexdigest()==md['sha256']and bb.decode()==md['original_text'])
  c=next(c for c in ctx['candidates']if c['id']==ident)
  for cc in c['contexts']:
   bb=z.read(cc['member']);check(ident+' source context '+cc['member'],hashlib.sha256(bb).hexdigest()==cc['sha256']and json.loads(bb)==cc['json'])
  check(ident+' pre-render exclusion identity',sr['eligible_for_new_source_study']and not sr['known_history']and not sr['historical_exact_matches']and not sr['within_batch_exact_matches']and sr['nbt_sha256']==a['nbt_sha256'])
  cells={tuple(b['pos']):pal[b['state']]for b in d['blocks']};mat=get(ident+'-original-layer-matrices.json')
  state_map={tuple(b['pos']):b['state']for b in d['blocks']};expected=[{'y':y,'rows_z_increasing':[[state_map.get((x,y,zz),-1)for x in range(d['size'][0])]for zz in range(d['size'][2])]}for y in range(d['size'][1])]
  check(ident+' every original full state layer matrix',mat['all_original_layers']==expected and mat['state_legend']=={str(i):s for i,s in enumerate(pal)})
  runs=get(ident+'-original-stair-runs.json')['original_bottom_stair_runs'];dirs={'north':(0,-1),'south':(0,1),'east':(1,0),'west':(-1,0)}
  for ri,run in enumerate(runs):
   check(ident+' stair pattern raw states '+str(ri),all(cells[tuple(t)]==v and v['Properties']['half']=='bottom'and v['Properties']['facing']==run['facing']for t,v in zip(run['positions'],run['states'])))
   dx,dz=dirs[run['facing']];check(ident+' stair step progression '+str(ri),all([t[0]+dx,t[1]+1,t[2]+dz]==u for t,u in zip(run['positions'],run['positions'][1:])))
   check(ident+' stair above original not generic air '+str(ri),all(cells.get(tuple(q['pos']),{'__omitted_original__':True})==q['state']for aa in run['above2_original']for q in aa))
  check(ident+' source missing context membership only',all(n not in z.namelist()for n in c['missing']))
  base='ati_stoneworks'if ident=='F01'else'ice_tribe';rootjson=next(cc['json']for cc in c['contexts']if cc['member']==f'data/ati_structures/worldgen/structure/{base}.json');pool=next(cc['json']for cc in c['contexts']if cc['member']==f'data/ati_structures/worldgen/template_pool/{base}.json')
  check(ident+' actual selected single root element',len(pool['elements'])==1 and pool['elements'][0]['weight']==1 and pool['elements'][0]['element']['location']=='ati_structures:'+base and pool['elements'][0]['element']['element_type']=='minecraft:single_pool_element'and pool['elements'][0]['element']['projection']=='rigid'and pool['fallback']=='minecraft:empty')
  check(ident+' actual root bounds and terrain behavior',rootjson['size']==(2 if ident=='F01'else 7)and rootjson['max_distance_from_center']==80 and rootjson['terrain_adaptation']=='none'and rootjson['project_start_to_heightmap']=='WORLD_SURFACE_WG'and rootjson['use_expansion_hack']is True and rootjson['start_height']=={'absolute':0})
  boxes=[b for b in d['blocks']if pal[b['state']]['Name']in ['minecraft:chest','minecraft:barrel']];check(ident+' original boxes no seed or prefilled inventory',all('LootTableSeed'not in b['nbt']and not b['nbt'].get('Items')for b in boxes))
  if ident=='F01':
   check('F01 exact volume/raw sparse breakdown',math.prod(d['size'])==110592 and len(pos)==110512 and r['air']==85673 and r['nonair']==24839 and f['omitted_positions']==80)
   check('F01 original no beds smith/anvil;5stonecutter',all(count[n]==0 for n in ['minecraft:smithing_table','minecraft:anvil','minecraft:damaged_anvil'])and not any(n.endswith('_bed')for n in count)and count['minecraft:stonecutter']==5)
   check('F01 original 3 fueled but unlit furnaces',count['minecraft:furnace']==3 and sorted(b['nbt']['Items'][0]['Count']for b in d['blocks']if pal[b['state']]['Name']=='minecraft:furnace')==[16,16,32]and all(pal[b['state']]['Properties']['lit']=='false'and b['nbt']['BurnTime']==b['nbt']['CookTime']==0 and b['nbt']['Items'][0]['id']=='minecraft:charcoal'and b['nbt']['Items'][0]['Slot']==1 for b in d['blocks']if pal[b['state']]['Name']=='minecraft:furnace'))
   check('F01 blast2empty unlit',count['minecraft:blast_furnace']==2 and all(b['nbt']['Items']==[]and pal[b['state']]['Properties']['lit']=='false'for b in d['blocks']if pal[b['state']]['Name']=='minecraft:blast_furnace'))
   check('F01 grind2 at high decorative cross-member original',count['minecraft:grindstone']==2 and cells[31,45,10]['Properties']=={'face':'wall','facing':'east'}and cells[36,45,10]['Properties']=={'face':'wall','facing':'west'}and cells[31,44,10]['Name']=='minecraft:air'and cells[31,43,10]['Name']=='minecraft:oak_wood')
   check('F01 exact fire water original',count['minecraft:lava']==5 and count['minecraft:lava_cauldron']==2 and count['minecraft:water']==313 and count['minecraft:campfire']==26 and all(pal[b['state']]['Properties']['lit']=='true'and b['nbt']['Items']==[]for b in d['blocks']if pal[b['state']]['Name']=='minecraft:campfire'))
   check('F01 exact source entities including malformed empty nbt',len(d['entities'])==37 and sum(e['nbt']=={}for e in d['entities'])==1 and Counter(e['nbt'].get('id')for e in d['entities'])==Counter({'minecraft:pillager':17,'minecraft:shulker':2,'minecraft:vindicator':11,'minecraft:evoker':2,'minecraft:minecart':2,None:1,'minecraft:illusioner':1,'minecraft:ravager':1}))
   check('F01 original40 boxes',len(boxes)==40 and count['minecraft:chest']==35 and count['minecraft:barrel']==5)
   check('F01 exact 5 connectors not11 studied buildings',count['minecraft:jigsaw']==5 and sum(b['nbt']['pool']=='ati_structures:stoneworks'for b in d['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw')==4)
   chain=get('F01-selected-route-and-hoist-states.json')['states'];check('F01 selected landing/hoist states original',all(cells.get(tuple(q['pos']),{'__omitted_original__':True})==q['state']for q in chain))
   check('F01 original monster override empty config not source enemies removed',rootjson['spawn_overrides']['monster']=={'bounding_box':'full','spawns':[]})
   side=next(cc['json']for cc in c['contexts']if cc['member'].endswith('/template_pool/stoneworks.json'));check('F01 sidepool11 original allsingle weights+projection',len(side['elements'])==11 and side['fallback']=='ati_structures:stoneworks'and side['name']=='ati_structures:ati_stoneworks'and all(e['weight']==1 and e['element']['element_type']=='minecraft:single_pool_element'and e['element']['processors']=='minecraft:empty'and e['element']['projection']==('terrain_matching'if i<6 else'rigid')for i,e in enumerate(side['elements'])))
   check('F01 low actual turning stairs2 sets with2air above',all(any(run['positions']==ps and all(q['state']['Name']=='minecraft:air'for aa in run['above2_original']for q in aa)for run in runs)for ps in [[[24,1,35],[23,2,35],[22,3,35],[21,4,35]],[[17,6,34],[17,7,33],[17,8,32],[17,9,31]]]))
  else:
   check('F02 exact volume/raw sparse breakdown',math.prod(d['size'])==28560 and len(pos)==12228 and r['air']==7532 and r['nonair']==4696 and f['omitted_positions']==16332)
   check('F02 ice-water distinct blocks exact',count['minecraft:packed_ice']==2537 and count['minecraft:blue_ice']==44 and count['minecraft:water']==805 and count['minecraft:snow_block']==49 and count['minecraft:snow']==49)
   check('F02 12 source residents not12buildings',len(d['entities'])==12 and Counter(e['nbt']['id']for e in d['entities'])==Counter({'minecraft:villager':11,'minecraft:iron_golem':1})and all(e['nbt']['VillagerData']['type']=='minecraft:plains'for e in d['entities']if e['nbt']['id']=='minecraft:villager'))
   check('F02 4 exact bedpairs',count['minecraft:light_gray_bed']==8 and all(cells[tuple(h)]['Properties']['part']=='head'and cells[tuple(t)]['Properties']['part']=='foot'and cells[tuple(h)]['Properties']['facing']==cells[tuple(t)]['Properties']['facing']==face for h,t,face in [([23,1,16],[23,1,17],'north'),([23,1,19],[24,1,19],'west'),([37,1,18],[36,1,18],'east'),([30,6,23],[30,6,22],'south')]))
   check('F02 original jukebox not playing/no audio interaction',count['minecraft:jukebox']==1 and cells[17,2,6]['Properties']['has_record']=='false'and next(b['nbt']for b in d['blocks']if b['pos']==[17,2,6])['IsPlaying']==0)
   check('F02 original stacked furnaces empty unlit',cells[35,4,19]['Name']=='minecraft:furnace'and cells[35,5,19]['Name']=='minecraft:blast_furnace'and all(b['nbt']['Items']==[]and b['nbt']['BurnTime']==b['nbt']['CookTime']==0 and pal[b['state']]['Properties']['lit']=='false'for b in d['blocks']if pal[b['state']]['Name']in ['minecraft:furnace','minecraft:blast_furnace']))
   check('F02 20 source boxes11empty no loot8references',len(boxes)==20 and sum('LootTable'not in b['nbt']for b in boxes)==11 and len(set(b['nbt']['LootTable']for b in boxes if 'LootTable'in b['nbt']))==8)
   check('F02 no jigsaw/anvil/lava original',count['minecraft:jigsaw']==count['minecraft:anvil']==count['minecraft:lava']==0)
   check('F02 source root villager in monster preserved not executed',rootjson['spawn_overrides']['monster']=={'bounding_box':'full','spawns':[{'type':'minecraft:villager','weight':1,'minCount':1,'maxCount':2}]})
for case,n in zip(review['cases'],[27,13]):
 check(case['id']+' seven actual observations',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'});check(case['id']+' actual image bindings count',len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact image binding',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' old written comparison unchanged '+f['path'],bind(f['path'])==f)
 check(case['id']+' no self admission/native clearance',case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
check('prior097 broader prefilter exact unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
dedup=get('dedup-evidence.json');check('337 history pairs not semantic total',screen['history_unique_archive_member_pairs']==dedup['historical_unique_local_archive_member_pairs']==337);check('current no exact old raw role occupancy',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('current pair no exact',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys'])
check('40 actual current PNG only',len(list(OUT.glob('F??-*.png')))==review['actual_current_images_viewed']==40);check('F01max1 F02hold0 currentformal0',review['pending_maximum']==1 and review['held_zero']==1 and review['formal_credit_added']==0 and [c['credit_proposal_maximum']for c in review['cases']]==[1,0])
def verify_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():verify_bindings(w)
 elif isinstance(v,list):
  for w in v:verify_bindings(w)
verify_bindings(get('latest-independent-admissions.json'));verify_bindings(get('carried-forward-pending.json'))
check('097F01 max1 pending retained no overwrite095 receipt',get('carried-forward-pending.json')['prior_pending_preserved'][0]['batch']==97 and get('carried-forward-pending.json')['prior_pending_preserved'][0]['maximum']==1 and get('carried-forward-pending.json')['current_pending'][0]['batch']==98 and get('carried-forward-pending.json')['prior095_F02_already_resolved_once_via_previous097_not_new_admission'])
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
status='SEALED_F01_MAX1_PENDING_RELEVANCE_FAMILY_F02_SETTLEMENT_HELD_ZERO';session=get('session.json');session['status']=status;write('session.json',session)
write('active-checkpoint.json',{'batch':98,'status':status,'source_bodies_studied':2,'actual_current_images_viewed':40,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'prior097_F01_pending_preserved':True,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':99,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('098 ATi stoneworks根L形厂屋/ice_tribe聚落，两源40实际PNG/14观察，F01最多1待Main完整相关适用/整空间家族审、F02hold0；本批formal0。337历史archive/member+同源字节别名/raw-role-occupancy先排除再渲染，当前无exact不代表语义通过。所有原NBT/每层矩阵/functional与BE/entities、原stairruns及上2格原状态保存核对。\n\nF0148³/DV3465声明110592，110512记录=24839非air85673显式air/80省略。北多层长厂厅接西南长翼，东南低切石/堆料场；两段真实低回折阶west24,1,35到21,4,35→20,5,35bottomslab及17..19,5,35木板/中rail，再north17,6,34到17,9,31→17,10,30bottomslab，均上2air。意图与原半阶/轨道碰撞/全楼导航分开。高y25+多阶为坡屋盖，不叫通顶梯；双wallgrind31/36,45,10相向连吊运横构/31,44air，不可叫可用高层砂轮室。低5stonecutter、3y10原炉slot1charcoal16/16/32非空/unlit、2y13blast空，lava5/lavacauldron2/water313/26lit空campfire、无床/smith/anvil。原35chest+5barrel全部无seed/无预填，有6无loot；原37entities含17pillager/11vindicator/2shulker/2evoker/2minecart/illusioner/ravager以及一条空nbt记录原留不补删，不叫工人/已生成。rootmonsterfullboxspawns空不移除源敌人。root单体权1single rigid empty，size2/max80/surface/terrainNONE/expansiontrue。原5jigsaw含四外围stoneworks、中心terrainlarge。外围11片前6terrainmatching后5rigid/empty/self fallback，内部name原ati_stoneworks，不修别名/不计11栋；terrainlarge2rigid/mossify20/self fallback。003steam_house旧完整文字及064/079实际读比较绑定，不重旧PNG/接受。F01仅根完整屋体的相关性/家族最多1待审，不是原生地形全装配或生产链完成。\n\nF0242×20×34/DV3465声明28560，12228记录=4696非air7532air/16332省略，最高非air14。多处冰住屋/岗位共同冰地桥台的整聚落，不一栋铺、不按12实体/岗位/房间计。packedice2537/blueice44/water805分类同蓝必须原名分；4properbedpairs分布三低处和东南上房。smith24,1,16与ceilinggrind12,4,25、东南上下炉35,4/5,19分散不硬连同屋。20容器7chest13barrel，11无loot空/其余8引用表全部无seed。11原villager type全plains/1golem；rootmonster类别fullboxvillager1..2w1只配置不加成13实例。选中single rigid/mossify20/empty fallback，size7/max80/terrainNONE/expansiontrue；原NBT无jigsaw，biometag仅frozenocean/deepfrozenocean；不当7栋或7片。jukebox无record/IsPlaying0、noteblocks/bell只读不播放。\n\n原Jar文件名V1.4.2，Forge/fabric metadata实际1.4.0且Forge displayName Structory，ATi/Alex credits、AllRightsReserved/pack15，差异原留。root/pool/biome/元信息及关键功能/实体读取，原全部表保存核哈希；部分loot完整读、未宣称每条权重/函数及519palette/157sign逐项全部人工解释，详context-reading-boundaries。不把单Jar vanilla表/processor缺失当环境缺失，不发奖/复制资源/修源。097F01最多1待审继续保留；095F02接受1已在097合并，098只carry不重算；COD4仍153差847。无Java/Gradle/游戏/QA/声音亮度唤醒/存档实例/共享Jar/产品/清单/任务/指南针/模型贴图/网络/提交推送。下一099继续固定本地完整相关来源；Main统一准入与删除任务。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':status,'source_bodies_studied':2,'actual_current_images_viewed':40,'manual_observations':14,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':1,'formal_credit':0},ensure_ascii=False))

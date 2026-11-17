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
  check(ident+' original entities0',d['entities']==[])
  route=get(ident+'-route-evidence.json')['selected_route_states'];check(ident+' recorded route states including omitted',all(cells.get(tuple(q['pos']),{'__omitted_original__':True})==q['state']for q in route))
  if ident=='F01':
   check('F01 sparse exact 2048/841/129/712/1207',math.prod(d['size'])==2048 and len(pos)==841 and r['air']==129 and r['nonair']==712 and f['omitted_positions']==1207)
   check('F01 inner 5 ladder states west',count['minecraft:ladder']==5 and all(cells[8,y,10]=={'Name':'minecraft:ladder','Properties':{'waterlogged':'false','facing':'west'}}for y in range(1,6)))
   check('F01 roof trapdoor bottom closed and west landing/air',cells[8,6,10]['Properties']['half']=='bottom'and cells[8,6,10]['Properties']['open']=='false'and cells[7,5,10]['Name']=='minecraft:spruce_planks'and all(cells[7,y,10]['Name']=='minecraft:air'for y in [6,7]))
   check('F01 one true door one orange bed pair',count['minecraft:mangrove_door']==2 and count['minecraft:orange_bed']==2 and cells[3,1,6]['Properties']['part']=='head'and cells[4,1,6]['Properties']['part']=='foot'and cells[3,1,6]['Properties']['facing']==cells[4,1,6]['Properties']['facing']=='west')
   check('F01 two original unlit empty blast',count['minecraft:blast_furnace']==2 and all(b['nbt']['Items']==[] and b['nbt']['BurnTime']==b['nbt']['CookTime']==0 and pal[b['state']]['Properties']['lit']=='false'for b in d['blocks']if pal[b['state']]['Name']=='minecraft:blast_furnace'))
   barrels=[b for b in d['blocks']if pal[b['state']]['Name']=='minecraft:barrel'];check('F01 7 original seeded barrels including2roof',len(barrels)==7 and all('LootTableSeed'in b['nbt']for b in barrels)and sum(b['pos'][1]==6 for b in barrels)==2)
   check('F01 source water14 lava0',count['minecraft:water']==14 and count['minecraft:lava']==0)
   j=next(b for b in d['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw');check('F01 mule pool original sand socket',j['pos']==[5,0,14]and j['nbt']['pool']=='trek:mobs/passive/mule'and j['nbt']['final_state']=='minecraft:sand')
   check('F01 decorative closed 10 fencegate windows y2y3',count['minecraft:spruce_fence_gate']==10 and all(b['pos'][1]in [2,3]and pal[b['state']]['Properties']['open']=='false'for b in d['blocks']if pal[b['state']]['Name']=='minecraft:spruce_fence_gate'))
  else:
   check('F02 all7560/897/6663 no omission',math.prod(d['size'])==len(pos)==7560 and r['air']==6663 and r['nonair']==897 and f['omitted_positions']==0)
   check('F02 original loom44 base y1 or y2',count['minecraft:loom']==44 and all(b['pos'][1]in [1,2]for b in d['blocks']if pal[b['state']]['Name']=='minecraft:loom'))
   check('F02 original unusual mixed source palette',all(count[n]==v for n,v in [('minecraft:melon',45),('minecraft:sponge',44),('minecraft:wet_sponge',29),('minecraft:green_glazed_terracotta',36),('minecraft:green_concrete_powder',36)]))
   check('F02 4 ladder states west',count['minecraft:ladder']==4 and all(cells[11,y,7]['Name']=='minecraft:ladder'and cells[11,y,7]['Properties']['facing']=='west'for y in range(3,7)))
   check('F02 upper landing TOP slab/air',cells[12,6,7]['Properties']['type']=='top'and cells[12,6,7]['Name']=='minecraft:spruce_slab'and all(cells[12,y,7]['Name']=='minecraft:air'for y in [7,8]))
   check('F02 one proper upper greenbed',count['minecraft:green_bed']==2 and cells[13,7,5]['Properties']['part']=='foot'and cells[14,7,5]['Properties']['part']=='head'and cells[13,7,5]['Properties']['facing']==cells[14,7,5]['Properties']['facing']=='east')
   check('F02 6 barrels empty no loot or seed',count['minecraft:barrel']==6 and all(b['nbt']=={'Items':[],'id':'minecraft:barrel'}for b in d['blocks']if pal[b['state']]['Name']=='minecraft:barrel'))
   check('F02 3 furnaces unlit empty',all(cells[x,3,4]['Properties']['lit']=='false'and next(b['nbt']for b in d['blocks']if b['pos']==[x,3,4])['Items']==[]for x in [4,5,6]))
   check('F02 3 unlit campfires not heat',count['minecraft:campfire']==3 and all(pal[b['state']]['Properties']['lit']=='false'and b['nbt']['Items']==[]for b in d['blocks']if pal[b['state']]['Name']=='minecraft:campfire'))
   check('F02 no anvil grind smith or lava',all(count[n]==0 for n in ['minecraft:smithing_table','minecraft:grindstone','minecraft:anvil','minecraft:damaged_anvil','minecraft:lava']))
   check('F02 bed阁 actual inner ladder not8 exterior ascending oaksteps',count['minecraft:oak_stairs']==8 and all(b['pos'][1]==2 for b in d['blocks']if pal[b['state']]['Name']=='minecraft:oak_stairs'))
  world=get('active-worldgen-reference-screen.json');check(ident+' all684 current worldgenJSON source bindings',len(world['checked_worldgen_json'])==684 and all(hashlib.sha256(z.read(x['member'])).hexdigest()==x['sha256']for x in world['checked_worldgen_json']))
  wr=next(x for x in world['rows']if x['id']==ident);found=[];mentions=[]
  for x in world['checked_worldgen_json']:
   bb=z.read(x['member']);j=json.loads(bb)
   if wr['location']in bb.decode():mentions.append(x['member'])
   if '/template_pool/'in x['member']:
    for e in j.get('elements',[]):
     if e.get('element',{}).get('location')==wr['location']:found.append({'member':x['member'],'element':e})
  check(ident+' selected and mention evidence equals current JSON',found==wr['actual_selected_pool_elements_found']and mentions==wr['exact_location_text_matches'])
  check(ident+' expected selected source binding',len(found)==(1 if ident=='F01'else 0))
  check(ident+' source missing exact membership',all(n not in z.namelist()for n in c['missing']))
for case,n in zip(review['cases'],[7,13]):
 check(case['id']+' seven actual observations',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'})
 check(case['id']+' actual image bindings count',len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact image binding',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' old written comparison binding '+f['path'],bind(f['path'])==f)
 check(case['id']+' no self admission or native clearance',case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
check('current broader prefilter binding',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
pref=get('broader-path-functional-prefilter.json');check('actual new machine scan counts no semanticcredit',pref['source_bodies_machine_scanned_not_studied']==2480 and len(pref['fixed_archives'])==40 and len(pref['rows'])==87 and len(pref['errors'])==0 and len(pref['same_archive_byte_aliases_excluded'])==37 and pref['building_credit_added']==pref['actual_visual_readings']==0)
check('corrected descriptive bound70 not inherited50', 'x/z5..70' in pref['selection']and 'Plural basenames' in pref['selection'])
dedup=get('dedup-evidence.json');check('335 historical pairs not semantic total',screen['history_unique_archive_member_pairs']==dedup['historical_unique_local_archive_member_pairs']==335)
check('current no exact historical raw role occupancy',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']))
check('current pair no exact',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys'])
check('20 actual current PNG only',len(list(OUT.glob('F??-*.png')))==review['actual_current_images_viewed']==20)
check('F01max1 F02hold0 currentformal0',review['pending_maximum']==1 and review['held_zero']==1 and review['formal_credit_added']==0 and [c['credit_proposal_maximum']for c in review['cases']]==[1,0])
def verify_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():verify_bindings(w)
 elif isinstance(v,list):
  for w in v:verify_bindings(w)
verify_bindings(get('latest-independent-admissions.json'));verify_bindings(get('carried-forward-pending.json'));verify_bindings(get('carried-forward-admission-resolution.json'))
check('095F02 resolved accepted1 once no currentcredit',get('latest-independent-admissions.json')['newly_notified_admission_095_F02']['increment']==get('carried-forward-admission-resolution.json')['resolved_once']['accepted_increment']==1 and get('carried-forward-pending.json')['prior095_F02_resolved_accepted_once']and get('carried-forward-pending.json')['current_pending'][0]['batch']==97)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
status='SEALED_F01_MAX1_PENDING_INDEPENDENT_REVIEW_F02_HELD_ZERO'
session=get('session.json');session['status']=status;write('session.json',session)
write('active-checkpoint.json',{'batch':97,'status':status,'source_bodies_studied':2,'actual_current_images_viewed':20,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'prior095_F02_resolved_accepted_once':True,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':98,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('097 两源20实际PNG/14观察。F01 Trek desert_ranch完整L形地面工住/内直梯上可用L形平顶储藏露台/东侧外水院，最多1待Main整空间家族独立审；F02旧jungle_village_1椭圆抬台单长工房+东端梯接小床阁，混材处理链/适用及近族边界未证hold0。当前formal0，不制作/删任务。\n\n新广路径机器预筛2480NBT/40固定Jar/87markers/0errors，37同源字节别名排除，335历史archive/member在渲染前去重，不是2480或87实际建筑研究。原description继承50的文字错误已在当前未封批修为实际70边界/原脚本精确条件并刷新screen绑定，未重跑扫描。两原NBT完整/每层state矩阵、全部BE/entities、route/元信息/上下文均保存核对。当前raw/role/occupancy无exact，不当语义自动通过。\n\nF0116×8×16/DV3337，841记录=712非air129air，声明2048中1207省略；base0/use1，L形屋顶floor5/use6。内梯8,y1..5,10west→bottom closed trap8,6,10及7,5,10木板落脚/7,6/7,7,10air；一床在地面北横段，双blast/切石/砧+壁砂轮在南窄段。两屋顶桶只是总7桶一部分/原Seed全保留，露台不是第二封闭工坊。有14水和含水阶、无岩浆；10关闭fencegate是成对y2/3窗饰，不是10院门。南jigsaw实际mule池/finalsand不叫NPC。root size2/max64/start0/surface/beardthin/expansionfalse，选中single1rigid/empty；isdesert1mandatory+15optional不推已安装。ownloot四池含原基础compass，不代表中文指南针接入；trash三池原读不生成奖。060/061/064/071/079/087旧完整判断实际读比较，仅保存绑定不旧PNG重审。\n\nF0221×20×18/DV3105全7560=897非air6663air/entities0；floor2/use3三炉北西、东六桶空无loot，内4梯到floor6TOPslab/use7一绿床阁；oak8bottomstairs全y2是桌椅非连续外登阶。44loom基圈以及melon45/sponge44/wetsponge29/greenglazed36/greenpowder36原混材不擅换成成品木石。原13空sign/3unlit campfires，不叫中文任务或火源。实际684worldgenJSON SHA核对本location0selected/0text；仅JSON范围不推永久未用。低双jigsaw原minecraft命名空间/一empty一actualvillage/jungle/jungle_village_1/finalair，后池单Jar缺，不编trek别名/选屋processor/root或环境缺失。\n\n095F02已Main接受1的65dbbf54…收据本097首次合并一次，解决096当时pending，不改封存096，不继续挂095待审，不转本批credit/COD4。COD4仍153差847、门槛未达，无Java/QA/游戏/声音亮度唤醒/原存档实例/共享Jar/产品/任务/指南针/主清单/贴图模型/提交推送。下一098继续固定本地完整相关来源；Main统一准入及删任务。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json']
write('RECEIPT.json',{'status':status,'source_bodies_studied':2,'actual_current_images_viewed':20,'manual_observations':14,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files})
print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':1,'formal_credit':0},ensure_ascii=False))

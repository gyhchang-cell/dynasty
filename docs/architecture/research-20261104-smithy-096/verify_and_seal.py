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
  expected=[{'y':y,'rows_z_increasing':[[next((b['state']for b in d['blocks']if b['pos']==[x,y,zz]),-1)for x in range(d['size'][0])]for zz in range(d['size'][2])]}for y in range(d['size'][1])]
  check(ident+' every original full state layer matrix',mat['all_original_layers']==expected and mat['state_legend']=={str(i):s for i,s in enumerate(pal)})
  check(ident+' no entities/bed/ladder/true door',d['entities']==[] and not any(any(w in n for w in ['bed','ladder','door'])for n in count))
  if ident=='F01':
   check('F01 smith and smoker original',count['minecraft:smithing_table']==1 and count['minecraft:smoker']==1 and cells[6,1,2]['Name']=='minecraft:smithing_table'and cells[5,1,2]['Properties']['lit']=='false')
   check('F01 3 original lit campfires and two barrels',count['minecraft:campfire']==3 and count['minecraft:barrel']==2 and all(pal[b['state']]['Properties']['lit']=='true'for b in d['blocks']if pal[b['state']]['Name']=='minecraft:campfire'))
   check('F01 all10 cobble stairs top at y6 not ladder',count['minecraft:cobblestone_stairs']==10 and all(b['pos'][1]==6 and pal[b['state']]['Properties']['half']=='top'for b in d['blocks']if pal[b['state']]['Name']=='minecraft:cobblestone_stairs'))
  else:
   check('F02 single empty unlit blast and barrel',count['minecraft:blast_furnace']==1 and count['minecraft:barrel']==1 and cells[5,0,4]['Properties']['lit']=='false'and next(b['nbt']for b in d['blocks']if b['pos']==[5,0,4])['Items']==[])
   debug=get('F02-debug-markers.json');groups=debug['groups'];actual=[b for b in d['blocks']if pal[b['state']]['Name']=='minecraft:structure_block']
   check('F02 all22 identical original DATA debug payloads bound',len(actual)==debug['source_count']==22 and len(groups)==1 and sorted(b['pos']for b in actual)==sorted(groups[0]['positions'])and all({'state':pal[b['state']],'nbt':b['nbt']}==groups[0]['original']for b in actual))
   check('F02 no actual spawner or descending stair',count['minecraft:spawner']==0 and all(pal[b['state']]['Properties']['half']=='top'for b in d['blocks']if 'stairs'in pal[b['state']]['Name']))
  screen2=get('active-worldgen-reference-screen.json');check(ident+' old template selected in0checkedpool/not runtime inference',next(r for r in screen2['rows']if r['id']==ident)['actual_selected_pool_elements_found']==[])
  check(ident+' actual current worldgen256 bindings and no old text',len(screen2['checked_worldgen_json'])==256 and all(hashlib.sha256(z.read(x['member'])).hexdigest()==x['sha256']and 'mushroom_village_old'not in z.read(x['member']).decode()for x in screen2['checked_worldgen_json']))
  for x in screen2['nested_loot_and_item_tag_presence']:check(ident+' nested reference actual presence '+x['member'],(x['member']in z.namelist())==x['present_in_single_fixed_jar'])
for case,n in zip(review['cases'],[14,13]):
 check(case['id']+' seven observations',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'});check(case['id']+' actual viewed image count',len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact image binding',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' unchanged saved comparison '+f['path'],bind(f['path'])==f)
 check(case['id']+' no self admission/native credit',case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
check('reused092 original prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
dedup=get('dedup-evidence.json');check('333 historical pairs not semantic total',screen['history_unique_archive_member_pairs']==dedup['historical_unique_local_archive_member_pairs']==333);check('two current no exact old or loose',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('two current not exact to each other',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys']);check('27 actual PNG only',len(list(OUT.glob('F??-*.png')))==review['actual_current_images_viewed']==27);check('both held0 no current pending',review['pending_maximum']==review['formal_credit_added']==0 and review['held_zero']==2 and all(c['credit_proposal_maximum']==0 for c in review['cases']))
def verify_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained independent binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():verify_bindings(w)
 elif isinstance(v,list):
  for w in v:verify_bindings(w)
verify_bindings(get('latest-independent-admissions.json'))
check('F01 exact all1782 positions',functional[0]['declared_volume']==1782 and functional[0]['stored_records']==1782 and functional[0]['omitted_positions']==0 and raw[0]['nonair']==550 and raw[0]['air']==1232)
check('F02 exact all1620 positions',functional[1]['declared_volume']==1620 and functional[1]['stored_records']==1620 and functional[1]['omitted_positions']==0 and raw[1]['nonair']==391 and raw[1]['air']==1229)
verify_bindings(get('carried-forward-pending.json'))
check('095F02 max1 pending retained no currentcredit',get('carried-forward-pending.json')['current_batch_new_pending']==0 and get('carried-forward-pending.json')['prior_unreviewed_proposals_preserved'][0]['batch']==95 and get('carried-forward-pending.json')['prior_unreviewed_proposals_preserved'][0]['maximum']==1)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
status='SEALED_TWO_OLD_SOURCE_BODIES_HELD_ZERO_RELEVANCE_OR_DEBUG_BOUNDARY'
session=get('session.json');session['status']=status;write('session.json',session)
write('active-checkpoint.json',{'batch':96,'status':status,'source_bodies_studied':2,'unqualified_for_complete_related_credit':2,'actual_current_images_viewed':27,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'prior095_F02_max1_pending_preserved':True,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':97,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('096 DA旧蘑菇工棚/高炉源体，两源27实际PNG/14观察，均hold0，不作为2完整相关铁匠铺信用。\n\n333历史archive/member与同源字节/raw-role-occupancy渲染前排除，当前原完整NBT与每层state矩阵/BE/entities保留核对。F019×22×9/DV3120全1782=550非air1232air，低开放/半围作业坪北smith/smoker/两桶，黄陶土187橙wool48高盖无梯/上工作房；低源职业棚适用不足与既有单地面工作空间0，3lit空campfires不是3经营层，10cobblestairs全y6TOP烟构不叫登楼。F029×20×9/DV3120全1620=391非air1229air，炉桶在原最低y0/缺脚下世界，22个y2DATA结构块同一空metadata/name/size0原payload和全部位置单独保存，不执行/清理后冒完工；原4playerhead非4NPC，无实际spawner，无梯/床。\n\n固定Jar当前256worldgenJSON实际SHA绑定，两个旧NBT location及old目录文字均0匹配/0selectedpool元素；只已查JSON范围，不断言bytecode未用或永久废弃。原jigsaw指现行houses池是8个modern small0..7/weight1 single rigid/houseprocessor，不含旧屋，不自动套当前selectedprocessor/根。F02内spawners接头指向资源在单Jar缺，非empty/NPC/已出怪；所有接头finalstructure_void保留。引用modernprocessor世界位置random蘑菇换色/灰wool→stem只配置已读未执行。ownbarrelloot全3池含FineWine两CustomPotionEffects原NBT/鱼tag/两vanilla嵌套loot，单Jar缺不推环境缺失，不基础potion冒变体/发奖励。\n\n086/092/093保存整屋判断实际读比较绑定，不看旧PNG/重跑接受。095F02最多1待Main独立审阅沿原收据保留不转/取消；此前092F02已接受1等旧累计保持不重计。COD4仍153差847，未达1000，无Java/游戏/制作/贴图模型/产品/清单/任务/指南针/原实例/共享Jar/声音亮度唤醒。下一097继续固定本地完整相关来源，不反复本批旧帽棚0。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':status,'source_bodies_studied':2,'unqualified_for_complete_related_credit':2,'actual_current_images_viewed':27,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':0,'formal_credit':0},ensure_ascii=False))

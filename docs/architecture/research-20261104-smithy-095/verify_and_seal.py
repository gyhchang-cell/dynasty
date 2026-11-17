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
  be=next(c for c in get('bed-and-route-evidence.json')['cases']if c['id']==ident)
  check(ident+' saved bed pairs original',all(cells[tuple(x['foot'])]==x['original_foot_state'] and cells[tuple(x['head'])]==x['original_head_state'] and x['original_head_state']['Properties']['part']=='head'for x in be['original_bed_pairs']))
  check(ident+' every original foot accounted',len(be['original_bed_pairs'])+len(be['unpaired_foot_states'])==sum(n.endswith('_bed')and v['Properties']['part']=='foot'for n,v in [(s['Name'],s)for s in cells.values()]))
  check(ident+' omitted positions distinct from explicit air',mat['omitted']==-1 and f['omitted_positions']>0)
  if ident=='F01':
   check('F01 six original paintings not six residents',len(d['entities'])==6 and all(e['nbt']['id']=='minecraft:painting'for e in d['entities']))
   check('F01 seven original bed pairs no orphan feet',len(be['original_bed_pairs'])==7 and be['unpaired_foot_states']==[])
   check('F01 single empty unlit blast',count['minecraft:blast_furnace']==1 and cells[8,3,3]['Properties']['lit']=='false'and next(b['nbt']for b in d['blocks']if b['pos']==[8,3,3])['Items']==[])
   check('F01 threewide sixstep internal stair',all(cells[x,y,z]['Name']=='minecraft:dark_oak_stairs'and cells[x,y,z]['Properties']['half']=='bottom'and cells[x,y,z]['Properties']['facing']=='south'for x in [15,16,17]for y,z in [(3,14),(4,15),(5,16),(6,17),(7,18),(8,19)]))
  else:
   check('F02 two armor stands and two paintings original',Counter(e['nbt']['id']for e in d['entities'])=={'minecraft:armor_stand':2,'minecraft:painting':2})
   check('F02 four pairs and three orphan feet not 11beds',len(be['original_bed_pairs'])==4 and sorted(x['foot']for x in be['unpaired_foot_states'])==[[13,3,9],[13,3,10],[13,3,11]])
   check('F02 full original six ladder chain and open headroom',all(cells[10,y,10]['Name']=='minecraft:ladder'and cells[10,y,10]['Properties']['facing']=='east'for y in range(3,9))and all(cells[10,y,10]['Name']=='minecraft:air'for y in range(9,12)))
   check('F02 upper landing and two internal room doors',cells[11,8,10]['Name']=='minecraft:dark_oak_wood'and all(cells[11,y,10]['Name']=='minecraft:air'for y in range(9,12))and cells[13,9,8]['Name']==cells[12,9,14]['Name']=='minecraft:spruce_door')
   check('F02 old cauldron level3 preserved not remapped',cells[19,3,17]=={'Name':'minecraft:cauldron','Properties':{'level':'3'}})
   for x in be['ladder_exit_and_upper_door_routes']:check('F02 retained route state '+str(x['pos']),cells.get(tuple(x['pos']),{'Name':'OMITTED'})==x['original_state'])
  for xx in [x for x in get('expanded-dependency-context.json')['rows']if x['id']==ident]:check(ident+' nested reference presence in fixed Jar '+xx['member'],(xx['member']in z.namelist())==xx['present_in_single_fixed_jar'])
for case,n in zip(review['cases'],[16,12]):
 check(case['id']+' seven observations',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'});check(case['id']+' actual viewed image count',len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact image binding',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' unchanged saved comparison '+f['path'],bind(f['path'])==f)
 check(case['id']+' no self admission/native credit',case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
check('reused092 original prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
dedup=get('dedup-evidence.json');check('331 historical pairs not semantic total',screen['history_unique_archive_member_pairs']==dedup['historical_unique_local_archive_member_pairs']==331);check('two current no exact old or loose',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('two current not exact to each other',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys']);check('28 actual PNG only',len(list(OUT.glob('F??-*.png')))==review['actual_current_images_viewed']==28);check('F01held0 F02max1 pending formal0',review['pending_maximum']==1 and review['formal_credit_added']==0 and review['held_zero']==1 and [c['credit_proposal_maximum']for c in review['cases']]==[0,1])
def verify_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained independent binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():verify_bindings(w)
 elif isinstance(v,list):
  for w in v:verify_bindings(w)
verify_bindings(get('latest-independent-admissions.json'))
check('F01 exact sparse counts',functional[0]['declared_volume']==14375 and functional[0]['stored_records']==4616 and functional[0]['omitted_positions']==9759 and raw[0]['nonair']==3143 and raw[0]['air']==1473)
check('F02 exact sparse counts',functional[1]['declared_volume']==9450 and functional[1]['stored_records']==3083 and functional[1]['omitted_positions']==6367 and raw[1]['nonair']==2196 and raw[1]['air']==887)
verify_bindings(get('carried-forward-admission-resolution.json'))
check('092F02 prior admission not counted again',get('carried-forward-admission-resolution.json')['already_bound_092F02_not_added_again']and get('carried-forward-admission-resolution.json')['new_formal_credit_claimed']==0)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
status='SEALED_TWO_COMPLETE_BODIES_F01_HOLD0_F02_MAX1_PENDING'
session=get('session.json');session['status']=status;write('session.json',session)
write('active-checkpoint.json',{'batch':95,'status':status,'source_bodies_studied':2,'complete_source_bodies':2,'actual_current_images_viewed':28,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'previous_admissions_retained_not_recounted':True,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':96,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('095 Simply Houses森林住宅/石匠复合屋，28实际PNG、14观察；F01相关性hold0，F02最多1待Main独立整栋语义审阅，当前正式0。\n\n331历史archive/member与同源字节/raw-role-occupancy渲染前排除；全部原NBT层state矩阵/BE/entities、元信息/选屋池/生成根/全部ownloot/tag和嵌套引用在单Jar有无记录保存验证。F0123×25×25/DV2586声明14375，4616records=3143非air1473air/9759省略，最高实构20；单空未lit高炉的多层住宅，底4+上2+阁1有效床对，6painting不是住户，炉/大房不充分相关性0。\n\nF0221×18×25/DV2586声明9450，3083records=2196非air887air/6367省略，最高实构15。西低盖地面石作/营火工棚接东闭式工住长屋；底北闭室内六段ladder10,3..8,10，出口10,9..11,10air/东落脚11,8,10实木上air，升到北西damagedanvil工作室，东门13,9,8通独立药室、南门12,9,14通单床/箱居室；两套不同工作标高与上T向隔间/原内门组织最多1待独立审查，不凭梯子、换石工或房数计数。低红床3对/上1对，另3孤foot x13,3,z9..11朝south对应处非head，保留不修/不说11床；旧cauldron level3不改现版水锅。2armorstand+2painting原局部/内部Pos和装束全保留，不是新增角色建模/4NPC，分类图未渲染实体。\n\n旧完整判断064同作者北热厅/东南主屋内折阶上住再梯储阁、071下工上住直阶、087双独立地面店外阶住、092所有工住在单上盖室，以及旧破宅/同层双翼记录已实际读写比较绑定，不重跑旧接受/不看旧PNG。两current独屋pool各1single/rigid/empty，rootforesthouse size5/stonemason2而两max8/start0/beardthin/expansionfalse；nested #minecraft:is_forest和vanilla weaponsmithloot单Jar缺不当环境缺失。酒水10entries明确effect/lore与Beer双setpotion原序，不拿基础potion冒NBT变体，不发奖励。\n\n既有092F02接受1沿094证据链保留不再增，其他旧接受累计不重置，COD4仍153差847。未达1000，无Java/游戏/制作/模型贴图/清单/任务/指南针/实例/共享Jar/声音亮度唤醒改动。下一096固定本地完整相关来源，先交付095F02最多1待审。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':status,'source_bodies_studied':2,'complete_source_bodies':2,'actual_current_images_viewed':28,'manual_observations':14,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':1,'formal_credit':0},ensure_ascii=False))

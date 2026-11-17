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
  expect=[{'pos':b['pos'],'state':pal[b['state']],'original_block_entity':b.get('nbt')}for b in d['blocks']if b.get('nbt')or any(w in pal[b['state']]['Name']for w in ['door','furnace','smithing','grindstone','bed','lava','water','stairs','ladder','anvil','loom','cartography','crafting','stonecutter'])];check(ident+' all functional/BE original including bytes',expect==restore(f['functional_states']))
  for md in [m for m in ctx['metadata']if m['id']==ident]:
   bb=z.read(md['member']);check(ident+' metadata '+md['member'],hashlib.sha256(bb).hexdigest()==md['sha256']and bb.decode()==md['original_text'])
  c=next(c for c in ctx['candidates']if c['id']==ident)
  for cc in c['contexts']:
   bb=z.read(cc['member']);check(ident+' source context '+cc['member'],hashlib.sha256(bb).hexdigest()==cc['sha256']and json.loads(bb)==cc['json'])
  check(ident+' pre-render exclusion identity',sr['eligible_for_new_source_study']and not sr['known_history']and not sr['historical_exact_matches']and not sr['within_batch_exact_matches']and sr['nbt_sha256']==a['nbt_sha256'])
  cells={tuple(b['pos']):pal[b['state']]for b in d['blocks']};mat=get(ident+'-original-layer-matrices.json')
  expected=[{'y':y,'rows_z_increasing':[[next((b['state']for b in d['blocks']if b['pos']==[x,y,zz]),-1)for x in range(d['size'][0])]for zz in range(d['size'][2])]}for y in range(d['size'][1])]
  check(ident+' every original full state layer matrix',mat['all_original_layers']==expected and mat['state_legend']=={str(i):s for i,s in enumerate(pal)})
  check(ident+' no original entities and no ladder',d['entities']==[] and count['minecraft:ladder']==0)
  if ident=='F01':
   check('F01 12 barrels and one chest',count['minecraft:barrel']==12 and count['minecraft:chest']==1)
   furnace=next(b['nbt']for b in d['blocks']if b['pos']==[3,4,9])
   check('F01 original blast charcoal fuel not empty',furnace['Items']==[{'Slot':1,'id':'minecraft:charcoal','Count':5}]and furnace['BurnTime']==furnace['CookTime']==0 and cells[3,4,9]['Properties']['lit']=='false')
   check('F01 doublewidth 3 bottomsteps',all(cells[x,y,z]['Name']=='minecraft:spruce_stairs'and cells[x,y,z]['Properties']['half']=='bottom'and cells[x,y,z]['Properties']['facing']=='east'for x,y in [(2,1),(3,2),(4,3)]for z in [3,4]))
  else:
   check('F02 two empty unlit blast furnaces',count['minecraft:blast_furnace']==2 and all(b['nbt']['Items']==[] and pal[b['state']]['Properties']['lit']=='false'for b in d['blocks']if pal[b['state']]['Name']=='minecraft:blast_furnace'))
   check('F02 lava not water cauldron and no bed',count['minecraft:lava_cauldron']==1 and not any('bed'in n or 'water'in n for n in count))
   check('F02 two distinct lit and unlit campfires',count['minecraft:campfire']==2 and cells[13,2,6]['Properties']['lit']=='true'and cells[5,3,3]['Properties']['lit']=='false')
for case,n in zip(review['cases'],[8,10]):
 check(case['id']+' seven observations',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'});check(case['id']+' actual viewed image count',len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact image binding',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' unchanged saved comparison '+f['path'],bind(f['path'])==f)
 check(case['id']+' no self admission/native credit',case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
check('reused092 original prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
dedup=get('dedup-evidence.json');check('329 historical pairs not semantic total',screen['history_unique_archive_member_pairs']==dedup['historical_unique_local_archive_member_pairs']==329);check('two current no exact old or loose',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('two current not exact to each other',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys']);check('18 actual PNG only',len(list(OUT.glob('F??-*.png')))==review['actual_current_images_viewed']==18);check('both held0 no current pending',review['pending_maximum']==review['formal_credit_added']==0 and review['held_zero']==2 and all(c['credit_proposal_maximum']==0 for c in review['cases']))
def verify_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained independent binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():verify_bindings(w)
 elif isinstance(v,list):
  for w in v:verify_bindings(w)
verify_bindings(get('latest-independent-admissions.json'))
check('F01 all explicit 1260 source positions',functional[0]['declared_volume']==1260 and functional[0]['stored_records']==1260 and functional[0]['omitted_positions']==0 and raw[0]['nonair']==428 and raw[0]['air']==832)
check('F02 all explicit 2535 source positions',functional[1]['declared_volume']==2535 and functional[1]['stored_records']==2535 and functional[1]['omitted_positions']==0 and raw[1]['nonair']==486 and raw[1]['air']==2049)
verify_bindings(get('carried-forward-admission-resolution.json'))
check('092F02 Main admitted1 once with current0',get('carried-forward-admission-resolution.json')['resolved_once']['accepted_increment']==1 and get('carried-forward-admission-resolution.json')['current_batch_new_pending']==0)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
status='SEALED_TWO_COMPLETE_BODIES_HELD_ZERO_RELEVANCE_OR_SHARED_WORKSPACE'
session=get('session.json');session['status']=status;write('session.json',session)
write('active-checkpoint.json',{'batch':94,'status':status,'source_bodies_studied':2,'complete_source_bodies':2,'actual_current_images_viewed':18,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'previous092_F02_main_admission_bound_once':1,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':95,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('094 T&T海边主屋/猪灵工坊，18实际PNG、14观察，两个完整来源均hold0。\n\n329历史archive/member与同源字节/raw-role-occupancy渲染前排除；全原NBT、全部层原state矩阵/BE/entities、元信息/选屋池/生成根/loot/tag/processor实际保存阅读核对。F019×10×14/DV3105全1260=428非air832air，双宽3底阶外梯接北平台/北门，地面露天桶与实填白石基，上室单床/含5木炭但未lit高炉，渔业住宅相关性不足和架高单室近族0。F0215×13×13/DV3465全2535=486非air2049air，单共享空间沿壁工作/箱及东外热台，原2空未lit高炉、内磨/外熔岩锅/两异lit营火，尖盖非二层；职业名、两炉、盖形不充分成立新的整体空间机制，0。\n\nF01 root size6/max80/beach+14optional，F02 root size2/max80/仅optional wythers savanna_basaltic_incursions，NPC spawn配置不是已生成实体；两选屋legacyrigid，F01empty/F02street_piglin六条完整规则已读未执行，worldwater条件与输入黑陶土分开，4个random.2不叫各最终20%。F01单Jar缺3vanilla引用非环境缺失；原种子/loot完整保存，不当实际付款发奖。\n\n主协调新独立收据092F02 SHA8cf17041bfb8b58f2baf488266ceb307c3512cba16234b26918ac793854ee0e8绑定一次接受1，原093待审记录历史不修改，当前新增正式信用0；所有既有接受保留未重跑。COD4仍153差847，未达1000，不提前制作、不改任务/指南针/清单，不Java/游戏/原实例/共享Jar/声音亮度唤醒。下一095继续固定本地完整相关语义不同案例。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':status,'source_bodies_studied':2,'complete_source_bodies':2,'actual_current_images_viewed':18,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':0,'formal_credit':0},ensure_ascii=False))

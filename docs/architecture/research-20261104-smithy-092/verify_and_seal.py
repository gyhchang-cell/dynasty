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
sources=get('sources.json')['candidates'];raw=get('raw-source-audit.json')['candidates'];review=get('manual-review.json');ctx=get('source-context.json');screen=get('pre-render-history-screen.json');functional=get('functional-evidence.json')['candidates'];expanded=get('expanded-context.json')
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
  for cc in [cc for cc in expanded['rows']if cc['id']==ident]:
   bb=z.read(cc['member']);check(ident+' expanded context '+cc['member'],hashlib.sha256(bb).hexdigest()==cc['sha256']and json.loads(bb)==cc['json'])
  check(ident+' pre-render exclusion identity',sr['eligible_for_new_source_study']and not sr['known_history']and not sr['historical_exact_matches']and not sr['within_batch_exact_matches']and sr['nbt_sha256']==a['nbt_sha256'])
  if ident=='F02':
   cells={tuple(b['pos']):pal[b['state']]for b in d['blocks']};mat=get('F02-functional-layer-matrices.json');check('F02 eight original layer matrices',mat['layers']==[{'y':y,'z_rows':[[cells.get((x,y,zz),{'Name':'OMITTED'})for x in range(11)]for zz in range(11)]}for y in [0,1,5,6,7,8,9,10]]);check('F02 full original center shaft',mat['original_center_shaft']==[{'y':y,'state':cells.get((5,y,5),{'Name':'OMITTED'})}for y in range(11)]);check('F02 5 ladders closed top trapdoor open upper air',all(cells[5,y,5]['Name']=='minecraft:ladder'for y in range(1,6))and cells[5,6,5]['Properties']['open']=='false'and cells[5,6,5]['Properties']['half']=='top'and cells[5,7,5]['Name']==cells[5,8,5]['Name']=='minecraft:air');check('F02 actual upper work site',cells[3,7,9]['Name']=='minecraft:smithing_table'and cells[1,8,3]['Name']=='minecraft:grindstone'and cells[1,8,7]['Name']=='minecraft:anvil');check('F02 six original empty unlit furnace BE',sum(1 for b in d['blocks']if pal[b['state']]['Name']in ['minecraft:furnace','minecraft:blast_furnace','minecraft:smoker']and pal[b['state']]['Properties']['lit']=='false'and b['nbt']['Items']==[]and b['nbt']['CookTime']==b['nbt']['BurnTime']==0)==6)
  else:
   cb=next(b for b in d['blocks']if b.get('nbt',{}).get('id')=='minecraft:campfire');check('F01 Paper byte array losslessly four zero bytes',cb['nbt']['Paper.StopCooking']==bytes(4));check('F01 no ladder or bed/furnace',not any(any(w in n for w in ['ladder','bed','furnace'])for n in count));check('F01 six lava states preserved including flow levels',count['minecraft:lava']==6 and {pal[b['state']]['Properties']['level']for b in d['blocks']if pal[b['state']]['Name']=='minecraft:lava'}=={'0','2','8'})
for case,n in zip(review['cases'],[11,9]):
 check(case['id']+' seven observations',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'});check(case['id']+' actual viewed image count',len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact image binding',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' unchanged saved comparison '+f['path'],bind(f['path'])==f)
 check(case['id']+' no self admission/native credit',case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
prefilter=get('name-negative-functional-prefilter.json');check('machine search metadata original binding',bind(prefilter['fixed_metadata']['path'])==prefilter['fixed_metadata']);check('1154 scans41 candidates12 fixed sources not visual credits',prefilter['source_bodies_machine_scanned_not_studied']==prefilter['selected_metadata_candidates']==1154 and len(prefilter['rows'])==41 and len(prefilter['fixed_archives'])==12 and prefilter['actual_visual_readings']==prefilter['building_credit_added']==0 and not prefilter['errors']);check('current prefilter bound before rendering',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
for f in prefilter['fixed_archives']:check('fixed machine-search source '+f['path'],bind(f['path'])==f)
dedup=get('dedup-evidence.json');check('325 historical pairs not semantic total',screen['history_unique_archive_member_pairs']==dedup['historical_unique_local_archive_member_pairs']==325);check('two current no exact old or loose',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('two current not exact to each other',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys']);check('20 actual PNG only',len(list(OUT.glob('F??-*.png')))==review['actual_current_images_viewed']==20);check('F01held0 F02max1pending not self accepted',review['pending_maximum']==review['held_zero']==1 and review['formal_credit_added']==0 and review['cases'][0]['credit_proposal_maximum']==0 and review['cases'][1]['credit_proposal_maximum']==1)
def verify_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained independent binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():verify_bindings(w)
 elif isinstance(v,list):
  for w in v:verify_bindings(w)
verify_bindings(get('latest-independent-admissions.json'))
check('F01 exact sparse counts',functional[0]['declared_volume']==1936 and functional[0]['stored_records']==1899 and functional[0]['omitted_positions']==37 and raw[0]['nonair']==612 and raw[0]['air']==1287);check('F02 exact sparse counts',functional[1]['declared_volume']==1331 and functional[1]['stored_records']==963 and functional[1]['omitted_positions']==368 and raw[1]['nonair']==481 and raw[1]['air']==482)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=get('session.json');session['status']='SEALED_F01_HELD_ZERO_F02_MAX1_PENDING';write('session.json',session)
write('active-checkpoint.json',{'batch':92,'status':'SEALED_CURRENT_RESEARCH_F02_MAX1_PENDING','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':20,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':93,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('092 名称不含铁匠的新功能筛选，DA/Trek两完整蘑菇工坊\n\n1154未收录且名称不含smith/forge/armorer的限界房屋候选/12固定本地Jar，原NBT哈希对7139旧metadata一致/0error，41工作方块标记候选。这是机器筛选非1154研究/41有效参考；浴场base/middle/top等组件不渲染、不计。选2源经325历史archive/member+全部同源别名/rawroleoccupancy前置排重，生成并实际查看20PNG/14观察，F01hold0，F02最多1待Main独立审核，正式0。\n\nF01 DA小蘑菇工房：11×16×11，1899record=612nonair1287air/37省略；南/东门同一地面室，西热端/北砧磨/东南smith，无梯床和上层工作板。6lava含level0/2/8且1在上构，不称6静源。北桶原loot无seed，高处损坏砧/空lit营火不是可用二层；单室热冷近族hold0。实际南side1→village_start(big0)/side0/finalair，不说empty/NPC/整村研究。DAAllRightsReserved仅研究不复制。processor红棕随机位于locationpredicate非input，lightgraywool→stem未执行。Paper.StopCooking原4zero bytes用可逆hex保存并反解核对，raw落盘失败后只恢复记录，无额外渲染/图片信用。\n\nF02 Trek独立蘑菇工住屋：11³，963record=481nonair482air/368省略，南低门→中心5,1..5,5竖梯→5,6,5 closed top盖→上室y7中心air。y6骨块整地板；东6原空/unlit炉（2blast/2smoker/2furnace）、西磨/砧/制图/织机、南smith/craft/桶、北1床，四壁工住周边布置/中央竖口散开。独立性依据是唯一菌柄竖向入口+全工作生活集中上盖，不是外形、上楼或工位数；对063/070/071/087既有下工上住/外阶/单低菌室完整保存判断比较后，最多1待审，仍可能工住单室近族hold。NPCactualplains8/1/1/finalboneblock补地板不是10人。root size1/max64/empty，不套村参数。\n\n根/池/processor/tag/自有loot全文已读；DAvanillaforesttag和fisher/butcher嵌套loot缺于单Jar单列，不冒环境缺失。Trekbiometags展开2mandatorybiomes+4optional，loot4池4原桶seed保存，未抽取付款。全部图是分类整格示意非纹理/碰撞/实机。旧079/080/087等独立接受累计保留不重跑重算；COD4仍153差847，门槛未达。无Java/制作/主清单或产品/原实例/共享Jar改动。下一093继续固定本地完整功能候选，先排精确/别名和语义近族，不等待收据消费。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_F01_HELD_ZERO_F02_MAX1_PENDING','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':20,'manual_observations':14,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':1,'formal_credit':0},ensure_ascii=False))

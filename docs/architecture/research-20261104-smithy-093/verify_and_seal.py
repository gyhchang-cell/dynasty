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
  for cc in [cc for cc in expanded['rows']if cc.get('id',ident)==ident]:
   bb=z.read(cc['member']);check(ident+' expanded context '+cc['member'],hashlib.sha256(bb).hexdigest()==cc['sha256']and json.loads(bb)==cc['json'])
  check(ident+' pre-render exclusion identity',sr['eligible_for_new_source_study']and not sr['known_history']and not sr['historical_exact_matches']and not sr['within_batch_exact_matches']and sr['nbt_sha256']==a['nbt_sha256'])
  cells={tuple(b['pos']):pal[b['state']]for b in d['blocks']};mat=next(m for m in get('functional-layer-matrices.json')if m['id']==ident)
  check(ident+' six full functional layer matrices',mat['functional_layers']==[{'y':y,'z_rows':[[cells.get((x,y,zz),{'Name':'OMITTED'})for x in range(d['size'][0])]for zz in range(d['size'][2])]}for y in [1,2,3,4,5,6]])
  check(ident+' no ladder or lava/water',not any(any(w in n for w in ['ladder','lava','water'])for n in count))
  if ident=='F01':
   check('F01 eight original item frames not humanoids',len(d['entities'])==8 and all(e['nbt']['id']=='minecraft:item_frame'for e in d['entities']))
   check('F01 source unnamespaced quartz separate',count['smooth_quartz']==126 and count['minecraft:smooth_quartz']==27)
   check('F01 original empty unlit blast',cells[6,2,8]['Properties']['lit']=='false'and next(b['nbt']for b in d['blocks']if tuple(b['pos'])==(6,2,8))['Items']==[])
  else:
   check('F02 no original entities',d['entities']==[])
   check('F02 source unnamespaced quartz separate',count['smooth_quartz']==83 and count['minecraft:smooth_quartz']==367)
   check('F02 3 stacked high campfires no furnace',count['minecraft:campfire']==3 and not any('furnace'in n for n in count))
for case,n in zip(review['cases'],[9,10]):
 check(case['id']+' seven observations',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'});check(case['id']+' actual viewed image count',len(case['images_actually_viewed'])==n)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact image binding',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' unchanged saved comparison '+f['path'],bind(f['path'])==f)
 check(case['id']+' no self admission/native credit',case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
check('reused092 original prefilter unchanged',bind(screen['prefilter_binding']['path'])==screen['prefilter_binding'])
dedup=get('dedup-evidence.json');check('327 historical pairs not semantic total',screen['history_unique_archive_member_pairs']==dedup['historical_unique_local_archive_member_pairs']==327);check('two current no exact old or loose',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('two current not exact to each other',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys']);check('19 actual PNG only',len(list(OUT.glob('F??-*.png')))==review['actual_current_images_viewed']==19);check('both held0 no current pending',review['pending_maximum']==review['formal_credit_added']==0 and review['held_zero']==2 and all(c['credit_proposal_maximum']==0 for c in review['cases']))
def verify_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained independent binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():verify_bindings(w)
 elif isinstance(v,list):
  for w in v:verify_bindings(w)
verify_bindings(get('latest-independent-admissions.json'))
check('F01 exact sparse counts',functional[0]['declared_volume']==4913 and functional[0]['stored_records']==4817 and functional[0]['omitted_positions']==96 and raw[0]['nonair']==977 and raw[0]['air']==3840)
check('F02 exact sparse counts',functional[1]['declared_volume']==6647 and functional[1]['stored_records']==6583 and functional[1]['omitted_positions']==64 and raw[1]['nonair']==1465 and raw[1]['air']==5118)
verify_bindings(get('carried-forward-pending.json'))
check('092F02 pending preserved no current credit',get('carried-forward-pending.json')['current_batch_new_pending']==0 and get('carried-forward-pending.json')['prior_unreviewed_proposals_preserved'][0]['maximum']==1)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=get('session.json');session['status']='SEALED_TWO_GROUND_MUSHROOM_FAMILIES_HELD_ZERO';write('session.json',session)
write('active-checkpoint.json',{'batch':93,'status':'SEALED_TWO_GROUND_MUSHROOM_FAMILIES_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':19,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':94,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('093 Trek两地面菌柄工住屋，既有同源家族均hold0\n\n重用092名称负向真实功能预筛，当前blust_furnace(原拼写)/grindstone两源经327历史archive/member+同源字节别名/rawroleoccupancy渲染前排除，实际查看19PNG/14观察，2完整原体均为070F01同源东门进地面工住单室近族，0当前待增/0正式信用。高炉/多铁砧/冠盖和新陈设不算独立；092F02菌柄竖梯至上盖主工住室仍最多1待Main独立审查，绑定保留，不移额度/不自认通过。\n\nF01 17³/DV3465，4817records=977nonair3840air/96省略，8原itemframes(1可见stoneslab+7不可见材料展示)不是8人物/产出；东门12,2/3,8进单室、西空未litblast6,2,8、北箱无seed、南单粉床、3高低损坏砧。F02 17×23×17，6583records=1465nonair5118air/64省略，东门13,2/3,8→原连续air到西磨5,2,8，北箱/南单黑床，无炉；3叠高营火是烟饰非3炉。两使用y2，无梯到高冠盖，未带namespace smooth_quartz分别126/83与namespaced27/367分开保留未修。\n\n两选屋weight2 legacyrigid/empty；housefallback原trek plains terminators池4元素/terrainmatching/street_plains引用已保存，规则未展开不套选屋。root size6/max80/mushroomfields/start0/beardthin/expansionhacktrue，不套092独屋size1/max64。两原NPCsocket指minecraft:village/mushroom/villagers，单Jar缺；同Jar另trek池nitwit1/baby1/unemployed10实际另存，命名空间不自动alias/修复，也不称12NPC。vanilla armorer/weaponsmith loot缺于单modJar不冒环境缺失，保留原箱无seed。\n\n全部原NBT实体/BE、六层全功能矩阵/分类视图/metadata与资源上下文保存验证，不是原生纹理/门半格碰撞或skin验收。无Java/制作/模型贴图/任务指南针/清单或产品/原实例/共享Jar改动。既有Main079/080/087等累计保留不重跑，COD4仍153差847，1000门槛未达/全任务未完成。下一094继续固定本地真实完整功能且空间不同来源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_TWO_GROUND_MUSHROOM_FAMILIES_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':19,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending_maximum':0,'formal_credit':0},ensure_ascii=False))

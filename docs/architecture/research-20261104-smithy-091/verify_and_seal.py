"""Current-batch source/evidence integrity, no historical admission rerun."""
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
def write(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def get(n):return json.loads((OUT/n).read_text())
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
sources=get('sources.json')['candidates'];raw=get('raw-source-audit.json')['candidates'];review=get('manual-review.json');context=get('source-context.json');screen=get('pre-render-history-screen.json');functional=get('functional-evidence.json')['candidates'];matrices=get('functional-layer-matrices.json')
check('2 aligned current bodies',len(sources)==len(raw)==len(review['cases'])==len(functional)==2 and [a['id']for a in sources]==[a['id']for a in raw]==[a['id']for a in review['cases']])
check('fixed archive binding',bind(sources[0]['source_archive'])==screen['fixed_archive'])
with ZipFile(sources[0]['source_archive'])as z:
 md=context['metadata'];bb=z.read(md['member']);check('original metadata exact',hashlib.sha256(bb).hexdigest()==md['sha256']and bb.decode()==md['original_text'])
 for a,r,f,mat in zip(sources,raw,functional,matrices):
  ident=a['id'];b=z.read(a['member']);d=read(b);pal=d.get('palette')or d['palettes'][0];pos=[tuple(x['pos'])for x in d['blocks']];count=Counter(pal[x['state']]['Name']for x in d['blocks'])
  check(ident+' compressed original sha',hashlib.sha256(b).hexdigest()==a['nbt_sha256']==r['nbt_sha256']);check(ident+' entire decoded original preserved',d==r['nbt_decoded_original']);check(ident+' version size',d['DataVersion']==a['DataVersion']and d['size']==a['size']);check(ident+' all positions unique',len(pos)==len(set(pos)));check(ident+' all positions in bounds',all(all(0<=p[i]<d['size'][i]for i in range(3))for p in pos));check(ident+' palette indices valid',all(0<=x['state']<len(pal)for x in d['blocks']));check(ident+' materials exact',dict(count)==r['material_counts']);check(ident+' air nonair exact',sum(v for k,v in count.items()if k in AIR)==r['air']and len(pos)-r['air']==r['nonair']);check(ident+' sparse record volume separate',f['stored_records']==len(pos)and f['declared_volume']==math.prod(d['size'])and f['omitted_positions']==math.prod(d['size'])-len(pos));check(ident+' all entities preserved',f['entities_original']==d.get('entities',[]))
  expect=[{'pos':b['pos'],'state':pal[b['state']],'original_block_entity':b.get('nbt')}for b in d['blocks']if b.get('nbt')or any(w in pal[b['state']]['Name']for w in ['door','furnace','smithing','grindstone','bed','lava','water','stairs'])];check(ident+' all functional states blockentities preserved',expect==f['functional_states'])
  cells={tuple(b['pos']):pal[b['state']]for b in d['blocks']}
  check(ident+' original complete functional matrices',mat['layers_y2_3_4']==[{'y':y,'z_rows':[[cells.get((x,y,zz),{'Name':'OMITTED'})for x in range(d['size'][0])]for zz in range(d['size'][2])]}for y in [2,3,4]])
  sr=next(x for x in screen['rows']if x['canonical_member']==a['member']);check(ident+' pre-render identity and exact exclusions',sr['eligible_for_new_source_study']and not sr['known_history']and not sr['exact_history_matches']and not sr['within_batch_exact']and sr['original_nbt_sha256']==a['nbt_sha256'])
 for c in context['candidates']:
  for f in c['contexts']:
   b=z.read(f['member']);check(c['id']+' original context '+f['member'],hashlib.sha256(b).hexdigest()==f['sha256']and json.loads(b)==f['json'])
 for f in get('expanded-context.json')+[get('biome-collection-expanded.json')]:
  b=z.read(f['member']);check('expanded context '+f['member'],hashlib.sha256(b).hexdigest()==f['sha256']and json.loads(b)==f['json'])
 for c in context['candidates']:
  house=next(a for a in c['contexts']if a['member'].endswith('/houses.json'));elements=[a for a in house['json']['elements']if a['element'].get('location')==c['location']]
  check(c['id']+' actual selected weight single element',len(elements)==1 and elements[0]['weight']==1 and elements[0]['element']['element_type']=='minecraft:single_pool_element')
  v=next(a for a in c['contexts']if a['member'].endswith('/vines.json'))['json'];check(c['id']+' connector is feature not NPC',len(v['elements'])==1 and v['elements'][0]['element']['element_type']=='minecraft:feature_pool_element')
for case in review['cases']:
 check(case['id']+' seven actual observation topics',set(case['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'})
 check(case['id']+' nine actual viewed PNG',len(case['images_actually_viewed'])==9)
 for f in case['images_actually_viewed']:
  check(Path(f['path']).name+' exact bound PNG',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' valid PNG',True)
 for f in case['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(case['id']+' original comparison binding '+f['path'],bind(f['path'])==f)
 check(case['id']+' held0 no self-admission',case['credit_proposal_maximum']==case['formal_credit_added']==0 and case['native_acceptance']is False)
for f in get('protected-inputs.json')['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=get('dedup-evidence.json');check('323 current historical identities not credits',dedup['historical_unique_local_archive_member_pairs']==screen['history_unique_archive_member_pairs']==323);check('reuse 090 prior prefilter unchanged',bind(screen['reused_prior_prefilter_binding']['path'])==screen['reused_prior_prefilter_binding']);check('no old exact or loose exact',all(not a['historical_exact_matches']and not a['loose_exact_matches']for a in dedup['entries']));check('no current pair exact',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys']);check('18 current actual PNG',len(list(OUT.glob('F??-*.png')))==review['actual_current_images_viewed']==18);check('2 complete bodies held0',review['whole_smithy_bodies_studied']==review['held_zero']==2 and review['pending_maximum']==review['formal_credit_added']==0)
latest=get('latest-independent-admissions.json')
def check_bindings(v):
 if isinstance(v,dict):
  if set(['path','sha256','bytes'])<=v.keys():check('retained independent binding '+v['path'],bind(v['path'])==v)
  else:
   for w in v.values():check_bindings(w)
 elif isinstance(v,list):
  for w in v:check_bindings(w)
check_bindings(latest)
check('F01 exact sparse breakdown',len(raw[0]['nbt_decoded_original']['blocks'])==423 and raw[0]['nonair']==381 and raw[0]['air']==42 and functional[0]['omitted_positions']==193)
check('F02 exact sparse breakdown',len(raw[1]['nbt_decoded_original']['blocks'])==646 and raw[1]['nonair']==549 and raw[1]['air']==97 and functional[1]['omitted_positions']==344)
check('F01 no invented furnace chest lava',not any(any(w in n for w in ['furnace','chest','lava','water','bed'])for n in raw[0]['material_counts']))
check('F02 one hot trough two grindstones',raw[1]['material_counts']['minecraft:lava']==2 and raw[1]['material_counts']['minecraft:grindstone']==2 and raw[1]['material_counts']['minecraft:chest']==1)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=get('session.json');session['status']='SEALED_TWO_EXISTING_FAMILIES_HELD_ZERO';write('session.json',session)
write('active-checkpoint.json',{'batch':91,'status':'SEALED_CURRENT_STUDY_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':18,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':92,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('091 RS沼泽工具匠/武器匠：两个既有空间族，均hold0\n\n323历史archive/member+同源全部字节别名/rawroleoccupancy在渲染前排除，重用090预筛并只比较当前2源，不重跑旧接受。2完整原体/18实际查看PNG/14观察，无待增、正式0。F01西门短L冷工屋/东南工具台，无箱热床；与068/084冷L族近，泥根高盖不单独增信用。F02南外双熔岩一槽/外砂轮→南门→北小冷室/内砂轮与北西箱，属057/067前热后冷近族；无床/阁层/炉/水，不把根盖或门方向计独立。\n\nF01 8×11×7/DV3465，616体积423记录=381非air42air/193省略；F02 9×11×10，990体积646记录=549非air97air/344省略。底0/1实泥根不是吊脚二层，地板2/使用3。高处bottomstairs为屋盖/炉构细部非连续楼梯；分类灰图泥根非石，半块/根孔隙/门实际碰撞未验。两室内jigsaw实际swamp/vines feature→placed placement[]→configured RSstructure_vines attempts10/length3/xzrange4/heightrange10，非NPC/待补房。\n\nRS7.1.19Forge/TelepathicGrunt/LGPLv3，实际选屋weight1 single_pool_element/rigid/mossify5规则+voidprocessor，不套legacy。中心pathrandomizer完整上下文另存，不当选屋处理；rootcustomsize6/地形radius2range22/biomeradius1/start0/boxhacktrue，无maxdistance不套116。swampcollection2mandatory+2optional tag，不冒自然生成。F02原lootseed保留/vanillaloot不在单modJar不等环境缺失。\n\n已接受079/080/087及之前收据累计绑定不重跑/重算，不给COD4加分，COD4仍153差847。1000门槛未达，无制作、Java、原实例/存档/共享Jar/模型贴图/任务指南针/主清单改动。下一批092继续固定本地空间不同完整来源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json']
write('RECEIPT.json',{'status':'SEALED_TWO_EXISTING_FAMILIES_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':18,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files})
print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':0,'formal_credit':0},ensure_ascii=False))

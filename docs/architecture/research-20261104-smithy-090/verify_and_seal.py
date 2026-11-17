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
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
checks=[]
def check(n,v):
 checks.append({'name':n,'passed':bool(v)})
 if not v:raise AssertionError(n)
s=json.loads((OUT/'sources.json').read_text())['candidates'];r=json.loads((OUT/'raw-source-audit.json').read_text())['candidates'];review=json.loads((OUT/'manual-review.json').read_text());context=json.loads((OUT/'source-context.json').read_text())
check('two raw/source/review aligned',len(s)==len(r)==len(review['cases'])==2 and [a['id']for a in s]==[a['id']for a in r]==[a['id']for a in review['cases']])
with ZipFile(s[0]['source_archive'])as z:
 check('fixed source archive SHA',bind(s[0]['source_archive'])['sha256']==s[0]['source_archive_sha256'])
 check('original metadata SHA',hashlib.sha256(z.read(context['metadata']['member'])).hexdigest()==context['metadata']['sha256'])
 check('original metadata text',z.read(context['metadata']['member']).decode()==context['metadata']['original_text'])
 f=json.loads((OUT/'secondary-metadata.json').read_text());bb=z.read(f['member']);check('secondary metadata intact',hashlib.sha256(bb).hexdigest()==f['sha256']and json.loads(bb)==f['json'])
 for a,b in zip(s,r):
  raw=z.read(a['member']);d=read(raw);pal=d.get('palette')or d['palettes'][0];pos=[tuple(x['pos'])for x in d['blocks']]
  check(a['id']+' raw hash',hashlib.sha256(raw).hexdigest()==a['nbt_sha256']==b['nbt_sha256']);check(a['id']+' decoded original',d==b['nbt_decoded_original']);check(a['id']+' unique positions',len(pos)==len(set(pos)));check(a['id']+' bounds',all(all(0<=p[i]<d['size'][i]for i in range(3))for p in pos));check(a['id']+' indices',all(0<=x['state']<len(pal)for x in d['blocks']));check(a['id']+' size/version',d['size']==a['size']and d['DataVersion']==a['DataVersion']);check(a['id']+' original entities preserved',d.get('entities',[])==b['nbt_decoded_original'].get('entities',[]))
  counts=Counter(pal[x['state']]['Name']for x in d['blocks']);check(a['id']+' all materials',dict(counts)==b['material_counts']);check(a['id']+' air nonair',sum(v for k,v in counts.items()if k in AIR)==b['air']and len(pos)-b['air']==b['nonair']);check(a['id']+' sparse accounting',len(pos)+ (math.prod(d['size'])-len(pos))==math.prod(d['size']))
 for a in context['candidates']:
  for c in a['contexts']:
   bb=z.read(c['member']);check(a['id']+' context '+c['member'],hashlib.sha256(bb).hexdigest()==c['sha256']and json.loads(bb)==c['json'])
 for c in json.loads((OUT/'biome-collection-context.json').read_text()):check(c['member'],hashlib.sha256(z.read(c['member'])).hexdigest()==c['sha256']and json.loads(z.read(c['member']))==c['json'])
for c in review['cases']:
 check(c['id']+' seven topics',set(c['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'})
 for f in c['images_actually_viewed']:
  check(Path(f['path']).name+' bound image',bind(f['path'])==f)
  with Image.open(f['path'])as im:im.verify()
  check(Path(f['path']).name+' PNG valid',True)
 for f in c['semantic_family_comparison']['saved_existing_judgments_reused_not_reaccepted']:check(c['id']+' unchanged comparison '+f['path'],bind(f['path'])==f)
 check(c['id']+' zero self admission',c['formal_credit_added']==0 and c['native_acceptance']is False)
check('14 actually viewed bindings',sum(len(c['images_actually_viewed'])for c in review['cases'])==14)
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('321 history source pairs',dedup['historical_unique_local_archive_member_pairs']==321);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one pair no exact duplication',len(dedup['within_batch_pairs'])==1 and all(not p['exact_keys']for p in dedup['within_batch_pairs']));check('two whole both held formal0',review['pending_maximum']==0 and review['held_zero']==2 and review['whole_smithy_bodies_studied']==2 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 321',screen['history_unique_archive_member_pairs']==321)
for a in s:
 row=next(x for x in screen['rows']if x['canonical_member']==a['member'])
 check(a['id']+' pre-render history excluded',row['eligible_for_new_source_study']and not row['known_history']and row['original_nbt_sha256']==a['nbt_sha256'])
latest=json.loads((OUT/'latest-independent-admissions.json').read_text())
for key in ['receipt','clarification']:
 f=latest[key];check('independent main '+key+' binding',bind(f['path'])==f)
f=latest['newly_notified_admission_062']['receipt'];check('independent062 saved unchanged',bind(f['path'])==f)
f=latest['newly_notified_admission_066_F01']['receipt'];check('independent066 F01 saved unchanged',bind(f['path'])==f)
for key in ['newly_notified_admission_080_F01','newly_notified_admission_079_F01']:
 f=latest[key]['receipt'];check('independent '+key+' unchanged',bind(f['path'])==f)
check('current batch not self admitted',latest['current_batch_formal_credit_added']==0)
for key in ['newly_notified_admission_087_F01','newly_notified_admission_087_F02']:
 f=latest[key]['receipt'];check('independent '+key+' unchanged',bind(f['path'])==f)
check('14 generated actual PNG',len(list(OUT.glob('F??-*.png')))==14 and review['actual_current_images_viewed']==14)
with ZipFile(s[0]['source_archive'])as z:
 c=json.loads((OUT/'biome-collection-expanded.json').read_text());b=z.read(c['member']);check('biome collection original intact',hashlib.sha256(b).hexdigest()==c['sha256']and json.loads(b)==c['json'])
check('F01 exact sparse accounting',math.prod(r[0]['size'])==448 and len(r[0]['nbt_decoded_original']['blocks'])==220 and r[0]['air']==44 and r[0]['nonair']==176)
check('F02 exact sparse accounting',math.prod(r[1]['size'])==392 and len(r[1]['nbt_decoded_original']['blocks'])==250 and r[1]['air']==31 and r[1]['nonair']==219)
check('F02 37 original pressure placeholders',r[1]['material_counts']['minecraft:stone_pressure_plate']==37)
c=json.loads((OUT/'pre-render-current-fingerprint-screen.json').read_text());check('58 keyword prefilter metadata not credit',len(c['rows'])==c['candidates_screened']==58 and c['whole_reference_credit']==0 and c['actual_visual_readings']==0)
check('prefilter metadata original binding',bind(c['fixed_metadata_binding']['path'])['sha256']==c['fixed_metadata_binding']['sha256'])
for f in c['fixed_archives']:check('prefilter fixed source archive '+f['path'],bind(f['path'])==f)
check('5 old exact',sum(bool(a['historical_exact_matches']or a['alias_history_matches'])for a in c['rows'])==5)
check('14 current only exact',sum(bool(a['earlier_current_exact_matches'])and not a['historical_exact_matches']and not a['alias_history_matches']for a in c['rows'])==14)
for a in s:
 row=next(v for v in c['rows']if v['member']==a['member']and v['source_archive']==a['source_archive']);check(a['id']+' selected before render no exact',not row['historical_exact_matches']and not row['alias_history_matches']and not row['earlier_current_exact_matches']and row['nbt_sha256']==a['nbt_sha256'])
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_BOTH_HELD_ZERO';write('session.json',session)
write('active-checkpoint.json',{'batch':90,'status':'SEALED_TWO_SINGLE_ARMORER_WORKROOM_FAMILIES_HELD_ZERO','current_keyword_candidates_screened_not_credit':58,'source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':91,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('090 固定本地58关键词预筛与RS巨型针叶林两单室甲匠屋\n\n58是当前机器候选，不是58参考。321历史/全部同源别名+rawroleoccupancy在渲染前排：5旧精确、14仅本轮较早候选精确；余39无这些精确仍含misc/残迹/室内组件和可能近族。只选gianttaiga armorerhouse1/2生成并实际查看14PNG、14观察，2完整小屋但都属既有单室族hold0，无待增/正式0。预筛与已保存旧指纹比较不是重跑旧接受。\n\nF01 8×8×7/DV3465，448体积仅220记录=176nonair+44air/另228省略；西门公共室/南西箱/东炉烟构，长spruceplanks全块gable。F02 7×8×7/DV3465，392体积仅250记录=219nonair+31air/另142省略；北门公共室/东南单blast，无箱/NPC/床。37stonepressureplate在y3/5/6/7为原待随机饰位，不是密实石坡盖；真实屋盖木板+26木slab。选屋mossify12rules实际读/保存含.01button/.01bottomcobbleslab/.99air占位替换，未执行，不把源示意当处理后实机。单室不靠长坡/三窗/无箱/材质变化计独立。\n\n原source primary RS7.1.19+1.20.1Forge/TelepathicGrunt/LGPLv3，secondary实际packmetadata format15而非fabric。两houseweight2legacyrigid/mossify12rules；towncenter道路pathrandomizer16rules只上下文不替代选屋。实际customgenericjigsaw root size6/validbiomeradius1/terrainheightradius2/allowedrange22/start0/beardthin/useboundingboxhacktrue，无显式maxdistance不套116。根tag实际collection展开oldpine/oldspruce2mandatory+14optional条目、其中1重复/13distinct。F01原lootseed/炉空、F02无loot，原入口finalstairs仅facing不补原属性；sparse省略不冒air/地形实测。\n\nMain087F02收据77c205d9…新增1仅COD3NPC01接入latest，和087F01各1只增2不重算F01；079/080/087旧接受不重跑。COD4仍153差847/1000未达，无Java/制作/清单删除。下一批091优先新的完整相关空间，排近族、misc和残迹。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_TWO_SINGLE_ARMORER_WORKROOM_FAMILIES_HELD_ZERO','current_keyword_candidates_screened_not_credit':58,'source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':14,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':0,'held_zero':2,'formal_credit':0},ensure_ascii=False))

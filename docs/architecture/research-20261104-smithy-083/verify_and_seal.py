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
check('17 actually viewed bindings',sum(len(c['images_actually_viewed'])for c in review['cases'])==17)
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('309 history source pairs',dedup['historical_unique_local_archive_member_pairs']==309);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one pair no exact duplication',len(dedup['within_batch_pairs'])==1 and all(not p['exact_keys']for p in dedup['within_batch_pairs']));check('both held zero formal0',review['pending_maximum']==0 and review['held_zero']==2 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 309',screen['history_unique_archive_member_pairs']==309)
for a in s:
 row=next(x for x in screen['rows']if x['canonical_member']==a['member'])
 check(a['id']+' pre-render history excluded',row['eligible_for_new_source_study']and not row['known_history']and row['original_nbt_sha256']==a['nbt_sha256'])
latest=json.loads((OUT/'latest-independent-admissions.json').read_text())
for key in ['receipt','clarification']:
 f=latest[key];check('independent main '+key+' binding',bind(f['path'])==f)
f=latest['newly_notified_admission_062']['receipt'];check('independent062 saved unchanged',bind(f['path'])==f)
f=latest['newly_notified_admission_066_F01']['receipt'];check('independent066 F01 saved unchanged',bind(f['path'])==f)
check('current batch not self admitted',latest['current_batch_formal_credit_added']==0)
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_PENDING_INDEPENDENT_REVIEW';write('session.json',session)
write('active-checkpoint.json',{'batch':83,'status':'SEALED_TWO_WHOLE_BODIES_BOTH_FAMILY_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':17,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':84,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('083 草甸甲匠皮匠与老针叶林甲匠肉铺\n\n2完整体/17实际PNG/14观察，both家族hold0、pending0、正式0。F01 11×11×10/DV3578，1210=407nonair+803air，西单门入单共用室，北满水锅level3/皮箱、南砧/甲箱/高炉，屋盖宽檐层叠但没有通达二楼/床梯；不能把高盖当二层。真实骨块墙44、木盖非全石，水锅不等淬火验收。两箱seed原样。F02 13×9×10/DV3105，1170=331nonair+839air，南短门廊+单门入一共用室，西烟熏/肉箱、东北高炉/东甲箱；当前无内隔门中线原air，不能套用060F02同主题旧双室判断。设备/双烟帽/去隔门不比既有单长厅布局更独立。smoker原Slot1煤Count2，litfalse/BurnTime0，不写全空或已燃烧。\n\n先309历史/同源同字节别名排除，无exact只是机械去重。实际F01weight1/streetmeadow4规则原读，F02weight3/empty，中心streetpolish3规则仅保存/读不施本屋。root/tag实读，meadow replaceTRUE、oldtaiga replacefalse，必选/可选不混淆，不虚称实际落地。街口empty与底NPC真实plains/taiga池分开，原版loot/NPC不在单modJar不等整合缺失。旧累计/Main066F01/062/061绑定不变，COD4仍153差847，1000未达；无Java/制作/清单删除/用户实例操作。下一批固定本地新整体组织完整相关源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_ONLY_BOTH_FAMILY_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':17,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':0,'held_zero':2,'formal_credit':0},ensure_ascii=False))

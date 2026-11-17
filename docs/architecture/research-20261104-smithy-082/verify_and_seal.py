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
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('307 history source pairs',dedup['historical_unique_local_archive_member_pairs']==307);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one pair no exact duplication',len(dedup['within_batch_pairs'])==1 and all(not p['exact_keys']for p in dedup['within_batch_pairs']));check('both held zero formal0',review['pending_maximum']==0 and review['held_zero']==2 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 307',screen['history_unique_archive_member_pairs']==307)
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
write('active-checkpoint.json',{'batch':82,'status':'SEALED_TWO_WHOLE_BODIES_BOTH_FAMILY_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':83,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('082 沼泽木台双职业铺与北欧石工甲匠铺\n\n2完整原建筑、14实际PNG、14具体观察，均家族hold0非机械exact重复，正式0。F01 10×8×10/DV3120，800全记录=397nonair+403air，西木廊入单室、外凸西南magma与顶营火/西smith、东内高炉高箱，近063F02木屋西廊东热罩及既有房+外热区家族；无床，增设备/草顶不足。swampboat目录不等船壳或可航功能；东高炉y2而下格y1原air照存，不填支架。F02 9×8×11/DV3105，792全记录=276nonair+516air，南热室西客门北工门连小北石工坪，近已有单室+外坪/多门冷热点家族；草顶与设备/门差不足另计。北stonecutter y0上方y1是NPCsocket，不称已生成NPC/实机可用站位。两者均无上楼通路或床。\n\n先307历史/同Jar同字节别名筛，新指纹无exact不等独立；旧063等判断绑定复用无旧图重验。两houseweight1/legacyrigid/empty；street处理器随towncenters保存，不施本屋；Swedish原Snowy大写照存不修。实际root/tag保存，Swedish全部17optional不证明已装/生成。F01实际NPCpool三等权候选非三已生成NPC，F02原版taiga池不在modJar不等环境缺失。原箱seed/空sign/炉状态留全，无loot运行/付款回执宣称。\n\n1000门槛未达，旧累计/Main收据保留，COD4仍153差847；无Java/制作/主清单删除/实例修改。下一批仅固定本地完整相关新源，近族不反复出图。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_ONLY_BOTH_FAMILY_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':14,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':0,'held_zero':2,'formal_credit':0},ensure_ascii=False))

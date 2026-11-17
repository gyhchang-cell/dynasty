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
check('two source/raw/review aligned',len(s)==len(r)==len(review['cases'])==2 and [a['id']for a in s]==[a['id']for a in r]==[a['id']for a in review['cases']])
with ZipFile(s[0]['source_archive'])as z:
 check('fixed source archive SHA',bind(s[0]['source_archive'])['sha256']==s[0]['source_archive_sha256'])
 check('original metadata SHA',hashlib.sha256(z.read(context['metadata']['member'])).hexdigest()==context['metadata']['sha256'])
 check('original metadata text',z.read(context['metadata']['member']).decode()==context['metadata']['original_text'])
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
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('289 history source pairs',dedup['historical_unique_local_archive_member_pairs']==289);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one internal pair no exact duplication',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys']);check('pending max1 formal0',review['pending_maximum']==1 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 289',screen['history_unique_archive_member_pairs']==289)
for a in s:
 row=next(x for x in screen['rows']if x['canonical_member']==a['member'])
 check(a['id']+' pre-render history excluded',row['eligible_for_new_source_study']and not row['known_history']and row['original_nbt_sha256']==a['nbt_sha256'])
latest=json.loads((OUT/'latest-independent-admissions.json').read_text())
for key in ['receipt','clarification']:
 f=latest[key];check('independent main '+key+' binding',bind(f['path'])==f)
check('current batch not self admitted',latest['current_batch_formal_credit_added']==0)
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_PENDING_INDEPENDENT_REVIEW';write('session.json',session)
write('active-checkpoint.json',{'batch':73,'status':'SEALED_TWO_WHOLE_SOURCE_BODIES_ONE_PENDING_ONE_HELD','source_bodies_studied':2,'actual_current_images_viewed':14,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'newly_notified_main_061_increment':2,'not_total_cumulative':True,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':74,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('# 073 沙漠紧凑匠铺研究\n\n两个原完整单体，14张PNG实际查看、14项观察。F01西低敞前棚接小东围护炉/高双箱室，非经典前敞热/后冷室同职能顺序；最多1待独立家族/相关性复核，不以平顶垛口/砂岩/尺寸计数，主审仍可hold。F02窄长西敞棚→东工作台+熔岩锅/北高箱，和071F02/072F02基本组织近，缩窄/换材/平檐不足独立，hold0。\n\n两源无床/梯/实体，高箱和小垛不是二层。F01高炉west/不燃/空、双箱原loot/seed及closedtop家具承托保留；F02熔岩锅不是水锅/热锻全流程。F01入口empty/finalstructure_void；F02jointrollable/empty/final一对方括号jungle east bottom阶，未修原源。主要灰平檐为birch半砖，不当石棚。两源DV3953，标牌/低口/半砖/高箱/功能/地形未原生验。\n\n先289历史archive/member及别名排除后渲染，新输入与历史/两存量松散/内部1对无精确匹配，不等于语义信用。实际两屋weight1/rigid/single/processorsempty；同整池zombie_desert非当前处理。原版desert tag与loot未在固定Jar补造。\n\n正式0，COD3空间研究不加COD4，153/1000差847不变；累计不重置。1000前不制作，不改任务/指南针/主清单，不删提示词、不Java/游戏。继续074。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_ONLY_PENDING_INDEPENDENT_REVIEW','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':14,'manual_observations':14,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':1,'held_zero':1,'formal_credit':0},ensure_ascii=False))

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
check('18 actually viewed bindings',sum(len(c['images_actually_viewed'])for c in review['cases'])==18)
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('300 history source pairs',dedup['historical_unique_local_archive_member_pairs']==300);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one internal pair no exact duplication',len(dedup['within_batch_pairs'])==1 and all(not p['exact_keys'] for p in dedup['within_batch_pairs']));check('pending max0 formal0',review['pending_maximum']==0 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 300',screen['history_unique_archive_member_pairs']==300)
for a in s:
 row=next(x for x in screen['rows']if x['canonical_member']==a['member'])
 check(a['id']+' pre-render history excluded',row['eligible_for_new_source_study']and not row['known_history']and row['original_nbt_sha256']==a['nbt_sha256'])
latest=json.loads((OUT/'latest-independent-admissions.json').read_text())
for key in ['receipt','clarification']:
 f=latest[key];check('independent main '+key+' binding',bind(f['path'])==f)
f=latest['newly_notified_admission_062']['receipt'];check('independent062 saved unchanged',bind(f['path'])==f)
check('current batch not self admitted',latest['current_batch_formal_credit_added']==0)
coverage=json.loads((OUT/'fixed_trek_smithy_source_coverage.json').read_text())
check('25 unique canonical filename-set coverage',len(coverage['rows'])==25 and len(set(c['canonical_member']for c in coverage['rows']))==25)
with ZipFile(s[0]['source_archive'])as z:
 for row in coverage['rows']:
  check(row['canonical_member']+' alias same bytes',hashlib.sha256(z.read(row['canonical_member'])).hexdigest()==hashlib.sha256(z.read(row['same_bytes_compatibility_alias'])).hexdigest()==row['original_nbt_sha256'])
  check(row['canonical_member']+' saved manual links',bool(row['saved_manual_study_bindings']))
  for f in row['saved_manual_study_bindings']:check('study link unchanged '+f['path'],bind(f['path'])==f)
check('coverage not credit admission',coverage['not_semantic_credit_total']and coverage['not_25_accepted_buildings']and not coverage['production_gate_met']and coverage['formal_credit_added']==0)
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_PENDING_INDEPENDENT_REVIEW';write('session.json',session)
write('active-checkpoint.json',{'batch':78,'status':'SEALED_TWO_WHOLE_BODIES_BOTH_FAMILY_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':18,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'fixed_trek_filename_set_study_links':25,'not_25_accepted_buildings':True,'newly_notified_main_062_increment':2,'not_total_cumulative':True,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':79,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('078 草原两铺家族持零；固定Trek匠铺命名集研究链接闭合\n\n2完整原体/18实际PNG/14观察，均hold0，无待审新信用。F01同077甲匠15×13脚印、西门主厅、南低棚双向炉/下营火/两高低箱；移除床梯/降屋盖/换木砖不足独立。原2甲架/新count/内外位置保存，无床梯不能沿兄弟源发明高阁。F02低L西北热作棚接东北箱室/南双床翼，与056/058家族近，双床/砧/瓦材差不足独立。门/床/作业均y2，无二层，原显式air路径保存不称碰撞已验。\n\n先300历史archive/member/兼容别名排除，无exact重复不代表语义新设计。actual两屋mossify10两规则阅读，权2/1 single rigid；DV3953/真实入口finalair或cobble east bottom阶保留，当前原版tag/loot与旁支zombie缺固定Jar不等整个环境缺失。\n\nfixed_trek_smithy_source_coverage.json对固定Jar按职业命名找到的25规范NBT均链接已有人工研究，另25同字节structure兼容别名不多算；这是源研究覆盖，绝非25有效建筑或1000达标，也非整个Trek相关建筑穷尽。旧批只绑定不重看/重接纳。下一步其他作者/既有离线新源先预筛。当前正式0/COD4仍153差847/累计保留，不制作/删除清单/Java。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_ONLY_BOTH_EXISTING_FAMILY_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':18,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':0,'held_zero':2,'formal_credit':0},ensure_ascii=False))

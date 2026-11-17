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
check('25 actually viewed bindings',sum(len(c['images_actually_viewed'])for c in review['cases'])==25)
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('282 history source pairs',dedup['historical_unique_local_archive_member_pairs']==282);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one internal pair no exact duplication',len(dedup['within_batch_pairs'])==1 and not dedup['within_batch_pairs'][0]['exact_keys']);check('pending max2 formal0',review['pending_maximum']==2 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 282',screen['history_unique_archive_member_pairs']==282)
for a in s:
 row=next(x for x in screen['rows']if x['canonical_member']==a['member'])
 check(a['id']+' pre-render history excluded',row['eligible_for_new_source_study']and not row['known_history']and row['original_nbt_sha256']==a['nbt_sha256'])
latest=json.loads((OUT/'latest-independent-admissions.json').read_text())
for key in ['receipt','clarification']:
 f=latest[key];check('independent main '+key+' binding',bind(f['path'])==f)
check('current batch not self admitted',latest['current_batch_formal_credit_added']==0)
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_PENDING_INDEPENDENT_REVIEW';write('session.json',session)
write('active-checkpoint.json',{'batch':70,'status':'SEALED_TWO_WHOLE_SOURCE_BODIES_TWO_PENDING','source_bodies_studied':2,'actual_current_images_viewed':25,'pending_maximum':2,'formal_credit_added':0,'newly_notified_main_061_increment':2,'not_total_cumulative':True,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':71,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('# 070 新原源匠铺研究\n\n先用282历史archive/member对和兼容别名排除，再研究Trek两原始完整单体；25张图实际查看、14项观察。F01菌柄式底层工作/储藏/床位一室，上方装饰冠盖与西砖烟囱，非可住多层。原未带命名空间smooth_quartz和item frame实体内外位置全部保留；固定Jar缺失minecraft:village/mushroom/villagers，不能因minecraft命名空间冒称原版池存在。\n\nF02架高savanna甲匠：地面热工作口、西折阶→高门→南双床双箱主室、北爬梯→闭合顶活板门。高炉litfalse/空，lava_cauldron不是水锅，两床对非四床，双箱原loot/seed不当两次奖励。DataVersion3953不能冒称本项目兼容。\n\n两源最多各1待独立适用性/完整性/家族复核，正式增量0。新输入与282历史对/两已存松散指纹/内部1对无精确匹配；这不是有效建筑数。原版碰撞、功能、地形、照明、火/烟、村民与运行兼容未验。分类图不代表原生材质/网格。\n\n061主审F01/F03新接纳2及村民池澄清已绑定；这是阶段增量，不重置累计；059/060既有5保留。061F03仅入口empty，两栏台socket是真实taiga/villagers并finalair，不当空池/两个NPC。069重复源纠正为0新增，不再提交重审。\n\nCOD3NPC01空间参考；不加COD4，维持153/1000差847。1000前不制作，不改任务/指南针/主清单；不运行Java、不接触游戏。继续071新源，先排除历史和别名，不等主审。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_ONLY_PENDING_INDEPENDENT_REVIEW','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':25,'manual_observations':14,'pending_maximum':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':2,'formal_credit':0},ensure_ascii=False))

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
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('317 history source pairs',dedup['historical_unique_local_archive_member_pairs']==317);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one pair no exact duplication',len(dedup['within_batch_pairs'])==1 and all(not p['exact_keys']for p in dedup['within_batch_pairs']));check('two whole pending no self credit',review['pending_maximum']==2 and review['held_zero']==0 and review['whole_smithy_bodies_studied']==2 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 317',screen['history_unique_archive_member_pairs']==317)
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
check('17 generated actual PNG',len(list(OUT.glob('F??-*.png')))==17 and review['actual_current_images_viewed']==17)
def cells(a):
 d=a['nbt_decoded_original'];pal=d.get('palette')or d['palettes'][0];return {tuple(v['pos']):pal[v['state']]for v in d['blocks']}
a,b=map(cells,r)
check('F01 real two north bottom stone stairs',all(a[pos]['Name']=='minecraft:stone_brick_stairs'and a[pos]['Properties']['half']=='bottom'and a[pos]['Properties']['facing']=='north'for pos in [(3,2,5),(3,3,4)]))
check('F01 stair entry pocket original air',a[(3,2,6)]['Name']==a[(3,3,6)]['Name']=='minecraft:air')
check('F02 four external bottom north stairs',all(b[(4,y,z)]['Name']=='minecraft:birch_stairs'and b[(4,y,z)]['Properties']['half']=='bottom'and b[(4,y,z)]['Properties']['facing']=='north'for y,z in [(1,8),(2,7),(3,6),(4,5)]))
check('F02 lower shop divider and floor4',all(b[(x,y,4)]['Name']=='minecraft:quartz_bricks'for x in [0,1,2,3]for y in [1,2,3]) and all(b[(x,4,z)]['Name']=='minecraft:spruce_planks'for x in [1,2]for z in [5,6,7,8]))
check('F02 two beds not four',sum(v['Name']=='minecraft:gray_bed'for v in b.values())==4 and sum(v['Name']=='minecraft:gray_bed'and v['Properties']['part']=='head'for v in b.values())==2)
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_TWO_WHOLE_PENDING';write('session.json',session)
write('active-checkpoint.json',{'batch':87,'status':'SEALED_TWO_WHOLE_PENDING_INDEPENDENT_FAMILY_REVIEW','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':17,'pending_maximum':2,'held_zero':0,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':88,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('087 都铎相邻错层热作业铺与地中海窄双底店上居住屋\n\n2完整原体、17实际PNG/14观察，最多2待独立整屋相关及家族复核，正式0。F01 9×12×12/DV3578，1296全记录=476nonair+820air：东单外门进低屠宰室（floor1/stand2），经西内门至3,2,6凹口，沿northbottomstonebrickstairs3,2,5→3,3,4上西高甲匠室（floor3/stand4）；西室下全实体高基，不发明下居室。10top木梯为装饰工作/梁不是楼梯，无床。原2空sign、skull单摆件、炉空/箱seed保留。相邻错层封闭双作业室整体最多1，非单凭双炉/高低盖。\n\nF02 5×10×10/DV3578，500全记录=334nonair+166air：底层北工具/南制箭两小店被z4实墙隔开各东门，南店上单间2床+箱（floor4/stand5）。东贴墙从南北向四bottombirch阶4,y1,z8→y2,z7→y3,z6→y4,z5，三个top支承接上门3,5,4；另1top为店内家具，不把8birchstairs都作踏梯。真实quartzbricks160是白石英主墙，分类图red不代表红砖墙。2eastempty接口finalwall/topstair不是两实际街道，两NPCsocket不等2人，4bedstates=2床。双底店不互通+单上居住独立外直梯整体最多1，仍与070/071家族有风险，不按职业/门/床拆计。\n\n先317历史/同源别名排，无exact不决定语义。F01 houseweight2/legacyrigid/empty，towncenterstreetprocessor不套屋；F02实际houses/regular.json weight1/legacyrigid/streetmed三andesiteslab随机规则原读，未执行。actual village roots Tudorsize5/Medsize3，不借同theme哨站；biometagTudor7optional条目有1重复/6distinct，Med10optional，无mandatoryvanilla。真实medhouse loot8entries/3..8rolls全部保存不运行。原版loot/NPC缺单Jar不等环境缺。旧独立079F01/080F01收据保留不重跑/不重置，COD4仍153差847，1000未达。无Java/制作/清单删除，下一批088固定本地新完整相关源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_TWO_WHOLE_PENDING_INDEPENDENT_REVIEW','source_bodies_studied':2,'whole_smithy_bodies_studied':2,'actual_current_images_viewed':17,'manual_observations':14,'pending_maximum':2,'held_zero':0,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':2,'held_zero':0,'formal_credit':0},ensure_ascii=False))

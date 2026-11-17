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
check('12 actually viewed bindings',sum(len(c['images_actually_viewed'])for c in review['cases'])==12)
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('319 history source pairs',dedup['historical_unique_local_archive_member_pairs']==319);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one pair no exact duplication',len(dedup['within_batch_pairs'])==1 and all(not p['exact_keys']for p in dedup['within_batch_pairs']));check('one whole one ruin both held formal0',review['pending_maximum']==0 and review['held_zero']==2 and review['whole_smithy_bodies_studied']==1 and review['ruin_bodies_not_whole_smithies']==1 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 319',screen['history_unique_archive_member_pairs']==319)
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
check('12 generated actual PNG',len(list(OUT.glob('F??-*.png')))==12 and review['actual_current_images_viewed']==12)
e=r[0]['nbt_decoded_original']['entities'];check('F01 one original armorstand not NPC',len(e)==1 and e[0]['nbt']['id']=='minecraft:armor_stand'and e[0]['blockPos']==[0,1,2]and e[0]['pos']==[0.5,1.0,2.5]and e[0]['nbt']['Pos']==[1462.5,-58.0,44.5])
check('F02 only ruin material inventory',set(r[1]['material_counts'])=={'minecraft:cobblestone','minecraft:grass_block','minecraft:air','minecraft:mossy_cobblestone_stairs','minecraft:jigsaw','minecraft:chest'} and r[1]['nonair']==54 and r[1]['air']==270)
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_BOTH_HELD_ZERO';write('session.json',session)
write('active-checkpoint.json',{'batch':88,'status':'SEALED_ONE_SOD_WORKROOM_FAMILY_AND_ONE_EXPOSED_RUIN_BOTH_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':1,'ruin_bodies_not_whole_smithies':1,'actual_current_images_viewed':12,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':89,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('088 雪针叶林覆草甲匠屋与森林工具铺露天遗迹\n\n2原体=1完整单室铺+1露天残基，12实际PNG/14观察，均hold0，无待增/正式0。F01 9×8×7/DV3105，504全记录=245nonair+259air；南/西双门同一窄小室、西北箱东炉，覆草低盖。比060F03同snowyviking三侧外热/冷工作组织更简化，草盖/换炉/加外盔甲架不形成新空间家族。1原armorstand非NPC、局部blockPos0,1,2和内部旧worldPos1462.5,-58,44.5保留不挪动；静态分类图不画实体不冒原外观已验。grass/tallgrass薄植物不当整格楼层，目录snowy不等实际雪冰覆盖。\n\nF02 9×3×12/DV3120，324全记录=54nonair+270air，只cobble46/grassblock4/苔阶2/入口socket1/职业loot箱1。原无屋盖围护/门/工作台/炉/NPC；完整残迹文件不等完整匠铺，toolsmithloot名不补功能，两个残石区不拼想两建筑，hold0。实际root/towncenters有，不编缺失root。\n\n先319历史/同源别名排。F01 houseweight5/legacyrigid/vanillastreet_snowy_or_taiga，F02weight2/legacyrigid/vanillamossify70，单Jar未含实际原版processor不按名冒全文读/执行雪或70%。towncenterforeststreet七规则实际读保存仅上下文，sand/gravel输出原带level0保留不修，不套house。实际roots snowysize6/forestsize7，各start0/max116/beardthin；tags各1mandatory+16optional，原未namespace snowy_coniferious_forest保留不擅修，optional不证已装生成。旧Main079/080等收据累计保持不重验，COD4仍153差847，1000未达。无Java/制作/清单删除。下一批089固定本地新完整相关源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_SOD_WORKROOM_FAMILY_AND_EXPOSED_RUIN_BOTH_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':1,'ruin_bodies_not_whole_smithies':1,'actual_current_images_viewed':12,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':0,'held_zero':2,'formal_credit':0},ensure_ascii=False))

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
check('15 actually viewed bindings',sum(len(c['images_actually_viewed'])for c in review['cases'])==15)
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('311 history source pairs',dedup['historical_unique_local_archive_member_pairs']==311);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one pair no exact duplication',len(dedup['within_batch_pairs'])==1 and all(not p['exact_keys']for p in dedup['within_batch_pairs']));check('one pending one pavilion held formal0',review['pending_maximum']==1 and review['held_zero']==1 and review['whole_smithy_bodies_studied']==1 and review['professional_pavilion_bodies_with_unresolved_whole_smithy_relevance']==1 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 311',screen['history_unique_archive_member_pairs']==311)
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
write('active-checkpoint.json',{'batch':84,'status':'SEALED_ONE_WHOLE_COLD_L_SHOP_PENDING_ONE_PAVILION_HELD','source_bodies_studied':2,'whole_smithy_bodies_studied':1,'professional_pavilion_bodies_with_unresolved_whole_smithy_relevance':1,'actual_current_images_viewed':15,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':85,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('084 花林甲匠职业亭与L形冷工具铺\n\n2原体=1完整冷铺+1完整职业亭（整栋铁匠铺适用性不足），15实际PNG/14观察，F01hold0、F02最多1待独立相关/家族复核，正式0。F01 9×9×9/DV3105，729全记录=295nonair+434air；西阶到抬高方坪，西南箱/东炉，烟道到高盖营火；方亭整体完整不等整栋相关铺已验，叠檐不是二层。12sprucegate全部y4/openfalse沿檐作梁饰，不是地面12入口。西街口actualkaisynstreets/finalstructurevoid非empty，底NPC真plains池/finalair。\n\nF02 10×8×13/DV3105，1040全记录=387nonair+653air，西门入南较高较宽箱主室，经共用东侧通路到北低窄smith翼；西北凹角有低外廊/门檐。高低翼同层，无内门/上层/床梯/热源。实际x3..7,y1,z8与x6,y1,z4..8原air，屋盖是深板岩两交接坡。与056/067L低翼家族有风险，最多1待Main看整体组织是否独立；若只是旧L形删热换家具必须hold0，不靠日式顶/材质/无床增加信用。\n\n先311历史/全部同源同字节别名排，指纹无exact不决定语义。两houseweight4/legacyrigid/实际minecraftmossify10在单Jar不含，不冒称已读/应用具体概率，不证明整环境缺失。花林街pool16elements/fallbackterminators仅道路上下文，不能算16建筑；街processor实际5规则已读不替代houseprocessor。root/tag原文保存，两原箱seed/炉空/上盖营火留全。旧累计/Main收据不重置，COD4仍153差847，1000未达；无Java/制作/主清单删除/实例操作。下一批固定本地新完整相关源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_ONLY_ONE_COLD_L_SHOP_PENDING_ONE_PAVILION_HELD','source_bodies_studied':2,'whole_smithy_bodies_studied':1,'professional_pavilion_bodies_with_unresolved_whole_smithy_relevance':1,'actual_current_images_viewed':15,'manual_observations':14,'pending_maximum':1,'held_zero':1,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':1,'held_zero':1,'formal_credit':0},ensure_ascii=False))

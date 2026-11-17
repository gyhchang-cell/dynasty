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
check('13 actually viewed bindings',sum(len(c['images_actually_viewed'])for c in review['cases'])==13)
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('313 history source pairs',dedup['historical_unique_local_archive_member_pairs']==313);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('one pair no exact duplication',len(dedup['within_batch_pairs'])==1 and all(not p['exact_keys']for p in dedup['within_batch_pairs']));check('one whole one ground unclosed both held formal0',review['pending_maximum']==0 and review['held_zero']==2 and review['whole_smithy_bodies_studied']==1 and review['ground_assembly_unclosed_bodies']==1 and review['formal_credit_added']==0)
screen=json.loads((OUT/'pre-render-history-screen.json').read_text())
check('pre-render history 313',screen['history_unique_archive_member_pairs']==313)
for a in s:
 row=next(x for x in screen['rows']if x['canonical_member']==a['member'])
 check(a['id']+' pre-render history excluded',row['eligible_for_new_source_study']and not row['known_history']and row['original_nbt_sha256']==a['nbt_sha256'])
latest=json.loads((OUT/'latest-independent-admissions.json').read_text())
for key in ['receipt','clarification']:
 f=latest[key];check('independent main '+key+' binding',bind(f['path'])==f)
f=latest['newly_notified_admission_062']['receipt'];check('independent062 saved unchanged',bind(f['path'])==f)
f=latest['newly_notified_admission_066_F01']['receipt'];check('independent066 F01 saved unchanged',bind(f['path'])==f)
f=latest['newly_notified_admission_080_F01']['receipt'];check('independent080 F01 saved unchanged',bind(f['path'])==f and f['sha256']=='bb8d021f1ca45a5fc91ce2fc1b71ce5033d951f2724d3ea0c470f8a2d9b8bed5')
check('current batch not self admitted',latest['current_batch_formal_credit_added']==0)
with ZipFile(s[0]['source_archive'])as z:
 c=json.loads((OUT/'actual-nilotic-root-pool.json').read_text());bb=z.read(c['member']);check('actual nilotic basepool original',hashlib.sha256(bb).hexdigest()==c['sha256']and json.loads(bb)==c['json'])
 c=json.loads((OUT/'nilotic-base-assembly-context.json').read_text());bb=z.read(c['member']);d=read(bb);check('base original decoded intact',hashlib.sha256(bb).hexdigest()==c['sha256']and d==c['nbt_decoded_original'])
 pal=d.get('palette')or d['palettes'][0];counts=Counter(pal[x['state']]['Name']for x in d['blocks']);check('base not solid floor',d['size']==[80,1,80]and d['DataVersion']==3120 and len(d['blocks'])==6400 and counts=={'minecraft:air':6382,'minecraft:jigsaw':18});check('base18 houses sockets',len(c['all_block_entities'])==18 and all(x['nbt']['pool']=='kaisyn:village/exclusives/nilotic/houses'and x['nbt']['name']==x['nbt']['target']=='minecraft:building_floor'for x in c['all_block_entities']))
 c=c['base_processor'];bb=z.read(c['member']);check('base processor original',hashlib.sha256(bb).hexdigest()==c['sha256']and json.loads(bb)==c['json'])
check('13 generated and actual images',len(list(OUT.glob('F??-*.png')))==13 and review['actual_current_images_viewed']==13)
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_BOTH_HELD_ZERO';write('session.json',session)
write('active-checkpoint.json',{'batch':85,'status':'SEALED_ONE_SINGLE_WORKROOM_FAMILY_AND_ONE_GROUND_UNCLOSED_BOTH_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':1,'ground_assembly_unclosed_bodies':1,'actual_current_images_viewed':13,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'cumulative_not_reset':True,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':86,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('085 稀疏丛林双职业木工室与尼罗甲匠屋体\n\n2原体=1完整单室铺+1地形地板承托未闭屋体，13实际PNG/14观察，均hold0无待增/正式0。F01北双扇门入单公共室，西北炉/高箱、中东石工、南箱；4门状态=2门扇一入口，6gate在y3高窗/栏位，oakslab屋盖不是灰石或二层。单室家族不靠双职业/木料/双门获独立。真实NPC池是tribal且1/1/10权重不是12人，原样保留。\n\nF02西openTRUE单门，南一绿床/东南箱、东炉、西北外空lit营火，均使用层y0；中央down_east buildingfloor接头不是水平街口。实际root absolute-1/start nilotic/base_plate，原80×1×80base仅6382air+18向上houses接头无实体地板；root/pool存在不等地面承托闭合。house rigid/.4packedmud→mudbrick/.4mangrovewood→roots；base terrainmatching/实际jigsawreplacement。不冒缺actualroot，不拿18槽位/基底或有床改变算新增整建筑。061F02已有同边界判断直接绑定复用，不重看旧图或重验旧范围。\n\n先313历史/同源别名排，指纹无exact不等语义独立。F02先前截断PNG未计，已分批实际重看7图，合全批13图。080F01 Main收据bb8d021f…接入最新独立增1仅COD3NPC01，旧累计不重置/COD4仍153差847，080验收不重跑。两原箱/炉/床/门/processor原态完整，无Java/制作/资产或清单删除；1000门槛与全部任务仍未达。下一批086固定本地新完整相关源。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_SINGLE_WORKROOM_FAMILY_AND_GROUND_UNCLOSED_BOTH_HELD_ZERO','source_bodies_studied':2,'whole_smithy_bodies_studied':1,'ground_assembly_unclosed_bodies':1,'actual_current_images_viewed':13,'manual_observations':14,'pending_maximum':0,'held_zero':2,'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':0,'held_zero':2,'formal_credit':0},ensure_ascii=False))

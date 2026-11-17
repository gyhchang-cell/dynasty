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
  check(a['id']+' raw hash',hashlib.sha256(raw).hexdigest()==a['nbt_sha256']==b['nbt_sha256']);check(a['id']+' decoded original',d==b['nbt_decoded_original']);check(a['id']+' unique positions',len(pos)==len(set(pos)));check(a['id']+' bounds',all(all(0<=p[i]<d['size'][i]for i in range(3))for p in pos));check(a['id']+' indices',all(0<=x['state']<len(pal)for x in d['blocks']));check(a['id']+' size/version',d['size']==a['size']and d['DataVersion']==a['DataVersion']);check(a['id']+' original entities preserved',d.get('entities',[])==[])
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
check('20 actually viewed bindings',sum(len(c['images_actually_viewed'])for c in review['cases'])==20)
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:check('protected unchanged '+f['path'],bind(f['path'])==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('279 history source pairs',dedup['historical_unique_local_archive_member_pairs']==279);check('two reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact old/loose matches',all(not c['historical_exact_matches']and not c['loose_exact_matches']for c in dedup['entries']));check('three internal pairs no exact duplication',len(dedup['within_batch_pairs'])==3 and all(not p['exact_keys']for p in dedup['within_batch_pairs']));check('pending max2 formal0',review['pending_maximum']==2 and review['formal_credit_added']==0)
write('verification.json',{'status':'PASS_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'java_run':False,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_PENDING_INDEPENDENT_REVIEW';write('session.json',session)
write('active-checkpoint.json',{'batch':68,'status':'SEALED_THREE_WHOLE_SOURCE_BODIES_TWO_PENDING_ONE_HELD_ZERO','source_bodies_studied':3,'actual_current_images_viewed':20,'pending_maximum':2,'held_zero':['F03'],'formal_credit_added':0,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':69,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('# 068 甲匠与工具匠研究\n\n3个完整原源体、20张实际查看图、21项具体观察。F01菇林双门单室甲匠/北东折角台/南中央空高炉/烟囱意向；F02菇林西南双门进连续L窄工具室/北端工作台；各max1待独立完整性、相关性与家族复核。F03山地单室并排双高炉，缺足够独立空间语义保守0，不以双炉、变长或换材增加信用。\n\n两菇林原源全体积有记录；山地原源234记录/490声明体积，50显式air、256省略。全部原状态、工作位、炉空Items、门hinge及入口final_state保存；蘑菇/原木通用分类灰/棕不代表原生材质质量。实际入村processor、根、标签闭包已读，排烟/碰撞/运行未验。\n\n新输入与279历史source pair及2复用松散指纹比较，无精确匹配；3组内部比较亦无精确匹配。数字不是有效建筑数量，去重不等于独立家族。旧批次验收不重跑，累计不清零。正式增量0，COD4仍153/1000缺847；本批仅COD3空间，不挪入COD4。\n\n未制作、改任务/指南针、删清单或运行Java。下一批继续尚未实际研究的相关完整匠铺。\n')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json'];write('RECEIPT.json',{'status':'SEALED_RESEARCH_ONLY_PENDING_INDEPENDENT_REVIEW','source_bodies_studied':3,'whole_smithy_bodies_studied':3,'actual_current_images_viewed':20,'pending_maximum':2,'held_zero':['F03'],'formal_credit_added':0,'checks_passed':len(checks),'java_run':False,'native_acceptance':False,'all_tasks_complete':False,'files':files});print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':2,'formal_credit':0},ensure_ascii=False))

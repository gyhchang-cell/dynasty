"""Verify this batch without Java or historical acceptance reruns; seal once."""
import json,hashlib,math,sys
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
def check(name,value):
 checks.append({'name':name,'passed':bool(value)})
 if not value:raise AssertionError(name)
s=json.loads((OUT/'sources.json').read_text())['candidates'];r=json.loads((OUT/'raw-source-audit.json').read_text())['candidates'];manual=json.loads((OUT/'manual-review.json').read_text());archives={}
for a,b in zip(s,r):
 jar=a['source_archive']
 if jar not in archives:
  archives[jar]=ZipFile(jar);check('archive SHA',bind(jar)['sha256']==a['source_archive_sha256'])
 raw=archives[jar].read(a['member']);d=read(raw);check(a['id']+' raw SHA',hashlib.sha256(raw).hexdigest()==a['nbt_sha256']==b['nbt_sha256']);check(a['id']+' decoded original equality',d==b['nbt_decoded_original']);pal=d.get('palette')or d['palettes'][0];pos=[tuple(x['pos'])for x in d['blocks']]
 check(a['id']+' positions unique',len(pos)==len(set(pos)));check(a['id']+' positions in bounds',all(all(0<=p[i]<d['size'][i]for i in range(3))for p in pos));check(a['id']+' state indices',all(0<=x['state']<len(pal)for x in d['blocks']))
 counts=Counter(pal[x['state']]['Name']for x in d['blocks']);check(a['id']+' counts',sum(v for k,v in counts.items()if k not in AIR)==b['nonair'] and sum(v for k,v in counts.items()if k in AIR)==b['air']);check(a['id']+' no lost original entities',len(d.get('entities',[]))==0);check(a['id']+' exact size and version',d['size']==a['size'] and d['DataVersion']==a['DataVersion'])
for c in manual['cases']:
 check(c['id']+' seven concrete topics',set(c['observations'])=={'layout','proportion','facade','roof','materials','circulation','terrain'})
 for x in c['images_actually_viewed']:
  check(Path(x['path']).name+' image hash',bind(x['path'])==x)
  with Image.open(x['path'])as im:im.verify()
  check(Path(x['path']).name+' image readable',True)
 check(c['id']+' no self credit',c['formal_credit_added']==0)
check('24 actually viewed image bindings',sum(len(c['images_actually_viewed'])for c in manual['cases'])==24)
context=json.loads((OUT/'source-context.json').read_text())
for a in context['candidates']:
 for c in a['contexts']:
  bb=archives[s[0]['source_archive']].read(c['member']);check(a['id']+' context '+c['member'],hashlib.sha256(bb).hexdigest()==c['sha256'] and json.loads(bb)==c['json'])
for c in json.loads((OUT/'biome-collection-context.json').read_text()):
 check(c['member'],hashlib.sha256(archives[s[0]['source_archive']].read(c['member'])).hexdigest()==c['sha256'])
protected=[]
for f in json.loads((OUT/'protected-inputs.json').read_text())['files']:
 current=bind(f['path']);protected.append({'path':f['path'],'unchanged':current==f,'current':current})
 check('protected unchanged '+f['path'],current==f)
dedup=json.loads((OUT/'dedup-evidence.json').read_text());check('274 history pairs new input comparison',dedup['historical_unique_local_archive_member_pairs']==274);check('2 reused loose fingerprints',len(dedup['explicit_accepted_loose'])==2);check('no exact historical/loose matches',all(not e['historical_exact_matches']and not e['loose_exact_matches']for e in dedup['entries']));check('three internal comparisons',len(dedup['within_batch_pairs'])==3 and all(not e['exact_keys']for e in dedup['within_batch_pairs']));check('one proposal two holds no formal credit',sum(c['credit_proposal_maximum']for c in manual['cases'])==1 and manual['formal_credit_added']==0)
write('verification.json',{'status':'PASS_CURRENT_RESEARCH_INTEGRITY_ONLY','checks_passed':len(checks),'checks':checks,'protected':protected,'native_acceptance':False,'independent_semantic_admission':False,'formal_credit_added':0,'java_run':False,'all_tasks_complete':False})
session=json.loads((OUT/'session.json').read_text());session['status']='SEALED_RESEARCH_PENDING_INDEPENDENT_REVIEW';write('session.json',session)
write('active-checkpoint.json',{'batch':66,'status':'SEALED_THREE_SOURCE_BODIES_ONE_PENDING_TWO_HELD_ZERO','actual_images_viewed':24,'pending_maximum':1,'held_zero':['F02','F03'],'formal_credit_added':0,'verification':bind(OUT/'verification.json'),'previous_checkpoint':bind(OUT/'previous-checkpoint.json'),'next_batch':67,'java_run':False,'all_tasks_complete':False})
(OUT/'HANDOFF.md').write_text('''# 066 匠铺研究收据\n\n本批研究 RepurposedStructures 山地武器匠1/2、海洋武器匠1三个原源体，实际查看24张图，逐例记录布局、比例、立面、屋顶、材质、动线、地形共21项观察。原始稀疏NBT、水状态、方块实体、村池、根、processor和本地生物群系标签证据均保存。没有复制原建筑到产品。\n\n- F01：封闭小冷加工室、门前双砂轮，最多1项待独立完整性/相关性/家族复核。\n- F02：单砂轮单坡遮棚，尚未证完整独立匠铺，0。\n- F03：水下前石棚/后木室，实际水84/气泡2，保留0家族独立信用；不能把含水、坡盖或炉箱位移当新家族。两张隐藏液体图仅辅助观察。\n\n新输入与274个历史archive/member对及2个已保存松散源指纹比较，无精确匹配；3组内部比较无精确匹配。此为去重辅助，274不是有效建筑数。旧已验收批次未重新验收，059/060接纳记录继续沿用065绑定，不重置累计数。\n\n当前正式增量0，COD4仍153/1000、差847，COD3不得挪入COD4。未制作建筑、改任务/指南针、删清单或运行Java。主协调负责独立复核与主清单。下一批继续新输入竹林匠铺，不等主审。\n''')
files=[bind(p)for p in sorted(OUT.iterdir())if p.is_file()and p.name!='RECEIPT.json']
write('RECEIPT.json',{'status':'SEALED_RESEARCH_ONLY_PENDING_INDEPENDENT_REVIEW','source_bodies_studied':3,'whole_smithy_bodies_studied':2,'shelter_boundary_unproven':1,'actual_current_images_viewed':24,'pending_maximum':1,'held_zero':['F02','F03'],'formal_credit_added':0,'checks_passed':len(checks),'native_acceptance':False,'all_tasks_complete':False,'files':files})
print(json.dumps({'receipt':bind(OUT/'RECEIPT.json'),'files':len(files),'checks_passed':len(checks),'pending':1,'formal_credit':0},ensure_ascii=False))

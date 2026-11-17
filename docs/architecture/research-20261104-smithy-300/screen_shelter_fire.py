import json,sys,hashlib
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read

def bind(p):
 p=Path(p).resolve();b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def ld(p):return json.loads(Path(p).read_text())
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
m=R/'docs/architecture/research-20261101-dungeons-026/all-structure-metadata.json';mm=ld(m);inv=ld(mm['fixed_archive_inventory']['path']);hist=R/'docs/architecture/research-20261104-smithy-153/history-fingerprints.json';prior={x['source']['member']for x in ld(hist)['entries']};texts=[(p,p.read_text())for p in (R/'docs/architecture').glob('research-*/manual-review.json')];candidates=[]
for e in mm['entries']:
 n=e['member'].lower();s=e.get('size',[])
 if len(s)==3 and min(s)>=5 and max(s)<=40 and any(t in n for t in ['snow','mountain','cabin','chalet','lodge']) and any(t in n for t in ['houses/','cabin','chalet','lodge','house.nbt']) and not any(t in n for t in ['zombie','street','decor','terminator','animal','pens','farm']):
  hits=[bind(p)for p,t in texts if e['member']in t]
  if not hits and e['member']not in prior:candidates.append(e)
archives={};entries=[]
for e in candidates:
 a=e['source_archive']
 if a not in archives:
  b=bind(a);assert b['sha256']==next(v['sha256']for v in inv['archives']if v['path']==a);archives[a]=b
 with ZipFile(a)as z:raw=z.read(e['member']);d=read(raw)
 assert hashlib.sha256(raw).hexdigest()==e['nbt_sha256']
 pal=d['palette'];c=Counter(pal[b['state']]['Name']for b in d['blocks']);features=[]
 for b in d['blocks']:
  s=pal[b['state']]
  if any(t in s['Name']for t in ['_bed','campfire','furnace','smoker','fireplace'])or s['Name']=='minecraft:fire':features.append(dict(pos=b['pos'],state=s,nbt=b.get('nbt')))
 entries.append(dict(source=e,materials=dict(c),features=features,entities=len(d.get('entities',[])),beds=sum(v for k,v in c.items()if k.endswith('_bed')),heating=sum(v for k,v in c.items()if any(t in k for t in ['campfire','furnace','smoker','fireplace'])or k=='minecraft:fire'),lit_heating=sum(f['state'].get('Properties',{}).get('lit')=='true'for f in features if not f['state']['Name'].endswith('_bed')),actual_whole_reading=False,formal_credit_added=0))
put('bounded-header-screen.json',dict(batch=300,metadata=bind(m),history=bind(hist),archives=list(archives.values()),filter=dict(min_each_axis=5,max_any_axis=40,name_topics=['snow','mountain','cabin','chalet','lodge'],name_whole_terms=['houses/','cabin','chalet','lodge','house.nbt'],excluded_terms=['zombie','street','decor','terminator','animal','pens','farm'],exact_member_old_manual_and153_cache_excluded=True),entries=entries,limits=['只有材料计数和床/炉候选状态与BE，未逐栋阅读全层/PNG/全部palette/地形/动线。','无历史member命中不证明未研究或语义独立，仍需旧ID/同族比较。','床和lit炉块同时出现不能证明同居住空间可达/烤火位/火安全/入口或地形已验。'],new_complete_whole_studies=0,formal_credit_added=0))
put('active-checkpoint.json',dict(batch=300,status='BOUNDED_HEADER_SCREEN_ONLY_NOT_WHOLE',screened=len(entries),new_complete_whole_studies=0,formal_credit_added=0,tasks_deleted=0,next='实际读筛选结果，只有真正相近且非旧同族的完整居住/烤火空间才进入全源研究；否则保存明确bounded缺口。'))
print('SCREENED',len(entries))
for e in entries:print(e['source']['member'],e['source']['size'],'beds',e['beds'],'heating',e['heating'],'lit',e['lit_heating'])

import json,hashlib,sys,importlib.util
from pathlib import Path
from zipfile import ZipFile
P=Path('/Users/a15356015027/Desktop/dynasty/docs/architecture/research-20261104-smithy-283');P.mkdir(exist_ok=False);R=P.parents[2];PRE=P.parent/'research-20261104-smithy-282'
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
a=next(a for a in json.loads((PRE/'additional-smith-history-screen.json').read_text())['rows']if a['id']=='S019');sys.path.insert(0,str(R/'tools/architecture'));from nbt_read import read
from whole_building_candidates import AIR,plans
sp=importlib.util.spec_from_file_location('v',R/'docs/architecture/research-20261101-task-map/inspect_expanded_sources.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
assert bind(a['source_archive'])==a['fixed_archive']
with ZipFile(a['source_archive'])as z:
 raw=z.read(a['member']);assert hashlib.sha256(raw).hexdigest()==a['nbt_sha256'];d=read(raw);pal=d['palette'];cells={tuple(b['pos']):pal[b['state']]['Name']for b in d['blocks']if pal[b['state']]['Name']not in AIR}
 for y in range(0,12,2):plans(cells,d['size'],y,'S019').save(P/f'S019-y{y}.png')
 v.vertical(cells,d['size'],'S019').save(P/'S019-vertical.png')
 put('source.json',{'source':a,'decoded_original':d,'previous282_receipt':bind(PRE/'RECEIPT.json'),'previous_bound_views_reused_not_new_credit':[bind(PRE/f'S019-{n}.png')for n in ['whole','cutaway']]})
 loc='kaisyn:village/exclusives/rustic/professions_misc/rustic_armorer_1';ctx=[]
 for n in z.namelist():
  if n.endswith('.json')and ('/worldgen/'in n)and loc in z.read(n).decode(errors='replace'):
   bb=z.read(n);j=json.loads(bb);ctx.append({'member':n,'sha256':hashlib.sha256(bb).hexdigest(),'json':j});print('PARENT',n,json.dumps(j))
 for n in z.namelist():
  if n.endswith('.json')and '/worldgen/structure/'in n and 'rustic'in n:
   bb=z.read(n);j=json.loads(bb);ctx.append({'member':n,'sha256':hashlib.sha256(bb).hexdigest(),'json':j});print('ROOT',n,json.dumps(j))
 put('direct-context.json',{'contexts':ctx,'not_all_generation_dependencies_read':True})
print('DV',d['DataVersion'],'size',d['size'],'stored',len(d['blocks']),'palette',len(pal),'entities',d.get('entities',[]))
for i,p in enumerate(pal):print(i,json.dumps(p,separators=(',',':')))
print('BE')
for b in d['blocks']:
 if 'nbt'in b:print(b)
print('ALL300 state matrix; ? omitted')
m={tuple(b['pos']):b['state']for b in d['blocks']}
for y in range(12):
 print('y',y)
 for zz in range(5):print(zz,' '.join(str(m.get((x,y,zz),'?'))for x in range(5)))

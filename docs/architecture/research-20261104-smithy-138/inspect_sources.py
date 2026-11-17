"""Original fixed-local NBT/context and class-color diagrams; no game or product writes."""
import sys,json,hashlib,importlib.util
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,iso,plans
spec=importlib.util.spec_from_file_location('sections',ROOT/'docs/architecture/research-20261101-task-map/inspect_expanded_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,default=lambda value: {'__original_nbt_byte_array_hex__':value.hex()} if isinstance(value,bytes) else (_ for _ in ()).throw(TypeError(type(value).__name__)))+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
previous=ROOT/'docs/architecture/research-20261104-smithy-137';put('previous-checkpoint.json',{'receipt':bind(previous/'RECEIPT.json'),'cumulative_not_reset':True})
put('protected-inputs.json',{'files':[bind(ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json'),bind(previous/'RECEIPT.json')]+[bind(p)for p in sorted(Path('/Users/a15356015027/Desktop/code x提示词').glob('cod[1-6].txt'))]})
rows=[];raws=[];contexts=[];metadata=[]
for a in json.loads((OUT/'pre-render-history-screen.json').read_text())['rows']:
 assert a['eligible_for_new_source_study'];jar=a['source_archive'];assert bind(jar)==a['fixed_archive'];ident=a['id'];member=a['member'];ns,sub=member[5:].split('/structures/');location=ns+':'+sub[:-4]
 with ZipFile(jar)as z:
  names=set(z.namelist());b=z.read(member);assert hashlib.sha256(b).hexdigest()==a['nbt_sha256'];d=read(b);pal=d.get('palette')or d['palettes'][0];counts=Counter(pal[x['state']]['Name']for x in d['blocks']);air=sum(v for k,v in counts.items()if k in AIR)
  row={'id':ident,'source_archive':jar,'source_archive_sha256':a['fixed_archive']['sha256'],'member':member,'nbt_sha256':a['nbt_sha256'],'size':d['size'],'DataVersion':d['DataVersion'],'purpose':'COD3 NPC01 老陈 山脚铁匠铺完整功能空间参考','formal_credit_added':0};rows.append(row);raws.append({**row,'nbt_decoded_original':d,'air':air,'nonair':len(d['blocks'])-air,'material_counts':dict(counts)})
  for n in ['META-INF/mods.toml','fabric.mod.json','pack.mcmeta']:
   if n in names:
    bb=z.read(n);metadata.append({'id':ident,'source_archive':jar,'member':n,'sha256':hashlib.sha256(bb).hexdigest(),'original_text':bb.decode()})
  if '--records-only' not in sys.argv:
   cells={tuple(x['pos']):pal[x['state']]['Name']for x in d['blocks']if pal[x['state']]['Name']not in AIR};rev={(d['size'][0]-1-x,y,d['size'][2]-1-zz):n for(x,y,zz),n in cells.items()}
   whole=Image.new('RGB',(1520,1360),'#edf0f2')
   for k,(cc,rot)in enumerate([(cells,0),(cells,1),(rev,0),(rev,1)]):whole.paste(iso(cc,d['size'],rot,f'{ident} whole view{k}; full-cell approximation'),((k%2)*760,(k//2)*680))
   whole.save(OUT/f'{ident}-whole.png');cut=Image.new('RGB',(1520,1360),'#edf0f2');low=3;high=7
   for k,(level,rot)in enumerate([(low,0),(low,1),(high,0),(high,1)]):cut.paste(iso(cells,d['size'],rot,f'{ident} cut <=y{level}',cutoff=level),((k%2)*760,(k//2)*680))
   cut.save(OUT/f'{ident}-cutaway.png')
   for y in range(0,d['size'][1],2):plans(cells,d['size'],y,ident).save(OUT/f'{ident}-y{y}.png')
   m.vertical(cells,d['size'],ident).save(OUT/f'{ident}-vertical.png')
  wanted=['data/terralith/worldgen/structure/fortified_desert_village.json','data/terralith/worldgen/template_pool/village/desert/houses.json','data/terralith/worldgen/template_pool/village/desert/starts.json']
  for x in d['blocks']:
   for key,kind in [('pool','worldgen/template_pool'),('LootTable','loot_tables')]:
    v=x.get('nbt',{}).get(key)
    if isinstance(v,str)and ':'in v and v!='minecraft:empty':ns2,path=v.split(':',1);wanted.append(f'data/{ns2}/{kind}/{path}.json')
  seen=set();saved=[];missing=[]
  while wanted:
   n=wanted.pop(0)
   if n in seen:continue
   seen.add(n)
   if n not in names:missing.append(n);continue
   bb=z.read(n);j=json.loads(bb);saved.append({'member':n,'sha256':hashlib.sha256(bb).hexdigest(),'json':j})
   def walk(v):
    if isinstance(v,dict):
     for k,w in v.items():
      if k in ['processors','pillar_processor_list']and isinstance(w,str)and ':'in w and w!='minecraft:empty':ns2,path=w.split(':',1);wanted.append(f'data/{ns2}/worldgen/processor_list/{path}.json')
      if k=='biomes'and isinstance(w,str)and w.startswith('#'):ns2,path=w[1:].split(':',1);wanted.append(f'data/{ns2}/tags/worldgen/biome/{path}.json')
      walk(w)
    elif isinstance(v,list):
     for w in v:walk(w)
   if '/template_pool/'in n and any(e.get('element',{}).get('location')==location for e in j.get('elements',[])):
    for e in j['elements']:
     if e.get('element',{}).get('location')==location:walk(e)
   else:walk(j)
  contexts.append({'id':ident,'source_archive':jar,'location':location,'contexts':saved,'missing':missing})
  print(ident,member,'size',d['size'],'records',len(d['blocks']),'air',air,'nonair',len(d['blocks'])-air,'entities',len(d.get('entities',[])))
  print('CONTEXTS',[c['member']for c in saved],'MISSING',missing)
put('sources.json',{'candidates':rows,'metadata_only_not_credit':True});put('raw-source-audit.json',{'candidates':raws});put('source-context.json',{'metadata':metadata,'candidates':contexts});put('active-checkpoint.json',{'batch':138,'status':'SOURCE_VIEWS_SAVED_MANUAL_REVIEW_PENDING','formal_credit_added':0,'java_run':False,'all_tasks_complete':False});print('CURRENT_PNG',len(list(OUT.glob('*.png'))))

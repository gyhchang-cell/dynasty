"""Offline original-source inspection only. No world, Java or product files."""
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
def put(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
prev=ROOT/'docs/architecture/research-20261104-smithy-074';put('previous-checkpoint.json',{'receipt':bind(prev/'RECEIPT.json'),'formal_credit_added':0,'cumulative_not_reset':True})
put('protected-inputs.json',{'files':[bind(p)for p in [ROOT/'docs/architecture/continuation-20261022/references/full-buildings.json',prev/'RECEIPT.json']]+[bind(p)for p in sorted(Path('/Users/a15356015027/Desktop/code x提示词').glob('cod[1-6].txt'))]})
discovery=json.loads((prev/'pre-render-history-screen.json').read_text());jar=discovery['fixed_archive']['path'];actual=bind(jar)['sha256'];assert actual==discovery['fixed_archive']['sha256']
rows=[];raws=[];contexts=[]
with ZipFile(jar)as z:
 names=set(z.namelist());md=z.read('META-INF/mods.toml')
 for i,(theme,basename) in enumerate([('swamp_vanilla','swamp_armorer_1'),('swamp_vanilla','swamp_toolsmith_1'),('swamp_vanilla','swamp_weaponsmith_1')],1):
  ident=f'F{i:02d}';location=f'trek:village/{theme}/houses/{basename}';member='data/trek/structures/'+location.split(':')[1]+'.nbt';screen=json.loads((OUT/'pre-render-history-screen.json').read_text());eligible=next(v for v in screen['rows']if v['canonical_member']==member);assert eligible['eligible_for_new_source_study']and not eligible['known_history'];b=z.read(member);assert hashlib.sha256(b).hexdigest()==eligible['original_nbt_sha256'];d=read(b);pal=d.get('palette')or d['palettes'][0];counts=Counter(pal[x['state']]['Name']for x in d['blocks']);air=sum(v for k,v in counts.items()if k in AIR)
  row={'id':ident,'source_archive':jar,'source_archive_sha256':actual,'member':member,'nbt_sha256':hashlib.sha256(b).hexdigest(),'size':d['size'],'DataVersion':d['DataVersion'],'purpose':'COD3 NPC01 老陈 山脚铁匠铺空间参考','formal_credit_added':0};rows.append(row);raws.append({**row,'nbt_decoded_original':d,'air':air,'nonair':len(d['blocks'])-air,'material_counts':dict(counts)})
  cells={tuple(x['pos']):pal[x['state']]['Name']for x in d['blocks']if pal[x['state']]['Name']not in AIR}
  reversedcells={(d['size'][0]-1-x,y,d['size'][2]-1-zz):n for(x,y,zz),n in cells.items()}
  whole=Image.new('RGB',(1520,1360),'#edf0f2')
  for k,(cc,rot)in enumerate([(cells,0),(cells,1),(reversedcells,0),(reversedcells,1)]):whole.paste(iso(cc,d['size'],rot,f'{ident} whole view{k}; full-cell approximation'),((k%2)*760,(k//2)*680))
  whole.save(OUT/(ident+'-whole.png'))
  cut=Image.new('RGB',(1520,1360),'#edf0f2')
  for k,(level,rot)in enumerate([(3,0),(3,1),(7,0),(7,1)]):cut.paste(iso(cells,d['size'],rot,f'{ident} cut <=y{level}',cutoff=level),((k%2)*760,(k//2)*680))
  cut.save(OUT/(ident+'-cutaway.png'))
  for level in range(0,d['size'][1],2):plans(cells,d['size'],level,ident).save(OUT/f'{ident}-y{level}.png')
  m.vertical(cells,d['size'],ident).save(OUT/(ident+'-vertical.png'))
  wanted=[f'data/trek/worldgen/template_pool/village/{theme}/houses.json',f'data/trek/worldgen/template_pool/village/{theme}/town_centers.json',f'data/trek/worldgen/structure/village/{theme}.json'];seen=set();saved=[];missing=[]
  # Include exact connector pools and loottables. Connector metadata is not a building count.
  for x in d['blocks']:
   n=x.get('nbt',{})
   for key,kind in [('pool','worldgen/template_pool'),('LootTable','loot_tables')]:
    v=n.get(key)
    if isinstance(v,str)and ':'in v and v!='minecraft:empty':ns,path=v.split(':',1);wanted.append(f'data/{ns}/{kind}/{path}.json')
  while wanted:
   member2=wanted.pop(0)
   if member2 in seen:continue
   seen.add(member2)
   if member2 not in names:missing.append(member2);continue
   b2=z.read(member2);j=json.loads(b2);saved.append({'member':member2,'sha256':hashlib.sha256(b2).hexdigest(),'json':j})
   # Follow processor references, but do not expand unrelated whole villages or count their pieces.
   def walk(v):
    if isinstance(v,dict):
     for k,w in v.items():
      if k in ['processors','pillar_processor_list']and isinstance(w,str)and ':'in w and w!='minecraft:empty':ns,path=w.split(':',1);wanted.append(f'data/{ns}/worldgen/processor_list/{path}.json')
      walk(w)
    elif isinstance(v,list):
     for w in v:walk(w)
   walk(j)
  contexts.append({'id':ident,'location':location,'contexts':saved,'missing':missing})
  print(ident,member,d['size'],'records',len(d['blocks']),'air',air,'materials',json.dumps(dict(counts)))
  for x in d['blocks']:
   s=pal[x['state']]
   if s['Name']=='minecraft:jigsaw':print('CONNECTOR',x['pos'],json.dumps(s),json.dumps(x.get('nbt')))
put('sources.json',{'candidates':rows,'metadata_only_not_credit':True});put('raw-source-audit.json',{'candidates':raws});put('source-context.json',{'metadata':{'member':'META-INF/mods.toml','sha256':hashlib.sha256(md).hexdigest(),'original_text':md.decode()},'candidates':contexts});put('active-checkpoint.json',{'batch':75,'status':'SOURCE_VIEWS_SAVED_MANUAL_REVIEW_PENDING','formal_credit_added':0,'java_run':False,'all_tasks_complete':False});print('PNGS',len(list(OUT.glob('*.png'))))

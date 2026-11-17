"""Read original two-piece connection topology and render research-only assembly; credit stays zero."""
import sys,json,hashlib,importlib.util
from pathlib import Path
from zipfile import ZipFile
from collections import Counter
from PIL import Image
P=Path(__file__).resolve().parent;R=P.parents[2];assert not(P/'RECEIPT.json').exists();sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
from whole_building_candidates import AIR,iso
sp=importlib.util.spec_from_file_location('section',R/'docs/architecture/research-20261101-task-map/inspect_expanded_sources.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec)
def put(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def bind(p):
 b=Path(p).read_bytes();return {'path':str(Path(p).resolve()),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
screen=json.loads((P/'pre-render-history-screen.json').read_text());parts=[];cells={};originals=[];contexts=[]
for i,a in enumerate(screen['rows']):
 assert a['eligible_for_new_source_study'] and bind(a['source_archive'])==a['fixed_archive']
 with ZipFile(a['source_archive'])as z:
  bb=z.read(a['member']);assert hashlib.sha256(bb).hexdigest()==a['nbt_sha256'];d=read(bb);pal=d['palette'];c=Counter(pal[b['state']]['Name']for b in d['blocks']);jig=[{'pos':b['pos'],'state':pal[b['state']],'nbt':b['nbt']}for b in d['blocks']if pal[b['state']]['Name']=='minecraft:jigsaw'];main=[b for b in jig if b['nbt']['pool'].endswith('/illager_windmill_main')];assert len(main)==1
  parts.append({'id':a['id'],'member':a['member'],'archive':a['fixed_archive'],'nbt_sha256':a['nbt_sha256'],'size':d['size'],'DataVersion':d['DataVersion'],'palette_count':len(pal),'stored':len(d['blocks']),'air':sum(c[k]for k in AIR),'nonair':sum(v for k,v in c.items()if k not in AIR),'omitted':48*32*34-len(d['blocks']),'entities':len(d['entities']),'material_counts':dict(c),'main_connector':main[0],'jigsaw_count':len(jig),'block_entity_count':sum('nbt'in b for b in d['blocks'])});originals.append({'id':a['id'],'member':a['member'],'nbt_decoded_original':d})
  for b in d['blocks']:
   if pal[b['state']]['Name']not in AIR:
    pos=(b['pos'][0],b['pos'][1]+32*i,b['pos'][2]);assert pos not in cells;cells[pos]=pal[b['state']]['Name']
  if i==0:
   for n in ['data/dungeons_arise/worldgen/structure/illager_windmill.json','data/dungeons_arise/worldgen/template_pool/prairie/illager_windmill/illager_windmill_start.json','data/dungeons_arise/worldgen/template_pool/prairie/illager_windmill/illager_windmill_main.json','data/dungeons_arise/worldgen/template_pool/prairie/illager_windmill/illager_windmill_fields.json','data/dungeons_arise/worldgen/template_pool/prairie/illager_windmill/illager_windmill_spawners.json','data/dungeons_arise/tags/worldgen/biome/has_structure/illager_windmill_biomes.json']:
    b=z.read(n);contexts.append({'member':n,'sha256':hashlib.sha256(b).hexdigest(),'json':json.loads(b)})
lo,hi=[x['main_connector']for x in parts];assert lo['pos']==[0,31,33]and hi['pos']==[0,0,33]and lo['state']['Properties']['orientation']=='up_south'and hi['state']['Properties']['orientation']=='down_south'and lo['nbt']['target']==hi['nbt']['name']and hi['nbt']['target']==lo['nbt']['name'];assert lo['nbt']['joint']==hi['nbt']['joint']=='aligned'
put('original-two-part-source.json',{'parts':originals});put('source-topology.json',{'parts':parts,'contexts':contexts,'derived_identity_rotation':True,'derived_upper_translation':[0,32,0],'basis':'matching name/target, opposed up/down front, aligned common south top; adjacent connector positions, no rotation needed','research_composite_size':[48,64,34],'part_count':2,'whole_building_credit':0,'assembly_not_executed_in_game':True,'fields_and_spawners_not_references':True,'all_original_layers_or_palette_states_read':False,'no_product_asset_written':True})
size=[48,64,34];rev={(47-x,y,33-z):n for(x,y,z),n in cells.items()};whole=Image.new('RGB',(1520,1360),'#edf0f2')
for k,(c,rot)in enumerate([(cells,0),(cells,1),(rev,0),(rev,1)]):whole.paste(iso(c,size,rot,f'DA mill joint-derived two-part composite {k}; research only'),((k%2)*760,(k//2)*680))
whole.save(P/'assembly-whole.png');cut=Image.new('RGB',(1520,1360),'#edf0f2')
for k,(y,rot)in enumerate([(15,0),(31,1),(40,0),(50,1)]):cut.paste(iso(cells,size,rot,f'joint-derived composite <=y{y}; no credit',cutoff=y),((k%2)*760,(k//2)*680))
cut.save(P/'assembly-cutaway.png');sec.vertical(cells,size,'DA mill composite').save(P/'assembly-vertical.png')
put('active-checkpoint.json',{'batch':157,'status':'ORIGINAL_JOINT_TOPOLOGY_READ_ASSEMBLY_VIEWS_PENDING','complete_whole_reference_studies':0,'formal_credit_added':0,'source_fragments_not_counted_as_buildings':True,'all_original_layers_read':False,'java_run':False,'next':'Actually inspect three overall diagrams, then preserve bounded topology milestone; full palette/floors/BE/accessibility and whole-family comparison still required.'})
print(json.dumps({'parts':[{k:v for k,v in p.items()if k not in ['material_counts','archive']}for p in parts],'contexts':contexts},ensure_ascii=False,indent=2))

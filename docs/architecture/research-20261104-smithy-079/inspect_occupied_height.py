import sys,json,importlib.util
from pathlib import Path
from PIL import Image
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
assert not (OUT/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from whole_building_candidates import AIR,iso
spec=importlib.util.spec_from_file_location('sections',ROOT/'docs/architecture/research-20261101-task-map/inspect_expanded_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=json.loads((OUT/'raw-source-audit.json').read_text())['candidates'][1];d=a['nbt_decoded_original'];pal=d['palette'];cells={tuple(b['pos']):pal[b['state']]['Name']for b in d['blocks']if pal[b['state']]['Name']not in AIR};size=[d['size'][0],1+max(p[1]for p in cells),d['size'][2]];rev={(size[0]-1-x,y,size[2]-1-z):n for(x,y,z),n in cells.items()};im=Image.new('RGB',(1520,1360),'#edf0f2')
for k,(cc,rot)in enumerate([(cells,0),(cells,1),(rev,0),(rev,1)]):im.paste(iso(cc,size,rot,'F02 occupied envelope; original NBT unchanged'),((k%2)*760,(k//2)*680))
im.save(OUT/'F02-occupied-whole.png');m.vertical(cells,size,'F02 occupied envelope only').save(OUT/'F02-occupied-vertical.png')
(OUT/'occupied-height-boundary.json').write_text(json.dumps({'id':'F02','original_size':d['size'],'visualization_envelope':size,'all_original_records_preserved':True,'nonair_above_y12':sum(p[1]>12 for p in cells),'not_40_storeys':True,'generated_png_total':33,'planned_actual_view_count':20,'upper_generated_empty_plans_not_claimed_viewed':list('F02-y'+str(y)+'.png'for y in range(14,40,2))},ensure_ascii=False,indent=2)+'\n')

import json,sys,itertools,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[2];assert not(P/'RECEIPT.json').exists()
sys.path.insert(0,str(ROOT/'tools/architecture'))
from whole_building_candidates import iso,plans,AIR
spec=importlib.util.spec_from_file_location('sections',ROOT/'docs/architecture/research-20261101-task-map/inspect_expanded_sources.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=json.loads((P/'raw-source-audit.json').read_text())['candidates'];origins=[(0,0,0),(2,-14,4),(0,-20,-4)];allcells={};out=[]
for r,o in zip(rows,origins):
 d=r['nbt_decoded_original'];pal=d['palette'];blocks={tuple(b['pos']):b for b in d['blocks']};ident=r['id'];sx,sy,sz=d['size'];lines=['Original indices; ?=omitted NOTair; each z row columns x.']
 for y in range(sy):
  lines.append(f'y={y}')
  for z in range(sz):lines.append(f'z{z}: '+','.join(f'{v}x{len(list(g))}'for v,g in itertools.groupby([blocks.get((x,y,z),{}).get('state','?')for x in range(sx)])))
 (P/f'{ident}-full-layer-index-rle.txt').write_text('\n'.join(lines)+'\n')
 cells={p:pal[b['state']]['Name']for p,b in blocks.items()if pal[b['state']]['Name']not in AIR}
 board=Image.new('RGB',(760*min(sy,3),680*((sy+2)//3)),'#edf0f2')
 for y in range(sy):board.paste(plans(cells,d['size'],y,ident),(760*(y%3),680*(y//3)))
 # plans size may differ: resize forbidden here; board sizes derive actual panels below
 panels=[plans(cells,d['size'],y,ident)for y in range(sy)];w,h=panels[0].size;board=Image.new('RGB',(w*min(sy,3),h*((sy+2)//3)),'#edf0f2')
 for y,panel in enumerate(panels):board.paste(panel,(w*(y%3),h*(y//3)))
 board.save(P/f'{ident}-all-plans.png')
 for (x,y,z),name in cells.items():
  q=(x+o[0],y+o[1]+20,z+o[2]+4);assert q not in allcells;allcells[q]=name
 out.append(dict(id=ident,source_origin=list(o),normalized_origin=[o[0],o[1]+20,o[2]+4],size=d['size'],stored=len(blocks),declared=sx*sy*sz))
size=[8,25,12];whole=Image.new('RGB',(1520,1360),'#edf0f2');rev={(7-x,y,11-z):n for(x,y,z),n in allcells.items()}
for i,(cells,rot)in enumerate([(allcells,0),(allcells,1),(rev,0),(rev,1)]):whole.paste(iso(cells,size,rot,'218 derived one short-shaft assembly; ORIGINAL jigsaws'),(760*(i%2),680*(i//2)))
whole.save(P/'whole-assembly.png');cut=Image.new('RGB',(1520,1360),'#edf0f2')
for i,(y,rot)in enumerate([(2,0),(2,1),(21,0),(21,1)]):cut.paste(iso(allcells,size,rot,f'218 normalized cutoff {y}; original jigsaws',cutoff=y),(760*(i%2),680*(i//2)))
cut.save(P/'whole-cutaway.png');m.vertical(allcells,size,'218 ORIGINAL normalized composite').save(P/'whole-vertical.png')
(P/'derived-assembly.json').write_text(json.dumps(dict(pieces=out,source_bounds_min=[0,-20,-4],source_bounds_max=[7,4,7],size=size,derivation=['top origin=(0,0,0)','middle=top+(3,0,5)+(0,-1,0)-(1,13,1)=(2,-14,4)','basement=middle+(1,0,1)+(0,-1,0)-(3,5,9)=(0,-20,-4)'],stored=sum(a['stored']for a in out),piece_declared=sum(a['declared']for a in out),bounding_volume=2400,territory_outside_piece_boxes=1466,one_whole_only=True,source_jigsaws_preserved=True,all_final_ladders_no_explicit_facing=True,worldgen_and_processor_implementation_unverified=True),ensure_ascii=False,indent=2)+'\n')
print('6 diagrams',[(f.name,Image.open(f).size)for f in P.glob('*.png')]);print('3 RLE tables generated')

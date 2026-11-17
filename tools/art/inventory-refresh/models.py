"""Authored, single-block site decorations; same IDs, interactions and blockstates.

No raster artwork generation. Models use vanilla pixel materials at native density.
Run this file to reproduce the geometry and inventory parents only.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
ASSET=ROOT/'src/main/resources/assets/dynasty'
DOC=ROOT/'docs/art/inventory-refresh-v1'
MATERIALS={'wood':'spruce_planks','cut':'stripped_spruce_log','end':'stripped_spruce_log_top',
 'oak':'oak_planks','dark':'dark_oak_planks','iron':'iron_block','metal':'gray_terracotta',
 'bronze':'copper_block','patina':'weathered_copper','leather':'brown_terracotta',
 'stone':'stone_bricks','moss':'mossy_stone_bricks','carved':'chiseled_stone_bricks',
 'slate':'deepslate_tiles','paper':'white_wool','red':'red_wool','tea':'cyan_terracotta',
 'soil':'dirt','leaf':'moss_block','gold':'raw_gold_block','coal':'coal_block'}
def box(x,y,z,X,Y,Z,tex='wood',**extra):
 assert all(a<b for a,b in zip((x,y,z),(X,Y,Z)))
 return {'from':[x,y,z],'to':[X,Y,Z],'faces':{f:{'texture':'#'+tex} for f in ('north','south','east','west','up','down')},**extra}
def posts(x0,x1,z0,z1,top,tex='cut'):
 return [box(x,0,z,x+2,top,z+2,tex) for x in (x0,x1) for z in (z0,z1)]
def ring(x,y,z,size,thick,tex='bronze'):
 # Square/stepped ring with actual negative space; no cylinder or filled disk.
 return [box(x,y,z,x+size,y+thick,z+thick,tex),box(x,y+size-thick,z,x+size,y+size,z+thick,tex),
         box(x,y+thick,z,x+thick,y+size-thick,z+thick,tex),box(x+size-thick,y+thick,z,x+size,y+size-thick,z+thick,tex)]
def site_models():
 m={}
 # Bellows: wooden lower/upper boards, three clearly separated leather pleats,
 # bronze nozzle and linked top handle. Overall14x11x12, low stable base.
 b=[box(1,0,3,13,2,13),box(1,8,3,13,10,13),box(2,2,4,12,8,12,'leather')]
 for y in (2,4,6):b += [box(1,y,3,13,y+1,13,'dark')]
 b += [box(12,3,6,14,7,10,'bronze'),box(14,4,7,16,6,9,'metal'),box(3,10,7,5,12,9,'cut'),box(3,12,7,10,13,9,'cut'),box(9,10,7,10,12,9,'bronze')]
 m['old_bellows']=b
 # Waterwheel: two bearing stands, cross axle and eight coarse paddles around
 # an open rim. The missing upper-right paddle visibly explains 'broken'.
 b=[box(0,0,4,16,2,12,'slate'),box(1,2,6,3,10,10,'cut'),box(13,2,6,15,10,10,'cut'),box(0,8,7,16,10,9,'bronze')]
 wheel=[]
 for y,z,Y,Z in [(3,6,4,10),(14,6,15,10),(6,2,12,3),(6,13,12,14),(4,3,6,5),(12,3,14,5),(4,11,6,13)]:
  wheel.append(box(5,y,z,11,Y,Z,'wood'))
 wheel += [box(6,3,7,10,15,9,'cut'),box(6,8,2,10,10,14,'cut'),box(4,7,6,12,11,10,'patina')]
 b += wheel;m['broken_waterwheel']=b
 m['broken_waterwheel_repaired']=b+[box(5,12,11,11,14,13,'wood')]
 # Rack: connected frame, two distinct upright hafts with steel blade/head.
 b=[box(1,0,2,15,2,5,'dark'),box(1,0,11,15,2,14,'dark')]+posts(2,12,3,10,13)
 b += [box(2,11,3,14,13,5),box(4,2,7,5,14,8,'cut'),box(9,2,7,10,12,8,'cut'),box(4,13,6,5,16,9,'iron'),box(8,11,6,12,14,9,'metal')]
 m['old_weapon_rack']=b
 # Abandoned armour bench with a dented open helmet, stacked plates and rack.
 b=posts(1,12,2,11,7)+[box(0,7,1,16,9,15),box(2,9,4,7,10,11,'metal'),box(3,10,4,7,13,6,'metal'),box(2,10,6,3,13,10,'metal'),box(3,13,5,7,14,10,'iron'),box(8,9,5,14,10,12,'patina'),box(9,10,6,13,11,11,'patina')]
 m['abandoned_armory']=b
 # Small mechanism box: iron-banded timber chest, exposed top gear and catch.
 b=[box(2,0,2,14,2,14,'dark'),box(3,2,3,13,9,13),box(2,9,2,14,11,14,'cut')]
 for x in (3,11):b.append(box(x,2,2.5,x+1,10,13.5,'metal'))
 b += ring(5,4,2,6,1,'bronze')+[box(7,6,1.5,9,8,3,'iron'),box(5,11,5,11,12,11,'bronze'),box(4,11,7,12,12,9,'bronze'),box(7,11,4,9,12,12,'bronze'),box(7,12,7,9,13,9,'metal')]
 m['puzzle_box']=b
 # Shrine: framed hollow alcove, broad two-step roof, votive and incense.
 b=[box(1,0,2,15,2,14,'stone'),box(2,2,11,14,11,13,'moss'),box(2,2,3,4,11,12,'cut'),box(12,2,3,14,11,12,'cut'),box(0,11,1,16,13,15,'slate'),box(2,13,3,14,15,13,'slate'),box(6,2,7,10,7,10,'carved'),box(6,2,4,10,4,6,'bronze'),box(7,4,5,8,7,6,'coal')]
 m['wayside_shrine']=b
 m['nameless_tomb']=[box(1,0,1,15,2,15,'moss'),box(2,2,4,14,4,13,'soil'),box(4,4,6,12,5,12,'leaf'),box(4,2,2,12,11,5,'stone'),box(5,11,2,11,13,5,'stone'),box(6,5,1.5,10,9,2,'slate')]
 # Scar is physically recessed between separate stone sections, not a flat icon.
 m['sword_scar_wall']=[box(1,0,3,15,2,13,'stone'),box(2,2,6,7,14,11,'moss'),box(8,2,6,14,14,11,'stone'),box(7,2,8,8,14,11,'slate'),box(2,14,5,14,16,12,'stone')]
 m['broken_stele']=[box(1,0,2,15,3,14,'moss'),box(4,3,6,12,10,10,'stone'),box(4,10,6,8,15,10,'stone'),box(8,10,6,10,12,10,'stone'),box(5,5,5.5,11,8,6,'carved'),box(11,3,3,14,5,6,'stone')]
 m['battlefield_remnant']=[box(1,0,2,15,1,14,'soil'),box(3,1,5,4,15,6,'cut'),box(4,10,5,10,14,6,'red'),box(4,8,5,7,10,6,'red'),box(8,1,7,13,3,12,'metal'),box(9,3,8,12,4,11,'patina'),box(5,1,9,6,5,10,'cut'),box(4,5,9,7,6,10,'iron')]
 m['herb_spot']=[box(2,0,2,14,1,14,'soil'),box(3,1,3,6,2,7,'leaf'),box(8,1,7,12,2,12,'leaf'),box(5,1,6,6,5,7,'cut'),box(3,3,5,8,4,8,'leaf'),box(9,1,9,10,6,10,'cut'),box(7,4,8,12,5,11,'leaf')]
 # Low open funerary bier with wrapped body/cloth cap, small incense bowl.
 m['mortuary_room']=posts(2,12,3,10,4)+[box(1,4,2,15,6,14,'dark'),box(4,6,4,12,8,11,'paper'),box(5,8,5,11,9,10,'paper'),box(5,6,11,11,10,13,'dark'),box(2,6,2,5,8,4,'bronze')]
 m['ghost_market_boat']=[box(2,0,4,14,2,12,'dark'),box(0,2,4,16,5,6),box(0,2,10,16,5,12),box(0,2,6,2,5,10),box(14,2,6,16,5,10),box(3,2,6,5,3,10,'cut'),box(11,2,6,13,3,10,'cut'),box(8,2,7,9,15,8,'cut'),box(5,12,7,13,13,8,'cut'),box(5,8,7,8,12,8,'paper'),box(10,9,7,12,12,9,'red'),box(10,8,7,12,9,9,'bronze')]
 m['wayside_tea_stall']=posts(2,12,2,12,9)+[box(1,9,1,15,11,15),box(5,11,5,9,14,9,'tea'),box(6,14,6,8,15,8,'bronze'),box(9,12,6,11,13,8,'tea'),box(11,11,10,14,13,13,'paper'),box(11,13,10,14,13.5,13,'leather'),box(2,11,10,4,13,12,'paper')]
 m['wayside_tea_stall_overturned']=[{**e,'from':[e['from'][0],e['from'][2],16-e['to'][1]],'to':[e['to'][0],e['to'][2],16-e['from'][1]]} for e in m['wayside_tea_stall']]
 # Well: true hollow curb, continuous uprights, crossbar, rope and bucket.
 m['ancient_well']=[box(1,0,1,15,6,4,'moss'),box(1,0,12,15,6,15,'stone'),box(1,0,4,4,6,12,'stone'),box(12,0,4,15,6,12,'moss'),box(1,6,7,3,14,9,'cut'),box(13,6,7,15,14,9,'cut'),box(1,13,7,15,15,9,'cut'),box(7,6,7,8,14,8,'leather'),box(5,3,5,10,4,10,'dark'),box(5,4,5,6,7,10),box(9,4,5,10,7,10),box(6,4,5,9,7,6),box(6,4,9,9,7,10)]
 return m
def write(path,data):
 if path.exists():
  backup=DOC/'before'/path.relative_to(ASSET);backup.parent.mkdir(parents=True,exist_ok=True)
  if not backup.exists():backup.write_bytes(path.read_bytes())
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def publish_sites():
 models=site_models();report=[]
 for ident,elements in models.items():
  aliases={k:'minecraft:block/'+v for k,v in MATERIALS.items() if any(f['texture']=='#'+k for e in elements for f in e['faces'].values())}
  model={'parent':'minecraft:block/block','ambientocclusion':True,'textures':{**aliases,'particle':next(iter(aliases.values()))},'elements':elements}
  write(ASSET/'models/block'/f'{ident}.json',model)
  if ident.endswith(('_overturned','_repaired')):continue
  write(ASSET/'models/item'/f'{ident}.json',{'parent':'dynasty:block/'+ident})
  if ident=='broken_waterwheel':write(ASSET/'blockstates'/f'{ident}.json',{'variants':{'lit=false':{'model':'dynasty:block/'+ident},'lit=true':{'model':'dynasty:block/broken_waterwheel_repaired'}}})
  report.append({'id':ident,'cuboids':len(elements),'inventory':'Same model via vanilla block/block display inheritance','placed':'Same cuboids, existing interaction preserved'})
 (DOC/'site-models.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('Published',len(report),'site decorations and',len(models)-len(report),'existing-state variants')
if __name__=='__main__':publish_sites()

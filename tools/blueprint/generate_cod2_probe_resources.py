"""Generate minimal framework-test resources using existing Minecraft textures."""
import json
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'src/main/resources'
def write(relative,value):
    path=ROOT/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')
write('data/dynasty/worldgen/structure/dungeon_framework_probe.json',{
    'type':'dynasty:dungeon_probe','biomes':'#minecraft:is_overworld','step':'surface_structures',
    'spawn_overrides':{},'terrain_adaptation':'none'})
write('data/dynasty/loot_tables/dungeons/probe_supplies.json',{'type':'minecraft:chest','pools':[{
    'rolls':2,'entries':[{'type':'minecraft:item','name':'minecraft:bread','weight':4},
                       {'type':'minecraft:item','name':'minecraft:arrow','weight':3}]}]})
write('assets/dynasty/models/block/dungeon_empty.json', {'textures': {}, 'elements': []})
for name,texture in {
    'dungeon_core':'chiseled_deepslate','seal_stone':'chiseled_stone_bricks',
    'shootable_beast_eye':'end_portal_frame_eye','seal_door':'polished_deepslate',
    'resettable_floor':'deepslate_tiles','pressure_trap_emitter':'dispenser_front'}.items():
    write(f'assets/dynasty/models/block/{name}.json',{'parent':'minecraft:block/cube_all','textures':{'all':f'minecraft:block/{texture}'}})
    write(f'assets/dynasty/blockstates/{name}.json',{'multipart':[
        {'when':{'open':'false'},'apply':{'model':f'dynasty:block/{name}'}},
        {'when':{'open':'true'},'apply':{'model':'dynasty:block/dungeon_empty'}}]})
print('Probe structure, marker models and LootTable generated; no natural StructureSet')
test_template=ROOT/'data/dynasty_cod2/structures/bow_ritual_test.nbt'
test_template.parent.mkdir(parents=True,exist_ok=True)
shutil.copyfile(ROOT/'data/dynasty/structures/bow_ritual_test.nbt',test_template)

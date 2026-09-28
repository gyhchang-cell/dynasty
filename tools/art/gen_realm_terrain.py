"""Original realm geology, sparse worldgen and shared navigation names. Idempotent."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/'src/main/resources'
DATA=RES/'data/dynasty'
ASSETS=RES/'assets/dynasty'
REALMS={
 'celestial_dynasty':('celestial_stone','jade_soil','天朝玉岩','灵玉沃土','Celestial Jadestone','Jade Earth'),
 'underworld':('underworld_stone','spirit_soil','幽冥岩','幽魂土','Underworld Slate','Spirit Earth'),
 'jiuxiao':('cloud_stone','star_soil','九霄云岩','星砂地','Cloudstone','Star Earth'),
 'dragon_palace':('tidal_stone','pearl_sand','龙宫潮纹岩','珍珠砂','Tidal Stone','Pearl Sand'),
}

def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def block(name): return {'type':'minecraft:block','result_state':{'Name':'dynasty:'+name}}
def main():
 langs={l:json.loads((ASSETS/f'lang/{l}.json').read_text()) for l in ('zh_cn','en_us')}
 for realm,(stone,soil,sz,gz,se,ge) in REALMS.items():
  for name,zh,en in ((stone,sz,se),(soil,gz,ge)):
   write(ASSETS/f'blockstates/{name}.json',{'variants':{'':{'model':'dynasty:block/'+name}}})
   write(ASSETS/f'models/block/{name}.json',{'parent':'minecraft:block/cube_all','textures':{'all':'dynasty:block/'+name}})
   write(ASSETS/f'models/item/{name}.json',{'parent':'dynasty:block/'+name})
   write(DATA/f'loot_tables/blocks/{name}.json',{'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:item','name':'dynasty:'+name}],'conditions':[{'condition':'minecraft:survives_explosion'}]}]})
   for loc,value in (('zh_cn',zh),('en_us',en)): langs[loc]['block.dynasty.'+name]=value
  path=DATA/f'worldgen/noise_settings/{realm}.json'
  noise=json.loads(path.read_text())
  noise['default_block']={'Name':'dynasty:'+stone}
  noise['surface_rule']={'type':'minecraft:sequence','sequence':[
   {'type':'minecraft:condition','if_true':{'type':'minecraft:vertical_gradient','random_name':'minecraft:bedrock_floor','true_at_and_below':{'above_bottom':0},'false_at_and_above':{'above_bottom':5}},'then_run':{'type':'minecraft:block','result_state':{'Name':'minecraft:bedrock'}}},
   {'type':'minecraft:condition','if_true':{'type':'minecraft:stone_depth','offset':2,'add_surface_depth':False,'secondary_depth_range':0,'surface_type':'floor'},'then_run':block(soil)},
   block(stone)]}
  write(path,noise)
  for loc in langs:
   langs[loc]['travelerstitles.dynasty.'+realm]=langs[loc]['dimension.dynasty.'+realm]
 for loc,values in langs.items(): write(ASSETS/f'lang/{loc}.json',values)
 for tool,ids in (('pickaxe',[r[0] for r in REALMS.values()]),('shovel',[r[1] for r in REALMS.values()])):
  path=RES/f'data/minecraft/tags/blocks/mineable/{tool}.json'
  obj=json.loads(path.read_text()) if path.exists() else {'replace':False,'values':[]}
  obj['values']=list(dict.fromkeys(obj['values']+['dynasty:'+x for x in ids]));write(path,obj)
 # Vanilla carvers/ore replacers must recognize the original rocks, preserving resources.
 for tag in ('base_stone_overworld','stone_ore_replaceables','overworld_carver_replaceables'):
  path=RES/f'data/minecraft/tags/blocks/{tag}.json'
  obj=json.loads(path.read_text()) if path.exists() else {'replace':False,'values':[]}
  obj['values']=list(dict.fromkeys(obj['values']+['dynasty:'+r[0] for r in REALMS.values()]));write(path,obj)
 # Full structures are discoverable in the overworld, not merely tiny feature ruins.
 for tag,ids in (('dirt',['jade_soil','spirit_soil','star_soil']),('sand',['pearl_sand'])):
  path=RES/f'data/minecraft/tags/blocks/{tag}.json'
  obj=json.loads(path.read_text()) if path.exists() else {'replace':False,'values':[]}
  obj['values']=list(dict.fromkeys(obj['values']+['dynasty:'+x for x in ids]));write(path,obj)
 write(DATA/'tags/worldgen/biome/imperial_settlements.json',{'replace':False,'values':['#dynasty:celestial','minecraft:plains','minecraft:sunflower_plains','minecraft:meadow','minecraft:savanna']})
 for name,spacing,separation in [('palace',56,18),('academy',56,18),('great_wall_gate',48,16),('star_altar',52,17),('stone_grove',42,14)]:
  path=DATA/f'worldgen/structure/{name}.json';obj=json.loads(path.read_text())
  if name in ('palace','academy','great_wall_gate'): obj['biomes']='#dynasty:imperial_settlements'
  write(path,obj)
  path=DATA/f'worldgen/structure_set/{name}.json';obj=json.loads(path.read_text())
  obj['placement'].update(spacing=spacing,separation=separation);write(path,obj)
 # Absolute values avoid multiplying rarity on every generator run.
 for path in (DATA/'worldgen/placed_feature').glob('*.json'):
  if path.stem in ('jade_ore','dragon_crystal_ore','imperial_tomb'): continue
  obj=json.loads(path.read_text())
  for entry in obj['placement']:
   if entry['type']=='minecraft:rarity_filter': entry['chance']=max(480,entry['chance'])
  write(path,obj)
 print('Realm geology: 8 custom blocks; title aliases; overworld structures; sparse building features.')

if __name__=='__main__': main()

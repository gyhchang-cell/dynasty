"""Native block geometry with distinct clue silhouettes; uses vanilla textures, no added gameplay systems."""
from pathlib import Path
import json
base=Path('src/main/resources/assets/dynasty')
variants={}
for i in range(45):
 variants[f'kind={i}']={'model':f'dynasty:block/story_anchor_{i}'}
 if i>=30:obj={'parent':'minecraft:block/stone_bricks'}
 else:
  tex=['stone_bricks','chiseled_stone_bricks','mossy_stone_bricks','dark_oak_planks','oak_planks','mushroom_stem','netherrack','cobblestone','water_still','chiseled_stone_bricks','sea_lantern','oak_log','iron_block','anvil','copper_block','stone','soul_sand','bookshelf','spruce_planks','gold_block','oak_log','soul_sand','cauldron_side','obsidian','acacia_log','gold_block','prismarine','chiseled_stone_bricks','bone_block_side','copper_block'][i]
  parts=[]
  def part(a,b):parts.append({'from':a,'to':b,'faces':{f:{'texture':'#all'} for f in ['north','south','east','west','up','down']}})
  if i in [0,1,3,15,19,27]:part([3,0,3],[13,2,13]);part([5,2,6],[11,15,10]);part([4,12,5],[12,14,11])
  elif i in [7,8,22,26]:
   for a,b in [([1,0,1],[15,3,4]),([1,0,12],[15,3,15]),([1,0,4],[4,3,12]),([12,0,4],[15,3,12]),([4,1,4],[12,2,12])]:part(a,b)
  elif i in [10,21,25]:part([3,0,3],[13,2,13]);part([7,2,7],[9,9,9]);part([4,9,4],[12,15,12])
  elif i in [16,24,6]:part([5,0,5],[11,2,11]);part([4,2,4],[12,9,12]);part([6,9,6],[10,13,10])
  elif i in [12,13,29]:part([3,0,3],[13,2,13]);part([4,2,4],[12,8,12]);part([5,8,5],[11,10,11])
  elif i in [4,17,18,28]:part([2,0,4],[14,3,12]);part([3,3,5],[13,5,11])
  elif i in [5,11,20]:part([4,0,4],[12,12,12]);part([2,9,2],[14,12,14])
  else:part([2,0,2],[14,2,14]);part([5,2,5],[11,10,11]);part([3,10,3],[13,12,13])
  obj={'textures':{'all':'minecraft:block/'+tex,'particle':'minecraft:block/'+tex},'elements':parts}
 p=base/f'models/block/story_anchor_{i}.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2)+'\n')
p=base/'blockstates/story_anchor.json';p.write_text(json.dumps({'variants':variants},indent=2)+'\n')

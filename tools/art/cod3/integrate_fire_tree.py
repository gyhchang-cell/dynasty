#!/usr/bin/env python3
"""Build the production placement/visual metadata from the delivered building source manifest."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];D=R/'docs/art/cod3-fire-tree-v2';A=R/'src/main/resources/assets/dynasty';DATA=R/'src/main/resources/data/dynasty'
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def main():
    m=json.loads((D/'geometry.json').read_text());assert m['size']==[47,43,47]
    buds=m['bud_centers'];assert 1<=len(buds)<=64 and all(len(p)==3 and all(0<=v<extent for v,extent in zip(p,m['size'])) for p in buds)
    dump(A/'scenic/fire_tree.json',{'size':m['size'],'bud_centers':buds,'effect_anchor':m['effect_anchor'],'template_sha256':hashlib.sha256((DATA/'structures/scenic_fire_tree.nbt').read_bytes()).hexdigest(),'rotation':'none'})
    dump(DATA/'worldgen/structure/scenic_fire_tree.json',{'type':'dynasty:scenic_fire_tree','biomes':'#dynasty:has_structure/scenic_fire_tree','step':'surface_structures','spawn_overrides':{},'terrain_adaptation':'none'})
    dump(DATA/'worldgen/structure_set/scenic_fire_tree.json',{'structures':[{'structure':'dynasty:scenic_fire_tree','weight':1}],'placement':{'type':'minecraft:random_spread','salt':460091301,'spacing':96,'separation':32}})
    dump(DATA/'tags/worldgen/biome/has_structure/scenic_fire_tree.json',{'replace':False,'values':['minecraft:plains','minecraft:sunflower_plains','minecraft:savanna','minecraft:savanna_plateau','minecraft:badlands','minecraft:wooded_badlands','minecraft:eroded_badlands']})
    print('Integrated fire-tree metadata and registered fresh-chunk dry-terrain ravine placement; no world edits.')
if __name__=='__main__':main()

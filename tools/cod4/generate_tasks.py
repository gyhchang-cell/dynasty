"""Generate COD4 advancement/slot data, then use the existing canonical FTB book builder."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'src/main/resources/data/dynasty'
nodes=json.loads((ROOT/'docs/cod4/quest-nodes.json').read_text())
for node in nodes:
    (D/'advancements'/(node['advancement']+'.json')).write_text(json.dumps({'criteria':{'code':{'trigger':'minecraft:impossible'}}},indent=2)+'\n')
# Remove our obsolete nested files if assets were regenerated.
for p in (D/'advancements/cod4').glob('*.json'):p.unlink()
if (D/'advancements/cod4').exists():(D/'advancements/cod4').rmdir()
p=D/'curios_progression.json';data=json.loads(p.read_text())
for id,key in [('silk_pouch','cod4_silk'),('jade_crown','cod4_crown')]:
    node=next(n for n in nodes if n['item']==id);data[key]={'title':node['title'],'quest_id':node['id']}
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
sys.path.insert(0,str(ROOT/'tools/art'))
from gen_ftbquests import build
build()

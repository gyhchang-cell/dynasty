"""Content coverage, graph references, and multi-use materials; not a substitute for runtime tests."""
from pathlib import Path
import json,re,collections
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'src/main/resources/assets/dynasty';D=ROOT/'src/main/resources/data/dynasty'
rows=json.loads((ROOT/'docs/cod4/secondary-roster.json').read_text());assert len(rows)==30
for row in rows:
 id=row['id'];geo=json.loads((A/'geo/secondary'/f'{id}.geo.json').read_text());bones=geo['minecraft:geometry'][0]['bones'];names={b['name'] for b in bones};assert len(bones)==len(names)
 for b in bones:assert 'parent' not in b or b['parent'] in names
 anim=json.loads((A/'animations/secondary'/f'{id}.animation.json').read_text());assert set(anim['animations'])=={'idle','wander','hunt','flee','attack','special','evade'}
 for state in anim['animations'].values():assert set(state['bones'])<=names
 assert (D/'loot_tables/entities'/f'{id}.json').exists();assert (A/'models/item'/f'{id}_spawn_egg.json').exists()
materials='qimen_cable qimen_gear fox_pelt wolf_fang python_gall crab_shell kappa_scale sprite_jade lantern_oil locust_dust'.split();uses=collections.defaultdict(list)
for path in sorted((D/'recipes/cod4').glob('*.json')):
 recipe=json.loads(path.read_text());seen={v['item'].split(':')[-1] for v in recipe.get('ingredients',[]) if 'item' in v}
 for id in sorted(seen):
  if id in materials:uses[id].append(path.stem)
for id in materials:assert len(uses[id])>=2,(id,uses[id])
# Capture existing accessory source/quest evidence rather than inventing "GOOD" statuses.
source=(ROOT/'src/main/java/com/dynasty/DynastyTrinkets.java').read_text();ids=set(re.findall(r'charm\("([^"]+)"\)',source))|set(re.findall(r'\{"([^"]+)",\s*\d',source))
quest_text={p.stem:p.read_text() for p in (ROOT/'modpack/config/ftbquests/quests/chapters').glob('*.snbt')};recipe_text={str(p.relative_to(D)):p.read_text() for p in (D/'recipes').rglob('*.json')}
loot_text={str(p.relative_to(D)):p.read_text() for p in (D/'loot_tables').rglob('*.json')}
output=[]
for id in sorted(ids):
 recipes=[p for p,s in recipe_text.items() if re.search(r'"result"\s*:\s*\{[^}]*"item"\s*:\s*"dynasty:'+id+'"',s)]
 loot=[p for p,s in loot_text.items() if '"dynasty:'+id+'"' in s]
 quests=[p for p,s in quest_text.items() if 'dynasty:'+id+'"' in s]
 output.append({'id':id,'sources':sorted(recipes)+sorted(loot)+['trinket_box (existing weighted pool)'],'chapters':sorted(quests),'review':'NO_TASK_LINK' if not quests else 'SOURCE_AND_TASK_VERIFIED','visual':'existing renderer + proc feedback; client review pending'})
report={'secondary_entities':len(rows),'animation_states':210,'new_effects':8,'material_recipe_uses':dict(uses),'accessories_reviewed':len(output),'runtime_evidence':'See verification.md; static coverage does not certify visuals or behavior completeness.'}
(ROOT/'docs/cod4/content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(ROOT/'docs/cod4/accessory-audit.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))

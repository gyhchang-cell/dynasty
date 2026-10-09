"""Content coverage, graph references, and multi-use materials; not a substitute for runtime tests."""
from pathlib import Path
import json,re,collections
ROOT=Path(__file__).resolve().parents[2];A=ROOT/'src/main/resources/assets/dynasty';D=ROOT/'src/main/resources/data/dynasty'
rows=json.loads((ROOT/'docs/cod4/secondary-roster.json').read_text());assert len(rows)==30
for row in rows:
 id=row['id'];geo=json.loads((A/'geo/secondary'/f'{id}.geo.json').read_text());bones=geo['minecraft:geometry'][0]['bones'];names={b['name'] for b in bones};assert len(bones)==len(names)
 for b in bones:assert 'parent' not in b or b['parent'] in names
 anim=json.loads((A/'animations/secondary'/f'{id}.animation.json').read_text())
 expected={'idle','wander','hunt','flee','attack','special','evade'}
 phase_clips={'red_fox':{'pounce'},'golden_leopard':{'stalk','pounce'},'giant_python':{'coil'},'carp_spirit':{'pounce','return_water'},'crab_soldier':{'side_charge','pinch'},'bat_demon':{'circle','dive'},'gray_falcon':{'circle','dive'},'wooden_magpie':{'circle','dive'},'corpse_beetle':{'burrow','eruption'},'stone_worm':{'burrow','eruption'},'venom_scorpion':{'pinch','sting'},'wandering_spirit':{'possession'}}
 assert set(anim['animations'])==expected|phase_clips.get(id,set()),f'{id}: missing base state or authored phase clip'
 for state in anim['animations'].values():assert set(state['bones'])<=names
 assert (D/'loot_tables/entities'/f'{id}.json').exists();assert (A/'models/item'/f'{id}_spawn_egg.json').exists()
materials='qimen_cable qimen_gear fox_pelt wolf_fang python_gall crab_shell kappa_scale sprite_jade lantern_oil locust_dust'.split();uses=collections.defaultdict(list)
for path in sorted((D/'recipes/cod4').glob('*.json')):
 recipe=json.loads(path.read_text());seen={v['item'].split(':')[-1] for v in recipe.get('ingredients',[]) if 'item' in v}
 for id in sorted(seen):
  if id in materials:uses[id].append(path.stem)
for id in materials:assert len(uses[id])>=2,(id,uses[id])
# Source, mechanism, duplicate-rule and exact objective audit share one owner.
import runpy
runpy.run_path(str(ROOT/'tools/cod4/audit_accessories.py'),run_name='__main__')
output=json.loads((ROOT/'docs/cod4/accessory-audit.json').read_text())
report={'secondary_entities':len(rows),'animation_states':sum(len(json.loads((A/'animations/secondary'/f"{row['id']}.animation.json").read_text())['animations']) for row in rows),'new_effects':8,'material_recipe_uses':dict(uses),'accessories_reviewed':len(output),'runtime_evidence':'See verification.md; static coverage does not certify visuals or behavior completeness.'}
(ROOT/'docs/cod4/content-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))

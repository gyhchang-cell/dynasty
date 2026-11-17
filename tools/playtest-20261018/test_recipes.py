"""Prevent unordered ingredient collisions from silently making another output unobtainable."""
from pathlib import Path
import json,unittest
R=Path(__file__).resolve().parents[2]
class RecipeChecks(unittest.TestCase):
 def test_no_identical_inputs_with_different_outputs(self):
  seen={}
  for p in (R/'src/main/resources/data/dynasty/recipes').glob('*.json'):
   d=json.loads(p.read_text());out=d.pop('result',None);d.pop('group',None);d.pop('category',None)
   if d.get('type')=='minecraft:crafting_shapeless':d['ingredients']=sorted(d['ingredients'],key=lambda x:json.dumps(x,sort_keys=True))
   key=json.dumps(d,sort_keys=True)
   if key in seen:self.assertEqual(seen[key][1],out,(seen[key][0],p.name))
   seen[key]=(p.name,out)
 def test_wind_branch_is_distinct_from_direct_upgrade(self):
  d=R/'src/main/resources/data/dynasty/recipes'
  a=json.loads((d/'branch_fengling_bow.json').read_text());b=json.loads((d/'evolve_archer_1.json').read_text())
  self.assertNotEqual(a['addition'],b['addition']);self.assertEqual(a['addition'],{'item':'dynasty:sky_feather'})
if __name__=='__main__':unittest.main()

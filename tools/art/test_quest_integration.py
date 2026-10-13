"""Regression: native icon count, old-save identities, routes and actionable guidance."""
import json
import re
import unittest
from pathlib import Path
import quest_story as story
from quest_snbt import list_compounds
from quest_presentation import icon_stack, task_presentation
from quest_cod4 import PLAN, SITES

class QuestIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book=story.build_source_book()
        cls.before=json.loads((story.ROOT/'docs/quests-integration-v1/before-book.json').read_text())
        cls.quests={q['id']:q for c in cls.book for q in c['quests']}

    def test_entire_existing_save_contract_and_main_spine(self):
        before={q['id']:q for c in self.before for q in c['quests']}
        self.assertEqual(set(before),set(self.quests))
        for key,old in before.items():
            self.assertEqual((old['tasks'],old['rewards']),(self.quests[key]['tasks'],self.quests[key]['rewards']),key)
            if old['role']=='main':
                self.assertEqual(old['deps'],self.quests[key]['deps'])
                self.assertEqual((old['x'],old['y']),(self.quests[key]['x'],self.quests[key]['y']))
        self.assertEqual(808,len(before))

    def test_compound_icons_have_native_positive_count(self):
        self.assertEqual('{ id: "dynasty:qimen_gear", Count: 1b }',icon_stack('{ id: "dynasty:qimen_gear" }'))
        self.assertEqual('{ id: "minecraft:stone", Count: 1b }',icon_stack('{ id: "minecraft:stone", Count: 0b }'))
        for c in self.book:
            # Check the exported document too, including chapter and reward icons.
            for icon in re.findall(r'\bicon:\s*(\{[^{}]*\})', story.encode(c)):
                self.assertRegex(icon, r'\bCount:\s*[1-9]\d*b?')
            for q in c['quests']:
                self.assertIn('Count: 1b',icon_stack(q['icon']))
                for block in list_compounds('\ttasks: '+task_presentation(q),'tasks'):
                    if 'type: "advancement"' in block:
                        self.assertRegex(block,r'icon: \{[^{}]*Count: 1b')
                        self.assertIn('title:',block)
                        self.assertEqual(1,len(re.findall('type: "advancement"',block)))

    def test_no_floating_extensions_or_cover_overlap(self):
        moved=[(c,q) for c in self.book for q in c['quests'] if q.get('route')=='cod4']
        self.assertEqual(46,len(moved))
        for c,q in moved:
            self.assertTrue(c['file'].startswith('dynasty_cod4_'))
            self.assertTrue(q['deps'])
            self.assertNotIn('minecraft:wheat',q['icon'])
            self.assertNotIn('minecraft:grass_block',q['icon'])
            self.assertNotIn('dynasty:', ''.join(v for v in q['description'] if not v.startswith('{')))
        home=next(c for c in self.book if c['file']=='dynasty_home')
        self.assertEqual(1,len(home['quests']))
        self.assertEqual(8,sum(bool(i.get('click')) for i in home['images']))

    def test_nested_cod4_recipes_have_real_ingredients(self):
        recipes=story.recipe_index()
        for item in list(PLAN)[:13]+['regen_pill','qi_pill','antidote_pill','army_ration']:
            data=recipes['dynasty:'+item]
            self.assertTrue(any(r['id']=='cod4/'+item for r in data),item)
            q=next(q for q in self.quests.values() if q.get('cod4_item')==item)
            self.assertIn(' → ', ' '.join(q['description']))
        self.assertEqual({'dynasty:refined_steel':1,'minecraft:copper_ingot':1,'minecraft:redstone':1},
                         next(r for r in recipes['dynasty:qimen_gear'] if r['id']=='cod4/qimen_gear')['ingredients'])

    def test_material_to_supply_and_weapon_to_ammunition(self):
        for after,before in [('repeating_crossbow','qimen_cable'),('repeating_bolt','repeating_crossbow'),
                             ('siege_crossbow','repeating_crossbow'),('heavy_bolt','siege_crossbow'),
                             ('regen_pill','sprite_jade'),('antidote_pill','python_gall'),
                             ('soul_incense','lantern_oil'),('broken_waterwheel','qimen_cable')]:
            self.assertIn(before,PLAN[after][3])

    def test_interaction_directions_resolve_to_real_worldgen(self):
        for item,(location,*_) in SITES.items():
            self.assertTrue((story.DATA/f'worldgen/structure/{location}.json').is_file(),item)
        texts={q.get('cod4_item'):' '.join(q['description']) for q in self.quests.values()}
        for item,expected in [('battlefield_remnant','三处不同'),('mortuary_room','治疗药水'),
                              ('ghost_market_boat','安魂香'),('ancient_well','七次'),('old_bellows','三格内')]:
            self.assertIn(expected,texts[item])
        self.assertEqual(8,sum('必须亲手合成一次' in text for text in texts.values()))

if __name__=='__main__':unittest.main()

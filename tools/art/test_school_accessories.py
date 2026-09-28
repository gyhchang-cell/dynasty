"""Fixed expansion contract: mechanics, recipe progression, art provenance and optional quests."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from PIL import Image
from gen_trinkets7 import ITEMS, TRINKETS
from gen_curios import classifications
import quest_story

ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/'src/main/resources'
DOC=ROOT/'docs/art/school-accessories-v2'

class AccessoryExpansionTests(unittest.TestCase):
    def test_four_per_school_and_eight_real_upgrade_chains(self):
        slots=classifications()
        for school in ('guard','sword','archer','talisman'):
            group=[v for v in ITEMS.values() if v['school']==school]
            self.assertEqual(6,len(group))
            advanced=[v for v in group if v['recipe'][0].split(':')[-1] in ITEMS]
            self.assertEqual(4,len(advanced))
            for item in advanced:
                old=ITEMS[item['recipe'][0].split(':')[-1]]
                self.assertEqual(old['school'],school)
                self.assertEqual(old['slot'],item['slot'])
            for item in group:
                self.assertEqual(item['slot'],slots[item['id']])
                self.assertEqual([0,0,0],item['spec'][-3:],'No timed triggers or environmental conditions')

    def test_generated_data_and_recipes_match(self):
        java=(ROOT/'src/main/java/com/dynasty/DynastyAccessoryData.java').read_text()
        lang=json.loads((RES/'assets/dynasty/lang/zh_cn.json').read_text())
        for key,item in ITEMS.items():
            self.assertIn(f'case "{key}" -> new Bonus("{item["school"]}", "{item["bonus_kind"]}", {item["bonus"]});',java)
            recipe=json.loads((RES/f'data/dynasty/recipes/{key}.json').read_text())
            if item['recipe'][0].split(':')[-1] in ITEMS:
                self.assertEqual('minecraft:smithing_transform',recipe['type'])
                self.assertEqual({'item':item['recipe'][0]},recipe['base'])
                self.assertEqual({'item':item['recipe'][1]},recipe['addition'])
            else:
                self.assertEqual([{'item':v} for v in item['recipe']],recipe['ingredients'])
                self.assertLessEqual(len(recipe['ingredients']),9)
            self.assertEqual('dynasty:'+key,recipe['result']['item'])
            for ingredient in item['recipe']:
                if not ingredient.startswith('dynasty:'):continue
                ident=ingredient.split(':')[1]
                self.assertTrue('item.dynasty.'+ident in lang or 'block.dynasty.'+ident in lang,ingredient)
            self.assertEqual(item['zh_effect'],lang['tooltip.dynasty.accessory_damage.'+key])
            if item['bonus_kind']=='melee':self.assertTrue(item['zh_effect'].startswith('近战伤害 +'))
            if item['bonus_kind']=='arrow':self.assertTrue(item['zh_effect'].startswith('箭矢伤害 +'))
            if item['bonus_kind']=='edict':self.assertTrue(item['zh_effect'].startswith('律令兵器伤害 +'))

    def test_every_piece_has_native_book_and_independent_quest(self):
        book=quest_story.build_book()
        for key,item in ITEMS.items():
            found=[(c,q) for c in book for q in c['quests'] if q['target']=='dynasty:'+key and c.get('route')]
            self.assertEqual(1,len(found))
            chapter,q=found[0]
            self.assertEqual(item['school'],chapter['route'])
            predecessor=item['recipe'][0].split(':')[-1]
            expected=[other['id'] for other in chapter['quests'] if other['target']=='dynasty:'+predecessor] if predecessor in ITEMS else []
            self.assertEqual(expected,q['deps'])
            for c in book:
                for other in c['quests']:
                    if q['id'] in other['deps']:
                        self.assertIn(other['target'].split(':')[-1],ITEMS,'Only accessory evolution may depend on accessory nodes')
            for locale in ('zh_cn','en_us'):
                entry=json.loads((RES/f'assets/dynasty/patchouli_books/imperial_codex/{locale}/entries/accessories/{key}.json').read_text())
                self.assertTrue(any(p.get('recipe')=='dynasty:'+key for p in entry['pages']))
                for page in entry['pages']:
                    self.assertNotIn('%',page.get('text',''), 'Literal percent breaks Patchouli localization')
                route=json.loads((RES/f'assets/dynasty/patchouli_books/imperial_codex/{locale}/entries/schools/{item["school"]}.json').read_text())
                self.assertTrue(any(p.get('recipe')=='dynasty:'+key for p in route['pages']))

    def test_twenty_eight_unique_authored_sprites_with_backups(self):
        hashes=set()
        for doc,manifest,count in [(DOC,'assets.json',16),(DOC,'remasters.json',12),(ROOT/'docs/art/accessory-refining-v3','assets.json',8)]:
            rows=json.loads((doc/manifest).read_text());self.assertEqual(count,len(rows))
            for row in rows:
                self.assertTrue(row['prompt']);self.assertEqual('built-in image_gen',row['mode'])
                self.assertTrue((ROOT/row['project_source']).is_file())
                path=ROOT/row['texture']
                hashes.add(hashlib.sha256(path.read_bytes()).hexdigest())
                with Image.open(path) as image:
                    self.assertEqual((128,128),image.size)
                    self.assertEqual('RGBA',image.mode)
                    alpha=image.getchannel('A');self.assertEqual(0,alpha.getextrema()[0])
                    self.assertGreaterEqual(alpha.getextrema()[1],250,'Visible near-opaque material, not a ghost sprite')
                    x0,y0,x1,y1=alpha.getbbox()
                    self.assertTrue(x0>=3 and y0>=3 and x1<=125 and y1<=125,'Unclipped sprite')
                    self.assertGreaterEqual(max(x1-x0,y1-y0),118,'Fill inventory slot')
                if manifest=='remasters.json':
                    before=DOC/'before'/path.name;self.assertTrue(before.is_file())
                    self.assertNotEqual(before.read_bytes(),path.read_bytes())
        self.assertEqual(36,len(hashes),'No palette-swap duplicates')

if __name__=='__main__':unittest.main(verbosity=2)

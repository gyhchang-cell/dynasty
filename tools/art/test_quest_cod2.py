"""Chensha elite branches must use real, ownership-scoped kill detectors."""
import json
import unittest
from pathlib import Path
import quest_cod2
import quest_story
import quest_journey

ROOT=Path(__file__).resolve().parents[2]


class ChenshaQuestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book=quest_story.build_book()
        cls.quests={q['id']:q for c in cls.book for q in c['quests']}

    def test_real_kills_are_scoped_to_the_authored_garrison(self):
        definitions=quest_cod2.garrison_advancements()
        for role,entity,flag in [('jinwu','pilin_zhijinwu','0b'),('hammer','juchui_jinjia_lishi','1b')]:
            name='defeat_chensha_'+role
            path=ROOT/f'src/main/resources/data/dynasty/advancements/dungeons/{name}.json'
            actual=json.loads(path.read_text());self.assertEqual(definitions[name],actual)
            criterion=actual['criteria']['kill']
            self.assertEqual('minecraft:player_killed_entity',criterion['trigger'])
            self.assertEqual({'type':'dynasty:'+entity,'nbt':'{ForgeData:{ChenshaGarrison:{Hammer:'+flag+'}}}'},criterion['conditions']['entity'])

    def test_optional_branches_do_not_gate_main_progression_or_invent_coffin_loot(self):
        guide=quest_journey.ident('cod2:chensha:route')
        ids={quest_journey.ident('cod2:chensha:'+role) for role in ('jinwu','hammer')}
        for key in ids:
            q=self.quests[key]
            self.assertEqual([guide],q['deps']);self.assertEqual('advancement',q['kind'])
            self.assertEqual('[]',q['rewards']);self.assertEqual('exploration_branch',q['role'])
        for q in self.quests.values():
            if q['role']=='main':self.assertTrue(ids.isdisjoint(q['deps']))

    def test_guide_links_resolve_to_both_guard_quests(self):
        guide=self.quests[quest_journey.ident('cod2:chensha:route')]
        links={json.loads(t)['clickEvent']['value'] for t in guide['description'] if t.startswith('{"')}
        self.assertTrue({quest_journey.ident('cod2:chensha:'+role) for role in ('jinwu','hammer')}<=links)

    def test_exported_book_and_c9_chapter_match_the_generator(self):
        actual=json.loads((ROOT/'docs/quests-remaster/book.json').read_text())
        exported=next(c for c in actual if c['file']=='dynasty_c9')
        generated=next(c for c in self.book if c['file']=='dynasty_c9')
        self.assertEqual(generated,exported)
        self.assertEqual(quest_story.encode(generated),(ROOT/'modpack/config/ftbquests/quests/chapters/dynasty_c9.snbt').read_text())

    def test_wangsi_uses_registered_underworld_structure_without_unfinished_rewards(self):
        visit=self.quests[quest_journey.ident('cod2:wangsi:visit')]
        guide=self.quests[quest_journey.ident('cod2:wangsi:route')]
        self.assertEqual('dynasty:visit_yinsi_wangsi_cheng',visit['target'])
        self.assertEqual([visit['id']],guide['deps'])
        for q in (visit,guide):
            self.assertEqual('[]',q['rewards']);self.assertEqual('exploration_branch',q['role'])
        advancement=json.loads((ROOT/'src/main/resources/data/dynasty/advancements/visit_yinsi_wangsi_cheng.json').read_text())
        self.assertEqual({'dimension':'dynasty:underworld','structure':'dynasty:yinsi_wangsi_cheng'},
            advancement['criteria']['visit']['conditions']['player'][0]['predicate'])
        placement=json.loads((ROOT/'src/main/resources/data/dynasty/worldgen/structure_set/yinsi_wangsi_cheng.json').read_text())
        self.assertEqual('dynasty:yinsi_wangsi_cheng',placement['structures'][0]['structure'])
        self.assertIn('主河水位不变',''.join(guide['description']))
        for q in self.quests.values():
            if q['role']=='main':self.assertTrue({visit['id'],guide['id']}.isdisjoint(q['deps']))


if __name__=='__main__':unittest.main()

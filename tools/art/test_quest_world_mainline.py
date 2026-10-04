"""Real registry goals, persistent receipts, and narrowly scoped story dependency tests."""
import copy
import json
import unittest
import quest_story as story
from quest_routes import code


class WorldMainlineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book=story.build_book()
        cls.rows=[q for c in cls.book for q in c['quests']]

    def test_all_six_objectives_are_real_mainline_advancements(self):
        rows=[q for q in self.rows if q.get('world_story')]
        self.assertEqual(6,len(rows))
        self.assertEqual(6,len({q['target'] for q in rows}))
        for q in rows:
            self.assertEqual('main',q['role'])
            self.assertEqual('advancement',q['kind'])
            resource=story.ROOT/'src/main/resources/data/dynasty/advancements'/((q['target'].split(':')[1])+'.json')
            data=json.loads(resource.read_text())
            if 'story_slay_' in q['target']:
                criterion=data['criteria']['slay']
                self.assertEqual('minecraft:player_killed_entity',criterion['trigger'])
                self.assertEqual(q['target'].replace('story_slay_',''),criterion['conditions']['entity']['type'])
            else:
                self.assertEqual([['natural','placed']],data['requirements'])
                self.assertEqual('minecraft:location',data['criteria']['natural']['trigger'])
                self.assertEqual('minecraft:impossible',data['criteria']['placed']['trigger'])

    def test_four_ritual_branches_follow_dragon_exploration(self):
        rows={q['id']:q for q in self.rows}
        dragon=code(1,0xA0005)
        for i in (10,20,30,40):
            self.assertEqual([dragon],rows[code(1,0x90000+i)]['deps'])
        for i in (10,20,40):
            self.assertEqual([code(1,0x90000+i)],rows[code(1,0x90000+i+2)]['deps'])
        # Phoenix is not required in chapters 01-08; keep its real kill objective.
        self.assertEqual([code(1,0x9001F)],rows[code(1,0x90020)]['deps'])
        for i in (14,24,34,44,51):
            self.assertTrue(rows[code(1,0x90000+i)]['target'].startswith('dynasty:ritual_'))

    def test_other_routes_cannot_use_story_gate_exception(self):
        book=copy.deepcopy(self.book)
        q=next(q for c in book for q in c['quests'] if q.get('route')=='guard')
        q['deps']=[code(1,0xA0005)]
        q['world_story_gate']=code(1,0xA0005)
        with self.assertRaisesRegex(AssertionError,'Build gates'):
            story.validate(book)

    def test_new_receipts_dont_grant_items_or_commands(self):
        # One-time quest XP only; neither advancing nor reconnecting spawns rewards.
        for q in self.rows:
            if q.get('world_story'):
                self.assertNotIn('type: "command"',q['rewards'])
                self.assertNotIn('type: "item"',q['rewards'])


if __name__=='__main__':unittest.main()

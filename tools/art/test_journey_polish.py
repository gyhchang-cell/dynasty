import unittest
from collections import Counter
from quest_growth import refining_costs
from quest_story import build_book

class JourneyPolishTests(unittest.TestCase):
    def test_refining_exact_each_step(self):
        for rank in (1,5,15,30):
            lines=refining_costs(rank,lambda x:x.split(':')[1])
            self.assertEqual(rank-{1:0,5:1,15:5,30:15}[rank],len([s for s in lines if s.startswith('+')]))
        text=' '.join(refining_costs(5,lambda x:x.split(':')[1]))
        self.assertIn('+4 → +5：jade×2，经验 6 级',text)
        self.assertIn('材料合计：jade×5',text)
        high=' '.join(refining_costs(30,lambda x:x.split(':')[1]))
        self.assertNotIn('+14 → +15',high)
        self.assertIn('+15 → +16',high)

    def test_each_chapter_two_real_branches(self):
        for c in build_book():
            if not c['main']:continue
            rows={q['id']:q for q in c['quests']}
            branches=[q for q in rows.values() if q['role']=='chapter_branch']
            self.assertEqual(4,len(branches))
            self.assertEqual(2,sum(rows[q['deps'][0]]['role']=='main' for q in branches))
            for q in branches:
                self.assertEqual('item',q['kind'])
                if q['target'].startswith('dynasty:') and q['target'] not in {
                        'dynasty:emperor_bone','dynasty:sky_token','dynasty:dragon_emperor_seal'}:
                    self.assertTrue(q['recipe_ids'],q['target'])
            self.assertEqual([],c['images'])

if __name__=='__main__':unittest.main(verbosity=2)

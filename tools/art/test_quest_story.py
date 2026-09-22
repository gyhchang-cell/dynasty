"""Regression checks for the v2 quest migration and guidance, including negative cases."""
import copy
import json
import re
import unittest

import quest_story as story
from verify_ftbquests import cycle_check, layout_check


class QuestStoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = story.build_book()
        cls.main = [q for c in cls.book if c["main"] for q in c["quests"]]

    def test_frozen_ids_and_rewards(self):
        story.validate(self.book)
        self.assertEqual(488, sum(len(c["quests"]) for c in json.loads(story.LEGACY.read_text())))

    def test_reproducible(self):
        self.assertEqual(self.book, story.build_book())

    def test_compass_material_reward_precedes_both_compasses(self):
        supplies, compasses = self.book[1]["quests"][:2]
        self.assertEqual("minecraft:cobblestone", supplies["target"])
        self.assertEqual(4, supplies["count"])
        self.assertIn('id: "minecraft:compass", Count: 2b', supplies["rewards"])
        self.assertIn('team_reward: false', supplies["rewards"])
        self.assertEqual([supplies["id"]], compasses["deps"])
        for item in ("naturescompass:naturescompass", "explorerscompass:explorerscompass"):
            self.assertIn(item, compasses["tasks"])
            self.assertIn(item, story.recipe_index())

    def test_export_matches_source(self):
        for c in self.book:
            self.assertEqual(story.encode(c), (story.OUT / "chapters" / (c["file"]+".snbt")).read_text())

    def test_layout_and_cycle(self):
        allq = [q for c in self.book for q in c["quests"]]
        graph = {q["id"]:q["deps"] for q in allq}
        self.assertEqual([], cycle_check(graph,set(graph)))
        for c in self.book:
            problems = []
            layout_check(c["file"],[(q["x"],q["y"]) for q in c["quests"]],problems)
            self.assertEqual([],problems)

    def test_small_main_chapters_and_no_catalog_gate(self):
        self.assertEqual(8, sum(c["main"] for c in self.book))
        self.assertTrue(all(5 <= len(c["quests"]) <= 10 for c in self.book if c["main"]))
        self.assertTrue(all(not q["deps"] for c in self.book if not c["main"] for q in c["quests"]))

    def test_milestones_still_personal(self):
        allq = {q["id"]:q for c in self.book for q in c["quests"]}
        for key, v in json.loads((story.DATA / "curios_progression.json").read_text()).items():
            q = allq[v["quest_id"]]
            self.assertEqual("hexagon",q["shape"])
            self.assertIn('dynasty unlock_curio '+key+'"',q["rewards"])
            self.assertIn('team_reward: false',q["rewards"])

    def test_every_actual_recipe_alternative_is_explained(self):
        recipes = story.recipe_index()
        for c in self.book:
            for q in c["quests"]:
                if q["kind"]=="item":
                    self.assertEqual([r["id"] for r in recipes.get(q["target"],[])],q.get("recipe_ids",[]))
                if q["kind"]=="checkmark":
                    self.assertEqual("[]",q["rewards"])

    def test_material_steps_precede_consuming_upgrades(self):
        ids = {q["target"]:i for i,q in enumerate(self.main)}
        for before, after in [("mu_mao","shi_ge"),("shi_ge","tong_dao"),("tong_dao","tie_jian"),
            ("tie_jian","sword_bronze"),("cinnabar","ink_stick"),("ink_stick","blueprint"),
            ("blueprint","sword_bronze"),("talisman_paper","return_talisman"),
            ("return_talisman","jade_portal"),("dragon_crystal","jade_portal"),
            ("emperor_bone","xuantian_jade")]:
            self.assertLess(ids["dynasty:"+before],ids["dynasty:"+after])

    def test_portals_are_craftable_in_pairs(self):
        recipes = story.recipe_index()
        for item in ["jade_portal","underworld_portal","cloud_portal","dragon_gate"]:
            recipe = next(r for r in recipes["dynasty:"+item] if r["id"]==item)
            self.assertEqual(2, recipe["output"])
            self.assertNotIn("dynasty:"+item,recipe["ingredients"])

    def test_dimension_bosses_follow_entry(self):
        positions = {(q["kind"],q["target"]):i for i,q in enumerate(self.main)}
        for boss,dim in {"eunuch_mastermind":"celestial_dynasty", "undead_first_emperor":"underworld",
            "nine_heaven_general":"jiuxiao","dragon_king":"dragon_palace","dragon_emperor":"celestial_dynasty"}.items():
            self.assertLess(positions[("dimension","dynasty:"+dim)],positions[("kill","dynasty:"+boss)])

    def test_non_recipe_weapon_gifts_are_explained(self):
        for target in ["sunbow","gilded_mace","supreme_sword","seven_star_saber"]:
            q = next(q for c in self.book for q in c["quests"] if q["kind"]=="item" and q["target"]=="dynasty:"+target)
            self.assertFalse(q.get("unverified_source"))
            self.assertIn("非合成获取", "".join(q["description"]))

    def test_mutating_old_reward_rejected(self):
        book = copy.deepcopy(self.book)
        old = next(q for c in book for q in c["quests"] if q["rewards"]!="[]")
        old["rewards"]="[]"
        with self.assertRaises(AssertionError):
            story.validate(book)

    def test_catalog_dependency_rejected(self):
        book = copy.deepcopy(self.book)
        book[1]["quests"][0]["deps"]=[next(c for c in book if not c["main"])["quests"][0]["id"]]
        with self.assertRaises(AssertionError):
            story.validate(book)

    def test_missing_main_source_rejected(self):
        book = copy.deepcopy(self.book)
        book[1]["quests"][0]["unverified_source"]=True
        with self.assertRaises(AssertionError):
            story.validate(book)

    def test_duplicate_id_rejected(self):
        book = copy.deepcopy(self.book)
        book[0]["quests"].append(copy.deepcopy(book[0]["quests"][0]))
        with self.assertRaises(AssertionError):
            story.validate(book)

    def test_boss_links_work_both_ways(self):
        from boss_quest_guides import GUIDES, validate_links
        self.assertGreater(validate_links(self.book), 40)
        allq = {q["id"]:q for c in self.book for q in c["quests"]}
        for boss,(number,*_) in GUIDES.items():
            guide = allq[f"1{number:015x}"]
            main = next(q for q in self.main if q["kind"]=="kill" and q["target"]=="dynasty:"+boss)
            self.assertEqual(guide["id"],json.loads(main["description"][0])["clickEvent"]["value"])
            self.assertEqual(main["id"],json.loads(guide["description"][0])["clickEvent"]["value"])
            self.assertIn("消耗一个信物", "".join(guide["description"]))

    def test_broken_guide_link_rejected(self):
        book=copy.deepcopy(self.book)
        guide=next(q for c in book for q in c["quests"] if q["target"]=="guide:dragon_emperor")
        link=json.loads(guide["description"][0]);link["clickEvent"]["value"]="10000000000fffff"
        guide["description"][0]=json.dumps(link)
        with self.assertRaises(AssertionError):
            story.validate(book)


if __name__ == "__main__":
    unittest.main()

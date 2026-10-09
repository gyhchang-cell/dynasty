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
        cls.main = [q for c in cls.book if c["main"] for q in c["quests"] if q['role']=='main']
        cls.cod4_nodes = json.loads((story.ROOT / "docs/cod4/quest-nodes.json").read_text())

    def cod4_ids(self, chapter):
        return [node["id"] for node in self.cod4_nodes if node["chapter"] == chapter]

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
        # Chapter 03 preserves its 19 nodes and adds six cod1 encounter branches.
        self.assertEqual([18,23,25,13,12,11,12,11],
                         [len(c['quests'])-len(self.cod4_ids(c['file'])) for c in self.book if c['main']])
        self.assertEqual({node['id'] for node in self.cod4_nodes},
                         {q['id'] for c in self.book for q in c['quests'] if q.get('route') == 'cod4'})
        self.assertEqual(32,sum(q['role']=='chapter_branch' for c in self.book for q in c['quests']))
        self.assertEqual(2,sum(q.get('target') in ('dynasty:tiangong_citadel','dynasty:tiangong_mining_estate') for c in self.book for q in c['quests']))
        self.assertTrue(all(not q["deps"] for c in self.book if not c["main"] for q in c["quests"] if q["role"]!="build"))

    def test_milestones_still_personal(self):
        allq = {q["id"]:q for c in self.book for q in c["quests"]}
        for key, v in json.loads((story.DATA / "curios_progression.json").read_text()).items():
            q = allq[v["quest_id"]]
            if v.get("unlock_source") == "content":
                item = {"cod4_silk": "silk_pouch", "cod4_crown": "jade_crown"}[key]
                self.assertEqual("advancement", q["kind"])
                self.assertEqual("dynasty:cod4_obtain_" + item, q["target"])
                self.assertEqual("[]", q["rewards"], "Personal server milestones must not also grant team rewards")
                self.assertFalse(q["deps"])
                continue
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
            def targets(quest):
                return {json.loads(line)["clickEvent"]["value"] for line in quest["description"] if line.startswith('{"')}
            self.assertIn(guide["id"], targets(main))
            self.assertIn(main["id"], targets(guide))
            self.assertIn("消耗一个信物", "".join(guide["description"]))

    def test_broken_guide_link_rejected(self):
        book=copy.deepcopy(self.book)
        guide=next(q for c in book for q in c["quests"] if q["target"]=="guide:dragon_emperor")
        link=json.loads(guide["description"][0]);link["clickEvent"]["value"]="10000000000fffff"
        guide["description"][0]=json.dumps(link)
        with self.assertRaises(AssertionError):
            story.validate(book)

    def test_four_real_build_journeys(self):
        from quest_routes import ROUTES
        from weapon_evolution_paths import PATHS
        routes=[c for c in self.book if c.get("route")]
        self.assertEqual(set(ROUTES),{c["route"] for c in routes})
        for c in routes:
            extension_ids = self.cod4_ids(c['file'])
            self.assertEqual(extension_ids, [q['id'] for q in c['quests'] if q.get('route') == 'cod4'])
            self.assertEqual(35+len(PATHS[c['route']])+len(extension_ids),len(c["quests"]))
            self.assertEqual(0,len(c["quest_links"]))
            self.assertEqual(34+len(PATHS[c['route']])+len(extension_ids),sum(q["kind"]!="checkmark" for q in c["quests"]))
            self.assertEqual(9+len(extension_ids),sum(q["kind"]=="advancement" for q in c["quests"]))
            self.assertNotIn("repeatable:",story.encode(c))
            self.assertIn("can_repeat: false",story.encode(c))
            for q in c["quests"]:
                self.assertNotIn("command",q["rewards"])
                if q["rewards"]!="[]": self.assertIn("team_reward: false",q["rewards"])
        self.assertEqual(4,len({c["layout"] for c in routes}))

    def test_no_decorative_dependency_lines(self):
        for chapter in self.book:
            self.assertFalse(any('/backdrop_' in image['image'] for image in chapter.get('images',[])))
        for c in self.book:
            if c.get('route'):
                self.assertEqual([],c['quests'][3]['deps'])
                self.assertEqual([],c['quests'][4]['deps'])
                self.assertTrue(all(c['quests'][3]['id'] not in q['deps'] and c['quests'][4]['id'] not in q['deps'] for q in c['quests']))
                self.assertIn('不要求格挡、走位、连击或满蓄',c['quests'][5]['how'])
                self.assertEqual(6,sum(q['subtitle']=='锻造进化' for q in c['quests']))

    def test_new_ids_are_explicit_and_reordering_safe(self):
        from quest_routes import ROUTES, code
        from weapon_evolution_paths import PATHS
        for c in self.book:
            if c.get("route"):
                base=ROUTES[c["route"]]["base"]
                self.assertEqual([code(1,base+i) for i in range(12)] +
                                 [code(1,base+0x20+i) for i in (1,3,6,10)]+[code(1,base+i) for i in range(0x62,0x68)]+[code(1,base+0x80),code(1,base+0x81)]+[code(1,base+i) for i in range(0x90,0x96)]+[code(1,base+i) for i in range(0xa0,0xa5)],
                                 [q["id"] for q in c["quests"][:35]])
                self.assertEqual([code(1,base+0xb0+i) for i in range(len(PATHS[c['route']]))],
                                 [q['id'] for q in c['quests'][35:] if q.get('route') != 'cod4'])
                self.assertEqual(self.cod4_ids(c['file']), [q['id'] for q in c['quests'] if q.get('route') == 'cod4'])
        reversed_book=list(reversed(copy.deepcopy(self.book)))
        # Reordering optional chapters must not alter any identity; main itself stays ordered.
        optional=[c for c in reversed_book if not c["main"]]
        main=[c for c in self.book if c["main"]]
        story.validate(main+optional)

    def test_actual_trial_advancements_and_recipes_exist(self):
        for c in self.book:
            if not c.get("route"): continue
            for q in c["quests"]:
                if q["kind"]=="advancement":
                    path=story.DATA/"advancements"/(q["target"].split(":")[1]+".json")
                    data=json.loads(path.read_text())
                    self.assertEqual({"minecraft:impossible"},{v["trigger"] for v in data["criteria"].values()})
                    self.assertFalse(data.get("rewards"),"Trial rewards must not duplicate quest rewards")
                for target in re.findall(r'item: \{ id: "(dynasty:[^"]+)"',q["tasks"]):
                    short=target.split(":")[1]
                    self.assertTrue((story.ROOT/"src/main/resources/assets/dynasty/models/item"/(short+".json")).exists(),target)

    def test_home_is_navigation_not_main_gate(self):
        home=next(c for c in self.book if c["file"]=="dynasty_home")
        self.assertFalse(home["main"])
        self.assertTrue(all(not q["deps"] and q["rewards"]=="[]" for q in home["quests"]))
        self.assertEqual(1, sum(q["role"] == "guide" for q in home["quests"]),
                         "Navigation cards must not add fake completion tasks")
        side = [q for q in home["quests"] if q["role"] == "side"]
        self.assertEqual(1, len(side))
        self.assertEqual("10000000000F1001", side[0]["id"])
        self.assertEqual("advancement", side[0]["kind"])
        self.assertEqual("dynasty:first_infusion", side[0]["target"])
        self.assertEqual(self.cod4_ids(home['file']), [q['id'] for q in home['quests'] if q.get('route') == 'cod4'])
        self.assertEqual(8,sum(bool(i.get("click")) for i in home["images"]))
        self.assertEqual(75,len(self.main))
        self.assertEqual(9,len([c for c in self.book if c["group"]==4]))

    def test_layout_includes_links_and_has_no_overlap(self):
        for c in self.book:
            problems=[]
            layout_check(c["file"],[(q["x"],q["y"]) for q in c["quests"]+c.get("quest_links",[])],problems)
            self.assertEqual([],problems,c["file"])

    def test_build_branches_are_thematic_not_copied_collect_goals(self):
        routes=[c for c in self.book if c.get("route")]
        branches=[{(q["kind"],q["target"]) for q in c["quests"] if q["id"][-2:] in {"06","07","08","09","0b"}} for c in routes]
        for i,a in enumerate(branches):
            for b in branches[i+1:]: self.assertLessEqual(len(a&b),1)
        for c in routes:
            self.assertFalse(any(q["target"] in {"dynasty:return_talisman","explorerscompass:explorerscompass"} for q in c["quests"]))
        archery=next(c for c in routes if c["route"]=="archer")
        self.assertTrue(any(q["target"]=="minecraft:arrow" and q["count"]==64 for q in archery["quests"]))
        target=next(q for q in archery["quests"] if q["target"]=="minecraft:target")
        self.assertIn("不检测搭建",target["how"])

    def test_charm_sections_follow_real_mechanics_and_cover_every_entry(self):
        from quest_atlas import charm_sections,CHARM_SECTIONS
        groups=charm_sections()
        self.assertEqual(3,groups["blood_oath_seal"])
        self.assertEqual(3,groups["internal_injury_talisman"])
        self.assertEqual(2,groups["dawn_blade_charm"])
        self.assertEqual(2,groups["jade_cicada"])
        self.assertEqual(0,groups["war_deity_signet"])
        self.assertEqual(1,groups["alchemy_furnace_charm"])
        c=next(c for c in self.book if c["file"]=="dynasty_accessory_charm")
        entries=c["quests"][1:]+c["quest_links"]
        self.assertEqual({"dynasty:"+item for item in groups},{q["target"] for q in entries})
        for q in entries: self.assertEqual(CHARM_SECTIONS[groups[q["target"].split(":")[1]]],q["atlas_section"])
        counts=[s["count"] for s in c["atlas_sections"]]
        self.assertNotEqual(min(counts),max(counts),"Do not force equal-size semantic categories")

    def test_native_lists_do_not_confuse_images_links_and_quests(self):
        from quest_snbt import list_compounds,object_id
        for c in self.book:
            text=story.encode(c)
            self.assertEqual([q["id"] for q in c["quests"]],[object_id(b) for b in list_compounds(text,"quests")])
            self.assertEqual(len(c.get("quest_links",[])),len(list_compounds(text,"quest_links")))
            self.assertEqual(len(c.get("images",[])),len(list_compounds(text,"images")))
            self.assertNotIn("atlas_section:",text,"Editorial metadata is not a native FTB field")
            for block in list_compounds(text,"quest_links"):
                for axis in ("x","y"): self.assertRegex(block,r"\b"+axis+r": -?\d+\.\d+d")

    def test_cross_build_gate_and_cycle_rejected(self):
        book=copy.deepcopy(self.book)
        routes=[c for c in book if c.get("route")]
        routes[0]["quests"][0]["deps"]=[routes[1]["quests"][0]["id"]]
        with self.assertRaises(AssertionError): story.validate(book)
        book=copy.deepcopy(self.book)
        route=next(c for c in book if c.get("route"))
        route["quests"][0]["deps"]=[route["quests"][2]["id"]]
        with self.assertRaises(AssertionError): story.validate(book)

    def test_broken_native_image_or_quest_link_rejected(self):
        for kind in ("image","link","resource","slot"):
            book=copy.deepcopy(self.book)
            c=next(c for c in book if c.get("route"))
            if kind=="image": c["images"][0]["click"]="#100000000fffffff"
            elif kind=="link": next(ch for ch in book if ch.get('quest_links'))['quest_links'][0]["linked_quest"]="100000000fffffff"
            elif kind=="resource": c["images"][0]["image"]="https://invalid.example/art.png"
            else:
                atlas=next(c for c in book if c["file"]=="dynasty_accessory_necklace")
                atlas["quest_links"].pop()
            with self.assertRaises(AssertionError): story.validate(book)


if __name__ == "__main__":
    unittest.main()

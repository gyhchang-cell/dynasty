from quest_bugfix_oct17 import REMOVED_BLUEPRINT_PREPS
from quest_bugfix_oct18 import REMOVED
REMOVED_BLUEPRINT_PREPS = REMOVED_BLUEPRINT_PREPS | REMOVED

def migrated_tasks(key, tasks):
    return tasks.replace('dynasty:refined_steel','dynasty:sky_feather') if key=='1000000000030280' else tasks

def migrated_deps(deps, old):
    out=[]
    for dep in deps:
        values=migrated_deps(old[dep]['deps'],old) if dep in REMOVED_BLUEPRINT_PREPS else [dep]
        out.extend(v for v in values if v not in out)
    return out

"""Migration checks: old saves, easier goals, live navigation and readable blocks."""
import copy
import json
import re
import unittest
from pathlib import Path
import quest_story as story
import quest_journey as journey

class QuestJourneyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=story.build_source_book();cls.book=story.build_book()
        cls.before={q['id']:q for c in cls.base for q in c['quests']}
        cls.after={q['id']:q for c in cls.book for q in c['quests']}
        # Semantic regressions must ignore native FTB colour spans. Presentation is audited separately.
        for q in cls.after.values():q['description']=[journey.clean(s) for s in q['description']]

    def test_consolidation_preserves_every_quest_and_reward(self):
        self.assertEqual(20,len(self.book));self.assertGreater(len(self.after),1200)
        self.assertTrue(set(self.before)<=set(self.after))
        for k,q in self.before.items():
            self.assertEqual(q['rewards'],self.after[k]['rewards'])
            self.assertEqual(q['target'],self.after[k]['target'])
        journey.validate(self.book,self.base)

    def test_lowered_goals_keep_task_id_and_detection(self):
        lowered=[q for q in self.after.values() if q.get('journey_previous_count')]
        self.assertGreater(len(lowered),40)
        for q in lowered:
            self.assertLess(q['count'],self.before[q['id']]['count'])
            self.assertEqual(re.findall(r'\bid: "([12][a-f0-9A-F]{15})"',q['tasks']),
                             re.findall(r'\bid: "([12][a-f0-9A-F]{15})"',self.before[q['id']]['tasks']))

    def test_main_story_cannot_acquire_catalog_gate(self):
        for k,q in self.before.items():
            if q['role']=='main':self.assertEqual(q['deps'],self.after[k]['deps'])
        bad=copy.deepcopy(self.book)
        q=next(q for c in bad for q in c['quests'] if q['role']=='main')
        q['deps']=[next(q['id'] for c in bad for q in c['quests'] if q['role']=='tutorial')]
        with self.assertRaises(AssertionError):journey.validate(bad,self.base)

    def test_new_tasks_are_small_and_do_not_farm_rewards(self):
        for q in self.after.values():
            if q.get('journey_new'):
                self.assertEqual(1,q['count']);self.assertEqual('[]',q['rewards'])
                if q['kind']=='item':self.assertIn('consume_items: false',q['tasks'])

    def test_removed_chapter_links_are_redirected(self):
        dead={c['id'] for c in self.base if c['file']+'.snbt' in journey.known_removed()}
        for q in self.after.values():
            for s in q['description']:
                if s.startswith('{"'):self.assertNotIn(json.loads(s)['clickEvent']['value'],dead)

    def test_inline_figures_exist_and_dimensions_are_bounded(self):
        images=[s for q in self.after.values() for s in q['description'] if s.startswith('{image:')]
        self.assertGreaterEqual(len(images),30)
        for s in images:
            self.assertIn('width:220 height:110 align:center',s)
            self.assertIn('fit:true',s,'Images must fit the native 200px minimum-width quest view')
            p=story.ROOT/'src/main/resources/assets'/s.split('image:',1)[1].split(' ',1)[0].replace(':','/',1)
            self.assertTrue(p.is_file())
        from quest_journey_images import FIGURES
        used={s.split(' ',1)[0].rsplit('/',1)[-1].removesuffix('.png') for s in images}
        self.assertEqual(set(FIGURES),used,'Every operation figure needs a real quest-body entry')
        gear=self.after['1000000000c40002']
        self.assertEqual('dynasty:cod4_obtain_qimen_gear',gear['target'])
        self.assertIn('type: "advancement"',gear['tasks'])
        self.assertTrue(any('/qimen.png ' in s for s in gear['description']))

    def test_layout_has_no_close_or_coincident_nodes(self):
        for c in self.book:
            qs=c['quests']
            for i,q in enumerate(qs):
                for p in qs[i+1:]:
                    self.assertGreaterEqual(max(abs(p['x']-q['x']),abs(p['y']-q['y'])),1.0,c['file'])

    def test_visible_arrows_do_not_pass_through_unrelated_buttons(self):
        from quest_layout_geometry import audit
        for c in self.book:
            result=audit(c)
            self.assertEqual([],result['button_penetrations'],c['file'])
            self.assertEqual([],result['edge_crossings'],c['file'])

    def test_layout_keeps_recipe_steps_adjacent_and_ordered(self):
        for c in self.book:
            if c['main']:continue
            lanes={}
            for q in c['quests']:
                if q.get('for_quest'):lanes.setdefault(q['for_quest'],[]).append(q)
            for parent,preps in lanes.items():
                # Main-page materials are now in themed pages; their parent
                # stays on the story spine and is reached by an exact jump.
                lane=preps+([] if self.after[parent]['role']=='main' else [self.after[parent]])
                if self.after[parent]['role']=='main':
                    self.assertTrue(all(q.get('journey_main_origin') for q in preps))
                for a,b in zip(lane,lane[1:]):
                    self.assertAlmostEqual(a['y'],b['y'])
                    self.assertAlmostEqual(1.65,b['x']-a['x'])

    def test_mechanical_branches_are_visible_below_their_prerequisites(self):
        # Regression: the old packed row made gear arrows pass through arrows
        # and an infusion tutorial, falsely suggesting a shared crafting chain.
        chain=['1000000000c40002','1000000000c40001','1000000000c40003',
               '1000000000c40004','1000000000c4000c']
        for a,b in zip(chain,chain[1:]):
            self.assertGreater(self.after[b]['y'],self.after[a]['y'])
            self.assertFalse(self.after[b].get('hide_dependency_lines',False))

    def test_obscured_prerequisites_keep_their_real_detector_and_click_target(self):
        affected=[q for q in self.after.values() if q.get('journey_obscured_dependencies')]
        self.assertGreater(len(affected),10)
        for q in affected:
            self.assertNotEqual('main',q['role'])
            links={json.loads(s).get('clickEvent',{}).get('value')
                   for s in q['description'] if s.startswith('{"')}
            self.assertTrue(set(q['journey_obscured_dependencies']) <= links)
            self.assertTrue(q['hide_dependency_lines'])
        snapshot=json.loads((journey.DOC/'last-deployed-book.json').read_text())
        journey.validate_forward(self.book,snapshot)
        prior={q['id']:q for c in snapshot for q in c['quests']}
        for c in snapshot:
            for old in c['quests']:
                if old['id'] in REMOVED_BLUEPRINT_PREPS:continue
                self.assertEqual(migrated_deps(old['deps'],prior),self.after[old['id']]['deps'])
                self.assertEqual(old.get('size',1.),self.after[old['id']].get('size',1.),
                                 'User requires unchanged quest button scale')

    def test_main_pages_have_no_optional_spurs_and_saved_tasks_survive(self):
        previous=json.loads((journey.DOC/'last-deployed-book.json').read_text())
        old={q['id']:q for c in previous for q in c['quests']}
        added_cod2={journey.ident('cod2:chensha:'+key) for key in ('visit','route','jinwu','hammer')}
        added_cod2|={journey.ident('cod2:wangsi:'+key) for key in ('visit','route')}
        self.assertEqual((set(old)-REMOVED_BLUEPRINT_PREPS)|added_cod2,set(self.after))
        for key,q in old.items():
            if key in REMOVED_BLUEPRINT_PREPS:continue
            n=self.after[key]
            for field in ('tasks','count','rewards','target','kind','deps'):
                self.assertEqual(migrated_deps(q[field],old) if field=='deps' else migrated_tasks(key,q[field]) if field=='tasks' else q[field],n[field],(key,field))
        for c in self.book:
            if not c['main']:continue
            self.assertTrue(all(q['role']=='main' for q in c['quests']))
            self.assertLessEqual(max(q['x'] for q in c['quests'])-min(q['x'] for q in c['quests']),6.)
            self.assertIn(c['autofocus_id'],{q['id'] for q in c['quests']})
        relocated=[q for q in self.after.values() if q.get('journey_main_origin')]
        self.assertEqual(102,len(relocated))

    def test_home_entry_fits_without_changing_quest_or_image_aspect_ratio(self):
        home=next(c for c in self.book if c['file']=='dynasty_home')
        self.assertEqual(19,len(home['images']))
        self.assertEqual({c['id'] for c in self.book if c is not home},
                         {im['click'].lstrip('#') for im in home['images']})
        self.assertEqual(home['quests'][0]['id'],home['autofocus_id'])
        self.assertEqual((0.,0.),(home['quests'][0]['x'],home['quests'][0]['y']))
        from PIL import Image
        for im in home['images']:
            self.assertAlmostEqual(4.,im['width']/im['height'])
        # Conservative FTB default 24px button + 8px spacing; no zoom override.
        main=home['images'][:8]
        self.assertLessEqual(max(im['x']+im['width']/2 for im in main)*32,150)
        self.assertLessEqual(max(abs(im['y'])+im['height']/2 for im in main)*32,100)
        for c in self.book:
            for im in c.get('images',[]):
                with Image.open(story.ROOT/'src/main/resources/assets'/im['image'].replace(':','/',1)) as png:
                    self.assertAlmostEqual(png.width/png.height,im['width']/im['height'],delta=.02)
            self.assertNotIn('zoom',c)
            self.assertNotIn('default_quest_size',c)

    def test_visible_titles_do_not_leak_resource_ids(self):
        for q in self.after.values():
            for field in ('title','display_title'):
                self.assertNotRegex(q.get(field,''),r'\b[a-z_]+:[a-z_]+',q['id'])

    def test_chinese_adjacent_resource_ids_are_translated_in_visible_prose(self):
        for q in self.after.values():
            for line in q['description']:
                text=json.loads(line).get('text','') if line.startswith('{"') else '' if line.startswith('{image:') else line
                # No Unicode word-boundary: Chinese + Latin are both word chars.
                self.assertNotRegex(text,r'(?:minecraft|dynasty|naturescompass|explorerscompass):[a-z0-9_/]+',q['id'])

    def test_lowered_counts_match_kill_titles_and_only_one_goal_line(self):
        q=self.after['1000000000030207']
        self.assertIn('value: 3L',q['tasks']);self.assertIn('3名骷髅',q['title'])
        goals=[journey.clean(s) for s in q['description'] if s.startswith(('&e击败','击败'))]
        self.assertEqual(['击败骷髅×3。'],goals)
        for q in self.after.values():
            detector=re.search(r'type:\s*"kill"[^}]*entity:\s*"([^"]+)"[^}]*value:\s*(\d+)L',q['tasks'])
            if detector and q['target'] not in {'dynasty:royal_guard','dynasty:imperial_soldier','dynasty:jade_guard'}:
                goals=[s for s in q['description'] if re.fullmatch(r'击败[^。]*×\d+。',s)]
                self.assertEqual(1,len(goals),q['id'])
                self.assertIn('×'+detector[2]+'。',goals[0])

    def test_quantity_text_cleanup_does_not_restore_attacking_friendly_troops(self):
        for q in self.after.values():
            if q['target'] in {'dynasty:royal_guard','dynasty:imperial_soldier','dynasty:jade_guard'} and q['kind']=='kill':
                self.assertIn('无需主动攻击',' '.join(q['description']))
                self.assertFalse(any(s.startswith('击败') for s in q['description']))

    def test_bottle_and_target_tutorials_use_vanilla_recipes_without_new_old_gates(self):
        recipes=json.loads((journey.DOC/'round9-vanilla-recipes.json').read_text())['recipes']
        self.assertEqual(['# #',' # '],recipes['glass_bottle']['pattern'])
        self.assertEqual(3,recipes['glass_bottle']['result']['count'])
        self.assertEqual([' R ','RHR',' R '],recipes['target']['pattern'])
        self.assertEqual(9,len(recipes['hay_block']['ingredients']))
        bottles=[self.after[journey.ident('bottle-material:'+key)] for key in ('glass','bottle')]
        self.assertEqual(['minecraft:glass','minecraft:glass_bottle'],[q['target'] for q in bottles])
        self.assertEqual([bottles[0]['id']],bottles[1]['deps'])
        target_materials=[self.after[journey.ident('target-material:'+key)] for key in ('wheat','hay','redstone')]
        self.assertEqual(['minecraft:wheat','minecraft:hay_block','minecraft:redstone'],[q['target'] for q in target_materials])
        for i,q in enumerate(target_materials):
            self.assertEqual([target_materials[i-1]['id']] if i else [],q['deps'])
        for q in bottles+target_materials:
            self.assertIn('type: "item"',q['tasks']);self.assertIn('count: 1L',q['tasks'])
            self.assertIn('consume_items: false',q['tasks']);self.assertEqual('[]',q['rewards'])
        target=self.after['1000000000030208'];text=' '.join(target['description'])
        self.assertIn('标靶×1',target['title']);self.assertIn('不检测搭建或命中',text)
        self.assertIn('target_recipe.png',text)
        water=self.after[journey.ident('brewing:water')]
        self.assertNotIn(bottles[1]['id'],water['deps'])
        self.assertNotIn(target_materials[-1]['id'],target['deps'])
        self.assertIn('玻璃瓶×3',' '.join(bottles[1]['description']))

    def test_native_qa_manifest_has_matching_page_names_ids_and_current_counts(self):
        # Caught a source-only QA bug: appending two PAGES without two NAMES
        # would fail after the original twelve screenshots when display returns.
        source=(story.ROOT/'tools/art/quest-integration-qa/com/dynasty/client/QuestIntegrationQa.java').read_text()
        pages=re.search(r'long\[\] PAGES=\{([^}]+)\}',source)[1]
        names=re.search(r'String\[\] NAMES=\{([^}]+)\}',source)[1]
        ids=[format(int(v,16),'016x') for v in re.findall(r'0x([a-f0-9]+)L',pages)]
        labels=re.findall(r'"([^"]+)"',names)
        plan=json.loads((journey.DOC/'native-plan.json').read_text())
        self.assertEqual(plan,[list(pair) for pair in zip(labels,ids)])
        self.assertEqual(len(ids),len(labels))
        live=set(self.after)|{c['id'] for c in self.book}
        self.assertTrue(set(ids)<=live)
        expected=json.loads((journey.DOC/'native-expectations.json').read_text())
        self.assertEqual(len(self.after),expected['quests'])
        self.assertIn('quests=='+str(len(self.after)),source)
        from quest_journey_images import FIGURES
        self.assertEqual(len(FIGURES),expected['operation_figures'])
        self.assertIn('figures=='+str(len(FIGURES)),source)
        native_figures=re.search(r'String\[\] FIGURES=\{([^}]+)\}',source)[1]
        self.assertEqual(set(FIGURES),set(re.findall(r'"([^"]+)"',native_figures)))
        self.assertIn('for(String name:FIGURES)',source)

    def test_dependency_cycle_rejected(self):
        bad=copy.deepcopy(self.book)
        q=next(q for c in bad for q in c['quests'] if q.get('journey_new'))
        q['deps']=[q['id']]
        with self.assertRaises(AssertionError):journey.validate(bad,self.base)

    def test_merged_charm_catalogue_keeps_real_groups_and_materials_together(self):
        from quest_atlas import charm_sections
        classes=charm_sections()
        c=next(c for c in self.book if c['file']=='dynasty_c10')
        nodes=[q for q in c['quests'] if q.get('section')=='dynasty_accessory_charm']
        retained=[q for q in nodes if not q.get('journey_main_origin')]
        self.assertEqual(104,len(retained))
        items=[q for q in nodes if q['kind']=='item' and not q.get('for_quest')]
        self.assertEqual(86,len([q for q in items if not q.get('journey_main_origin')]))
        self.assertTrue(all(q.get('journey_effect_notes') for q in items))
        for q in items:self.assertEqual(classes[q['target'].split(':')[1]],q['journey_charm_group'])
        for q in nodes:
            if q.get('for_quest'):
                self.assertEqual(self.after[q['for_quest']]['journey_charm_group'],q['journey_charm_group'])
        bounds=[]
        for i in range(4):
            group=[q for q in nodes if q.get('journey_charm_group')==i]
            bounds.append((min(q['x'] for q in group),max(q['x'] for q in group),
                           min(q['y'] for q in group),max(q['y'] for q in group)))
        self.assertGreater(bounds[1][0]-bounds[0][1],1.)
        self.assertGreater(bounds[3][0]-bounds[2][1],1.)
        self.assertGreater(min(bounds[2][2],bounds[3][2])-max(bounds[0][3],bounds[1][3]),2.)

    def test_charm_group_labels_and_route_references_cover_all_registered_charms(self):
        from quest_atlas import charm_sections
        c=next(c for c in self.book if c['file']=='dynasty_c10')
        labels=[im for im in c['images'] if '/labels/charm_' in im['image']]
        self.assertEqual(4,len(labels))
        for i,label in enumerate(labels):
            q=self.after[label['click'].lstrip('#')]
            self.assertEqual(i,q['journey_charm_group']);self.assertFalse(q.get('for_quest'))
            p=story.ROOT/'src/main/resources/assets'/label['image'].replace(':','/',1)
            self.assertTrue(p.is_file())
            for node in c['quests']:
                self.assertFalse(abs(node['x']-label['x'])<label['width']/2+.5 and
                                 abs(node['y']-label['y'])<label['height']/2+.5,node['id'])
        header=self.after[journey.ident('section:dynasty_accessory_charm')]
        links={json.loads(s)['clickEvent']['value'] for s in header['description'] if s.startswith('{"')}
        self.assertEqual(8,len(links));self.assertTrue(links<=set(self.after))
        here={q['target'].split(':')[-1] for q in c['quests']
              if q.get('section')=='dynasty_accessory_charm' and q['kind']=='item' and not q.get('for_quest')}
        covered=here|{self.after[k]['target'].split(':')[-1] for k in links}
        self.assertEqual(set(charm_sections()),covered)

    def test_charm_prose_separates_day_night_cost_and_hit_probability(self):
        dusk=' '.join(self.after['10000000000000d8']['description'])
        self.assertIn('佩戴：夜晚，攻击+26%',dusk)
        self.assertIn('代价：白天，生命上限-20%',dusk)
        self.assertIn('会心，额外伤害+45%；概率25%',dusk)
        blood=' '.join(self.after['1000000000000107']['description'])
        self.assertIn('代价：常驻，生命上限-30%',blood)
        self.assertIn('吸血15%',blood)
        conditional=[q for q in self.after.values() if q.get('journey_effect_notes') and
                     '生命低于40%' in ' '.join(q['description'])]
        self.assertTrue(conditional)
        jade=next(q for q in self.after.values() if q.get('journey_effect_notes') and q['target']=='dynasty:jade_cicada')
        self.assertIn('生命不高于30%',' '.join(jade['description']))
        piercer=next(q for q in self.after.values() if q.get('journey_effect_notes') and q['target']=='dynasty:armor_piercer_token')
        self.assertIn('击退+0.35',' '.join(piercer['description']))

    def test_legacy_charm_tutorial_uses_actual_timers_and_weather_boundary(self):
        notes={q['target']:' '.join(q['description']) for q in self.after.values() if q.get('journey_effect_notes')}
        self.assertIn('每3秒',notes['dynasty:war_drum_charm'])
        self.assertIn('每60秒',notes['dynasty:gold_seal_charm'])
        self.assertIn('下雨或雷雨',notes['dynasty:storm_charm'])
        self.assertIn('灼魂',notes['dynasty:tomb_candle'])
        self.assertIn('取较高者',notes['dynasty:imperial_seal_charm'])

    def test_slot_headers_are_distinct_after_chapter_merge(self):
        headers=[q for q in self.after.values() if q.get('section_header') and
                 (q.get('section','').startswith('dynasty_accessory_') or q.get('section')=='dynasty_c10')]
        self.assertEqual(9,len(headers))
        self.assertEqual(9,len({q['title'] for q in headers}))
        self.assertTrue(all(' · ' in q['title'] for q in headers))

    def test_prep_steps_match_real_recipe_inputs(self):
        recipes=story.recipe_index()
        for q in self.after.values():
            if q.get('for_quest'):
                target=self.after[q['for_quest']]['target']
                self.assertTrue(any((q['target'] in r['ingredients'] or q['target']=='minecraft:oak_planks' and '#minecraft:planks' in r['ingredients']) for r in recipes[target]))

    def test_short_tutorials_keep_scene_conditions(self):
        for item,terms in [('puzzle_box',['40秒','潜行']),('ancient_well',['7次','3分钟']),
                           ('mortuary_room',['2分钟','治疗药水']),('ghost_market_boat',['朱砂','2分钟'])]:
            q=next(q for q in self.after.values() if q.get('cod4_item')==item)
            text=' '.join(s for s in q['description'] if not s.startswith('{'))
            for term in terms:self.assertIn(term,text)
            self.assertLess(len(text),220)

    def test_site_pages_keep_their_building_and_main_hand_action(self):
        from quest_cod4 import SITES,LOCATIONS
        pages={q['cod4_item']:q for q in self.after.values() if q.get('cod4_item') in SITES}
        self.assertEqual(15,len(pages))
        for item,q in pages.items():
            location=LOCATIONS[SITES[item][0]]
            text=' '.join(s for s in q['description'] if not s.startswith('{'))
            self.assertIn('主世界'+location,text,item)
            self.assertIn('旧建筑无互动点',text,item)
            self.assertIn(location,q['subtitle'])
            visit=journey.SITE_VISITS[SITES[item][0]]
            links={json.loads(s)['clickEvent']['value'] for s in q['description'] if s.startswith('{"')}
            self.assertIn(visit,links,item)
            self.assertIn('结构罗盘',' '.join(self.after[visit]['description']))
            self.assertEqual(self.before[q['id']]['tasks'],q['tasks'])
            self.assertEqual(self.before[q['id']]['rewards'],q['rewards'])
        text=' '.join(pages['old_weapon_rack']['description'])
        self.assertIn('等30秒再交互',text)
        text=' '.join(pages['mortuary_room']['description'])
        self.assertIn('主手拿普通治疗药水右键停尸台',text)
        self.assertIn('满2分钟',text)

    def test_site_material_steps_detect_real_items_without_changing_saved_gates(self):
        old={q['id']:q for c in json.loads((journey.DOC/'last-deployed-book.json').read_text()) for q in c['quests']}
        for item,target in [('broken_stele','minecraft:paper'),('nameless_tomb','minecraft:poppy'),('old_bellows','minecraft:charcoal')]:
            q=self.after[journey.ident('site-prep:'+item)]
            site=next(q for q in self.after.values() if q.get('cod4_item')==item)
            self.assertEqual(target,q['target']);self.assertEqual('item',q['kind'])
            self.assertEqual('[]',q['rewards']);self.assertIn('count: 1L',q['tasks'])
            self.assertIn('consume_items: false',q['tasks'])
            self.assertNotIn(q['id'],site['deps'])
            self.assertEqual(old[site['id']]['deps'],site['deps'])
            self.assertEqual(site['deps'],q['deps'])
            self.assertAlmostEqual(site['y'],q['y'])
            self.assertAlmostEqual(1.65,site['x']-q['x'])
            links={json.loads(s)['clickEvent']['value'] for s in site['description'] if s.startswith('{"')}
            self.assertIn(q['id'],links)

    def test_healing_brewing_uses_exact_potion_and_links_to_actual_rescue(self):
        melon=self.after[journey.ident('brewing:melon')];healing=self.after[journey.ident('brewing:healing')]
        self.assertEqual('minecraft:glistering_melon_slice',melon['target'])
        self.assertEqual([journey.ident('brewing:awkward')],melon['deps'])
        self.assertEqual([melon['id']],healing['deps'])
        self.assertEqual('minecraft:healing',healing['journey_potion'])
        self.assertIn('Potion: "minecraft:healing"',healing['tasks'])
        self.assertIn('match_nbt: true',healing['tasks']);self.assertIn('weak_nbt_match: true',healing['tasks'])
        self.assertIn('consume_items: false',healing['tasks'])
        self.assertIn('强效治疗药水不符合',' '.join(healing['description']))
        for q in (melon,healing):self.assertEqual('[]',q['rewards'])
        rescue=self.after['1000000000c40029']
        self.assertNotIn(healing['id'],rescue['deps'])
        for q,target in [(healing,rescue['id']),(rescue,healing['id'])]:
            links={json.loads(s)['clickEvent']['value'] for s in q['description'] if s.startswith('{"')}
            self.assertIn(target,links)
        recipe=json.loads((journey.DOC/'round15-vanilla-recipes.json').read_text())['recipes']['glistering_melon_slice']
        self.assertEqual(['###','#X#','###'],recipe['pattern'])
        self.assertEqual('minecraft:gold_nugget',recipe['key']['#']['item'])
        self.assertEqual('minecraft:melon_slice',recipe['key']['X']['item'])
        tracker=(story.ROOT/'src/main/java/com/dynasty/cod3/SecretTracker.java').read_text()
        self.assertIn('case 29->net.minecraft.world.item.alchemy.PotionUtils.getPotion(p.getMainHandItem())==net.minecraft.world.item.alchemy.Potions.HEALING;',tracker)

    def test_wild_material_pages_state_real_loot_uses_without_next_step_boilerplate(self):
        pairs={
            'fox_pelt':('red_fox','皮革×2'), 'wolf_fang':('gray_wolf','灰狼牙饰'),
            'python_gall':('giant_python','避毒丹'), 'crab_shell':('crab_soldier','精钢'),
            'kappa_scale':('river_imp','避水珠'), 'sprite_jade':('stone_sprite','回春丹'),
            'lantern_oil':('lantern_ghost','安魂香'), 'locust_dust':('locust_swarm','毒烟弹'),
        }
        for item,(enemy,use) in pairs.items():
            q=next(q for q in self.after.values() if q.get('cod4_item')==item)
            text=' '.join(s for s in q['description'] if not s.startswith('{'))
            loot=json.loads((story.ROOT/'src/main/resources/data/dynasty/loot_tables/entities'/f'{enemy}.json').read_text())
            pools=[p for p in loot['pools'] if any(e.get('name')=='dynasty:'+item for e in p['entries'])]
            self.assertTrue(pools,item)
            self.assertTrue(all(any(c['condition']=='minecraft:killed_by_player' for c in p['conditions']) for p in pools))
            self.assertIn('击败后有概率掉落',text);self.assertIn(use,text)
            self.assertIn('×1',text);self.assertNotIn('背包持有即可',text)
            self.assertNotRegex(text,'下一步|下一站|继续前往|沿河继续|去哪里|如何完成|采回来做什么')
            self.assertLess(len(text),180,item)
            self.assertEqual(self.before[q['id']]['tasks'],q['tasks'])
        pearl=json.loads((story.ROOT/'src/main/resources/data/dynasty/recipes/cod4/kappa_pearl.json').read_text())
        self.assertEqual('dynasty:sea_pearl',pearl['result']['item'])
        self.assertEqual({'dynasty:kappa_scale','minecraft:ender_pearl','dynasty:jade'},
                         {i['item'] for i in pearl['ingredients']})

    def test_mechanical_weapon_pages_explain_charge_dual_hand_and_tether_controls(self):
        terms={
            'repeating_crossbow':['蓄满后松手装填','再按住右键','最多装3发','普通箭','不能装重钢弩矢'],
            'siege_crossbow':['蓄满后松手装填','一次1发','普通箭','不能装连发弩矢','消耗连弩'],
            'rope_dart':['12格','拉近','Boss免疫牵引','不能穿墙'],
            'flying_claw':['12格','把自己拉向落点','普通敌人','不会穿墙'],
            'meteor_hammer':['至少1秒后松开','4格','可见敌人'],
            'mandarin_duck_axe':['副手放鸳鸯钺','主手持另一把钺或空手','按住右键','3秒','只持主手一把钺不能'],
        }
        for item,expected in terms.items():
            q=next(q for q in self.after.values() if q.get('cod4_item')==item)
            text=' '.join(s for s in q['description'] if not s.startswith('{'))
            for word in expected:self.assertIn(word,text,item)
            self.assertNotIn('回收过程',text)
            self.assertEqual(self.before[q['id']]['tasks'],q['tasks'])
            self.assertEqual(self.before[q['id']]['rewards'],q['rewards'])
        weapons=(story.ROOT/'src/main/java/com/dynasty/expansion/ExpansionWeapons.java').read_text()
        self.assertIn('CrossbowItem.getChargeDuration(stack)',weapons)
        self.assertIn('s.getItem() instanceof ArrowItem && (!isBolt(s)',weapons)
        self.assertIn('getUseDuration(stack)-remaining<20',weapons)
        guard=(story.ROOT/'src/main/java/com/dynasty/expansion/EquipmentBehaviors.java').read_text()
        self.assertIn('p.getOffhandItem().is(ExpansionContent.DUCK.get())',guard)

    def test_supply_pages_distinguish_craft_detection_from_finishing_item_use(self):
        supplied={'army_ration','regen_pill','qi_pill','antidote_pill','zhuangyuan_wine',
                  'marching_wine','soul_incense','guide_incense'}
        pages=[q for q in self.after.values() if q.get('cod4_item') in supplied]
        self.assertEqual(8,len(pages))
        for q in pages:
            text=' '.join(s for s in q['description'] if not s.startswith('{'))
            self.assertIn('亲手合成',text);self.assertIn('合成就记录，无须试用',text)
            self.assertIn('拾取或购买不计',text);self.assertIn('按住右键直到用完',text)
            self.assertIn('消耗一份',text);self.assertIn('→',text)
            self.assertEqual(self.before[q['id']]['tasks'],q['tasks'])
        byitem={q['cod4_item']:' '.join(q['description']) for q in pages}
        self.assertIn('答题时间增加6秒',byitem['zhuangyuan_wine'])
        self.assertIn('不解除凋零',byitem['antidote_pill'])
        self.assertIn('手持它右键现场互动点，不要先用掉',byitem['soul_incense'])
        self.assertIn('换维度后失效',byitem['guide_incense'])
        for nonfood in ('silk_pouch','jade_crown'):
            text=' '.join(next(q['description'] for q in self.after.values() if q.get('cod4_item')==nonfood))
            self.assertNotIn('直到用完',text);self.assertIn('获得',text)

    def test_map_card_jump_cannot_point_to_removed_chapter(self):
        bad=copy.deepcopy(self.book)
        c=next(c for c in bad if c['file']=='dynasty_home')
        self.assertEqual(19,len(c['images']))
        c['images'][0]['click']='#'+next(c['id'] for c in self.base if c['file']=='dynasty_accessory_ring')
        with self.assertRaises(AssertionError):journey.validate(bad,self.base)

    def test_secondary_item_in_multi_goal_is_also_reduced(self):
        q=next(q for q in self.after.values() if q['title']=='云台防坠 · 水与搭路石')
        self.assertIn('count: 4L',q['tasks']);self.assertNotIn('count: 64L',q['tasks'])
        self.assertIn('圆石×4',' '.join(q['description']))

    def test_every_multi_item_goal_lists_all_serialized_items_and_counts(self):
        from quest_snbt import list_compounds
        from quest_journey_help import display_name
        deployed={q['id']:q for c in json.loads((journey.DOC/'last-deployed-book.json').read_text()) for q in c['quests']}
        affected=[]
        for q in self.after.values():
            compounds=list_compounds('\ttasks: '+q['tasks'],'tasks')
            items=[t for t in compounds if 'type: "item"' in t]
            if len(items)<2:continue
            affected.append(q['id']);text=' '.join(s for s in q['description'] if not s.startswith('{'))
            for task in items:
                target=re.search(r'item:\s*\{[^}]*id:\s*"([^"]+)"',task)[1]
                count=re.search(r'count:\s*(\d+)L',task)[1]
                self.assertIn(display_name(target)+'×'+count,text,q['id'])
            self.assertEqual(migrated_tasks(q['id'],deployed[q['id']]['tasks']),q['tasks'])
            self.assertFalse(any(s.startswith('&e取得') for s in q['description']),q['id'])
        self.assertEqual(25,len(affected))

    def test_old_inventory_advancement_pages_match_actual_json_conditions(self):
        from quest_journey_help import display_name
        for key in ('jade_sword','full_jade_armor','dragon_crystal','keju','dynasty_root'):
            path=story.ROOT/'src/main/resources/data/dynasty/advancements'/f'{key}.json'
            conditions=json.loads(path.read_text())['criteria']['has_item']
            self.assertEqual('minecraft:inventory_changed',conditions['trigger'])
            q=next(q for q in self.after.values() if q['target']=='dynasty:'+key and 'type: "advancement"' in q['tasks'])
            text=' '.join(s for s in q['description'] if not s.startswith('{'))
            for predicate in conditions['conditions']['items']:
                for item in predicate['items']:self.assertIn(display_name(item),text)
            self.assertNotIn('游戏进度界面',text)
            self.assertEqual(self.before[q['id']]['tasks'],q['tasks'])
            self.assertEqual(self.before[q['id']]['rewards'],q['rewards'])
        text=' '.join(self.after['1000000000000065']['description'])
        self.assertIn('同时持有',text);self.assertIn('各1件',text)
        self.assertIn('正式科举另用科举试卷', ' '.join(self.after['100000000000012b']['description']))

    def test_friendly_interaction_and_legacy_marshal_do_not_claim_wrong_completion(self):
        beast=self.after['1000000000000175'];conditions=json.loads((story.ROOT/'src/main/resources/data/dynasty/advancements/beast_friend.json').read_text())['criteria']['tame']
        self.assertEqual('dynasty:qilin',conditions['conditions']['entity']['type'])
        self.assertEqual(['dynasty:immortal_peach'],conditions['conditions']['item']['items'])
        self.assertIn('手持蟠桃右键麒麟',' '.join(beast['description']))
        self.assertIn('dynasty:immortal_peach',beast['icon'])
        marshal=self.after['1000000000000067']
        self.assertIn('可跳过',marshal['subtitle']);self.assertTrue(marshal['unverified_trigger'])
        self.assertEqual(self.before[marshal['id']]['tasks'],marshal['tasks'])
        self.assertEqual(self.before[marshal['id']]['rewards'],marshal['rewards'])
        self.assertNotIn('上：官道驿站',' '.join(self.after['1000000000000147']['description']))

    def test_infusion_station_tutorial_follows_recipe_and_successful_apply(self):
        recipe=json.loads((story.ROOT/'src/main/resources/data/dynasty/recipes/infusion_table.json').read_text())
        self.assertEqual(['SJS','BCB','BBB'],recipe['pattern'])
        self.assertEqual('dynasty:infusion_table',recipe['result']['item'])
        table=self.after[journey.ident('infusion:table')];infusion=self.after['10000000000F1001']
        self.assertEqual('dynasty:infusion_table',table['target']);self.assertEqual('item',table['kind'])
        self.assertIn('青铜锭×5',' '.join(table['description']))
        self.assertIn('银锭×2',' '.join(table['description']))
        self.assertNotIn(table['id'],infusion['deps'])
        materials=json.loads((story.ROOT/'src/main/resources/data/dynasty/infusion/materials.json').read_text())
        bronze=next(m for m in materials if m['itemId']=='dynasty:bronze_ingot')
        self.assertEqual(2,bronze['requiredCount']);self.assertEqual(['WEAPON'],bronze['applicableTypes'])
        self.assertEqual('',bronze['gate']);self.assertEqual(1,bronze['capacityCost'])
        text=' '.join(infusion['description'])
        self.assertIn('青铜锭×2',text);self.assertIn('3级经验',text);self.assertIn('确认一次炼入',text)
        menu=(story.ROOT/'src/main/java/com/dynasty/infusion/InfusionMenu.java').read_text()
        self.assertIn('if(!remove&&p instanceof',menu);self.assertIn('award(sp,"first_infusion")',menu)

    def test_writing_lane_keeps_old_exam_gate_and_uses_true_shapeless_recipe(self):
        evidence=json.loads((journey.DOC/'round10-vanilla-recipes.json').read_text())['entries']
        recipe=evidence['data/minecraft/recipes/writable_book.json']['recipe']
        self.assertEqual('minecraft:crafting_shapeless',recipe['type'])
        self.assertEqual({'minecraft:book','minecraft:ink_sac','minecraft:feather'},
                         {i['item'] for i in recipe['ingredients']})
        qs=[self.after[journey.ident('writing:'+key)] for key in ('book','ink','quill')]
        self.assertEqual(['minecraft:book','minecraft:ink_sac','minecraft:writable_book'],[q['target'] for q in qs])
        for i,q in enumerate(qs):
            self.assertEqual([qs[i-1]['id']] if i else [],q['deps'])
            self.assertEqual('item',q['kind']);self.assertEqual('[]',q['rewards'])
            self.assertIn('consume_items: false',q['tasks'])
        self.assertEqual(self.before['100000000000012a']['deps'],self.after['100000000000012a']['deps'])
        self.assertIn('签名后变成成书',' '.join(qs[-1]['description']))

    def test_nightly_additions_keep_deployed_save_identities(self):
        previous=json.loads((journey.DOC/'last-deployed-book.json').read_text())
        journey.validate_forward(self.book,previous)
        bad=copy.deepcopy(self.book)
        q=next(q for c in bad for q in c['quests'] if q.get('for_quest'))
        q['target']='minecraft:dirt'
        with self.assertRaisesRegex(AssertionError,'identity repurposed'):
            journey.validate_forward(bad,previous)
        bad=copy.deepcopy(self.book)
        c=next(c for c in bad if any(q.get('for_quest') for q in c['quests']))
        c['quests'].remove(next(q for q in c['quests'] if q.get('for_quest')))
        with self.assertRaisesRegex(AssertionError,'quest lost'):
            journey.validate_forward(bad,previous)

    def test_preparation_identity_survives_new_cheaper_recipe(self):
        from unittest.mock import patch
        from quest_story import recipe_index
        recipes=copy.deepcopy(recipe_index())
        parent='1000000000030063'
        c=copy.deepcopy(next(c for c in self.base if c['file']=='dynasty_build_guard'))
        target=next(q['target'] for q in c['quests'] if q['id']==parent)
        recipes[target].insert(0,{'id':'new_cheaper','type':'minecraft:crafting_shapeless',
            'ingredients':{'minecraft:dirt':1,'minecraft:stick':1},'output':1})
        with patch('quest_story.recipe_index',return_value=recipes):
            added=journey.preparations(c)
        expected=json.loads(Path(journey.__file__).with_name('quest_journey_preparations.json').read_text())['parents'][parent]
        actual=[q for q in added if q.get('for_quest')==parent]
        self.assertEqual([(q['id'],q['target']) for q in expected],[(q['id'],q['target']) for q in actual])
        section_locked=[q for q in self.after.values() if q.get('for_quest') and q['section']==c['file'] and not q.get('journey_main_origin')]
        self.assertEqual({q['id'] for q in section_locked},{q['id'] for q in added}-REMOVED_BLUEPRINT_PREPS)

    def test_prep_source_hints_are_grounded_and_short(self):
        from quest_journey_help import source_hint
        for q in self.after.values():
            if q.get('for_quest'):
                self.assertTrue(q['source_hint']);self.assertEqual(__import__('quest_readability_oct20').shorten(source_hint(q['target'])),q['description'][1])
                self.assertLess(len(q['description'][1]),180)
        self.assertIn('没有朱砂矿',source_hint('dynasty:cinnabar'))
        self.assertIn('Y=-60至-5',source_hint('dynasty:dragon_crystal'))
        self.assertIn('纸',source_hint('dynasty:blueprint'))

    def test_distant_arrows_preserve_gates_and_have_clickable_prerequisites(self):
        hidden=[q for q in self.after.values() if q.get('journey_distant_dependencies')]
        self.assertGreater(len(hidden),10)
        for q in hidden:
            self.assertNotEqual('main',q['role'])
            links={json.loads(s)['clickEvent']['value'] for s in q['description'] if s.startswith('{"')}
            self.assertTrue(set(q['journey_distant_dependencies'])<=links)
            self.assertTrue(set(q['journey_distant_dependencies'])<=set(q['deps']))
            c=next(c for c in self.book if q in c['quests'])
            self.assertIn('hide_dependency_lines: true',story.encode(c))
        bad=copy.deepcopy(self.book)
        q=next(q for c in bad for q in c['quests'] if q.get('journey_distant_dependencies'))
        q['description']=[s for s in q['description'] if not s.startswith('{"')]
        with self.assertRaisesRegex(AssertionError,'Hidden prerequisite'):
            journey.validate(bad,self.base)

    def test_compass_steps_detect_real_items_not_reading(self):
        targets={'naturescompass:naturescompass','explorerscompass:explorerscompass'}
        helpers=[self.after[journey.ident('navigation:'+s)] for s in ('nature','explorer')]
        self.assertEqual(targets,{q['target'] for q in helpers})
        for q in helpers:
            self.assertEqual('item',q['kind']);self.assertEqual('[]',q['rewards'])
            self.assertIn('四角留空',' '.join(q['description']))
        q=self.after['100000000001000b']
        self.assertIn('自然指南针×1、结构罗盘×1',' '.join(q['description']))
        self.assertEqual(q['tasks'],self.before[q['id']]['tasks'])

    def test_refining_detail_keeps_actual_stage_and_costs(self):
        for route in ('guard','sword','archer','talisman'):
            guide=self.after[journey.ident('refining:'+route)]
            text=' '.join(guide['description'])
            for term in ('0–9','10–24','25–49','50级','上限64','上限39'):
                self.assertIn(term,text)
            q=next(q for q in self.after.values() if q['target']=='dynasty:refine_'+route+'_30')
            self.assertIn('+30',q['description'][0]);self.assertIn('龙晶×55、玄天玉×37',' '.join(q['description']))
            self.assertLess(sum(len(s) for s in q['description'] if not s.startswith('{')),180)

    def test_repetitive_loot_and_slot_prose_are_compact(self):
        for q in self.after.values():
            self.assertFalse(any(s.startswith(('探索宝箱：','可能掉落：')) for s in q['description']))
            if q['target'].startswith('guide:slot_'):
                self.assertLess(sum(len(s) for s in q['description'] if not s.startswith('{')),140)

    def test_launcher_drift_is_rejected_without_writes(self):
        from tempfile import TemporaryDirectory
        from sync_quest_journey import check_baseline,digest
        with TemporaryDirectory() as folder:
            p=Path(folder)/'data.snbt';p.write_bytes(b'{original: true}')
            expected={'data.snbt':digest(p.read_bytes())}
            check_baseline(Path(folder),expected)
            p.write_bytes(b'{other_developer: true}')
            with self.assertRaisesRegex(AssertionError,'Launcher definitions changed'):
                check_baseline(Path(folder),expected)
            self.assertEqual(b'{other_developer: true}',p.read_bytes())

    def test_merged_chapter_number_does_not_survive_in_prose(self):
        q=self.after['10000000000a0005']
        self.assertIn('《四象试炼与讨伐》',' '.join(q['description']))
        self.assertNotIn('第 09 章',' '.join(q['description']))

    def test_wind_main_uses_normal_recipe_and_preserves_optional_event_detector(self):
        q=self.after['1000000000010026'];text=' '.join(q['description'])
        self.assertIn('普通羽毛×2',text);self.assertIn('丝绸×1',text)
        self.assertIn('符纸×1',text);self.assertIn('御风符×1',text)
        normal=json.loads((story.ROOT/'src/main/resources/data/dynasty/recipes/wind_talisman.json').read_text())
        self.assertEqual(['dynasty:talisman_paper','minecraft:feather','minecraft:feather','dynasty:silk'],
                         [i['item'] for i in normal['ingredients']])
        self.assertEqual(1,normal['result']['count'])
        self.assertEqual(self.before[q['id']]['deps'],q['deps'])
        rare=self.after['10d388e6188a3f8e']
        self.assertIn('可选',rare['title']);self.assertEqual('dynasty:xuanniao_shenyu',rare['target'])
        self.assertNotIn(rare['id'],q['deps'])
        materials=[self.after[journey.ident('wind-material:'+key)] for key in ('feather','silk','paper')]
        self.assertEqual(['minecraft:feather','dynasty:silk','dynasty:talisman_paper'],[m['target'] for m in materials])
        for i,m in enumerate(materials):
            self.assertEqual('item',m['kind'])
            self.assertEqual([materials[i-1]['id']] if i else q['deps'],m['deps'])

    def test_rare_feather_help_matches_event_conditions_and_probability(self):
        from quest_journey_help import source_hint
        cat=json.loads((story.ROOT/'src/main/resources/data/dynasty/world_events/catalog.json').read_text())
        event=next(e for e in cat if e['id']=='dynasty:xuanniao_zhige')
        text=source_hint('dynasty:xuanniao_shenyu')
        self.assertIn(str(event['minDistanceFromSpawn'])+'格',text)
        self.assertIn(str(event['radius'])+'格',text)
        self.assertEqual((0,12000),(event['startTime'],event['endTime']))
        self.assertIn('主世界白天',text)
        loot=json.loads((story.ROOT/'src/main/resources/data/dynasty/loot_tables/events/xuanniao_zhige.json').read_text())
        chance=loot['pools'][0]['conditions'][0]['chance']
        self.assertIn(str(round(chance*100))+'%',text);self.assertIn('非必出',text)
        manager=(story.ROOT/'src/main/java/com/dynasty/worldevent/DynastyWorldEventManager.java').read_text()
        kills=re.search(r'getInt\(KILLS\)>=(\d+)',manager)
        self.assertIn(kills[1]+'只敌对怪',text)
        celestial=manager.split('case CELESTIAL->{',1)[1].split('default->',1)[0]
        ticks=int(re.search(r'instance.started>=(\d+)',celestial)[1])
        self.assertIn(str(ticks//20)+'秒',text)

    def test_building_material_sources_and_altar_types_are_distinct(self):
        courtyard=(story.ROOT/'src/main/java/com/dynasty/structure/AcademyCourtyard.java').read_text()
        for short,symbol,qid in [('marble_block','MARBLE_BLOCK','1000000000000022'),
                                  ('crimson_pillar','CRIMSON_PILLAR','1000000000000024')]:
            self.assertIn('DynastyBlocks.'+symbol,courtyard)
            loot=json.loads((story.ROOT/f'src/main/resources/data/dynasty/loot_tables/blocks/{short}.json').read_text())
            self.assertEqual('dynasty:'+short,loot['pools'][0]['entries'][0]['name'])
            self.assertNotIn('silk_touch',json.dumps(loot))
            text=' '.join(self.after[qid]['description'])
            self.assertIn('书院',text);self.assertIn('无须精准采集',text)
            self.assertIn('academy_materials.png',text)
        altar=self.after['1000000000000027']
        self.assertIn('建筑装饰',altar['title'])
        self.assertIn('法阵·祭坛',' '.join(altar['description']))
        self.assertEqual('dynasty:altar',altar['target'])

    def test_acquisition_help_does_not_claim_crafting_or_manual_detection(self):
        for key in ('nature','explorer'):
            q=self.after[journey.ident('navigation:'+key)]
            self.assertIn('获得',q['description'][0])
            self.assertNotIn('合成并持有',q['description'][0])
        for route in ('guard','sword','archer','talisman'):
            q=self.after[journey.ident('refining:'+route)]
            self.assertEqual('checkmark',q['kind'])
            self.assertIn('本页是阅读教程',' '.join(q['description']))

    def test_army_clear_prose_follows_serialized_detector_without_changing_cod6(self):
        from quest_cod6 import QUESTS
        for qid in QUESTS:
            q=self.after[qid];text=' '.join(s for s in q['description'] if not s.startswith('{'))
            self.assertIn('advancement: "dynasty:army_clear_',q['tasks'])
            self.assertEqual(self.before[qid]['tasks'],q['tasks'])
            self.assertEqual(self.before[qid]['deps'],q['deps'])
            self.assertIn('完成',q['description'][0]);self.assertIn('军阵关卡',q['description'][0])
            self.assertIn('募兵台',text);self.assertIn('关卡结算胜利',text)
            self.assertIn('野外击杀不算本节点',text)
            self.assertNotIn('自然生成',text);self.assertNotIn('亲自击败',text)
        army=(story.ROOT/'src/main/java/com/dynasty/army/ArmyEncounters.java').read_text()
        self.assertIn('"army_clear_"+id',army);self.assertIn('troops.isEmpty()',army)

    def test_brewing_filters_require_the_actual_potion_and_keep_legacy_identity(self):
        c=next(c for c in self.book if c['file']=='dynasty_c1')
        export=story.encode(c)
        qs=[self.after[journey.ident('brewing:'+key)] for key in ('stand','fuel','wart','water','awkward')]
        self.assertEqual(['minecraft:brewing_stand','minecraft:blaze_powder','minecraft:nether_wart','minecraft:potion','minecraft:potion'],[q['target'] for q in qs])
        for i,q in enumerate(qs):self.assertEqual([qs[i-1]['id']] if i else [],q['deps'])
        for q,expected in zip(qs[-2:],['minecraft:water','minecraft:awkward']):
            self.assertIn('tag: { Potion: "'+expected+'" }',q['tasks'])
            self.assertIn('match_nbt: true',q['tasks']);self.assertIn('weak_nbt_match: true',q['tasks'])
            self.assertIn(q['tasks'].split('item: ',1)[1].split(', count:',1)[0],export)
        legacy=self.after['100000000000002b']
        self.assertEqual(self.before[legacy['id']]['tasks'],legacy['tasks'])
        self.assertEqual(self.before[legacy['id']]['rewards'],legacy['rewards'])
        self.assertIn('可跳过',legacy['subtitle']);self.assertTrue(legacy['unverified_source'])

    def test_structure_visits_are_short_actionable_and_keep_actual_advancements(self):
        for qid in ('10000000000a0000','10000000000a0005','10000000000a0006'):
            q=self.after[qid];text=' '.join(s for s in q['description'] if not s.startswith('{'))
            self.assertEqual(self.before[qid]['tasks'],q['tasks'])
            self.assertIn('进入',q['description'][0]);self.assertIn('结构罗盘',text)
            self.assertNotIn('place',text);self.assertNotIn('dynasty:',text)
            self.assertLess(len(text),100)

    def test_accessory_upgrade_prose_preserves_effect_and_actual_recipe(self):
        selected=[q for q in self.after.values() if q.get('route') and q.get('subtitle')=='进阶饰品']
        expected=[q for q in self.before.values() if q.get('route') and q.get('subtitle')=='进阶饰品']
        self.assertEqual({q['id'] for q in expected},{q['id'] for q in selected})
        for q in selected:
            self.assertIn(q['purpose']+'。',q['description'])
            recipes=[s for s in q['description'] if '→' in s]
            self.assertEqual(1,len(recipes));self.assertIn('保留淬炼',' '.join(q['description']))
            self.assertLess(sum(len(s) for s in q['description'] if not s.startswith('{')),140)

if __name__=='__main__':unittest.main()

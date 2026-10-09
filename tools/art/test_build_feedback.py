"""Geometry, localization and generated resource regressions for the feedback update."""
import json,unittest,subprocess
from pathlib import Path
from quest_story import build_book
ROOT=Path(__file__).resolve().parents[2];RES=ROOT/'src/main/resources'
class FeedbackTests(unittest.TestCase):
    def test_new_visits_have_real_world_predicates(self):
        rows=[q for c in build_book() for q in c['quests'] if q['role']=='exploration_branch']
        visits={'dynasty:visit_post_house','dynasty:visit_herbal_retreat','dynasty:tiangong_mining_estate','dynasty:visit_desert_caravan','dynasty:tiangong_citadel','dynasty:visit_ruined_battlefield'}
        found={q['target'] for q in rows if q['kind']=='advancement'}
        self.assertTrue(visits<=found,'All six visits must remain present alongside newer crafting/combat branches')
        for q in rows:
            if q['kind']!='advancement' or q['target'] not in visits:continue
            a=json.loads((RES/('data/dynasty/advancements/'+q['target'].split(':')[1]+'.json')).read_text())
            location=[c for c in a['criteria'].values() if c['trigger']=='minecraft:location']
            self.assertEqual(1,len(location));pred=location[0]['conditions']['player'][0]['predicate']
            self.assertEqual('minecraft:overworld',pred['dimension'])
            structure=json.loads((RES/('data/dynasty/worldgen/structure/'+pred['structure'].split(':')[1]+'.json')).read_text())
            expected=q['target'] if q['target'] in {'dynasty:tiangong_mining_estate','dynasty:tiangong_citadel'} else 'dynasty:travel_site'
            if q['target']=='dynasty:visit_ruined_battlefield':expected='dynasty:battlefield'
            self.assertEqual(expected,structure['type']);self.assertTrue(structure['biomes'])
    def test_refinement_pages_do_not_repeat_previous_band(self):
        from quest_growth import refining_costs
        for start,end in [(0,1),(1,5),(5,15),(15,30)]:
            lines=[l for l in refining_costs(end,lambda s:s) if l.startswith('+')]
            self.assertEqual(end-start,len(lines));self.assertTrue(lines[0].startswith(f'+{start} → +{start+1}'))
    def test_side_meshes_cover_only_real_silhouette_pixels(self):
        count=0
        for p in (RES/'assets/dynasty/models/item').glob('*.json'):
            m=json.loads(p.read_text())
            if not m.get('dynasty_solid_edges'):continue
            self.assertEqual('dynasty:item/solid_handheld',m['parent'],p.name)
            parent=json.loads((RES/'assets/dynasty/models/item/solid_handheld.json').read_text())
            self.assertNotIn('parent',parent,'builtin/generated ancestors discard explicit elements at runtime')
            count+=1;png=RES/('assets/'+m['textures']['layer0'].replace(':','/textures/',1)+'.png')
            w,h=map(int,subprocess.check_output(['magick','identify','-format','%w %h',str(png)]).split())
            rgba=subprocess.check_output(['magick',str(png),'-alpha','on','-depth','8','RGBA:-'])
            def opaque(x,y):return 0<=x<w and 0<=y<h and rgba[(y*w+x)*4+3]>=26
            front=m['elements'][0];self.assertEqual([0,0,16,16],front['faces']['south']['uv']);self.assertEqual([16,0,0,16],front['faces']['north']['uv'])
            expected={(x,y,face) for y in range(h) for x in range(w) if opaque(x,y)
                for face,dx,dy in [('west',-1,0),('east',1,0),('up',0,-1),('down',0,1)] if not opaque(x+dx,y+dy)}
            actual=set()
            for e in m['elements'][1:]:
                x=round(e['from'][0]*w/16);y=round(h-e['to'][1]*h/16)
                for face,data in e['faces'].items():
                    actual.add((x,y,face));u,v,u2,v2=data['uv']
                    self.assertTrue(x<u*w/16<u2*w/16<x+1,p.name)
                    self.assertTrue(y<v*h/16<v2*h/16<y+1,p.name)
                self.assertAlmostEqual(16/w,e['to'][0]-e['from'][0]);self.assertAlmostEqual(16/h,e['to'][1]-e['from'][1])
            self.assertEqual(expected,actual,p.name)
        self.assertGreaterEqual(count,32)
        for key in ('leifu_staff','taiyi_whisk_icon'):
            self.assertTrue(json.loads((RES/f'assets/dynasty/models/item/{key}.json').read_text())['dynasty_solid_edges'])
    def test_whisk_held_path_preserves_original_inventory_art(self):
        held=json.loads((RES/'assets/dynasty/models/item/taiyi_whisk.json').read_text())
        icon=json.loads((RES/'assets/dynasty/models/item/taiyi_whisk_icon.json').read_text())
        parent=json.loads((RES/'assets/dynasty/models/item/solid_handheld.json').read_text())
        self.assertEqual('builtin/entity',held['parent'])
        self.assertEqual(parent['display'],held['display'])
        self.assertEqual('dynasty:item/taiyi_whisk',icon['textures']['layer0'])
        self.assertTrue(icon['elements']);self.assertTrue(icon['dynasty_solid_edges'])
    def test_armor_outputs_are_complete_square_rgba_icons(self):
        manifest=json.loads((ROOT/'docs/art/build-feedback-v5/armor-assets.json').read_text());self.assertEqual(12,len(manifest))
        for row in manifest:
            p=RES/f"assets/dynasty/textures/item/{row['id']}.png"
            dimensions=subprocess.check_output(['magick','identify','-format','%w %h %[channels]',str(p)]).decode()
            self.assertTrue(dimensions.startswith('128 128 srgba'),dimensions)
    def test_lamp_texture_and_localization(self):
        m=json.loads((RES/'assets/dynasty/models/block/element_lamp_2_off.json').read_text())
        self.assertNotIn('minecraft:block/magma_block',m['textures'].values())
        zh=json.loads((RES/'assets/dynasty/lang/zh_cn.json').read_text())
        self.assertIn('箱子',zh['dynasty.puzzle.msg.solved_claim']);self.assertIn('下一步',zh['dynasty.puzzle.clue.lamp'])
if __name__=='__main__':unittest.main(verbosity=2)

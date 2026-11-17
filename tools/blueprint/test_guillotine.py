"""Focused non-JVM regressions. Interprets the actual whitelisted Java clock methods.

This does not check Java types, Forge APIs, live collision, sound or network timing.
"""
import copy
import json
import math
import re
import unittest
from pathlib import Path
from review_chensha_architecture import JavaCoordinates, PARSER, ROOT
from build_guillotine import MODELS, TEXTURES, ASSETS, model, vanilla_images

FIELDS={'warning','active','recovery','pulseTicks','contactDelay','phase','ticks','warningGear','lastUpdate','contact'}


class ClockCode(JavaCoordinates):
    def expr(self,n):
        text=n.text.decode();f=n.child_by_field_name
        if n.type=='identifier' and text in FIELDS:return 'state['+repr(text)+']'
        if n.type=='field_access' and text.startswith('Phase.'):return repr(text[6:])
        if n.type=='method_invocation' and text=='duration()':return 'duration(state)'
        if n.type=='binary_expression' and n.child_by_field_name('operator').text==b'/':
            # The clock divisions are Java int / int, truncating toward zero.
            return 'int('+self.expr(f('left'))+'/'+self.expr(f('right'))+')'
        if n.type=='switch_expression':
            condition=self.expr(f('condition'));cases=[];default=None
            for rule in f('body').named_children:
                label,value=rule.named_children;value=self.expr(value.named_children[0])
                if label.named_children:cases.append((label.named_children[0].text.decode(),value))
                else:default=value
            assert default is not None
            for label,value in reversed(cases):default=f'({value} if {condition}=={label!r} else {default})'
            return default
        return super().expr(n)

    def statements(self,n,depth=1):
        if n.type=='return_statement' and not n.named_children:return '    '*depth+'return\n'
        return super().statements(n,depth)

    def clock(self,source):
        tree=PARSER.parse(source);assert not tree.root_node.has_error
        body=next(n for n in tree.root_node.named_children if n.type=='class_declaration').child_by_field_name('body')
        env=dict(self.env)
        for method in body.named_children:
            if method.type!='method_declaration':continue
            name=method.child_by_field_name('name').text.decode()
            if name not in {'duration','trigger','tickActive','pause','consumeContact','reset'}:continue
            args=[p.child_by_field_name('name').text.decode() for p in method.child_by_field_name('parameters').named_children]
            code='def '+name+'(state'+''.join(','+a for a in args)+'):\n'+self.statements(method.child_by_field_name('body'))
            exec(compile(code,'actual DungeonHazard.'+name,'exec'),env)
        return env


class GeometryCode(JavaCoordinates):
    def expr(self,n):
        f=n.child_by_field_name
        if n.type=='object_creation_expression' and f('type').text==b'AABB':
            return '('+','.join(self.expr(c) for c in f('arguments').named_children)+')'
        if n.type=='method_invocation':
            name=f('name').text.decode();obj=f('object');raw=obj.text.decode() if obj else ''
            if raw=='anchor' and name in ('getX','getY','getZ'):return 'anchor['+str(('getX','getY','getZ').index(name))+']'
            if raw=='facing' and name=='getAxis':return '("Z" if facing in ("NORTH","SOUTH") else "X")'
        return super().expr(n)


def initial(w=20,a=4,r=16,pulse=0,delay=2):
    return dict(warning=w,active=a,recovery=r,pulseTicks=pulse,contactDelay=delay,phase='IDLE',ticks=0,
                warningGear=0,lastUpdate=-1,contact=False)


class GuillotineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clock=ClockCode().clock((ROOT/'src/main/java/com/dynasty/dungeon/DungeonHazard.java').read_bytes())
        code=GeometryCode();source=(ROOT/'src/main/java/com/dynasty/dungeon/GuillotineTrap.java').read_text()
        constants=re.search(r'public static final double ([^;]+);',source)[1]
        code.env.update({key:float(value) for key,value in (entry.split('=') for entry in constants.split(','))})
        cls.geometry=code.load('GuillotineTrap',['bladeY','sweep'])

    def test_real_clock_delays_contact_until_drop_finishes(self):
        s=initial();self.clock['trigger'](s,0);hits=[]
        for t in range(2,41,2):
            self.clock['tickActive'](s,t)
            if self.clock['consumeContact'](s):hits.append(t)
            self.assertFalse(self.clock['consumeContact'](s))
        self.assertEqual([22],hits);self.assertEqual('IDLE',s['phase'])

    def test_same_core_schedule_repeats_exactly_forty_ticks(self):
        s=initial();hits=[]
        for t in range(0,124,2):
            if s['phase']=='IDLE':self.clock['trigger'](s,t)
            self.clock['tickActive'](s,t)
            if s['phase']=='IDLE':self.clock['trigger'](s,t)
            if self.clock['consumeContact'](s):hits.append(t)
        self.assertEqual([22,62,102],hits)

    def test_existing_eight_profile_timelines_match_pre_edit_source(self):
        old=ClockCode().clock((ROOT/'docs/art/cod2-guillotine-v1/before/src/main/java/com/dynasty/dungeon/DungeonHazard.java').read_bytes())
        profiles=(ROOT/'src/main/java/com/dynasty/dungeon/DungeonTrapProfile.java').read_text()
        rows=re.findall(r'(\w+)\("[^"\n]+",(\d+),(\d+),(\d+),[\d.]+,(?:true|false)\)',profiles)
        self.assertEqual(9,len(rows))
        for name,w,a,r in rows:
            if name=='GUILLOTINE':continue
            before=initial(int(w),int(a),int(r),20 if name=='ARROW_RAIN' else 0,0);after=copy.deepcopy(before)
            for t in list(range(0,200,2))+[1000,1002,1004,1006]:
                for api,s in ((old,before),(self.clock,after)):
                    if s['phase']=='IDLE':api['trigger'](s,t)
                    api['tickActive'](s,t)
                self.assertEqual(before,after,(name,t))
                self.assertEqual(old['consumeContact'](before),self.clock['consumeContact'](after))

    def test_pause_and_long_time_gap_do_not_mint_contacts(self):
        s=initial();self.clock['trigger'](s,0)
        for t in range(2,21,2):self.clock['tickActive'](s,t)
        self.clock['pause'](s,1000);self.assertEqual(0,s['ticks'])
        self.clock['tickActive'](s,1002);self.assertTrue(self.clock['consumeContact'](s))
        self.clock['pause'](s,2000);self.clock['tickActive'](s,2002);self.assertFalse(self.clock['consumeContact'](s))
        self.clock['reset'](s);self.clock['trigger'](s,0);self.clock['tickActive'](s,10000)
        self.assertEqual(('WARNING',0,False),(s['phase'],s['ticks'],s['contact']))

    def test_existing_arrow_pulses_keep_integer_division_semantics(self):
        s=initial(30,40,80,20,0);self.clock['trigger'](s,0);hits=[]
        for t in range(2,71,2):
            self.clock['tickActive'](s,t)
            if self.clock['consumeContact'](s):hits.append(t)
        self.assertEqual([30,50],hits)

    def test_motion_and_contact_have_same_geometry(self):
        g=self.geometry
        self.assertEqual(-.875,g.bladeY(0,0));self.assertEqual(-.875,g.bladeY(2,0))
        self.assertEqual(-3,g.bladeY(2,.5));self.assertEqual(-3,g.bladeY(2,1))
        self.assertEqual(-.875,g.bladeY(3,1))
        for direction in ('NORTH','SOUTH','EAST','WEST'):
            box=g.sweep((-16,20,-1),direction)
            self.assertEqual((17,19.875),(box[1],box[4]))
            self.assertEqual((2.75,.375) if direction in ('NORTH','SOUTH') else (.375,2.75),
                             (box[3]-box[0],box[5]-box[2]))

    def test_new_sources_parse_as_java(self):
        paths=list((ROOT/'docs/art/cod2-guillotine-v1/before/src/main/java').rglob('*.java'))
        for p in paths:
            actual=ROOT/'src/main/java'/p.relative_to(ROOT/'docs/art/cod2-guillotine-v1/before/src/main/java')
            self.assertFalse(PARSER.parse(actual.read_bytes()).root_node.has_error,str(actual))
        for name in ('GuillotineTrap','GuillotineGameTests'):
            p=ROOT/f'src/main/java/com/dynasty/dungeon/{name}.java'
            self.assertFalse(PARSER.parse(p.read_bytes()).root_node.has_error,str(p))

    def test_generated_models_and_uv_resolve_existing_vanilla_textures(self):
        from PIL import Image
        from io import BytesIO
        for data in vanilla_images():
            atlas=Image.open(BytesIO(data)).convert('RGBA')
            self.assertEqual((16,16),atlas.size);self.assertEqual((255,255),atlas.getextrema()[3])
        for name,cubes in MODELS.items():
            data=json.loads((ASSETS/f'models/block/cod2_guillotine/{name}.json').read_text())
            self.assertEqual(json.loads(json.dumps(model(cubes))),data)
            for e in data['elements']:
                self.assertTrue(all(0<=a<b<=16 for a,b in zip(e['from'],e['to'])))
                for face in e['faces'].values():
                    self.assertEqual([0,0,16,16],face['uv'])
                    self.assertIn(data['textures'][face['texture'][1:]],TEXTURES)
        variants=json.loads((ASSETS/'blockstates/guillotine_trap.json').read_text())['variants']
        self.assertEqual({'facing='+f for f in ('north','south','east','west')},set(variants))

    def test_chinese_warning_is_present_without_claiming_natural_dungeon(self):
        lang=json.loads((ASSETS/'lang/zh_cn.json').read_text())
        self.assertEqual('悬闸狗头铡',lang['block.dynasty.guillotine_trap'])
        self.assertIn('离开',lang['message.dynasty.dungeon.guillotine_warning'])
        probe=(ROOT/'src/main/java/com/dynasty/dungeon/DungeonProbePiece.java').read_text()
        self.assertIn('new BlockPos(6,4,37),"guillotine_probe",DungeonContent.GUILLOTINE.get()',probe)

    def test_cuboids_have_no_overlapping_coplanar_outer_faces(self):
        for model_name,cubes in MODELS.items():
            for i,(name,lo,hi,material) in enumerate(cubes):
                for other,bottom,top,_ in cubes[i+1:]:
                    for axis in range(3):
                        overlap=all(min(hi[k],top[k])-max(lo[k],bottom[k])>1e-6 for k in range(3) if k!=axis)
                        if not overlap:continue
                        self.assertFalse(lo[axis]==bottom[axis] or hi[axis]==top[axis],
                            f'{model_name}: same-facing overlap between {name} and {other}, axis {axis}')


if __name__=='__main__':unittest.main()

"""Refine the existing seven-state rigs without recreating their geometry or materials."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'src/main/resources/assets/dynasty'

def refine():
    for name in ('tree_spirit', 'lantern_ghost', 'river_imp', 'drowning_ghost', 'jingwei_bird'):
        path = ASSETS / 'animations/secondary' / (name + '.animation.json')
        document = json.loads(path.read_text())
        geometry = json.loads((ASSETS / 'geo/secondary' / (name + '.geo.json')).read_text())
        bones = {bone['name'] for bone in geometry['minecraft:geometry'][0]['bones']}
        special = document['animations']['special']
        special.update(loop=True, animation_length=.8)
        motion = special['bones']
        motion['root'] = {'position': {'0.0': [0, 0, 0], '0.18': [0, -.6, .8], '0.32': [0, .25, -.6], '0.8': [0, 0, 0]}}
        motion['head'] = {'rotation': {'0.0': [-12, 0, 0], '0.2': [-25, 0, 0], '0.32': [16, 0, 0], '0.8': [0, 0, 0]}}
        if name == 'tree_spirit':
            for bone in bones:
                if bone.startswith('branch_'):
                    motion[bone] = {'rotation': {'0.0': [0, 0, 0], '0.2': [-28, 0, (int(bone[-1]) - 1.5) * 8], '0.32': [18, 0, 0], '0.8': [0, 0, 0]}}
        elif name == 'lantern_ghost':
            motion['ribs'] = {'scale': {'0.0': [1, 1, 1], '0.22': [1.12, 1.05, 1.12], '0.4': [1, 1, 1]}, 'rotation': [0, 'query.anim_time * 40', 0]}
        elif name == 'jingwei_bird':
            motion['stone'] = {'scale': {'0.0': [1, 1, 1], '0.25': [1, 1, 1], '0.3': [0, 0, 0], '0.8': [0, 0, 0]}}
        else:
            for side, sign in (('left', 1), ('right', -1)):
                motion[side + '_fin'] = {'rotation': {'0.0': [0, 0, sign * 15], '0.2': [-45, 0, sign * 35], '0.45': [-75, 0, sign * 20], '0.8': [0, 0, 0]}}
        assert set(motion) <= bones
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')

def refine_contact_actions():
    # Authored phase clips supplement, rather than replace, each original seven-state rig.
    kinds = {
        'red_fox': ('pounce',), 'golden_leopard': ('stalk', 'pounce'),
        'giant_python': ('coil',), 'carp_spirit': ('pounce', 'return_water'),
        'crab_soldier': ('side_charge', 'pinch'), 'bat_demon': ('circle', 'dive'),
        'gray_falcon': ('circle', 'dive'), 'wooden_magpie': ('circle', 'dive'),
        'corpse_beetle': ('burrow', 'eruption'), 'stone_worm': ('burrow', 'eruption'),
        'venom_scorpion': ('pinch', 'sting'), 'wandering_spirit': ('possession',),
    }
    for name, clips in kinds.items():
        path = ASSETS / 'animations/secondary' / (name + '.animation.json')
        doc = json.loads(path.read_text())
        geo = json.loads((ASSETS / 'geo/secondary' / (name + '.geo.json')).read_text())
        available = {bone['name'] for bone in geo['minecraft:geometry'][0]['bones']}
        for clip in clips:
            bones = {'root': {}}
            if clip == 'stalk':
                bones['body'] = {'position': [0, -2.4, 0], 'rotation': [-8, 0, 0]}
                bones['head'] = {'rotation': [12, 0, 0]}
                bones['tail'] = {'rotation': [0, 'math.sin(query.anim_time * 180) * 10', -12]}
                for i in range(4): bones['leg_' + str(i)] = {'rotation': [-22 if i < 2 else 24, 0, 0]}
            elif clip == 'pounce':
                bones['root'] = {'rotation': {'0.0': [-12, 0, 0], '0.25': [-28, 0, 0], '0.45': [8, 0, 0], '0.8': [0, 0, 0]}}
                bones['head'] = {'rotation': {'0.0': [-10, 0, 0], '0.3': [22, 0, 0], '0.8': [0, 0, 0]}}
                for i in range(4): bones['leg_' + str(i)] = {'rotation': [-50 if i < 2 else 45, 0, 0]}
                if name == 'carp_spirit':
                    bones['tail'] = {'rotation': [0, 'math.sin(query.anim_time * 420) * 25', 0]}
                    bones['left_fin'] = {'rotation': [0, 0, 55]}; bones['right_fin'] = {'rotation': [0, 0, -55]}
            elif clip == 'coil':
                for i in range(1, 7): bones['segment_' + str(i)] = {'rotation': [0, 24 + i * 3, 'math.sin(query.anim_time * 150) * 3']}
                bones['head'] = {'rotation': [-18, -30, 0]}
            elif clip in ('circle', 'dive'):
                diving = clip == 'dive'
                bones['body'] = {'rotation': [52 if diving else -8, 0, 15 if not diving else 0]}
                for side, sign in (('left', 1), ('right', -1)):
                    bones[side + '_wing'] = {'rotation': [10 if diving else 0, 0, sign * 40 if diving else 'math.sin(query.anim_time * 500) * ' + str(sign * 25)]}
                    bones[side + '_wingtip'] = {'rotation': [0, 0, sign * 28 if diving else 'math.sin(query.anim_time * 500 - 25) * ' + str(sign * 32)]}
                if name == 'wooden_magpie': bones['gears'] = {'rotation': [0, 0, 'query.anim_time * 320']}
            elif clip == 'burrow':
                bones['root'] = {'position': {'0.0': [0, 0, 0], '0.2': [0, -7, 0], '0.9': [0, -7, 0]}, 'rotation': [14, 0, 0]}
                for i in range(6): bones['leg_' + str(i)] = {'rotation': ['math.sin(query.anim_time * 450 + ' + str(i * 60) + ') * 35', 0, 0]}
            elif clip == 'eruption':
                bones['root'] = {'position': {'0.0': [0, -7, 0], '0.1': [0, 2, 0], '0.5': [0, 0, 0]}, 'rotation': {'0.0': [-40, 0, 0], '0.2': [-16, 0, 0], '0.6': [0, 0, 0]}}
                bones['head'] = {'rotation': [-25, 0, 0]}
            elif clip in ('pinch', 'side_charge'):
                bones['root'] = {'rotation': [0, 0, 'math.sin(query.anim_time * 300) * 6']}
                for side, sign in (('left', 1), ('right', -1)):
                    bones[side + '_claw'] = {'rotation': {'0.0': [0, sign * 32, 0], '0.2': [-25, sign * 60, 0], '0.32': [-38, sign * -8, 0], '0.8': [0, 0, 0]}}
            elif clip == 'sting':
                bones['tail'] = {'rotation': {'0.0': [0, 0, 0], '0.2': [-48, 0, 0], '0.3': [-85, 0, 0], '0.8': [0, 0, 0]}}
                bones['stinger'] = {'rotation': [-35, 0, 0]}
            elif clip == 'possession':
                bones['body'] = {'scale': [0.82, 1.12, 0.82], 'rotation': [0, 'math.sin(query.anim_time * 140) * 20', 0]}
                bones['tail'] = {'rotation': [0, 0, 'math.sin(query.anim_time * 240) * 18']}
            elif clip == 'return_water':
                bones['root'] = {'rotation': [25, 0, 0]}
                bones['tail'] = {'rotation': [0, 'math.sin(query.anim_time * 550) * 28', 0]}
                bones['left_fin'] = {'rotation': [0, 0, 'math.sin(query.anim_time * 400) * 30']}
                bones['right_fin'] = {'rotation': [0, 0, 'math.sin(query.anim_time * 400) * -30']}
            bones = {k: v for k, v in bones.items() if k in available}
            doc['animations'][clip] = {'loop': True, 'animation_length': .9, 'bones': bones}
        if name == 'red_fox':
            doc['animations']['evade']['bones']['root'] = {'rotation': [0, 18, -14], 'position': {'0.0': [0, 0, 0], '0.2': [1.5, .5, 0], '0.4': [0, 0, 0]}}
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n')

if __name__ == '__main__':
    refine()
    refine_contact_actions()

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

if __name__ == '__main__':
    refine()

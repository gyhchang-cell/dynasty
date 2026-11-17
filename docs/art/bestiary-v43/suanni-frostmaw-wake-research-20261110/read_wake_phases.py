"""Source-channel observations only; does not evaluate model geometry or run Java."""
from pathlib import Path
import hashlib
import json
import math
import re

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[3]
SOURCE = ROOT / 'build/creature-reference-1000/BobMowzie__MowziesMobs-Public/src/main/java/com/bobmowzie/mowziesmobs/client/model/entity/ModelFrostmaw.java'


def read_clip(text, name):
    marker = 'if (entity.getAnimation() == EntityFrostmaw.' + name + ') {'
    start = text.index(marker)
    cursor = text.index('{', start) + 1
    depth = 1
    end = cursor
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    block = text[cursor:end - 1]
    phases, current, tick = [], None, 0
    for line in block.splitlines():
        match = re.search(r'animator\.(startKeyframe|setStaticKeyframe|resetKeyframe)\((\d+)\)', line)
        if match:
            op, duration = match[1], int(match[2])
            current = dict(kind=op, start=tick, end=tick + duration, duration=duration, target={})
            tick += duration
            phases.append(current)
        match = re.search(r'animator\.(rotate|move)\((\w+), ([^;]+)\);', line)
        if match:
            key = match[2] + ':' + match[1]
            numbers = [float(n.strip().rstrip('fF')) for n in match[3].split(',')]
            assert len(numbers) == 3
            previous = current['target'].get(key, [0., 0., 0.])
            current['target'][key] = [a + b for a, b in zip(previous, numbers)]
    return dict(name=name, line_start=text[:start].count('\n')+1, line_end=text[:end].count('\n')+1,
                total_keyframe_ticks=tick, phases=phases)


def channel_at(clip, time, key):
    previous = {}
    for phase in clip['phases']:
        target = phase['target']
        if phase['start'] <= time < phase['end']:
            before = previous.get(key, [0., 0., 0.])
            if phase['kind'] == 'setStaticKeyframe':
                return before
            after = target.get(key, [0., 0., 0.])
            weight = math.sin((time-phase['start'])/phase['duration'] * math.pi/2)
            return [a*(1-weight) + b*weight for a,b in zip(before,after)]
        if phase['kind'] != 'setStaticKeyframe':
            previous = target
    return [0., 0., 0.]


def main():
    text = SOURCE.read_text()
    names = ['ACTIVATE_ANIMATION', 'ACTIVATE_NO_CRYSTAL_ANIMATION', 'DEACTIVATE_ANIMATION']
    clips = [read_clip(text, n) for n in names]
    initial = clips[0]['phases'][0]['target']
    other_initial = clips[1]['phases'][0]['target']
    inverse = clips[2]['phases'][0]['target']
    sleep_start = text.index('else if (entity.getAnimation() != EntityFrostmaw.ACTIVATE_ANIMATION')
    sleep_end = text.index('chest.scaleChildren = false;', sleep_start)
    sleep = {}
    sleep_code = re.sub(r'//[^\n]*', '', text[sleep_start:sleep_end])
    for part, field, sign, value in re.findall(r'(\w+)\.(rotateAngle[XYZ]|rotationPoint[XYZ])\s*([+-])=\s*([-\d.]+)f?;', sleep_code):
        key = part + (':rotate' if field.startswith('rotateAngle') else ':move')
        vector = sleep.setdefault(key, [0.,0.,0.])
        vector['XYZ'.index(field[-1])] += float(value)*(1 if sign=='+' else -1)
    assert set(sleep)==set(initial)
    assert all(abs(a-b)<1e-8 for key in sleep for a,b in zip(sleep[key],initial[key]))
    cancellation = {key: [a+b for a,b in zip(initial.get(key,[0.,0.,0.]),inverse.get(key,[0.,0.,0.]))]
                    for key in initial.keys() | inverse.keys()}
    assert all(abs(v)<1e-8 for vector in cancellation.values() for v in vector)
    assert initial == other_initial
    assert [c['total_keyframe_ticks'] for c in clips] == [118,97,20]
    data = dict(source=str(SOURCE), sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                scope='All three selected keyframe branches; no geometry, render, terrain or world contact reconstruction',
                interpolation='sin(t*pi/2), additive same-channel operations; zero-duration pose primes previous target',
                clips=clips, activation_initial_targets_equal=True,
                activation_initial_equals_inactive_direct_base=True,
                inactive_direct_base=sleep,
                deactivate_initial_cancels_static_sleep_targets=True,
                cancellation_scope='Selected base sleep target only; breathing and cached terrain overlays remain outside this numeric equality',
                declared_entity_durations=[118,100,25],
                zero_relative_pose_tail_ticks=[0,3,5],
                samples=[dict(clip=c['name'],time=t,root_rotate=channel_at(c,t,'root:rotate'),
                              root_move=channel_at(c,t,'root:move'),head_rotate=channel_at(c,t,'headJoint:rotate'),
                              left_hand_rotate=channel_at(c,t,'leftHand:rotate'),
                              right_hand_rotate=channel_at(c,t,'rightHand:rotate'))
                         for c in clips for t in sorted(set([0,5,15,c['total_keyframe_ticks']-0.001,c['total_keyframe_ticks']]))],
                new_accepted_credit=0)
    (BATCH/'phase-observation.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:data[k] for k in ['activation_initial_targets_equal','deactivate_initial_cancels_static_sleep_targets','declared_entity_durations','zero_relative_pose_tail_ticks']}))
    print(json.dumps([{k:c[k] for k in ['name','line_start','line_end','total_keyframe_ticks']} | {'boundaries':[p['end'] for p in c['phases']]} for c in clips]))


if __name__ == '__main__':
    main()

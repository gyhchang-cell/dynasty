"""Fail-closed raw-evidence checks. No launch; synthetic regression fixtures are not native acceptance."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

CUE = 'equipment_confirmed_fangtian_sweep'
HOOKS = {'FangtianSweep.before', 'FangtianSweep.after', 'Cod3Vfx.before', 'Cod3Vfx.after'}
IDENTITY = ('case', 'binding', 'mode', 'capture', 'role', 'session', 'artifact', 'build')
VIEWS = {'first': 'FIRST_PERSON', 'third': 'THIRD_PERSON_BACK'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same_entity(a, b):
    return all(a.get(k) == b.get(k) and a.get(k) is not None for k in ('uuid', 'id', 'dimension'))


def valid_stamp(stamp, case, mode, binding, role):
    return (stamp.get('case') == case and stamp.get('mode') == mode and
            stamp.get('binding') == binding and stamp.get('role') == role and
            stamp.get('build') == 'sweepqa-02' and bool(stamp.get('capture')) and
            bool(stamp.get('session')) and re.fullmatch('[0-9a-f]{64}', stamp.get('artifact', '')) is not None)


def analyze(output, case, mode, view, calibration=None):
    checks, observations, hashes = {}, {}, {}
    report = dict(case=case, mode=mode, requested_view=view, checks=checks, observations=observations,
                  input_sha256=hashes, overall_acceptance=False,
                  visual_acceptance='PENDING manual crescent/old-mesh shape, occlusion and composition review')
    try:
        if not re.fullmatch('[a-zA-Z0-9_-]{1,70}', case) or view not in VIEWS or mode not in ('success', 'cancel-attack', 'cancel-damage', 'invulnerable'):
            raise ValueError('Invalid case/view')
        def load(suffix):
            path = output / (case + suffix)
            hashes[path.name] = sha(path)
            return json.loads(path.read_text())
        fixture = load('-fixture.json')
        server, client, frames = load('-server-events.json'), load('-client-events.json'), load('-client-frames.json')
        actor, targets, fi = fixture['actor'], fixture['targets'], fixture['identity']
        primary, binding = targets[0], fi['binding']
        events = lambda xs, kind: [x['data'] for x in xs if x['kind'] == kind]
        full_events = lambda xs, kind: [x for x in xs if x['kind'] == kind]
        starts, ends = full_events(client, 'client-capture-start'), full_events(client, 'client-capture-end')
        ci = starts[0] if len(starts) == 1 else {}
        checks['fixture_identity'] = (fixture['case'] == case and fixture['mode'] == mode and
            valid_stamp(fi, case, mode, binding, 'server') and len(targets) == 2 and
            len({t['uuid'] for t in targets}) == 2 and all(t['dimension'] == actor['dimension'] for t in targets))
        checks['all_server_records_bound'] = bool(server) and all(
            valid_stamp(x, case, mode, binding, 'server') and all(x.get(k) == fi.get(k) for k in IDENTITY) for x in server)
        checks['all_client_records_and_frames_bound'] = bool(client) and bool(frames) and all(
            valid_stamp(x, case, mode, binding, 'client') and all(x.get(k) == ci.get(k) for k in IDENTITY) for x in client + frames)
        checks['same_loaded_QA_artifact'] = ci.get('artifact') == fi['artifact']
        checks['exact_fixture_bytes_imported'] = len(starts) == 1 and ci['data'].get('fixtureSHA256') == hashes[case+'-fixture.json']
        checks['capture_actor_and_view'] = (len(starts) == 1 and same_entity(ci['data']['player'], actor) and
            ci['data']['observerOnly'] is False and ci['data']['view'] == view and ci['data']['cooldown'] >= .99)
        attacks, c_attacks = events(server, 'server-native-attack'), events(client, 'actual-client-gamemode-attack')
        checks['server_attack_bound_to_main_actor'] = len(attacks) == 1 and same_entity(attacks[0]['actor'], actor) and same_entity(attacks[0]['target'], primary)
        checks['client_attack_bound_to_main_actor'] = len(c_attacks) == 1 and same_entity(c_attacks[0]['player'], actor) and same_entity(c_attacks[0]['target'], primary)
        checks['expected_attack_cancel_state'] = len(attacks) == 1 and attacks[0]['cancelled'] == (mode == 'cancel-attack')
        checks['full_client_observation_window'] = (len(starts) == len(ends) == 1 and
            ends[0]['data']['reason'] == 'bounded-40-client-ticks' and ends[0]['data']['ticks'] >= 40 and
            starts[0]['nano'] < ends[0]['nano'] and all(starts[0]['nano'] <= x['nano'] <= ends[0]['nano'] for x in client))
        checks['actual_requested_camera_only'] = bool(frames) and all(f['view'] == VIEWS[view] for f in frames)
        loaded = set(events(client, 'loaded-render-hook'))
        checks['live_render_hooks_whole_capture'] = (HOOKS <= loaded and bool(frames) and
            all(HOOKS <= set(f.get('hooks', [])) for f in frames) and
            min(f['ageClientTicks'] for f in frames) <= 6 and max(f['ageClientTicks'] for f in frames) >= 40)
        checks['no_probe_errors'] = not events(server, 'probe-error') and not events(client, 'probe-error')
        before, after = full_events(server, 'receipt-before-exact-consumer'), full_events(server, 'receipt-after-exact-consumer')
        def by_cycle(xs):
            result = {}
            for x in xs:
                result.setdefault(x['data']['cycle'], []).append(x)
            return result
        bc, ac = by_cycle(before), by_cycle(after)
        cycle = attacks[0]['cycle'] if len(attacks) == 1 else -10000
        # Explicit nonempty, paired, consecutive post-attack consumer coverage; no all([]) green.
        checks['live_paired_END_coverage_20_cycles'] = bool(before) and bool(after) and all(
            len(bc.get(t, [])) == len(ac.get(t, [])) == 1 and bc[t][0]['nano'] < ac[t][0]['nano']
            for t in range(cycle + 1, cycle + 21))
        checks['queue_empty_after_observed_consumer'] = bool(after) and all(not x['data']['rows'] for x in after)
        rows = [r for x in before for r in x['data']['rows']]
        checks['all_receipts_bound_to_main_actor'] = all(same_entity(r['actor'], actor) and same_entity(r['main'], primary) for r in rows)
        finals = events(server, 'server-final-targets')
        last = finals[-1] if finals else []
        hp0 = {t['uuid']: t['health'] for t in targets}
        checks['final_targets_bound'] = len(last) == len(targets) and all(any(same_entity(t, x) for t in targets) for x in last) and {x['uuid'] for x in last} == set(hp0)
        deltas = {x['uuid']: hp0[x['uuid']] - x['health'] for x in last if x['uuid'] in hp0}
        checks['finite_health'] = len(deltas) == len(targets) and all(math.isfinite(d) for d in deltas.values())
        observations['health_loss'] = deltas
        damages = events(server, 'server-damage-event-not-final-hp')
        def bound_damage(d):
            return same_entity(d['owner'], actor) and same_entity(d['direct'], actor) and any(same_entity(d['target'], t) for t in targets) and d['source'] in ('player', 'mob')
        checks['damage_sources_bound'] = all(bound_damage(d) for d in damages)
        wire = events(client, 'actual-s2c-handle')
        cues = [x for x in wire if x['sequence'] == CUE]
        def own_packet(p):
            return p.get('entity') == actor['id'] and p.get('dimension') == actor['dimension']
        def own_ghost(g, frame_tick):
            p = g.get('packet', {})
            return g.get('item') == 'dynasty:halberd_fangtian' and same_entity(g.get('actor', {}), actor) and own_packet(p) and p.get('sequence') == 'mesh_weapon' and -2 <= frame_tick-p.get('start', float('-inf')) < p.get('duration', 0) and any(
                all(p.get(k) == w.get(k) for k in ('sequence', 'entity', 'dimension', 'start', 'seed', 'template')) for w in wire)
        if mode == 'success':
            checks['one_owner_dimension_cue'] = len(cues) == 1 and own_packet(cues[0]) and cues[0]['duration'] == 6
            checks['genuine_health_loss'] = bool(deltas) and any(d > 0 for d in deltas.values())
            checks['real_adjacent_tick_cue'] = any(
                r['age'] == 1 and r['consumedNow'] - r['produced'] == 1 and
                r['capturedLevelMatchesActor'] and r['capturedLevelMatchesMain'] and
                (r['secondary'] or r['primaryDamage'] and r['main']['health'] < r['health']) and
                any(c['start'] == r['consumedNow'] and own_packet(c) for c in cues) for r in rows)
            checks['native_mesh_weapon_wire'] = any(x['sequence'] == 'mesh_weapon' and own_packet(x) for x in wire)
            checks['crescent_geometry_observed'] = any(f['geometry'].get('FangtianSweep') for f in frames)
            checks['same_frame_owner_crescent_old_mesh'] = any(f['geometry'].get('FangtianSweep') and any(own_ghost(g, f['tick']) for g in f['afterimages']) for f in frames)
            checks['native_pixel_pair_saved'] = any(
                'nativeBefore' in d and (output/d['nativeBefore']).is_file() and (output/d['nativeAfter']).is_file()
                for f in frames for k, d in f['nativePixelDelta'].items() if k == 'FangtianSweep')
        else:
            checks['no_dedicated_cue'] = not cues
            checks['no_dedicated_geometry'] = not any(f['geometry'].get('FangtianSweep') for f in frames)
            checks['no_health_loss'] = bool(deltas) and all(d == 0 for d in deltas.values())
            if mode == 'cancel-damage':
                checks['bound_damage_actually_cancelled'] = bool(damages) and all(bound_damage(d) and d['cancelled'] for d in damages)
            if mode == 'invulnerable':
                checks['fixture_and_final_invulnerable'] = all(t.get('invulnerable') is True for t in targets + last)
            checks['same_session_positive_calibration'] = False
            if calibration and calibration != case:
                positive = analyze(output, calibration, 'success', view)
                observations['calibration'] = dict(case=calibration, mechanical_checks_pass=positive['mechanical_checks_pass'], input_sha256=positive['input_sha256'])
                pi = positive.get('identity', {})
                checks['same_session_positive_calibration'] = (positive['mechanical_checks_pass'] and
                    all(ci.get(k) == pi.get('client', {}).get(k) and fi.get(k) == pi.get('server', {}).get(k)
                        for k in ('session', 'artifact', 'build')) and
                    len(starts) == 1 and ci['nano'] > pi.get('end_nano', float('inf')) and
                    min(x['nano'] for x in server) > pi.get('server_end_nano', float('inf')))
        observations['receipt_ages'] = [r['age'] for r in rows]
        observations['sequences'] = sorted({x['sequence'] for x in wire})
        observations['camera_views'] = sorted({f['view'] for f in frames})
        report['identity'] = dict(server=fi, client={k: ci.get(k) for k in IDENTITY}, end_nano=ends[0]['nano'] if len(ends) == 1 else None, server_end_nano=max(x['nano'] for x in server))
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError) as ex:
        checks['complete_well_formed_evidence'] = False
        report['error'] = f'{type(ex).__name__}: {ex}'
    report['mechanical_checks_pass'] = bool(checks) and all(checks.values())
    report['status'] = 'MECHANICAL_PASS_VISUAL_PENDING' if report['mechanical_checks_pass'] else 'INSUFFICIENT_OR_REJECTED_EVIDENCE'
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument('output', type=Path)
    p.add_argument('case')
    p.add_argument('--mode', choices=['success', 'cancel-attack', 'cancel-damage', 'invulnerable'], required=True)
    p.add_argument('--view', choices=VIEWS, required=True)
    p.add_argument('--calibration', help='Earlier positive age1 case in same output, process sessions and QA artifact; required for negatives')
    a = p.parse_args()
    if not re.fullmatch('[a-zA-Z0-9_-]{1,70}', a.case):
        p.error('Invalid case ID')
    r = analyze(a.output, a.case, a.mode, a.view, a.calibration)
    (a.output/(a.case+'-analysis02.json')).write_text(json.dumps(r, indent=2)+'\n')
    print(json.dumps(r, indent=2))
    return 0 if r['mechanical_checks_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

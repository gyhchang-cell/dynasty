#!/usr/bin/env python3
"""Check original identities, scope continuity and immutable receipts offline."""
import ast
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash, role
from whole_building_candidates import AIR


def sha(data):
    return hashlib.sha256(data).hexdigest()


def get(path):
    return json.loads(path.read_text())


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def evidence(e, image=False):
    p = Path(e['path'])
    assert sha(p.read_bytes()) == e['sha256'], p
    if image:
        with Image.open(p) as im:
            im.verify()


def exact(value, identity):
    if isinstance(value, str):
        return value == identity
    if isinstance(value, dict):
        return any(exact(v, identity) for v in value.values())
    if isinstance(value, list):
        return any(exact(v, identity) for v in value)
    return False


def main():
    original = BASE / 'research-20261101-proposal-semantic-acceptance-010-015'
    definitions = get(original / 'scoped-reference-register.json')
    for e in definitions['preserved_registries']:
        evidence(e)
    preserved = [original] + [BASE / f'research-20261101-dungeons-{n:03d}' for n in range(16, 29)]
    for folder in preserved:
        for e in get(folder / 'RECEIPT.json')['files']:
            p = folder / e['path']
            assert p.stat().st_size == e['bytes'] and sha(p.read_bytes()) == e['sha256'], p

    src = get(OUT / 'sources.json')
    assert src['new_source_templates'] == src['automatic_credit'] == 0
    assert [c['prior_identity'] for c in src['candidates']] == ['002-F02', '002-F06', '015-F01', '013-F01']
    for a in src['source_archives']:
        assert sha(Path(a['path']).read_bytes()) == a['sha256']
    rawnbt, rawstates, cells = {}, {}, {}
    for c in src['candidates']:
        assert c['source_is_previously_studied'] and c['new_source_template_credit'] == 0
        evidence(c['original_index'])
        evidence(c['original_whole_image'], True)
        oldid = c['prior_identity'].split('-', 1)[1]
        old = next(r for r in get(Path(c['original_index']['path']))['candidates'] if r['id'] == oldid)
        assert all(c[k] == old[k] for k in ('source_archive', 'member', 'nbt_sha256', 'size'))
        with ZipFile(c['source_archive']) as z:
            raw = z.read(c['member'])
            assert sha(raw) == c['nbt_sha256']
            d = read(raw)
            assert d['size'] == c['size']
            pal = d.get('palette') or d['palettes'][0]
            states = {tuple(b['pos']): pal[b['state']] for b in d['blocks']}
            assert len(states) == len(d['blocks'])
            assert all(0 <= p[i] < d['size'][i] for p in states for i in range(3))
            cs = {p: s for p, s in states.items() if s['Name'] not in AIR}
            assert len(cs) == c['nonair']
            assert dict(Counter(s['Name'] for s in cs.values())) == c['materials']
            sockets = [dict(position=b['pos'], state=pal[b['state']], data=b.get('nbt', {}))
                       for b in d['blocks'] if pal[b['state']]['Name'] == 'minecraft:jigsaw']
            assert sockets == c['sockets']
            doors = [dict(position=list(p), state=s) for p, s in states.items()
                     if s['Name'].endswith('_door') and s.get('Properties', {}).get('half') == 'lower']
            assert doors == c['doors']
            for e in c['pool_references']:
                assert json.loads(z.read(e['member'])) == e['data']
                assert exact(e['data'], c['source_dedup_identity'])
        rawnbt[c['id']], rawstates[c['id']], cells[c['id']] = d, states, cs

    audit = get(OUT / 'raw-source-audit.json')
    dedup = get(OUT / 'dedup-evidence.json')
    assert dedup['historical_unique_local_archive_member_pairs'] == 217
    assert not dedup['within_batch_exact_duplicate_pairs'] and dedup['formal_credit_added'] == 0
    for c, a, h in zip(src['candidates'], audit['entries'], dedup['entries']):
        assert c['id'] == a['id'] == h['id']
        cs = cells[c['id']]
        assert a['occupied_bounds'] == [[min(p[i] for p in cs), max(p[i] for p in cs)] for i in range(3)]
        assert a['materials'] == c['materials']
        assert h['nbt_sha256'] == c['nbt_sha256']
        assert h['occupancy_sha256'] == geometry_hash({p: 1 for p in cs}, c['size'])
        assert h['role_sha256'] == geometry_hash({p: role(s['Name']) for p, s in cs.items()}, c['size'])
        assert len(h['historical_exact_matches']) == 1
        match = h['historical_exact_matches'][0]
        assert match['archive'] == c['source_archive'] and match['member'] == c['member']
        assert set(match['reasons']) == {'member', 'nbt_sha256', 'occupancy_sha256', 'role_sha256'}
        with ZipFile(c['source_archive']) as z:
            for e in a['archive_json_identity_mentions']:
                raw = z.read(e['member'])
                assert sha(raw) == e['sha256'] and json.loads(raw) == e['data']
                assert exact(e['data'], c['source_dedup_identity'])
            for e in a['outgoing_pools']:
                assert not e['assembled'] and e['building_credit'] == 0
                if e['status'] == 'FOUND_LOCAL':
                    raw = z.read(e['member'])
                    assert sha(raw) == e['sha256'] and json.loads(raw) == e['data']
        assert not a['native_routes_verified'] and not a['terrain_generated'] and not a['components_assembled']

    authored = get(OUT / 'authored-use-evidence.json')
    for row, c in zip(authored['entries'], src['candidates']):
        assert row['id'] == c['id'] and row['prior_identity'] == c['prior_identity']
        assert row['entities'] == [dict(position=e.get('pos'), id=e.get('nbt', {}).get('id')) for e in rawnbt[c['id']].get('entities', [])]
        with ZipFile(c['source_archive']) as z:
            raw = z.read(row['metadata']['member'])
        assert sha(raw) == row['metadata']['sha256'] and raw.decode() == row['metadata']['text']
        assert row['actor_building_credit'] == 0 and not row['native_entities_spawned']
    guard_entities = authored['entries'][0]['entities']
    assert Counter(e['id'] for e in guard_entities) == {'minecraft:pillager': 11, 'minecraft:vindicator': 4, 'minecraft:evoker': 1}
    assert Counter(math.floor(e['position'][1]) for e in guard_entities) == {2: 5, 3: 1, 12: 6, 20: 4}
    for y in (11, 19):
        assert any(p[1] == y and s['Name'].endswith('_planks') for p, s in rawstates['T01'].items())
    assert [s['position'] for s in src['candidates'][0]['sockets']] == [[10, 0, 11]]
    assert src['candidates'][0]['sockets'][0]['data']['final_state'] == 'minecraft:dirt'

    planes = get(OUT / 'room-layer-original-states.json')
    detail = get(OUT / 'detail-evidence.json')
    expected_cuts = {'T01': [3, 20, 7, 7], 'T02': [3, 12, 11, 10], 'C01': [6, 21, 9, 9], 'C02': [12, 20, 10, 10]}
    for row in planes['entries']:
        states = rawstates[row['id']]
        for plane in row['selected_horizontal_planes']:
            observed = {tuple(e['position']): e['state'] for e in plane['original_states']}
            assert len(observed) == len(plane['original_states']) == plane['stored_positions']
            assert observed == {p: s for p, s in states.items() if p[1] == plane['y']}
            assert plane['explicit_air_positions'] == sum(s['Name'] in AIR for s in observed.values())
            assert plane['nonair_positions'] == sum(s['Name'] not in AIR for s in observed.values())
    for row in detail['entries']:
        assert [c['coordinate'] for c in row['cuts']] == expected_cuts[row['id']]
        ladders = defaultdict(list)
        for p, s in cells[row['id']].items():
            if s['Name'] == 'minecraft:ladder':
                ladders[(p[0], p[2])].append(p[1])
        assert sorted(row['ladder_runs'], key=lambda r: (r['x'], r['z'])) == [dict(x=x, z=z, ys=sorted(ys)) for (x, z), ys in sorted(ladders.items())]

    review = get(OUT / 'manual-review.json')
    assert len(review['entries']) == 4 and review['new_source_templates'] == 0
    assert review['previous_source_template_rereads'] == review['actual_new_section_images_viewed'] == review['actual_unique_previous_whole_images_viewed'] == 4
    assert review['independent_references_added'] == 1 and not review['independent_human_review_claimed']
    images = set()
    for row, c in zip(review['entries'], src['candidates']):
        assert row['source'] == c and row['prior_identity'] == c['prior_identity']
        assert set(row['observations']) == {'layout', 'proportion', 'facade', 'roof', 'materials', 'circulation', 'terrain'}
        assert not row['native_acceptance'] and not row['independent_human_review']
        assert row['credit'] == (1 if row['id'] == 'T01' else 0)
        assert row['credit_identity'] == ('002-F02' if row['id'] == 'T01' else None)
        for e in row['actual_images_viewed']:
            evidence(e, True)
            images.add(e['path'])
    assert len(images) == 8
    for e in review['prior_comparison_evidence']:
        evidence(e)

    scope = get(OUT / 'scoped-reference-update.json')
    for key in ('prior_update', 'original_scope_definitions', 'previous_hold_evidence'):
        evidence(scope[key])
    prior = get(Path(scope['prior_update']['path']))
    assert scope['added_ids'] == scope['old_candidate_first_scope_acceptance'] == ['002-F02']
    assert scope['added_credit'] == 1 and scope['new_source_discoveries'] == 0 and not scope['scope_definitions_changed']
    for key in ('previous_two_holds_retained', 'other_holds_retained', 'recent_holds_retained'):
        assert scope[key] == prior[key]
    assert scope['prior_58_block_assembly_exclusion_retained'] == dict(id='028-A01', complete_size=[18, 58, 18], credit=0, scope_height_max=53)
    for s, old, original_s in zip(scope['scopes'], prior['scopes'], definitions['scopes']):
        assert s['scope_id'] == old['scope_id'] == original_s['scope_id']
        assert s['scope_definition'] == old['scope_definition'] == original_s['scope_definition']
        assert s['accepted_ids'] == old['accepted_ids'] + (['002-F02'] if s['scope_id'] == 'DUN03-SINGLE-WATCHPOST' else [])
        assert len(s['accepted_ids']) == len(set(s['accepted_ids'])) == s['accepted_references']
        assert s['target'] == 1000 and s['remaining'] == 1000 - s['accepted_references'] and not s['construction_allowed']
    assert [s['accepted_references'] for s in scope['scopes']] == [6, 10, 1]
    old_watch = next(s for s in prior['scopes'] if s['scope_id'] == 'DUN03-SINGLE-WATCHPOST')
    assert {r['prior_identity'] for r in review['semantic_comparisons']} == set(old_watch['accepted_ids'])
    assert len(review['semantic_comparisons']) == 9
    assert scope['production_tasks_completed'] == scope['production_changes'] == scope['checklist_deletions'] == 0
    boundary = get(OUT / 'discovery-boundary.json')
    for e in boundary['indices_checked']:
        evidence(e)
    assert boundary['local_only'] and not boundary['java_run'] and not boundary['game_run'] and boundary['network_requests'] == 0
    assert boundary['production_changes'] == boundary['checklist_deletions'] == boundary['sound_brightness_window_save_changes'] == 0
    for p in OUT.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))

    report = dict(
        status='PASS_OLD_COMPLETE_CANDIDATE_FIRST_SCOPE_ACCEPTANCE', batch=29,
        previous_source_templates_reread=4, new_source_templates=0,
        actual_new_section_images_viewed=4, actual_previous_whole_images_reopened=4,
        historical_unique_local_archive_member_pairs=217, exact_matches_are_prior_self_identities=True,
        new_valid_scoped_references=1, accepted_ids=['002-F02'], scoped_counts=[6, 10, 1], remaining=[994, 990, 999],
        original_source_states_entities_and_pool_values_verified=True,
        prior_receipt_packages_unchanged=len(preserved), other_scope_registries_unchanged=True,
        all_old_holds_retained=True, authored_58_block_tower_exclusion_retained=True,
        construction_allowed=False, independent_human_review_claimed=False,
        native_collision_terrain_or_gameplay_acceptance=False,
        network_requests=0, java_run=False, game_run=False,
        production_changes=0, checklist_deletions=0, sound_brightness_window_save_changes=0)
    dump('verification.json', report)
    files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'RECEIPT.json')
    dump('RECEIPT.json', dict(status=report['status'], files=[dict(path=str(p.relative_to(OUT)), bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT / 'RECEIPT.json')['files']:
        p = OUT / e['path']
        assert p.stat().st_size == e['bytes'] and sha(p.read_bytes()) == e['sha256']
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()

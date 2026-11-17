#!/usr/bin/env python3
"""Offline source, upper-ring and zero-credit hold verification."""
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile
from PIL import Image

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
sys.path.insert(0, str(OUT.parents[2] / 'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash, role
from whole_building_candidates import AIR


def sha(b):
    return hashlib.sha256(b).hexdigest()


def get(p):
    return json.loads(p.read_text())


def dump(n, v):
    (OUT / n).write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')


def evidence(e, image=False):
    p = Path(e['path'])
    assert sha(p.read_bytes()) == e['sha256'], p
    if image:
        with Image.open(p) as im:
            im.verify()


def main():
    original = BASE / 'research-20261101-proposal-semantic-acceptance-010-015'
    definitions = get(original / 'scoped-reference-register.json')
    for e in definitions['preserved_registries']:
        evidence(e)
    preserved = [original] + [BASE / f'research-20261101-dungeons-{n:03d}' for n in range(16, 32)]
    for folder in preserved:
        for e in get(folder / 'RECEIPT.json')['files']:
            p = folder / e['path']
            assert p.stat().st_size == e['bytes'] and sha(p.read_bytes()) == e['sha256'], p
    src = get(OUT / 'sources.json')
    assert src['new_source_templates'] == src['automatic_credit'] == 0
    assert [c['prior_identity'] for c in src['candidates']] == ['001-F11', '003-F11', '015-F01']
    for a in src['source_archives']:
        assert sha(Path(a['path']).read_bytes()) == a['sha256']
    states, occupied = {}, {}
    for c, a, h in zip(src['candidates'], get(OUT / 'raw-source-audit.json')['entries'], get(OUT / 'dedup-evidence.json')['entries']):
        evidence(c['original_index'])
        evidence(c['original_whole_image'], True)
        old = next(r for r in get(Path(c['original_index']['path']))['candidates'] if r['id'] == c['prior_identity'].split('-')[1])
        assert all(c[k] == old[k] for k in ('member', 'source_archive', 'size', 'nbt_sha256'))
        assert c['source_is_previously_studied'] and c['new_source_template_credit'] == 0
        assert c['id'] == a['id'] == h['id']
        with ZipFile(c['source_archive']) as z:
            raw = z.read(c['member'])
            assert sha(raw) == c['nbt_sha256']
            d = read(raw)
            assert d['size'] == c['size']
            pal = d.get('palette') or d['palettes'][0]
            s = {tuple(b['pos']): pal[b['state']] for b in d['blocks']}
            assert len(s) == len(d['blocks'])
            assert all(0 <= p[i] < d['size'][i] for p in s for i in range(3))
            cs = {p: v for p, v in s.items() if v['Name'] not in AIR}
            assert len(cs) == c['nonair'] and Counter(v['Name'] for v in cs.values()) == c['materials']
            assert c['sockets'] == [dict(position=b['pos'], state=pal[b['state']], data=b.get('nbt', {})) for b in d['blocks'] if pal[b['state']]['Name'] == 'minecraft:jigsaw']
            assert c['doors'] == [dict(position=list(p), state=v) for p, v in s.items() if v['Name'].endswith('_door') and v.get('Properties', {}).get('half') == 'lower']
            for e in c['pool_references']:
                assert json.loads(z.read(e['member'])) == e['data']
            for e in a['archive_json_identity_mentions']:
                raw = z.read(e['member'])
                assert sha(raw) == e['sha256'] and json.loads(raw) == e['data']
            for e in a['outgoing_pools']:
                assert not e['assembled'] and e['building_credit'] == 0
                if e['status'] == 'FOUND_LOCAL':
                    raw = z.read(e['member'])
                    assert sha(raw) == e['sha256'] and json.loads(raw) == e['data']
        assert a['occupied_bounds'] == [[min(p[i] for p in cs), max(p[i] for p in cs)] for i in range(3)]
        assert h['occupancy_sha256'] == geometry_hash({p: 1 for p in cs}, c['size'])
        assert h['role_sha256'] == geometry_hash({p: role(v['Name']) for p, v in cs.items()}, c['size'])
        assert len(h['historical_exact_matches']) == 1
        m = h['historical_exact_matches'][0]
        assert m['archive'] == c['source_archive'] and m['member'] == c['member']
        states[c['id']], occupied[c['id']] = s, cs
    de = get(OUT / 'dedup-evidence.json')
    assert de['historical_unique_local_archive_member_pairs'] == 217 and not de['within_batch_exact_duplicate_pairs']
    cuts = {'T01': [5, 20, 8, 8], 'T02': [4, 23, 7, 11], 'C01': [6, 21, 9, 9]}
    detail = get(OUT / 'detail-evidence.json')
    for row in detail['entries']:
        assert [r['coordinate'] for r in row['cuts']] == cuts[row['id']]
        ladders = defaultdict(list)
        for p, v in occupied[row['id']].items():
            if v['Name'] == 'minecraft:ladder':
                ladders[(p[0], p[2])].append(p[1])
        assert sorted(row['ladder_runs'], key=lambda r: (r['x'], r['z'])) == [dict(x=x, z=z, ys=sorted(ys)) for (x, z), ys in sorted(ladders.items())]
    assert detail['entries'][0]['ladder_runs'] == [dict(x=8, z=8, ys=list(range(1, 7)) + list(range(8, 22)))]
    assert detail['entries'][1]['ladder_runs'] == [dict(x=7, z=11, ys=[2,4,5,6,9,12,13,14,16,17,18,19,20,22,23,24,25])]
    for row in get(OUT / 'room-layer-original-states.json')['entries']:
        for plane in row['selected_horizontal_planes']:
            observed = {tuple(r['position']): r['state'] for r in plane['original_states']}
            assert len(observed) == len(plane['original_states']) == plane['stored_positions']
            assert observed == {p: v for p, v in states[row['id']].items() if p[1] == plane['y']}
            assert plane['explicit_air_positions'] == sum(v['Name'] in AIR for v in observed.values())
    upper = get(OUT / 'upper-original-states.json')
    assert upper['prior_identity'] == '001-F11' and upper['building_credit'] == 0
    assert [p['y'] for p in upper['planes']] == [18, 19]
    for row in upper['planes']:
        assert {tuple(r['position']): r['state'] for r in row['original_states']} == {p: v for p, v in states['T01'].items() if p[1] == row['y']}
    assert occupied['T01'][(6,19,7)]['Name'] == 'minecraft:spruce_slab'
    assert occupied['T01'][(6,19,6)]['Name'] == 'minecraft:lantern'
    socket = next(s for s in src['candidates'][0]['sockets'] if s['position'] == [7,19,7])
    assert socket['data']['pool'] == 'trek:mobs/hostile/stray' and socket['data']['final_state'] == 'minecraft:spruce_planks'
    for c, expected in zip(src['candidates'][:2], (5,11)):
        assert len(c['sockets']) == expected
    review = get(OUT / 'manual-review.json')
    assert review['independent_references_added'] == review['new_source_templates'] == 0
    assert review['previous_source_template_rereads'] == review['actual_unique_previous_whole_images_viewed'] == 3
    assert review['actual_new_section_images_viewed'] == 4 and not review['independent_human_review_claimed']
    images = set()
    for row, c in zip(review['entries'], src['candidates']):
        assert row['source'] == c and row['credit'] == 0 and row['credit_identity'] is None
        assert not row['native_acceptance'] and not row['independent_human_review']
        assert set(row['observations']) == {'layout','proportion','facade','roof','materials','circulation','terrain'}
        for e in row['actual_images_viewed']:
            evidence(e, True)
            images.add(e['path'])
    assert len(images) == 7
    for e in review['prior_comparison_evidence']:
        evidence(e)
    scope = get(OUT / 'scoped-reference-update.json')
    for k in ('prior_update','original_scope_definitions','previous_hold_evidence'):
        evidence(scope[k])
    prior = get(Path(scope['prior_update']['path']))
    assert scope['scopes'] == prior['scopes'] and not scope['added_ids'] and scope['added_credit'] == 0
    assert [s['accepted_references'] for s in scope['scopes']] == [8,10,1]
    for k in ('previous_two_holds_retained','other_holds_retained','recent_holds_retained','prior_58_block_assembly_exclusion_retained','prior_other_exclusions_retained'):
        assert scope[k] == prior[k]
    assert scope['prior_additional_holds_retained'] == prior['current_batch_holds']
    assert [s['id'] for s in scope['current_batch_holds']] == ['001-F11','003-F11']
    boundary = get(OUT / 'discovery-boundary.json')
    for e in boundary['indices_checked']:
        evidence(e)
    assert boundary['local_only'] and not boundary['java_run'] and not boundary['game_run'] and boundary['network_requests'] == 0
    assert boundary['production_changes'] == boundary['checklist_deletions'] == boundary['sound_brightness_window_save_changes'] == 0
    for p in OUT.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    report = dict(status='PASS_ICE_TOWER_FAMILY_AND_ICE_FORT_ROUTE_HOLDS', batch=32,
      old_source_templates_reread=3, actual_images_viewed=7, new_source_templates=0,
      new_valid_scoped_references=0, scoped_counts=[8,10,1], remaining=[992,990,999],
      upper_ring_original_states_and_actor_socket_checked=True, no_reconstruction_or_actor_assembly=True,
      prior_receipt_packages_unchanged=len(preserved), all_old_holds_and_58_block_exclusion_retained=True,
      construction_allowed=False, independent_human_review_claimed=False,
      native_collision_terrain_or_gameplay_acceptance=False,
      java_run=False, game_run=False, network_requests=0, production_changes=0,
      checklist_deletions=0, sound_brightness_window_save_changes=0)
    dump('verification.json', report)
    files = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'RECEIPT.json')
    dump('RECEIPT.json', dict(status=report['status'], files=[dict(path=str(p.relative_to(OUT)), bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in files]))
    for e in get(OUT / 'RECEIPT.json')['files']:
        p = OUT / e['path']
        assert p.stat().st_size == e['bytes'] and sha(p.read_bytes()) == e['sha256']
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()

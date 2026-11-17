#!/usr/bin/env python3
"""Verify a zero-credit hold, not manufacture a reference completion."""
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


def dump(name, v):
    (OUT / name).write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')


def evidence(e, image=False):
    p = Path(e['path'])
    assert sha(p.read_bytes()) == e['sha256'], p
    if image:
        with Image.open(p) as im:
            im.verify()


def main():
    initial = BASE / 'research-20261101-proposal-semantic-acceptance-010-015'
    definitions = get(initial / 'scoped-reference-register.json')
    for e in definitions['preserved_registries']:
        evidence(e)
    preserved = [initial] + [BASE / f'research-20261101-dungeons-{n:03d}' for n in range(16, 31)]
    for folder in preserved:
        for e in get(folder / 'RECEIPT.json')['files']:
            p = folder / e['path']
            assert p.stat().st_size == e['bytes'] and sha(p.read_bytes()) == e['sha256'], p
    src = get(OUT / 'sources.json')
    assert src['new_source_templates'] == src['automatic_credit'] == 0
    assert [c['prior_identity'] for c in src['candidates']] == ['001-F05', '016-F01', '011-F04', '002-F02']
    for a in src['source_archives']:
        assert sha(Path(a['path']).read_bytes()) == a['sha256']
    states, occupied, nbts = {}, {}, {}
    for c in src['candidates']:
        evidence(c['original_index'])
        evidence(c['original_whole_image'], True)
        old = next(r for r in get(Path(c['original_index']['path']))['candidates'] if r['id'] == c['prior_identity'].split('-')[1])
        assert all(c[k] == old[k] for k in ('member', 'source_archive', 'nbt_sha256', 'size'))
        assert c['source_is_previously_studied'] and c['new_source_template_credit'] == 0
        with ZipFile(c['source_archive']) as z:
            raw = z.read(c['member'])
            assert sha(raw) == c['nbt_sha256']
            d = read(raw)
            assert d['size'] == c['size']
            pal = d.get('palette') or d['palettes'][0]
            s = {tuple(b['pos']): pal[b['state']] for b in d['blocks']}
            assert len(s) == len(d['blocks'])
            assert all(0 <= p[i] < d['size'][i] for p in s for i in range(3))
            cells = {p: v for p, v in s.items() if v['Name'] not in AIR}
            assert len(cells) == c['nonair'] and Counter(v['Name'] for v in cells.values()) == c['materials']
            assert c['sockets'] == [dict(position=b['pos'], state=pal[b['state']], data=b.get('nbt', {})) for b in d['blocks'] if pal[b['state']]['Name'] == 'minecraft:jigsaw']
            assert c['doors'] == [dict(position=list(p), state=v) for p, v in s.items() if v['Name'].endswith('_door') and v.get('Properties', {}).get('half') == 'lower']
            for e in c['pool_references']:
                assert json.loads(z.read(e['member'])) == e['data']
        states[c['id']], occupied[c['id']], nbts[c['id']] = s, cells, d
    for c, a, h in zip(src['candidates'], get(OUT / 'raw-source-audit.json')['entries'], get(OUT / 'dedup-evidence.json')['entries']):
        cs = occupied[c['id']]
        assert c['id'] == a['id'] == h['id']
        assert a['occupied_bounds'] == [[min(p[i] for p in cs), max(p[i] for p in cs)] for i in range(3)]
        assert h['occupancy_sha256'] == geometry_hash({p: 1 for p in cs}, c['size'])
        assert h['role_sha256'] == geometry_hash({p: role(v['Name']) for p, v in cs.items()}, c['size'])
        assert len(h['historical_exact_matches']) == 1
        m = h['historical_exact_matches'][0]
        assert m['archive'] == c['source_archive'] and m['member'] == c['member']
        with ZipFile(c['source_archive']) as z:
            for e in a['archive_json_identity_mentions']:
                raw = z.read(e['member'])
                assert sha(raw) == e['sha256'] and json.loads(raw) == e['data']
            for e in a['outgoing_pools']:
                assert not e['assembled'] and e['building_credit'] == 0
                if e['status'] == 'FOUND_LOCAL':
                    raw = z.read(e['member'])
                    assert sha(raw) == e['sha256'] and json.loads(raw) == e['data']
    de = get(OUT / 'dedup-evidence.json')
    assert de['historical_unique_local_archive_member_pairs'] == 217 and not de['within_batch_exact_duplicate_pairs']
    cuts = {'T01': [5, 15, 9, 9], 'T02': [5, 16, 7, 7], 'T03': [6, 20, 7, 7], 'C01': [12, 20, 7, 7]}
    details = get(OUT / 'detail-evidence.json')
    for row in details['entries']:
        assert [r['coordinate'] for r in row['cuts']] == cuts[row['id']]
        ladders = defaultdict(list)
        for p, v in occupied[row['id']].items():
            if v['Name'] == 'minecraft:ladder':
                ladders[(p[0], p[2])].append(p[1])
        assert sorted(row['ladder_runs'], key=lambda r: (r['x'], r['z'])) == [dict(x=x, z=z, ys=sorted(ys)) for (x, z), ys in sorted(ladders.items())]
    assert len(details['entries'][0]['ladder_runs']) == 4
    assert all(r['ys'] == list(range(15, 20)) for r in details['entries'][0]['ladder_runs'])
    for row in get(OUT / 'room-layer-original-states.json')['entries']:
        for plane in row['selected_horizontal_planes']:
            observed = {tuple(r['position']): r['state'] for r in plane['original_states']}
            assert len(observed) == len(plane['original_states']) == plane['stored_positions']
            assert observed == {p: v for p, v in states[row['id']].items() if p[1] == plane['y']}
            assert plane['explicit_air_positions'] == sum(v['Name'] in AIR for v in observed.values())
    assert nbts['T01']['size'] == [19, 25, 19] and max(p[1] for p in occupied['T01']) == 22
    assert not any(p[1] in (23, 24) for p in occupied['T01'])
    authored = get(OUT / 'authored-use-evidence.json')
    assert authored['entities'] == [dict(position=e.get('pos'), id=e.get('nbt', {}).get('id')) for e in nbts['T01'].get('entities', [])]
    assert {'minecraft:pillager', 'minecraft:vindicator', 'minecraft:illusioner'} <= {e['id'] for e in authored['entities']}
    review = get(OUT / 'manual-review.json')
    assert review['independent_references_added'] == review['new_source_templates'] == 0
    assert review['previous_source_template_rereads'] == review['actual_new_section_images_viewed'] == review['actual_unique_previous_whole_images_viewed'] == 4
    images = set()
    for row, c in zip(review['entries'], src['candidates']):
        assert row['source'] == c and row['credit'] == 0 and row['credit_identity'] is None
        assert not row['native_acceptance'] and not row['independent_human_review']
        assert set(row['observations']) == {'layout', 'proportion', 'facade', 'roof', 'materials', 'circulation', 'terrain'}
        for e in row['actual_images_viewed']:
            evidence(e, True)
            images.add(e['path'])
    assert len(images) == 8
    for e in review['prior_comparison_evidence']:
        evidence(e)
    height = review['height_consistency_issue']
    assert height['stored_height'] == 25 and height['occupied_height'] == 23 and height['top_stored_empty_layers'] == [23, 24]
    prior_mud = get(BASE / 'research-20261101-dungeons-029/raw-source-audit.json')['entries'][2]
    assert prior_mud['size'] == [15, 25, 15] and prior_mud['occupied_bounds'][1] == [0, 22]
    scope = get(OUT / 'scoped-reference-update.json')
    for k in ('prior_update', 'original_scope_definitions', 'previous_hold_evidence'):
        evidence(scope[k])
    prior = get(Path(scope['prior_update']['path']))
    assert scope['scopes'] == prior['scopes'] and not scope['added_ids'] and scope['added_credit'] == 0
    assert [s['accepted_references'] for s in scope['scopes']] == [8, 10, 1]
    for k in ('previous_two_holds_retained', 'other_holds_retained', 'recent_holds_retained', 'prior_58_block_assembly_exclusion_retained', 'prior_other_exclusions_retained'):
        assert scope[k] == prior[k]
    assert scope['current_batch_holds'][0]['id'] == '001-F05' and scope['current_batch_holds'][0]['credit'] == 0
    boundary = get(OUT / 'discovery-boundary.json')
    for e in boundary['indices_checked']:
        evidence(e)
    assert boundary['local_only'] and not boundary['java_run'] and not boundary['game_run'] and boundary['network_requests'] == 0
    assert boundary['production_changes'] == boundary['checklist_deletions'] == boundary['sound_brightness_window_save_changes'] == 0
    for p in OUT.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    report = dict(status='PASS_ZERO_CREDIT_HEIGHT_BASIS_AND_FAMILY_HOLDS', batch=31,
      old_source_templates_reread=4, actual_images_viewed=8, new_source_templates=0,
      new_valid_scoped_references=0, scoped_counts=[8, 10, 1], remaining=[992, 990, 999],
      original_bytes_states_actor_evidence_and_height_checked=True,
      stored25_occupied23_height_issue_explicit=True, prior_receipt_packages_unchanged=len(preserved),
      existing_counts_not_silently_revised=True, all_old_holds_and_58_block_exclusion_retained=True,
      construction_allowed=False, native_collision_terrain_or_gameplay_acceptance=False,
      independent_human_review_claimed=False, java_run=False, game_run=False, network_requests=0,
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

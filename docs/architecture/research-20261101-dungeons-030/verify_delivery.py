#!/usr/bin/env python3
"""Offline integrity and scope audit; never launches Java or the game."""
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
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash, role
from whole_building_candidates import AIR


def sha(b):
    return hashlib.sha256(b).hexdigest()


def get(p):
    return json.loads(p.read_text())


def dump(name, d):
    (OUT / name).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')


def evidence(e, image=False):
    p = Path(e['path'])
    assert sha(p.read_bytes()) == e['sha256'], p
    if image:
        with Image.open(p) as im:
            im.verify()


def exact(v, k):
    if isinstance(v, str):
        return v == k
    if isinstance(v, dict):
        return any(exact(x, k) for x in v.values())
    if isinstance(v, list):
        return any(exact(x, k) for x in v)
    return False


def main():
    original = BASE / 'research-20261101-proposal-semantic-acceptance-010-015'
    definitions = get(original / 'scoped-reference-register.json')
    for e in definitions['preserved_registries']:
        evidence(e)
    preserved = [original] + [BASE / f'research-20261101-dungeons-{n:03d}' for n in range(16, 30)]
    for folder in preserved:
        for e in get(folder / 'RECEIPT.json')['files']:
            p = folder / e['path']
            assert p.stat().st_size == e['bytes'] and sha(p.read_bytes()) == e['sha256'], p
    src = get(OUT / 'sources.json')
    assert src['new_source_templates'] == src['automatic_credit'] == 0
    assert [c['prior_identity'] for c in src['candidates']] == ['009-F01', '009-F04', '010-F01', '019-F01']
    for a in src['source_archives']:
        assert sha(Path(a['path']).read_bytes()) == a['sha256']
    rawstates, cells = {}, {}
    for c in src['candidates']:
        evidence(c['original_index'])
        evidence(c['original_whole_image'], True)
        old = next(r for r in get(Path(c['original_index']['path']))['candidates'] if r['id'] == c['prior_identity'].split('-')[1])
        assert all(c[k] == old[k] for k in ('source_archive', 'member', 'size', 'nbt_sha256'))
        assert c['source_is_previously_studied'] and c['new_source_template_credit'] == 0
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
            assert len(cs) == c['nonair'] and dict(Counter(s['Name'] for s in cs.values())) == c['materials']
            assert c['sockets'] == [dict(position=b['pos'], state=pal[b['state']], data=b.get('nbt', {})) for b in d['blocks'] if pal[b['state']]['Name'] == 'minecraft:jigsaw']
            assert c['doors'] == [dict(position=list(p), state=s) for p, s in states.items() if s['Name'].endswith('_door') and s.get('Properties', {}).get('half') == 'lower']
            for e in c['pool_references']:
                assert json.loads(z.read(e['member'])) == e['data'] and exact(e['data'], c['source_dedup_identity'])
        rawstates[c['id']], cells[c['id']] = states, cs
    audit = get(OUT / 'raw-source-audit.json')
    dedup = get(OUT / 'dedup-evidence.json')
    assert dedup['historical_unique_local_archive_member_pairs'] == 217 and not dedup['within_batch_exact_duplicate_pairs']
    for c, a, h in zip(src['candidates'], audit['entries'], dedup['entries']):
        assert c['id'] == a['id'] == h['id']
        cs = cells[c['id']]
        assert a['occupied_bounds'] == [[min(p[i] for p in cs), max(p[i] for p in cs)] for i in range(3)]
        assert a['materials'] == c['materials']
        assert h['nbt_sha256'] == c['nbt_sha256']
        assert h['occupancy_sha256'] == geometry_hash({p: 1 for p in cs}, c['size'])
        assert h['role_sha256'] == geometry_hash({p: role(s['Name']) for p, s in cs.items()}, c['size'])
        assert len(h['historical_exact_matches']) == 1
        m = h['historical_exact_matches'][0]
        assert m['archive'] == c['source_archive'] and m['member'] == c['member']
        assert set(m['reasons']) == {'member', 'nbt_sha256', 'occupancy_sha256', 'role_sha256'}
        with ZipFile(c['source_archive']) as z:
            for e in a['archive_json_identity_mentions']:
                raw = z.read(e['member'])
                assert sha(raw) == e['sha256'] and json.loads(raw) == e['data'] and exact(e['data'], c['source_dedup_identity'])
            for e in a['outgoing_pools']:
                assert not e['assembled'] and e['building_credit'] == 0
                if e['status'] == 'FOUND_LOCAL':
                    raw = z.read(e['member'])
                    assert sha(raw) == e['sha256'] and json.loads(raw) == e['data']
        assert not a['native_routes_verified'] and not a['terrain_generated'] and not a['components_assembled']
    for c, a, count in zip(src['candidates'][:2], audit['entries'][:2], (14, 8)):
        assert len(c['sockets']) == count
        assert all(s['data']['pool'] in ('kaisyn:outpost/pillagers/grunt', 'kaisyn:outpost/pillagers/outpost_captain') for s in c['sockets'])
        author = [e['data'] for e in a['archive_json_identity_mentions'] if '/structure/' in e['member']]
        assert len(author) == 1 and author[0]['start_pool'] == c['source_dedup_identity']
        assert author[0]['project_start_to_heightmap'] == 'WORLD_SURFACE_WG'
        assert author[0]['spawn_overrides']['monster']['spawns'][0]['type'] == 'minecraft:pillager'
    detail = get(OUT / 'detail-evidence.json')
    cuts = {'T01': [2, 6, 10, 11], 'T02': [2, 5, 24, 14], 'C01': [2, 8, 3, 3], 'C02': [1, 12, 28, 15]}
    for row in detail['entries']:
        assert [c['coordinate'] for c in row['cuts']] == cuts[row['id']]
        ladders = defaultdict(list)
        for p, s in cells[row['id']].items():
            if s['Name'] == 'minecraft:ladder':
                ladders[(p[0], p[2])].append(p[1])
        assert sorted(row['ladder_runs'], key=lambda r: (r['x'], r['z'])) == [dict(x=x, z=z, ys=sorted(ys)) for (x, z), ys in sorted(ladders.items())]
    for row in get(OUT / 'room-layer-original-states.json')['entries']:
        for p in row['selected_horizontal_planes']:
            states = {tuple(e['position']): e['state'] for e in p['original_states']}
            assert len(states) == len(p['original_states']) == p['stored_positions']
            assert states == {k: v for k, v in rawstates[row['id']].items() if k[1] == p['y']}
            assert p['explicit_air_positions'] == sum(s['Name'] in AIR for s in states.values())
            assert p['nonair_positions'] == sum(s['Name'] not in AIR for s in states.values())
    review = get(OUT / 'manual-review.json')
    assert review['independent_references_added'] == 2 and review['new_source_templates'] == 0
    assert review['previous_source_template_rereads'] == review['actual_new_section_images_viewed'] == review['actual_unique_previous_whole_images_viewed'] == 4
    images = set()
    for row, c in zip(review['entries'], src['candidates']):
        assert row['source'] == c and row['prior_identity'] == c['prior_identity']
        assert row['credit'] == (1 if row['id'] in ('T01', 'T02') else 0)
        assert row['credit_identity'] == (c['prior_identity'] if row['credit'] else None)
        assert set(row['observations']) == {'layout', 'proportion', 'facade', 'roof', 'materials', 'circulation', 'terrain'}
        assert not row['native_acceptance'] and not row['independent_human_review']
        for e in row['actual_images_viewed']:
            evidence(e, True)
            images.add(e['path'])
    assert len(images) == 8 and not review['independent_human_review_claimed']
    for e in review['prior_comparison_evidence']:
        evidence(e)
    scope = get(OUT / 'scoped-reference-update.json')
    for k in ('prior_update', 'original_scope_definitions', 'previous_hold_evidence'):
        evidence(scope[k])
    prior = get(Path(scope['prior_update']['path']))
    assert scope['added_ids'] == scope['old_candidate_first_scope_acceptance'] == ['009-F01', '009-F04']
    assert scope['added_credit'] == 2 and scope['new_source_discoveries'] == 0 and not scope['scope_definitions_changed']
    for k in ('previous_two_holds_retained', 'other_holds_retained', 'recent_holds_retained', 'prior_58_block_assembly_exclusion_retained'):
        assert scope[k] == prior[k]
    assert scope['prior_other_exclusions_retained'] == prior['current_exclusions']
    for s, old, initial in zip(scope['scopes'], prior['scopes'], definitions['scopes']):
        assert s['scope_id'] == old['scope_id'] == initial['scope_id']
        assert s['scope_definition'] == old['scope_definition'] == initial['scope_definition']
        assert s['accepted_ids'] == old['accepted_ids'] + (scope['added_ids'] if s['scope_id'] == 'DUN03-MEDIUM-GROUND-GARRISON' else [])
        assert len(s['accepted_ids']) == len(set(s['accepted_ids'])) == s['accepted_references']
        assert s['target'] == 1000 and s['remaining'] == 1000 - s['accepted_references'] and not s['construction_allowed']
    assert [s['accepted_references'] for s in scope['scopes']] == [8, 10, 1]
    old_garrison = next(s for s in prior['scopes'] if s['scope_id'] == 'DUN03-MEDIUM-GROUND-GARRISON')
    assert {r['prior_identity'] for r in review['semantic_comparisons']} == set(old_garrison['accepted_ids'])
    boundary = get(OUT / 'discovery-boundary.json')
    for e in boundary['indices_checked']:
        evidence(e)
    assert boundary['local_only'] and not boundary['java_run'] and not boundary['game_run'] and boundary['network_requests'] == 0
    assert boundary['production_changes'] == boundary['checklist_deletions'] == boundary['sound_brightness_window_save_changes'] == 0
    for p in OUT.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    report = dict(status='PASS_TWO_OLD_WHOLE_GARRISON_CANDIDATES_FIRST_SCOPE_ACCEPTANCE', batch=30,
      source_templates_reread=4, new_source_templates=0, actual_images_viewed=8,
      new_valid_scoped_references=2, accepted_ids=scope['added_ids'], scoped_counts=[8, 10, 1], remaining=[992, 990, 999],
      historical_pairs_checked=217, exact_matches_are_old_self_identities=True,
      prior_receipt_packages_unchanged=len(preserved), other_registries_unchanged=True,
      old_holds_and_58_block_exclusion_retained=True, construction_allowed=False,
      independent_human_review_claimed=False, native_collision_terrain_or_gameplay_acceptance=False,
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

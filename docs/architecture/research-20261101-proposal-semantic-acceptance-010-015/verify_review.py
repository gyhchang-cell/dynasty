#!/usr/bin/env python3
"""Verify source bytes, states, interfaces, immutable inputs and scoped accounting offline."""
import ast
from collections import Counter, defaultdict
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile
from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = OUT.parent
sys.path.insert(0, str(ROOT / 'tools/architecture'))
from nbt_read import read
from reference_components import geometry_hash, role
from whole_building_candidates import AIR
from record_review import UNCHANGED

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def digest(b):
    return hashlib.sha256(b).hexdigest()

def load(p):
    return json.loads(p.read_text())

def ev(p):
    return dict(path=str(p), sha256=sha(p))

def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def canonical(rows):
    return sorted(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in rows)

def check_evidence(e, image=False):
    p = Path(e['path'])
    assert sha(p) == e['sha256'], p
    if image:
        with Image.open(p) as im:
            im.verify()

def main():
    sources = load(OUT / 'sources.json')
    ledger = load(OUT / 'scoped-reference-register.json')
    semantic = load(OUT / 'semantic-review.json')
    dedup = load(OUT / 'dedup-evidence.json')
    assert len(sources['inputs']) == 35
    for e in sources['inputs']:
        check_evidence(e)
    check_evidence(ledger['semantic_review'])
    check_evidence(ledger['dedup_evidence'])
    check_evidence(semantic['task_anchor'])
    for p, expected in UNCHANGED.items():
        assert sha(BASE / p) == expected
    assert len(semantic['entries']) == len(sources['candidates']) == 13
    assert len(ledger['accepted']) == 11 and len(ledger['held']) == 2
    assert {e['id'] for e in ledger['held']} == {'011-F04', '012-F03'}
    assert {e['id'] for e in semantic['entries']} == {e['id'] for e in sources['candidates']}
    assert len({(e['source']['source_archive'], e['source']['member']) for e in semantic['entries']}) == 13
    assert sum(e['credit'] for e in semantic['entries']) == 11
    by_id = {e['id']:e for e in semantic['entries']}
    assigned = []
    for scope in ledger['scopes']:
        ids = scope['accepted_ids']
        assert scope['target'] == 1000
        assert scope['accepted_references'] == len(ids)
        assert scope['remaining'] == 1000 - len(ids)
        assert scope['construction_allowed'] is False
        for i in ids:
            assert by_id[i]['credit'] == 1 and by_id[i]['scope_id'] == scope['scope_id']
        assigned.extend(ids)
    assert len(assigned) == len(set(assigned)) == 11
    assert sorted(s['accepted_references'] for s in ledger['scopes']) == [1, 4, 6]
    assert dedup['historical_unique_local_archive_member_pairs'] == 188
    assert dedup['prior_self_identities'] == 13 and dedup['other_historical_pairs_per_proposal'] == 187
    assert dedup['history_excluding_all_thirteen_reviewed_identities'] == 175
    assert not dedup['within_batch_exact_duplicate_pairs']
    assert len({e['occupancy_sha256'] for e in dedup['entries']}) == 13
    dedup_by_id = {e['id']:e for e in dedup['entries']}
    archives = {}
    state_rows = []
    image_paths = set()
    pool_checks = 0
    missing_pools = []
    component_pairs = set()
    for c in sources['candidates']:
        archive = Path(c['source_archive'])
        if archive not in archives:
            assert sha(archive) == c['source_archive_sha256']
            archives[archive] = c['source_archive_sha256']
        folder = BASE / f"research-20261101-dungeons-{c['original_batch']:03d}"
        original = next(e for e in load(folder / 'sources.json')['candidates'] if e['id'] == c['original_id'])
        original_states = next(e for e in load(folder / 'vertical-original-states.json')['entries'] if e['id'] == c['original_id'])
        original_detail = next(e for e in load(folder / 'detail-evidence.json')['entries'] if e['id'] == c['original_id'])
        original_interface = next(e for e in load(folder / 'interface-audit.json')['entries'] if e['id'] == c['original_id'])
        with ZipFile(archive) as z:
            raw = z.read(c['member'])
            assert digest(raw) == c['nbt_sha256'] == original['nbt_sha256']
            nbt = read(raw)
            palette = nbt.get('palette') or nbt['palettes'][0]
            assert nbt['size'] == c['size']
            cells = {tuple(b['pos']):palette[b['state']]['Name'] for b in nbt['blocks'] if palette[b['state']]['Name'] not in AIR}
            assert dict(Counter(cells.values())) == original['materials']
            assert len(cells) == original['nonair']
            bounds = [[min(p[a] for p in cells), max(p[a] for p in cells)] for a in range(3)]
            assert bounds == original_detail['occupied_bounds']
            states = []
            ladders = defaultdict(list)
            doors = []
            sockets = []
            for block in nbt['blocks']:
                state = palette[block['state']]
                name = state['Name']
                row = dict(position=block['pos'], state=state)
                if name.endswith('_stairs') or name.endswith('_door') or name == 'minecraft:ladder':
                    states.append(row)
                if name == 'minecraft:ladder':
                    x,y,zz = block['pos']
                    ladders[(x,zz)].append(y)
                if name.endswith('_door') and state.get('Properties', {}).get('half') == 'lower':
                    doors.append(row)
                if name == 'minecraft:jigsaw':
                    sockets.append(dict(position=block['pos'], state=state, data=block['nbt']))
            assert canonical(states) == canonical(original_states['stairs_doors_ladders'])
            assert canonical(doors) == canonical(original['doors'])
            assert canonical(sockets) == canonical(original['sockets'])
            outgoing = defaultdict(list)
            for s in sockets:
                outgoing[s['data']['pool']].append(s['position'])
            assert set(outgoing) == {p['pool'] for p in original_interface['outgoing_pools']}
            for p in original_interface['outgoing_pools']:
                assert sorted(p['socket_positions']) == sorted(outgoing[p['pool']])
                if p['status'] == 'FOUND_LOCAL':
                    body = z.read(p['member'])
                    assert digest(body) == p['sha256']
                    assert json.loads(body) == p['data']
                    pool_checks += 1
                    for comp in p['component_identities_only']:
                        if comp['exists_in_archive']:
                            assert digest(z.read(comp['member'])) == comp['sha256']
                            component_pairs.add((str(archive), comp['member']))
                else:
                    assert p['status'] == 'NOT_IN_THIS_ARCHIVE'
                    assert p['member'] not in z.namelist()
                    missing_pools.append(dict(id=c['id'], pool=p['pool'], status=p['status']))
        de = dedup_by_id[c['id']]
        assert de['nbt_sha256'] == c['nbt_sha256']
        assert geometry_hash({p:1 for p in cells}, nbt['size']) == de['occupancy_sha256']
        assert geometry_hash({p:role(n) for p,n in cells.items()}, nbt['size']) == de['role_sha256']
        assert len(de['prior_self_records_not_new_discovery']) == 1
        assert de['prior_self_records_not_new_discovery'][0]['member'] == c['member']
        assert not de['other_historical_exact_matches']
        review = by_id[c['id']]
        assert len(review['observations']) == 7
        assert set(review['observations']) == {'layout','proportion','facade','roof','materials','circulation','terrain'}
        assert review['native_acceptance'] is False
        assert len(review['actual_images_reviewed_again']) == 4
        for e in review['actual_images_reviewed_again']:
            check_evidence(e, image=True)
            image_paths.add(e['path'])
        for name in ('seven_aspect_record','original_state_record','interface_record'):
            check_evidence(review[name])
        state_rows.append(dict(id=c['id'], occupied_bounds=bounds, lower_doors=doors,
                               ladder_y_values=[dict(x=x,z=zz,ys=sorted(ys)) for (x,zz),ys in sorted(ladders.items())],
                               raw_opening_vertical_states_verified=len(states), outgoing_sockets=len(sockets)))
    assert len(image_paths) == 52
    assert len(semantic['historical_comparison_images_reviewed_again']) == 16
    for e in semantic['historical_comparison_images_reviewed_again']:
        check_evidence(e, image=True)
        assert e['path'] not in image_paths
    assert missing_pools == [dict(id='011-F02',pool='minecraft:village/common/cats',status='NOT_IN_THIS_ARCHIVE')]
    # Check every historical source-batch receipt, including held batch014.
    receipts_checked = []
    for batch in range(10, 16):
        folder = BASE / f'research-20261101-dungeons-{batch:03d}'
        for e in load(folder / 'RECEIPT.json')['files']:
            p = folder / e['path']
            assert p.stat().st_size == e['bytes'] and sha(p) == e['sha256'], p
        receipts_checked.append(ev(folder / 'RECEIPT.json'))
    for p in OUT.glob('*.py'):
        ast.parse(p.read_text(), filename=str(p))
    dump('raw-source-recheck.json',dict(entries=state_rows, source_archives=[dict(path=str(p),sha256=h) for p,h in archives.items()],
                                      found_local_pool_records_verified=pool_checks,
                                      distinct_component_byte_identities_verified=len(component_pairs),
                                      missing_pools_preserved=missing_pools, components_credited_as_buildings=0,
                                      native_path_or_terrain_acceptance=False))
    report = dict(status='PASS', proposals_reconsidered=13, accepted_scoped_layout_references=11,
                  held_proposals=2, remaining_original_23_template_holds=12,
                  scopes=[{k:s[k] for k in ('scope_id','accepted_references','target','remaining','construction_allowed')} for s in ledger['scopes']],
                  actual_source_image_relooks=52, actual_historical_image_relooks=16, new_source_templates=0, new_images=0,
                  immutable_input_evidence_files=35, source_batch_receipts_verified=receipts_checked,
                  preserved_registries=ledger['preserved_registries'],
                  source_archives_verified=len(archives), source_nbt_and_geometry_verified=13,
                  historical_geometry_screen_pairs_per_proposal=187, historical_pairs_are_not_reference_credit=True,
                  formal_review_is_same_owner=True, independent_human_review_claimed=False,
                  production_tasks_completed=0, checklist_deletions=0, network_requests=0,
                  java_run=False, game_run=False, sound_brightness_or_save_changes=0)
    dump('verification.json', report)
    files = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != 'RECEIPT.json')
    dump('RECEIPT.json',dict(status='PASS', files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
    for e in load(OUT / 'RECEIPT.json')['files']:
        p = OUT / e['path']
        assert p.stat().st_size == e['bytes'] and sha(p) == e['sha256']
    print(json.dumps({k:v for k,v in report.items() if k not in ('source_batch_receipts_verified','preserved_registries')},ensure_ascii=False))

if __name__ == '__main__':
    main()

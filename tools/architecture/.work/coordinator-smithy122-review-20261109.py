"""Record Main's actual whole-building review; never edit product or master TODOs."""
from pathlib import Path
import sys, json, hashlib, datetime, zipfile

sys.dont_write_bytecode = True
R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / 'tools/architecture'))
from nbt_read import read

B = R / 'docs/architecture/research-20261104-smithy-122'
D = R / 'docs/cod4/audit-20261022'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref = lambda p: {'path': str(Path(p).relative_to(R)), 'sha256': sha(p)}

assert sha(B/'RECEIPT.json') == '40e6fd862ee0464a914142ae4e429ef4fe53ad6d27902d9cd717fb669ed7b43f'
receipt = json.loads((B/'RECEIPT.json').read_text())
assert len(receipt['files']) == 42
for e in receipt['files']:
    p = Path(e['path'])
    assert p.stat().st_size == e['bytes'] and sha(p) == e['sha256']
old_bindings = []
for number, expected in [(120, 'ddbbf98515c03943388d89485b35b76652808067208545789cbe0e57f34de9b3'),
                         (121, 'ab611bded6035812c3a9144de675ed801c69c31da346226ef498dda8fe638706')]:
    p = B.parent / f'research-20261104-smithy-{number}' / 'RECEIPT.json'
    assert sha(p) == expected
    entries = json.loads(p.read_text())['files']
    for e in entries:
        q = Path(e['path'])
        assert sha(q) == e['sha256'] and q.stat().st_size == e['bytes']
    old_bindings.append({'receipt': ref(p), 'bound_files_unchanged': len(entries), 'new_semantic_credit': 0})

admissions = json.loads((B/'latest-independent-admissions.json').read_text())
pending = json.loads((B/'carried-forward-pending.json').read_text())
carry = admissions['newly_notified_admission_120_F02']
assert carry == pending['120F02_resolved_accept1_first122']
assert carry['first_bound_batch'] == 122 and carry['increment'] == 1 and carry['current_batch_source_credit'] == 0
assert sha(carry['receipt']['path']) == carry['receipt']['sha256']
assert not pending['carried_unresolved_whole_reference_proposals']
assert len(pending['current_batch_pending_cases']) == 1

row = json.loads((B/'raw-source-audit.json').read_text())['candidates'][0]
assert row['id'] == 'F01' and sha(row['source_archive']) == row['source_archive_sha256']
context = json.loads((B/'source-context.json').read_text())
with zipfile.ZipFile(row['source_archive']) as z:
    raw = z.read(row['member'])
    assert hashlib.sha256(raw).hexdigest() == row['nbt_sha256']
    n = read(raw)
    assert n == row['nbt_decoded_original']
    for e in context['candidates'][0]['contexts']:
        data = z.read(e['member'])
        assert hashlib.sha256(data).hexdigest() == e['sha256'] and json.loads(data) == e['json']
    for e in context['metadata']:
        if e['id'] == 'F01':
            data = z.read(e['member'])
            assert hashlib.sha256(data).hexdigest() == e['sha256'] and data.decode() == e['original_text']

pal = n['palette']
states = {tuple(v['pos']): v for v in n['blocks']}
matrix = json.loads((B/'F01-route-source-matrix.json').read_text())
for v in matrix['positions']:
    s = states.get(tuple(v['pos']))
    assert v['original_stored'] == (s is not None)
    if s is not None:
        assert pal[s['state']] == v['state'] and s.get('nbt') == v['nbt']
assert len(n['blocks']) == 1313 and len(pal) == 106 and n['entities'] == []
for z in [1, 2]:
    for x, y in [(4, 1), (5, 2), (6, 3), (7, 4)]:
        s = pal[states[x, y, z]['state']]
        assert s['Name'] == 'minecraft:stone_brick_stairs' and s['Properties']['facing'] == 'east'
assert pal[states[6, 1, 1]['state']]['Name'] == 'minecraft:stonecutter'

manual = json.loads((B/'manual-review.json').read_text())['cases'][0]
comparators = []
for e in manual['saved_written_comparisons']:
    p = Path(e['path'])
    assert sha(p) == e['sha256']
    cases = json.loads(p.read_text())['cases']
    comparators.append({'source': ref(p), 'complete_current_written_observations_actually_read': [
        {'id': c['id'], 'member': c['member'],
         'observations': c.get('observations', c.get('screening_observations')),
         'family_comparison': c.get('semantic_family_comparison', {}).get('comparison'),
         'whole_boundary': c.get('whole_boundary')}
        for c in cases], 'old_images_and_source_chains_reread': False, 'new_credit': 0})

review = {
    'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'reviewer_thread': '01a16364-cac0-7ca2-a042-a5312781ca34',
    'author_thread': '01a12515-f16a-7be3-b79a-bd5500f7ccd4',
    'decision': 'ACCEPT_ONE_COMPLETE_RELATED_COD3_CIVILIAN_WORKSHOP_SPATIAL_REFERENCE_ONLY',
    'source_receipt': ref(B/'RECEIPT.json'),
    'integrity_only': {'current42_files_bound': True, 'old_batches': old_bindings,
                       'prior120F02_first_carry_verified': carry, 'new_credit': 0},
    'source': {k: v for k, v in row.items() if k not in ['nbt_decoded_original', 'material_counts']},
    'actual_Main_reading': {
        'all10_images_actually_viewed': [ref(B/f'F01-{v}.png') for v in
            ['whole', 'cutaway', 'vertical', 'y0', 'y2', 'y4', 'y6', 'y8', 'y10', 'y12']],
        'full106_original_palette_states_read': pal,
        'primary_original_index_layers_read': [
            {'y': y, 'rows_z0to10_columns_x0to13_omitted_null': [
                [(states.get((x, y, z)) or {}).get('state') for x in range(14)]
                for z in range(11)]} for y in [0, 1, 2, 3, 4, 5, 6, 8, 9]],
        'all_original_block_entities_read': [v for v in n['blocks'] if 'nbt' in v],
        'source_context5_JSON_read': context['candidates'][0],
        'source_metadata3_read': [v for v in context['metadata'] if v['id'] == 'F01'],
        'route570_binding_only': ref(B/'F01-route-source-matrix.json'),
        'all1313_positions_individually_semantically_read': False,
        'F02_Main_images_or_source_studied': False},
    'written_comparators': comparators,
    'whole_spatial_judgment': [
        'One small complete civilian work/living building: a west-entry lower work hall connects through its north internal door to the open-ended cold-work recess underneath the external stairs; independent north exterior stairs reach a covered arrival landing and the single full-width upper living room. The relationship between internal lower circulation and external upper access is the studied whole, not individual furniture or material novelty.',
        '071F01 uses an internal east stair within the work hall to upper living/storage;122 keeps this vertical access outside and uses its underside as a door-connected secondary cold-work recess.087F02 has two unconnected bottom shops and only a south-half upper dwelling;122 has one connected lower work system and one unified upper room.',
        '070F02 has an open ground hot-work recess under an elevated main living house and a bent exterior approach;122 combines a closed ground hall, internally reached understair recess, straight exterior side climb and covered upper landing. These whole circulation relationships support one related instance, not a second credit for having two stonecutters.',
        '064 multi-level hot hall/house,095 internal ladder to three upper rooms,097 internal ladder to open L roof terrace,111 same-level opposite porches,115 internal stair to upper work/store plus hot wing/yard do not reproduce this whole arrangement. Relatedness is civilian workshop spatial planning only, not complete smithing craft.'],
    'specific_observations_and_limits': [
        '14x14x11/DV3953;2156 declared,1313 stored=982nonair331explicitair;843 omitted remain unknown. Two main usable levels floor0/use1 and floor4/use5;roof13 and chest8 do not make extra living floors.',
        'North double-width z1/2 stairs rise EAST x4y1,x5y2,x6y3,x7y4. They do not rise north. Landing x8..10,y4,z1/2 has upper air and turns south to door9,5/6,3. West lower door3,1/2,6 and internal north door9,1/2,3 are closed original states, not tested navigation.',
        'The north recess remains open at its west end. Stonecutter6,1,1 lies underneath the stair band; useful spatial intent is visible but actual head clearance and NPC interaction are untested. Other cutter7,1,7 is in the lower hall.',
        'Upper west-facing bed headx4/footx5,y5,z4..7 are four pairs, not eight beds. East bedside circulation x7..9 has explicit air; x6,y5,z4..7 are bottom slabs, not air. Five seeded mason chests include high storage, not an attic access proof.',
        'Lower masonry and upper timber/white-concrete enclosure use broad pitched oak-stair roof; small north landing roof is bottom oak slab at y8. Generic full-cell diagrams obscure half-block geometry, doors, materials and collisions. No water-tightness or NPC pathfinding claim.',
        'One west-facing empty-pool finalair entrance socket, no source entities or villager sockets. Mason residence sign is static original English, not Chinese quest dialogue. No furnace/anvil/lava or payment/getting-item receipt establishes smithy gameplay.',
        'Source plains root jigsaw size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue;exact mason house weight4/single/rigid/mossify10. Town-center mossify20 is contextual, not current house processor. Missing vanilla resources in this one Jar do not establish environment absence;DV3953/current1.20.1 compatibility and natural placement untested.',
        'Keep111 four fence columns y1..3,115 open-trapdoor/wall-torch corrections and118 actualDV3465/3105. No old source/image studies rerun. No direct copying or early production before applicable1000 complete references.'],
    'new_related_whole_COD3_reference': 1,
    'new_COD4_whole_building_credit': 0,
    'global_or_other_reference_credit': 0,
    'first_author_carry_required_exactly_once': True,
    'whole_dataset_cumulative_total_inferred': False,
    'production_changes': 0, 'native_acceptance': False, 'game_starts': 0,
    'checklist_deletions': 0, 'all_tasks_complete': False, 'actual_active_hours_claimed': None}
target = D/'coordinator-smithy122-F01-whole-review-20261109.json'
with target.open('x') as f:
    json.dump(review, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps({'receipt': ref(target), 'actual_Main_PNG': 10,
                  'related_COD3_whole_reference': 1, 'new_COD4': 0, 'production': 0}))

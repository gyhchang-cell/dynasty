"""Seal Main's independent spatial judgment; do not mutate specialist batches."""
from pathlib import Path
import sys, json, hashlib, zipfile, datetime

sys.dont_write_bytecode = True
R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / 'tools/architecture'))
from nbt_read import read

B = R / 'docs/architecture/research-20261104-smithy-125'
D = R / 'docs/cod4/audit-20261022'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref = lambda p: {'path': str(Path(p)), 'sha256': sha(p), 'bytes': Path(p).stat().st_size}
assert sha(B/'RECEIPT.json') == 'bc6ea8984fbbee2908fddbc26407202f6e41b8e71b5568f84e9c2273b9c845d2'
receipt = json.loads((B/'RECEIPT.json').read_text())
assert len(receipt['files']) == 52
for e in receipt['files']:
    assert sha(e['path']) == e['sha256'] and Path(e['path']).stat().st_size == e['bytes']
row = next(v for v in json.loads((B/'raw-source-audit.json').read_text())['candidates'] if v['id'] == 'F02')
assert sha(row['source_archive']) == row['source_archive_sha256']
context = json.loads((B/'source-context.json').read_text())
ctx = next(v for v in context['candidates'] if v['id'] == 'F02')
meta = [v for v in context['metadata'] if v['id'] == 'F02']
with zipfile.ZipFile(row['source_archive']) as z:
    data = z.read(row['member'])
    assert hashlib.sha256(data).hexdigest() == row['nbt_sha256']
    n = read(data)
    assert n == row['nbt_decoded_original']
    for e in ctx['contexts']:
        data = z.read(e['member'])
        assert hashlib.sha256(data).hexdigest() == e['sha256'] and json.loads(data) == e['json']
    for e in meta:
        data = z.read(e['member'])
        assert hashlib.sha256(data).hexdigest() == e['sha256'] and data.decode() == e['original_text']
    assert all(v not in z.namelist() for v in ctx['missing'])
pal = n['palette']
states = {tuple(v['pos']): v for v in n['blocks']}
assert len(pal) == 112 and len(states) == 1757 and not n['entities']
matrix = json.loads((B/'F02-route-source-matrix.json').read_text())
for v in matrix['positions']:
    s = states.get(tuple(v['pos']))
    assert v['original_stored'] == (s is not None)
    if s is not None:
        assert pal[s['state']] == v['state'] and s.get('nbt') == v['nbt']

comparators = []
for num, case_id in [(95,'F02'),(97,'F01'),(120,'F02'),(122,'F01'),(123,'F01')]:
    p = B.parent/f'research-20261104-smithy-{num:03d}'/'manual-review.json'
    c = next(v for v in json.loads(p.read_text())['cases'] if v['id'] == case_id)
    comparators.append({'source': ref(p), 'case_id': case_id, 'member': c['member'],
                        'complete_written_observations_actually_read': c.get('observations',c.get('screening_observations')),
                        'old_images_or_source_chains_reread': False, 'new_credit': 0})

route = [(2,y,14-y) for y in range(1,5)] + [(2,4,9),(2,5,9),(2,6,9)]
route += [(x,y,3) for x in range(2,6) for y in range(4,7)]
route += [(8,y,7) for y in [5,6]]
route += [(x,y,5) for x in [11,12,13] for y in range(5,14)]
route += [(6,y,z) for z in [9,10,11] for y in [4,5,6]]
point = lambda p: {'pos': list(p), 'original_stored': p in states,
                    'state': pal[states[p]['state']] if p in states else None,
                    'nbt': states[p].get('nbt') if p in states else None}
for y in range(1,5):
    s = pal[states[2,y,14-y]['state']]
    assert s['Name'] == 'minecraft:oak_stairs' and s['Properties']['facing'] == 'north'
for y in range(5,13):
    assert pal[states[12,y,5]['state']]['Name'] == 'minecraft:ladder'
assert pal[states[12,13,5]['state']]['Name'] == 'minecraft:air'
bentities = [v for v in n['blocks'] if 'nbt' in v]
villagers = [v for v in bentities if v['nbt'].get('pool') == 'trek:village/swamp/villagers']
assert len(villagers) == 2
assert all(v['nbt']['final_state'] == 'minecraft:cobblestone_slab[type=top, waterlogged=false]' for v in villagers)
manual = next(v for v in json.loads((B/'manual-review.json').read_text())['cases'] if v['id'] == 'F02')
review = {
 'recorded_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'reviewer_thread': '01a16364-cac0-7ca2-a042-a5312781ca34',
 'author_thread': '01a12515-f16a-7be3-b79a-bd5500f7ccd4',
 'decision': 'ACCEPT_ONE_COMPLETE_RELATED_COD3_CIVILIAN_WORKSHOP_SPATIAL_REFERENCE_ONLY',
 'source_receipt': ref(B/'RECEIPT.json'),
 'integrity_only': {'bound_current_files':52,'author_501_integrity_checks_are_not_semantic_credit':True,
                    'primary_route_matrix_bound_positions':len(matrix['positions']),'new_credit':0},
 'source': {k:v for k,v in row.items() if k not in ['nbt_decoded_original','material_counts']},
 'actual_Main_reading': {
  'all16_F02_PNG_actually_viewed': [ref(B/f'F02-{s}.png') for s in ['whole','cutaway','vertical']+[f'y{y}' for y in range(0,25,2)]],
  'all112_original_palette_states_read':pal,
  'all_original_block_entities_read':bentities,
  'main_floor_primary_index_matrices_read':[
   {'y':y,'columns_x1to14_rows_z1to11_omitted_null':[[states.get((x,y,z),{}).get('state') for x in range(1,15)] for z in range(1,12)]} for y in [4,5,6]],
  'upper_pavilion_primary_index_matrices_read':[
   {'y':y,'columns_x9to14_rows_z2to8_omitted_null':[[states.get((x,y,z),{}).get('state') for x in range(9,15)] for z in range(2,9)]} for y in [13,14]],
  'low_target_ground_primary_index_matrix_read':{'y':0,'columns_x5to14_rows_z10to14_omitted_null':[[states.get((x,0,z),{}).get('state') for x in range(5,15)] for z in range(10,15)]},
  'exact_route_states_read':[point(p) for p in route],
  'all7_original_context_JSON_read':ctx,'all3_original_metadata_read':meta,
  'complete_F02_author_observations_read':manual['screening_observations'],
  'all1757_positions_individually_semantically_read':False,
  'F01_Main_visual_or_original_source_study':False},
 'written_comparators':comparators,
 'whole_spatial_judgment':[
  'One complete civilian workshop/home organization: north-rising west exterior stairs reach a covered west arrival platform; west reception/display and east fletching/two-bed living spaces occupy the raised main layer, divided by a door-bearing partial partition; the internal east ladder reaches a small open covered work pavilion, while southern target positions remain in a lower independent site zone. This entire organization is one reference, not separate credit for its two beds, targets, three tables, sockets, rooms or roof.',
  '120F02 has exterior raised arrival but a single continuous L-shaped one-layer work/home hall and southwest recessed wet work, without the internal ladder or upper work branch.125 adds the reception-to-partitioned work/living relation and an internal high work branch; its relation to the lower site zone is also different. Elevation or swamp materials alone would not justify acceptance.',
  '123F01 has a ground longitudinal fletching hall and its internal ladder leads to an open work pavilion, with a same-ground east target yard and no beds or reception-to-work/living partition.097F01 combines one L-shaped mixed ground work/home room, internal ladder to an open L storage terrace, and east water court.125 is not accepted merely for the shared internal ladder/pavilion or side yard; the jointly studied raised arrival, transverse functional partition and inhabited work/home layer under a separate high work node distinguish the complete design.',
  '095F02 has a lower enclosed bedroom and separate stonecutter shed, then internal ladder to an upper anvil room branching into two enclosed rooms;122F01 has a lower connected hall/understair cold recess and entirely external upper dwelling access. Neither is this two-part main-layer reception/work-home organization with internal access to a small open pavilion and a lower separate activity zone. One related whole instance accepted, without treating every changed furnishing or family similarity as extra credit.',
  'Relevance is civilian craft-workshop planning, including arriving customers, living/work adjacency, vertical work separation and lower outdoor activity. There is no furnace/anvil/lava and this is not a complete smithing process, exact Dynasty terrain placement, NPC behavior or quest implementation.'],
 'specific_limits':[
  '17x25x17/DV3953;7225declared=1757stored+5468omitted. Stored1249nonair508air. Omitted cells remain unknown, and generic full-cell diagrams are not native collision/half-block/door geometry or original textured renders.',
  'Main floor4/use5, upper pavilion floor13 bottom slab/use14, roof maximum24; high double chest at10 is not a third usable living storey. East two bed pairs are foot12/head13,y5,z7/8; x11 bedside is bottom slab, not air.',
  'West exterior stairs (2,1,13) to (2,4,10) face north. West door4,5/6,3 and internal door8,5/6,7 are original closed states. Partial x8 partition includes stair/fence/air, so internal door is not proven sole traversable link or a full sealed wall.',
  'Eight west-facing ladder blocks x12,y5..12,z5 lead toward air at12,13,5; west adjacency includes planks at y9 and upper bottom slab. Ladder landing, headroom and NPC route are untested. The high work pavilion is open framed/fenced, not an enclosed bedroom.',
  'South door6,5/6,9 overlooks top closed trapdoors at y4,z10/11 and a closed gate6,5,11, not a direct air path to ground. Low target y0 matrix contains sparse soil and many omitted cells: no continuous deck, terrain support or reliable route asserted.',
  'Five original seeded fletcher chest blocks include one double pair; all loot remains a reference, not claimed obtained. Four bed states are two beds; candles3/litfalse is one block, not three heat sources. Two target blocks have power0; no active shooting or crafting observed.',
  '15jigsaws consist of11downward oak-column sockets,2villager sockets,2empty entrance sockets. Pool candidates do not prove actual residents. Both current final_state values contain correctly spelled cobblestone_slab and the exact original space after comma; old120 slap typo is not transferred.',
  'Saved swamp_vanilla houses pool points to a different swamp_vanilla path; no exact swamp source selection. Column pool and vanilla loot missing only inside this source Jar. Processor and villager pools are contextual, not shown applied. Original pack metadata and DV do not prove current1.20.1 compatibility or natural generation.',
  'Old111/115/118 corrections and prior120first122,122first124 acceptances remain unchanged. Written comparisons reuse prior evidence; no old source/image chains re-executed. F01 remains bounded author hold0, not independently re-reviewed by Main.'],
 'new_related_whole_COD3_reference':1,'new_COD4_whole_building_credit':0,
 'global_or_other_reference_credit':0,'first_author_carry_required_exactly_once':True,
 'whole_dataset_cumulative_total_inferred':False,
 'production_changes':0,'native_acceptance':False,'game_starts':0,
 'checklist_deletions':0,'all_tasks_complete':False,'actual_active_hours_claimed':None}
target = D/'coordinator-smithy125-F02-whole-review-20261109.json'
with target.open('x') as f:
    json.dump(review,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'receipt':ref(target),'actual_Main_images':16,'original_BE':len(bentities),
                  'new_related_COD3_whole_reference':1,'new_COD4':0,'production':0}))

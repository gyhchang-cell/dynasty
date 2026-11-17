"""Seal Main's completed reading; no production or author-batch writes."""
import hashlib
import importlib.util
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/Users/a15356015027/Desktop/dynasty')
BASE = ROOT / 'docs/architecture/research-20261104-smithy-138'
OUT = ROOT / 'docs/cod4/audit-20261022/coordinator-smithy138-F02-whole-review-20261109.json'
assert not OUT.exists(), 'Immutable receipt already exists'

def load(p):
    return json.loads(p.read_text())

def binding(p):
    b = p.read_bytes()
    return {'path': str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
            'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}

receipt = load(BASE / 'RECEIPT.json')
assert binding(BASE / 'RECEIPT.json')['sha256'] == '1f4fbc59a6362db31bc588dda0ec38e1eaae84d5cf06ce7d97d46bdb56f32342'
for f in receipt['files']:
    now = binding(Path(f['path']))
    assert (now['sha256'], now['bytes']) == (f['sha256'], f['bytes'])
c = load(BASE / 'raw-source-audit.json')['candidates'][1]
assert c['id'] == 'F02'
spec = importlib.util.spec_from_file_location('readonly_nbt', ROOT / 'tools/architecture/nbt_read.py')
nbt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nbt)
assert binding(Path(c['source_archive']))['sha256'] == c['source_archive_sha256']
contexts = load(BASE / 'source-context.json')['candidates'][1]['contexts']
with zipfile.ZipFile(c['source_archive']) as z:
    raw = z.read(c['member'])
    assert hashlib.sha256(raw).hexdigest() == c['nbt_sha256']
    decoded = nbt.read(raw)
    assert decoded == c['nbt_decoded_original']
    for ctx in contexts:
        rawctx = z.read(ctx['member'])
        assert hashlib.sha256(rawctx).hexdigest() == ctx['sha256']
        assert json.loads(rawctx) == ctx['json']
assert decoded['size'] == [13, 22, 15] and decoded['DataVersion'] == 2974
assert len(decoded['blocks']) == 4290 and len(decoded['palette']) == 79 and decoded['entities'] == []
palette = decoded['palette']
states = {tuple(b['pos']): palette[b['state']] for b in decoded['blocks']}
assert states[(7, 7, 2)]['Name'] == 'minecraft:crafting_table'
assert states[(7, 6, 2)]['Properties']['open'] == 'false'
assert {s['Name'] for s in palette if 'candle' in s['Name']} == {'minecraft:orange_candle'}
imgs = [binding(p) for p in sorted(BASE.glob('F02-*.png'))]
assert len(imgs) == 14
comparators = []
for batch, cid, judgment in [
    ('126', 'F01', 'Continuous winding interior stair exits laterally into a long covered upper work gallery. Current whole has a lower flower room, upper main workroom, side vestibule and a separate rear scaffold to a roof/tower-base ledge; neither winding stair nor gallery is claimed new alone.'),
    ('128', 'F02', 'Outer stair serves a raised closed hot-work room over an animal yard, with west low public apron. Current basement flower display and upper cold workroom are not an animal yard beneath an elevated heat room, and the side vestibule/rear scaffold are different whole circulation organization.'),
    ('134', 'F02', 'Ground public library -> interior turn stair -> upper cartography work area with a platform under the same roof. Current source places the flower room below an elevated main room and uses a southwest buffered side entry and rear scaffold to an open roof/tower base; a cartography table or roof terrace alone is already old.'),
    ('136', 'F02', 'Open central court and two staggered north stair flights linked by open perimeter work ledges. Current main room is enclosed above a flower basement, with separate side entry and scaffold route, not a repeated perimeter-court organization.'),
]:
    p = ROOT / f'docs/architecture/research-20261104-smithy-{batch}/manual-review.json'
    case = next(x for x in load(p)['cases'] if x['id'] == cid)
    comparators.append({**binding(p), 'case': cid,
        'actual_saved_fields_read': {k: case['screening_observations'][k] for k in ['layout','proportion','circulation']},
        'independent_comparison': judgment, 'old_PNG_or_original_NBT_replayed': False, 'additional_reference_credit': 0})
observations = [
 'One whole elevated civilian cold-workshop arrangement: basement flower display under the main workroom, southwest side-entry vestibule one step above the main use floor, and a rear scaffold to the tower-base ledge and north door out to the roof. The whole combination is a related space-organization study for COD3 NPC01; not an operational smithy, separate buildings, automatic flower farm, or an approved game feature.',
 'All22 original planes0..21 were actually read as lossless row state-index runs, all79palette entries and both blockentities read;14 original F02 PNGs actually viewed. Full-cell category-color diagrams are not the source textures/collision meshes. 4290stored=1682nonair+2608explicitair, no omitted positions. y21 is entirely original air, not a usable22nd floor.',
 'Independent archive extraction and equality check used the existing shared read-only nbt_read.py decoder, not a newly independent parser implementation. Archive/NBT hashes and the entire decoded original match; integrity verification adds no semantic reference credit.',
 'Basement floor1/use2 contains21grass and21poppies in three7-wide rows atz5/8/11, with open spruce trapdoor borders, hanging lantern groups and andesite enclosure. These plants and lamps are static source placement, not renewal, survival resources or tested work production.',
 'Source southern-facing ladder pieces atx6y2..4z2 andx7y3..5z2 lead toward TOP/south/closed trapdoor(7,6,2); crafting_table occupies(7,7,2) directly above and cut sandstone is at(7,6,3). No unobstructed basement-to-main passage, headroom or NPC usability is accepted. The whole design can be studied despite this documented source defect; its vertical material route must not be copied as a proved usable path.',
 'North jigsaw(3,7,0)north_up targets the roads pool with literal final air, arriving on the western exterior terrace rather than directly through the solid wall atx5z2. Southwest south/bottom step(3,7,8) -> north/right closed jungle door(3,8/9,9) -> vestibule air(3,8,10) ->(4,8,11)/(5,8,11) above west/bottom step(5,7,11) ->main air(6,7,11). Actual gray concrete powder below at(6,6,11) is not an assertion of stable runtime floor behavior.',
 'Main floor6/use7 contains cartography table(9,7,2), crafting table(7,7,2),15bookshelves, chairs and the east-facing chest(6,7,3). Correction to the author sealed description: the candle palette is orange_candle only, not red candles. Preserve sealed source receipt and carry this correction; no color-variant extra reference.',
 'Rear scaffold(10,y7..12,12)distance0/bottomfalse reaches air at(10,13/14,12), then thex10z11/10/9air corridor above cut-sandstone floor12, then north/left door(10,13/14,8) and roof air(10,13/14,7). These state relationships do not certify scaffold movement, headroom, NPC pathfinding or collision.',
 'Roof floor12 retains a2x2air well atx7/8,z9/10; fences atx9z9/10 andx7..9z11 bound only parts of its edges. It is not a fully paved roof. Tower shell and alternating bottom/TOP cut slabs y14..20, including localized northwest top slabs aty19, provide no continuous internal upper ascent or full upper work floor.',
 'Only two blockentities: road jigsaw and east single cartographer chest with LootTableSeed5999756742035830497; entities[] and no villager socket. No bed/furnace/anvil/water/lava. A south-facing piston(7,7,1)extendedfalse,9redstone states power0 and wall-west button(10,6,7)poweredfalse do not prove machine operation or automated flower harvest.',
 'Actual root fortified_desert_village jigsaw size5/max80/start0/WORLD_SURFACE_WG/beard_thin/expansiontrue; selected house weight2 rigid single_pool_element uses minecraft:empty processor. Starts has a single weight1 rigid castle, whose NBT remains unread. Roads context was semantically scoped to name/fallback/count15/straight2sample; no claim of studying14other road layouts or the castle.',
 'Actual biome tag replacefalse has desert/desert_oasis/lush_desert. The road processor clears grass/tallgrass and makes conditional water-preserving or spruce-bridge substitutions, with later terrain-dependent random choices. It is context for roads and does not automatically process this house or prove actual generated terrain.',
 'Cartographer loot spyglass random chance0.2, boots, saddle/bundle/lead, maps/compass/book and paper/stick/emerald pools are candidates only, not paid trades, real inventory, Chinese compass text or native player receipts. Collected contexts missing[] means only those collected dependencies were found in the source archive, not a complete current runtime environment.',
 'Terralith metadata was reused from the already completed Main136 fixed-source metadata reading (3entries,0new credit), not reread as a new source chain. DV2974/source pack metadata does not establish current1.20.1 compatibility, natural mountain placement or runtime acceptance. Study spatial principles only, no source asset copying.',
 'Main F01 images0 and whole-source studyfalse; no F01 credit or claim of viewing every generated image in batch138. Historical111fence/115open-trapdoor-and-walltorch/118DataVersion corrections remain. New acceptance does not alter sealed138/139/140 or erase their older pending status retrospectively.',
]
report = {
 'recorded_at': datetime.now(timezone.utc).isoformat(),
 'reviewer_thread': '01a16364-cac0-7ca2-a042-a5312781ca34',
 'author_thread': '01a12515-f16a-7be3-b79a-bd5500f7ccd4',
 'decision': 'ACCEPT_ONE_COMPLETE_RELATED_COD3_NPC01_SPATIAL_REFERENCE_NOT_GAME_TASK',
 'source_receipt': binding(BASE/'RECEIPT.json'),
 'integrity_only': {'declared_current_files_verified':len(receipt['files']), 'author_4673_checks_not_Main_4673_checks':True, 'hashing_adds_reference_credit':0},
 'source': {k:c[k] for k in ['source_archive','source_archive_sha256','member','nbt_sha256','size','DataVersion','nonair','air']},
 'actual_Main_reading': {'current_original_F02_images_viewed':imgs, 'all_original_palette_entries_read':79,
    'all_original_layers_read':list(range(22)), 'layer_dimensions':[13,15], 'all_original_block_entities_read':2,
    'original_entities':[], 'archive_extraction_entire_saved_original_equality':True,
    'decoder':binding(ROOT/'tools/architecture/nbt_read.py'), 'decoder_is_existing_shared_utility':True,
    'original_context_scope':['root full','selected house entry only','starts full,castleNBT unread','roadpool name/fallback/count15/straight2 sample only','cartographer loot full','biometag full','roadprocessor full'],
    'context_byte_equality_bindings':[{k:x[k] for k in ['member','sha256']} for x in contexts],
    'source_bindings':[binding(BASE/f) for f in ['raw-source-audit.json','manual-review.json','full-study-reading-boundary.json','source-context.json','source-context-reading.json']],
    'metadata_reuse_only':binding(ROOT/'docs/cod4/audit-20261022/coordinator-smithy136-F02-whole-review-20261109.json'),
    'F01_Main_images_viewed':0,'F01_Main_whole_source_study':False,'F01_credit':0},
 'written_comparators':comparators,
 'whole_spatial_judgment':{'unit':'One related complete civilian cold-workshop spatial design, COD3 NPC01 only',
    'credit':1,'independent_combination':'Lower flower room / upper main cold workroom / raised southwest buffered side entry / separate rear scaffold to tower base and roof; no proved basement connection or continuous upper tower circulation',
    'relevance_limit':'Spatial layering and separated entry/service approach only; no smithing/material-farm/fully-passable-route/mountain or native usability claim'},
 'observations_and_limits':observations,
 'new_related_whole_COD3_reference':1,'new_COD4_whole_building_credit':0,'global_or_other_reference_credit':0,
 'first_author_carry_required_exactly_once':True,'author_must_not_mutate_sealed138':True,
 'whole_dataset_cumulative_total_inferred':False,'production_changes':0,'native_acceptance':False,
 'game_starts':0,'checklist_deletions':0,'all_tasks_complete':False,'actual_active_hours_claimed':None,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('x') as f:
    json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(binding(OUT),ensure_ascii=False))

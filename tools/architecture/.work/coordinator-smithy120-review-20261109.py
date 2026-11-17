"""Save independent study of one complete related workshop, not a product completion."""
from pathlib import Path
import sys, json, hashlib, datetime, zipfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools/architecture'))
from nbt_read import read
B = ROOT/'docs/architecture/research-20261104-smithy-120'
D = ROOT/'docs/cod4/audit-20261022'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return {'path':str(Path(p).relative_to(ROOT)), 'sha256':sha(p)}

assert sha(B/'RECEIPT.json') == 'ddbbf98515c03943388d89485b35b76652808067208545789cbe0e57f34de9b3'
receipt=json.loads((B/'RECEIPT.json').read_text())
for f in receipt['files']:
    assert sha(f['path']) == f['sha256']
row=next(r for r in json.loads((B/'raw-source-audit.json').read_text())['candidates'] if r['id']=='F02')
archive=Path(row['source_archive']); assert sha(archive)==row['source_archive_sha256']
with zipfile.ZipFile(archive) as z:
    raw=z.read(row['member']); assert hashlib.sha256(raw).hexdigest()==row['nbt_sha256']
    n=read(raw); assert n==row['nbt_decoded_original']
    contexts=json.loads((B/'source-context.json').read_text())
    source_context=next(x for x in contexts['candidates'] if x['id']=='F02')
    for item in source_context['contexts']:
        payload=z.read(item['member']); assert hashlib.sha256(payload).hexdigest()==item['sha256']
        assert json.loads(payload)==item['json']
states={tuple(v['pos']):v for v in n['blocks']};pal=n['palette']
route=json.loads((B/'F02-route-source-matrix.json').read_text())
for v in route['positions']:
    source=states[tuple(v['pos'])]
    assert v['original_stored'] is True and pal[source['state']]==v['state'] and source.get('nbt')==v['nbt']
for z in range(7,11): assert pal[states[(2,4,z)]['state']]['Name']=='minecraft:air'
assert len(n['blocks'])==934 and len(pal)==91 and n['entities']==[]
images=[B/('F02-'+v+'.png') for v in ['whole','cutaway','vertical','y0','y2','y4','y6','y8','y10','y12']]
prior=[]
for batch,ident in [(61,'F03'),(61,'F01'),(95,'F02'),(97,'F01'),(111,'F02'),(115,'F01')]:
    p=ROOT/f'docs/architecture/research-20261104-smithy-{batch:03}/manual-review.json'
    case=next(v for v in json.loads(p.read_text())['cases'] if v['id']==ident)
    prior.append({'source':ref(p),'case':ident,
                  'complete_current_written_observations_actually_read': {k:v for k,v in case.items() if k not in ['images_actually_viewed','saved_written_comparisons','comparison_history','inputs','source_context','comparison_sources','images','source_comparisons']},
                  'old_source_or_images_reread':False,'new_credit':0})
own={
 'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'reviewer_thread':'01a16364-cac0-7ca2-a042-a5312781ca34',
 'author_thread':'01a12515-f16a-7be3-b79a-bd5500f7ccd4',
 'decision':'ACCEPT_ONE_COMPLETE_RELATED_COD3_WORKSHOP_SPATIAL_REFERENCE_ONLY',
 'source_receipt':ref(B/'RECEIPT.json'),
 'source':{k:v for k,v in row.items() if k not in ['nbt_decoded_original','material_counts']},
 'actual_source_reading':{
  'all10_listed_PNG_actually_viewed': [ref(p) for p in images],
  'full91_palette_states_actually_read':pal,
  'actual_primary_original_index_layers':[{'y':y,'rows_z0to12_columns_x0to11':[[(states.get((x,y,z)) or {}).get('state') for x in range(12)] for z in range(13)]} for y in range(3,9)],
  'original_functional_positions_actually_read':[v for v in n['blocks'] if pal[v['state']]['Name'] in ['minecraft:oak_door','minecraft:water_cauldron','minecraft:light_blue_bed','minecraft:chest','minecraft:jigsaw','minecraft:decorated_pot','minecraft:spruce_wall_hanging_sign']],
  'source_contexts_actually_read':source_context,
  'route105_original_states_bound':ref(B/'F02-route-source-matrix.json'),
  'whole934_position_semantic_reading_claimed':False,
  'all934_parsed_equal_is_integrity_not_reference_credit':True,
  'F01_source_or_images_not_Main_studied':True},
 'complete_current_written_comparisons':prior,
 'whole_family_judgment':[
  'Accept one related complete civilian workshop spatial design for COD3 NPC01. One raised unified house combines a covered NW arrival platform, a side recessed external wet-work strip and a continuous enclosed L work/living interior. The division and access between these zones, not the three cauldrons or two beds, forms one studied instance.',
  'Against061F03, its elevated open front work-veranda feeding one small cold room is not this covered entry platform branching sidewards to the recessed wet strip and through one west door to an L interior with a south domestic continuation.',
  'Against061F01, this is raised external arrival into a continuous interior and side outdoor wet strip, rather than a ground long hot hall with separate bedroom inner/outer doors and front cold court.',
  'Against095F02,097F01 and115F01, there is no internal ladder/stair to an independently usable upper work/storage/bed level. High chests do not supply another floor. Against111F02, the arrangement is not a three-door central workroom between opposite same-level porches.',
  'Do not count roof, profession, water levels, bed pairs, rooms, sections, views, sockets or palette as extra buildings; no whole-dataset cumulative count inferred.'],
 'specific_observations':[
  '12x13x13/DV3953.934stored positions include705nonair229explicitair;1094omitted positions remain unknown, not air. Main inspected complete exterior/sections plus palette/primary layer indices/functional original NBT; no claim of every position individually semantically read.',
  'Exterior bottom oak stair path (2,1,9)->(2,2,8)->(2,3,7)->(2,4,6) faces north; north landing top slabs at(2/3,4,3/5) lead to west-facing closed door(4,5/6,3). No half-block collision or NPC traversal proof.',
  'Correction retained: x2,y4,z7..10 are explicitly air. Do not describe that line as a continuous western corridor. Wet-strip access turns through the roof-corner side floor near x3/4,z6, with x4,z7..10 slab floor beside the cauldrons.',
  'Three water cauldrons (5,5,7/8/9) levels3/1/2 sit outside x6 timber wall; north interior reaches south paired beds via x7/8,z5/6 air. Two bed pairs at x7 and9,z9/10 are two beds, not four.',
  'Low broad pitched spruce roof/trim binds whole composition; spruce stairs/slabs/trapdoors and oak framework dominate.58vines are wall vegetation, not58grass floor tiles. Generic full-cell color diagrams do not reproduce slab collisions, textures or waterproofing.',
  'Three seeded tannery chests, two high at y8, do not imply an attic stair. No furnace, lava, smithing table, anvil or grinder establishes a complete smithing production chain; only spatial organization is relevant here.',
  'Fourteen hanging signs include13blank and one static Local/Tannery versus CLOSED faces. They do not prove dynamic opening hours, Chinese tasks or active vendor state.',
  'Two villagers are jigsaw requests, not actual entities. Their original final_state cobblestone_slap misspelling remains uncorrected. Ten down-column sockets use a missing-in-this-Jar pool, not ten extra buildings.',
  'Original body is village/swamp while saved nearby root/houses use swamp_vanilla. Exact selected matching source is empty; adjacent weighted entries/processors do not establish natural registration or application to this body. Missing single-Jar dependencies do not prove environment missing.',
  'Root size6/maxdistance80/WORLD_SURFACE_WG/start0/terrainnone and actual material/roof organization may guide future authored integration only after applicable1000wholebuildings. No direct copy or current1.20.1 compatibility claim.'],
 'new_related_whole_COD3_reference':1,
 'new_COD4_whole_building_credit':0,
 'global_or_other_research_credit':0,
 'first_author_carry_required_exactly_once':True,
 'original120_sealed_files_unchanged':True,
 'production_changes':0,'native_acceptance':False,'game_starts':0,
 'checklist_deletions':0,'all_tasks_complete':False,'actual_active_hours_claimed':None}
target=D/'coordinator-smithy120-F02-whole-review-20261109.json'
with target.open('x') as f:json.dump(own,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'path':str(target.relative_to(ROOT)),'sha256':sha(target),
                  'new_COD3_whole_reference':1,'new_COD4':0,'Main_actualPNG':10,'route_original_states':len(route['positions']),'production':0}))

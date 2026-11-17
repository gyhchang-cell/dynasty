"""Record Main's actual complete small-workshop study and exact prior carry."""
from pathlib import Path
import sys,json,hashlib,datetime,zipfile
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'tools/architecture'))
from nbt_read import read
B=R/'docs/architecture/research-20261104-smithy-126'
D=R/'docs/cod4/audit-20261022'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'path':str(Path(p)),'sha256':sha(p),'bytes':Path(p).stat().st_size}
assert sha(B/'RECEIPT.json')=='0c84b3d27cb6dbfb2b17527b33b4f6bdef6d73a96856113ffe87f0bc1a35e96a'
sealed=json.loads((B/'RECEIPT.json').read_text());assert len(sealed['files'])==39
for e in sealed['files']:
    assert sha(e['path'])==e['sha256'] and Path(e['path']).stat().st_size==e['bytes']
admission=json.loads((B/'latest-independent-admissions.json').read_text())['newly_notified_admission_125_F02']
pending=json.loads((B/'carried-forward-pending.json').read_text())
assert admission==pending['125F02_resolved_accept1_first126']
assert admission['increment']==1 and admission['first_bound_batch']==126 and admission['current_batch_source_credit']==0
assert sha(admission['receipt']['path'])==admission['receipt']['sha256']
assert pending['carried_unresolved_whole_reference_proposals']==[]
assert pending['current_batch_pending_cases']==[{'batch':126,'id':'F01','maximum':1,'independent_admission':False}]
old125=B.parent/'research-20261104-smithy-125'/'RECEIPT.json'
assert sha(old125)=='bc6ea8984fbbee2908fddbc26407202f6e41b8e71b5568f84e9c2273b9c845d2'
for e in json.loads(old125.read_text())['files']:
    assert sha(e['path'])==e['sha256'] and Path(e['path']).stat().st_size==e['bytes']
row=json.loads((B/'raw-source-audit.json').read_text())['candidates'][0]
assert row['id']=='F01' and sha(row['source_archive'])==row['source_archive_sha256']
context=json.loads((B/'source-context.json').read_text())
ctx=next(v for v in context['candidates'] if v['id']=='F01')
meta=[v for v in context['metadata'] if v['id']=='F01']
with zipfile.ZipFile(row['source_archive']) as z:
    raw=z.read(row['member']);assert hashlib.sha256(raw).hexdigest()==row['nbt_sha256']
    n=read(raw);assert n==row['nbt_decoded_original']
    for e in ctx['contexts']:
        raw=z.read(e['member']);assert hashlib.sha256(raw).hexdigest()==e['sha256'] and json.loads(raw)==e['json']
    for e in meta:
        raw=z.read(e['member']);assert hashlib.sha256(raw).hexdigest()==e['sha256'] and raw.decode()==e['original_text']
    assert all(p not in z.namelist() for p in ctx['missing'])
pal=n['palette'];S={tuple(b['pos']):b for b in n['blocks']}
assert len(pal)==45 and len(S)==648 and n['entities']==[] and n['size']==[6,11,13]
matrix=json.loads((B/'F01-route-source-matrix.json').read_text())
for v in matrix['positions']:
    b=S.get(tuple(v['pos']));assert v['original_stored']==(b is not None)
    if b is not None:assert pal[b['state']]==v['state'] and b.get('nbt')==v['nbt']
steps=[((3,1,9),'west'),((2,2,10),'south'),((3,3,11),'east'),((4,4,10),'north'),
       ((3,5,9),'west'),((2,6,10),'south'),((3,7,11),'east'),((4,8,10),'north')]
for p,facing in steps:
    s=pal[S[p]['state']];assert s['Name']=='minecraft:smooth_sandstone_stairs' and s['Properties']['facing']==facing and s['Properties']['half']=='bottom'
assert pal[S[4,4,8]['state']]['Name']=='minecraft:cut_sandstone'
for y in [5,6]:assert pal[S[4,y,8]['state']]['Name']=='minecraft:air'
comparators=[]
for num,case_id in [(71,'F01'),(87,'F02'),(115,'F01'),(123,'F01')]:
    p=B.parent/f'research-20261104-smithy-{num:03d}'/'manual-review.json'
    c=next(v for v in json.loads(p.read_text())['cases'] if v['id']==case_id)
    comparators.append({'source':ref(p),'case_id':case_id,'member':c['member'],
      'complete_current_written_observations_actually_read':c.get('observations',c.get('screening_observations')),
      'old_images_or_original_source_chains_reread':False,'new_credit':0})
review={
 'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'reviewer_thread':'01a16364-cac0-7ca2-a042-a5312781ca34',
 'author_thread':'01a12515-f16a-7be3-b79a-bd5500f7ccd4',
 'decision':'ACCEPT_ONE_COMPLETE_RELATED_COD3_CIVILIAN_WORKSHOP_SPATIAL_REFERENCE_ONLY',
 'source_receipt':ref(B/'RECEIPT.json'),
 'integrity_only':{'current39_files_bound':True,'author308_checks_are_not_semantic_credit':True,
    'primary_route_matrix_bound_positions':len(matrix['positions']),
    'sealed125_52files_unchanged':True,'125F02_first126_carry_verified_not_new126_credit':admission,'new_credit':0},
 'source':{k:v for k,v in row.items() if k not in ['nbt_decoded_original','material_counts']},
 'actual_Main_reading':{
   'all9_F01_PNG_actually_viewed':[ref(B/f'F01-{s}.png') for s in ['whole','cutaway','vertical','y0','y2','y4','y6','y8','y10']],
   'all45_original_palette_states_read':pal,
   'all5_original_block_entities_read':[b for b in n['blocks'] if 'nbt' in b],
   'all11_primary_index_layers_read':[
      {'y':y,'columns_x0to5_rows_z0to12_omitted_null':[[S.get((x,y,z),{}).get('state') for x in range(6)] for z in range(13)]} for y in range(11)],
   'eight_original_spiral_step_states_read':[{'pos':list(p),'state':pal[S[p]['state']]} for p,_ in steps],
   'source_context3_JSON_read':ctx,'source_metadata3_read':meta,
   'all648_full_state_objects_individually_expanded_or_native_collision_read':False,
   'index_matrices_include210omitted_unknown_not_air':True,
   'F02_Main_images_or_original_source_study':False},
 'written_comparators':comparators,
 'prior_Main_written_judgments_reused_without_source_replay':[
    {'receipt':ref(D/'coordinator-smithy125-F02-whole-review-20261109.json'),
     'reused_comparator_cases':['095F02 internal ladder to branched upper enclosed work/living rooms',
       '097F01 L-shaped mixed ground room/internal ladder/open roof storage terrace',
       '122F01 lower linked hall/under-exterior-stair recess and independent full upper bedroom'],
     'those_old_NBT_or_PNG_reread_this_turn':False,'new_credit':0}],
 'whole_spatial_judgment':[
  'One whole narrow civilian craft shop: west lower entrance opens into a longitudinal reception/display/store hall; the enclosed south-end core carries a continuous compact turning stair, which exits sideways at the intermediate work level into a nearly full-length covered open-sided upper fletching gallery and continues to a small higher fenced landing. The functional split between lower reception/storage, upper work gallery and the stair continuing past its side exit is the studied design.',
  '071F01 has a straight internal stair from the armorer hall to an upper multi-bed living floor.115F01 uses a straight three-step indoor stair in a transverse hall/low side hot-work wing/enclosed side yard organization.126 places the repeated-turn compact stair at the end of a narrow longitudinal shop and releases it into the side of the work gallery, rather than simply changing material or stair direction in those plans.',
  '087F02 splits the bottom into two mutually unconnected shops with an external straight climb to only a partial upper dwelling.126 has one connected lower hall and an internal continuous climb servicing the upper gallery, with no bedroom or separate second shop.',
  '123F01/097F01 use straight internal ladders from a long/L hall to an open small pavilion/roof terrace plus side yard;126 is stair circulation embedded in the end core, side exit to a long gallery, then continued climb to a restricted high landing. Not accepted merely for adding another fletching table, roof cap, target block or height. The complete related civilian work/reception organization supports one studied instance.',
  'No furnace/anvil/lava, operational shooting range, named Dynasty NPC behavior or original task payment/getting-item evidence exists in this study. Relatedness is craft-shop spatial planning only, not a finished smithing building or game task.'],
 'observations_and_limits':[
  '6x11x13/DV3953;858declared,648stored=435nonair213explicitair,210omitted unknown; no source entities or beds/ladder. Ground floor0/use1, upper gallery top birch slab floor4/use5. Top y8 partial landing and y9 fence/y10 carpet/corner slabs do not make a third fully floored operational storey.',
  'Eight bottom smooth-sandstone steps face west/south/east/north twice. Full-block corner landings and intermediate exit4,4,8 with4,5/6,8air are original coordinates, not collision or NPC path tests. Existing roofs/slab undercuts/headroom/stair-turn clearance remain untested.',
  'Lower x2/3,y1/2,z2..7 are the long hall clearance. East chairs, fence, pressure plates and lantern are not general air. The three seeded chest blocks include one double pair at2,3,z6/7, not three shops or three independently obtained rewards.',
  'Upper x2..4,y4,z1..7 are top birch slabs; fletching table3,5,1 occupies its north end. Side y6 is mostly open air with middle fence posts, so the upper gallery is not an enclosed bedroom. Main roof birch bottom slabs at8 cover this long gallery; the south stair top has a separate low fence/cap finish.',
  'Targets2/3,1,11 remain behind the lower stair section and3,7,1 is above the upper north table, allpower0. No three verified shooting lanes, NPC aim/line-of-sight or safe projectiles claimed. Lower rear targets are not rooms.',
  'Unique west-facing original closed jungle door1,1/2,2 and entrance jigsaw0,1,2 empty/finalstructure_void do not prove street attachment. Full sandstone base in x1..5 and partial x0/sand edge do not establish native terrain support at a Dynasty mountain foot.',
  'Exact desert houses pool selection weight2/single/rigid/empty processor is present. Root size6/max80/start0/WORLD_SURFACE_WG/beardthin/expansiontrue and town-center weights are contextual, not measured house spawn probability. Zombie town processors are not applied to this selected house. Single-Jar missing vanilla loot/biome/zombieprocessor does not prove environment absence. Pack metadata/DV3953 does not prove current1.20.1/native compatibility.',
  'Generic full-cell projections are classification diagrams, not native original textured rendering/geometry. No copying authors original assets or early new building production before applicable1000 complete related references.',
  '125F02first126 received exactlyonce and pending removed;120first122/122first124 remain only carry0. Original125 stays sealed. Preserve111 four posts y1..3,115trapdoor/torch,118DV and125partialpartition/lowtarget/noexactpool/correctslabspace corrections. Current snowyF02 is author bounded0, not independently Main visual reviewed.'],
 'new_related_whole_COD3_reference':1,'new_COD4_whole_building_credit':0,
 'global_or_other_reference_credit':0,'first_author_carry_required_exactly_once':True,
 'whole_dataset_cumulative_total_inferred':False,'production_changes':0,
 'native_acceptance':False,'game_starts':0,'checklist_deletions':0,
 'all_tasks_complete':False,'actual_active_hours_claimed':None}
assert len(review['actual_Main_reading']['all5_original_block_entities_read'])==5
target=D/'coordinator-smithy126-F01-whole-review-20261109.json'
with target.open('x') as f:json.dump(review,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'receipt':ref(target),'actual_Main_PNG':9,'new_related_COD3_reference':1,
 'new_COD4':0,'native_acceptance':False,'production':0}))

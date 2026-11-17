"""Record completed Main whole spatial study, not game-task completion."""
import hashlib
import importlib.util
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path('/Users/a15356015027/Desktop/dynasty')
B=ROOT/'docs/architecture/research-20261104-smithy-142'
S=ROOT/'docs/architecture/research-20261104-smithy-141'
OUT=ROOT/'docs/cod4/audit-20261022/coordinator-smithy141-F01-142-whole-review-20261110.json'
assert not OUT.exists()
def load(p):return json.loads(p.read_text())
def sha(v):return hashlib.sha256(v).hexdigest()
def bind(p):
    v=p.read_bytes()
    return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'sha256':sha(v),'bytes':len(v)}
assert bind(B/'RECEIPT.json')['sha256']=='6505462602be33983a7212b92c054777c66bd875d0357f9fb880fe22cc118ad4'
receipt=load(B/'RECEIPT.json')
for f in receipt['files']:
    now=bind(Path(f['path']))
    assert now['sha256']==f['sha256'] and now['bytes']==f['bytes']
c=load(S/'raw-source-audit.json')['candidates'][0]
spec=importlib.util.spec_from_file_location('shared_readonly_decoder',ROOT/'tools/architecture/nbt_read.py')
nbt=importlib.util.module_from_spec(spec);spec.loader.exec_module(nbt)
assert bind(Path(c['source_archive']))['sha256']==c['source_archive_sha256']
with zipfile.ZipFile(c['source_archive']) as z:raw=z.read(c['member'])
assert sha(raw)==c['nbt_sha256'];d=nbt.read(raw)
assert d==c['nbt_decoded_original'] and d['size']==[17,40,17] and d['DataVersion']==3578
assert len(d['palette'])==135 and len(d['blocks'])==4263 and d['entities']==[]
states={tuple(x['pos']):d['palette'][x['state']] for x in d['blocks']}
indexes={tuple(x['pos']):x['state'] for x in d['blocks']}
assert len(indexes)==4263
assert sum(v['Name']=='minecraft:air' for v in states.values())==2319
assert len(states)-2319==1944 and 17*40*17-len(states)==7297
assert max(y for x,y,z in states)==16
assert all((x,y,z) not in states for y in range(17,40) for z in range(17) for x in range(17))
# Exact reconstruction checks the lossless index actually read; no new design credit.
index={};current=None
for line in (B/'original-layer-index-runs.txt').read_text().splitlines():
    if line.startswith('Y='):current=int(line.split(';')[0].split('=')[1])
    elif current is not None and line and line[0].isdigit():
        z,encoded=line.split(':',1);x=0
        for token in encoded.split(','):
            if ':' in token:value,length=token.split(':');length=int(length)
            else:value,length=token,1
            for dx in range(length):index[(x+dx,current,int(z))]=None if value=='-' else int(value)
            x+=length
        assert x==17
assert len(index)==11560
assert all(v==indexes.get(pos) for pos,v in index.items())
route=load(B/'route-state-evidence.json')
for items in route.values():
    for item in items:
        pos=tuple(item['pos']);assert item['omitted']==(pos not in states)
        if pos in states:assert item['state']==states[pos]
blockentities=[x for x in d['blocks'] if 'nbt' in x]
assert len(blockentities)==14
assert states[(7,2,5)]['Name']=='minecraft:oak_stairs' and states[(7,2,5)]['Properties']['half']=='top'
assert states[(3,3,9)]['Name']=='minecraft:spruce_trapdoor' and states[(3,3,9)]['Properties']['open']=='true'
assert {v['Name'] for v in d['palette'] if 'candle' in v['Name']}=={'minecraft:red_candle'}
images=[S/f'F01-{s}.png' for s in ['whole','cutaway','vertical','y0','y2','y4','y6','y8','y10','y12','y14','y16']]
comparators=[]
for batch,cid,judgment in [
 ('070','F02','Earlier single-side external turning stair reaches raised sleeping/storage room over a low hot-work recess. Current east twin entry/public hall and internal folded ascent to open-side storage hall is a different whole organization; warmth or timber alone is not novelty.'),
 ('087','F02','Earlier two disconnected ground shops have independent east doors and external stair only to southern sleeping room. Current ground public dining/preparation hall remains shared and internal staircase leads to one central upper hall opening toward north/south storage recesses, not two separate shops plus one bedroom.'),
 ('115','F01','Earlier west low hot wing/east fenced animal yard and short internal straight stair to enclosed upper cold workshop. Current east entry wing, shared downstairs public hall, western folded staircase and upper open-side storage alcoves under cross-gabled roof differ as one whole; smoker/crafting-table swaps alone count0.'),
 ('134','F02','Earlier ground reading room/internal stair/upper north cartography room with separate door and covered west terrace. Current central upper hall branches through open north/south passages into paired storage recesses, no separate work-room door or west terrace; folded stairs and covered second floor already old0.'),
]:
    p=ROOT/f'docs/architecture/research-20261104-smithy-{batch}/manual-review.json'
    case=next(x for x in load(p)['cases'] if x['id']==cid)
    fields={k:case[k] for k in ['observations','screening_observations','whole_boundary','semantic_family_comparison','saved_written_comparisons'] if k in case}
    comparators.append({**bind(p),'case':cid,'complete_selected_saved_fields_read':fields,'Main_whole_comparison':judgment,'old_images_or_NBT_replayed':False,'extra_credit':0})
findings=[
 'Accept one complete related civilian workshop spatial design for COD3 NPC01: projecting east entry wing with opposing north/south doors feeds a common ground public dining/preparation hall; western internal folded stair rises to central upper hall with open north/south storage alcoves beneath a coordinated cross-gabled roof. This is one whole arrangement, not door/room/stair/storage/chest/components counted separately.',
 'Actually viewed12 original141 PNGs (whole4rotations, cutaway, both vertical sections and y0..16 paired planes). All135palette entries and all40lossless original planes read; upper17..39 entirely omitted, not original air or floors. Source17x40x17 means11560declared positions,4263stored=1944nonair+2319explicitair and7297omitted. Bounding-box height is not40storeys.',
 'Source bytes independently extracted from fixed Terralith archive and entire decoded original compared with saved audit using existing shared read-only decoder. This is integrity verification, not independently implemented parser or additional building/source credit. All14blockentities and entities[] actually read.',
 'Lower hall northern preparation zone has two unlit empty smokers with CookTime/BurnTime/CookTimeTotal0 and no recipes; southern zone contains seating. No anvil/lava/quenching/working smithy or actual customer service follows from these static fixtures. Relevance is public/work/storage layering, not complete blacksmith process.',
 'East wing entry actual north-facing left/open oakdoor at13,2/3,5 and south-facing right/open oakdoor at13,2/3,11 sit above bottom cobblestone outside steps13,1,4/12. The east central15,3,8 position is green glass pane, not a straight exterior through-door. Road socket16,1,14 east_up finalair does not prove generated road continuity or terrain placement.',
 'Ground route hall5,2/3,7 via4,2/3,7 and3,2/3,7/8 reaches west stair. First bottom south stair3,2,9 has east/open/bottom spruce trapdoor3,3,9, not air. Turning planks3/2,2,10 then north bottom steps2,3,9 ->2,4,8 ->2,5,7 and landing2/3,5,6 lead to south return3,6,7 ->3,7,8 ->top/north landing3,7,9 then upper4/5,7,9. Thin state/half/slab geometry retained; no native collision, headroom or NPC passage guarantee.',
 'Upper use8 over spruce floor7 opens atx6/7,z5 andz11 with explicit two-high air into north/south recesses. Eight chest blockentities form four left/right pairs (x4/9 atz3/4 and12/13) sharing upper loot table but preserving all8seeds; not eight rooms, eight separate designs or eight rewards. No inner doors mean no claimed sealed private bedrooms.',
 'Lower north-facing chest7,1,5 has top/south oak stair7,2,5 directly above; do not replace this with air or claim tested lid access. Own lower tavern_downstairs seed8818157813776627923 and eight upstairs seeds remain exact rawsource. Loot tables are references, not loaded loot results, paid materials, inventories or quest receipts.',
 'Three crafting tables support upper/east-side cold work; wooden framing, low stone/tuff/cobble base, green panes and stair/slab roof states organize scale and enclosure. Red candle palette107 is three unlit candles, unlike prior138 orange candle; no conflation or color-reference credit. Smoke-column/chimney top16 is not proof of firing or exhaust.',
 'Two up_south villager sockets use minecraft:village/plains/villagers finalair at11,2,8 and7,8,8. entities[] means no stored real NPC here; sockets, source profession title and static workstations do not prove generated NPC count or task functionality.',
 'Four selected complete old written spatial judgments actually read and compared with exact source bindings. Previous source/images behind those judgments not replayed; whole-family uniqueness is scoped to those comparisons, not a claim that all previous/global designs were semantically reread or absent.',
 'Whole141 source and142deepening are the same NBT472a9407; accept only one first reference total for this source. No new142design, layer/rotations/screens/roof/door/room credits. Preserve sealed141/142 and later143; next unsealed author batch must carry complete Main judgment in admissions/resolved exactly once.',
 'All15 declared142files verified unchanged; authorverification count is not Main semantic count. Twelve viewed PNGs are category-colored full-cell approximations, not actual game textures/meshes. Eleven upper paired PNGs18..38 not viewed; all their original omitted states were actually read in lossless index and extracted original, no filled-air invention.',
 'No current jigsaw pool/processor/root-generation/loot context source reading added here; context/collision/terrain/fire/service pathfinding/current compatibility/runtime remain unverified. Study principles only; no copying source asset, new building production, COD4building-ledger increment, native/game-task acceptance or checklist deletion.1000gate not met.'
]
report={
 'recorded_at':datetime.now(timezone.utc).isoformat(),'reviewer_thread':'01a16364-cac0-7ca2-a042-a5312781ca34','author_thread':'01a12515-f16a-7be3-b79a-bd5500f7ccd4',
 'decision':'ACCEPT_ONE_COMPLETE_RELATED_COD3_NPC01_SPATIAL_REFERENCE_NOT_GAME_TASK',
 'source_receipt':bind(B/'RECEIPT.json'),'source':{k:c[k] for k in ['source_archive','source_archive_sha256','member','nbt_sha256','size','DataVersion','air','nonair']},
 'actual_Main_reading':{'source_images_viewed':[bind(p) for p in images],'palette_entries_read':135,'original_layers_read':list(range(40)),'all_blockentities_read':14,'entities':[],
 'decoded_source_equality':True,'lossless_index_all_cells_equal_original':True,'original_route_items_verified':sum(map(len,route.values())),
 'decoder_existing_shared_utility':bind(ROOT/'tools/architecture/nbt_read.py'),'source_context_not_newly_read':True,
 'source_bindings':[bind(S/'raw-source-audit.json'),bind(S/'manual-review.json')]+[bind(B/f) for f in ['original-palette.json','original-layer-index-runs.txt','route-state-evidence.json','complete-study-review.json']]},
 'written_comparators':comparators,'independent_observations_and_limits':findings,
 'whole_spatial_judgment':{'credit':1,'unit':'one entire related civilian workshop design, same141F01source deepened142','scope':'COD3 NPC01 spatial study only'},
 'new_related_whole_COD3_reference':1,'new_COD4_whole_building_credit':0,'global_or_other_reference_credit':0,
 'first_author_carry_required_exactly_once':True,'sealed_author_batches_unchanged':True,'cumulative_total_not_inferred_or_reset':True,
 'production_changes':0,'native_acceptance':False,'game_starts':0,'checklist_deletions':0,'active_hours_claimed':None,
 'read_failure_limit':'One comparator discovery expected screening_observations on older schema and failed after source/route output. All four schema-specific complete spatial judgment fields recovered in subsequent bounded output; no incomplete comparator credited. Receipt prewrite verification first rejected singleton run tokens, then an invented palette filename; corrected from actual format/file inventory. No receipt or production written on failures; successful complete original equality is integrity only.'
}
with OUT.open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(bind(OUT)))

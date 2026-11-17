"""Recheck actual source, UV samples and review accounting. No production writes."""
from pathlib import Path
from contextlib import ExitStack
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import zipfile
from PIL import Image
from check_faces import cube_faces, face_edges

D=Path(__file__).resolve().parent
R=D.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()

def main():
    baseline=read(D/'source-baseline.json')
    changed=[p for p,h in baseline.items() if not (R/p).is_file() or sha(R/p)!=h]
    errors=[{'kind':'source_changed_since_frozen_review','path':p} for p in changed]
    assert len(baseline)==289
    receipt=read(next(D.glob('texture-requirements-receipt-*.json')))
    rule=R/'docs/art/USER_TEXTURE_REQUIREMENTS.md'
    assert sha(rule)==receipt['sha256']==sha(R/receipt['snapshot'])
    assert rule.read_bytes()==Path('/Users/a15356015027/.codex/user-preferences/texture-requirements.md').read_bytes()
    assert len(receipt['targets'])==len(set(receipt['targets']))==56
    inv=read(D/'face-and-seam-inventory.json');faces=0;edges=0;regions=set()
    assert len(inv['entries'])==56 and not inv['errors']
    for row in inv['entries']:
        p=R/row['path']
        if sha(p)!=row['sha256']:errors.append({'kind':'stale_atlas_inventory','path':row['path']});continue
        image=Image.open(p).convert('RGBA');assert image.size==(64,32)
        for part in row['parts']:
            reference={f['direction']:f for f in cube_faces(part['part'])}
            actual_edges=face_edges(list(reference.values()))
            assert len(part['faces'])==6 and len(part['seams'])==12
            for f in part['faces']:
                source=reference[f['direction']]
                assert f['uv_corners']==[list(v) for v in source['uv']]
                assert f['model_corners']==[list(v) for v in source['xyz']]
                assert f['normal']==source['normal']
                x0,y0,x1,y1=f['crop'];assert 0<=x0<x1<=64 and 0<=y0<y1<=32
                pixels=list(image.crop((x0,y0,x1,y1)).get_flattened_data())
                assert f['total_pixels']==len(pixels)
                assert f['visible_pixels']==sum(p[3]>=26 for p in pixels)
                assert f['fully_transparent']==(f['visible_pixels']==0)
                regions.add((row['path'],tuple(f['crop'])));faces+=1
            for s in part['seams']:
                ep=tuple(tuple(v) for v in s['xyz_endpoints'])
                assert ep in actual_edges
                assert {s['face_a'],s['face_b']}=={x[0]['direction'] for x in actual_edges[ep]}
                a=[list(image.getpixel(tuple(x))) for x in s['texels_a']]
                b=[list(image.getpixel(tuple(x))) for x in s['texels_b']]
                assert a==s['rgba_a'] and b==s['rgba_b'] and len(a)==len(b)==s['length']
                assert s['alpha_disagreement']==sum((x[3]>=26)!=(y[3]>=26) for x,y in zip(a,b))
                assert s['both_visible']==sum(x[3]>=26 and y[3]>=26 for x,y in zip(a,b))
                edges+=1
    assert (faces,edges,len(regions))==(1680,3360,1176)
    mirrors=read(D/'mirror-correspondence.json')
    assert mirrors['count']==len(mirrors['checks'])==84
    assert all(x['north_faces_exact_horizontal_mirror'] for x in mirrors['checks'])
    selections=read(D/'seam-review-selection.json')['seams']
    assert len(selections)==len({s['key'] for s in selections})==112
    manual=read(D/'manual-review.json')
    assert len(manual['per_material'])==28
    for k,n in [('face_pages_opened',14),('seam_pages_opened',7),('mirror_pages_opened',4),('icon_match_pages_opened',3)]:
        assert len(manual[k])==n and all((D/p).is_file() for p in manual[k])
    f=read(D/'findings.json')
    assert f['protected_inventory_icons']==112
    assert f['protection_categories']=={'selected_original_icons':52,'fine_old_icons':20,'historically_redrawn_v15_icons':40}
    assert len(f['orphan_caps'])==10 and Counter(x['material'] for x in f['orphan_caps'])==dict.fromkeys(['bamboo','brocade','cloth','leather','sea_silk'],2)
    seam_map={s['key']:s for r in inv['entries'] for p in r['parts'] for s in p['seams']}
    for cap in f['orphan_caps']:
        assert cap['cap_crop']==[48,16,52,20] and cap['cap_visible']==cap['cap_pixels']==16
        for key in cap['edge_keys']:
            s=seam_map[key];assert s['alpha_disagreement']==s['length'] and s['both_visible']==0
    assert {x['material'] for x in f['whole_canvas_worn_sets']}=={'bronze','general','jade','sky','xuantian'}
    assert all(x['layer2_body_north_row_visible']==[8]*12 for x in f['whole_canvas_worn_sets'])
    assert f['new_artwork']==f['checklist_deletions']==0 and not f['game_acceptance']
    waist=read(D/'waist-coverage-review.json')
    assert len(waist['rows'])==28 and waist['waist_source_v_range']==[28,32]
    assert Counter(x['classification'] for x in waist['rows'])=={'WHOLE_TORSO_OLD_PATTERN':5,'BOTTOM_FOUR_MODEL_ROWS_WAIST_CORRESPONDENCE_CONFIRMED':23}
    contract=read(D/'uv-contract.json')
    refs=read(D/'reference-variants-provenance.json');review=read(D/'reference-variant-review.json')
    assert sha(R/refs['source'])==refs['source_sha256']
    controls=read(D/'vanilla-control-provenance.json')
    assert controls['review_page_opened']=='vanilla-controls-review.png'
    assert (D/controls['review_page_opened']).is_file()
    old=read(R/'docs/art/armor-continuation-20261102/armor-reference-provenance.json')
    old_review=read(R/'docs/art/armor-continuation-20261102/reference-review.json')
    with ExitStack() as stack:
        cache={}
        def zip_bytes(jar,entry):
            if jar not in cache:cache[jar]=stack.enter_context(zipfile.ZipFile(jar))
            return cache[jar].read(entry)
        for source in contract['sources'].values():
            assert sha(Path(source['jar']))==contract['jar_sha256']
            assert digest(zip_bytes(source['jar'],source['entry']))==source['sha256']
        for row in controls['rows']:
            assert sha(D/row['local'])==row['sha256']==digest(zip_bytes(row['jar'],row['entry']))
        for provenance,folder in [(refs,D),(old,R/'docs/art/armor-continuation-20261102')]:
            for row in provenance['cases']:
                for a in row['assets']:
                    assert sha(folder/a['local'])==a['sha256']==digest(zip_bytes(a['jar'],a['entry']))
    assert len(refs['cases'])==57 and sum(len(c['assets']) for c in refs['cases'])==194
    flat=[c for g in review['observations'] for c in g['cases']]
    assert len(flat)==len(set(flat))==57 and set(flat)=={x['case_key'] for x in refs['cases']}
    assert len(review['observations'])==review['conservative_learning_groups']==11
    union_names={x['case_key'] for prov in [refs,old] for x in prov['cases']}
    union_assets={(a['jar'],a['entry'],a['sha256']) for prov in [refs,old] for c in prov['cases'] for a in c['assets']}
    assert len(union_names)==review['combined_reopened_name_families']==75
    assert len(union_assets)==review['combined_unique_archive_payloads']==253
    assert len({a[2] for a in union_assets})==review['combined_unique_png_sha256']
    retained=[g for g in old_review['observations'] if not set(g['cases'])&set(flat)]
    assert len(retained)+len(review['observations'])==review['combined_conservative_learning_groups']==23
    assert review['fresh_global_reference_credit']==0 and not review['production_allowed']
    assert len(review['pages_opened'])==8 and all((D/p).is_file() for p in review['pages_opened'])
    received=read(D/'attachment-handoff-received.json');handoff=read(R/received['source'])
    assert sha(R/received['source'])==received['source_sha256']
    assert len(received['entries'])==len(handoff['entries'])==2
    for entry,raw in zip(received['entries'],handoff['entries']):
        assert entry['native_item_id']=='UNCONFIRMED_EXISTING_MODEL_PROP_NOT_A_NEW_REGISTERED_ITEM'
        for p,h in entry['input_hashes'].items():assert sha(R/p)==h
        geo=next(p for p in raw['inputs'] if p.endswith('.geo.json'))
        bone=next(b for b in read(R/geo)['minecraft:geometry'][0]['bones'] if b['name']==entry['attachment_bone'])
        assert bone==raw['attachment_bone_raw'] and bone['parent']=='right_hand'
    result={'checked_at':datetime.now(timezone.utc).isoformat(),
       'status':'PASS_EVIDENCE_WITH_OPEN_ART_FINDINGS' if not errors else 'SOURCE_OR_EVIDENCE_REVIEW_REQUIRED',
       'baseline_paths':len(baseline),'armor_resource_paths':280,'java_readonly_paths':2,'prop_body_resource_paths':6,'handoff_doc_paths':1,
       'source_unchanged':not changed,'changed_paths':changed,'errors':errors,
       'source_png':56,'geometry_face_instances':faces,'distinct_source_face_regions':len(regions),
       'edge_pairs':edges,'manual_priority_edges':112,'mirror_correspondences':84,
       'orphan_cap_instances':10,'whole_mask_torso_families':5,'approved_material_mismatch_priorities':3,
       'reviewed_reference_png_this_scope':194,'reviewed_name_families_this_scope':57,
       'combined_reopened_png':253,'combined_name_families':75,'combined_conservative_learning_groups':23,
       'vanilla_controls':4,'fresh_global_reference_credit':0,'independent_1000_reference_gate_met':False,
       'requirements_sha256':receipt['sha256'],'production_texture_changes':0,'new_artwork':0,
       'game_starts':0,'game_acceptance':False,'checklist_deletions':0,
       'limits':['PASS applies to evidence/source preservation, not acceptance of the open art findings.',
                 'Undeformed local face/edge/UV review does not cover posed joints, renderer lighting or third-party overrides.',
                 'No new artwork before the independent-reference gate; no item ID invented for embedded props.']}
    (D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))
    assert not errors

if __name__=='__main__':main()

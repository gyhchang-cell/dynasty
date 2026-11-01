"""Evidence consistency only; never an automatic visual-quality or study-credit judge."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from PIL import Image, ImageOps

D=Path(__file__).resolve().parent
R=D.parents[3]
errors=[];viewed=0;proposals=0;assets=0;batch_summary=[]
archive_hashes={}
for path in sorted(D.glob('review-batch-*.json')):
    doc=json.loads(path.read_text());actual_proposals=0;actual_pngs=0
    for row in doc['rows']:
        actual_proposals+=row['distinct_family_proposed_credit']
        sheet=row.get('inspected_detail_view',row.get('inspection_sheet'))
        if sheet and not (R/sheet).is_file():errors.append('Missing sheet: '+sheet)
        for asset in row.get('assets',[row]):
            p=R/asset['local_path'];actual_pngs+=1
            if not p.is_file():errors.append('Missing PNG: '+str(p));continue
            data=p.read_bytes()
            if hashlib.sha256(data).hexdigest()!=asset['sha256']:errors.append('PNG SHA mismatch: '+str(p))
            if asset.get('git_blob_sha'):
                h=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                if h!=asset['git_blob_sha']:errors.append('Git blob mismatch: '+str(p))
            if asset.get('jar') and asset.get('jar_sha256'):
                jar=asset['jar']
                if jar not in archive_hashes:
                    archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
                if archive_hashes[jar]!=asset['jar_sha256']:errors.append('Archive changed: '+jar)
            if asset.get('rgba_sha256'):
                rgba=Image.open(p).convert('RGBA')
                if hashlib.sha256(rgba.tobytes()).hexdigest()!=asset['rgba_sha256']:errors.append('Decoded RGBA mismatch: '+str(p))
            Image.open(p).verify()
    if actual_pngs!=doc['viewed_pngs']:errors.append('Batch viewed count mismatch: '+path.name)
    if actual_proposals!=doc['proposed_distinct_design_families']:errors.append('Batch family sum mismatch: '+path.name)
    if doc['coordinator_accepted_new_visual_credit']!=0 or doc['production_gate_met'] is not False:errors.append('Unauthorized credit/gate claim: '+path.name)
    viewed+=actual_pngs;proposals+=actual_proposals
    batch_summary.append({'batch':path.name,'pngs_opened':actual_pngs,'proposed_families':actual_proposals})
for model in json.loads((D/'uv-model-supplement.json').read_text())['rows']:
    if hashlib.sha256((R/model['path']).read_bytes()).hexdigest()!=model['sha256']:errors.append('Model SHA mismatch: '+model['path'])
prior_opened=0
for name in ['prior-case-semantic-review.json','prior-batch07-semantic-review.json','prior-batch11-semantic-review.json']:
    prior=json.loads((D/name).read_text())
    for row in prior['rows']:
        if row.get('accepted_credit')!=0:errors.append('Prior reuse improperly credited: '+row['case'])
        if 'prior_local_png' in row:
            prior_opened+=1
            if hashlib.sha256((R/row['prior_local_png']).read_bytes()).hexdigest()!=row['prior']['sha256']:errors.append('Prior PNG changed: '+row['case'])
            if not (R/row['comparison_sheet']).is_file():errors.append('Prior sheet missing: '+row['case'])
            if not row.get('observation_zh'):errors.append('Missing manual prior observation: '+row['case'])
            jar=row['prior']['jar']
            if jar not in archive_hashes:archive_hashes[jar]=hashlib.sha256(Path(jar).read_bytes()).hexdigest()
            if archive_hashes[jar]!=row['prior_jar_sha256']:errors.append('Prior archive changed: '+row['case'])
bindings=json.loads((D/'current-weapon-uv-bindings.json').read_text())
for row in bindings['rows']:
    for key in ['model','png']:
        if hashlib.sha256((R/row[key]).read_bytes()).hexdigest()!=row[key+'_sha256']:errors.append('Current binding source changed: '+row[key])
uv_crops=json.loads((D/'uv-layer-crops.json').read_text())
uv_review=json.loads((D/'uv-layer-manual-review.json').read_text())
if set(uv_crops['sheets'])!={r['sheet'] for r in uv_review['rows']}:errors.append('UV layer review sheet coverage mismatch')
if uv_review['new_accepted_visual_credit']!=0 or uv_review['production_changes']!=0:errors.append('Unauthorized UV crop credit')
sample_count=0;zero_count=0
for row in uv_crops['rows']:
    for kind in ['model','texture']:
        if hashlib.sha256((R/row[kind]).read_bytes()).hexdigest()!=row[kind+'_sha256']:errors.append('UV source changed: '+row[kind])
    if not (R/row['inspection_sheet']).is_file():errors.append('Missing UV crop sheet: '+row['inspection_sheet'])
    im=Image.open(R/row['texture']).convert('RGBA')
    for face in row['faces']:
        if face['status']!='SIGNED_INTEGER_CROP':
            zero_count+=1
            if not 0 in face['uv_size']:errors.append('Unsampled nonzero UV face: '+str(face))
            continue
        sample_count+=1
        patch=im.crop(list(map(int,face['bounds'])))
        if face['flip_u_for_sample']:patch=ImageOps.mirror(patch)
        if face['flip_v_for_sample']:patch=ImageOps.flip(patch)
        if hashlib.sha256(patch.tobytes()).hexdigest()!=face['crop_rgba_sha256']:errors.append('UV crop pixel mismatch: '+row['bone'])
if sample_count!=uv_review['integer_nonzero_face_crops'] or zero_count!=uv_review['zero_area_faces_not_resampled']:errors.append('UV crop count mismatch')
alpha_edges=json.loads((D/'current-weapon-alpha-edge-correspondence.json').read_text())
for row in alpha_edges['rows']:
    for key in ['model','png']:
        if hashlib.sha256((R/row[key]).read_bytes()).hexdigest()!=row[key+'_sha256']:errors.append('Alpha edge source changed: '+row[key])
    for key in ['missing_segments','extra_segments','duplicate_segments','unmapped_geometry','side_uv_wrong_owner_pixel','side_uv_spans_multiple_png_texels']:
        if row[key]:errors.append('Alpha edge correspondence unresolved: '+row['model']+' '+key)
if alpha_edges['source_cutout_rule']['minimum_byte_alpha_at_full_modulation']!=26:errors.append('Unexpected alpha rule')
layer_binding=json.loads((D/'arctic-item-layer-binding.json').read_text())
for row in layer_binding['rows']:
    if hashlib.sha256((R/row['model_local_path']).read_bytes()).hexdigest()!=row['model_sha256']:errors.append('Arctic binding JSON changed')
    for src in row['source_pngs']:
        if hashlib.sha256((R/src['local_path']).read_bytes()).hexdigest()!=src['sha256']:errors.append('Arctic item layer changed')
layer_review=json.loads((D/'arctic-layer-manual-review.json').read_text())
if not (R/layer_review['inspection_sheet']).is_file() or layer_review['new_equipment_credit']!=0:errors.append('Arctic layer evidence invalid')
register=json.loads((D/'semantic-applicability-register.json').read_text())
if register['original_stage_family_proposal_sum']!=proposals:errors.append('Stale stage proposal total in register')
if register['accepted_new_visual_credit']!=0 or register['production_gate_met'] is not False:errors.append('Unauthorized register acceptance')
for scope in register['scope_contribution']:
    if scope['original_threshold']!=1000 or scope['production_gate_met'] is not False or scope['new_accepted_visual_credit']!=0:errors.append('Scope gate changed: '+scope['scope'])
changed=[]
for a in json.loads((D/'production-baseline.json').read_text())['rows']:
    assets+=1
    if not (R/a['path']).is_file() or hashlib.sha256((R/a['path']).read_bytes()).hexdigest()!=a['sha256']:changed.append(a['path'])
# Shared-workspace changes are reported without assuming authorship or undoing them.
result={'checked_at':datetime.now(timezone.utc).isoformat(),'evidence_consistency':'PASS' if not errors else 'FAIL',
    'batches':batch_summary,'pngs_opened_including_exclusions':viewed,'proposed_families_pending_semantic_review':proposals,
    'formal_new_credit':0,'production_gate_met':False,'protected_source_paths':assets,
    'prior_icons_reopened_separately_not_new_credit':prior_opened,'local_archives_verified':len(archive_hashes),
    'current_weapon_model_states_checked':len(bindings['rows']),
    'reference_uv_models_flat_island_study':uv_crops['models'],'reference_uv_cubes_flat_island_study':len(uv_crops['rows']),
    'reference_uv_signed_nonzero_face_crops':sample_count,'reference_uv_zero_area_faces_not_resampled':zero_count,
    'current_weapon_cutout_boundary_segments_checked':sum(r['expected_nonzero_alpha_boundary_segments'] for r in alpha_edges['rows']),
    'supplementary_arctic_source_item_pngs_opened_not_new_cases':layer_review['source_pngs_opened'],
    'protected_paths_changed_since_baseline':changed,'errors':errors,
    'limits':'Hashes/counts verify evidence only, never quality, unique semantic examples, manual viewing, elapsed active hours, runtime or task completion.'}
(D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(bool(errors))

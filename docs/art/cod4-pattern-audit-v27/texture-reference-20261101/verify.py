"""Evidence consistency only; never an automatic visual-quality or study-credit judge."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from PIL import Image

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
for name in ['prior-case-semantic-review.json','prior-batch07-semantic-review.json']:
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
    'protected_paths_changed_since_baseline':changed,'errors':errors,
    'limits':'Hashes/counts verify evidence only, never quality, unique semantic examples, manual viewing, elapsed active hours, runtime or task completion.'}
(D/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(bool(errors))

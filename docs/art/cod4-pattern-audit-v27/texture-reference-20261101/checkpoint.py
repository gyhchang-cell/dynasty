"""Write this specialty's checkpoint only; never edit shared coordinator ledgers."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
D=Path(__file__).resolve().parent
v=json.loads((D/'verification.json').read_text());assert v['evidence_consistency']=='PASS'
assert not v['protected_paths_changed_since_baseline']
p=json.loads((D/'progress.json').read_text());now=datetime.now(timezone.utc)
deadline=datetime.fromisoformat(p['window']['deadline_utc'])
direct=(D/'direct-continuation-authority.json').is_file()
s=json.loads((D/'semantic-applicability-register.json').read_text())
raw=v['pngs_opened_including_exclusions'];families=v['proposed_families_pending_semantic_review']
historical=s['historically_reused_equipment_family_names']
ids=[int(r['reference_id'].split('-')[1]) for path in D.glob('review-batch-*.json')
     for r in json.loads(path.read_text())['rows'] if r.get('reference_id','').startswith('VIS-')]
next_id=max(ids)+1;next_batch=len(v['batches'])+1
p.update(updated_at=now.isoformat(),status='REFERENCE_STUDY_IN_PROGRESS_NOT_TASK_COMPLETE',
    latest_batches=[r['batch'] for r in v['batches']],pngs_opened_including_exclusions=v['pngs_opened_including_exclusions'],
    proposed_design_families_pending_review=v['proposed_families_pending_semantic_review'],formal_new_visual_credit=0,
    prior_icons_reopened_separately_not_new_credit=v['prior_icons_reopened_separately_not_new_credit'],
    historically_reused_equipment_families=historical,signed_face_sample_sheets=3,
    expanded_reference_uv_layer_sheets=14+v['extension_reference_uv_sheets'],
    expanded_reference_uv_models=v['reference_uv_models_flat_island_study']+v['extension_reference_uv_models'],
    expanded_reference_uv_cubes=v['reference_uv_cubes_flat_island_study']+v['extension_reference_uv_cubes'],
    expanded_reference_uv_nonzero_faces=v['reference_uv_signed_nonzero_face_crops']+v['extension_reference_uv_signed_face_crops'],
    current_weapon_cutout_boundary_segments_checked=10628,supplementary_arctic_item_source_pngs=8,
    supplementary_held_item_source_pngs=v['supplementary_held_source_item_pngs_opened_not_new_cases'],
    local_archives_verified=v['local_archives_verified'],exact_local_archive_entry_payloads_checked=v['exact_local_archive_entry_payloads_checked'],
    protected_resources_unchanged=True,production_changes=0,game_starts=0,todo_deletions=0,todo_backups=0,
    verification_sha256=hashlib.sha256((D/'verification.json').read_bytes()).hexdigest(),
    handoff_status='DIRECT_WORK_IN_PROGRESS_NOT_COMPLETE' if direct else ('LOCAL_CHECKPOINT_WINDOW_STILL_ACTIVE_NOT_COMPLETE' if now<deadline else 'DEADLINE_REACHED_LOCAL_CHECKPOINT'),
    last_action=f'Actual local source study through batch{next_batch-1}: {raw} PNGs including exclusions, {families} stage family proposals and {historical} historical reuses. Existing artifact534 signed source crops/192 item-mesh correspondence checks;8workshops12material PNGs/300declared faces not unfolded;4offering originals preserved. No production/main TODO changes.')
p['window']['status']='SUPERSEDED_BY_DIRECT_CONTINUATION' if direct else ('ACTIVE' if now<deadline else 'DEADLINE_REACHED')
p['window']['deadline_applies_to_current_work']=not direct
p['direct_continuation_authority']='direct-continuation-authority.json' if direct else None
p['kimono_signed_face_crops']=v.get('kimono_signed_face_crops',0)
p['expanded_requirement_index']='expanded-texture-uv-requirements.json'
p['expanded_requirement_original_files']=v['expanded_requirement_original_files']
p['expanded_requirement_source_files_changed_since_index']=v['expanded_requirement_source_files_changed_since_index']
for field in ['existing_artifact_source_faces_checked','existing_artifact_item_geo_uv_comparisons',
    'existing_workshop_material_pngs_checked','existing_workshop_declared_faces_not_unfolded',
    'existing_offering_original_pngs_checked']:
    p[field]=v[field]
p['next_steps']=[
    f'Continue pinned local related texture design research only. Next VIS-{next_id:03}/batch{next_batch:02}. No unavailable web quota probes or Java/model/building work.',
    f'Keep six independent1000 gates; {families} stage labels include{historical} old equipment reuses, context and partial motifs. Formal new credit0.',
    'Resolve held proper equipment source/slot cases: Arctic wearable UV/tint; primordial helmet vs whole atlas; Modular Golems monstrosity icon vs Cataclysm player helm are not an accepted pair.',
    'Continue expanded cod1/cod2/cod3/cod4/cod6 texture/UV requirements only. Preserve newer approved creatures, artifacts and offering originals; cod5 absent at read. No quest/program/building work.',
    'Need program-owner evidence for longyin builtin/entity GUI icon route and8workshop GUI material/layout routes. No named PNG is not a functional bug;300omitted face UV fields were not unfolded or game-verified.',
    'No production before applicable threshold. Preserve303 baseline assets, original saves, client, audio/brightness, main prompts and shared Jar.',
    'Direct continuation supersedes the previous13:44:05Beijing cutoff. Continue related local sources and existing pattern/UV checks. Never claim wall time as active hours.' if direct else 'At13:44:05Beijing save/end delegated window with actual remaining evidence; wall time is not five active hours.']
(D/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
receipt={'recorded_at':now.isoformat(),'status':'STAGE_RECEIPT_NOT_FULL_TASK_COMPLETION',
    'continuation_baseline':{'started_utc':'2026-11-01T03:12:33+00:00','raw_pngs':500,'stage_family_names':137,
        'meaning':'Own previously saved progress; totals include exclusions, not accepted cases.'},
    'new_this_continuation':{'raw_pngs_actually_opened':raw-500,'old_icons_reopened_not_new_credit':v['prior_icons_reopened_separately_not_new_credit']-40,
        'additional_stage_family_proposals':families-137,'supplementary_exact_item_source_pngs':4,
        'additional_known_png_uv_models':v['extension_reference_uv_models'],'additional_known_png_uv_faces':v['extension_reference_uv_signed_face_crops'],
        'existing_artifact_signed_source_faces':v['existing_artifact_source_faces_checked'],
        'existing_artifact_item_geo_uv_comparisons':v['existing_artifact_item_geo_uv_comparisons'],
        'existing_workshop_material_pngs':v['existing_workshop_material_pngs_checked'],
        'existing_workshop_declared_faces_not_unfolded':v['existing_workshop_declared_faces_not_unfolded'],
        'existing_offering_original_pngs_preserved':v['existing_offering_original_pngs_checked'],
        'production_changes':0,'todo_deletions':0,'game_starts':0},
    'cumulative':{'raw_pngs_opened_including_exclusions':raw,'stage_family_names':families,
        'historical_equipment_family_reuse':historical,'formal_new_credit':0,
        'prior_icons_reopened_not_new_credit':v['prior_icons_reopened_separately_not_new_credit'],
        'protected_paths_unchanged':v['protected_source_paths']},
    'next_reference':f'VIS-{next_id:03}','next_batch':next_batch,
    'expanded_requirement_original_files':v['expanded_requirement_original_files'],
    'remaining':'Six original1000 gates not met; expanded five-file texture/UV requirements indexed, not completed. Partial material/reference UV crops are not full runtime acceptance. Builtin/entity GUI routing and8machine GUI layouts held for program-owner evidence. Next local checkpoint in progress.json.',
    'window_deadline_beijing':p['window']['deadline_beijing'],'window_still_active':False if direct else now<deadline,'direct_work_active':direct,
    'actual_active_five_hours_claimed':False,'source_scope':'Texture/pattern/UV only; local source evidence. No production, main coordinator/TODO, shared Jar, UI/audio/brightness/world/push changes.'}
(D/'stage-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':p['handoff_status'],'pngs':raw,'stage_family_names':families,'formal_new_credit':0,'historical_window_applies':not direct,'direct_work_active':direct}))

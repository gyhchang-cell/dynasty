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
p.update(updated_at=now.isoformat(),status='REFERENCE_STUDY_IN_PROGRESS_NOT_TASK_COMPLETE',
    latest_batches=[r['batch'] for r in v['batches']],pngs_opened_including_exclusions=v['pngs_opened_including_exclusions'],
    proposed_design_families_pending_review=v['proposed_families_pending_semantic_review'],formal_new_visual_credit=0,
    prior_icons_reopened_separately_not_new_credit=v['prior_icons_reopened_separately_not_new_credit'],
    historically_reused_equipment_families=34,signed_face_sample_sheets=3,expanded_reference_uv_layer_sheets=14,
    expanded_reference_uv_models=3,expanded_reference_uv_cubes=52,expanded_reference_uv_nonzero_faces=270,
    current_weapon_cutout_boundary_segments_checked=10628,supplementary_arctic_item_source_pngs=8,
    protected_resources_unchanged=True,production_changes=0,game_starts=0,todo_deletions=0,todo_backups=0,
    verification_sha256=hashlib.sha256((D/'verification.json').read_bytes()).hexdigest(),
    handoff_status='LOCAL_CHECKPOINT_WINDOW_STILL_ACTIVE_NOT_COMPLETE' if now<deadline else 'DEADLINE_REACHED_LOCAL_CHECKPOINT',
    last_action='Opened188 additional PNGs in batches09-11 plus20 prior icons; recorded52 source UV cubes/270 nonzero face islands;16 current weapon states match10628 cutout boundary segments at alpha26; resolved Arctic omitted item layer but wearable binding held. No production or main TODO changes.')
p['window']['status']='ACTIVE' if now<deadline else 'DEADLINE_REACHED'
p['next_steps']=[
    'Continue pinned local related texture design research only. Next VIS ID469/batch12. Never repeat unavailable web quota probes or cross into Java/model/building work.',
    'Keep six independent1000 gates;137 family labels include34 historical equipment reuses, exclusions/context and partial motifs. No formal new credit granted.',
    'Resolve held proper equipment source/slot cases: Arctic wearable UV/tint; primordial helmet vs whole atlas; Modular Golems monstrosity icon vs Cataclysm player helm are not an accepted pair.',
    'No production before applicable threshold. Preserve303 baseline assets, original saves, client, audio/brightness, main prompts and shared Jar.',
    'At13:44:05Beijing save/end delegated window with actual remaining evidence; wall time is not five active hours.']
(D/'progress.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n')
receipt={'recorded_at':now.isoformat(),'status':'STAGE_RECEIPT_NOT_FULL_TASK_COMPLETION',
    'new_this_continuation':{'raw_pngs_actually_opened':188,'old_icons_reopened_not_new_credit':20,
        'additional_stage_family_proposals':38,'reference_uv_cubes_inspected':52,'reference_uv_signed_nonzero_faces':270,
        'current_weapon_boundary_segments_checked':10628,'supplementary_arctic_source_item_pngs':8,
        'production_changes':0,'todo_deletions':0,'game_starts':0},
    'cumulative':{'raw_pngs_opened_including_exclusions':500,'stage_family_names':137,
        'historical_equipment_family_reuse':34,'formal_new_credit':0,'prior_icons_reopened_not_new_credit':40,
        'protected_paths_unchanged':303},
    'remaining':'Six original1000 gates not met. Partial composition/material and reference UV crops are not full target/runtime acceptance. Next local checkpoint in progress.json.',
    'window_deadline_beijing':p['window']['deadline_beijing'],'window_still_active':now<deadline,
    'actual_active_five_hours_claimed':False,'source_scope':'Texture/pattern/UV only; local source evidence. No production, main coordinator/TODO, shared Jar, UI/audio/brightness/world/push changes.'}
(D/'stage-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':p['handoff_status'],'pngs':500,'stage_family_names':137,'formal_new_credit':0,'window_still_active':now<deadline}))

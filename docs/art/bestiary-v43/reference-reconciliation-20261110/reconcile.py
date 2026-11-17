"""Bounded reconciliation of existing ledgers; no fresh semantic/visual acceptance."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def evidence(rel):
 p=ROOT/rel;return {'path':rel,'sha256':sha(p)}
scopes=[('marshal','items','accepted_for_target'),('taoyan','items','accepted_for_target'),('wing','references','accepted_for_luban_yisha')]
ledgers=[];allids=[]
for name,key,flag in scopes:
 rel='docs/art/bestiary-v43/'+name+'-reference-review.json';d=json.loads((ROOT/rel).read_text());accepted=[r for r in d[key] if r.get(flag)]
 checks=[]
 for r in accepted:
  # Card lookup stays within the original batch directory, never global artwork search.
  if name=='taoyan':p=ROOT/'build/bestiary-v43'/r['batch']/r['card']
  else:p=ROOT/'build/bestiary-v43'/(name+'-reference')/r['card']
  checks.append({'identity':r['identity'],'path':str(p.relative_to(ROOT)),'expected_sha256':r.get('card_sha256'),'exists':p.exists(),'hash_matches':p.exists() and sha(p)==r.get('card_sha256')})
 ids={r['identity'] for r in accepted};allids.extend(ids)
 ledgers.append({'target':d['target'],'source':evidence(rel),'historical_accepted_for_target':d['accepted_for_target'],'historical_required':d.get('required',100),'accepted_rows':len(accepted),'exact_identity_keys':len(ids),'raw_family_labels':len({r.get('family') for r in accepted}),'raw_family_labels_are_not_rig_dedup':True,'viewed_flags':sum(bool(r.get('viewed')) for r in accepted),'observations_present':sum(bool(r.get('observation')) for r in accepted),'binding_kind_histogram':dict(Counter(r.get('binding_kind','not recorded') for r in accepted)),'original_limit':d.get('limits',d.get('qualification')),'cards':checks,'not_new_visual_or_source_review':True,'current_body_target_applicable_accepted':None})
legacy=json.loads((ROOT/'docs/art/creature-mc-v35/reference-ledger.json').read_text())
v40=json.loads((ROOT/'docs/art/bestiary-v40/references.json').read_text())
qimen=json.loads((ROOT/'docs/art/bestiary-v43/qimen-research-20261030/progress.json').read_text())
human=json.loads((ROOT/'docs/art/bestiary-v43/reference-review.json').read_text())
three=[]
for folder,pname in [('humanoid-recovery-research-20261110','checkpoint.json'),('native-damage-state-research-20261110','progress.json'),('crossbow-body-state-research-20261110','progress.json')]:
 base='docs/art/bestiary-v43/'+folder+'/'
 three.append({'batch':folder,'receipt':evidence(base+'receipt.json'),'index':evidence(base+'index.html'),'progress':evidence(base+pname),'new_accepted_credit':0})
extra_paths=['docs/art/creature-mc-v35/reference-ledger.json','docs/art/bestiary-v40/references.json','docs/art/bestiary-v41/references/ledger.json','docs/art/bestiary-v43/reference-review.json','docs/art/bestiary-v43/qimen-research-20261030/progress.json','docs/art/bestiary-v43/registered-art-continuation-20261031/progress.json','tools/art/bestiary-v43/progress.json','docs/art/bestiary-v43/body-joints-20261102/reference-contexts.json']
record={'recorded_utc':datetime.now(timezone.utc).isoformat(),'status':'BOUNDED_HISTORICAL_SCOPE_AND_COUNT_RECONCILIATION_NOT_NEW_REFERENCE_ACCEPTANCE','read_mode':'Ledger metadata/count/identity/hash reconciliation. Historical viewed flags/observations retained as records; this turn did not newly inspect all cards or reread all source bodies.','evidence':[evidence(p) for p in extra_paths],'three_sealed_batches':three,'target_ledgers':ledgers,
'historical_static_library':{'source':evidence('docs/art/creature-mc-v35/reference-ledger.json'),'rows':len(legacy),'status_counts':dict(Counter(r.get('status') for r in legacy.values())),'kind_counts':dict(Counter(r.get('kind') for r in legacy.values())),'historical_accepted_structure_rows':sum(r.get('accepted') is True for r in legacy.values()),'historical_values_preserved':True,'v40_inherited_record_count':v40['inherited_library_records'],'v40_inherited_accepted_samples':v40['inherited_accepted_samples'],'v40_not_new_1000_review':v40['not_new_1000_review'],'current_complete_body_texture_animation_applicable_credit':None,'limitation':'Static bind-pose structure only; no texture/animation/runtime approval. Do not convert this existing1000 into1000 complete applicable mechanisms or re-zero it.'},
'scope_authority':[
{'scope':'historical direct-human per-creature body+texture requirement','required':qimen['human_per_creature_reference_gate'],'evidence':'qimen progress gate_authority_boundary + this chat direct human requirement before each creature','interpretation':'Preserve the100 per-creature ledger; do not rewrite it as1000 because a different tool/weapon/architecture study uses1000.'},
{'scope':'separate queued six-tool/weapon research','required':qimen['separate_queued_weapon_research_gate'],'evidence':'qimen progress separate_queued_weapon_research_gate','interpretation':'Not body-model cumulative acceptance; item/tool production belongs to texture specialist.'},
{'scope':'new general production/fix gate in latest user-supplied project instructions','required':1000,'evidence':'AGENTS.md instructions supplied by user on recovery: 新制作/修复先满足适用范围1000处真实相关、语义不同的实现参考','interpretation':'Apply newer instruction to applicable new production; do not retroactively relabel old100 receipts or claim all old1000 structure records satisfy new complete-mechanism gate. No production authorized by this reconciliation.'}],
'human_candidate_ledger':{'candidate_count':human['candidate_count'],'inspected_cards':human['inspected_cards'],'per_creature_accepted_as_recorded':human['per_creature_accepted'],'textured_body_study':human['textured_body_study'],'limitation':'102 candidates and44 views over11 characters/6 geo files are not102 accepted applicable bodies or44 mechanisms.'},
'overlap_diagnostic':{'target_accepted_rows_total':len(allids),'exact_identity_union':len(set(allids)),'exact_identity_overlap_excess':len(allids)-len(set(allids)),'not_semantic_dedup_or_global_credit':True,'explanation':'Different targets may legitimately reuse one source. Same labels across repositories may be distinct; different labels may share a rig. No global count inferred.'},
'actual_cumulative_state':{'legacy_structure_accepted_as_recorded':1000,'target_specific_historical_accepted':{x['target']:x['historical_accepted_for_target'] for x in ledgers},'current_human_complete_applicable_accepted_total':None,'gap_for_historical_per_creature100':None,'gap_for_current_applicable1000':None,'new_accepted_credit_this_reconciliation':0,'historical_evidence_not_reset':True},
'concrete_missing_evidence':[
'A current named body target and exact reference-scope applicability map are not established by these three generic mechanism batches.',
'No cross-ledger semantic equivalence/rig inheritance map connecting all static library identities to complete relevant body+texture+animation implementations.',
'No per-current-target acceptance receipt for Human Companions against the applicable100 or newer1000 production gate; source study remains a candidate family.',
'Historical source+atlas study limits include renderer-path confirmation still pending for55 marshal and47 taoyan accepted rows; these are not silently upgraded to complete runtime bindings.',
'102 humanoid cards explicitly carry per_creature_accepted0; eleven textured characters use six underlying geo files and are not eleven independently qualified rigs.',
'Historical100s apply to gongsun_wuwang, taoyan_zhishi and luban_yisha structure/material scope, not swindler feigned-injury or herb_picker neutral baseline.',
'No current game acceptance; existing approved production remains protected.'],
'ownership':{'this_chat':'Creature/person body geometry, bones, body animations and attachment interfaces only.','texture_specialist':'Armor textures/worn UV; held items, weapons and hanging accessory objects themselves including model, texture and UV.','boundary':'Read actual holding hand, state, head-directed arms, sleeve transforms and parent/pivot interface; do not author object assets or consume their reference quotas.'},
'unchanged':['No production assets, main checklist, external prompts, sharedJar, game instances or worlds altered.','No Java/game/audio/brightness/focus operation.','No new source/body research credited merely from this metadata reconciliation.']}
(HERE/'receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
checks=[c for l in ledgers for c in l['cards']]
verification={'target_cards_checked':len(checks),'target_cards_missing':sum(not c['exists'] for c in checks),'target_card_hash_mismatches':[c['path'] for c in checks if c['exists'] and not c['hash_matches']],'all_three_batch_hashes_checked':True,'no_new_semantic_acceptance':True}
(HERE/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
progress={'recorded_utc':record['recorded_utc'],'receipt':evidence(str((HERE/'receipt.json').relative_to(ROOT))),'verification':evidence(str((HERE/'verification.json').relative_to(ROOT))),'accepted_total':None,'gap':None,'historical_state_preserved':record['actual_cumulative_state'],'next':'Close actual renderer death/hurt consumer for present SecondaryMob against exact GeckoLib4.8.4; do not infer it inherits vanilla LivingEntityRenderer.','all_tasks_complete':False,'production_modified':False}
(HERE/'progress.json').write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'receipt_sha256':sha(HERE/'receipt.json'),'verification':verification,'counts':record['actual_cumulative_state'],'overlap':record['overlap_diagnostic']},ensure_ascii=False))

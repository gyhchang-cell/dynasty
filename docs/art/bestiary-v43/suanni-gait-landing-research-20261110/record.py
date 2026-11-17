"""Seal new dense boundary evidence, preserving earlier passed scope and assets."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads((R/p).read_text())
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def source(p,scope):return dict(path=str(R/p),sha256=sha(R/p),scope=scope)
summary=json.loads((O/'sampling-summary.json').read_text())
prior_path='docs/art/bestiary-v43/suanni-body-policy-research-20261110/receipt.json';prior=load(prior_path)
assert summary['production_unchanged']
for p,h in summary['source_hashes'].items():assert sha(p)==h
ref=prior['related_external_study']
assert ref['entity_commit_provenance_verified']
for k in ['model','entity']:assert sha(ref[k]['path'])==ref[k]['sha256']
historical_path='docs/blueprint-cod1/evidence/bronze-suanni-v1/software-sampling.json';hist=load(historical_path)
historical_inputs={}
for suffix in ['geo/blueprint/elite/zhenmu_suanni_tonghou.geo.json','animations/blueprint/elite/zhenmu_suanni_tonghou.animation.json']:
 p='src/main/resources/assets/dynasty/'+suffix;h=hist.get('resourceSha256',{}).get(p)
 historical_inputs[p]=dict(historical_sha256=h,current_sha256=sha(R/p),matches=h==sha(R/p))
findings={
 'why_new_check':'Historical software receipt used81 poses per clip. Its animation hash still matches, but geometry hash differs from current approved final body; old floor/contact results are not transferred as current geometry acceptance. New study targets exported keys and interval midpoints of walk/stomp/death only, not rerunning passed fire/state timing.',
 'walk':'481 samples: at least3 paw endpoints planted and at least3 bronze ball bottoms within.03 model units of localY0. Maximum shin-tip to independent paw-pivot error.070584428units at27.9tick/rear_left (~4.4115mm). Maximum ball extent-vs-intendedlift residual.00667949units (~.4175mm), including interpolation residuals of both signs. This is measured software endpoint/extent evidence, not terrain/balance/no-slip or zero penetration proof.',
 'stomp':'103 samples: at least3 planted endpoints/near-ground balls. Maximum shin-paw pivot residual.0152107005units at9.9tick/front_left (~.9507mm); ball extent-vs-lift residual numerical roundoff. Lift->return follows existing source, no new strike frames/damage tests. Actual mesh overlap and server contact remain separate from pivot agreement.',
 'death':'165 samples: global mesh floor remainsY0 because independent support balls stay on ground. Current head/jaw minimum1.266967307units (~7.9185cm); cast upper/shin minimum.667352730units (~4.1710cm), both reached after collapse, unlike a claim that every detached part lies on floor. Global min alone conceals these positive gaps. Furnace-child upper chains detach from root-child paw chains intentionally on death; do not judge this as live IK failure.',
 'causal_limit':'Generator computes walk ball extents and death limb/head compensation before v33/v34/v35 body refiners; existing hierarchy/animation retained while final cubes change. Input mismatch plus measured part clearance establishes need for final-form review, not a proven native bug or authorization to alter offsets. Only local linear sampler transforms used, not native Gecko interpolation or gravity/terrain.',
 'fixed_reference':'Reuse prior independently byte-verified AlexsMobs Tiger ModelTiger/selected EntityTiger AIMelee at09755dade2cfbdf14839e026d3af446f9d3ff843. Related method: torso/hindleg counterbalance, planted versus swinging limbs, distinct recovery/reset. Preserve Suanni rolling bronze supports and original mechanisms. No new source scan, network fetch, new family, extra pose credit or copied reference geometry.',
 'gate':'Historical1000 static-structure references and prior target100s preserved. Mapping to current whole implementation, semantic distinctness/inheritance dedup and independent acceptance incomplete; new accepted credit0, applicable total/gap null. No production repair before applicable gate.',
 'limits':'No model/rig/animation/PNG/UV/weapon/accessory/armor/logic changes. No game/Java/native QA/user instance/sharedJar/coordinator checklist/prompt deletion/commit/push. Original cod1 §15 remains PARTIAL; static diagnostic data is not whole task acceptance.'}
write('findings.json',findings)
write('historical-input-comparison.json',dict(historical_receipt=source(historical_path,'read metadata and two hashes only, no old81 rerun'),inputs=historical_inputs))
write('applicability.json',dict(new_accepted_reference_credit=0,historical_structure_accepted=1000,historical_target100s_not_reset=True,
 applicable_whole_accepted_total=None,gap=None,
 reused_fixed_reference=source('docs/art/bestiary-v43/suanni-body-policy-research-20261110/tiger-whole-policy-study.json','existing selected Tiger body mechanism study, same identity'),
 missing=['Current-target whole implementation mapping and semantic/independent acceptance','Native motion/terrain/clip-reset/reload validation','Approved final-geometry landing gap assessment before any permitted repair']))
visual=dict(path=str(O/'contact-poses.png'),sha256=sha(O/'contact-poses.png'),
 code_sha256=sha(O/'preview.py'),texture_sha256=sha(R/'src/main/resources/assets/dynasty/textures/entity/blueprint/elite/zhenmu_suanni_tonghou.png'),
 dead_texture_sha256=sha(R/'src/main/resources/assets/dynasty/textures/entity/blueprint/elite/zhenmu_suanni_tonghou_dead.png'),
 inspected=True,kind='offline final-geometry/actual-PNG side poses, yaw90 elevation0, shared bounds/scale and localY0 line; not native capture',
 observation='At selected death24/57 frames support balls meet localY0 while head and broken upper limbs sit above it. These are still attached furnace-child parts rather than independently simulated falling pieces; therefore a positive part-floor clearance alone is not accepted as a gameplay defect. No production repair authorized. Live side views show current ball supports, without implying native balance or surface contacts.')
write('visual-inspection.json',visual)
write('receipt.json',dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_task=prior['task'],
 prior=source(prior_path,'passed fire/actor-state timing reused without rerun'),
 current_source_hashes=summary['source_hashes'],reference_byte_hashes={k:ref[k]['sha256']for k in ['model','entity']},
 helper=source('tools/art/secondary-cuboid/review_models.py','existing sample/transform/geometry functions reused'),
 findings=findings,summary=summary,historical_inputs=historical_inputs,visual_inspection=visual,
 production_modified=False,native_accepted=False,task_deletion_permitted=False,new_accepted_reference_credit=0))
(O/'README.md').write_text('# 镇墓狻猊：密集步态与落地边界\n\n本批只补尚未覆盖的关键帧及帧间边界，生产资产未改。\n\n'+'\n\n'.join('**'+k+'**：'+v for k,v in findings.items())+'\n')
write('progress.json',dict(original_task_id=prior['task']['original_task_id'],runtime_id=prior['task']['runtime_id'],
 new_scope='dense exported-key/midpoint walk/stomp/death boundaries saved',status='PARTIAL: final-form landing gap, reference acceptance and native checks remain',
 previous_progress='docs/art/bestiary-v43/suanni-body-policy-research-20261110/progress.json',
 old_passed_checks_rerun=False,new_accepted_reference_credit=0,applicable_whole_accepted_total=None,gap=None,production_modified=False,
 next=['Continue whole relevant reference applicability/semantic review, preserving existing Tiger identity and prior counts',
 'Do not alter production until applicable gate; native conditions currently unmet']))
write('handoff-metadata.json',{n:dict(path=str(O/(n+'.json')),sha256=sha(O/(n+'.json')))for n in ['receipt','progress','applicability','historical-input-comparison','sampling-summary','findings','visual-inspection']})
print(json.dumps(dict(handoff=str(O/'handoff-metadata.json'),sha256=sha(O/'handoff-metadata.json'),production_modified=False),ensure_ascii=False,indent=2))

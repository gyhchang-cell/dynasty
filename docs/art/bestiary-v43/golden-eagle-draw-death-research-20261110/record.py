"""Seal selected draw/death research without changing original tasks or assets."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[4]; O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads((R/p).read_text())
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def src(p,scope):return dict(path=str(R/p),sha256=sha(R/p),read_scope=scope)
prior='docs/art/bestiary-v43/golden-eagle-dive-policy-20261110/receipt.json'; old=load(prior)
assert all(sha(s['path'])==s['sha256'] for s in old['sources']+old['reused_helpers'])
curves=json.loads((O/'curve-source-comparison.json').read_text()); death=json.loads((O/'death-compensation-summary.json').read_text())
assert curves['all_tracks_equal']
observations={
 'applicability':'Reuses historical1000 bind-pose structure ledger and historical target100 scopes without reset or promotion. No established accepted mapping to this target complete draw/death implementation, no independent semantic whole-policy acceptance/cross-ledger dedup. New accepted reference credit0; applicable whole total and gap remain null. This research is not authorization for production.',
 'source_chain':'Read entire fixed GoldenEagle generator. It constructs body and two serial12-unit legs with independent talon pads, densifies tilt/draw controls before analytic IK, writes clips, computes death/dive floor correction, then calls inventory/material and v33/v34/v35 refiners. Those item/texture calls were read as export-order context only, not executed. Reviewed actor-specific three refiner branches: final geometry changes body/neck/wing cubes while keeping hierarchy and draw interface. Current seven clips and sources retain prior hashes.',
 'draw_controls':'rain total116ticks; pure solver controls (seconds,pull units,tilt degrees) are (0,0,0),(.3,0,-45),(1.5,10,-45),(1.55,0,-45),(1.9,0,0),(5.8,0,0). Hence bow points upward by6ticks, builds10-unit draw through30, snaps pull back30..31, then recovers tilt31..38. Grip endpoint fixed; draw endpoint derives from the same tilted arrow nock. No hand-held bow mesh or PNG/UV changes.',
 'solver_comparison':'Only pure keys/legs functions and literal HIP/REST/L extracted from exporter AST; full exporter never executed. Every current exported rain thigh/hock/talon/attached string/arrow/bow channel equals the regenerated pure numeric track. This is numeric authorship consistency, not native render acceptance or independent external reference credit.',
 'new_sampling_scope':'383 exported-key and interval-midpoint samples supplement old81 pose observations specifically for nonlinear endpoint drift under linear track interpolation. Maximum draw hock/talon residual0.044384593 model units (~2.774mm), nock/draw0.000514434 (~0.032mm), string/nock0.025648223 (~1.603mm), grip effectively zero. Old sparse-sample threshold .025 units is not generalized to these additional midpoints; report observed residual, do not overwrite historical receipt or pretend zero error.',
 'release_boundary':'Actor RAIN441 emits at30, visible drawn_arrow renderer hides atage>=30 while attached nock pull recovers through31. Body action still rain until116 unless cancelled. Server muzzle uses documented full-draw tip formula; exact native geometric/world spawn alignment remains to test. No actual EagleArrow object split/roof/shield lifecycle acceptance claimed in this body-only extension.',
 'death_position_curve':'212 exported body-position keys inspected via all425 union-key/midpoint samples against current final cubes. CompensationY ranges0..17.01 model units; bodypitch65deg by14ticks,90by28; scale1through56 then0by84, actor removal90. Compensation is local mesh clearance, not server falling/gravity displacement. It was computed before final body refiners and considered attachment geometry; current visible sampling excludes drawn_arrow because renderer hides it dead.',
 'death_interpretation':'At2.6ticks body-only lowest point is grip_hock11.61306units (~0.726m) above local origin while visible lower_bow_limb is0.01unit above it. Thus a body-only floor test would confuse an attachment-supported fallen pose with the entire mesh hovering. At69.6ticks body beak lowest2.58143units while scale~.514; collapse need not keep every visible vertex on ground. No sampled visible vertex penetrates localY0, but this does not establish native terrain contact or falling pose quality. No automatic offset adjustment.',
 'interruption':'Prior unchanged actor: actual healthloss>=8 while WINDUP stops30, cancels action and arrows, stops navigation/input, enables gravity, syncs skill0. visualAnimation selects hurt while hurtTime then fly/idle; no separate STUN clip. START change force-resets controller; rain limb/tilt restoration when switching clips and packet ordering remain native gaps. Dead actor cancels all spells/arrows and uses death clock; no repeated release proof beyond shared source clock checks.',
 'reload':'Finite bounded landing offsets/attack/lastCombat/death saved; invalid mark cancels, active gap>1 or reversal cancels and clears arrows. Alive reload syncs stored skill, dead clears it; gravity derives before final sync during load, as previously documented. Exact frame continuity, scale/position reset and no detached contact on reconnect remain native gaps; not asserted fixed.',
 'ownership_and_limits':'Read-only body/bone/animation/attachment interface study. No body geometry/skeleton/animation/gameplay changes, no held item/accessory/armor model/texture/UV work, no Java/game/QA/instance/sharedJar/main checklist/prompt deletion/commit/push. Whole source study is not original cod1 §14 completion.'}
sources=[src('tools/blueprint/generate_golden_eagle.py','entire file, body solver/export ordering; item and texture portions read context only, not run'),
 src('tools/art/secondary-cuboid/review_models.py','sample/transform/geometry functions through line99; native Gecko internals not assumed'),
 src('tools/art/creature-mc-v33/refine.py','actor-specific eagle body branch and surrounding selection context only'),
 src('tools/art/creature-mc-v34/refine.py','actor-specific eagle body branch and surrounding selection context only'),
 src('tools/art/creature-mc-v35/refine.py','actor-specific eagle branch and final finish binding only'),
 src('tools/blueprint/review_golden_eagle.py','entire existing software-review script read; not run or rewritten'),
 src('tools/blueprint/validate_golden_eagle.py','entire existing validation script read; not run, old fixed16px/object checks not applied to current assets'),
 src('src/main/resources/assets/dynasty/animations/blueprint/elite/liefeng_jindiao_yushi.animation.json','all rain solver tracks compared to pure source; all212 death position keys numerically inspected, selected sparse channels reused'),
 src('src/main/resources/assets/dynasty/geo/blueprint/elite/liefeng_jindiao_yushi.geo.json','current body and read-only attachment cube transforms used only for selected contact/clearance study')]
write('body-findings.json',observations)
checks=dict(prior_source_hashes_unchanged=True,all_rain_solver_tracks_equal=curves['all_tracks_equal'],
 rain_key_and_midpoint_count=curves['sample_count'],death_key_and_midpoint_count=death['sample_count'],
 visible_local_floor_min_units=death['visible_lowest']['visible_min_y_units'],
 local_floor_penetration_observed=death['visible_lowest']['visible_min_y_units']<0,
 production_modified=False,java_or_game_started=False,native_accepted=False)
write('verification.json',checks)
write('applicability.json',dict(new_accepted_credit=0,historical_structure_accepted=1000,historical_target100s_not_reset=True,
 applicable_whole_accepted_total=None,gap=None,
 reused_reference_receipt=src('docs/art/bestiary-v43/reference-reconciliation-20261110/receipt.json','historical scopes/count reconciliation reused; not rereading or recounting old300 cards'),
 missing=['Target applicable complete draw/death policy reference mapping','Independent semantic acceptance and inheritance dedup','Native body/attachment contacts, interrupt reset, falling death and reload']))
write('receipt.json',dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_task=old['task'],
 prior_receipt=src(prior,'completed dive state/source reading reused, no duplicate reference credit'),sources=sources,
 findings=observations,verification=checks,new_accepted_credit=0,applicable_whole_accepted_total=None,gap=None,
 original_task_retained=True,task_deletion_permitted=False,production_modified=False))
(O/'README.md').write_text('# 金雕羽士：拉弓与死亡补偿身体链\n\n原任务cod1 §14保持PARTIAL。本批仅补充固定本地源研究与离线数值检查，没有修改模型。\n\n'+
 '\n\n'.join('**'+k+'**：'+v for k,v in observations.items())+'\n')
write('progress.json',dict(original_task_id=old['task']['original_task_id'],runtime_id=old['task']['runtime_id'],
 selected_draw_and_death_curve_research='saved',whole_native_actor_accepted=False,new_accepted_credit=0,
 applicable_whole_accepted_total=None,gap=None,production_modified=False,
 previous_progress='docs/art/bestiary-v43/golden-eagle-dive-policy-20261110/progress.json',
 remaining=['Applicable whole implementation reference mapping and semantic acceptance','Native release/contact and interrupt reset','Native gravity/death/reload'],
 next='Check prior whole-owner coverage for original cod1 §15 镇墓狻猊铜吼 before next complete body-state review; do not author pending gate.'))
write('handoff-metadata.json',{n:dict(path=str(O/(n+'.json')),sha256=sha(O/(n+'.json'))) for n in ['receipt','progress','applicability','verification','curve-source-comparison','death-compensation-summary']})
print(json.dumps(dict(handoff=str(O/'handoff-metadata.json'),sha256=sha(O/'handoff-metadata.json'),verification=checks),ensure_ascii=False,indent=2))

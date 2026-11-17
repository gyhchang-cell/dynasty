"""Record reviewed static body policy; never modifies production or pending tasks."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[4]
O=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads((R/p).read_text())
def write(n,d): (O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def source(p,scope): return dict(path=str(R/p),sha256=sha(R/p),read_scope=scope)
ID='qingdeng_panguan_guichai'
geo=f'src/main/resources/assets/dynasty/geo/blueprint/elite/{ID}.geo.json'
anim=f'src/main/resources/assets/dynasty/animations/blueprint/elite/{ID}.animation.json'
sources=[source('src/main/java/com/dynasty/blueprint/elite/LampJudge.java','entire actor body state/trigger/interrupt/death/save-load'),
 source('src/main/java/com/dynasty/blueprint/elite/client/LampJudgeRenderer.java','entire file; butterfly visibility, body culling, mark text timing; object declarations context only'),
 source('src/main/java/com/dynasty/blueprint/elite/JudgeSpell.java','entire class as cage interruption/lifecycle producer; no object asset authoring or new object reference credit'),
 source(geo,'all bone hierarchy, pivots and default rotations; no cube or UV authoring'),
 source(anim,'all seven clips; unique left/right butterfly wing curves displayed in full, six pairs confirmed identical')]
prior=load('docs/art/bestiary-v43/tide-yasha-body-policy-20261110/receipt.json')
reuse=[dict(s,current_hash_matches=sha(s['path'])==s['sha256']) for s in prior['unchanged_reused_helpers']]
tp=Path('/Users/a15356015027/Desktop/code x提示词/cod1.txt')
lines=tp.read_text().splitlines(); start=next(i for i,l in enumerate(lines) if l.startswith('### 13. 青灯判官鬼差'))
end=next(i for i in range(start+1,len(lines)) if lines[i].startswith('### '))
task=dict(file=str(tp),sha256_at_read=sha(tp),original_task_id='cod1.txt §13 青灯判官鬼差',line_start=start+1,line_end=end,
 heading=lines[start],runtime_id='dynasty:'+ID,pending_text_copied=False,status='original PARTIAL retained',
 body_owner='existing 做建模的: body/bones/body animation/attachment interfaces',
 object_owner='existing 做贴图的: pen, stroke, cage and accessory object model/PNG/UV; no edits here',
 remaining_native_subscope=['build','singleplayer and two-player combat','natural encounter entrance','reload/reconnect/restart','stress and balance','actual contact/visibility/interrupt acceptance'])
write('task-scope.json',task)
findings={
 'trigger_and_priority':'Server/alive/enemy/sight/height delta <=3 and horizontal configured max-range gate; CAGE additionally validates loaded radius floor/no-fluid/full-body clearance and home distance. AI tries cage at squared distance<6.25, name at>25, otherwise strokes, still subject to actual gates. Body priority death > 431 name /432 strokes /433 cage > hurtTime > moving walk > idle. No distinct STUN clip.',
 'name_whole_policy':'431=40 windup+12 active+40 recovery=92 ticks, impact40. Mark follows valid target only through age35, then locks36..40. Server impact creates actual falling pen at mark+5Y, not damage from eye or brush mesh. Eye scales pulse1.12 at12/24/36; ledgers open to +/-45 by6, hold36, close40. Brush swivel alternates during naming then resets32. Renderer world-text ages0..11 death2,12..23 death1,24..39 death; bright at12..14,24..26,36..39. This is finite cast, not a new font or object-production task.',
 'strokes_whole_policy':'432=10+40+34=84 ticks, emits at10/18/26/34/42 in -20/-10/0/+10/+20 degrees from fixed cast direction. Brush local yaw has corresponding five authored directions at those ticks; server spawn is calculated in world coordinates, so exact nib-contact alignment is not proven. Ledger opens +/-25 at10, holds50 and closes64. Max7 owned JudgeSpell objects gate creation; effect cut has bounded16 distinct hit UUIDs and80-tick life, no new blade asset work.',
 'cage_whole_policy':'433=16+160+36=212 ticks. Ledger opens +/-90 by12, holds through176, closes190. Lamp XZ scale1.2 at16..176, resets212. During age16..175 actor may navigate toward fixed mark at.6 when AI enabled; it keeps CAGE clip rather than walk. At176 clears owned cages. Before16/after175 horizontal motion is stopped. This is a sliding possessed book, not a hidden human walk conversion.',
 'cage_break_and_interrupt':'Accepted server hurt while CAGE active from living attacker with horizontal normalized attacker offset dot cast direction<-.5 stops35 and clears cages. No damage threshold for this existing back-hit break. Otherwise actual health loss>=8 during WINDUP stops25. Ordinary stop clears cages only; already emitted non-cage pens/strokes remain bounded by their own lifetime. Time gap/reversal or death clears all owned spells. Do not claim every spell discard cancels actor.',
 'cage_producer_lifecycle':'JudgeSpell cage validates alive owner, same cast epoch/current CAGE, loaded bounds and age<160; a gap>1/reversal or distance>68 discards. Captures at most8 alive noncreative nonspectator players, uses radius2.6 for confinement, maintains last legal position, native same-level connection teleport preserves view, and calls breakCage if projected/fallback position unsafe. Other discard causes do not all call breakCage. Actual networking and legality remain native acceptance.',
 'death_and_hierarchy':'Death cancels body action/navigation/target/all spells; root does not undergo vanilla whole-body roll. Server removes at84 ticks, clip4.2sec. Iron spine shrinks to0 and movesY-15 by22; ledger children flare +/-150 by24. Broken brush tip rotates6..16 but inherits shrinking spine: not proof of independently visible detached debris after22. Inkstone expandsXZ1.3 by24, holds60, disappears84. Six butterfly roots are independent root children, visible only dead, grow0->1 at6..10, hold56, then0at84 while rising in distinct positions; wing curves +/-55 alternate17 keys, all six pairs use same curves. Six butterflies are one authored death mechanism, not six reference credits.',
 'reload_and_controller':'Stores EliteAttack, finite bounded landing offsets, LastCombatTick/death/loot/home. Invalid landing cancels; alive load syncs, dead load clears skill. Active next combat tick with gap>1/reversal cancels and clears all spells. Cage trapped-player map is not persisted; cage load sets born=-1 so it is discarded rather than restoring constraints. Actor and object reload need combined native testing; no seamless continuation claim. START change force-resets body controller; running skill/death uses world-age tick, reused shared clock/controller evidence not new reference.',
 'whole_policy_comparison':'Reuses completed InkAssassin policy: four owned matching-cast anchors break a field and stop30, whereas this single cage can break from back-hit/unsafe player correction and permits actor navigation while ledger remains spread. Both retain cast identity/time-gap guards, but those shared safeguards are not additional implementation credit.',
 'limits':'Static selected body-policy review only. No geometry/proportion/skeleton/PNG/UV/animation/gameplay edits. Actual visibility, interpolation, mark contact, moving-cage pose, multiplayer interruption and reload still need native acceptance. Existing original task retained.'}
write('body-findings.json',findings)
clips=load(anim)['animations']; bones=load(geo)['minecraft:geometry'][0]['bones']; names={b['name'] for b in bones}
write('timeline.json',dict(kind='source events and authored raw keyframes, not native replay',
 contracts={n:dict(total_ticks=t,impact_ticks=hits) for n,t,hits in [('name',92,[40]),('strokes',84,[10,18,26,34,42]),('cage',212,[16]),('death',84,[])]},
 name=dict(mark_updates_through=35,locked_from=36,eye_pulses=[12,24,36],release=40),
 cage=dict(actor_navigation_interval_inclusive=[16,175],clear_cages=176,ledger_full_spread_from=12,ledger_close=190),
 authored_channels={n:clips['animation.'+ID+'.'+n] for n in ['name','strokes','cage','death']}))
old=load('docs/art/bestiary-v43/reference-reconciliation-20261110/receipt.json')
write('applicability.json',dict(current_target='dynasty:'+ID,historical_structure_accepted=1000,
 historical_target100s=old['actual_cumulative_state']['target_specific_historical_accepted'],
 historical_counts_not_reset=True,new_accepted_credit=0,applicable_whole_accepted_total=None,gap=None,
 missing=['Accepted mapping from historical bind-pose1000/target-specific100 to this complete body-state policy',
 'Independent semantic acceptance and cross-ledger inheritance dedup',
 'Native actual pen contact, cage motion/back-hit/unsafe correction, death and reload acceptance'],
 reuse=source('docs/art/bestiary-v43/ink-assassin-body-policy-20261110/receipt.json','whole static body policy comparison, not new external reference')))
checks=dict(source_hashes_match=all(sha(s['path'])==s['sha256'] for s in sources),reused_helpers_match=all(s['current_hash_matches'] for s in reuse),
 all_clip_bones_exist=all(b in names for c in clips.values() for b in c['bones']),
 clip_contract_ticks={n:[clips['animation.'+ID+'.'+n]['animation_length']*20,t] for n,t in [('name',92),('strokes',84),('cage',212),('death',84)]},
 production_modified=False,java_or_game_started=False)
write('verification.json',checks)
write('receipt.json',dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),task=task,sources=sources,reused_helpers=reuse,
 findings=findings,whole_static_actor_policies_reviewed=1,new_accepted_credit=0,applicable_whole_accepted_total=None,gap=None,
 production_modified=False,java_or_game_started=False,task_deletion_permitted=False))
(O/'README.md').write_text('# 青灯判官：身体动作政策静态核对\n\n原任务保持PARTIAL；不复制待办正文。\n\n'+'\n\n'.join('**'+k+'**：'+v for k,v in findings.items())+'\n')
write('progress.json',dict(task=task['original_task_id'],receipt=source(str((O/'receipt.json').relative_to(R)),'complete selected static actor body policy'),
 previous_progress='docs/art/bestiary-v43/ink-assassin-body-policy-20261110/progress.json',new_accepted_credit=0,
 applicable_whole_accepted_total=None,gap=None,all_tasks_complete=False,
 next='Check existing whole-owner coverage and applicable evidence for cod1 §14 烈风金雕羽士 before next body-state review; no production until gate.'))
write('handoff-metadata.json',{k:dict(path=str(O/n),sha256=sha(O/n)) for k,n in [('receipt','receipt.json'),('progress','progress.json'),('task','task-scope.json'),('applicability','applicability.json'),('verification','verification.json')]})
print(json.dumps(dict(handoff=str(O/'handoff-metadata.json'),sha256=sha(O/'handoff-metadata.json'),checks=checks),ensure_ascii=False,indent=2))

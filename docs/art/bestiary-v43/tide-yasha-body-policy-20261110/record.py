"""Evidence only: existing aquatic body action policy, no production writes."""
from pathlib import Path
import datetime, hashlib, json
R=Path(__file__).resolve().parents[4]
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads((R/p).read_text())
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def src(p,scope):return {'path':str(R/p),'sha256':sha(R/p),'read_scope':scope}
actor='src/main/java/com/dynasty/blueprint/elite/TideYasha.java'
renderer='src/main/java/com/dynasty/blueprint/elite/client/TideYashaRenderer.java'
geo='src/main/resources/assets/dynasty/geo/blueprint/elite/fubo_xunhai_yecha.geo.json'
anim='src/main/resources/assets/dynasty/animations/blueprint/elite/fubo_xunhai_yecha.animation.json'
external='build/creature-reference-1000/AlexModGuy__AlexsMobs/'
pkg='src/main/java/com/github/alexthe666/alexsmobs/'
sources=[src(actor,'entire class, all action selection/priority/cancel/death/load paths'),
 src(renderer,'entire class: own body bindings and visibility/death handling; vortex renderer context only'),
 src(geo,'all bone names, parents, pivots and rotations, not object cube authoring'),
 src(anim,'all seven existing clips read; no new interpolation/runtime acceptance'),
 src(external+pkg+'entity/EntityLobster.java','entire class, claw attack trigger/count/progress/exit and custom save/load'),
 src(external+pkg+'client/model/ModelLobster.java','entire class: hierarchy and attack-progress body application; dependency helper internals excluded')]
previous=load('docs/art/bestiary-v43/gorilla-smash-body-research-20261110/receipt.json')
reuse=[]
for s in previous['sources']:
 if any(n in s['path'] for n in ['TimedAttack.java','SkillDefinition.java','AttackState.java']):
  reuse.append({'path':s['path'],'sha256':s['sha256'],'current_hash_matches':sha(Path(s['path']))==s['sha256'],
    'reuse_scope':'Previously entire source reviewed. Same unchanged helper, not new semantic credit.'})
original=Path('/Users/a15356015027/Desktop/code x提示词/cod1.txt')
lines=original.read_text().splitlines();start=next(i for i,l in enumerate(lines) if l.startswith('### 9. 伏波巡海夜叉'))
end=next(i for i in range(start+1,len(lines)) if lines[i].startswith('### '))
task={'file':str(original),'file_sha256_at_read':sha(original),'original_task_identifier':'cod1.txt §9 伏波巡海夜叉',
 'original_heading':lines[start],'line_start':start+1,'line_end':end,'scope_text':'\n'.join(lines[start:end]),
 'runtime_id':'dynasty:fubo_xunhai_yecha','status':'PARTIAL as explicitly recorded in original task; do not delete',
 'remaining_original_acceptance':['Java build','ordinary combat/singleplayer/multiplayer','actual underwater-ruin entrance','reload/reconnect/restart','pressure/equipment numerical acceptance'],
 'this_body_owner_scope':'Body skeleton/action state and attachment interface only. Other remaining acceptance stays with existing owner; no QA/instance creation.',
 'held_objects_owner':'Texture specialist retains fork/trident and other object model/PNG/UV; only hierarchy and transform interface read here.'}
write('original-task-scope.json',task)

findings={
 'trigger_and_selection':'Server only startSkill validates alive/registered skill/enemy/sight/horizontal range, plus real surface for DIVE and no existing owned vortex for WAVE. TimedAttack tryStart is the same unchanged idle/cooldown/finite-input contract already reviewed. AI tries combo at squared distance<=20.25, then dive when>16, then wave; actual skill min/max range gates still apply.',
 'combo_whole_action':'Skill393 total84ticks: WINDUP0..9, ACTIVE10..43, RECOVERY44..83. Three movement windows10..19,22..31,34..43 inclusive, each10steps*.2=2blocks if unobstructed. Step is collision move before impact19/31/43; unloaded next cell or displacement squared<.005 cancels to30tick stun. Third window at34 adds vertical.38 only onGround. This is a conditional intended distance, not actual path/contact acceptance.',
 'combo_body':'carapace->fork_hinge->fork_foresegment->fork_clamp->trident. Local hinge yaw -35at10/+18at19, -30at22/+18at31, -35at34/+15at43; returns0at50. Foresegment roll -10at10/+15at19, -10at22/+15at31, -20at34/+30at39/+5at43, return0at54. Carapace and tail-tip provide smaller counter-motion. Tip attack query is body-position plus fixed right/forward offset, not sampled from rendered bone; matching fork tip to query is unverified.',
 'dive_whole_action':'Skill392 total71ticks:30windup/1active/40recovery; impact30. Pool follows valid target surface through age<=20, then locks. Renderer root+children hidden iff392 and age>=9 and<30 and notdead. Authored root Y scale1->.08at8, holds through30, restores1at34. At30 emergence seeks one loaded unobstructed nearby location with height/home/distance/sight checks; failed emergence cancels30tick stun; valid emergence teleports once, faces pool and adds vertical.3. Animation alone is not server teleport/hit source.',
 'wave_context':'Skill391 total82ticks; impact18; hinge windup yaw-12at12 then+10at18, vent scales peak1.25at17 and return18. Existing trident rotation channel is read as attachment transform only; no weapon object modifications.',
 'body_priority':'death wins, then active skill391/392/393, then hurtTime hurt, horizontal motion walk, idle. Incoming ordinary hurt does not visually replace an active skill. No separate STUN clip branch. Gameplay stun may outlast hurt clip and display idle/walk.',
 'interrupt_exit':'Accepted server damage while alive with actual health loss>=8 and WINDUP stuns20 and immediately syncs. ACTIVE/RECOVERY do not use this custom interrupt. Death cancels attack, clears owned effects, navigation/target, syncs deathStart and chooses death; getDeathMaxRotation0 avoids additional whole-model death roll. Server removes at80ticks. No sound/game operation executed.',
 'visibility_death':'Renderer recomputes root/children hidden every custom animation call, so current skill cancellation or dead state clears dive hiding on next invocation. Reef shell+children hidden while alive, visible flag while dead; death scale then fades reef0 through24 to1at32. Live carapace scales1 through24 to0at32. Six root-parented legs remain until54 and scale0at76. Death effect fragments inherit reef_shell; not new server entities. Planted weapon/normal weapon visibility is an interface read only, not item production.',
 'clock_and_load':'Same0-transition controller as giant ape: reset on START change, loop idle/walk, hold-last others, RUNNING age from gameTime-START+partial except initial reset pass. Source save/load stores EliteAttack, pool, LastCombatTick, deathStart, loot flag/home. Invalid distant saved pool cancels DIVE; time gap>1 or reversal cancels active action on next combat. TimedAttack retains consumed frames/cooldowns, does not dump delayed hits. Not a seamless controller phase/blend persistence claim.',
 'external_whole_comparison':'Pinned Alex Lobster ticks target proximity<=1 and cooldown0 -> doHurtTarget writes ATTACK_TICK5 and calls super.doHurtTarget immediately; same class later applies target hurt2 when count2 and distance<1.3. Counter decrements and attackProgress ramps0..5 then decays; model interpolates prev/current progress, yaws paired arms+/-45 and hands-/+30, layered with idle/locomotion. Counter/damage tick block lacks its own explicit side guard; inherited damage behavior is not proved here. Do not transplant this double-path hit logic or treat visual peak as authoritative hit. Own custom NBT only variant/fromBucket, not counter/progress/cooldown; no own hurt/death cancel override. Inherited death/network/math helpers unreviewed, no complete engine/runtime claim.',
 'comparison_boundary':'Lobster is relevant low aquatic shell with linked claw articulation; it is not an underwater teleport/combo boss and supplies no proof for Yasha dive timing or balance. Transfer only connected parent-child body articulation and explicit attack-progress/return assessment. Existing Yasha body is six-foot shell, not Steve and not being converted.',
}
write('body-findings.json',findings)

a=load(anim)['animations'];g=load(geo)['minecraft:geometry'][0]['bones'];names={b['name'] for b in g}
def sample(v,t):
 if isinstance(v,list):return v
 q=sorted((float(k)*20,z) for k,z in v.items())
 if t<=q[0][0]:return q[0][1]
 for (s,x),(e,y) in zip(q,q[1:]):
  if t<=e:return [u+(v-u)*(t-s)/(e-s) for u,v in zip(x,y)]
 return q[-1][1]
combo=a['animation.fubo_xunhai_yecha.combo']; dive=a['animation.fubo_xunhai_yecha.dive']
timeline=[]
for t in range(85):
 timeline.append({'tick':t,'combo_phase':'WINDUP' if t<10 else 'ACTIVE' if t<44 else 'RECOVERY' if t<84 else 'IDLE',
  'combo_move_request':any(lo<=t<=hi for lo,hi in [(10,19),(22,31),(34,43)]),
  'combo_impact':t in [19,31,43],
  'fork_hinge_local_rotation':sample(combo['bones']['fork_hinge']['rotation'],t),
  'fork_foresegment_local_rotation':sample(combo['bones']['fork_foresegment']['rotation'],t),
  'dive_root_hidden_if_uninterrupted':9<=t<30,
  'dive_root_authored_scale':sample(dive['bones']['root']['scale'],t)})
write('timeline.json',{'kind':'source-contract raw local channels, no engine blend/movement/world-space contact simulation','samples':timeline})

recon='docs/art/bestiary-v43/reference-reconciliation-20261110/receipt.json';old=load(recon)
legacy='docs/art/creature-mc-v35/reference-ledger.json';lob=load(legacy)['AlexsMobs:Lobster']
app={'old_scope_receipt':src(recon,'existing reconciliation reused, old300 image hashes not repeated'),
 'historical_structure_accepted':old['actual_cumulative_state']['legacy_structure_accepted_as_recorded'],
 'historical_target100s':old['actual_cumulative_state']['target_specific_historical_accepted'],
 'existing_lobster_identity':'AlexsMobs:Lobster','existing_lobster_scope':lob['scope'],
 'existing_lobster_model_hash_matches':sha(R/(external+pkg+'client/model/ModelLobster.java'))==lob['sha256'],
 'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,
 'missing':['Old1000 is structural bind pose, not1000 complete aquatic combo/dive/interrupt/reload implementations.',
 'Three historical100 ledgers target gongsun_wuwang/taoyan_zhishi/luban_yisha, not this ID; no established whole-strategy applicability map.',
 'Current Lobster reading extends the existing identity; no independent acceptance or semantic-rig dedup makes it new credit.',
 'Missing actual Yasha fork-tip world-space vs server query, six-foot contact, visibility exit after cancel/death, reload/reconnect/native entrance acceptance.',
 'External original renderer was absent from selected cache; no textured/runtime binding or external base death/network/helper verification claimed.'],
 'dedup':'Shared TimedAttack/controller conventions reused from prior ape; new local semantic scope is six-foot fork combo plus dive hiding/emergence and death shell replacement, not another helper/frame/reference count.'}
write('applicability.json',app)
receipt={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_task':task['original_task_identifier'],
 'runtime_id':task['runtime_id'],'sources':sources,'unchanged_reused_helpers':reuse,
 'external_pin':load(external+'source.json')['sha'],'findings':findings,
 'completed':'One selected existing actor whole static body action policy including priority/interruption/death/reload, not runtime/full engine acceptance.',
 'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,
 'production_modified':False,'java_or_game_started':False,'main_checklist_modified':False,
 'no_new_entities_or_objects':True,'task_deletion_permitted':False}
write('receipt.json',receipt)
verification={'current_sources_match':all(sha(Path(s['path']))==s['sha256'] for s in sources),
 'reused_helper_hashes_match':all(s['current_hash_matches'] for s in reuse),
 'all_animation_bones_exist':all(b in names for clip in a.values() for b in clip['bones']),
 'combo_clip_ticks':combo['animation_length']*20,'combo_contract_ticks':84,
 'dive_clip_ticks':dive['animation_length']*20,'dive_contract_ticks':71,
 'death_clip_ticks':a['animation.fubo_xunhai_yecha.death']['animation_length']*20,'death_remove_ticks':80,
 'production_modified':False,'java_or_game_started':False}
write('verification.json',verification)
(O/'README.md').write_text('# 伏波巡海夜叉：身体动作政策\n\n原任务：cod1.txt 第9节；保持PARTIAL，未删除提示词。\n\n'+
 '\n\n'.join('**'+k+'**：'+v for k,v in findings.items())+
 '\n\n复用范围：不重读原300卡；保留旧1000结构与3项100账。适用完整累计及缺口为null。所有模型、动作、物件和UV保持。\n')
write('progress.json',{'receipt':src(str((O/'receipt.json').relative_to(R)),'this complete selected static actor policy'),
 'previous_progress':'docs/art/bestiary-v43/gorilla-smash-body-research-20261110/progress.json',
 'original_task':task['original_task_identifier'],'new_accepted_credit':0,'all_tasks_complete':False,
 'applicable_whole_accepted_total':None,'gap':None,
 'next':'Continued to confirmed RageCorpse / dynasty:banshan_jiazhou_shikuang, cod1.txt §10; see rage-corpse-body-policy-20261110. Avoid replaying unchanged TimedAttack/renderer fragments. Preserve gate and owner boundaries.'})
write('handoff-metadata.json',{k:{'path':str(O/n),'sha256':sha(O/n)} for k,n in
 [('receipt','receipt.json'),('progress','progress.json'),('task','original-task-scope.json'),('applicability','applicability.json'),('verification','verification.json')]})
print(json.dumps({'handoff':str(O/'handoff-metadata.json'),'sha256':sha(O/'handoff-metadata.json'),'verification':verification},ensure_ascii=False,indent=2))

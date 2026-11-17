"""Read-only body strategy study. Writes evidence here; never runtime assets."""
from pathlib import Path
import json, hashlib, datetime

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads((ROOT/p).read_text())
def write(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
def evidence(p, scope):
    q=ROOT/p
    return {'path':str(q),'sha256':H(q),'read_scope':scope}

actor='src/main/java/com/dynasty/blueprint/elite/BronzeGorilla.java'
geo='src/main/resources/assets/dynasty/geo/blueprint/elite/hanshan_tongjia_juyuan.geo.json'
anim='src/main/resources/assets/dynasty/animations/blueprint/elite/hanshan_tongjia_juyuan.animation.json'
external='build/creature-reference-1000/AlexModGuy__AlexsMobs/'
package='src/main/java/com/github/alexthe666/alexsmobs/'
sources=[evidence(actor,'entire entity, selected complete SMASH body strategy; other skills read for priority/exit context, not separate credits'),
 evidence('src/main/java/com/dynasty/blueprint/combat/TimedAttack.java','entire file: start, advance, cancellation, cooldown, save/load'),
 evidence('src/main/java/com/dynasty/blueprint/combat/SkillDefinition.java','entire file: timing contract and validation'),
 evidence('src/main/java/com/dynasty/blueprint/combat/AttackState.java','entire enum'),
 evidence('src/main/java/com/dynasty/blueprint/elite/client/BronzeGorillaRenderer.java','entire file: model bindings, selected body renderer and death roll; stone object renderer context only'),
 evidence(geo,'all bone parent/pivot/rotation metadata; body channel references, not object geometry authoring'),
 evidence(anim,'complete smash/idle/hurt channels, numeric all-key extraction; other clips not claimed complete'),
 evidence(external+package+'entity/EntityGorilla.java','entire 600-line entity: attack, stance and save/load; imported engine not fully available'),
 evidence(external+package+'client/model/ModelGorilla.java','entire 266-line model: geometry hierarchy, keyframe definitions, additive setupAnim'),
 evidence(external+package+'entity/ai/GorillaAIChargeLooker.java','entire goal: approach, chest-pound trigger, goal stop without animation cancellation'),
 evidence(external+package+'client/render/RenderGorilla.java','entire renderer: model/scale/body texture path, no object layer implementation review')]

allanim=read(anim)['animations'];smash=allanim['animation.hanshan_tongjia_juyuan.smash']
bones=read(geo)['minecraft:geometry'][0]['bones'];names={b['name'] for b in bones}
tracks={b:c for b,c in smash['bones'].items() if b!='held_rock'}
impacts=[24,32,40,48,56,64,72,80]
def sample(channel,t):
    if isinstance(channel,list): return channel
    pts=sorted((float(k)*20,v) for k,v in channel.items())
    if t<=pts[0][0]:return pts[0][1]
    for (ta,a),(tb,b) in zip(pts,pts[1:]):
        if t<=tb:return [x+(y-x)*(t-ta)/(tb-ta) for x,y in zip(a,b)]
    return pts[-1][1]
timeline=[]
for t in range(131):
    row={'tick':t,'server_phase':'WINDUP' if t<24 else 'ACTIVE' if t<88 else 'RECOVERY' if t<130 else 'IDLE',
         'impact':t in impacts,'impact_side_code':('side+1' if ((t-24)//8)%2==0 else 'side-1') if t in impacts else None}
    for side in ['left','right']:
        ch=tracks[side+'_forearm'];row[side+'_rotation']=sample(ch['rotation'],t);row[side+'_position']=sample(ch['position'],t)
    timeline.append(row)
write('timeline.json',{'kind':'raw authored local channels + server phase contract; not runtime bone matrices/contact proof','samples':timeline})

legacy='docs/art/creature-mc-v35/reference-ledger.json'
recon='docs/art/bestiary-v43/reference-reconciliation-20261110/receipt.json'
old=read(recon);lib=read(legacy)
checks=[]
for t in old['target_ledgers']:
    p=ROOT/t['source']['path']
    checks.append({'target':t['target'],'path':str(p),'hash_matches_previous':H(p)==t['source']['sha256'],
                   'historical_accepted':t['historical_accepted_for_target'],'current_gorilla_strategy_accepted':None})
model=ROOT/(external+package+'client/model/ModelGorilla.java')
scope={'historical_structure_accepted':old['actual_cumulative_state']['legacy_structure_accepted_as_recorded'],
       'historical_three_targets':old['actual_cumulative_state']['target_specific_historical_accepted'],
       'target_ledger_checks':checks,'old300_cards_rechecked':False,
       'gorilla_existing_identity':'AlexsMobs:Gorilla','gorilla_already_in_old1000':True,
       'old_model_source_hash_matches':H(model)==lib['AlexsMobs:Gorilla']['sha256'],
       'existing_gorilla_credit_scope':lib['AlexsMobs:Gorilla']['scope'],
       'current_applicable_complete_accepted_total':None,'gap':None,'new_accepted_credit':0,
       'specific_gaps':['Old Gorilla row is static bind-pose anatomy, explicitly excludes animation/texture posture; current reading extends this same identity, not another creature.',
                        'The300 cards belong to gongsun_wuwang/taoyan_zhishi/luban_yisha. No accepted target map establishes their complete arm-strike/stance/interrupt/reload applicability to this ape.',
                        'No cross-ledger semantic rig/state-machine equivalence map or independent whole-mechanism acceptance exists for current body scope.',
                        'External Citadel AnimationHandler/ModelAnimator tick, networking, reset internals are not present/read in selected local snapshot. External entity call sites do not prove engine behavior.',
                        'No native posture/contact, cancellation, chunk reload or multiplayer acceptance in this batch.']}
write('applicability.json',scope)

findings={
 'trigger':'Server startSkill421 requires alive valid enemy, sight, vertical delta<=3, horizontal range0..8, TimedAttack idle/cooldown/finite direction. AI tries at squared range<49; startSkill gate still applies. Navigation stops, facing/start tick/phase synchronize.',
 'clock':'SMASH421 windup24 active64 recovery42 =130ticks/6.5sec; impacts24,32,40,48,56,64,72,80. Server body motion at ages24..87 is .125 forward/tick with loaded/border/collision cancellation. No animation callback causes damage.',
 'selection':'visualAnimation precedence death > nonzero skill smash/throw/leap > hurtTime>0 hurt > moving walk > idle. STUN has no separate visual branch. A canceled action can show jaw-only hurt while hurtTime lasts, then walk/idle while gameplay stun remains.',
 'controller':'body transition0, reset when synced skillStart changes, loop idle/walk; hold-last all other clips. In RUNNING with active skill/death, adjustTick uses world gameTime - skillStart + partial; first reset pass retains base local timing. Not a full framework interpolation proof.',
 'hierarchy':'root->ribcage->{ape_skull->ape_jaw, upperarms->forearms->knuckles}; root->haunch->hindlegs->ankles->feet. Ribcage pitch therefore propagates to skull/arms; compensating local skull/arm tracks do not equal world-space independence.',
 'pose':'SMASH ribs reach-65deg and skull/upperarms+65 at10ticks, hold18, return24. Forearms windup(30,0,+/-70)at10, +/-90at14, +/-70at18; upperarms translate +/-8 by24 and hold88, return104. Alternating forearm lift cycles: left minima pitch-60 at28/44/60/76, right36/52/68/84, each returns by following8tick boundary. Timing table retains every tick and original displacement.',
 'contact_limit':'Server alternating impact side code begins side+1 at24. The lifted forearm phase must be checked against actual knuckle world-space ground contact and side basis; raw channel coincidence is not contact or clipping acceptance. No automatic retiming or bug declaration.',
 'interrupt':'Only accepted damage while alive on server, actual health loss>=12 and WINDUP invokes stun30. ACTIVE/RECOVERY hits do not invoke that custom cancel. SMASH movement failure stuns40. TimedAttack.cancel clears current/start/target/fired but retains cooldown. advance guards against callback changing/killing actor before further frames.',
 'exit':'At age130 advance cancels and sync clears skill. Death cancels action, sets deathStart, selects death, suppresses renderer whole-model death roll and removes at90ticks. Held-rock visibility is only read as attachment boundary; object untouched.',
 'reload':'TimedAttack saves skill/start/cooldowns/stun/origin/direction/target/fired; validates finite/valid-age on load. BronzeGorilla stores LastCombatTick; next combat cancels active if gap>1 or clock reverses. Thus no claimed seamless continuation across unloaded time. Already elapsed impacts become consumed, not dumped late; native exact-once/multiplayer behavior remains untested.',
 'reference':'Alex Gorilla uses non-Steve long-arm chest/haunch hierarchy. doHurtTarget requests20tick attack only when NO_ANIMATION; setAnimation requests standing/maxStandTime10; model arms wind7, strike5, recover6. Entity hit at tick10; stand progress ramps0..10 and overlays keyframes, then locomotion/head overlays. hurt only clears ordered sitting and delegates; it does not directly cancel current attack. Standing/forced sitting persist, current animation/tick do not appear in custom NBT. Chest-pound goal can stop at tick>=10 without clearing the40tick animation; engine end/reset is explicitly unverified here.',
 'transfer':'Learn separate body stance progress from attack clip; couple current authored attack and authoritative shared clock, include context cancellation/reload in assessment. No external model/texture/keyframe copied.'}
receipt={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':'dynasty:hanshan_tongjia_juyuan',
 'whole_strategy':'Existing SMASH body: trigger -> selected state -> skeleton channels -> interruption/exit -> save/reload boundary',
 'kind':'complete selected local static call-chain review, not full engine/runtime acceptance','sources':sources,
 'external_pin':read(external+'source.json')['sha'],'findings':findings,
 'dedup':{'same_external_family_as_old1000':'AlexsMobs:Gorilla','new_creature_family_credit':0,
         'previous_related':['swindler-body-state-research-20261110','controller-continuity-research-20261110','native-damage-state-research-20261110'],
         'semantic_difference':'Existing swindler deceptive/flee persistence and generic same-chain renderer rules do not cover this current shared-world-clock multihit body/stance and cancel-on-time-gap strategy.',
         'not_separate_credits':['left/right arm','8impact frames','serverphase','renderer','helper','reload path']},
 'production_modified':False,'java_or_game_started':False,'main_checklist_modified':False,
 'ownership':'Body/skeleton/animation and attachment interfaces only; all object models/textures/UV and armor materials untouched.',
 'applicable_whole_accepted_total':None,'gap':None,'new_accepted_credit':0}
if (OUT/'raw-channel-timeline.png').exists():
    receipt['viewed_diagnostic']={'path':str(OUT/'raw-channel-timeline.png'),
      'sha256':H(OUT/'raw-channel-timeline.png'),'actually_viewed':True,
      'observation':'Alternating forearm pitch/local-Y excursions occur within ACTIVE; return to baseline by recovery. Windup has sparse authored pose excursions. Not world-space matrices, ground contact or full runtime playback.',
      'new_reference_credit':0}
write('receipt.json',receipt)
lines=['# 铜臂巨猿：整套砸击身体策略核查','',
 '本批只读；保持已认可模型、动作、装备和玩法。不是游戏验收。',
 '',*['- **'+k+'**：'+v for k,v in findings.items()],
 '', '旧1000中的 Gorilla 已是同一结构参考，本次延伸动作研究不新增生物数。旧300卡不自动适用于当前巨猿动作范围；累计与缺口保持 null，详见 applicability.json。',
 '', '逐 tick 原始通道与服务器阶段见 timeline.json；曲线图只表示原始通道，不代表全局骨骼接触。']
(OUT/'README.md').write_text('\n'.join(lines)+'\n')
verification={'source_hashes_match':all(H(Path(s['path']))==s['sha256'] for s in sources),
 'all_smash_bones_exist':all(b in names for b in smash['bones']),
 'timeline_samples':len(timeline),'clip_ticks':smash['animation_length']*20,
 'all_impacts_inside_active':all(24<=t<88 for t in impacts),
 'target_ledger_hashes_match':all(c['hash_matches_previous'] for c in checks),
 'production_modified':False,'game_or_java_started':False}
write('verification.json',verification)
write('progress.json',{'receipt':evidence(str((OUT/'receipt.json').relative_to(ROOT)),'new complete selected static strategy'),
 'previous_progress':'docs/art/bestiary-v43/controller-continuity-research-20261110/progress.json',
 'whole_selected_local_static_strategies_completed':1,'external_engine_complete':False,
 'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,'all_tasks_complete':False,
 'next':'Next distinct local body candidate: snail_maiden shell/withdrawal -> flee/exit/reload strategy, only after this receipt. Existing approved bodies remain protected; no production before applicable gate.'})
write('handoff-metadata.json',{k:{'path':str(OUT/n),'sha256':H(OUT/n)} for k,n in [('receipt','receipt.json'),('progress','progress.json'),('applicability','applicability.json'),('verification','verification.json')]})
print(json.dumps({'handoff':str(OUT/'handoff-metadata.json'),'sha256':H(OUT/'handoff-metadata.json'),'verification':verification},indent=2))

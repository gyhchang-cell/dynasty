"""Read-only whole existing body policy; retains original task and owner limits."""
from pathlib import Path
import hashlib,json,datetime
R=Path(__file__).resolve().parents[4];O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads((R/p).read_text())
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def src(p,scope):return {'path':str(R/p),'sha256':sha(R/p),'read_scope':scope}
actor='src/main/java/com/dynasty/blueprint/elite/RageCorpse.java'
renderer='src/main/java/com/dynasty/blueprint/elite/client/RageCorpseRenderer.java'
geo='src/main/resources/assets/dynasty/geo/blueprint/elite/banshan_jiazhou_shikuang.geo.json'
anim='src/main/resources/assets/dynasty/animations/blueprint/elite/banshan_jiazhou_shikuang.animation.json'
sources=[src(actor,'entire class: trigger/skill priority/motion/impact/interrupt/death/save-load'),
 src(renderer,'entire class: bindings/death_mud visibility/death roll/culling'),
 src(geo,'all bone parent/pivot/rotation metadata only, no object geometry work'),
 src(anim,'all sparse channels plus extracted sampled-curve ranges/ends and spin/blood phase samples; not complete native playback')]
prior_path='docs/art/bestiary-v43/gorilla-smash-body-research-20261110/receipt.json'
prior=load(prior_path);reuse=[]
for s in prior['sources']:
 if any(t in s['path'] for t in ['TimedAttack.java','SkillDefinition.java','AttackState.java','BronzeGorilla.java']):
  reuse.append({'path':s['path'],'sha256':s['sha256'],'current_hash_matches':sha(Path(s['path']))==s['sha256'],
   'scope':'Reuse prior whole selected giant-ape body strategy / unchanged clock. No helper fragments counted anew.'})
p=Path('/Users/a15356015027/Desktop/code x提示词/cod1.txt');lines=p.read_text().splitlines()
s=next(i for i,l in enumerate(lines) if l.startswith('### 10. 搬山甲胄尸狂'));e=next(i for i in range(s+1,len(lines)) if lines[i].startswith('### '))
task={'file':str(p),'file_sha256_at_read':sha(p),'original_task_identifier':'cod1.txt §10 搬山甲胄尸狂',
 'line_start':s+1,'line_end':e,'original_text':'\n'.join(lines[s:e]),'runtime_id':'dynasty:banshan_jiazhou_shikuang',
 'remaining_original_acceptance':['build','combat/singleplayer/multiplayer','actual tomb entrance','reload/reconnect/restart','stress/balance'],
 'status':'PARTIAL preserved; source-only body review does not complete/delete gameplay acceptance',
 'body_owner':'Existing body geometry/bones/body actions/interfaces only',
 'object_owner':'Texture specialist: chains/shackles/back blades themselves, all model/texture/UV. Bone motion/parent read only here.'}
write('original-task-scope.json',task)
findings={
 'start_priority':'startSkill server/alive/enemy/sight/vertical delta<=3 and configured horizontal range checks, leap landing safety/home checks, then unchanged TimedAttack idle/cooldown/finite-input gate. AI tries LEAP when squared distance>25, SPIN when<25, otherwise BLOOD; range==25 falls to BLOOD. Actual min/max gates still apply.',
 'spin_strategy':'Skill40122windup+80active+40recovery=142ticks. Server requests .03 forward/tick for ages22..101 (2.4blocks only if all moves succeed), keeps entity facing original attack direction. Authored ROOT yaw0at22->2160at102, holds to142 (six visual turns). All child body/supports inherit this rendered rotation; server circular damage is not animated root geometry. Hits22,32,42,52,62,72,82,92. Logical facing stays fixed while mesh spins. No claim rotating AABB or skeletal collision.',
 'spin_body':'coffin_shell windup rocks pitch+3/-3/+3 then returns0at22; recovery rolls+4at112/-4at122/0at142. Foreknuckle roll has sampled windup left+50/right-50at10, returns0at22 and remains baseline. Chain root local yaw reaches-180at22 against authored default180; this interface change is not object asset modification or verified chain collision.',
 'blood_strategy':'Skill40316windup+25active+40recovery=81ticks, hits16/26/36. Facing locked from attack direction each combat tick. Existing front-knuckle windup rolls reach +/-90 and local Y up to11.03 then return0at16. Blood gates open from +/-8at14 to +/-70at16, hold to36 and close by50; viscera scales1.08at14 and1at16. Gates and viscera are children of coffin_shell, front supports independently root-parented. Server emission origin is bodyposition+direction*1.2+(0,1.5,0), not a bone ticket. Gate/stream alignment requires runtime/world-space validation, no fake completed contact.',
 'leap_context':'Skill40214windup+20active+50recovery=84ticks, hit33. Physical server clipped parabola age14..33 uses u=(age-13)/20 and vertical8*u*(1-u), maximum2blocks above interpolated baseline. travel suppresses its extra integrator only during this server skill interval, never enables NoGravity. Authored supports lift at14..33 and shell pitches at contact; actual ground contact remains unverified.',
 'interrupt_exit':'Accepted actual health loss>=12 while server/alive/WINDUP -> stop30stun; movement notloaded/border/obstruction or bad landing -> stop40stun. ACTIVE/RECOVERY ordinary hurt does not use that custom interrupt. stop cancels current action but cooldown remains through reused TimedAttack. At total end current/start clear; missed elapsed frames never dump late damage.',
 'visual_priority':'death > active401spin/402leap/403blood > hurtTime hurt > horizontal movement walk > idle. Same zero-transition controller/start-reset/world-clock RUNNING adjustment as unchanged giant ape; reusing it adds no reference credit. Gameplay STUN has no dedicated clip; no assumption that hurt is shown throughout recovery/stun.',
 'death_exit':'die cancels attack/navigation/target, syncs deathStart;80tick removal and4secdeathclip align numerically. Renderer death maxrotation0, death_mud visible flag only while dead; channel keeps mudscale0through16 then1at24, hold60 and0at80. RootY compresses to.45at12, then full-root scale0by78. Blood gates open+/-90by8; back-blade interface transforms depart8..30. No new object/server-entity work. Mud inherits root scale, not an independent floor effect.',
 'reload':'Custom NBT keeps EliteAttack, landing+finite bounded offsets, LastCombatTick/deathStart/loot/home. Invalid saved leap landing cancels leap. Next combat cancels active on gap>1 or clock reversal; cannot claim seamless unloaded animation. Same consumed-frame/cooldown protections reused; exact client interpolation/network/load ordering not executed.',
 'complete_comparison':'Closest already fully reviewed local strategy is BronzeGorilla SMASH: both four-support bodies with fixed server clock and strong windup; ape strikes alternate forearm motion with .125step and24/64/42 phases. Corpse401 instead rotates whole root during80active and rocks recovery while moving. Corpse403 instead exposes paired abdominal gates on a fixed direction. These are whole body strategies, not new helpers or new Gorilla species. Do not transplant ape geometry/keyframes or count this comparison as a new external family.',
 'limits':'This batch completes the selected local static actor policy trace, not native playback, texture acceptance, full continuous curve visual examination or framework internals. No production/model/animation/PNG/UV edits. No Java/game/QA/new instance/sharedJar changes.'}
write('body-findings.json',findings)
a=load(anim)['animations'];names={b['name'] for b in load(geo)['minecraft:geometry'][0]['bones']}
def sample(v,t):
 if isinstance(v,list):return v
 q=sorted((float(k)*20,x) for k,x in v.items())
 if t<=q[0][0]:return q[0][1]
 for (s,x),(e,y) in zip(q,q[1:]):
  if t<=e:return [u+(v-u)*(t-s)/(e-s) for u,v in zip(x,y)]
 return q[-1][1]
timeline=[];spin=a['animation.banshan_jiazhou_shikuang.spin'];blood=a['animation.banshan_jiazhou_shikuang.blood']
for t in range(143):
 timeline.append({'tick':t,'spin_phase':'WINDUP' if t<22 else 'ACTIVE' if t<102 else 'RECOVERY' if t<142 else 'IDLE',
 'spin_impact':t in [22,32,42,52,62,72,82,92],
 'spin_root_yaw':sample(spin['bones']['root']['rotation'],t)[1],
 'blood_gate_yaws':[sample(blood['bones'][side+'_blood_gate']['rotation'],t)[1] for side in ['left','right']],
 'blood_impact_if_blood_skill':t in [16,26,36]})
write('timeline.json',{'kind':'Independent hypothetical raw SPIN/BLOOD channels on same plot time, never simultaneous runtime skills','samples':timeline})
app=load('docs/art/bestiary-v43/tide-yasha-body-policy-20261110/applicability.json')
write('applicability.json',{'historical_structure_accepted':app['historical_structure_accepted'],
 'historical_target100s':app['historical_target100s'],'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,
 'reused_whole_strategy_receipt':src(prior_path,'prior giant-ape whole static body, unchanged helpers hash-checked'),
 'missing':['No current-target accepted complete spin/gate/death/reload applicability map of old1000 or300cards.',
 'No world-space support/chain/abdominal gate vs emission alignment or actual rotating hit-volume/native combat acceptance.',
 'Independent implementation acceptance and cross-ledger semantic dedup incomplete; same Gorilla study reused, not added again.'],
 'old300_cards_rescanned':False,'historical_counts_not_reset':True})
verification={'current_sources_match':all(sha(Path(x['path']))==x['sha256'] for x in sources),
 'reused_whole_source_hashes_match':all(x['current_hash_matches'] for x in reuse),
 'all_clip_bones_exist':all(b in names for c in a.values() for b in c['bones']),
 'clip_contract_ticks':{k:[a['animation.banshan_jiazhou_shikuang.'+k]['animation_length']*20,v] for k,v in [('spin',142),('leap',84),('blood',81),('death',80)]},
 'production_modified':False,'java_or_game_started':False}
write('verification.json',verification)
write('receipt.json',{'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_task':task['original_task_identifier'],
 'runtime_id':task['runtime_id'],'sources':sources,'reused_sources':reuse,'findings':findings,
 'one_whole_selected_static_actor_policy':True,'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,
 'production_modified':False,'java_or_game_started':False,'task_deletion_permitted':False})
(O/'README.md').write_text('# 搬山甲胄尸狂：完整身体策略\n\n原任务cod1.txt第10节，保持PARTIAL。\n\n'+
 '\n\n'.join('**'+k+'**：'+v for k,v in findings.items())+'\n')
write('progress.json',{'original_task':task['original_task_identifier'],
 'receipt':src(str((O/'receipt.json').relative_to(R)),'this selected complete local static body policy'),
 'previous_progress':'docs/art/bestiary-v43/tide-yasha-body-policy-20261110/progress.json',
 'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,'all_tasks_complete':False,
 'next':'Next distinct existing task candidate cod1.txt §11 墨家绝影刺客: verify existing class/ID and prior coverage, then complete cloak/body visibility/pin-break/exit/reload chain; no production before gate.'})
write('handoff-metadata.json',{k:{'path':str(O/n),'sha256':sha(O/n)} for k,n in
 [('receipt','receipt.json'),('progress','progress.json'),('task','original-task-scope.json'),('applicability','applicability.json'),('verification','verification.json')]})
print(json.dumps({'handoff':str(O/'handoff-metadata.json'),'sha256':sha(O/'handoff-metadata.json'),'verification':verification},ensure_ascii=False,indent=2))

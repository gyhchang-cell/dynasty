"""Document existing complete body-policy chain. Never writes production or task lists."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[4]; O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads((R/p).read_text())
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def src(p,scope):return {'path':str(R/p),'sha256':sha(R/p),'read_scope':scope}
actor='src/main/java/com/dynasty/blueprint/elite/InkAssassin.java'
geo='src/main/resources/assets/dynasty/geo/blueprint/elite/mojia_jueying_cike.geo.json'
anim='src/main/resources/assets/dynasty/animations/blueprint/elite/mojia_jueying_cike.animation.json'
sources=[src(actor,'entire actor: trigger, movement, target/visibility, interruption, death, save/load'),
 src('src/main/java/com/dynasty/blueprint/elite/client/InkAssassinRenderer.java','entire file, actor root/children/death_wash body visibility; object renderer declarations context only'),
 src('src/main/java/com/dynasty/blueprint/elite/InkSpike.java','entire class only as producer of body interruption and anchor cast identity/lifetime; no object asset authoring'),
 src(geo,'all body/attachment bone parent,pivot,default rotation metadata; not object cube or UV work'),
 src(anim,'all seven authored clips read, all channels sparse and fully displayed')]
prior='docs/art/bestiary-v43/tide-yasha-body-policy-20261110/receipt.json'
reuse=[]
for s in load(prior)['unchanged_reused_helpers']:
 reuse.append({**s,'current_hash_matches':sha(Path(s['path']))==s['sha256']})
taskfile=Path('/Users/a15356015027/Desktop/code x提示词/cod1.txt');ls=taskfile.read_text().splitlines()
s=next(i for i,l in enumerate(ls) if l.startswith('### 11. 墨家绝影刺客'));e=next(i for i in range(s+1,len(ls)) if ls[i].startswith('### '))
task={'file':str(taskfile),'sha256_at_read':sha(taskfile),'original_task_id':'cod1.txt §11 墨家绝影刺客',
 'line_start':s+1,'line_end':e,'heading':ls[s],'runtime_id':'dynasty:mojia_jueying_cike',
 'pending_text_copied':False,'status':'original PARTIAL retained',
 'remaining_native_subscope':['build','singleplayer/two-player combat','actual Tiangong city entrance','reload/reconnect/restart','stress/balance','contact and interruption visibility acceptance'],
 'body_owner':'Existing 做建模的: body geometry/bones/actions and attachment interfaces',
 'object_owner':'Existing 做贴图的: daggers, spikes, pellets/accessory objects model/PNG/UV; this batch changes none'}
write('task-scope.json',task)
findings={
 'trigger':'startSkill validates server, alive, enemy, sight, heightdelta<=2 and configured range; FIELD additionally validates same-height four floor anchors and clear rays before tryStart. Same unchanged TimedAttack clock/cooldown gate reused. AI tries stealth at distanceSquared>16, field at<36, then mist; conditions still pass skill min/max gates. Partial field creation failure cancels rather than leave a body action running.',
 'conceal_whole_policy':'411 total111ticks=70windup+11active+30recovery, hit80. concealed() uses skill411 and age1..79 and notdead. combat sets Invisible by same age; renderer independently hides ROOT and children from concealed(), not transparency alone. Start clears target references on at most16 nearby mobs currently targeting this entity, not universal aggro immunity or collision removal.',
 'mark_and_backstab':'For age<70 follows target-derived behind point with floor validation; at70 stops tracking for last10ticks. At80 clears invisibility, tries one blink to saved mark with distance<=8, height<=2, home/loaded/full-body clearance/ground/ray gates. Faces target, requires rangeSquared<=4 and clear ray, then compares current target view dot offset<-.5 for3x versus1x damage. Turning cancels bonus, not necessarily the ordinary hit. Failed blink stops30stun.',
 'conceal_body_channels':'rootY scale1->.25by4, holds78, restores1at80; fold wings reach-/+20by4, hold78 and recover80. Most fold compression is under root hidden state, so authored scale alone is not a visible dissolve proof. Daggers/carriages are read only as attachment interfaces: local carriage X-/+5 and dagger yaw+/-180at80..86, return94. No dagger assets edited.',
 'field_whole_policy':'412 total92ticks=10windup+46active+36recovery, impacts15/27/39/51. Current cast must have four owned matching-start anchors during age10..55; target loss/out-of-home cancels. Four diagonal route stages begin10/22/34/46, each ten collision-step requests toward opposite corner. At begin tries bounded blink to route start; step verifies loaded/success displacement. Stage gaps20..21/32..33/44..45 do not run a step for next stage. Damage uses current body circle1.1, not mesh dagger tip. Four routes/hits are one strategy, no new reference credits.',
 'field_body_and_break':'Wings-/+15 at10 through56, recover64; carriage translation+/-5 and dagger turn held through56; carriage yaw alternates at attack ticks15/27/39/51. InkSpike accepted hurt or die invokes breakField; caster only stops30stun if current FIELD and owned spike castStart equals current attack.started. Anchor expiry56, missing/wrong/dead owner, cast mismatch or time gap discards anchor. Prior cast spikes cannot intentionally break a later cast. No native sweep or packet acceptance claimed.',
 'mist_context':'413 total59ticks=8windup+21active+30recovery, emits8. Real .16backward step at ages1..6, intended .96distance only if unobstructed. Wings flare-/+35at3, recover by8; heart scale1.15at6, reset8. Cloud cap/pellet renderer declarations were seen in actor context, but whole cloud effect lifetime/texture/native blind acceptance not reviewed here.',
 'state_priority_and_interrupt':'death > skills411/412/413 > hurtTime hurt > horizontal movement walk > idle. Accepted actual healthloss>=6 on alive server while WINDUP stops25stun. Missing/invalid target or out-of-home target stops20; blocked route/broken field/blink failure usually30. stop cancels attack retaining cooldowns, clears invisibility and field, stops navigation, cancels visual event, syncs immediately. No distinct STUN body clip; gameplay stun can display idle/walk after hurtTime ends.',
 'death_visibility':'die cancels attack, fields/clouds, invisibility/navigation/target; syncs deathStart and chooses3sec death. ROOT hidden calculation becomes false because concealed requires notdead. death_wash visible flag only while dead; scale0through14 then1at20,1.3XZat46 and0at60. Root Y compresses.18by12, XZgrow1.2by40, entire scale0by58. Death renderer adds no whole-body roll; server removes when max(deathTime,gameTime-deathStart)>=60. Root-child wash inherits compression, not independent world mesh.',
 'reload':'NBT stores EliteAttack, mark+finite bounded offsets, LastCombatTick/deathStart/loot/home. Invalid mark cancels action; alive reload syncs and derives Invisible from concealed(), dead reload explicitly clears it. Next combat gap>1 or clock reversal cancels active, clears field/invisibility. Shared TimedAttack fired/cooldown safeguards retained, no phase-continuity claim. Exact client scale reset when switching to clip without root scale, network visibility ordering and death/load rendering remain native acceptance gaps.',
 'dedup_comparison':'Closest completed local whole body is TideYasha: both use actor-dependent root hiding, but Yasha dive hides9..29 and emerges once30; this stealth has moving mark->10tick lock->back-angle check80 plus matching-cast breakable field. Shared controller/clock and hide helpers are reused, not counted as another reference. Existing body is folded ink ray, not a human conversion.',
 'limits':'Complete selected actor static body policy, not whole runtime/client engine or object effects acceptance. No model/PNG/UV/animation/logic edits, no Java/game/QA/instance/sharedJar/main list changes.'}
write('body-findings.json',findings)
a=load(anim)['animations'];names={b['name'] for b in load(geo)['minecraft:geometry'][0]['bones']}
def sample(v,t):
 if isinstance(v,list):return v
 q=sorted((float(k)*20,x) for k,x in v.items())
 if t<=q[0][0]:return q[0][1]
 for (s,x),(e,y) in zip(q,q[1:]):
  if t<=e:return [u+(v-u)*(t-s)/(e-s) for u,v in zip(x,y)]
 return q[-1][1]
stealth=a['animation.mojia_jueying_cike.stealth'];field=a['animation.mojia_jueying_cike.field']
write('timeline.json',{'kind':'conditional source contract + raw channels, hypothetical independent skills; not native interpolation/path/visibility playback',
 'samples':[{'tick':t,'concealed_if_uninterrupted':1<=t<80,'mark_tracks_if_stealth':t<70,
 'stealth_impact':t==80,'stealth_root_scale':sample(stealth['bones']['root']['scale'],t),
 'field_impact_if_field':t in [15,27,39,51],
 'left_wing_local_rotation_if_field':sample(field['bones']['left_fold_wing']['rotation'],t)} for t in range(112)]})
old=load('docs/art/bestiary-v43/reference-reconciliation-20261110/receipt.json')
write('applicability.json',{'historical_structure_accepted':1000,'historical_target100s':old['actual_cumulative_state']['target_specific_historical_accepted'],
 'current_target':task['runtime_id'],'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,
 'old300_cards_rechecked':False,'historical_counts_not_reset':True,
 'reuse_receipt':src(prior,'completed TideYasha static whole policy reused for semantic comparison, not new reference'),
 'specific_missing':['No accepted current-target mapping from old1000 bind-pose structures to complete stealth/field/visibility/reload strategies.',
 'Historical100s for gongsun_wuwang/taoyan_zhishi/luban_yisha remain their original scopes, not a qualified gate for InkAssassin.',
 'No independent complete-implementation acceptance/cross-ledger inheritance dedup for this target.',
 'Missing actual hidden-but-hittable combat, late-stage mark lock, turn-away bonus, broken-anchor interruption, cancellation scale restoration and multiplayer/reload acceptance.']})
verification={'source_hashes_match':all(sha(Path(s['path']))==s['sha256'] for s in sources),
 'reused_helpers_match':all(s['current_hash_matches'] for s in reuse),
 'all_clip_bones_exist':all(b in names for c in a.values() for b in c['bones']),
 'clip_contract_ticks':{n:[a['animation.mojia_jueying_cike.'+n]['animation_length']*20,t] for n,t in [('stealth',111),('field',92),('mist',59),('death',60)]},
 'production_modified':False,'java_or_game_started':False}
write('verification.json',verification)
write('receipt.json',{'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'task':task,
 'sources':sources,'reused_helpers':reuse,'findings':findings,
 'whole_static_actor_policies_reviewed':1,'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,
 'production_modified':False,'java_or_game_started':False,'task_deletion_permitted':False})
(O/'README.md').write_text('# 墨家绝影刺客：完整身体动作政策\n\n原任务cod1.txt第11节保持PARTIAL，原待办正文不复制。\n\n'+
 '\n\n'.join('**'+k+'**：'+v for k,v in findings.items())+'\n')
write('progress.json',{'task':task['original_task_id'],'receipt':src(str((O/'receipt.json').relative_to(R)),'selected complete static body policy'),
 'previous_progress':'docs/art/bestiary-v43/rage-corpse-body-policy-20261110/progress.json',
 'new_accepted_credit':0,'applicable_whole_accepted_total':None,'gap':None,'all_tasks_complete':False,
 'next':'Continue cod1.txt §13 青灯判官鬼差 body/book articulation/mark-cast/cage interruption/death/reload, verify prior whole-owner coverage first; §12 giant-ape selected smash already reviewed.'})
write('handoff-metadata.json',{k:{'path':str(O/n),'sha256':sha(O/n)} for k,n in [('receipt','receipt.json'),('progress','progress.json'),('task','task-scope.json'),('applicability','applicability.json'),('verification','verification.json')]})
print(json.dumps({'handoff':str(O/'handoff-metadata.json'),'sha256':sha(O/'handoff-metadata.json'),'verification':verification},ensure_ascii=False,indent=2))

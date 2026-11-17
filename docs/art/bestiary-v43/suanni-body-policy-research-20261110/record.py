"""Selected static body policy + one external implementation study. No asset writes."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[4]; O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads((R/p).read_text())
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def src(p,scope):return dict(path=str(R/p),sha256=sha(R/p),read_scope=scope)
ID='zhenmu_suanni_tonghou';base='src/main/resources/assets/dynasty/'
geo=base+f'geo/blueprint/elite/{ID}.geo.json';anim=base+f'animations/blueprint/elite/{ID}.animation.json'
g=load(geo)['minecraft:geometry'][0];a=load(anim)['animations'];names={b['name']for b in g['bones']}
tp=Path('/Users/a15356015027/Desktop/code x提示词/cod1.txt');ls=tp.read_text().splitlines()
s=next(i for i,l in enumerate(ls)if l.startswith('### 15. 镇墓狻猊铜吼'));e=next(i for i in range(s+1,len(ls))if ls[i].startswith('### '))
task=dict(original_task_id='cod1.txt §15 镇墓狻猊铜吼',file=str(tp),sha256_at_read=sha(tp),line_start=s+1,line_end=e,heading=ls[s],runtime_id='dynasty:'+ID,
 pending_text_copied=False,status='original PARTIAL retained',body_owner='existing 做建模的',object_owner='existing 做贴图的; no item/accessory/armor model PNG UV edits')
sources=[src('src/main/java/com/dynasty/blueprint/elite/BronzeSuanni.java','entire actor: trigger, fixed orientation, head sweep/muzzle interface, interrupt/death/reload'),
 src('src/main/java/com/dynasty/blueprint/elite/client/BronzeSuanniRenderer.java','entire file; body/dead material selection and culling; effect scaling context only'),
 src('src/main/java/com/dynasty/blueprint/elite/SuanniEffect.java','entire class as body-controlled flame orientation/cast cancellation and lifetime boundary; no effect object authoring'),
 src('tools/blueprint/generate_bronze_suanni.py','entire file read; leg solver, gait, head and death compensation; exporter/item/texture/refiner calls NOT executed'),
 src(geo,'all bone hierarchy/pivots; no production geometry or UV modification'),
 src(anim,'all sparse idle/fire/roar/hurt channels and all death-position channels read; dense walk/stomp solver provenance reviewed from generator, not claiming native or exhaustive dense replay')]
prior=load('docs/art/bestiary-v43/tide-yasha-body-policy-20261110/receipt.json')
reuse=[dict(v,current_hash_matches=sha(v['path'])==v['sha256'])for v in prior['unchanged_reused_helpers']]
findings={
 'trigger_selection':'Server/alive/enemy/sight, abs heightdelta<=3 and configured horizontal range. Cast freezes horizontal velocity/navigation and fixed facing; server advances once per game tick even noAI. AI checks close roar first when squared distance<16, then fire, then stomp; actual cooldown/range gates still apply. Body priority death >451fire/452stomp/453roar >hurtTime >moving walk >idle.',
 'fire_policy':'451=24windup+60active+44recovery=128ticks, hits24/34/44/54/64/74. Whole body always faces cast direction. Independent head yaw reaches-45 at24,+45at83 and holds through84; server sweep clamps -45+(age-24)*90/59 identically. Jaw reaches25deg at24, holds84 and resets100. Bellows contract2units at24 and return26; paired mane gears counterrotate720deg by24 and2520by84. Body remains planted; no chasing target with head after cast start.',
 'fire_interface':'fireMuzzle uses fixed head pivot forward.75 plus swept outlet1.25 and height1.4375, flame length collider-ray clips up to8m. One visible flame created24 if effect cap allows, follows same head direction untilage84; actor damage is six explicit strip pulses, not continuous contact from mesh. Thus last visible portion74..83 is not six new hits. Effect root length scaling is read-only interface, no effect model/texture work. Exact current refined mouth/outlet alignment remains native/geometry acceptance gap.',
 'stomp_policy':'452=10+20+32=62ticks, impacts10/14/18/22/26. Left front paw endpoint lifts6units by9, drops by10; current upper/shin/paw channels share densified analytic endpoint control. Ground origin derived from same cast-facing offset and five points .5/1.5/2.5/3.5/4.5 beyond origin. Invalid floor/blocked ray sets persisted crackStopped and stops later crack creation, not the body attack clock. Existing live cracks may outlast62tick body clip; cancellation/death clears all. No new floor edits or gameplay mechanics authored.',
 'roar_policy':'453=14+1+45=60ticks; head pitches-25 and jaw30 at14, holds24, recovers40; gear braces+/-22 at14..24. Server at14 uses radius4 LOS-gated knockback and shield stop/cooldown60. Native resistance/terrain determine displacement; do not claim fixed6m. Root body not translated by authored roar, no physics-free force illusion accepted.',
 'four_foot_support':'Four two-link upper/shin chains descend from hollow_furnace, but each paw is independent root child; bronze ball child follows paw. Generator walk2.4sec assigns quarter-cycle phase offset; each paw swings/lifts only first quarter, then stays planted for remaining three quarters in endpoint space. Authored balls rotate360 eachcycle with local extent correction; this is a rolling bronze support design, not tiger skeletal gait copied. Actual speed vsworld displacement/terrain contact and final refiner geometry clearance not accepted from source alone.',
 'death_policy':'90tick death, no vanilla whole-body roll. Furnace starts sink/compress at8, reachesY-18/Yscale.45at24 and holds; core grows1.2at8 then0at16. Dead texture switches at16. Head pitches35at24, jaw35by10. Paw/ball root chains stay separate while upper limbs remain furnace children; limb and head position corrections are explicit, intentional broken-collapse geometry, not a successful joined live IK pose. Source compensation computed before v33/v34/v35 body refiners; no claim it remains grounded against actual terrain.',
 'interrupt_recovery':'Accepted actual healthloss>=10 while WINDUP stops35, clears effects/nav/horizontal velocity and syncs skill0. No custom ACTIVE interruption by ordinary hit in this actor. Timegap>1/reversal during active action cancels and clears effects. Skill START change resets controller; current hurtTime drives short hurt then idle/walk, no separate stun body clip. Native restoration of head/jaw/gear pose on clip switch remains to verify.',
 'reload':'Saves EliteAttack, home/site, LastCombatTick, DeathStart, LootDropped, CrackStopped. Invalid loaded attack clears owned effects; death load clears skill and restores death clock. Loaded active action with later combat timegap cancels. Effect has owner/epoch/born/lastTick/pulse persistence; flame additionally requires matching skill451/current epoch andage24..83. Cracks bounded60ticks but not required to remain in STOMP. No native restart/reconnect acceptance or arbitrary persistence reset.',
 'limits':'Original cod1 task remains PARTIAL. This is current static actor body policy and selected external behavior study, not all seven clips dense numerical acceptance or gameplay completion. No production asset/gameplay edits, Java/game/QA/instance/sharedJar/main checklist/prompt cleanup/commit/push.'}
write('task-scope.json',task);write('body-findings.json',findings)
refroot='build/creature-reference-1000/AlexModGuy__AlexsMobs/src/main/java/com/github/alexthe666/alexsmobs/'
model=src(refroot+'client/model/ModelTiger.java','entire model: hierarchy, all keyframes, setupAnim pose blends/walk/run/target head and render restoration')
entity=src(refroot+'entity/EntityTiger.java','selected complete AIMelee nested goal and tick, hurt, animation accessors, registerGoals, sync/save-load related sections; not whole entity/base/Citadel internals')
historical=load('docs/art/creature-mc-v35/reference-ledger.json')['AlexsMobs:Tiger']
upstream=json.loads((O/'upstream-byte-verification-curl.json').read_text())
bound=len(upstream)==2 and all(v.get('matches_local') and v.get('exit_code')==0 for v in upstream)
assert bound
reference=dict(identity='AlexsMobs:Tiger',historical_structure_record=historical,model=model,entity=entity,
 model_hash_matches_historical=historical['sha256']==model['sha256'],
 local_cache_has_own_git=False,parent_git_not_source_revision=True,entity_commit_provenance_verified=bound,upstream_byte_comparison=upstream,
 provenance_note='Cache lacks .git; git -C resolves Dynasty parent, its HEAD is NOT AlexsMobs revision. Model and entity fetched from official raw.githubusercontent.com at historical pin09755dade2cfbdf14839e026d3af446f9d3ff843 using system curl with TLS verification enabled; both match local bytes. Initial Python certificate failure retained separately, no TLS bypass.',
 selected_policy='one related four-legged predator melee/stance implementation, not one reference per paw/keyframe/pose',
 observations={
 'trigger':'AIMelee starts when live target exists; dist<12 +NO_ANIMATION+onGround+cooldown0+notHolding selects20tick leap and sets70attempt cooldown. Otherwise cooldown>0 or water plus close<4+targetWidth and NO_ANIMATION chooses either15tick paw.',
 'model_timing':'Paw variants each5tick preparation +3tick body/forelimb drive +2tick follow-through +5reset. Actor damage condition is animationTick8; matches end of second stage. Head/tail/body/hindlegs coordinate: torso lifts/leans, hindlegs counterrotate, striking forelimb swings; not isolated paw rotation. Left/right are mirrored variants, one policy credit candidate only.',
 'leap':'Model5prepare+5extend+5hold+5reset. Entity stops navigation and faces target during leap, applies launch velocity on ground at ticks5..10, attempts close contact when tick>=15, then running/stealth off and holding on. No explicit once-hit latch in selected leap branch; do not claim exactly one damage attempt independent of native invulnerability.',
 'continuous_body':'setupAnim resets default pose then applies keyed animation and locomotion/pose layers; running has torso/head counter-bob, slow walk has opposed torso/head flap. Sit/sleep/hold blend progress interpolated from actor previous/current values; sleep suppresses faceTarget, hold spreads forelimbs. These functions show complete-body force/attention cues, not reusable numerical assets.',
 'interrupt_and_reload_limit':'AIMelee.stop clears running/stealth/holding, not explicitly current animation; selected hurt override removes attacker blessing but does not replace animation. Tick ends with Citadel AnimationHandler update. Save/load overrides persist sitting/sleeping/white, not these animation/holding fields. Inherited death, packet/reset and Citadel internals not read here; no full framework or restart guarantee.',
 'application':'Compare tiger torso/hindleg counterbalance with Suanni fixed three-foot endpoint support and planted head-sweep. Preserve bronze-lion mechanical gait; learn coordinated body force and attention, do not import tiger mesh/texture/angles. Whether Suanni requires posture changes cannot be accepted from source alone and production gate remains unmet.'},
 dedup=dict(new_family=False,extends_prior_static_family=True,new_accepted_credit=0,independent_semantic_acceptance='pending',applicable_whole_accepted_total=None,gap=None))
write('tiger-whole-policy-study.json',reference)
def sample(v,t):
 if isinstance(v,list):return v
 q=sorted((float(k)*20,x)for k,x in v.items())
 if t<=q[0][0]:return q[0][1]
 for (s,x),(e,y)in zip(q,q[1:]):
  if t<=e:return [u+(v-u)*(t-s)/(e-s)for u,v in zip(x,y)]
 return q[-1][1]
f=a['animation.'+ID+'.fire']['bones']; timeline=[]
for t in range(129):
 yaw=sample(f['lion_head']['rotation'],t)[1];sweep=max(-45,min(45,-45+(t-24)*90/59))
 timeline.append(dict(tick=t,raw_head_yaw=yaw,server_sweep=sweep,head_sweep_error_if_active=abs(yaw-sweep) if 24<=t<84 else None,
 jaw_pitch=sample(f['hinged_lower_jaw']['rotation'],t)[0],hit=t in [24,34,44,54,64,74],flame_active_if_created=24<=t<84))
write('fire-timeline.json',dict(kind='raw linear authored channels and source timing; not native playback',samples=timeline))
checks=dict(source_hashes_match=all(sha(x['path'])==x['sha256']for x in sources),helpers_unchanged=all(x['current_hash_matches']for x in reuse),
 all_clip_bones_exist=all(b in names for c in a.values()for b in c['bones']),
 clip_ticks={n:[a['animation.'+ID+'.'+n]['animation_length']*20,t]for n,t in [('fire',128),('stomp',62),('roar',60),('death',90)]},
 active_head_sweep_max_error_degrees=max(r['head_sweep_error_if_active']or 0 for r in timeline),
 model_hash_matches_historical=reference['model_hash_matches_historical'],production_modified=False,java_or_game_started=False,native_accepted=False)
write('verification.json',checks)
write('applicability.json',dict(historical_structure_accepted=1000,historical_target100s_not_reset=True,new_accepted_credit=0,
 applicable_whole_accepted_total=None,gap=None,reused_identity='AlexsMobs:Tiger',
 missing=['Applicable complete implementation mapping/independent semantic acceptance and inheritance dedup','Native head-outlet/contact/stun reset, final-refined walk/death terrain/reload acceptance']))
write('receipt.json',dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),task=task,sources=sources,reused_helpers=reuse,
 findings=findings,related_external_study=reference,checks=checks,new_accepted_credit=0,applicable_whole_accepted_total=None,gap=None,
 production_modified=False,original_task_retained=True,task_deletion_permitted=False))
(O/'README.md').write_text('# 镇墓狻猊：身体动作与四足参考\n\n原任务保留；无生产修改，无实机通过。\n\n'+'\n\n'.join('**'+k+'**：'+v for k,v in findings.items())+'\n\n外部参考为Alex’s Mobs Tiger同一既有家族的选定近战/姿态链。模型和实体字节均与上游固定提交逐字节核实；不新增有效计数。\n')
write('progress.json',dict(original_task_id=task['original_task_id'],static_body_policy='saved; dense walk/death geometry acceptance not claimed',related_external_selected_policy='Tiger melee/stance saved, same historical family',
 new_accepted_credit=0,applicable_whole_accepted_total=None,gap=None,all_tasks_complete=False,production_modified=False,
 previous_progress='docs/art/bestiary-v43/golden-eagle-draw-death-research-20261110/progress.json',
 next=['Review dense Suanni walk/support and final-refined death contact if not already covered by current-input receipt','Native gaps remain; no production until applicable gate']))
write('handoff-metadata.json',{n:dict(path=str(O/(n+'.json')),sha256=sha(O/(n+'.json')))for n in ['receipt','progress','applicability','verification','task-scope','tiger-whole-policy-study','upstream-byte-verification','upstream-byte-verification-curl']})
assert all(abs(x-y)<1e-8 for x,y in checks['clip_ticks'].values())
assert checks['active_head_sweep_max_error_degrees']<1e-8
print(json.dumps(dict(handoff=str(O/'handoff-metadata.json'),sha256=sha(O/'handoff-metadata.json'),checks=checks),ensure_ascii=False,indent=2))

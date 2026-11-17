"""Selected existing dive policy evidence only; no production writes."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[4]; O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def src(p,scope):return dict(path=str(R/p),sha256=sha(R/p),read_scope=scope)
id='liefeng_jindiao_yushi'; base='src/main/resources/assets/dynasty/'
anim=base+f'animations/blueprint/elite/{id}.animation.json'; geo=base+f'geo/blueprint/elite/{id}.geo.json'
a=json.loads((R/anim).read_text())['animations']; g=json.loads((R/geo).read_text())['minecraft:geometry'][0]['bones']
sources=[src('src/main/java/com/dynasty/blueprint/elite/GoldenEagle.java','entire actor; selected dive through trigger/flight/interrupt/gravity/death/reload; rain/fan context only'),
 src('src/main/java/com/dynasty/blueprint/elite/client/GoldenEagleRenderer.java','entire file, body arrow visibility/dead texture/culling; object rotation context only'),
 src(geo,'all bone hierarchy/pivots/default rotations; not cube/UV production'),
 src(anim,'complete dive wing/outer-wing/body channels; idle/fly/fan/hurt wing channels and death sparse body/wing/scale/string interface channels; dense rain limb/string and death position curves NOT fully read')]
tp=Path('/Users/a15356015027/Desktop/code x提示词/cod1.txt'); lines=tp.read_text().splitlines()
s=next(i for i,l in enumerate(lines) if l.startswith('### 14. 烈风金雕羽士'));e=next(i for i in range(s+1,len(lines)) if lines[i].startswith('### '))
task=dict(original_task_id='cod1.txt §14 烈风金雕羽士',file=str(tp),sha256_at_read=sha(tp),line_start=s+1,line_end=e,heading=lines[s],
 runtime_id='dynasty:'+id,pending_text_copied=False,status='PARTIAL retained',body_owner='existing body specialist',object_owner='existing texture specialist; no bow/arrow object asset edits')
findings={
 'trigger':'DIVE443=16windup+16active+100recovery=132ticks, impact31. Server/alive/enemy/sight, heightdelta<=6, horizontal3..12, loaded floor searched2above/3below and home<=32. Landing fixed at cast start; face uses fixed horizontal direction. AI tries rain then fan then dive, so selected dive is not evidence it occurs at every distance/cooldown combination.',
 'actual_path':'During ages16..31, u=(age-15)/16 moves physical actor from origin toward fixed landing in16 collision-tested requests. Loaded expanded bounds and squared distance to wanted<=.04 required, otherwise stop40. Travel suppresses ordinary movement during server dive16..30 to avoid a second move; final step31 uses ground travel policy. These are source conditions, not successful native trajectory evidence.',
 'raw_channels':'Body local yaw0->720deg at16->1440at32 and holds132. Left/right wingZ-/+65at16..32 then recover-/+8at40. Outer-wing yaw+/-55 through full clip. Body local Yposition10.21 constant. At server impact31 raw yaw1395deg under linear key sampling, not1440 until32; no inference of true renderer easing/contact acceptance. Wings/body mesh rotation do not replace server hit circle.',
 'impact':'At31 requires squared distance landing<=.25 and sturdy ground below or stop40. Sets gravity on and fallDistance0; radius2,height3,circle360, at most16 enemies with line of sight, existing damage/knockback retained. No new collision range or damage edits.',
 'ground_and_interrupt':'grounded when dead, synced STUN, or skill443 age>=31. Accepted actual health loss>=8 during DIVE ages29..31 stops100; otherwise WINDUP heavy hit stops30. stop clears arrows, navigation and motion input, restores gravity and nonpositive vertical velocity. After cancel skill0 may display hurt then idle/fly; no dedicated grounded-STUN body clip. Whether the pose reads as grounded counter-window needs native observation, not automatic pose rewrite.',
 'visibility_death':'Renderer hides drawn_arrow unless alive skill441 age<30; after dive it stays hidden. Body uses separate dead PNG resource, no PNG edits here. Death enables gravity, clears arrows; sparse clip pitches body65deg by14ticks/90by28, folds wings by14, body scale1through56->0at84, server removal90. String interface scales0by8; actual broken object treatment belongs texture owner. Dense death position compensation not fully read, so no full death trajectory claim.',
 'reload':'Saved landing finite offsets within.51 and distance<=24, EliteAttack/last tick/death/loot/home. Invalid landing cancels. NoGravity derived during load before final skill sync, so transient ordering and subsequent combat/travel correction must be checked natively; not asserted as defect. Active time gap>1/reversal cancels and clears arrows. Dead clears skill; corpse lifetime90. Shared controller tick/reset logic reused, not a new reference.',
 'comparison':'Completed TideYasha dive has hide/emerge at30 and mark tracking through20; this eagle fixes mark at start and physically descends16..31, remains visible, with29..31 heavy-hit counter window. Distinct local strategy comparison, zero new accepted external credit.',
 'scope_boundary':'Selected existing dive static policy reviewed; whole rain draw/arrow split and full dense death motion NOT claimed. No production assets, gameplay, tests, instances, shared Jar, task text or coordinator checklist modified.'}
write('task-scope.json',task);write('body-findings.json',findings)
write('timeline.json',dict(kind='uninterrupted conditional source contract + raw linear key sampling, NOT native playback',
 samples=[dict(tick=t,physical_dive_fraction=(t-15)/16 if 16<=t<=31 else None,impact=t==31,
 heavy_counter_window=29<=t<=31,grounded_if_still_dive=t>=31,raw_body_yaw=min(t,32)*45) for t in range(133)],
 authored_dive_body_channels={k:a['animation.'+id+'.dive']['bones'][k] for k in ['raptor_body','left_wing','right_wing','left_outer_wing','right_outer_wing']}))
prior=R/'docs/art/bestiary-v43/tide-yasha-body-policy-20261110/receipt.json'
reuse=[dict(v,current_hash_matches=sha(v['path'])==v['sha256']) for v in json.loads(prior.read_text())['unchanged_reused_helpers']]
checks=dict(source_hashes_match=all(sha(x['path'])==x['sha256'] for x in sources),helpers_match=all(x['current_hash_matches'] for x in reuse),
 all_clip_bones_exist=all(b in {x['name'] for x in g} for c in a.values() for b in c['bones']),
 clip_ticks={n:[a['animation.'+id+'.'+n]['animation_length']*20,t] for n,t in [('rain',116),('fan',72),('dive',132),('death',90)]},
 production_modified=False,java_or_game_started=False)
write('verification.json',checks)
write('receipt.json',dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),task=task,sources=sources,reused_helpers=reuse,findings=findings,
 selected_static_dive_policy_reviewed=True,whole_actor_all_channels_reviewed=False,new_accepted_credit=0,applicable_whole_accepted_total=None,gap=None,
 production_modified=False,task_deletion_permitted=False,java_or_game_started=False))
write('progress.json',dict(original_task_id=task['original_task_id'],status='selected dive policy saved; whole actor pending',new_accepted_credit=0,applicable_whole_accepted_total=None,gap=None,
 previous_progress='docs/art/bestiary-v43/lamp-judge-body-policy-20261110/progress.json',
 next=['Read dense rain talon/limb/string curve with authoring source and contact interface, preserving object-owner scope',
 'Read death body position compensation curve before full death-policy acceptance',
 'Complete applicable-reference mapping/semantic dedup before production; native flight/contact/counter-window/death/reload pending']))
(O/'README.md').write_text('# 烈风金雕羽士：俯冲身体链路\n\n原任务保留；当前为选定俯冲的静态核对，非全角色验收。\n\n'+'\n\n'.join('**'+k+'**：'+v for k,v in findings.items())+'\n')
write('handoff-metadata.json',{n:dict(path=str(O/(n+'.json')),sha256=sha(O/(n+'.json'))) for n in ['receipt','progress','task-scope','verification']})
print(json.dumps(dict(handoff=str(O/'handoff-metadata.json'),sha256=sha(O/'handoff-metadata.json'),checks=checks),ensure_ascii=False,indent=2))

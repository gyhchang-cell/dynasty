"""Freeze live experiment evidence; no result here authorizes a release."""
from pathlib import Path
import sys,json,re,math,difflib,bisect
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/experiments-190'))
from summarize_app_trials import summarize,POSE
CANDIDATES={
 'top-repeat-ne':'191-top-window','top-repeat-nw':'191-top-window',
 'audit-nw':'192-input-audit','sharedtop-nw':'192-top-intersection',
 'launch-nw':'192-launch-support','launch-nw-retry':'192-launch-support',
 'continuation-nw':'192-continuation-support','sprint-nw':'192-sprint-motion',
 'pidclick-nw':'192-ordered-click','route-nw':'192-launch-route',
 'placement-nw':'192-placement-route','clear-top-nw':'192-clear-top',
 'clear-top-ne':'192-clear-top','clear-top-sw':'192-clear-top','clear-top-se':'192-clear-top',
 'clear-top-flat-nw':'192-clear-top','clear-top-switch-ne':'192-clear-top',
 'clear-shared-ne':'192-clear-shared-top','clear-shared-nw':'192-clear-shared-top','clear-shared-sw':'192-clear-shared-top','clear-shared-se':'192-clear-shared-top',
 'clear-cache-ne':'192-clear-cache-top','clear-cache-nw':'192-clear-cache-top','clear-cache-sw':'192-clear-cache-top','clear-cache-se':'192-clear-cache-top',
 'native-top-ne':'192-native-top','native-top-nw':'192-native-top','native-top-sw':'192-native-top','native-top-se':'192-native-top',
 'rise-cont-ne':'192-rise-continuation','rise-cont-nw':'192-rise-continuation','rise-cont-sw':'192-rise-continuation','rise-cont-se':'192-rise-continuation',
 'top-retry-ne':'192-top-retry','top-retry-nw':'192-top-retry','top-retry-sw':'192-top-retry','top-retry-se':'192-top-retry',
 'cont-retry-ne':'192-continuation-retry','cont-retry-nw':'192-continuation-retry','cont-retry-sw':'192-continuation-retry','cont-retry-se':'192-continuation-retry',
 'native-cont-ne':'192-native-continuation','native-cont-nw':'192-native-continuation','native-cont-sw':'192-native-continuation','native-cont-se':'192-native-continuation',
 'future-side-ne':'192-future-side','future-side-nw':'192-future-side','future-side-sw':'192-future-side','future-side-se':'192-future-side',
 'flat-nw':'192-top-retry','flat-ne':'192-top-retry',
 'fasttop-flat-nw':'191-fasttop-control','fasttop-flat-ne':'191-fasttop-control',
 'runway-flat-ne':'192-actual-runway','runway-flat-nw':'192-actual-runway','runway-rise-ne':'192-actual-runway','runway-rise-nw':'192-actual-runway',
 'flow-flat-ne':'192-flat-flow','flow-flat-nw':'192-flat-flow','flow-flat-sw':'192-flat-flow','flow-flat-se':'192-flat-flow',
 'pending-flat-ne':'192-pending-render','pending-flat-nw':'192-pending-render','pending-rise-ne':'192-pending-render',
 'frame-flat-ne':'192-frame-audit','frame-rise-nw':'192-frame-audit',
 'logical-rise-nw':'192-logical-gate','logical-rise-ne':'192-logical-gate','logical-flat-ne':'192-logical-gate','logical-flat-nw':'192-logical-gate',
 'direct-rise-ne':'192-direct-takeoff', 'cone-rise-ne':'192-top-cone',
 'cone-flow-ne':'192-cone-flow','cone-flow-nw':'192-cone-flow','cone-flow-sw':'192-cone-flow','cone-flow-se':'192-cone-flow',
 'head-audit-ne':'192-head-audit','head-gate-ne':'192-head-gate','head-gate-nw':'192-head-gate','head-gate-sw':'192-head-gate','head-gate-se':'192-head-gate',
 'native-support-ne':'192-native-support','return-ne':'192-return-window','return-nw':'192-return-window','return-sw':'192-return-window','return-se':'192-return-window',
 'contact-nw':'192-return-contact','contact-ne':'192-return-contact','contact-sw':'192-return-contact','contact-se':'192-return-contact','contact-flat-ne':'192-return-contact','contact-switch-ne':'192-return-contact',
 'pending-head-sw':'192-pending-head','pending-head-ne':'192-pending-head','pending-head-nw':'192-pending-head','pending-head-se':'192-pending-head',
 'glide-sw':'192-corner-glide','glide-se':'192-corner-glide','glide-ne':'192-corner-glide','glide-nw':'192-corner-glide',
 'head-face-se':'192-head-face','head-face-sw':'192-head-face','head-face-ne':'192-head-face','head-face-nw':'192-head-face',
 'predicted-se':'192-predicted-corner','predicted-sw':'192-predicted-corner','predicted-ne':'192-predicted-corner','predicted-nw':'192-predicted-corner','predicted-flat-se':'192-predicted-corner',
 'budget-se':'192-flight-budget','budget-sw':'192-flight-budget','budget-ne':'192-flight-budget','budget-nw':'192-flight-budget','budget-flat-se':'192-flight-budget','budget-switch-se':'192-flight-budget',
 **{f'window-{x}':'192-launch-window' for x in ['se','sw','ne','nw']},
 **{f'loop-{x}':'192-loop-audit' for x in ['se','sw','ne','nw']},
 **{f'live-{x}':'192-live-loop' for x in ['se','sw','ne','nw','flat-se','flat-ne','switch-se']},
 **{f'three-{x}':'192-flight-three' for x in ['se','sw','ne','nw','flat-se','flat-ne','switch-se']},
 **{f'finish-{x}':'192-air-finish' for x in ['se','sw','ne','nw','flat-se','flat-ne','switch-se']},
 **{f'side-{x}':'192-side-cone' for x in ['se','sw','ne','nw','flat-se','flat-ne','switch-se']},
 **{f'facing-{x}':'192-bridge-facing' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'flatreturn-{x}':'192-flat-return' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'nativepitch-{x}':'192-native-pitch' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'exposure-{x}':'192-exposure-choice' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'shortrunway-{x}':'192-short-runway' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'phase-{x}':'192-phase-audit' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'posttick-{x}':'192-post-tick' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'observed-{x}':'192-observed-click' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'receipt-{x}':'192-receipt-retry' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'cruisereturn-{x}':'192-cruise-return' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw','switch-se-repeat','cardinal-s','cardinal-n','ceiling-se']},
 **{f'aircurve-{x}':'192-air-curve' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw','cardinal-s']},
 **{f'risecurve-{x}':'192-rise-curve' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw','cardinal-s']},
 **{f'openingfollow-{x}':'192-opening-follow' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw','cardinal-s']},
 **{f'risehandoff-{x}':'192-rise-handoff' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw','cardinal-s']},
 **{f'handoff-{x}':'192-landing-handoff' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'returnslack-{x}':'192-return-slack' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'returncurve-{x}':'192-return-curve' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'sidefirst-{x}':'192-side-before-rise' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw']},
 **{f'nativemove-{x}':'192-native-motion' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'edge-{x}':'192-opening-edge' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw']},
 **{f'opening-{x}':'192-opening-budget' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw']},
 **{f'chord-{x}':'192-landing-chord' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw','cardinal-s']},
 **{f'lateral-{x}':'192-lateral-landing' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'pitch-{x}':'192-side-pitch' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'retry-{x}':'192-pending-retry' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']},
 **{f'click-{x}':'192-click-window' for x in ['se','sw','ne','nw','flat-se','flat-ne','flat-sw','flat-nw','switch-se','switch-sw']}}
CANDIDATES.update({f'manual-{x}':'192-manual-finish' for x in [
 'mouse-flat-ne','key-rise-sw','combo-rise-se','button-rise-nw']})
CANDIDATES.update({f'manualedge-{x}':'192-manual-edge' for x in [
 'button-rise-nw-repeat','inventory-flat-sw','switch-se','cardinal-s','cardinal-n','cardinal-e','cardinal-w']})
trials=[]
for label,candidate in CANDIDATES.items():
 p=ROOT/'.build/state-live'/f'xiaocai190-app-diag192-{label}.log'
 if not p.exists():continue
 t=summarize(p);t['candidate']=candidate
 lines=p.read_text().splitlines()
 statuses=[l.split(' STATE ',1)[1] for l in lines if ' STATE ' in l]
 failures=[s for s in statuses if any(w in s for w in ['偏离路线','未落在','没有及时','超时','缺少方块','没有识别到'])]
 if failures:
  t['first_failure']=failures[0]
  t['outcome']='failed_even_if_later_input_interrupted'
 if not t['finish_audit'] and t['final_status']=='本跳已完成，已落地并回正。':
  t['outcome']='observed_finish_without_release_audit_not_acceptance'
 poses=[(float(m[1]),*map(float,m.group(2,3,4,5,6)),m[7]=='true',m[8]) for l in lines if (m:=POSE.match(l))]
 tele=[]
 for l in lines:
  if ' TELE ' not in l:continue
  m=re.search(r'sprint=Optional\((true|false)\)',l)
  v=re.search(r'velocity=\(([-\d.eE]+), ([-\d.eE]+), ([-\d.eE]+)\)',l)
  if m and v:tele.append((float(l.split()[0]),m[1]=='true',math.hypot(float(v[1]),float(v[3]))*20))
 times=[a[0] for a in tele]
 launches=[]
 for a,b in zip(poses,poses[1:]):
  if a[6] and not b[6] and b[7] in ['takeoff','flight']:
   i=bisect.bisect_right(times,b[0])-1
   q=tele[i] if i>=0 and b[0]-tele[i][0]<.08 else None
   launches.append({'time':b[0],'sprinting':q[1] if q else None,'velocity_bps':round(q[2],3) if q else None})
 t['first_airborne_sprint_samples']=launches
 t['sprint_caveat']='First observed airborne sample, not the exact jump event. A toggled HUD or held Control is not evidence of game sprint state.'
 trials.append(t)
# Source diffs keep every experimental change reviewable without distributing it.
base=ROOT/'.build/candidates/191-top-window'
for candidate in sorted(c for c in set(CANDIDATES.values()) if c.startswith('192-')):
 source=ROOT/'.build/candidates'/candidate;patch=[]
 for p in sorted([*source.glob('Sources/*.swift'),*source.glob('telemetry/src/**/*.java'),*source.glob('Tests/*.swift')]):
  rel=p.relative_to(source).as_posix();old=base/rel
  a=old.read_text().splitlines(True) if old.exists() else []
  patch.extend(difflib.unified_diff(a,p.read_text().splitlines(True),fromfile='191-top-window/'+rel,tofile=candidate+'/'+rel))
 (Path(__file__).parent/(candidate+'.patch')).write_text(''.join(patch))
report={'client_date':'2026-10-30','shipped':False,'desktop_preserved':'1.8.9; diagonal not accepted',
 'trials':trials,'normal_CPS_cap':18,'burst_enabled':False,
 'reference_review':{'creator':'ikun是小菜','source':'7679101635557166371','native_fps':30,
 'new_reviewed_intervals':[[8,10],[10,12]],'new_reviewed_frames':120,
 'observations':['W/S changes visible during the placement-and-return cycle.','From 10.1 to 11.3 the repeated short turns overlap visible block placement; no F3 coordinates or authoritative sprint flag are present.','Sprinting (Toggled) is a toggle label, not proof of internal sprint state.']},
 'findings':['Landing-chord: four level30s trials174 contacts, four rising30s trials213 contacts, one diagonal T-switch30s trial49 contacts, one cardinal T-switch18s trial27 contacts; all finished grounded and aligned. No repeated backing or repair-turn loops were logged; visual smoothness, longer runs and first4 remain unaccepted.',
 'Opening-edge produced4 first-flight cells in NE/SE/NW short tests but only3 in SW; all76 contacts survived. Do not describe this as a four-block horizontal jump or guaranteed four-cell opening.',
 'Opening-budget50ms reserve only lengthened NE horizontal span2.43→2.62 and still3 cells; not retained.',
 'Lateral landing correction completed NE44 level contacts; SE stopped grounded after20 due to the separate short-chord classification. Both recorded geometries have regression tests.',
 'Receipt-confirmed retry completed SE42/SW39/NW41 level contacts, but NE fell on the sixth flight; not accepted.',
 'Reject post-tick-only gating (SE14 fall) and removing commanded-ray gate (SE6 fall). The failed post-tick click used a ticksDue=0 sample immediately before a due=1 frame; timestamp ties must be resolved by log line order.',
 'Read-only tick-phase audit: in phase-flat-SE, ticksDue=0 had 102/102 clicks confirmed within 160 ms; ticksDue=1 had 2/24 unconfirmed (line order, not rounded timestamp ties). Snapshot runs before physics in ave.av. Post-tick gate is experimental, not validated at <=20 FPS.',
 'Recorded short-corner runway false rejection fixed in isolated candidate; targeted test and full suite passed, but live SE17 later fell for a separate placement failure.',
 'Native-pitch centre fallback failed at SE6; side-pitch intersection alone failed at SW27. Neither replaces bridge-facing.',
 'Earlier level return completed SW43 contacts, failed SE8. Keep as a separate experiment, not a new accepted baseline.',
 'Unconfirmed pending retry produced an unintended raised block after five level SW contacts and was rejected. Await confirmation; do not blindly retry at the CPS interval.',
 'Bridge-facing face cost completed SW51 and SE51 contacts, but pure-level SW failed after 15. Not accepted.',
 'Click-window deferral failed after 11 pure-level SW contacts; rejected, pending retry is based on bridge-facing instead.',
 'Periodic idle discovery/permission/UI maintenance measured 30–80 ms on the main loop; skip it while R is active, retaining separate focus/tap/AX checks. Diagnostic evidence is main-loop-evidence.json.',
 'A raised coast route requiring four new cells still failed without a periodic main-loop stall; three-cell budget allows moving level connectors. SE53 contacts passed, SW52 failed during R-up; not accepted.',
 'Air-finish preserves the current flight before entering landing sneak. Its targeted unit passed, but SW46 failed before R-up; side-face transition remains unresolved.',
 'SideFaceCone live SW failed after 5 contacts and was rejected. Geometry replay: 225 recorded samples, 178 shared current/next cones and 46 next-only cones; every returned ray hit the required face. One unavailable sample remains unguided. This is not live acceptance.',
 'EntityLivingBase.getLook(1) uses headYaw, not the current camera yaw. Native 507-frame audit: camera model mismatched 55 frames, head model mismatched 0. Source is local 1.8.9 pr.d(float) bytecode; read-only field pr.aK.',
 'Native right-click POST queue latency <0.1ms; delayed/misdirected placement is not an input-queue backlog.',
 'Reanchoring movement and placement together accumulated cross-track drift; rejected at 7 contacts.',
 'Reanchoring only placement still failed after 10 contacts; not an accepted fix.',
 'All-W sprint experiment reversed horizontal velocity while the camera faced backward; rejected.',
 'Read-only headYaw telemetry resolves the recorded camera-vs-game-ray mismatch; cardinal click math remains as before.',
 'PID-targeted right mouse events were not consumed by Java; keep session mouse path.',
 'Clear-body top gate did not actually enable any early top click in the NW34/NE29 trials; survival improvement is not causally established.',
 'Cached-only top gate and shared-top aim both failed live; neither is accepted.',
 'Rise continuation support still failed after 15 contacts due to a top retry delayed one extra tick.',
 'Top-only retry experiment permits a retry at clickDelay=3 only after button-up, a newer tick, and the unchanged CPS interval.',
 'Return-contact candidate completed 54 NW and 54 NE contacts with no repeated backing and all first-airborne sprint samples true, but SW failed at 12; not a release.',
 'Corner-glide adds a level adjustment only when both launch axes overhang the top face by >0.10 blocks. First SW trial: 53 contacts, 3 adjustments, no repeated backing; remaining modes and visual smoothness not accepted.',
 'Actual landing-path geometry fixes an old false unsupported-corner classification, but the app still repeats backing/runup; not accepted.',
 'Pending-render tracking failed after 11 contacts; rejected.',
 'Bytecode audit: ave.s runTick invokes bfk.a(1.0f) before Mouse.next, refreshing ave.s objectMouseOver from pk.a(distance,partial). ax rightClickMouse then consumes that cache. The previous claim that the old rendered cache alone determines click outcome was incomplete.'],
 'unrun_candidates':{'192-visible-face':'Alternate-face hypothesis was not established; built, not tested or merged.','192-launch-foot':'The alleged last block was never confirmed in the SW trace; built, not tested or merged.'},
 'own_video_review':{'video':'xiaocai190-app-diag192-flatreturn-flat-sw.mov','interval':[7,9],'native_frames_reviewed':116,'pages_reviewed':8,'smoothness_accepted':False,'finding':'Three return/back-turn sequences reviewed; large per-frame turn steps remain. Some frames repeat; no extra repair turn in this interval only.'},
 'release_gate':'No candidate has passed sustained diagonal level/rising, sprint takeoff, R finish, T transition, four headings and cardinal regression.'}
(Path(__file__).parent/'progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for t in trials:print(t['candidate'],Path(t['log']).stem.rsplit('192-',1)[-1],t['landing_contacts'],t['outcome'])

"""Audit selected successful stages across a preserved partial run and its minimal supplement."""
from pathlib import Path
import json,hashlib,math,re,sys
R=Path(__file__).resolve().parents[3]
B=R/'docs/cod4/audit-20261022/mob-network-acceptance'
first,second=sys.argv[1:3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
artifact=json.loads((R/'tools/cod4/mob-network-acceptance/.work/fullpack-artifact/manifest.json').read_text())
checks={};selected=[];runs=[];frames=[]
expected=[f'fullpack/{mob}/{stage}' for mob in ['bandit_thug','gray_wolf','paper_money_ghost','bat_demon'] for stage in ['natural-terrain-fixture','host-native-combat','peer-native-combat','native-ai-combat','battle-world-view','native-kill','corpse-no-repeat']]+[f'fullpack/explore-{offset}/{stage}' for offset in [0,256,512] for stage in ['natural-scene','native-walk','scene-after-walk']]
for run,n,complete in [(first,31,False),(second,6,True)]:
 O=B/run;cs=[json.loads(p.read_text()) for p in sorted(O.glob('result-*.json'))]
 checks[run+'_expected_result_indices']=[c['index'] for c in cs]==list(range(n))
 checks[run+'_all_nonempty_results_true']=all(c['pass'] is True and c['checks'] and all(v is True for v in c['checks'].values()) for c in cs)
 plan=json.loads((O/'stage-plan.json').read_text());checks[run+'_results_match_actual_plan']=[c['name'] for c in cs]==plan[:n]
 cons=json.loads((O/'connections.json').read_text());ids={c['name']:c['uuid'] for c in cons}
 checks[run+'_real_distinct_UUID_TCP']=len(cons)==2 and len(set(ids.values()))==2 and all(c['class']=='net.minecraft.server.level.ServerPlayer' for c in cons) and any('127.0.0.1:' in c['remote'] for c in cons)
 loaded=json.loads((O/'loaded-mods.json').read_text());checks[run+'_96_loaded_mods']=len(loaded)==96 and len({m['id'] for m in loaded})==96
 if complete:checks[run+'_server_finished_without_failure']=(O/'server-COMPLETE').exists() and not list(O.glob('*FAIL*')) and len(plan)==6
 else:
  partial=json.loads((O/'partial-stage-acceptance.json').read_text());checks[run+'_partial_explicitly_scoped']=partial['accepted_indices']==list(range(31)) and not (O/'server-COMPLETE').exists() and all('entity unavailable 31' in json.loads((O/(r+'-FAIL.json')).read_text())['error'] for r in ['host','peer'])
 for role in ['host','peer']:
  key=run+'_'+role;manifest=json.loads((O/(role+'-manifest.json')).read_text());inst=Path(manifest['instance']);source={k:v for k,v in manifest['source_files'].items() if k.startswith('mods/') and k.endswith('.jar')};overrides=manifest['qa_overrides'];log=(O/(role+'-client.log')).read_text(errors='replace')
  checks[key+'_85_production_JARs_retained']=len(source)==85 and all(sha(inst/k)==(overrides[k]['replacement_sha256'] if k in overrides else v) for k,v in source.items())
  checks[key+'_86_actual_JARs']=manifest['total_mod_jars']==86==len(list((inst/'mods').glob('*.jar')))
  checks[key+'_same_current_bundle_guard_artifact']=sha(inst/'mods/dynasty-1.4.0.jar')==manifest['unified_artifact_sha256']==artifact['patched_sha256']
  checks[key+'_QA_helper_matches_manifest']=all(sha(inst/'mods'/name)==digest for name,digest in manifest['added_jars'].items())
  checks[key+'_normal_exit0']=(O/(role+'-exit-code.txt')).read_text().strip()=='0'
  if complete:checks[key+'_complete_marker']=(O/(role+'-COMPLETE')).exists()
  checks[key+'_hidden_unfocused']='GUARD_NETWORK_QA_WINDOW visible=0 focused=0' in log
  checks[key+'_silent']='soundCategory_master:0.0' in (inst/'options.txt').read_text()
  checks[key+'_early_window_disabled']=bool(re.search(r'(?m)^earlyWindowControl\s*=\s*false\s*$',(inst/'config/fml.toml').read_text()))
  for c in cs:
   i=c['index'];prefix=f'{key}_{i}'
   inp=json.loads((O/f'{role}-input-{i}.json').read_text());ready=json.loads((O/f'server-ready-{i}.json').read_text())
   checks[prefix+'_native_input_identity_and_ack']=inp['selfUUID']==ids['Cod4Mob'+role.title()] and inp['name']==c['name'] and (O/f'{role}-ack-{i}').exists()
   checks[prefix+'_actual_ordered_ready_marker']=inp['nativeReadyMarkerReceived'] is True and (O/f'{role}-ready-seen-{i}').exists() and ready['markerTick']-ready['preparedTick']>=3
   if inp['action']=='view':
    render=json.loads((O/f'{role}-render-{i}.json').read_text());png=O/f'{role}-view-{i}.png';checks[prefix+'_real_dual_player_world_frame']=png.exists() and png.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') and 'AFTER_LEVEL' in render['event'] and render['trackedPlayers']==2
    frames.append(str(png.relative_to(B)))
   if inp['action']=='walk':checks[prefix+'_native_keyboard_walk']='native keyUp+keyJump for126 client ticks' in inp['api']
  if role=='host':checks[key+'_native_save']=all(s in log for s in ['Stopping server','All dimensions are saved'])
 runs.append({'run':run,'selected_stages':n,'normal_completed_run':complete,'loaded_mods':len(loaded),'connections':cons,'normal_client_exits':[0,0]})
 selected.extend({'run':run,**c} for c in cs)
checks['exact_37_semantic_stages_no_duplicates']=[c['name'] for c in selected]==expected and len({c['name'] for c in selected})==37
walks=[]
for c in selected:
 if c['name'].endswith('/native-walk'):
  rows=[]
  for after in c['after']['players']:
   before=next(p for p in c['before']['players'] if p['uuid']==after['uuid']);vec=lambda p:[float(x) for x in p['pos'].strip('()').split(',')];a,b=vec(before),vec(after);rows.append({'uuid':after['uuid'],'horizontal_distance':math.hypot(b[0]-a[0],b[2]-a[2]),'distance3d':math.dist(a,b),'on_ground':after['onGround'],'mode':after['mode'],'health':after['health'],'before':a,'after':b})
  walks.append({'run':c['run'],'index':c['index'],'name':c['name'],'anchor':c['after']['naturalWorld']['anchor'],'biome':c['after']['naturalWorld']['biome'],'players':rows})
checks['three_distinct_natural_terrain_walks']=len(walks)==3 and len({tuple(w['anchor']) for w in walks})==3 and all(p['horizontal_distance']>5 and p['on_ground'] and p['mode']=='SURVIVAL' and p['health']>0 for w in walks for p in w['players'])
ai=[c for c in selected if c['name'].endswith('/native-ai-combat')];kills=[c for c in selected if c['name'].endswith('/native-kill')]
checks['four_actual_AI_stage_damage_samples']=len(ai)==4 and all(c['before']['naturalWorld']['effectiveDamageEvents']==0 and c['after']['naturalWorld']['effectiveDamageEvents']>0 for c in ai)
checks['four_single_host_native_deaths']=len(kills)==4 and all(c['after']['deathEvents']==1 and not c['after']['mob']['alive'] and len(c['after']['effectivePlayerAttackers'])==2 for c in kills)
report={'status':'SCOPED_RUNTIME_PASS_VISUAL_REVIEW_PENDING' if all(checks.values()) else 'FAIL','scope':'85 production JAR +1 private QA;4 representative mob battles and3 distinct natural terrain native walks using2 real UUID clients;37 unique accepted stages across partialrun11 and minimal6-stage supplement. First run partial failure retained, not called fully successful.','runs':runs,'accepted_stages':len(selected),'checks':checks,'failed_checks':[k for k,v in checks.items() if not v],'artifact':artifact,'walks':walks,'AI_damage':[{'name':c['name'],'actual_stage_effective_damage_events':c['after']['naturalWorld']['effectiveDamageEvents']} for c in ai],'frames':frames,'scope_boundaries':['New private normal seed77 worlds with day fixed1000 and structuresfalse; natural terrain, not full structure/ecology generation acceptance','Mob spawning/iron gear/high health/last1HP high-damage kill/starting teleport are QA fixtures; no natural acquisition, playtime or full six-stage survival claim','Representative compatibility samples, not all cross-mod combinations or all30 species unique AI/skills; existing closed30-species and49-stage state receipts remain separate','Private dynamic_fps override disabled,30FPS/renderDistance2; not worst-case performance acceptance','Visual review must separately inspect actual frames; no automatic claim from markers'],'todo_changed':False}
(B/(second+'-combined-evidence-audit.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'accepted_stages':len(selected),'failed_checks':report['failed_checks'],'walks':walks,'frames':len(frames)},ensure_ascii=False,indent=2))
raise SystemExit(0 if all(checks.values()) else 1)

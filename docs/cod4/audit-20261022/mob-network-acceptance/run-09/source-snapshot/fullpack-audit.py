"""Full pack receipts stay separate from the closed ce9259 30-species matrix."""
from pathlib import Path
import sys,json,hashlib,zipfile,re,math
R=Path(__file__).resolve().parents[3];B=R/'docs/cod4/audit-20261022/mob-network-acceptance';run=sys.argv[1];O=B/run
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=[json.loads(p.read_text()) for p in sorted(O.glob('result-*.json'))]
artifact=json.loads((R/'tools/cod4/mob-network-acceptance/.work/fullpack-artifact/manifest.json').read_text())
expected_sha=artifact['patched_sha256']
checks={};checks['complete_37_stages']=len(cases)==37
plan=json.loads((O/'stage-plan.json').read_text())
checks['exact_plan_and_indices']=len(plan)==37 and [c['index'] for c in cases]==list(range(37)) and [c['name'] for c in cases]==plan
checks['all_results_pass']=all(c['pass'] is True and bool(c['checks']) and all(v is True for v in c['checks'].values()) for c in cases)
checks['server_complete_and_no_failure']=(O/'server-COMPLETE').exists() and not list(O.glob('*FAIL*'))
cons=json.loads((O/'connections.json').read_text());checks['real_distinct_UUID_TCP']=len(cons)==2 and len({c['uuid'] for c in cons})==2 and all(c['class']=='net.minecraft.server.level.ServerPlayer' for c in cons) and '127.0.0.1:' in cons[1]['remote']
loaded=json.loads((O/'loaded-mods.json').read_text());runtime=[]
for role in ['host','peer']:
 m=json.loads((O/(role+'-manifest.json')).read_text());inst=Path(m['instance']);source={k:v for k,v in m['source_files'].items() if k.startswith('mods/') and k.endswith('.jar')};overrides=m['qa_overrides'];checks[role+'_all_85_production_jars_retained']=len(source)==85 and all((inst/k).exists() and sha(inst/k)==(overrides[k]['replacement_sha256'] if k in overrides else v) for k,v in source.items());checks[role+'_86_jars']=m['total_mod_jars']==86 and len(list((inst/'mods').glob('*.jar')))==86;checks[role+'_accepted_guard_current_bundle_jar']=sha(inst/'mods/dynasty-1.4.0.jar')==expected_sha==m['unified_artifact_sha256'];checks[role+'_complete_exit0']=(O/(role+'-COMPLETE')).exists() and (O/(role+'-exit-code.txt')).read_text()=='0';checks[role+'_input_ack_all']=all((O/f'{role}-input-{c["index"]}.json').exists() and (O/f'{role}-ack-{c["index"]}').exists() for c in cases)
 log=(O/(role+'-client.log')).read_text(errors='replace')
 checks[role+'_hidden_unfocused']='GUARD_NETWORK_QA_WINDOW visible=0 focused=0' in log
 checks[role+'_silent_options']='soundCategory_master:0.0' in (inst/'options.txt').read_text()
 checks[role+'_all_native_ready_markers']=all((O/f'{role}-ready-seen-{c["index"]}').exists() and json.loads((O/f'{role}-input-{c["index"]}.json').read_text())['nativeReadyMarkerReceived'] and json.loads((O/f'server-ready-{c["index"]}.json').read_text())['markerTick']-json.loads((O/f'server-ready-{c["index"]}.json').read_text())['preparedTick']>=3 for c in cases)
 checks[role+'_native_inputs_linked']=all(json.loads((O/f'{role}-input-{c["index"]}.json').read_text())['selfUUID']==next(x['uuid'] for x in cons if x['name']=='Cod4Mob'+role.title()) for c in cases)
 views=[json.loads(p.read_text()) for p in O.glob(role+'-input-*.json') if json.loads(p.read_text())['action']=='view'];checks[role+'_actual_world_frames']=all((O/f'{role}-view-{v["index"]}.png').exists() and 'AFTER_LEVEL' in json.loads((O/f'{role}-render-{v["index"]}.json').read_text())['event'] for v in views);runtime.append({'role':role,'instance':str(inst),'jars':m['total_mod_jars'],'source_production_jars':len(source),'render_frames':len(views),'pid':int((O/(role+'-pid.txt')).read_text())})
walks=[]
for c in cases:
 if c['name'].endswith('/native-walk'):
  movements=[]
  for after in c['after']['players']:
   before=next(p for p in c['before']['players'] if p['uuid']==after['uuid'])
   vec=lambda p:[float(x) for x in p['pos'].strip('()').split(',')];a=vec(before);b=vec(after);movements.append({'uuid':after['uuid'],'before':a,'after':b,'distance':math.dist(a,b),'horizontal_distance':math.hypot(a[0]-b[0],a[2]-b[2]),'final_on_ground':after['onGround']})
  walks.append({'evidence':f'{run}/result-{c["index"]:03}.json','name':c['name'],'players':movements,'natural_world':c['after']['naturalWorld']})
checks['loaded_mods_include_all_96']=len(loaded)==96 and len({x['id'] for x in loaded})==96
checks['three_real_walks_both_move_over5']=len(walks)==3 and all(p['horizontal_distance']>5 and p['final_on_ground'] for w in walks for p in w['players'])
ai=[c for c in cases if c['name'].endswith('/native-ai-combat')];deaths=[c for c in cases if c['name'].endswith('/native-kill')];checks['three_distinct_exploration_anchors']=len(walks)==3 and len({tuple(w['natural_world']['anchor']) for w in walks})==3
checks['four_actual_AI_damage_samples']=len(ai)==4 and all(c['after']['naturalWorld']['effectiveDamageEvents']>0 for c in ai);checks['four_single_native_deaths']=len(deaths)==4 and all(c['after']['deathEvents']==1 and not c['after']['mob']['alive'] for c in deaths)
failed=[{'name':c['name'],'index':c['index'],'checks':c['checks']} for c in cases if not c['pass']]
report={'status':'pass' if all(checks.values()) and not failed else 'fail','run':run,'requirements_scope':'总待办156的完整整包真实双客户端实际战斗/自然地形探索兼容样本；不改待办，不冒充自然取得','production_sha256':expected_sha,'artifact_manifest':artifact,'connections':cons,'instances':runtime,'loaded_mod_count':len(loaded),'loaded_mod_list':f'{run}/loaded-mods.json','checks':checks,'stages':len(cases),'passed_stages':sum(c['pass'] for c in cases),'failed_stages':failed,'walks':walks,'combat_AI':[{'name':c['name'],'effective_damage_events':c['after']['naturalWorld']['effectiveDamageEvents'],'evidence':f'{run}/result-{c["index"]:03}.json'} for c in ai],'scope_boundaries':['完整modpack85生产Jar+私有QA=86Jar，无删mod；仅私有Dynasty在当前包上合并已验护卫两类，全部其余项字节不变','普通生成地形新世界，不铺平台，不导入旧档；开始位置与场景镜头可传送摆位，步行阶段126客户端tick实际按keyUp/keyJump','生物/初始铁剑护甲/高生命/最后1血高伤击杀是声明夹具；不声称自然获得或自然生成这些测试生物','dynamic_fps只在私有副本关闭后台限帧；30FPS与2区块渲染是QA运行配置，不代表高负载最坏表现','四类战斗、三处自然地表为代表兼容样本，不宣称全模组交叉组合、全30类独有技能、生态生成或自然取得闭合','两个自动控制真实客户端，独立UUID与TCP原生C2S，非FakePlayer；不是两名真人，不新增真人门槛'],'core30_report_unchanged':'report.md/report.json固定ce9259的30类闭合结论；本结果独立保存'}
(B/'fullpack-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
lines=['# 86 Jar 双客户端实际战斗/自然地形探索兼容','',f'状态：{report["status"]}。{len(cases)}阶段，{report["passed_stages"]}通过。两端各86Jar（85生产+1私有QA），实际加载{len(loaded)}个mod；绑定当前整包与已验护卫两类修复。','', '四类代表生物：山贼喽啰、灰狼、纸钱鬼、蝠妖。双方原生attack、生产AI实际伤害、单次原生死亡与尸体不重复事件。自然生成地表三处各原生步行126客户端tick；起点与展示摆位为夹具，未铺平台或导入旧档。','', '## 校验','',*[f'- {k}: {v}' for k,v in checks.items()],'', '## 实际探索位移','', '|场景|host移动距离|peer移动距离|生物群系|','|---|---:|---:|---|']
for w in walks:lines.append(f'|{w["name"]}|{w["players"][0]["distance"]:.2f}|{w["players"][1]["distance"]:.2f}|{w["natural_world"]["biome"]}|')
lines+=['','## 证据与边界','',f'- {run}/source-snapshot、双端manifest、connections、loaded-mods、input/ack/render/result、原始PNG与日志/退出码全部保留。','- fullpack-report.json记录逐项检查与探索原始坐标，fullpack-visual-review.json记录实际同框复核。','- '+ '\n- '.join(report['scope_boundaries']),'','原30类已由主协调独立审计闭合，不以本样本替代其证据；本任务不改待办。']
(B/'fullpack-report.md').write_text('\n'.join(lines)+'\n');(O/'fullpack-evidence-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'status':report['status'],'checks':checks,'failed':failed},ensure_ascii=False,indent=2))

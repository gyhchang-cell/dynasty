from pathlib import Path
import csv,json,statistics,hashlib
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/mob-load-acceptance';P=O/'run-02'
def quant(xs,p):
 s=sorted(xs);return s[min(len(s)-1,int((len(s)-1)*p))] if s else None
def stat(xs):return {'n':len(xs),'mean':statistics.mean(xs) if xs else None,'p50':quant(xs,.5),'p95':quant(xs,.95),'p99':quant(xs,.99),'max':max(xs) if xs else None}
if not (P/'run-finished.json').exists():raise SystemExit('Not finished; refusing to publish a completed measurement')
f=list(csv.DictReader((P/'frames.csv').open()));t=list(csv.DictReader((P/'ticks.csv').open()));a=list(csv.DictReader((P/'attacks.csv').open()));phases={}
for phase in dict.fromkeys(r['phase'] for r in f):
 fs=[r for r in f if r['phase']==phase];ts=[r for r in t if r['phase']==phase]
 def vs(rows,key):return [float(r[key]) for r in rows]
 phases[phase]={
  'frame_interval_ms':stat(vs(fs,'interval_ms')),'render_wall_ms':stat(vs(fs,'render_ms')),'server_tick_ms':stat(vs(ts,'tick_ms')),
  'rendered_cohort':stat(vs(fs,'rendered_cohort')),'frames_all20_submitted':sum(int(r['rendered_cohort'])==20 for r in fs),'all20_frame_fraction':sum(int(r['rendered_cohort'])==20 for r in fs)/len(fs),
  'client_cohort':stat(vs(fs,'client_cohort')),'particles':stat(vs(fs,'particles')),'client_entities':stat(vs(fs,'client_entities')),
  'alive_cohort':stat(vs(ts,'alive')),'no_ai':stat(vs(ts,'no_ai')),'active_paths':stat(vs(ts,'active_path')),'moved_over_025':stat(vs(ts,'moved_025')),'with_target':stat(vs(ts,'with_target')),'projectiles':stat(vs(ts,'projectiles')),'native_living_attack_events':sum(r['phase']==phase for r in a),
  'sample_ticks':len(ts),'screenshot':str(P/ (phase+'.png'))}
for phase,p in phases.items():
 base='baseline-water' if phase=='crab_soldier' else 'baseline-dry'
 p['comparison_baseline']=base
 p['p50_frame_delta_ms']=p['frame_interval_ms']['p50']-phases[base]['frame_interval_ms']['p50']
 p['p95_frame_delta_ms']=p['frame_interval_ms']['p95']-phases[base]['frame_interval_ms']['p95']
 p['mean_tick_delta_ms']=p['server_tick_ms']['mean']-phases[base]['server_tick_ms']['mean']
report={'status':'PARTIAL READ-ONLY ACCEPTANCE;19 proposed COD1 correspondences within budget,11 undefined; remaining26 cohorts not load-tested','runtime':'Forge47.4.10/Minecraft1.20.1, GeckoLib4.8.4; frozen current mod sources, Forge dev runtime, NOT entire modpack','settings':{'logical_window':'1280x800','framebuffer':'2560x1600 (verify PNG dimensions)','max_fps':120,'vsync':False,'render_distance':3,'simulation_distance':5,'particles':'all','JVM_heap':'3G','active_processors':2,'camera_xyz':[0,76,25],'camera_yaw_pitch':[180,29],'fov_option':1.0,'arena_floor_y':64,'arena_note':'43x37 stone platform in a fresh flat world; mobs viewed at roughly25 blocks, not close-up fill-rate stress'},'method':'Each phase200 native warmup ticks +400 sampled ticks. RenderTick frame intervals and wall time, ServerTick START/END wall time. Native GeckoLib Entity.Pre events count unique submitted SecondaryMob renderers per frame; visual PNG cross-check. Native AI enabled on all cohort mobs. One QA Cow target: NoAI only on dummy, large finite max-health with per-tick refill. Target teleports between waypoints every80 ticks to keep pursuit active; cohort never teleported or AI-disabled. Measured phases include zero-SecondaryMob baselines, plus one dummy and possible native projectiles for active cohorts. Controlled arena; not natural spawn/travel/multiplayer. No synthetic particles injected.','caveats':['Host concurrently runs other Java processes; see run-02-host-load.jsonl. Deltas are descriptive, not isolated causal costs or certified hardware limits.','Flying locust and ghosts use native direct movement in addition to or instead of navigation; path-active counts alone do not describe all AI.','No new performance SLA assumed. Average tick below50ms is reported only as sampled headroom; max/p95 and frame statistics retained.','Ghost cohort overlaps at a common target: 20 actual renderer submissions do not mean20 visually separable silhouettes. Locust cohort has0 native LivingAttack events because its contact skill targets players, not this QA Cow; that combat/particle worst case remains untested.',
'Remaining26 mobs, mixed species, natural terrain, long sessions, equipment item layers and full-pack interactions untested.','Render event counts indicate real submitted renderers, not a GPU occlusion/visibility query. PNGs allow visual audit.'],'phases':phases}
report['uncovered_cohorts']=[r['id'] for r in json.loads((O/'geometry-audit.json').read_text())['entities'] if r['id'] not in phases]
assert len(report['uncovered_cohorts'])==26
for name in ['tree_spirit','locust_swarm','wandering_spirit','crab_soldier']:
 rows=[r for r in t if r['phase']==name]
 assert len(rows)==400 and all(int(r['alive'])==20 and int(r['no_ai'])==0 for r in rows),name
 assert phases[name]['all20_frame_fraction']==1,name
report['cohort_data_integrity']='All4 active cohorts:400 sampled native ticks each,20 alive and NoAI=0 throughout; all sampled frames20 renderer submissions.'
report['cod1_comparison_summary']=json.loads((O/'cod1-comparison.json').read_text())['summary']
report['caveats'].append('Water arena has edge overflow and some crab models breach above the surface; water cohort is not a sustained fully-submerged navigation test. Water baseline particles and final residual particles are retained, not zeroed.')
(O/'load-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
g=json.loads((O/'geometry-audit.json').read_text())
c=json.loads((O/'cod1-comparison.json').read_text())
lines=['# COD4-1 第二项：只读验收','', '**结论：部分验收，不应删除整条待办。** 产品基础怪指向COD1基础30，而非vanilla。19类有规格依据的形态/用途对应候选，在选定对应关系下均满足面数≤基怪；11类保留未定义。4类代表cohort完成原生负载采样，剩余26类未覆盖。','', '原文依据：`docs/cod4/request.txt` 开头查重基准及§1.0；实际COD1资料目录为 `docs/blueprint-cod1/`（不存在docs/cod1）。`cod1.txt` / `cod1_new.txt`规格与 `BlueprintEntities` 的30个TemplateMob注册一致；本次原生探测全部30类最终绑定，不混入精英/Boss。','', '原版比较和旧自有模型差值只保留作参考，不用于认定违反原文或自动认定产品缺陷。对应候选按形态/用途选择，尚非原作者声明的一对一映射。完整选择理由与strong/shape/role依据见 `cod1-comparison.json`。','', '山贼与更夫被LOWEST注册覆盖为SteveFighterRenderer；其他28类为ExpansionClient.Renderer。COD1同样按实际dispatcher最终绑定计算，包括Steve覆盖；GeoCube非空quads与原生ModelPart.Cube.polygons用相同口径。计数是quad而非triangle，主体以外的手持物品/额外层均未计入。没有按大小或贴图透明度猜面数。','', '|次级怪|实际cuboid/quad|COD1基础对应候选|基怪cuboid/quad|次级减基怪quad|判定|','|---|---:|---|---:|---:|---|']
for r in g['entities']:
 v=r['cod1_comparison'];b=v['base_id'] or '未定义';base=f"{v['base_cuboids']}/{v['base_quads']}" if v['base_id'] else '—';delta=str(v['delta_quads']) if v['base_id'] else '—'
 lines.append(f"|{r['name']} `{r['id']}`|{r['cuboids']}/{r['declared_quads']}|{b}|{base}|{delta}|{'该对应下满足' if v['conditional_budget_met'] is True else '未定义'}|")
lines+=['','不以较大Boss、重做前自身模型、任意vanilla或无关大型核心怪冒充对应基准。11项保留原因逐条见JSON。未自行削模；当前没有从这19个对应中发现面数超标，因此不派发无依据的减资产修复。','', '## 原生客户端负载记录','', '|场景|帧间隔p50/p95 ms|渲染墙时p95 ms|服务端tick均值/p95 ms|20只实际提交帧比例|活跃路径均值|已移动只数均值|粒子均值/峰值|','|---|---:|---:|---:|---:|---:|---:|---:|']
for phase,p in phases.items():
 lines.append(f"|{phase}|{p['frame_interval_ms']['p50']:.2f}/{p['frame_interval_ms']['p95']:.2f}|{p['render_wall_ms']['p95']:.2f}|{p['server_tick_ms']['mean']:.2f}/{p['server_tick_ms']['p95']:.2f}|{p['all20_frame_fraction']:.1%}|{p['active_paths']['mean']:.2f}|{p['moved_over_025']['mean']:.2f}|{p['particles']['mean']:.1f}/{p['particles']['max']:.0f}|")
lines+=['','镜头位于(0,76,25)，俯角29°；地面Y64、43×37石台，FOV选项1.0（110°）。这是约25格距离的同屏测试，不是近距离大面积填充率压力测试。每场景200tick预热、400tick采样；无实体基线保持同配置/镜头/地形，水生场景使用水池基线。基线指无SecondaryMob，战斗场景另有1只测试靶和自然发出的投射物。怪物AI全开，靶子单独关闭AI并每tick补血、每80tick换目标点；怪物未瞬移。没有注入人工粒子。','', '帧间隔包含帧率限制与系统调度；渲染墙时不是GPU计时器。服务端时间为原生ServerTick START至END，原始逐帧、逐tick与攻击事件CSV保留。该机器同时运行其他Java任务，CPU负载记录保留，不能把本轮增量视为排除干扰后的单模组净成本。','', '游魂在共用目标处有明显模型重叠，事件证明20次独立实体提交，但截图无法分辨20个轮廓。蝗虫群的原生接触技只针对玩家，本靶为Cow，因此其原生攻击事件为0，不能把这一组算作玩家接触技能或最坏粒子负载验收。水池空场本身也有粒子（峰值96），末尾空场仍有余留粒子（峰值30），未把它们记成0。', '', '只覆盖最重飞行模型、树精地面寻路、游魂直接移动及蟹兵水生移动。其余26类、自然复杂地形、混合群、多人与整包性能未验收。是否全20只持续同屏需结合上表事件比例与PNG，低于20的帧不掩盖。','', '未负载测试的26类：'+ '、'.join(report['uncovered_cohorts'])+'。', '', '## 重现与证据','', '- `tools/cod4/mob-load-acceptance/prepare.py` 创建独立源码/资源/Gradle缓存快照；不碰主frozen。','- `run.py run-02` 使用全新私有profile；复测须换新run参数，保留旧世界。','- QA在额外sourceSet，未向正式src写入，也未创建或替换正式Jar。','- `geometry-counts.csv` / `geometry-audit.json` / `run-02/native-geometry.json` 是次级30类计数；vanilla比较仅供参考。', '- `cod1-comparison.json` / `cod1-comparison.csv` / `run-03/native-cod1-geometry.json` 是COD1基础30原生计数与19对应、11未定义证据。', '- 重现顺序：prepare.py → run.py(全新run) → audit.py → cod1_compare.py → summarize.py；现有分析脚本明确引用run-02负载与run-03基怪探测，复测时应显式调整对应路径。','- `run-02/frames.csv` / `ticks.csv` / `attacks.csv` / 原生PNG与客户端日志是负载证据。','- `run-01/FAIL.txt` 保留首次发现Steve渲染覆盖的探测失败；不算负载测试通过。','- 本任务未修改正式渲染器、模型、贴图或TODO。']
(O/'README.md').write_text('\n'.join(lines)+'\n')
manifest={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.rglob('*') if p.is_file() and p.name!='evidence-sha256.json'}
(O/'evidence-sha256.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:{'frame_p95':v['frame_interval_ms']['p95'],'tick_mean':v['server_tick_ms']['mean'],'all20':v['all20_frame_fraction'],'path_mean':v['active_paths']['mean'],'particles_max':v['particles']['max']} for k,v in phases.items()},indent=2))

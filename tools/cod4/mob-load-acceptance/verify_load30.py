"""Standalone raw-CSV verification; no import of earlier summarizers or client launch."""
from pathlib import Path
import csv,json,hashlib,math,collections,statistics
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/mob-load-acceptance'
INPUTS={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 INPUTS[str(p.relative_to(R))]=sha(p)
 with p.open() as f:return list(csv.DictReader(f))
def js(p):INPUTS[str(p.relative_to(R))]=sha(p);return json.loads(p.read_text())
def percentile(xs,p):
 xs=sorted(xs);assert xs
 return xs[math.floor((len(xs)-1)*p)]
def span(rows,k):return [min(float(x[k]) for x in rows),max(float(x[k]) for x in rows)]
roster=js(R/'docs/cod4/secondary-roster.json');original={'tree_spirit','locust_swarm','wandering_spirit','crab_soldier'}
runs={};allrows=[]
for run in ['run-02','run-04','run-06']:
 p=O/run;finished=js(p/'run-finished.json');frames=read(p/'frames.csv');ticks=read(p/'ticks.csv')
 assert not (p/'FAIL.txt').exists() and (O/(run+'-exit-code.txt')).read_text()=='0'
 INPUTS[str((O/(run+'-exit-code.txt')).relative_to(R))]=sha(O/(run+'-exit-code.txt'))
 warm,sample=finished['warmupTicks'],finished['sampleTicks']
 parsed={}
 for phase in finished['phases']:
  f=[x for x in frames if x['phase']==phase];t=[x for x in ticks if x['phase']==phase]
  assert len(t)==sample and sorted(int(x['age']) for x in t)==list(range(warm+1,warm+sample+1)),(run,phase)
  assert f and all(warm<int(x['age'])<=warm+sample for x in f)
  for x in f:
   for k in ('interval_ms','render_ms','rendered_cohort','client_cohort','particles','client_entities'):assert math.isfinite(float(x[k])) and float(x[k])>=0
  for x in t:assert math.isfinite(float(x['tick_ms'])) and float(x['tick_ms'])>=0
  active=not phase.startswith('baseline');assert all(int(x['alive'])==(20 if active else 0) and int(x['no_ai'])==0 for x in t)
  submitted=sum(int(x['rendered_cohort'])==20 for x in f)
  x={'run':run,'phase':phase,'warmup_ticks':warm,'sample_ticks':sample,'sample_frames':len(f),'alive_cohort_min_max':span(t,'alive'),'no_ai_min_max':span(t,'no_ai'),'client_cohort_min_max':span(f,'client_cohort'),'rendered_cohort_min_max':span(f,'rendered_cohort'),'client_total_entities_min_max':span(f,'client_entities'),'server_secondary_projectiles_min_max':span(t,'projectiles'),'render20_frames':submitted,'render20_fraction':submitted/len(f),'client20_frames':sum(int(x['client_cohort'])==20 for x in f),'render_count_histogram':dict(collections.Counter(x['rendered_cohort'] for x in f)),'particles_peak':max(int(x['particles']) for x in f),'particles_mean':statistics.mean(int(x['particles']) for x in f),'server_tick_p95_ms':percentile([float(x['tick_ms']) for x in t],.95),'server_tick_max_ms':max(float(x['tick_ms']) for x in t),'frame_interval_p95_ms':percentile([float(x['interval_ms']) for x in f],.95),'frame_interval_max_ms':max(float(x['interval_ms']) for x in f),'render_wall_p95_ms':percentile([float(x['render_ms']) for x in f],.95),'active_path_mean':statistics.mean(int(x['active_path']) for x in t),'moved025_mean':statistics.mean(int(x['moved_025']) for x in t),'screenshot':str((p/(phase+'.png')).relative_to(O)),'raw_frames':str((p/'frames.csv').relative_to(O)),'raw_ticks':str((p/'ticks.csv').relative_to(O)),'frames_below20':[dict(x) for x in f if int(x['rendered_cohort'])<20] if active else []}
  if 'fully_submerged' in t[0]:x['fully_submerged_min_max']=span(t,'fully_submerged')
  parsed[phase]=x
 runs[run]=parsed
for spec in roster:
 n=spec['id'];run='run-02' if n in original else 'run-04';x=dict(runs[run][n]);x['name']=spec['name'];x['id']=n
 base='baseline-water' if n in {'crab_soldier','river_imp','drowning_ghost','carp_spirit','snail_maiden'} else 'baseline-dry'
 x['matched_baseline']=run+'/'+base;allrows.append(x)
assert len(allrows)==30 and len({x['id'] for x in allrows})==30
# Independent recomputation versus previous aggregate is a cross-check, not its input.
prior_path=O/'remaining-load-results.json'
prior=js(prior_path) if prior_path.exists() else None
if prior:
 for x in allrows:
  a=prior['primary_cohorts'][x['id']]
  assert x['server_tick_p95_ms']==a['tick_ms']['p95'] and x['frame_interval_p95_ms']==a['interval_ms']['p95']
  assert x['particles_peak']==a['particles']['max'] and x['render20_fraction']==a['fraction_frames_20']
contact=runs['run-06']['locust_swarm--player-contact'];damage=read(O/'run-06/damage.csv')
contact['successful_player_damage_sample']=sum(x['phase']==contact['phase'] and 100<int(x['age'])<=300 and x['target']=='player' for x in damage)
assert contact['render20_fraction']==1 and contact['successful_player_damage_sample']>0
environment={}
for run in runs:
 p=O/(run+'-host-load.jsonl');INPUTS[str(p.relative_to(R))]=sha(p);observed=[json.loads(s) for s in p.read_text().splitlines()]
 environment[run]={'monitor_samples':len(observed),'first_utc':observed[0]['utc'],'last_utc':observed[-1]['utc'],'loadavg_1m_min_max':[min(t['loadavg'][0] for t in observed),max(t['loadavg'][0] for t in observed)],'java_process_count_min_max':[min(len(t['java_processes_without_arguments']) for t in observed),max(len(t['java_processes_without_arguments']) for t in observed)],'note':'Java processes include clients/Gradle/etc; process count is not a client count.'}
report={'host_environment':environment,'crosscheck_prior_summary':('exact match' if prior else 'unavailable, raw-only computation'),'status':'30/30 raw native cohort datasets verified; no complete product/skill/performance-SLA claim','percentile_definition':'Sorted observations, index floor((n-1)*0.95), zero based; ms. No clipping or zero-frame removal. Independent recomputation from raw CSV; previous aggregate used only for equality cross-check.','primary_sample_ticks':sum(x['sample_ticks'] for x in allrows),'primary_sample_frames':sum(x['sample_frames'] for x in allrows),'entities':allrows,'baselines':[v for run in ('run-02','run-04') for n,v in runs[run].items() if n.startswith('baseline')],'contact_supplement':contact,'inputs_sha256':INPUTS,'scope':[
'Run02 four classes200 warm/400 sample, open arena; run04 remaining26 classes100/200, glass enclosure. Dry/water baselines are same run and enclosure configuration. Do not pool them as identical workloads.',
'Alive/no_ai are server cohort counts, client_cohort is SecondaryMob count, client_total_entities is all client entities including player/dummy/projectiles. Total server entity count was not separately recorded; do not invent it. SecondaryProjectile count is separately available.',
'Actual renderer submissions are distinct entity IDs collected from GeoEntity.Pre or Steve RenderLiving.Post. This is not GPU-visible pixel count or20 distinguishable silhouettes. Four run04 phase-end frames have rendered/client cohort0, retained.',
'Particles are total observed live client particles, including environment, water and residual effects. Not a count of emitted particles or attributable exclusively to this mob. Water baseline nonzero is retained.',
'AI enabled on all20 cohort mobs. QA Cow alone NoAI and waypoint teleport/refill; four passive/escape types additionally receive controlled1-damage provocation. Native path counts/position changes do not prove every mob has successful pathfinding or all skills trigger.',
'Frame interval includes120fps cap and host scheduling. ServerTick START/END and render wall time include QA observation overhead and are not GPU timestamps. Parallel Java/other machine work is documented in per-run host-load JSONL; small differences are not causal evidence.',
'Run06 contact supplement uses low roof and extra ArmorStand observer plus in-arena survival player. Its dry baseline does not match that fixture; contact timings are descriptive, not isolated net cost. Successful contact and20 submissions do not establish worst-case particle coverage.',
'Original crab continuous full-submersion boundary, all skills, mixed cohorts, natural terrain, multiplayer, long sessions and full modpack remain outside acceptance.19 prior COD1 pairings unchanged; class-range extension is separately documented.'
]}
(O/'load30-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
keys=['id','name','run','warmup_ticks','sample_ticks','sample_frames','alive_cohort_min_max','no_ai_min_max','client_cohort_min_max','rendered_cohort_min_max','client_total_entities_min_max','render20_frames','render20_fraction','particles_peak','server_tick_p95_ms','frame_interval_p95_ms','render_wall_p95_ms','active_path_mean','moved025_mean','matched_baseline','raw_frames','raw_ticks','screenshot']
with (O/'load30-independent.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows({k:(json.dumps(x[k]) if isinstance(x[k],list) else x[k]) for k in keys} for x in allrows)
def rng(a):return str(int(a[0])) if a[0]==a[1] else f'{int(a[0])}–{int(a[1])}'
lines=['# 30类×20只：原始数据独立复核','',f"30/30类；{report['primary_sample_ticks']}个服务端采样tick；{report['primary_sample_frames']}个采样帧。所有类采样tick均20只存活、NoAI=0。新增26类100预热/200采样；旧4类200/400，分别标注，不混淆配置。",'', '粒子为存活粒子观测峰值；帧为间隔p95，tick为服务端墙时p95。客户端总实体包含玩家/靶子/投射物，不能当作怪物数量。','', '|类别|轮次 warm/sample|帧数|服务端存活/NoAI|客户端怪物范围|实际提交范围 / 20只帧比例|客户端总实体范围|粒子峰值|tick p95 ms|帧 p95 ms|截图|','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
for x in allrows:
 lines.append(f"|{x['name']} `{x['id']}`|{x['run']} {x['warmup_ticks']}/{x['sample_ticks']}|{x['sample_frames']}|{rng(x['alive_cohort_min_max'])}/{rng(x['no_ai_min_max'])}|{rng(x['client_cohort_min_max'])}|{rng(x['rendered_cohort_min_max'])} / {x['render20_fraction']:.3%}|{rng(x['client_total_entities_min_max'])}|{x['particles_peak']}|{x['server_tick_p95_ms']:.5f}|{x['frame_interval_p95_ms']:.5f}|[PNG]({x['screenshot']})|")
lines+=['','## 对应轮次基线（无SecondaryMob）','', '|轮次/基线|帧数|粒子峰值|tick p95 ms|帧 p95 ms|客户端总实体|','|---|---:|---:|---:|---:|---:|']
for x in report['baselines']:lines.append(f"|{x['run']}/{x['phase']}|{x['sample_frames']}|{x['particles_peak']}|{x['server_tick_p95_ms']:.5f}|{x['frame_interval_p95_ms']:.5f}|{rng(x['client_total_entities_min_max'])}|")
lines+=['','## 接触补测及异常帧','', f"蝗虫run-06另测：{contact['sample_ticks']}tick、{contact['sample_frames']}帧，全部提交20只；采样期成功对玩家伤害{contact['successful_player_damage_sample']}次；粒子峰值{contact['particles_peak']}；tick p95={contact['server_tick_p95_ms']:.5f}ms，帧p95={contact['frame_interval_p95_ms']:.5f}ms。该低顶接触夹具与普通干场基线不同，不作净增量比较。",'']
for x in allrows:
 if x['frames_below20']:lines.append(f"- {x['id']}："+json.dumps(x['frames_below20'],ensure_ascii=False))
lines+=['','## 并行机器环境','', '|轮次|1分钟load最少/最多|Java进程数最少/最多|','|---|---:|---:|']
for run,e in environment.items():lines.append(f"|{run}|{e['loadavg_1m_min_max'][0]:.2f}/{e['loadavg_1m_min_max'][1]:.2f}|{e['java_process_count_min_max'][0]}/{e['java_process_count_min_max'][1]}|")
lines+=['', 'Java进程包含客户端、Gradle等，不能把它当成客户端数量。CPU/load日志已列入输入SHA-256。', '', '## 范围与重现','', 'p95算法：排序后取零基索引floor((n−1)×0.95)；未删异常值、未删末端0提交帧。JSON保留精确值、计数直方图、所有低于20帧和原始文件SHA-256；CSV可独立导入。源码只读重算命令：`python3 tools/cod4/mob-load-acceptance/verify_load30.py`。不依赖旧汇总脚本；旧JSON若存在，只用于复算结果一致性交叉验证；缺失时仍可仅从原始CSV复算。','']+['- '+x for x in report['scope']]
(O/'load30-independent.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'classes':30,'ticks':report['primary_sample_ticks'],'frames':report['primary_sample_frames'],'phase_end_anomaly_frames':sum(len(x['frames_below20']) for x in allrows),'raw_vs_prior':'exact match on requested metrics'},ensure_ascii=False))

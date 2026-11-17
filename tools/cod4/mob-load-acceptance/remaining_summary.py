"""Read raw native runs without changing production assets or prior measurements."""
from pathlib import Path
import csv,json,statistics,hashlib,collections
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/cod4/audit-20261022/mob-load-acceptance'
def rows(p):
 with p.open() as f:return list(csv.DictReader(f))
def stats(xs):
 xs=sorted(float(x) for x in xs)
 return dict(n=len(xs),mean=statistics.mean(xs) if xs else None,p50=xs[int((len(xs)-1)*.5)] if xs else None,p95=xs[int((len(xs)-1)*.95)] if xs else None,p99=xs[int((len(xs)-1)*.99)] if xs else None,min=min(xs) if xs else None,max=max(xs) if xs else None)
def analyze(run,warm,sample):
 p=OUT/run;fs=rows(p/'frames.csv');ts=rows(p/'ticks.csv');att=rows(p/'attacks.csv');dam=rows(p/'damage.csv') if (p/'damage.csv').exists() else []
 results={}
 for name in dict.fromkeys(t['phase'] for t in ts):
  f=[x for x in fs if x['phase']==name];t=[x for x in ts if x['phase']==name]
  v={'run':run,'warmup_ticks':warm,'expected_sample_ticks':sample,'sample_ticks':len(t),'screenshot':f'{run}/{name}.png'}
  for k in ('interval_ms','render_ms','rendered_cohort','client_cohort','particles','client_entities'):v[k]=stats(x[k] for x in f)
  for k in ('tick_ms','alive','no_ai','active_path','moved_025','with_target','projectiles','in_water','fully_submerged'):
   if k in t[0]:v[k]=stats(x[k] for x in t)
  v['fraction_ticks_20_submerged']=sum(int(x.get('fully_submerged',-1))==20 for x in t)/len(t) if 'fully_submerged' in t[0] else None
  v['render_count_histogram']=dict(collections.Counter(x['rendered_cohort'] for x in f))
  v['fraction_frames_20']=sum(int(x['rendered_cohort'])==20 for x in f)/len(f) if f else 0
  v['frames_not20']=[{k:x[k] for k in ('age','rendered_cohort','client_cohort','interval_ms')} for x in f if int(x['rendered_cohort'])!=20] if not name.startswith('baseline') else []
  for label,data in [('native_attack_events',att),('native_damage_events',dam)]:
   matching=[x for x in data if x['phase']==name]
   v[label]={'whole_phase':len(matching),'sample_only':sum(warm<int(x['age'])<=warm+sample for x in matching),'target_counts':dict(collections.Counter(x['target'] for x in matching))}
  v['sample_integrity']=len(t)==sample and (name.startswith('baseline') or all(int(x['alive'])==20 and int(x['no_ai'])==0 for x in t))
  results[name]=v
 return results
old=analyze('run-02',200,400);new=analyze('run-04',100,200)
supplements={r:analyze(r,100,200) for r in ('run-05','run-06') if (OUT/r/'run-finished.json').exists()}
supplement=supplements.get('run-06',supplements.get('run-05',{}))
geom=json.loads((OUT/'geometry-audit.json').read_text());ids=[r['id'] for r in geom['entities']]
primary={n:(old[n] if n in old else new[n]) for n in ids if n in old or n in new}
finished=(OUT/'run-04/run-finished.json').exists()
report={'status':'Native cohort coverage only; overall COD4 item remains partial','run04_finished':finished,'covered_count':len(primary),'total':30,'uncovered':[n for n in ids if n not in primary],'primary_cohorts':primary,'run04_phases':new,'contact_supplement_runs':supplements,'cod1_summary':json.loads((OUT/'cod1-comparison.json').read_text())['summary'],'caveats':[
'前4类为run-02：200 warmup + 400 sample ticks、开放平台；新增26类为run-04：100 + 200 ticks、玻璃围护。跨轮配置不同，不将微小差异归因于怪物类型。各轮有自己的无SecondaryMob基线。',
'原生渲染事件计数为实际renderer提交，含Steve RenderLiving.Post及GeoEntity.Pre；不是GPU可见像素查询。模型可互相遮挡/重叠，非20个可分辨轮廓保证。零/不足20的样本完整保留。',
'所有cohort原生AI开启；Cow靶关闭AI，每80tick换位并补血；cohort未瞬移。饥民/采药人/骗子/螺女每60tick由QA玩家伤害源施加1点伤害以触发原生逃跑/防御；这是受控激发，不是自然玩家攻击距离测试。',
'路径活跃计数与位移只数是观察量，飞行直移不等同寻路；碰撞推挤也可造成位移。不能由20只NoAI=0推断20只均成功寻路。',
'run04水池水Y64..70、玻璃顶Y71；fully_submerged要求脚部在水且头顶所在格为水。原run02蟹兵仍未完成持续全潜水边界。',
'蝗虫真实玩家接触是额外边界场景，与主30类分母分开；伤害事件和攻击尝试分别记录。',
'帧间隔含120fps限制和系统调度，render_ms为CPU墙时而非GPU计时；tick为ServerTick START/END。其他Java客户端并行，host-load记录用于环境复核；不能由小差异断言性能因果或通用硬件SLA。',
'不是全技能、混合群、复杂自然地形、多人、长时间或整个整合包验收。19个COD1对应仍为有依据候选；11个未定义，不自动认定产品缺陷。']}
host=[json.loads(line) for line in (OUT/'run-04-host-load.jsonl').read_text().splitlines()]
report['run04_environment']={'host_samples':len(host),'loadavg_1m':stats(x['loadavg'][0] for x in host),'concurrent_java_process_count':stats(len(x['java_processes_without_arguments']) for x in host),'first_utc':host[0]['utc'],'last_utc':host[-1]['utc'],'settings':{'max_fps':120,'vsync':False,'particles':'all','render_distance':3,'simulation_distance':5,'JVM_heap':'3G','active_processors':2,'logical_window':'1280x800','camera_xyz':[0,76,25],'camera_yaw_pitch':[180,29],'fov_option':1.0},'secondary_geometry_equal_run03':json.loads((OUT/'run-03/native-geometry.json').read_text())==json.loads((OUT/'run-04/native-geometry.json').read_text()),'cod1_geometry_equal_run03':json.loads((OUT/'run-03/native-cod1-geometry.json').read_text())==json.loads((OUT/'run-04/native-cod1-geometry.json').read_text())}
report['contact_environment']={}
for run in supplements:
 host_contact=[json.loads(line) for line in (OUT/(run+'-host-load.jsonl')).read_text().splitlines()]
 report['contact_environment'][run]={'loadavg_1m':stats(x['loadavg'][0] for x in host_contact),'java_processes':stats(len(x['java_processes_without_arguments']) for x in host_contact),'first_utc':host_contact[0]['utc'],'last_utc':host_contact[-1]['utc']}
(OUT/'remaining-load-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
lines=['# 30类原生cohort负载覆盖补充','',f'已记录 **{len(primary)}/30** 类；run-04结束标志：{finished}。这是cohort覆盖，整条COD4-1第二项仍为部分验收。','', '每类20只；保留同屏实际渲染提交、原生AI/路径、粒子、tick和帧时间。下表均为采样期；伤害为采样期成功LivingDamage事件。','', '|类别|轮次 warm/sample|tick数|实际提交20帧比例 / 最少提交|帧p95 ms|tick均值/p95 ms|路径/位移均值|粒子均值/峰值|成功伤害|全潜水最少只数|','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for n,p in primary.items():
 sub=str(int(p['fully_submerged']['min'])) if 'fully_submerged' in p else '未记录'
 lines.append(f"|{n}|{p['run']} {p['warmup_ticks']}/{p['expected_sample_ticks']}|{p['sample_ticks']}|{p['fraction_frames_20']:.3%} / {p['rendered_cohort']['min']:.0f}|{p['interval_ms']['p95']:.3f}|{p['tick_ms']['mean']:.3f}/{p['tick_ms']['p95']:.3f}|{p['active_path']['mean']:.2f}/{p['moved_025']['mean']:.2f}|{p['particles']['mean']:.1f}/{p['particles']['max']:.0f}|{p['native_damage_events']['sample_only'] if p['run']=='run-04' else '未记录'}|{sub}|")
lines+=['','## 本轮无SecondaryMob基线及接触补测','', '|场景|帧p95 ms|tick均值/p95 ms|粒子均值/峰值|20只提交比例|成功伤害（整场/采样）|','|---|---:|---:|---:|---:|---:|']
for n,p in new.items():
 if not n.startswith('baseline') and '--' not in n:continue
 lines.append(f"|{n}|{p['interval_ms']['p95']:.3f}|{p['tick_ms']['mean']:.3f}/{p['tick_ms']['p95']:.3f}|{p['particles']['mean']:.1f}/{p['particles']['max']:.0f}|{p['fraction_frames_20']:.3%}|{p['native_damage_events']['whole_phase']}/{p['native_damage_events']['sample_only']}|")

if supplement:
 lines+=['','## 蝗虫真实玩家接触补测（最后完成轮次）','']
 for n,p in supplement.items():
  lines.append(f"- {n}：{p['sample_ticks']} tick；20只提交帧比例 {p['fraction_frames_20']:.3%}；成功玩家伤害整场/采样 {p['native_damage_events']['whole_phase']}/{p['native_damage_events']['sample_only']}；粒子峰值 {p['particles']['max']:.0f}；帧p95 {p['interval_ms']['p95']:.3f} ms；tick均值/p95 {p['tick_ms']['mean']:.3f}/{p['tick_ms']['p95']:.3f} ms。截图 `{p['screenshot']}`。")
 lines+=['', 'run-04接触场景截图仅天空、提交计数0；run-05同步普通实体角度后仍未解决，均保留为失败的渲染测量及真实接触事件证据。run-06额外同步LivingEntity头部/身体朝向；是否具备20只渲染证据以上表实测为准。只改QA观察相机，怪物AI和正式资产不变。所有补测另建私有profile，不重复30类分母。']
lines+=['', '接触补测使用低玻璃顶及额外ArmorStand观察者，真实玩家在场内；其baseline-dry仍为普通围护/场外玩家，因此不把接触补测减基线当作净成本。run-06成功记录20只提交与玩家伤害，粒子计数实测为0，不能由此声称覆盖接触粒子最坏情况。', '', '## 范围与解释','']+['- '+x for x in report['caveats']]
lines+=['','## 不足20帧的原始记录','']
for n,p in primary.items():
 if p['frames_not20']:lines.append(f"- {n}: "+json.dumps(p['frames_not20'],ensure_ascii=False))
lines+=['', 'run-04四个不足20的帧均位于age=300且client_cohort=0，发生在本类最后tick附近；符合阶段清理边界的表现，但未据此删除原始帧，也不当作稳定期20只GPU可见的保证。', '', '水生4类200/200 tick保持fully_submerged=20；该指标只证明所在水格，非全部潜水技能覆盖。', '', '并行环境原始日志保留。'+json.dumps(report['run04_environment'],ensure_ascii=False), '', '源码与69个测量资源核对：`run-04-source-integrity.json`；本轮计数与run-03一致。', '', '## 复核','', '`remaining-load-results.json`保留完整分位数、计数直方图、各期事件及原始相对路径；每轮`frames.csv`、`ticks.csv`、`attacks.csv`、PNG是原始证据，run-04另有`damage.csv`。`run-04-host-load.jsonl`含并行Java进程CPU和系统load，不含命令参数。','', '复现新增26类：`python3 tools/cod4/mob-load-acceptance/run.py run-NEW --remaining`（必须全新profile），结束后执行`remaining_summary.py`；当前脚本分析固定run-02/run-04，以保留两种采样协议。无正式Jar构建。']
(OUT/'remaining-load-report.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'covered':len(primary),'finished':finished,'uncovered':report['uncovered'],'not20':{n:len(p['frames_not20']) for n,p in primary.items() if p['frames_not20']},'integrity_fail':[n for n,p in primary.items() if not p['sample_integrity']]},ensure_ascii=False))

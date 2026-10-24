"""Reproduce eleven-item class ranges from fixed semantic policy and native bake evidence."""
from pathlib import Path
import json,hashlib,csv,collections
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/mob-load-acceptance'
policy_path=O/'class-budget-policy.json';policy=json.loads(policy_path.read_text())
core_path=O/'run-03/native-cod1-geometry.json';sec_path=O/'run-03/native-geometry.json'
core=json.loads(core_path.read_text());secondary=json.loads(sec_path.read_text())['secondary']
previous=json.loads((O/'cod1-comparison.json').read_text())
undefined={x['id'] for x in previous['entities'] if x['base_id'] is None}
lang=json.loads((R/'src/main/resources/assets/dynasty/lang/zh_cn.json').read_text())
def name(n):return lang.get('entity.dynasty.'+n,n)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
# Verify basic-only membership independently from registration text.
import re
registry=R/'src/main/java/com/dynasty/blueprint/BlueprintEntities.java'
registered=set(re.findall(r'=\s*mob\("([a-z_]+)"',registry.read_text()))
assert registered==set(core) and len(core)==30
catalog=[];integrity={};bone_evidence={}
for n,v in {**core,**{k:secondary[k] for k in undefined}}.items():
 rel='src/main/resources/assets/dynasty/'+v['resource'].split(':',1)[1];snapshot=R/'tools/cod4/mob-load-acceptance/.work/frozen'/rel;cur=R/rel
 g=json.loads(snapshot.read_text())
 if 'minecraft:geometry' in g:
  bones=g['minecraft:geometry'][0]['bones'];cubes=[c for b in bones for c in b.get('cubes',[])]
  declared=sum(len(c['uv']) if isinstance(c['uv'],dict) else 6 for c in cubes)
  structure=[{'name':b['name'],'parent':b.get('parent'),'cuboids':len(b.get('cubes',[]))} for b in bones]
 else:
  cubes=g['parts'];declared=6*len(cubes);structure=[{'name':x['name'],'parent':x.get('parent'),'cuboids':1} for x in cubes]
 assert len(cubes)==v['cuboids'] and declared==v['quads'],n
 integrity[rel]={'snapshot_sha256':digest(snapshot),'current_sha256':digest(cur),'current_equals_measured_snapshot':cur.read_bytes()==snapshot.read_bytes()}
 bone_evidence[n]={'native':v,'structure':structure}
 if n in core:catalog.append({'id':n,'name':name(n),**v,'included_groups':[k for k,x in policy['groups'].items() if n in x['candidates']],'sensitivity_groups':[k for k,x in policy['groups'].items() if n in x.get('sensitivity_only',[])]})
exclusions={
'ludun_jiashi':'大橹盾/防御重装，非轻装人形', 'pijia_panjiang_huwei':'明确重装双斧护卫，非轻装人形', 'zhenwang_zhangqiguan':'大型军旗/旗架，非轻装无大型背挂人形',
'jubi_shigandang':'石碑巨臂构造，非普通人/四足兽', 'kumu_shujing':'植物直桩与根足', 'shibian_lishi':'膨胀尸体、异常巨手比例', 'zhiren_jianke':'薄纸扎双足人形，非普通人/非自由悬空纸钱形',
'shashui_funigui':'依附水面/水下的软体人形，不是自由空中鬼怪', 'yinyang_zhijiao_youhun':'四轿夫+轿箱的载具复合体，非紧凑独立鬼怪，更非虫群',
'qingtong_shuangtoushekui':'双头关节蛇，无足', 'bishui_xuanjiao_youzi':'长蛇形体，无四足承重', 'bazu_digongzhu':'单体8足掘进构装，非四足/飞虫群', 'mingsha_shixie':'单体多足双螯翘尾，非四足/聚合飞虫',
'baimu_mowu':'单一连续多节多足躯干，不等于14个飞虫体', 'tongbi_feitian_yecha':'人形+额外双翼+异常巨臂，非小型非人形翼兽', 'xueju_mangguyu':'无足无振翅的浮空鱼，非鸟/紧凑阴魂',
'chimu_zhuha':'跳跃蛙腿与长舌，只有拓宽四足支撑时纳入敏感性范围', 'juli_bixi_kuilei':'重型龟壳/背碑四足，只纳入拓宽四足敏感性，不作螺女或野猪单一预算'}
for x in catalog:
 x['not_primary_reason']=exclusions.get(x['id']) if not x['included_groups'] else None
 assert x['included_groups'] or x['not_primary_reason'],x['id']

def members(ids):return [{'id':n,'name':name(n),**core[n]} for n in ids]
def bounds(ids):
 a=members(ids);return {'cuboids_min':min(x['cuboids'] for x in a),'cuboids_max':max(x['cuboids'] for x in a),'quads_min':min(x['quads'] for x in a),'quads_max':max(x['quads'] for x in a),'quad_lower_ids':[x['id'] for x in a if x['quads']==min(t['quads'] for t in a)],'quad_upper_ids':[x['id'] for x in a if x['quads']==max(t['quads'] for t in a)]}
rows=[];groups={};assigned=set()
for k,g in policy['groups'].items():
 assert all(n in core for n in g['candidates'])
 groups[k]={**g,'members':members(g['candidates']),'bounds':bounds(g['candidates'])}
 if g.get('sensitivity_only'):
  ids=g['candidates']+g['sensitivity_only'];groups[k]['expanded_sensitivity']={'members':members(ids),'bounds':bounds(ids)}
 for n in g['targets']:
  assert n in undefined and n not in assigned;assigned.add(n);q=secondary[n]['quads'];tests=[{'base_id':b,'base_cuboids':core[b]['cuboids'],'base_quads':core[b]['quads'],'delta_quads':q-core[b]['quads'],'meets':q<=core[b]['quads']} for b in g['candidates']]
  hits=sum(x['meets'] for x in tests);verdict='all_listed_candidates' if hits==len(tests) else 'some_listed_candidates' if hits else 'no_listed_candidates'
  rows.append({'id':n,'name':name(n),'cuboids':secondary[n]['cuboids'],'quads':q,'group':k,'comparison_tier':g['tier'],'range':groups[k]['bounds'],'candidates':tests,'satisfying_count':hits,'candidate_count':len(tests),'conditional_result':verdict,'direct_species_counterpart':None,'delta_quads_range':[q-groups[k]['bounds']['quads_max'],q-groups[k]['bounds']['quads_min']],'caveat':g['caveat']})
for n,why in policy['no_comparable'].items():
 assert n not in assigned;assigned.add(n);rows.append({'id':n,'name':name(n),'cuboids':secondary[n]['cuboids'],'quads':secondary[n]['quads'],'group':None,'range':None,'candidates':[],'candidate_count':0,'conditional_result':'no_comparable_baseline','direct_species_counterpart':None,'caveat':why})
assert assigned==undefined and len(rows)==11
# Source anchors are machine-retrievable first occurrences, plus exact resource skeletons.
anchors={}
for f in ['docs/blueprint-cod1/cod1.txt','docs/blueprint-cod1/cod1_new.txt','docs/blueprint-cod1/stage0-2-audit.md','docs/cod4/request.txt','src/main/java/com/dynasty/blueprint/BlueprintEntities.java']:
 p=R/f;lines=p.read_text().splitlines();anchors[f]={'sha256':digest(p),'name_occurrences':{n:[{'line':i+1,'text':s} for i,s in enumerate(lines) if n in s or name(n) in s][:3] for n in core if any(n in s or name(n) in s for s in lines)}}
report={'status':'Conditional class/range evidence; no forced one-to-one mapping, no asset changes','policy':policy,'policy_sha256':digest(policy_path),'native_inputs':{str(p.relative_to(R)):digest(p) for p in (core_path,sec_path)},'summary':dict(collections.Counter(x['conditional_result'] for x in rows)),'previous19_unchanged':True,'groups':groups,'eleven':rows,'basic30_catalog':catalog,'source_anchors':anchors,'measured_model_structure':bone_evidence,'resource_integrity':integrity}
(O/'class-budget-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
flat=[]
for x in rows:
 b=x['range'] or {};flat.append({k:x[k] for k in ('id','name','cuboids','quads','group','candidate_count','conditional_result','caveat')}|{'base_cuboids_min':b.get('cuboids_min'),'base_cuboids_max':b.get('cuboids_max'),'base_quads_min':b.get('quads_min'),'base_quads_max':b.get('quads_max'),'meets_ids':';'.join(t['base_id'] for t in x['candidates'] if t['meets']),'exceeds_ids':';'.join(t['base_id'] for t in x['candidates'] if not t['meets'])})
with (O/'class-budget-review.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
labels={'all_listed_candidates':'全部候选下满足','some_listed_candidates':'仅部分候选下满足','no_listed_candidates':'全部候选下超出','no_comparable_baseline':'无可比基准'}
lines=['# 原11项COD1类预算补充','', '这是只读类比判定，不是新机制、正式预算变更或作者指定的一对一。原19对应不动；11项的精确同型基准仍不杜撰。先固化分组规则，再由原生计数算范围。计数此前已可见，因此不是盲审。','', '|类别|本体cuboid/quad|类组|基础cuboid范围|基础quad下限–上限|候选满足数|条件结论|','|---|---:|---|---:|---:|---:|---|']
lines[4:4]=['## 选择与计数原则','', '- 仅从实际注册的COD1基础30选择，按最终dispatcher原生模型计数，不纳入精英/Boss、vanilla或旧自身模型。', '- 先按形态、肢体结构和移动/用途明确类组；骨架类比、粗类和用途参考分别标注，不能冒充精确物种对应。', '- 对全部候选逐个比较。次级quad≤范围下限才是在全部候选下满足；超过上限则全部超出；落在中间只算部分满足。不拿上限当统一通过线。', '- 计数包含实际烘焙的本体附件，外部手持层不算；quads不是triangles，不剔除低面数Steve候选、不拆分聚合虫群、不做体型比例换算。', '- 没有同型结构时下限/上限为null，不借重型载具或高面数模型补齐。原19项不改，这11项只补证据和条件结论。', '']
for x in rows:
 b=x['range'];lines.append(f"|{x['name']} `{x['id']}`|{x['cuboids']}/{x['quads']}|{x['group'] or '无'}|{str(b['cuboids_min'])+'–'+str(b['cuboids_max']) if b else '未定义'}|{str(b['quads_min'])+'–'+str(b['quads_max']) if b else '未定义'}|{x.get('satisfying_count',0)}/{x['candidate_count']}|{labels[x['conditional_result']]}|")
for k,g in groups.items():
 lines+=['',f'## {k}', '',g['definition'],'', '|COD1基础ID|实际cuboid/quad|最终模型资源|','|---|---:|---|']
 for x in g['members']:lines.append(f"|{x['id']}|{x['cuboids']}/{x['quads']}|{x['resource']}|")
 lines+=['',g['caveat']]
 if 'expanded_sensitivity' in g:
  lines+=['','拓宽敏感性：'+ '、'.join(f"{x['id']}={x['cuboids']}/{x['quads']}" for x in g['expanded_sensitivity']['members'])+'。完整范围 '+json.dumps(g['expanded_sensitivity']['bounds'],ensure_ascii=False)+'。蛙/重龟不作为首选，仅说明放宽骨架分类的结果；没有挑赑屃单独抬高预算。']
lines+=['','## 解释与剩余范围','', '轻装人形保留祭酒108、弩卒114等低预算：饥民156仅在刀手156下满足，骗子192和采药人180超出该组全部108–156候选，超过各候选的差额范围分别36–84、24–72 quad；这是类预算冲突，精确职业基准不存在，不能自动推导必须削模。其他外形不相近的重装人形204/222、旗官540没有拿来“过关”。', '', '纸钱鬼仅是移动/用途参考，不是相同纸钱骨架；鸟类仅是双翼粗类，COD1没有真正鸟形/机械鸟形。所有“全部满足”仅针对文中穷举的合理候选集，不能外推未知模型。','', '螺女与飞蝗群仍无可比基准；不采用重龟/大蜈蚣/复合纸轿当替身，不拆飞蝗14个虫体进行除法来掩盖单实体总面数。','', '完整30基础怪的纳入组、排除理由、模型骨架/part父子链、原生渲染器/资源与源码锚点在JSON；可独立核对范围两端及所有候选，CSV便于筛选。','', '复现：`python3 tools/cod4/mob-load-acceptance/class_budget_review.py`。无需启动客户端；读已保存run-03原生烘焙结果与隔离快照。模型声明计数另行对照原生计数；按6面长方体/显式UV面计数，不按文件大小。']
(O/'class-budget-review.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'summary':report['summary'],'changed_resources':[p for p,v in integrity.items() if not v['current_equals_measured_snapshot']]},ensure_ascii=False))

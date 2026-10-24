"""COD1 basic30 is the product comparator set; vanilla/old-self are context only."""
from pathlib import Path
import json,csv,hashlib,re
R=Path(__file__).resolve().parents[3];O=R/'docs/cod4/audit-20261022/mob-load-acceptance'
core=json.loads((O/'run-03/native-cod1-geometry.json').read_text());assert len(core)==30
# Selection is fixed by shape/role descriptions, never by a desired quad budget.
M={
'bandit_thug':('zuwu_daoshou','同为轻型持刀近战步兵；采用基础卒伍而非重装护卫','strong'),
'night_watchman':('zhenwang_zhangqiguan','同为站立人形、警戒并召集/支援同伴；更夫灯梆与掌旗官军旗有装备差异','role'),
'red_fox':('xunshan_mujiaquan','犬科尖吻四足/尾部轮廓；原基怪是机械犬，材质与机关附件不同','shape'),
'gray_wolf':('xunshan_mujiaquan','犬形四足、颌部扑咬/侦察警戒；原基怪为机械犬，不等同生物狼','shape'),
'giant_python':('bishui_xuanjiao_youzi','单头长蛇身、盘卷/缠绕控制；陆生蟒与水陆玄蛟幼崽栖息差异','strong'),
'tree_spirit':('kumu_shujing','同为直立树精、根系控制/材料生态；不使用更大的树类Boss','strong'),
'stone_sprite':('jubi_shigandang','石质近战构装、硬化/重击角色；小怪圆石短足与巨臂人形轮廓不同','role'),
'lantern_ghost':('fuhun_baibu_tongzi','浮游鬼怪、魂灯致盲/控制用途；纯灯笼与裹布童子本体不同','role'),
'paper_cut_child':('zhiren_jianke','极薄纸扎人形、快速近战；以纸人基怪而非普通僵尸对应','strong'),
'river_imp':('shashui_funigui','水域人形控制者、拉拽/下沉窒息；河童盘头与水鬼长发有外形差异','role'),
'drowning_ghost':('shashui_funigui','水鬼人形、潜水拖拽/溺水控制；同用途且同题材','strong'),
'carp_spirit':('xueju_mangguyu','纺锤鱼身、鳍与尾；鲤鱼水生跃击与盲骨鱼浮空环境不同','shape'),
'crab_soldier':('bazu_digongzhu','原基怪规格明确为“如同一只钢铁巨蟹”的中央体+放射节肢、横爬；蟹钳与钻头足不同','shape'),
'bat_demon':('youdeng_guimianfu','蝙蝠翼体、俯冲及致盲；同形态/用途','strong'),
'corpse_beetle':('bazu_digongzhu','地下甲壳节肢、多足突袭/钻地；6足甲虫与8足机械蛛差异保留','role'),
'venom_scorpion':('mingsha_shixie','同为低伏多足、双螯与翘尾的蝎类；毒刺与沙地石质效果不同','strong'),
'stone_worm':('baimu_mowu','单一长躯实体、地宫掠食/钻地角色；无足蚯龙与多足蜈蚣形态差异明显','role'),
'wandering_spirit':('yinbing_guizu','半透明人形灵体、无腿支撑漂浮/穿越与减速控制；阴兵带铠甲战戈','strong'),
'clockwork_rat':('xunshan_mujiaquan','同为发条齿轮四足机关、机关城外围小型侦察/干扰；鼠与犬体型不同','strong')}
UNDEFINED={
'famished_refugee':'COD1基础30无救赎型中立流民；不能只因人形就指定战斗兵预算',
'swindler':'无诈骗交易/识破逃跑型基础怪；长衫人形相似不足以唯一对应',
'herb_picker':'无中立采集交易NPC；不拿战斗祭酒替代职业',
'wild_boar':'基础30无直接猪形冲撞基怪；未以更大赑屃或Boss充数',
'golden_leopard':'无豹形潜伏突袭基础怪；木甲犬仅一般四足，不强行指定',
'snail_maiden':'无螺壳人形中立缩壳基怪；赑屃龟形不能直接等同',
'jingwei_bird':'无明确鸟形衔石中立基础怪；不以翼手蝙蝠/人形夜叉替代',
'gray_falcon':'无隼类鸟形基础怪；空战用途相似不足以强制对应',
'locust_swarm':'无飞蝗群单体积聚合基础怪；单条蜈蚣与飞行虫群并不等价',
'paper_money_ghost':'无纸钱本体漂浮吸钱基础怪；纸人/阴兵不等于纸钱轮廓',
'wooden_magpie':'无机械鸟形基础怪；木甲犬非飞行鸟，未用机关Boss代替'}
g=json.loads((O/'geometry-audit.json').read_text());rows=[]
for r in g['entities']:
 id=r['id'];pair=M.get(id);entry={'id':id,'cuboids':r['cuboids'],'quads':r['declared_quads'],'base_id':None,'base_cuboids':None,'base_quads':None,'delta_quads':None,'conditional_budget_met':None,'mapping_status':'undefined','reason':UNDEFINED.get(id)}
 if pair:
  base,why,kind=pair;v=core[base];entry.update(base_id=base,base_cuboids=v['cuboids'],base_quads=v['quads'],delta_quads=r['declared_quads']-v['quads'],conditional_budget_met=r['declared_quads']<=v['quads'],mapping_status='proposed '+kind+' correspondence',reason=why,base_native=v)
 r['cod1_comparison']=entry;rows.append(entry)
 assert pair or id in UNDEFINED
# Verify currently present relevant runtime sources/resources equal measured private snapshot.
source_files=['docs/cod4/request.txt','docs/blueprint-cod1/cod1.txt','docs/blueprint-cod1/cod1_new.txt','src/main/java/com/dynasty/blueprint/BlueprintEntities.java','src/main/java/com/dynasty/blueprint/client/TemplateMobRenderer.java','src/main/java/com/dynasty/blueprint/client/TemplateMobModel.java','src/main/java/com/dynasty/client/steve/SteveFighterBindings.java']
for v in core.values():
 path='src/main/resources/assets/dynasty/'+v['resource'].split(':',1)[1];source_files.append(path)
 p=R/path;frozen=R/'tools/cod4/mob-load-acceptance/.work/frozen'/path
 assert p.read_bytes()==frozen.read_bytes(),path+' changed since frozen native probe'
for f in source_files:
 if f.startswith('src/'):
  assert (R/f).read_bytes()==(R/'tools/cod4/mob-load-acceptance/.work/frozen'/f).read_bytes(),f+' current source diverged from probe snapshot'
sha={f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in sorted(set(source_files))}
summary={'matched':len(M),'undefined':len(UNDEFINED),'within_proposed_budget':sum(r['conditional_budget_met'] is True for r in rows),'over_proposed_budget':sum(r['conditional_budget_met'] is False for r in rows)}
report={'product_basis':'docs/cod4/request.txt §1.0 and opening dedup list: COD1 BASIC30; docs/cod1 does not exist, actual specification is docs/blueprint-cod1/cod1.txt and cod1_new.txt.','status':'PARTIAL; proposed correspondences need main-agent review; no deletion or asset edits','interpretation':'Vanilla and retained own-old-rig comparisons are context only, not proof of violating product requirement. Differences are not automatically product defects. No elite/Boss accepted as base.','native_method':'Same isolated current-source snapshot; final EntityRenderDispatcher renderer binding; GeckoLib nonnull GeoCube.quads or native Steve ModelPart.Cube.polygons. Body baked meshes only; held equipment/extra layers excluded consistently. run-03 is geometry-only; run-02 performance data preserved.','selection_rule':'19 shape/role correspondences selected from BASIC30 specifications; strong/shape/role confidence explicit.11 undefined rather than choose a bigger unrelated base. No mapping is asserted to be author-declared one-to-one.','summary':summary,'entities':rows,'all_cod1_basic_native':core,'source_sha256':sha}
(O/'cod1-comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
with (O/'cod1-comparison.csv').open('w') as f:
 keys=[k for k in rows[0] if k!='base_native'];w=csv.DictWriter(f,keys,extrasaction='ignore');w.writeheader();w.writerows(rows)
g['product_basis']=report['product_basis'];g['baseline_uncertainty']='COD1 BASIC30 is product base set. See cod1-comparison.json:19 explicit proposed correspondences,11 undefined. Vanilla and old-self are context only and must not be used as product violation claims.';g['cod1_summary']=summary
(O/'geometry-audit.json').write_text(json.dumps(g,ensure_ascii=False,indent=2))
print(summary)
for r in rows:
 if r['base_id']:print(r['id'],r['quads'],'vs',r['base_id'],r['base_quads'],'delta',r['delta_quads'])

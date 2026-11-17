"""A texture called armor is not automatically an appropriate MC-material target."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-15-candidates.json').read_text())['rows']
N={
545:('EXCLUDE-low-contrast-mottled-checks',545,0,'主体岛几乎全是灰紫细碎交错格，宏观很少明确板/布分材；背景透明，岛中有色像素为不透明。','只记录低对比细碎材质反例，不误报全透明或缺图；也不凭名字认定实际游戏甲坏了。'),
546:('EXCLUDE-low-contrast-mottled-checks',545,0,'腿层同样为稀少灰紫碎格，粗轮廓可见但材料主次弱。','同套上下层；对比低不意味着缺渲染，未运行也不作实机结论。'),
547:('stalwart-violet-plate-cyan-recess',547,1,'紫白板面在上端和外侧明亮，中间留近黑细孔及青色下沿，亮片按少数斜段分开。','可借大板与暗孔面积关系；白亮片偏多，后续不可整套等亮，不复制原像素。'),
548:('stalwart-violet-plate-cyan-recess',547,0,'腿层延续紫白亮片、黑青内槽，窄条按短节分段。','与547同设计上下层，不计新腿甲设计或完整UV案例。'),
549:('stalwart-charcoal-lime-panel-binding',549,1,'炭灰宽板上嵌少数浅绿短块，下缘为亮绿分段带，灰大面没有全边描白。','可借暗甲/嵌件/底带分工；亮绿色不移作当前帝王全身主色。'),
550:('stalwart-charcoal-lime-panel-binding',549,0,'腿层沿用暗灰主面和浅绿嵌短横，局部亮绿窄条保持连续。','上下层同装备，不加数；尚未核确切模型岛与左右腿镜像。'),
551:('stalwart-charcoal-lime-panel-binding',549,0,'升级版将灰主面换为暗红，绿色短嵌件和长底带的位置与原版大体一致。','与549保守合并同形升级族，红色和疣斑不自动增加一套案例。'),
552:('stalwart-charcoal-lime-panel-binding',549,0,'红腿层保留同绿色短横与底带，仅主材换红。','与原套及升级上下层合并，不凭升级名称分摊门槛。'),
553:('dungeon-loading-blue-faceted-dark-bindings',553,1,'深蓝大面内是少量灰蓝折片，近黑粗连接围出大孔；极少紫点和灰色框分立。','可借夜色材质主次；名称 spawner 不证明图像是笼格，也不能把名字当模型结构已验。'),
554:('dungeon-loading-blue-faceted-dark-bindings',553,0,'腿层深蓝区由浅蓝V折段集中提亮，顶部一小近黑横块与下边界保持。','与553同套，V形亮片不单算新符纹；只有平面材质观察。'),
}
for r in rows:
 n=int(r['reference_id'].split('-')[1]);family,rep,credit,note,limit=N[n]
 r.update(status='VISUALLY_REVIEWED_SOURCE_MATERIAL_ONLY',semantic_family=family,family_representative=f'VIS-{rep:03}',
  distinct_family_proposed_credit=credit,scope='equipment_material',observation_zh=note,limitation=limit,
  inspected_detail_view=r['supplemental_detail_view'],applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),
 proposed_distinct_design_families=3,coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='Ten source atlases and3 detail sheets opened. Low-contrast mottled pair excluded as a target style. Base/upgraded tungsten layers merge.3 material proposals only; names are not geometric or runtime evidence.',rows=rows)
(D/'review-batch-15.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))

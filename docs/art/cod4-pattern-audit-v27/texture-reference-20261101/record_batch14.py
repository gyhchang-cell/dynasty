"""Material-only source atlas observations, after all source/detail sheets opened."""
from pathlib import Path
from datetime import datetime,timezone
import json
D=Path(__file__).resolve().parent
rows=json.loads((D/'batch-14-candidates.json').read_text())['rows']
families={
515:('ages-black-gold-blue-banding','近黑的大块与土金面分开，少量金白角点提亮；蓝金相间长条与浅色窄段各自成岛。','只借黑底/金件/蓝带的面积分工；不复制阿努比斯头形、文化标识或完整图案。'),
517:('ages-red-lamellar-gold-fittings','红褐大片内部是暗红短格；细金亮件集中在窄岛与边连接处，皮褐束带保持暗。','可借皮束与层甲明度差；罗马式文化结构只作材料观察，不移作中式甲造型。'),
519:('ages-muted-gold-maroon-insets','土金条带围出较大的留空，绛红仅占几块矩形内衬；窄金横段用明暗短格表现接片。','不按金色多就判神圣；借强调色小面积和连接件秩序，不复制独特装甲纹样。'),
521:('ages-ivory-gold-chain-separation','乳白/灰钢大面与金色窄接件分开，黑底链格集中在少量内区，其他岛保持平整。','可借浅甲/暗内衬/金扣层级；全图多种细高光并非本项目必须照搬的精致标准。'),
523:('ages-silver-plate-dark-chain','银灰宽面有少数白色硬亮段，密黑灰链格集中于两个区域，红布小岛与褐带另置。','参考板/链/布分材；有些亮段较密，未来需更克制，不把西式板甲结构套入王朝。'),
525:('ages-brown-banded-light-lamellae','棕黑横甲片之间穿过浅褐窄带，宽褐束片与近黑板面层次分开，图集下方有细长浅带。','借条片方向及束带对比；不用日本服饰身份或细长岛位置推断本项目模型形态。'),
527:('ages-crimson-lamellae-brown-bands','暗褐大板分成多条横片，朱红长条以稀疏小黄扣连接，部分红面保留较大暗红内区。','可借甲片/系绳/扣件三层秩序；红饱和度与日本大铠身份不直接复制。'),
529:('ages-ivory-blue-gold-textile','乳白宽布面保留大片素色，蓝金等宽长条集中于窄岛，浅褐小棋格只在少数局部。','只借大素面与有限条纹对比；埃及式蓝金文化符号不移作王朝帝纹。'),
531:('ages-green-feather-bone-gold-clasps','绿色长片有深绿分节，灰白骨色短件与金小扣分区，红棕横片另置，不全身同色。','可借羽片/骨/扣分材，但羽冠与独特文化图案不能照搬；不能凭平面图宣称羽片展开通过。'),
533:('ages-dark-maroon-open-gold-links','深褐与暗红大面占主导，金色短粗链结或弯环是稀疏亮点，红面中留深孔。','只借暗底留孔与少量亮连接件；名字 Raijin 不证明是当前雷符身份。'),
539:('deep-aether-violet-facet-orange-joints','紫甲的白色成对斜亮片沿块面排列，橙黄只集中于中部小连接位置；暗紫细边连续。','可借面片光向与关节强调分工；不全套描白，也不因此认定完整模型UV或神圣甲完成。'),
541:('lost-aether-agility-green-white-chevron','绿色极少数小岛，旧版仅短白V；新版把白绿大V分成多个窄段，仍是同装备版本。','旧/新包版本合并，不计两个装备；岛少可能仅覆盖局部，不能擅报盔甲缺面。'),
543:('lost-aether-noble-open-loop-trim','灰白细边串成若干开口回环，长横边与小钩之间保留大空隙，上下层图案位置不同。','纹饰遮罩不是整套穿戴材质；上下层同一纹饰，不把灰白遮罩当实际最终染色或完整UV案例。'),
}
mapping={}
for rep in range(515,535,2):mapping[rep]=(rep,1);mapping[rep+1]=(rep,0)
mapping.update({535:(113,0),536:(113,0),537:(113,0),538:(113,0),539:(539,1),540:(539,0),541:(541,1),542:(541,0),543:(543,1),544:(543,0)})
for r in rows:
 n=int(r['reference_id'].split('-')[1]);rep,credit=mapping[n]
 if rep==113:
  family='aether-colored-plate-family'
  note=('青绿甲面由深边围浅色主面，局部V形亮片和短接点分开。' if n in [535,536] else '灰蓝甲面由暗边围浅色主面，少量浅青下缘；腿层沿用分段窄片。')
  limit='保守并入已读天境有色板甲材料族；颜色与细小分段变化不足以在本批追加新套装。未核完整绑定。'
 else: family,note,limit=families[rep]
 if n<535:
  note += ' 宽臂/窄臂两个源版本同套，局部岛布局有移位或删短，需分别绑定。'
 if n==540:note='腿层延续紫白斜亮片，橙黄小块只在窄连接处；与539同套。'
 if n==542:note='新版绿色小岛加入更宽白绿V和分段窄片；与541旧包仍归同装备。'
 if n==544:note='腿层由灰白小回环和短竖构成，中间多留空；与543同一纹饰。'
 r.update(status='VISUALLY_REVIEWED_SOURCE_MATERIAL_ONLY',semantic_family=family,family_representative=f'VIS-{rep:03}',
  distinct_family_proposed_credit=credit,scope='equipment_material',observation_zh=note,limitation=limit,
  inspected_detail_view=r.get('supplemental_detail_view',r['review_sheet']),applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0)
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=len(rows),
 proposed_distinct_design_families=sum(r['distinct_family_proposed_credit'] for r in rows),
 coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='30 actual source atlases plus five enlarged detail sheets opened. Ten normal/slim pairs merge; addon color-plate tiers reuse earlier Aether family. Legacy/new agility and trim layers merge. Material context only, no cultural copying or complete UV credit.',rows=rows)
(D/'review-batch-14.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))

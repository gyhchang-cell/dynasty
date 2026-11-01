"""Manual observations of the 24 Malum rune PNGs actually viewed on the full sheet."""
from pathlib import Path
import json

D=Path(__file__).resolve().parent
NOTES={
48:('bent-flow','灰石上青色阶梯折线向右下延伸，下端分出短点；高亮只在转折，石材边厚以一档暗色说明。'),
49:('fork-hook','紫石上粉色分叉长竖笔，顶部横叉与底部钩分开；不让主符与石材同明度。'),
50:('fire-s','褐石上黄橙S形折线，亮黄占中段，橙色落背光侧；火符不是整块石头换红色。'),
51:('fork-hook','灰石上紫色弯钩/短叉构图，与粉色分叉符属同类折钩；名称不同不自动记成新设计。'),
52:('stacked-bars','灰石上青黄相间三层短笔画，层间留深色间隙；不把亮点均匀撒全图。'),
53:('fire-s','紫石上黄橙S折，与burning_fervor同类，只换底材和细小弯折，不新增设计族。'),
54:('bent-flow','褐石的青色上下短弯，主体朝向与斜石长轴有夹角；同一流动折线族。'),
55:('bent-flow','紫灰石上青色片状斜折，根部深蓝、端点亮青；仍与阶梯流动主干合并。'),
56:('stacked-bars','紫石上三层洋红横笔交错，暗底保持分隔；与叠杠类合并，不按三条笔画计数。'),
57:('bent-flow','褐石上蓝青环抱短折、淡黄内点；只借冷暖小面积分配，轮廓仍是弯折类。'),
58:('fire-s','紫石上两个黄橙断笔沿斜轴分布，和S形火符组织相近；断开笔画不是额外两条参考。'),
59:('closed-lozenge','紫石中央绿黄小环，中心灰黑孔保留；环宽比亮度更影响缩小后的可读性。'),
60:('tree-fork','紫石上三向绿枝围淡黄短主干，枝向与石片对角相合；研究主干和分叉，不照搬其符号。'),
61:('closed-lozenge','灰石上绿黄闭合小环，上方淡黄端点；与indomitability都靠中央留孔识别，合并。'),
62:('closed-lozenge','紫石上洋红菱形环，四角为阶梯，中心留黑；四角造型差异暂不另拆设计。'),
63:('fork-hook','灰石上粉色分叉长折，与bolstering及spell_mastery同类；底色差异不新计。'),
64:('fire-s','灰石上黄橙斜向S折，笔画有中断；与其他火符保守合并，避免用名称拆数量。'),
65:('bent-flow','紫石上蓝青短折和淡黄上点，重心偏上；与howling_gale主干相近，合并。'),
66:('fork-hook','紫石上亮粉分叉竖钩，亮区在上、中段；和48不同，属于钩叉族，与49合并。'),
67:('center-post-ward','褐石上绿色左右短护翼围淡黄竖柱，深孔紧贴柱侧；可学中轴稳定与两侧支撑，但不直接认作山字符。'),
68:('bent-flow','紫石上蓝青斜向上下两块，中部有暗分割；同族弯折主干，不因时长语义另计。'),
69:('stacked-bars','紫石上两段青黄横块，上下错开；与dexterity叠杠族合并。'),
70:('fork-hook','灰石上粉红上叉下钩，色调较暖但拓扑仍是分叉钩；不单计生命属性。'),
71:('stacked-bars','灰石上紫色双横杠与短折，偏离闭环；合入叠杠族，不按传送/扭曲功能猜视觉差异。'),
}
rows=json.loads((D/'batch-02-candidates.json').read_text())['rows']
seen={};out=[]
for r in rows:
    i=int(r['reference_id'].split('-')[1]);family,note=NOTES[i]
    first=family not in seen
    rep=seen.setdefault(family,r['reference_id'])
    out.append({**r,'status':'VISUALLY_REVIEWED_LOCAL_NOT_COORDINATOR_ACCEPTED',
        'scope':'small_rune_symbol_material','semantic_family':'malum-'+family,
        'family_representative':rep,'distinct_family_proposed_credit':int(first),
        'observation_zh':note,'inspected_detail_view':'build/art-reference-20261101/malum-runes-full.png',
        'limitation':'Inventory rune art only, not animated shield/armor/weapon UV or game proof. All shared stone blanks/material colors are not separate designs.'})
(D/'review-batch-02.json').write_text(json.dumps({'viewed_pngs':len(out),'proposed_distinct_design_families':len(seen),
    'coordinator_accepted_new_visual_credit':0,'production_gate_met':False,
    'policy':'24 item names/PNGs collapse conservatively into seven visible glyph families; not 24 references. No credit assigned to individual school weapons without target applicability review.',
    'rows':out},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'viewed':len(out),'proposed_families':len(seen),'production_allowed':False}))

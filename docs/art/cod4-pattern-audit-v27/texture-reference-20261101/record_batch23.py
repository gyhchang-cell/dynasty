"""All 32 icons actually opened; GUI icon context is not academy identity credit."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json
D=Path(__file__).resolve().parent;rows=json.loads((D/'batch-23-candidates.json').read_text())['rows']
notes=[
'灰白短光棒/尾迹在黑底中逐级减亮，软光感强；不是符字身份，可作GUI低辨识反例。',
'紫色方折环、四角射线、中央2×2棋节点；主白段稀疏但彩底满铺，不直接复制成世界贴花。',
'暗骨色四枚弯牙/左右尖角围暗中部，暗底灰差小，作为深背景下读不清的反例。',
'白灰盾面尖底配金色外框，盾中央大留白；GUI完整底色不能直接套用透明物品。',
'黄橙两条折返风带，白高光集中在转折，底为褐色分区；动势来自折带不只是换色。',
'纯黑/暗灰正面头影只留双横紫眼，16px一眼读出眼位，形体信息少不能当角色纹样。',
'黑色竖菱孔、紫方折环、四边短芒；外环/负形比小碎点先读。',
'蓝深底上粗青白折雷竖贯、两侧小支路，像素转折清楚，白芯只局部。',
'同蓝青白折雷家族但主折角与粗细不同，和lightning_bolt保守合并。',
'金白斜光柱贯穿黄褐底，中心高亮大；图标光爆不是帝兵独立龙纹。',
'中央宽金光柱下端分两条向上卷边，后方暗底；主要轮廓和斜向光束不同。',
'左上箭头/右下杆的火箭，亮头与橙尾方向清楚；GUI火焰背景不是飞行尾迹贴图。',
'同斜箭向的紫色魔箭，边缘光感/多紫阶，只作同箭家族变化不拆学院身份。',
'灰铁箭头与褐杆、绿色毒带分材，比单光箭更有实体材料，但不照抄原版箭充原创。',
'红色薄月弧位于左上/下部，暗红中部有留空，灰度反差偏低。',
'粗暖黄月牙外缘橙红，内侧大暗孔，少量火尾；月弧与blood/shadow保守同构图族。',
'紫白粗月牙与右下短散线，和火/月弧同族，不因紫色算新招。',
'冰青短中柱、两侧横冰刺、下部宽弧与离散方点，几处方向结构优先。',
'两条灰白相反弧卷有暗中孔，外浅内暗大宽片，不是连续密噪点。',
'灰蓝云带下是两侧青白折雷，和裸雷图标同元素但云带提供图意；不算新学院。',
'中央白心、红边、暗红旋底；是生命语义，不能凭红色叫火焰或符箓。',
'同白心下方添弧环和两侧短端，心家族合并；不把下半环算第二个护体法阵。',
'暗绿/褐色分叉根束在近黑底上低对比，主根不易读，是暗部辨识反例。',
'木褐盾面、灰外框、金色树干/双侧叶形；与银盾同盾家族，材质与glyph可分层研究。',
'橙黄底上大斜金白打击弧和少量短尖，白区域偏大，不能据图标推世界爆发强度。',
'蓝白细折雷呈分支Y状、周围深蓝，和粗雷同族只记录线宽变化。',
'青色斜圆环内分三道短弧线，背景很暗；同通用环/波语汇，不冒充完整音律符字。',
'三把紫白长剑向上扇开，下方小柄交汇；主剑/侧剑有宽窄层次，不只三条发光棒。',
'青白斜冷光线穿小碎冰片，和siphoning同斜束构图，不当两个独立学院。',
'红色斜细束中心较亮、宽暗红两侧，和冷射线合并，注意本图光效不是材料表面纹理。',
'中央圆灰白物体，底部黄弧包住、上方火尖，不把图名heat误认纯火焰徽记。',
'蓝白中心冲击星、两侧厚弧及碎方块，图标中心白块大；不直接照搬成低遮挡命中贴花。']
assert len(notes)==len(rows)
for r,note in zip(rows,notes):
 im=Image.open(r['local_path']).convert('RGBA');pix=list(im.get_flattened_data())
 r.update(status='VISUALLY_REVIEWED_SOURCE_CONTEXT_ONLY',semantic_family='EXCLUDE_GUI_ICON_NOT_COMPLETE_TARGET_IDENTITY',scope='gui_symbol_readability',distinct_family_proposed_credit=0,
  observation_zh=note,source_alpha_bbox=im.getchannel('A').getbbox(),source_nonzero_alpha_pixels=sum(p[3]>0 for p in pix),source_partial_alpha_pixels=sum(0<p[3]<255 for p in pix),
  applicable_targets_proposal=[],coordinator_accepted_new_visual_credit=0,
  limitation='16px GUI技能图标不等于透明物品/盔甲/世界纹样。满底光效只作辨识度/负形/线宽背景与反例，箭、月弧、雷、心/环等同语义合并；不新增目标1000门槛计数。')
out=dict(recorded_at=datetime.now(timezone.utc).isoformat(),viewed_pngs=32,proposed_distinct_design_families=0,coordinator_accepted_new_visual_credit=0,production_gate_met=False,
 policy='All3overview and8integer-detail pages actually opened.32GUI icon source PNGs are context only, no literal copying, nonew identity cases.',rows=rows)
(D/'review-batch-23.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('32 actual GUI sources reviewed,0newcomplete identity cases.')

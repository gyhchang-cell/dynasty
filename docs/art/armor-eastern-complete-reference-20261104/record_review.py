"""D21 observations after opening two icon and six full native-atlas pages."""
from pathlib import Path
from datetime import datetime, timezone
import json
D=Path(__file__).resolve().parent
rows=[]
def row(group,cases,observation):
    rows.append(dict(semantic_group=group,prior_group=group,cases=cases,observation=observation,credit='APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS'))
row('divine_ornate_gold',['jinghui:cmrj','jinghui:jxyj','jinghui:mlxk'],
    '炽芒熔金是灰金闭面冠配红垂带、红金宽肩和红裤；金犀玄将用红顶羽、金肩双钩及黑红裙甲；墨鎏玄是高冠黄心、青领和黑金甲。三套只追加已有华金组，不以冠饰和颜色计独立完整信用。可学金边围住暗甲片、红/青布留在领口和内衬的主次；宽肩弧饰、直矩形裤片和细密挂条不用于普通盔甲微调。三个256方图集都有大量独立细岛和局部浅彩色块，未确认模型实际用到哪些岛；不将这些色块判成玩家身上调试色。')
row('samurai_plate_variants_conservative',['jinghui:gujiang','jinghui:xbws','jinghui:xbzhanxin'],
    '故将灰铁胸片叠红布、灰棕裙甲和黑鞋黄纹；新兵灰闭面盔红羽、宽肩灰片与短红绳；战损新兵沿用同一基础轮廓，改碎胸片、红绑带和破损裙边。战损与新兵合并，三名称追加既有叠片组。512方原图许多窄灰片和空白面，故将细碎斑纹及鞋底装饰在物品栏难读；新兵与战损主要差别要靠大缺口而非零散红点。原图留存，不能直接套普通64×32身体UV，也不缩源图。')
row('immersive_robe_open_front',['jinghui:hbjz'],
    '黑白剑头图是细长黑饰物带青横片，衣图灰白翅状框与垂布，裤为大片灰白矩形，鞋为深色方块；不能因四个槽位都有图就当标准头盔/甲身比例。256方图有黑白大面与细灰条岛、少量青金饰纹，只学白襟与暗内衬互衬，细吊饰和翅肩不照搬。追加袍服学习组，不给新设计信用。')
row('organic_aquatic_horned_plate',['jinghui:llongui'],
    '水龙头图主要是两根浅灰角，衣的宽肩骨片与长腿甲同灰白色，靴缩成黑底白V；普通装备轮廓不完整，追加水生角壳族作比例限制例。256方图的灰白和冷蓝大岛中有密边、小红点和棋格，实际骨架与选中部位未验。可借冷硬角骨/暗布材料分区，不能用两根角代替普通头盔，也不把怪物角部件单独算完整设计。')
row('molten_plate_dark_shell',['jinghui:weijin'],
    '卫烬赤红外翻冠翼、极宽红金肩、平红裙片和黑底红靴，火焰主要成为外轮廓装饰。256方原图大片红、黄火纹和少数独立长带，主次很强但肩冠太抢眼；只借黑内层承托红外层和集中金边，不把宽翼/飘带加到已认可盔甲。追加既有熔融暗壳组，未核为独立普通甲信用。')
row('mountain_realm_grid_lamellar',['jinghui:xinghet'],
    '星河剑宽扁黄绿编笠、暗红棕交错胸片、左右不对称腿片和棕鞋，胸两端浅色肩盘明显。256方图暗棕块与大量极窄黄红边岛并存。可学左右腿甲不同但腰带统一、胸片连续搭接，不学扁帽代替头盔和超宽肩盘。追加既有格片甲学习组，不凭不对称细部另计一整套。')
row('splendour_ornate_legwear_family',['jinghui:xipao'],
    '新春戏头饰短灰须配红心，衣上橙金戏曲饰与四根长蓝旗，红直裤及黑底红头鞋。256方图有高饱和红黄花纹、蓝旗和长杆；用途是舞台戏服，旗、杆、头饰不计独立设计。色块虽清楚但旗饰/裙甲的密度和体量偏离普通MC盔甲，这批作为装饰过多反例追加已有华饰族；不复制旗形、不转用整张穿戴图。')
row('priest_white_gold_cloth',['jinghui:yueqian'],
    '月浅双侧高蓝白冠与长坠，白灰交襟长袍配蓝领，下方灰蓝长裙和淡蓝方鞋。256方原图大面积白浅蓝，许多窄条和连阶明暗；局部近柔和插画效果，不能作为Dynasty粗像素的成稿标准。只借交领、袖缘和裙边的冷色布料层级，保留离散大色块与暗边，长冠坠/大裙矩形不照搬。追加既有祭服布料金边学习组，颜色不同不给新整套信用。')
keys={c['case_key'] for c in json.loads((D/'provenance.json').read_text())['cases']}
flat=[k for r in rows for k in r['cases']]
assert len(flat)==len(set(flat))==12 and set(flat)==keys and len(rows)==8
out=dict(reviewed_at=datetime.now(timezone.utc).isoformat(),pages_opened=[f'icons-{i:02}.png' for i in range(1,3)]+[f'worn-{i:02}.png' for i in range(1,7)],observations=rows,excluded_cases=[],complete_name_families_viewed=12,native_icon_entries_viewed=48,item_model_declarations_read=48,native_layer_candidate_entries_viewed=12,static_geomodel_texture_declarations=12,geometry_and_animation_context_payloads=24,animation_metadata_present=0,new_conservative_learning_groups=0,append_observations=8,limits='12个四件图标名称仅增加已读材料，不是12套适用完整独立MC设计；新兵战损合并、戏装/角冠等局部反例零新增设计信用。静态GeoModel声明不等于玩家实际选择的整条渲染链。',new_artwork=0,production_changes=0,game_starts=0,gate_met=False)
(D/'semantic-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('12 names / 48 icons / 12 static atlas declarations / 8 observations / 0 new groups')

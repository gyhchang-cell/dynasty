"""Manual observations from all2overview/5detail sheets actually opened."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import json, hashlib
D = Path(__file__).resolve().parent
rows = json.loads((D / 'batch-25-candidates.json').read_text())['rows']
notes = [
 '暗红叠鳞由宽短竖片错位组成，轮廓接近竖向椭圆而非单块钻石；上下尖、两侧阶梯收分，深沟连接材料层。',
 '绿龙鳞与红鳞同一错叠组织，片内仅两三阶绿高光；同物种颜色变体不另立案例。',
 '白鳞使用灰沟区分白片，不靠黑色逐像素边框；同形换色仍与其余龙鳞合并。',
 '冰蓝鳞的亮面在片左上、下右较暗，与白鳞共享结构；不能把冰色认成独立学院身份。',
 '海蛇绿鳞上窄下宽、下沿多短鳞尖，片间暗槽比龙鳞细，组成一束而非单个鳞片。',
 '深蓝海蛇鳞保留同轮廓与片位，是上一图的换色；明暗朝向不同不增加独立物品。',
 '长弯牙根部红褐、牙身灰白，尖端黄绿并有离体绿滴；颜色服务毒性，但不是白虎完整身份纹样。',
 '长羽由棕红羽根过渡到宽绿羽腹、狭青蓝羽尖；轮廓无对称大叶片，主轴斜向且材质变化分段。',
 '金属鸟单羽是极窄的棕灰阶梯长片，深根、亮尖；不是带大量细分叉的插画羽毛。',
 '羽束用数根上一类长片错开，片间深缝保留，属于同材质成束表现，不另算多个新羽毛设计。',
 '虹彩鳞上青下黄绿，以大片阶梯色带组织；颜色较多仍是离散像素，不是软件柔光。仅参考材料层，不能泛用所有祭品。',
 '黑灰钩爪先有粗厚上根，再向左下内弯，中央大留孔，亮面只占左上少量方块；爪不是一条细线。',
 '鸸鹋羽宽而破碎，棕色中轴两侧羽片短阶梯错开，尖端收成横短段；与细杆金属羽是两种材料读法。',
 '走鹃羽根部浅米、主羽深棕接蓝灰细长尖，长窄剪影靠不等宽段落读清；不是把宽羽等比压缩。',
 '石壳由上下错位的两片厚灰褐板组成，边缘深、板心米灰；一眼是层状壳片，不能把普通环换色称玄武。',
 '棘龟壳是横宽红褐甲片，三处上突和中央阴槽形成厚度；细节集中边缘，下面两暗支脚般延伸并非兽形骨架证明。',
 '名为毒牙但源图是宽暗青囊状顶与长褐根，尖牙剪影不明显；只作名称/可读性反例，不能直接取为白虎牙造型。',
 '龙之戒实际主体是银环、黑托与粉红宝石，没有可辨龙鳞/龙首；名称含龙不等于龙纹参考，排除身份门槛。',
 '金羽用粗黄中轴与宽短分叉，羽根留长杆，斜向轮廓与金属亮暗分离；高亮不通过外围模糊发光取得。',
 '龙皮是黑紫不规则圆片，少量暗紫岛表现起伏，整体对比很低；适合暗皮材反例/基底，不是完整龙身份图案。']
families = {
 941: ('icefire-overlapping-dragon-scale-cluster', 941),
 942: ('icefire-overlapping-dragon-scale-cluster', 941),
 943: ('icefire-overlapping-dragon-scale-cluster', 941),
 944: ('icefire-overlapping-dragon-scale-cluster', 941),
 945: ('icefire-sea-serpent-scalefan', 945), 946: ('icefire-sea-serpent-scalefan', 945),
 947: ('icefire-curved-poison-fang', 947), 948: ('icefire-segmented-green-feather', 948),
 949: ('icefire-metallic-narrow-feather', 949), 950: ('icefire-metallic-narrow-feather', 949),
 951: ('icefire-stepped-rainbow-scale', 951), 952: ('alex-hook-claw-negative-space', 952),
 953: ('alex-ragged-broad-feather', 953), 954: ('alex-long-segmented-feather', 954),
 955: ('alex-layered-rock-shell', 955), 956: ('alex-spiked-shell', 956),
 957: ('EXCLUDE_POOR_FANG_READABILITY_CONTEXT', None),
 958: ('EXCLUDE_DRAGON_NAME_WITHOUT_IDENTITY_PATTERN', None),
 959: ('aether-wide-barbed-gold-feather', 959), 960: ('EXCLUDE_LOW_CONTRAST_HIDE_CONTEXT', None),
}
for r, note in zip(rows, notes):
    n = int(r['reference_id'].split('-')[1]); family, rep = families[n]
    im = Image.open(r['local_path']).convert('RGBA'); pixels = list(im.get_flattened_data())
    r.update(status='VISUALLY_REVIEWED_MATERIAL_CONTEXT_ONLY', semantic_family=family,
        scope='offering_material_context', distinct_family_proposed_credit=int(n == rep), observation_zh=note,
        source_alpha_bbox=im.getchannel('A').getbbox(), source_partial_alpha_pixels=sum(0 < p[3] < 255 for p in pixels),
        source_nonzero_alpha_pixels=sum(p[3] > 0 for p in pixels), applicable_targets_proposal=[],
        cutout26_mask_sha256=hashlib.sha256(bytes(p[3] >= 26 for p in pixels)).hexdigest(),
        coordinator_accepted_new_visual_credit=0,
        limitation='cod6贡品/材质阅读背景，不是完整四象、学院身份或穿戴UV案例；历史是否重用待核，不自动加正式数。')
    if rep: r['family_representative'] = f'VIS-{rep:03}'
proposal_count = sum(r['distinct_family_proposed_credit'] for r in rows)
result = dict(recorded_at=datetime.now(timezone.utc).isoformat(), viewed_pngs=len(rows),
    proposed_distinct_design_families=proposal_count, coordinator_accepted_new_visual_credit=0,
    production_gate_met=False, rows=rows,
    policy='20originals/2overviews/5integer details actually viewed. Recolor/bundle merged;3counterexamples excluded. No production or full target acceptance.')
(D / 'review-batch-25.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(dict(pngs=len(rows), context_family_proposals=proposal_count, formal_new_credit=0)))

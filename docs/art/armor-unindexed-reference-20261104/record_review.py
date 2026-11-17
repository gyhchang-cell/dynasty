"""Actual full-set icon and raw-layer observations; animations and variants stay merged."""
from pathlib import Path
from datetime import datetime, timezone
import json

D = Path(__file__).resolve().parent


def main():
    rows = []

    def add(group, cases, note, prior=False):
        rows.append({'semantic_group': group, 'cases': cases.split(), 'observation': note,
                     'credit': 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' if prior else 'NEW_CONSERVATIVE_LEARNING_GROUP',
                     **({'prior_group': group} if prior else {})})

    add('complete_thief_hood_leather_panel', 'dark_souls_expansion:thief_set',
        '灰黑拱形兜帽、黑棕衣身配单侧棕皮带/肩、长暗裤与棕靴形成盗贼衣料身份。帽开口大黑区与袖肩灰片仍在小图可辨；裤几乎整块黑，作为对比不足反例。源图有柔明暗，项目只学大面分区和帽衣一致，不照搬渐变。')
    add('complete_faraam_elite_tabard_steel', 'dark_souls_expansion:faraam_set dark_souls_expansion:elite_knight_set',
        '两套银灰头肩、蓝绿/蓝色胸布与棕靴共享骑士罩袍材料组织，保守合为一族。faraam盔面分明、青胸中央大面配小腰扣；elite桶盔横缝、蓝衣金色纵带和浅肩。材料不同区域各有主面，不将金带扩为全胸密纹；不能把两套罩袍仅换色拆成两个信用。')
    add('complete_hard_leather_metal_shoulders', 'dark_souls_expansion:hard_leather_set',
        '灰低盔/方肩与棕皮短胸、暗裤灰膝、棕高靴构成皮革与金属连接。腰处少量金扣表达绑带，头胸仍紧凑；靴筒很高是比例限制例，不把普通MC短靴任意拉成长筒。原生候选64×64布局不能按64×32身体矩形切。')
    add('complete_blue_draped_steel', 'dark_souls_expansion:artorias_set',
        '深蓝披布环绕头侧与肩，胸前亮钢斜片、暗裤灰膝和灰靴使罩布与硬甲分开。头顶小尖和蓝披片都服务主体，不做巨大冠饰。明暗很暗，项目只借鉴布/钢位置和主次，不复制高密织纹或把胸片画成完整躯干人像。')
    add('immersive_robe_open_front', 'dark_souls_expansion:pyromancer_set',
        '棕兜帽与红棕竖向襟边、金黄腰带和棕靴构成开襟法衣，追加已有开襟衣袍组。帽不靠尖锥辨认身份；大块红襟和腰带比堆细符文有效。衣身暗部细渐变不直接带入项目，原生128×128层仍是未绑定候选。', True)
    add('complete_favor_crossed_gold_plate', 'dark_souls_expansion:favor_set',
        '细长金面盔、交叉金肩胸、裤腿横箍和金靴使金属结构贯穿四件。高亮很集中，虽轮廓可读，满金交叉条会抢掉胸主面；仅学结构带与深空隙，不把强力甲等同满屏金闪。')
    add('complete_balder_cage_helm_red_collar', 'dark_souls_expansion:balder_set',
        '高直笼形头盔、红色颈口、灰胸和外撇腰片配棕靴；衣领色只占小区，红披布与甲板材料分开。高盔和腰片容易偏离MC短紧凑轮廓，是比例边界例。256×256原生候选另直接打开完整PNG，不靠被总览行高截断的缩略图当看完。')
    add('complete_catarina_transverse_shell', 'dark_souls_expansion:catarina_set',
        '米白横向层层板带从圆鼓盔、宽腹甲到直胫重复，像洋葱壳。只作为分层带/材料重复的学习反例：圆鼓头胸与用户要求的MC倒U盔/短方肩冲突，不照搬，不因多条横带或多页拆算设计。白甲主体不能当白背景擦掉。')
    add('bone_reptile_rib_vest', 'dark_souls_expansion:darkwraith_set',
        '暗兜帽里米色骷髅面、灰黑横肋胸、暗裤和灰靴追加骨肋背心组。浅骨集中面孔，其余身体留暗大面；对比弱的下装是限制例。实体候选层不是物品实际穿戴绑定证据，不从名称判断玩家使用效果。', True)
    add('souls_black_knight_dark_silhouette', 'dark_souls_expansion:black_iron_set',
        '近黑桶盔、横分层大肩/胸、深红腰裙和黑靴追加既有黑骑士剪影组。红只在腰上缘，与灰靴边形成大区；黑甲低对比和过宽肩使主体不够清楚，不能为统一风格修改用户已认可的黑甲。', True)
    add('complete_sun_emblem_cloth_plate', 'dark_souls_expansion:solaire_set',
        '白灰桶盔配单侧短红缨、绿短肩布、白袍胸红黄太阳块和金属腿靴，身份来自有限几种大材料区。徽记在胸中央而不占满肩腰，绿色只在肩。可学粗色块徽记的面积约束，不复制原作者太阳图样或整套配色。')
    add('vanilla_outline_elemental_palette', 'undergarden:utherium undergarden:froststeel undergarden:cloggrum divinerpg:jungle deep_aether:stratus',
        '红、浅蓝、棕、亮绿、紫橙五个名称仍以基础盔、短胸、直裤、分靴为主，保守追加模板组。froststeel与utherium胸的横板和中空头口较明显，cloggrum用腹部竖片，jungle接近纯色模板，stratus把橙金边放盔侧/肩/腰/靴口。亮绿过饱和、紫色大浅胸区容易失材质，均作材料层级边界观察，不因五种色板加五套设计。', True)
    add('molten_plate_dark_shell', 'twilightforest:fiery',
        '黑棕主甲与金橙外缘、窄亮边和两帧轻微亮度变化，追加熔融暗壳族。图标保持MC方肩、直裤与短靴；留暗主面比满面橙噪点有效。四PNG都是16×32原生动画，两帧加插值声明属同套，不算8个部件设计，不在项目原稿做缩图或重采样。', True)
    add('complete_mechanized_dark_frame', 'traveloptics:mechanized_exoskeleton',
        '深灰框架、少量红橙节点、浅灰肩腿片贯穿四部位，头盔短横红面板辨识明确。节点比满胸发光纹克制，分腿仍清楚；肩/胸细线略多，应借鉴主面与节点面积，不用写实电线网覆盖主体。128×128底图和稀疏亮层是同套材质层，不是两套设计。')
    add('complete_etherium_pulsing_facet', 'enigmaticlegacy:etherium',
        '青白晶面盔、短胸与直裤、分靴用大斜亮面表达晶体，头脸开口保持深色。逐帧看12格亮面渐强、顶端有停留后反向回落；27个序列项含重复。动画后段胸几乎白满，是过曝丢材质反例。两张同名原生穿戴候选图实为全透明且哈希相同，不能由图标推出实穿外观或断言游戏隐形；外部渲染链尚未审读。')
    flat = [c for r in rows for c in r['cases']]
    p = json.loads((D / 'provenance.json').read_text())
    assert len(flat) == len(set(flat)) == 20 and set(flat) == {c['case_key'] for c in p['cases']}
    result = {
        'reviewed_at': datetime.now(timezone.utc).isoformat(),
        'pages_opened': [f'icons-{i:02}.png' for i in range(1, 4)] + [f'worn-{i:02}.png' for i in range(1, 6)] + ['animation-frames.png'],
        'extra_raw_images_opened': ['worn-references/dark_souls_expansion/fa519d81468d-balder_layer.png'],
        'observations': rows, 'excluded_cases': [],
        'complete_name_families_viewed': 20, 'native_icon_entries_viewed': 80,
        'item_model_declarations_read': 80, 'native_layer_candidate_entries_viewed': 26,
        'animation_metadata_read': 8, 'source_animation_frame_slots_reviewed': 56,
        'animated_name_families': 2, 'animation_additional_design_credit': 0,
        'new_conservative_learning_groups': 10, 'append_to_existing_groups': 5,
        'limits': '候选/名称/PNG/图层/帧均不等于设计信用。原生实体层未证明选中为玩家穿戴；静态JSON只证图标引用，未做目标UV或游戏验收。200学习组仍含局部、变体与反例，完整独立总数仍未知。',
        'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'gate_met': False,
    }
    assert sum(a['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP' for a in rows) == 10
    (D / 'semantic-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('20 complete-name cases / 80 icons / 26 raw layers / 10 new conservative learning groups')


if __name__ == '__main__':
    main()

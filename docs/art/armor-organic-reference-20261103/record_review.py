"""Actual visual observations, normalized families and explicit unproven-slot exclusion."""
from pathlib import Path
from datetime import datetime, timezone
import json

D = Path(__file__).resolve().parent


def main():
    rows = []

    def add(group, cases, observation, prior=False):
        rows.append({'semantic_group': group, 'cases': cases.split(), 'observation': observation,
                     'credit': 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' if prior else 'NEW_CONSERVATIVE_LEARNING_GROUP',
                     **({'prior_group': group} if prior else {})})

    add('organic_flesh_rib_armor_family', 'biomancy:acolyte_armor biomancy:warrior_armor',
        '两套红棕/肉粉甲均以骨条与亮绿腔体建立有机材料身份，保守合为一族。侍从两版本的帽/胸和补齐裤靴仍同套；战士胸/头的米色骨边比红粉主体更亮，骨片分区清楚。亮绿小格在缩略下非常抢眼，不能把全部甲面画成荧光点阵。源geo图集声明64×64或128×64，未证明套用标准穿戴UV。')
    add('unrealium_dark_purple_insets', 'butcher:dragon',
        '黑紫四件保留短胸、直腿、L靴；紫暗交错像网纹，灰边分出头盔。追加已有暗紫嵌片组，密集棋盘纹是材料不够大块的反例，不单因龙鳞名称给新设计信用。实际模型名前缀dragonscalearmor与PNG dragon不相同，按JSON引用对应。', True)
    add('organic_pillager_disguise_cloth', 'butcher:pillager',
        '暗红短外衣、青黑裤、棕靴配灰绿面具，服装材料和灰面罩各有身份；补读helmet模型实际指向pillager_mask。面具、上衣、裤、靴是同套伪装，不是四个设计。可学衣料分区，但不把面具画成全身人台，来源图不复制到项目。')
    add('organic_aquatic_horned_plate', 'callfromthedepth_:immemorial eeeabsmobs:ghost_warrior',
        '两套均用青蓝角盔、短宽肩胸、胸腹分节及分离直裤/靴建立水系板甲，保守一组。immemorial米白中甲与浅边突出，补读模型找到拼写为immemorial_leggins的裤图；ghost_warrior暗蓝底配少量亮蓝分节，缩小可读但胸的细弱对比需克制。角冠不能继续横向扩张；128×128候选geo只证实图集声明，未证物品绑定。')
    add('vanilla_outline_elemental_palette', 'geckolib:gecko_armor geckolib:wolf_armor the_awakening_of_the_elder_souls:rainbow',
        '绿色示例甲、灰色狼耳示例甲和彩虹甲沿基础短胸直腿轮廓，保守追加既有模板学习组。绿甲高饱和与彩虹满铺横跨部位是材料主次不足的反例；灰狼甲仅小耳/灰阶不能算一套复杂新结构。示例geo原生图集64×64和128×128，不将教程资源或图集大小本身计设计信用，也不写成游戏实测。', True)
    add('organic_champion_tabard_plate', 'goetyawaken:champion',
        '浅蓝灰胸腹与裤胫由金边、红色两侧布片连接，补齐靴后见深红靴筒/浅蓝脚。材质分区有用，头盔白羽缨明显偏高，胸肩也宽，应作为高级甲装饰与主体竞争的限制例；不能以亮金和长缨把MC基础甲扩大成人台插画。不从champion名称推断数值或获取阶段。')
    add('bone_reptile_rib_vest', 'mutantmonsters:mutant_skeleton mutantmore:mutant_wither_skeleton',
        '骨白/灰肋骨胸与深灰凋灵肋骨胸追加已有骨肋背心组。mutantmonsters两个版本的胸/裤/靴合并，老版细长肋骨与新版棕肩/米骨是同套演变；凋灵版补齐同前缀模型引用的靴。长细骨条容易失去短宽胸轮廓，应学留白和骨片位置，不把不同肢骨材料图计作装备套装。', True)
    add('organic_sunflower_material_family', 'utopiabosses:sunflower',
        '橙黄花瓣头/胸配绿茎裤与绿橙靴让植物身份一致；但头胸几乎像花朵徽章，基础甲的开口与肩腰被花瓣吞没，是本项目MC甲比例的反例。只借鉴材料在四件重复的位置，不照搬大圆花；同套geo的128×128声明不算额外设计。')
    add('wood_green_armor_family', 'utopiabosses:tree',
        '棕木甲主面配青绿叶肩与胫片，胸心开叉、盔上枝杈和腿侧叶片保持同一树材质族。追加既有木绿甲学习组，避免把每片叶、每根枝做成另一设计。原生128×128声明和图标用途分开记录，未证明其适用Dynasty标准UV。', True)
    excluded = [{'case_key': 'mutationcraft_origins:berserk',
                 'category': 'PLAYER_SLOT_OR_ITEM_BINDING_UNPROVEN',
                 'reason': '只看到近黑裤和两只分离靴，沿标准轮廓但对比很低。所在JAR中未找到这两个origins图对应的物品模型，不能仅凭textures/items/文件名认定普通玩家盔甲或给完整盔甲门槛信用。保留已看记录，待原生物品/槽位声明。'}]
    prov = json.loads((D / 'completed-provenance.json').read_text())
    flat = [c for r in rows for c in r['cases']] + [a['case_key'] for a in excluded]
    assert len(flat) == len(set(flat)) == 15 and set(flat) == {c['case_key'] for c in prov['cases']}
    result = {
        'reviewed_at': datetime.now(timezone.utc).isoformat(),
        'pages_opened': [f'index-icons-{i:02}.png' for i in range(1, 4)] + [f'icons-{i:02}.png' for i in range(1, 4)],
        'observations': rows, 'excluded_cases': excluded,
        'name_families_viewed': 15, 'native_icon_png_viewed': 63,
        'initial_index_icons_viewed': 57, 'same_family_parts_added': 6,
        'item_model_declarations_read': 61, 'native_geometry_atlas_declarations_read': 8,
        'new_conservative_learning_groups': 5, 'append_to_existing_groups': 4,
        'limits': '图标JSON证据不等于穿戴绑定；原生geo仅读图集描述，不证明选中、目标UV兼容或实机。189保守学习组仍含局部、变体、反例，不等于189套已验完整独立设计。',
        'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'gate_met': False,
    }
    (D / 'semantic-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('D13: 15 names / 63 icons / 5 new learning groups / 1 unproven-binding exclusion')


if __name__ == '__main__':
    main()

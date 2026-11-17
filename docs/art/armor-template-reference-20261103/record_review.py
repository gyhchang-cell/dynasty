"""Actual observations from six pages after fixing component-name inflation."""
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

    add('advanced_netherite_accent_variants', 'advancednetherite:netherite_diamond advancednetherite:netherite_emerald advancednetherite:netherite_gold advancednetherite:netherite_iron', '四套黑底甲的胸横带、靴筒和裤下段保持同模板，区别为青/绿/金/白金属包边；16张部位图仅归一组。局部异色仍不覆盖大黑底，有助于材料主次，不能为同一条包边换色计四套。')
    add('bloodmagic_living_sentient_family', 'bloodmagic:living bloodmagic:sentient', '两套均只读到头裤靴：红金/银青的靴筒横带、深色裤和额部/交叉面罩不同，保守同一套件学习族。无下划线命名已归并；不能把livinghelmet、livingleggings、livingboots当三设计。红额配暗裤对比清楚，交叉银面罩不是应删除的白背景。')
    add('mokels_horned_faceplate_family', 'mokels_rpg_two:diamond mokels_rpg_two:dread mokels_rpg_two:lunar mokels_rpg_two:minmin mokels_rpg_two:netherite', '银红、黑青、蓝翼、灰绿及红色头件/胸件围绕角盔、颊口和少量侧挂件变化，保守同族，不依材料名给五套完整甲信用。白甲红连接和黑甲青眼口的材料区可学，外挑大角、尖脸与过大胸挂只作不照搬的反例。')
    add('vanilla_outline_elemental_palette', 'shadowlands:belronite shadowlands:cloud shadowlands:emeraldium shadowlands:ghosmetal shadowlands:ghostly shadowlands:purity shadowlands:shadow shadowlands:shadowgem', '紫、白、绿、玉青、淡紫、绿粉、黑与红甲仍沿基础倒U头口、短胸、直裤/L靴模板；不同色块与局部短刺不能直接变成八个新设计组。cloud中间旋纹、purity异色肩腰记录为材料变化；shadow只有帽靴，不补完整套。', True)
    add('shadowlands_band_trim_family', 'shadowlands:creeper_alloy shadowlands:voiddiver', '绿金与淡紫套装以胸横带、裤腰带和靴口重复材料分节；非同像素，保守一个横带板甲学习组。窄边形成装甲片关系，不能放大为整面细条纹。')
    add('shadowlands_fire_accessory_family', 'shadowlands:firey shadowlands:starcrystal', '橙红两套在基本甲壳旁添加离散火粒/星刺，衣甲仍短宽。保守同热色附饰族，不按独立粒子或部位增加数目。静态图标中的火点不等于证明游戏有粒子或发光。')
    add('shadowlands_small_wing_cap', 'shadowlands:glowshroom_master', '绿黑基础衣裤配两侧短外伸帽片；物品比例仍简单，少量帽侧形变就能有身份，不需要巨头冠。只是原始图标观察，不推断特殊身体模型。')
    add('unrealium_dark_purple_insets', 'shadowlands:nightbreaker tenebrous_lands:purple', '黑紫头罩与黑底高亮紫胸裤作为既有暗底紫嵌片组的补充，不新增组。大块无层次荧光紫胸和过暗帽口是反例，不能用满幅饱和色取代材料分区。', True)
    add('splendour_textured_metal_family', 'splendour_ablaze_epoch:bronze splendour_ablaze_epoch:cupronickel', '橙铜三件与绿镍铜胸靴都用大金属面、窄暗缝、局部铆接表示材料；保守同族。铜纹偏密、鞋头偏圆，不把较高细节密度当成项目MC比例合格的依据。')
    add('splendour_ornate_legwear_family', 'splendour_ablaze_epoch:celesterral splendour_ablaze_epoch:damascene_steel', '蓝白金长护腿与红布银护腿各只有裤靴，保守同腿部材料连接学习组。白金膝片/深色内衬、银胫片/红裤的主次可学，不补想象中的头胸，也不按两个部件计四设计。')
    add('splendour_magnetic_white_plate', 'splendour_ablaze_epoch:magnetic_steel', '四件白银甲由浅板面、灰暗连接和少量铜红臂/膝带联系，套装一致；弧顶盔和鼓肩仅参考材质而非照搬轮廓。原稿的较碎斜亮线是需克制的部分。')
    add('magistu_closed_helmet_family', 'supernatural:gothic_diamond supernatural:gothic_golden supernatural:gothic_iron supernatural:gothic_netherite', '四种材质Gothic头盔为同一封闭横面窗模板，保守追加已读闭面头盔组，零新增设计信用。横暗面缝与鼻条是甲壳设计，不能为了露脸把金属主体清空。仅头件不冒充四套。', True)
    add('european_plate_shared_kit_conservative', 'tenebrous_lands:iron tenebrous_lands:medieval_netherite', '白铁/暗灰带红缨的两套以胸片、腰带、棕裤连接和靴筒分段表达板甲，保守追加既有板甲套件组。缨尖不算新设计，头壳里的白银与暗鼻条都保留设计意义。', True)
    prov = json.loads((D / 'provenance.json').read_text())
    flat = [c for row in rows for c in row['cases']]
    assert len(flat) == len(set(flat)) == 37 and set(flat) == {c['case_key'] for c in prov['cases']}
    assert sum(row['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP' for row in rows) == 9
    review = {'reviewed_at': datetime.now(timezone.utc).isoformat(), 'pages_opened': [f'icons-{i:02}.png' for i in range(1, 7)],
              'observations': rows, 'raw_index_name_families_before_normalization': 69,
              'normalized_name_families': 37, 'false_name_family_inflation_removed': 32, 'native_icon_png_viewed': 111,
              'new_conservative_learning_groups': 9, 'append_to_existing_groups': 4,
              'combined_reviewed_name_families': 341, 'combined_armor_name_families': 340,
              'combined_conservative_learning_groups': 145, 'gate_met': False, 'new_artwork': 0, 'production_changes': 0,
              'limits': '命名纠错不产生设计信用；学习组含部位不全及反例，不等同145套独立完整设计验收。'}
    (D / 'semantic-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: review[k] for k in ['raw_index_name_families_before_normalization', 'normalized_name_families', 'native_icon_png_viewed', 'new_conservative_learning_groups', 'combined_conservative_learning_groups']}, ensure_ascii=False))


if __name__ == '__main__':
    main()

"""Material/outline observations from all seven reviewed source contact sheets."""
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

    add('material_layout_skull_vent_metal_family', 'mutationcraft:metal_armor mutationcraft:rusted_metal_armor',
        '灰金属骷髅面罩、胸中央大圆孔/扣件、抬肩与胫侧细支架在两套中高度相同，锈版仅增橙棕腐蚀区，保守合一族。部位身份清楚，但细密灰点和颅骨面孔使其偏写实插画；只学氧化集中边缘与主面分区，不照搬噪点、圆胸孔或人脸。实际字面穿戴纹理均128×64，未套64×32探针。')
    add('gray_stone_suit_conservative', 'callfromthedepth_:marblearmor',
        '短宽米灰甲片配青色小嵌块，头盔留低开口，靴保留两脚空隙，追加既有石质甲学习组。库存像素偏深橄榄，而已追通的原生穿戴图很浅、白米纹较碎；这是图标/穿戴材质表达不同的明确来源观察，不能仅凭名字或同尺寸断言一致，也不据此修改外部模组。', True)
    add('organic_aquatic_horned_plate', 'callfromthedepth_:soularmor',
        '黑青底上少量亮青胸心、胫侧和横向角盔，追加上一批水系角盔板甲族；两侧角较宽，胸部亮点很小，不能继续扩大冠角替代短宽胸身。四部位声明initializeClient，原生图集128×128，静态纹理链通不等于已审完自定义几何或目标UV。', True)
    add('vanilla_outline_elemental_palette',
        'the_awakening_of_the_elder_souls:bronze_armor the_awakening_of_the_elder_souls:bronze_ultrarite_armor the_awakening_of_the_elder_souls:eclipse_armor the_awakening_of_the_elder_souls:emerald_armor the_awakening_of_the_elder_souls:enderite_armor the_awakening_of_the_elder_souls:ruby_armor the_awakening_of_the_elder_souls:sapphire_armor the_awakening_of_the_elder_souls:sapphire_ultrarite_armor the_awakening_of_the_elder_souls:ultrarite_armor',
        '九个名称沿倒U盔、短宽胸、两条直裤和L靴模板；铜/红宝/蓝宝是大色块加暗侧边，升级版、日食、末地色和紫材用横胸分节与窄盔眼缝。标准与升级铜裤实际引用同一PNG，蓝宝两版裤也同图，不能按名称或四部位拆计。绿宝色过荧光、升级胸中央过亮是材料层级的反例；浅色横胸不是透明背景。九个名称全部追加模板组，不增九套设计信用。', True)
    add('molten_plate_dark_shell', 'the_awakening_of_the_elder_souls:flaming_komodo_leather_armor',
        '黑色基础甲的橙红竖条/散格贯穿四件，追加已有熔融暗壳材料组。与铜红宝的平面大色块相比，穿戴图黑橙交错过密，缩略像棋盘；只借鉴热材质在分缝处强调，不把密集噪点当精致，也不由名字推断伤害阶段。', True)
    flat = [c for row in rows for c in row['cases']]
    p = json.loads((D / 'provenance.json').read_text())
    assert len(flat) == len(set(flat)) == 14 and set(flat) == {c['case_key'] for c in p['cases']}
    result = {
        'reviewed_at': datetime.now(timezone.utc).isoformat(),
        'pages_opened': ['icons-01.png', 'icons-02.png'] + [f'worn-{i:02}.png' for i in range(1, 6)],
        'observations': rows, 'excluded_cases': [],
        'name_families_viewed': 14, 'native_icon_entries_viewed': 56, 'native_worn_entries_viewed': 28,
        'item_model_declarations_read': 56, 'class_declarations_read': 73,
        'complete_static_item_chains': 56, 'complete_static_name_families': 14,
        'new_conservative_learning_groups': 1, 'append_to_existing_groups': 4,
        'source_rectangle_findings': '11套64×32候选的22图集作原图矩形探针；L1袖底与四侧末行均空，L2实心上身仅后5行。128×64/128×128的6图集不强行套标准探针。源事实不是目标几何/实机验收，不复制掩码，不把后5行硬套给所有Dynasty衣袍。',
        'limits': '56条静态注册/构造/槽位/JSON/字面纹理链已核；未排除全局渲染覆盖，未运行游戏或验收目标UV。190学习组含变体、局部与反例，不等于190个已验完整独立设计。',
        'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'gate_met': False,
    }
    (D / 'semantic-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('14 complete-name cases / 56 icons / 28 worn entries / 1 new conservative group')


if __name__ == '__main__':
    main()

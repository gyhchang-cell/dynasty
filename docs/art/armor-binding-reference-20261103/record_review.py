"""Record inspected native artwork and keep static bindings separate from game acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import json

D = Path(__file__).resolve().parent


def main():
    rows = [
        {
            'semantic_group': 'vanilla_outline_elemental_palette',
            'prior_group': 'vanilla_outline_elemental_palette',
            'credit': 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS',
            'cases': ['celestial_core:guardian_ocean', 'celestial_core:sakura',
                      'slendytubbies_craft:azurite_2_armor', 'slendytubbies_craft:berikelt',
                      'slendytubbies_craft:pure_iron_armor', 'slendytubbies_craft:redgold1'],
            'observation': '六个名称的倒U头盔、短宽胸身、直裤与L靴均属基础甲模板材料变体，保守追加既有学习组，不按颜色或四个部位增加独立设计。海洋玉绿、樱粉的浅亮区主要在顶部和胸面；深青/亮青套通过少量大亮面表达金属；纯铁白灰属于主体，不能当白底删除；暗红套维持暗边和局部亮红。只有四套slendy完成了注册、部位类、物品模型到声明穿戴路径的静态链，另外两套外部材质实现未核完。',
        },
        {
            'semantic_group': 'binding_virtual_gold_custom_uv',
            'credit': 'NEW_CONSERVATIVE_LEARNING_GROUP',
            'cases': ['celestial_core:virtual_gold'],
            'observation': '红橙主体配粉色侧面凸片，头侧与裤侧外挑明显，可作为过度扩张轮廓的限制反例。客户端装备扩展明确选择VGArmorModel，裤走inner，其余outer；模型声明64×64且腿有(16,48)等偏移，不能套用Dynasty标准64×32袖底/腰线矩形。图标引用明确，最终穿戴纹理路径仍依赖未核完的外部实现；一套而非四部位或两图集多套。',
        },
        {
            'semantic_group': 'binding_warding_plate_cloth_panels',
            'credit': 'NEW_CONSERVATIVE_LEARNING_GROUP',
            'cases': ['spellblademod:warding'],
            'observation': '青色板片与深绿布裤以大材料面分开，肩缘浅亮、竖向绑带、裤腿青色补片在小图中仍清楚，可借鉴金属/衬布在四件中的对应位置。不是把整个人体画进胸甲图标，也不将绿布变为细噪点。warding_chest物品模型实际指向warding_chestplate图；候选diamond_warding穿戴层虽有明确材质名线索，但注册选材和最终命名空间拼接未追完，保留待核。',
        },
    ]
    details = {
        'celestial_core:guardian_ocean': '通用helmet/boots文件名实际位于guardian_ocean子目录，按模型JSON归类；ocean穿戴图不能仅凭近似名称认定绑定。',
        'celestial_core:sakura': '同名通用部件位于sakura子目录，物品JSON明确；粉色四件不新增模板设计。',
        'celestial_core:virtual_gold': '自定义64×64几何声明仅用来限制图集比较，不修改人物身体/骨骼，也不将其当原版UV证据。',
        'slendytubbies_craft:azurite_2_armor': '四件字面getArmorTexture选择azurite_armor__layer_1/2，配深青图标。',
        'slendytubbies_craft:berikelt': '四件选择b2erikelt_armor而非同时存在的b1图集；b1只作为未选中的对照，不加设计信用。',
        'slendytubbies_craft:pure_iron_armor': '注册pur_iron_armor与图标文件pure_iron_armor_*不同，使用JSON引用和供应器链核对，不能从文件后缀猜部位。',
        'slendytubbies_craft:redgold1': '注册red_armorst_st、图标redgold1、字面穿戴red2_gold_armor三种命名不能互猜；另对red_gold不计第二套。',
        'spellblademod:warding': '板片/布层大分区有适用性；候选穿戴层仅按原图检查，不能写成实际绑定验收。',
    }
    review = {
        'reviewed_at': datetime.now(timezone.utc).isoformat(),
        'pages_opened': ['icons-01.png', 'icons-02.png'] + [f'worn-{i:02}.png' for i in range(1, 5)] + ['binding-focus.png'],
        'observations': rows, 'case_observations': details,
        'name_families_viewed': 8, 'native_icon_png_viewed': 32, 'native_worn_entries_viewed': 20,
        'item_model_declarations_read': 32, 'class_declarations_read': 30,
        'complete_static_item_chains': 16, 'sets_with_complete_static_chain': 4,
        'sets_with_unresolved_worn_chain': 4,
        'new_conservative_learning_groups': 2, 'append_to_existing_groups': 1,
        'source_rectangle_lessons': [
            '四套已确认声明的L1源矩形[48,16,52,20)为空，四侧末行也为空。矩形事实有助于区分短袖与孤立袖底；不排除全局渲染覆盖，不冒充目标几何验证。',
            '四套L2上身探针的三个非零像素alpha仅1；按alpha>0与>=128分别记录，不能把几乎透明残留误说成实心上身，也不能直接复制外部掩码。',
            '先确认声明选择的图集，再分析像素；同目录b1/b2或red/red2不等于可互换，更不是新增独立设计。',
        ],
        'new_artwork': 0, 'production_changes': 0, 'game_starts': 0, 'gate_met': False,
        'limits': '原生图和静态声明已读，仍不是目标穿戴、整体生态覆盖或实机验收。184保守学习组含局部、变体与反例，未验为184套完整独立设计。',
    }
    p = json.loads((D / 'provenance.json').read_text())
    flat = [c for r in rows for c in r['cases']]
    assert len(flat) == len(set(flat)) == 8 and set(flat) == {c['case_key'] for c in p['cases']} == set(details)
    (D / 'semantic-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
    print('D12: 8 names / 32 icons / 20 native worn entries / 2 new learning groups')


if __name__ == '__main__':
    main()

"""Record actual visual study; accessory/uncertain slots get no full armor credit."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile

D = Path(__file__).resolve().parent


def main():
    prov = json.loads((D / 'provenance.json').read_text())
    rows = []

    def add(group, cases, note, prior=False):
        rows.append({'semantic_group': group, 'cases': cases.split(), 'observation': note,
                     'credit': 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' if prior else 'NEW_CONSERVATIVE_LEARNING_GROUP',
                     **({'prior_group': group} if prior else {})})

    add('functional_neptunium_layered_scale', 'aquaculture:neptunium', '青绿四件沿短胸直腿分区，头侧突出与胸甲层叠表示水生金属甲；亮点偏多，只学深底/浅板/暗接缝的主次，不复制细碎检查纹或大侧角。四部件归一学习组。')
    add('functional_brewfest_clothing', 'brewery:brewfest', '八图是蓝白衬衫/红裙与蓝格短衣/棕裤的职业衣装族；紫帽及红帽换色不另计。白衣领和围裙是主体，鞋图偏横短，不照搬为原版靴筒比例。两套穿戴图为64×64原生图集，尚未证明模型绑定。')
    add('functional_white_chef_cloth', 'candlelight:chefs', '白厨师帽、白色纽扣上衣、灰格裤和黑鞋靠大材料区表达职业；竖纽扣列克制，帽子鼓形不拿来改变已有甲盔轮廓。白衣不可按白背景删除；64×64穿戴图分区只作观察。')
    add('functional_farmer_straps', 'kaleidoscope_cookery:farmer', '棕胸配白肩带、蓝直腿配棕腰及棕靴；两版本六图只一衣装族。两版本layer_1/layer_2分别同字节，不是四个设计。浅肩带对深衣块可借鉴粗麻/织锦层次，不照抄具体图样。')
    add('functional_tattered_cloth', 'majruszsdifficulty:tattered', '灰紫布衣边缘的垂片、兜帽暗面和裤脚缺口表现破旧织物；保留有意断边，不把所有透明缺口强制闭合。低对比斑点只作克制的磨损，不铺满噪点。')
    add('functional_fur_color_block_clothing', 'meadow:fur', '实际是紫粉头领、蓝胸和黄中心、棕靴的衣装，并非凭fur名称臆测米白毛皮。可学领口、胸主面、腰部三块比例，现有竹布甲不照搬艳色。')
    add('functional_masticated_partial_chest', 'undergarden:masticated', '只读到暗棕粗糙胸部单件；暗面混成一团，是缩小后材料辨识差的反例，不补想象中的头裤靴，更不称完整套装。')
    add('functional_winemaker_apron', 'vinery:winemaker', '红围裙、蓝裤、棕鞋用三个主材料区说明用途；围裙下沿偏斜，穿戴原图另有帽及带片，不凭图集碎片编造已注册部件。64×64布局不能直接套Dynasty原版身体UV。')
    add('functional_wooled_boot_material_variants', 'wooledboots:redy1aye_copper_wooled wooledboots:redy1aye_waxed_copper_wooled wooledboots:therrassium_wooled wooledboots:wooled_chainmail wooledboots:wooled_diamond wooledboots:wooled_golden wooledboots:wooled_iron wooledboots:wooled_leather wooledboots:wooled_netherite', '九图共享成对L形靴底模板，铜蜡差别和铁金钻材质换色保守一组。白色主要在鞋底/脚缘，不能误记为靴口毛边。铁与皮穿戴原图只作足部材质区研究，不算整套盔甲或新增层设计。')
    add('biome_closed_diving_equipment', 'create:copper_diving create:netherite_diving', '铜盔青色圆窗与暗盔橙色横窗、长筒靴沿闭合潜水装备既有族追加；铜/下界合金不算两套新结构。窗口轮廓可参考功能表达，禁止为露脸清除封闭面甲。', True)
    add('vanilla_outline_elemental_palette', 'dimdoors:woven_world_thread majruszsdifficulty:enderium', '黑布与紫甲沿基础短胸、直裤、L靴的材料变化归既有模板族。黑布胸的弱灰分段在小图难辨，是保留材料主面的反例；不能把配色或四部件算新套数。', True)

    rooted = next(c for c in prov['cases'] if c['case_key'] == 'artifacts:rooted')['icons'][0]
    entry = 'data/artifacts/tags/items/slot/feet.json'
    with zipfile.ZipFile(rooted['jar']) as z:
        raw = z.read(entry)
    assert 'artifacts:rooted_boots' in json.loads(raw)['values']
    excluded = [{'case_key': 'artifacts:rooted', 'kind': 'PLAYER_ACCESSORY_NOT_FULL_ARMOR',
                 'reason': '单只侧视棕靴带绿根，原生feet饰品标签；不是非玩家装备，也不按普通全套盔甲计数。',
                 'source': {'jar': rooted['jar'], 'entry': entry, 'sha256': hashlib.sha256(raw).hexdigest(), 'inspected_key': 'values', 'value': 'artifacts:rooted_boots'}}]
    confluence = sorted(c['case_key'] for c in prov['cases'] if c['case_key'].startswith('confluence:'))
    excluded += [{'case_key': c, 'kind': 'FOOTWEAR_ICON_SLOT_NOT_PROVEN_FOR_FULL_ARMOR_GATE',
                  'reason': '功能靴图标可作足部形状学习；尚无普通盔甲绑定证据，暂不计入全套盔甲门槛。'} for c in confluence]
    supplementary = [{'cases': confluence, 'additional_armor_design_credit': 0,
                      'observation': '十一名称十二图以成对L靴加翅片、火焰或异色边表达功能；花靴为单侧视图，Terraspark两版本仍一族。蓝绿、棕、紫、橙的局部变体合并研究，不从静态火点推断游戏效果。'},
                     {'cases': ['artifacts:rooted'], 'additional_armor_design_credit': 0,
                      'observation': '单侧棕靴配绿根，主体形状明确，但配饰图标与普通盔甲穿戴图需分开。'}]
    flat = [c for row in rows for c in row['cases']] + [e['case_key'] for e in excluded]
    assert len(flat) == len(set(flat)) == 33 and set(flat) == {c['case_key'] for c in prov['cases']}
    review = {'reviewed_at': datetime.now(timezone.utc).isoformat(),
              'pages_opened': [f'icons-{i:02}.png' for i in range(1, 6)] + ['worn-01.png', 'worn-02.png'],
              'observations': rows, 'supplementary_observations': supplementary, 'excluded_cases': excluded,
              'name_families_viewed': 33, 'armor_name_families_included': 21,
              'native_icon_png_viewed': 68, 'native_worn_entries_viewed': 10, 'distinct_worn_payloads': 8,
              'new_conservative_learning_groups': 9, 'append_to_existing_groups': 2,
              'combined_reviewed_name_families': 374, 'combined_armor_name_families': 361,
              'combined_conservative_learning_groups': 154, 'gate_met': False,
              'new_artwork': 0, 'production_changes': 0,
              'limits': '154含单件、不完整套与反例，不是154套已验独立设计；饰品与绑定不明的12名称保留学习但不给盔甲门槛信用。图集原图不是游戏/穿戴验收。'}
    (D / 'semantic-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
    print('D9: 33 names, 68 icons, 10 worn entries; 9 learning groups, 12 excluded from full armor gate')


if __name__ == '__main__':
    main()

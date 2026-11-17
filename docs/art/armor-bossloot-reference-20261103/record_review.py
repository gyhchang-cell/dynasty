"""Actual observations of all 103 native icons, conservative semantic families."""
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

    add('bossloot_dragon_bone_plate', 'block_factorys_bosses:dragon_bone', '暗棕头胸以橙亮角尖和胸中竖带表达热骨甲，补全棕靴/橙直裤；亮色控制在结构节点可学。大角、满橙裤与深胸的材料比例不直接照搬已有套装。')
    add('european_plate_shared_kit_conservative', 'block_factorys_bosses:knight royalvariations:royal_knight mythsandlegends:ironshade undead_unleashed:grave_metal', '四族均为金属盔窗、胸片与腰裤连接的骑士板甲变化，保守追加既有板甲组，不按红缨/蓝脊/材质分成新设计。皇家cuirass正是胸甲部件，已并回royal_knight。灰白大胸片配暗裤、亮膝/胫片保留可辨分节；暗墓铁全套对比偏弱是反例。', True)
    add('unrealium_dark_purple_insets', 'dragonloot:dragon dragonloot:upgraded_dragon undead_unleashed:nightweaver', '暗龙甲紫眼、升级胸两侧紫片和暗紫短靴追加暗底紫嵌片组；升级胸仍是同族变体，夜织仅靴，不冒充三套完整甲。暗色主面应留可辨平面，不靠整体黑团或细微灰差表达全部材料。', True)
    add('bossloot_spawner_cage_plate', 'dungeonnowloading:spawner', '深蓝甲以青色条架、头部红点和框状腰腿形成笼架身份，图标四件一致；局部中空与边架可启发机关材料分层，但不把全部胸面变成细格网。没有图标外的身体/游戏效果证据。')
    add('vanilla_outline_elemental_palette', 'dungeonnowloading:tempest weirdmobs:basaltsnake', '亮青基础甲与棕橙基础甲仍是短胸、直裤、L靴模板材料变化，保守追加既有基础轮廓组。青胸大浅面有清楚暗侧，棕橙胸接近平涂，是避免用单饱和面代替材料的对照。', True)
    add('bossloot_dragon_priest_robes', 'ice_and_fire_spellbooks:fire_dragon_priest ice_and_fire_spellbooks:ice_dragon_priest ice_and_fire_spellbooks:lightning_dragon_priest', '三套黑灰肩胸、长下摆、分腿内衬和角冠共享同模板，仅红/蓝/紫内衬变化，合一族。长衣与裤腿的主次可学，黑冠过暗且外挑，不直接改变已有头盔比例。')
    add('bossloot_bone_sculk_rib_armor', 'legendary_monsters:annihilator weirdmobs:wardendragon', '绿青暗底配米白骨片、胸肋横段、暗直裤和浅靴缘；两族有不同头结构，保守一个骨/暗底分区学习组。亮肋不是白框背景；角/外伸附片只能在MC主体上克制处理。')
    add('bossloot_blastproof_closed_mask', 'legendary_monsters:blastproof', '只见金黄封闭面罩，暗眼口与下部橙边说明甲壳厚度；是头件研究，不据名称声称全套抗爆数值或游戏穿戴已验。')
    add('bossloot_fiery_boot_edge', 'legendary_monsters:fiery', '单对黑高筒靴以橙黄脚缘集中亮色，保留长直靴筒和分开两脚；只学暗靴/亮底的材料主次，不从静态颜色推断发光或粒子。')
    add('bossloot_mossy_stone_chest', 'legendary_monsters:mossy', '灰胸主块配绿肩苔块，仅胸件。材料区域比随机绿点更清晰；缩小仍需留石面，不能将青苔和背景混成噪点。')
    add('bossloot_kobeko_shared_armor_family', 'monsterexpansion:kobeko_leivekilth monsterexpansion:leivekilth monsterexpansion:kobeko_rhyza monsterexpansion:rhyza', '蓝白/紫米白胸的交叉带、肩片与裤膝片有共同组织，kobeko版本主要在胸结构和帽形变化，四名称保守同族。补全见蓝帽/米白兜帽、金膝板和短靴；不能把特定胸型/帽型组合拆成多套信用。')
    add('bossloot_frosthowl_pale_hide', 'mythsandlegends:frosthowl', '米白毛皮头罩、白胸下沿与棕腰/白裤形成衣料和皮带区，白短靴承接；保留白主体，不能去白底时误删。毛边只需少量阶梯，不铺细毛或扩大耳角。')
    add('bossloot_soulpiercer_blue_hood', 'mythsandlegends:soulpiercer', '蓝兜帽、蓝肩袖配灰胸、蓝裤配灰靴是布/甲两区，不靠复杂符文。补全头靴后才观察整套关系；不拿原始两部件就声称完整。')
    add('bossloot_infected_organic_plate', 'spore:infected spore:infected_up', '肉色基础甲以暗红筋条连接头胸裤靴，升级胸额外长红侧条，仍同一有机甲族。反例是主体接近皮肤人台，Dynasty应学粗大筋片与暗接缝，不照抄写实肉身造型。')
    add('bossloot_stalwart_material_variants', 'stalwart_dungeons:chorundum stalwart_dungeons:tungsten stalwart_dungeons:warted_tungsten', '紫白/青暗底与灰绿、红绿四件用相近胸横片、腰带和靴口组织，材料变化保守一个族；亮色占小板面且暗内衬连贯可学，红绿大互补面容易抢主体，不当精致与否的唯一依据。')
    add('bossloot_blazewolf_single_mask', 'weirdmobs:blazewolf', '仅黄色兽耳头件，橙暗眼口与高亮头顶说明面罩；外观更像兽脸，作为人形盔甲误变生物头像的反例，不补想象胸裤靴。')
    add('bossloot_phantomfox_cloth_plate', 'weirdmobs:phantomfox', '蓝短裤/头罩配米白胸领与浅靴面，只有两主材料仍能成套。短耳与横眼口让头件有身份，但不能把已有MC倒U脸口全部换为动物头像；白胸领和靴面均非背景。')
    p = json.loads((D / 'provenance.json').read_text())
    flat = [c for r in rows for c in r['cases']]
    assert len(flat) == len(set(flat)) == 32 and set(flat) == {c['case_key'] for c in p['cases']}
    review = {'reviewed_at': datetime.now(timezone.utc).isoformat(),
              'pages_opened': [f'icons-{i:02}.png' for i in range(1, 6)] + ['completion-view.png'],
              'observations': rows, 'raw_index_name_families': 33, 'normalized_name_families': 32,
              'native_icon_png_viewed': 103, 'same_family_parts_added': 15,
              'new_conservative_learning_groups': 14, 'append_to_existing_groups': 3,
              'new_artwork': 0, 'production_changes': 0, 'gate_met': False,
              'limits': '文件与名称只是原生图标研究，不替代注册、模型绑定、获取数值或游戏穿戴；学习组包含单件/反例，不是完整独立设计验收。'}
    (D / 'semantic-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
    print('D10: 32 normalized names / 103 icons / 14 conservative learning groups')


if __name__ == '__main__':
    main()

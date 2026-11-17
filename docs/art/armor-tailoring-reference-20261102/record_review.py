"""Hand-written observations from six icon pages, four worn pages and two source probe pages."""
from datetime import datetime, timezone
from pathlib import Path
import json

D = Path(__file__).resolve().parent


def main():
    rows = []

    def add(group, cases, observation, prior=False):
        rows.append({'semantic_group': group, 'cases': cases.split(), 'observation': observation,
                     'credit': 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' if prior else 'NEW_CONSERVATIVE_LEARNING_GROUP',
                     **({'prior_group': group} if prior else {})})

    add('vanilla_outline_elemental_palette', 'aether:gravitite aether:neptune aether:obsidian aether:zanite aether:sentry dark_souls_expansion:leather immersive_armors:emerald immersive_armors:slime', 'Aether粉紫、蓝、黑紫、紫及灰靴、DarkSouls灰白leather图标、Immersive灰度emerald和绿slime均围绕基础倒U头口、短胸、直裤与L靴模板；材料/纹理有变化但不新增组。sentry仅一对靴，不冒充整套。原始灰度不代表最终染色后的外观，绑定/染色未实测。', True)
    add('aether_phoenix_short_earlets', 'aether:phoenix', '橙金四件基本比例接近原版，帽顶两侧短翼/耳片提供小幅剪影区别，胸中央亮面较大；不通过放大肩甲增加强力感。附属经典包版本没有另计，当前索引非assets根目录包也没有误当命名空间。')
    add('aether_valkyrie_white_gold_crown', 'aether:valkyrie', '白甲、金肩/金边、头顶分开的金冠短片，以及金白护腿相互对应；穿戴原图也维持浅色主体和局部金色。可借鉴鸿蒙的白金材料分工，不能复制冠片、中心图案或照搬UV。')
    add('souls_black_knight_dark_silhouette', 'dark_souls_expansion:black_knight', '深灰胸上缘短角、双竖角封闭头件及高深色靴构成尖锐身份；只见三件，不补裤。全暗部缩小容易粘连，需保留暗底上的阶梯亮面，不把轮廓无限拉长。')
    add('souls_falconer_cloth_hood', 'dark_souls_expansion:falconer', '棕帽圈与灰脸罩、红布短胸和棕靴分出软硬材料。面前灰块属于设计，不能自动抠除为露肤。三件结构归一套，布料红面不等同红金属。')
    add('souls_silver_enclosed_plate_family', 'dark_souls_expansion:fluted_knight dark_souls_expansion:havel', '银灰甲以分隔胸片、封闭面盔和棕暗接缝为主；Fluted偏横鼻梁，Havel偏竖面罩，保守同一闭面板甲学习组。二者并非同像素或已证同模型，不以三件数量凑六例。')
    add('souls_hollow_partial_mail', 'dark_souls_expansion:hollow', '灰色胸面与短面罩，仅两件；胸下收尖、领口深，与全封闭大桶盔不同。穿戴layer2完全透明，因此不能为了整套看齐凭空补满躯干和裤面。空层也不算一个新设计。')
    add('souls_hunter_brown_panels', 'dark_souls_expansion:hunter', '仅棕色长靴与米棕分段衣胸，浅横条在暗布底上形成可读节奏。借鉴衣扣/布面分区，不能据未出现的头裤脑补一套参考。')
    add('immersive_divine_sparse_trim_reference', 'immersive_armors:divine', '原始图标只有白色肩点、弧边、裤带片，属于稀疏底层/附层式结构研究；不能把灰白点片当完整神圣盔甲稿，更不能据此增加完整套装的验收信用。保留为边界反例学习组，完整绑定尚未核实。')
    add('immersive_robe_open_front', 'immersive_armors:robe', '原始灰袍图标有前胸大开口，窄纵衣缘和简单兜帽，四件不等于四参考。所读穿戴由body_middle/body_lower、leggings_middle/lower与overlay拆分；同为64×32也不能全贴到普通人体图集。')
    add('european_plate_shared_kit_conservative', 'immersive_armors:heavy magistuarmory:ceremonial magistuarmory:cuirassier magistuarmory:halfarmor magistuarmory:rustedhalfarmor magistuarmory:knight magistuarmory:platemail magistuarmory:rustedplatemail magistuarmory:wingedhussar magistuarmory:xivcenturyknight', '重型灰板甲、礼服金边、半甲/锈半甲、骑士、翼骑兵与十四世纪甲等共享原版紧凑白亮胸/灰侧/暗连接结构；部位缺失、金边及锈蚀版本不新增设计组，保守并入既有板甲套件组。cuirassier只有裤靴，wingedhussar仅胸，不能按名字补翅膀。', True)
    add('magistu_chainmail_rust_family', 'magistuarmory:chainmail magistuarmory:rustedchainmail', '常规与锈蚀锁甲的粗网格、护腿和包头口为同系，棕锈色不能算新设计。肩胸铁网、底部棕边/皮靴体现材质分开；原始网纹密度可作反例，项目不靠细棋盘表达高级感。')
    add('magistu_crusader_rust_family', 'magistuarmory:crusader magistuarmory:rustedcrusader', '普通/锈色十字军套按一族合并；头盔横眼缝和分片面甲是有意封闭，胸甲开口、腰横条和暗中心区别明确。layer1和layer2分别承载不同范围，不能根据某一透明区单独认定资源丢失。')
    add('magistu_lamellar_single_vest', 'magistuarmory:lamellar', '仅灰白片甲短胸，竖向边片与中央斜格相区分；不虚构头裤鞋。作为单件布局参考，不把片甲每列作为独立设计。')
    add('magistu_closed_helmet_family', 'magistuarmory:face magistuarmory:norman magistuarmory:rustednorman magistuarmory:shishak', '四种只出现头件的面甲/鼻甲/锈鼻甲/尖盔，保守归一个头件学习组。正面短横缝、鼻条、尖顶有差别，但锈版不新增；这是头盔参考，不是假造四套全身甲。')
    prov = json.loads((D / 'provenance.json').read_text())
    flat = [c for row in rows for c in row['cases']]
    assert len(flat) == len(set(flat)) == 37 and set(flat) == {c['case_key'] for c in prov['cases']}
    new = sum(r['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP' for r in rows)
    assert new == 13
    record = {'reviewed_at': datetime.now(timezone.utc).isoformat(),
              'pages_opened': [f'icons-{i:02}.png' for i in range(1, 7)] + [f'worn-{i:02}.png' for i in range(1, 5)] + ['sleeve-source-rectangles.png', 'waist-source-rectangles.png'],
              'observations': rows, 'icon_name_families': 37, 'original_icon_png': 104,
              'selected_worn_entries': 23, 'distinct_worn_png': 21,
              'new_conservative_learning_groups': new, 'append_to_existing_groups': 2,
              'prior_learning_groups_reused': 104, 'combined_conservative_learning_groups': 117,
              'combined_name_families': 264, 'gate_met': False, 'new_artwork': 0, 'production_changes': 0,
              'limits': '学习组含不完整装备与材料/层结构反例，不等于已验证的独立完整设计。部件、锈蚀、换色、空附层、经典包版本均不另计；未实机。'}
    (D / 'semantic-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['icon_name_families', 'original_icon_png', 'new_conservative_learning_groups', 'combined_conservative_learning_groups']}))


if __name__ == '__main__':
    main()

"""Actual observations of native armor/clothing, including sparse partial references."""
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

    add('mixed_caveman_asymmetric_hide', 'ageofweapons:caveman', '棕皮单肩胸与短腰裙、低帽和分靴构成原始皮衣族；斜肩披片和腰裙表达用途，不是标准金属胸板。不把短裤/帽放大为完整人台，也不以密集棕斑替代粗皮面。')
    add('mixed_rusty_metal_helmet', 'alshanex_familiars:rusty', '只见蓝银头件，橙锈局限一侧与下缘，亮金属面和锈区分离。可学氧化作为少量材料区，不据rusty名称画满随机噪点，不补不存在的同套部件。')
    add('souls_hunter_brown_panels', 'bloodandmadness:hunter', '灰暗长裤/黑鞋与补读黑色折边帽、棕面罩作为既有猎人衣料组的部分补充；图像对比很低是反例，不能声称看到完整上衣。帽+面罩是同张图内主体，不算两个设计。', True)
    add('unrealium_dark_purple_insets', 'born_in_chaos_v1:nightmareboots unusualend:ender_scrap', '暗灰成对靴与黑腰紫腿均仅单部位，追加已有暗底紫嵌片学习组。保留靴筒和两脚间隙，不能只因靴或裤有不同名称就补一套设计信用。', True)
    add('mixed_spiny_shell_partial_chest', 'born_in_chaos_v1:spinyshellchestplate', '只见灰蓝分层胸，肩片与腹部向下收拢，少量高亮让壳片可辨；是局部结构研究，肩刺不能扩大成压住胸身的装饰团。名称未分隔的后缀没有被拆成多件设计。')
    add('mixed_coral_segmented_armor', 'call_of_drowner:coral', '蓝胸/蓝靴配紫冠肩和金腰胫形成三种大材料区；补全帽靴后见全套互相对应。颜色饱和偏高，项目只借鉴关节/板片位置，不逐色照搬或用渐变混合。')
    add('vanilla_outline_elemental_palette', 'call_of_yucutan:jade enderitemod:enderite fathomless:crimson jerotes:copper rainbowcompound:obsidianite rainbowcompound:rainbow', '玉绿、深绿、暗红、铜橙、紫与彩虹均沿基础倒U盔、短宽胸、直裤和L靴变化，保守追加既有模板。铜的离散亮暗侧面可学，彩虹横带和全紫胸容易掩盖材料，作为限制反例，不按换色计六套。', True)
    add('mixed_celestial_inlay_family', 'celestisynth:lunar_stone celestisynth:solar_crystal', '紫蓝/月与红紫/日四件共享橙金边和中心亮片结构，补全月石三件后才能比较整套，保守同一嵌片甲族。中心明亮点保留大面积内衬，不扩大成圆环胸躯；头侧外挑需克制。')
    add('bossloot_bone_sculk_rib_armor', 'deeperdarker:warden', '青暗底配米白肩/胸纵骨和浅腰带，追加已读骨/暗底族；两侧角冠明显，身体主件依然短胸直腿。白骨不是白背景，不用扩大角冠来表现强度。', True)
    add('mixed_crying_armor_shared_addon_family', 'enigmaticaddons:crying enigmaticlegacy:crying', '两来源紫金胸的主体形状高度相近，仅高光/暗边略有差异，按同一哭泣甲族而非跨模组两套。裤膝紫亮、金鞋底与补读尖角盔一致；小图中金边不过多铺满紫主面。')
    add('mixed_dark_red_slit_plate', 'enigmaticlegacy:dark', '暗灰套装通过胸横板、灰膝/靴口及头盔红眼缝建立分段；是黑甲不依赖满幅高饱和亮纹的例子。胸的细弱灰差在缩小后不足，仍须保留大块平面。')
    add('mixed_dream_shadow_asymmetry', 'fantasy_ending:dream_shadow', '蓝/紫左右分色和分离的外侧阶梯片贯穿四件；结构可读但像发散能量人台，作为过度外挑和高亮吞掉甲壳的反例，不能把这种效果直接套鸿蒙甲。')
    add('mixed_nether_star_pale_plate', 'fantasy_ending:nether_star', '浅灰紫板甲与橙白大星状头件形成强烈对比，胸/裤细分节偏碎；星头很宽，是主体比例被装饰压过的反例。不按头上每根星刺计设计，也不从名字推断获取阶段。')
    add('mixed_glass_edge_armor', 'glass_armor:glass', '四件用浅蓝白硬边及大透明内面表达玻璃，裤两条长边与靴筒仍沿MC基础。浅边是主体，不能当白框背景删；透明材质应保留可读边界，不能为填满甲面而失去材料。')
    add('mixed_copper_classical_helm', 'iceandfire:armor_copper_metal', '棕铜面甲配深蓝短缨、短胸和蓝布裤/铜胫片；金属和织物分区比全铜换色有身份。保留鼻/面甲结构，不因封面脸口小便删掉铜片，缨不放大抢主体。')
    add('advanced_netherite_accent_variants', 'illagerinvasion:platinum_infused_netherite', '暗灰底甲配青白胸带、帽角和靴尖，补读裤膝后见同套局部包边，保守追加已有下界合金强调色组；同一亮带换材质不新算完整设计。', True)
    add('mixed_maid_clothing_apron', 'lethality:battle_maid', '黑短裙与浅紫白围裙、黑鞋/浅鞋口和拱形头巾都是布区，补全三图后才观察套装。只借鉴明暗主次，胸图V形白领不是金属胸甲，也不把黑裙改成整身盔甲人像。')
    add('mixed_agility_single_boot_family', 'lost_aether_content:agility', '两版本亮绿靴筒配灰白靴口/侧片，主体都是同对L靴，保守一个足部局部学习族。版本差异不多计，绿面过亮仅作配色反例，不当成已验速度效果。')
    add('virentium_gold_green_plate', 'savage_and_ravage:griefer', '绿主面与金边/金腰的四件追加已有金绿板甲学习组；补读头裤靴后可见金边只占结构带，不能用满幅金纹冒充神圣感。尖头/肩外伸不照搬为所有高级甲。', True)
    add('mixed_pykrete_cold_plate_straps', 'ulterlands:pykrete', '浅蓝帽面/肩胫配棕连接条，冷材料与棕绑带分离；裤膝蓝带连接棕直腿。可学材料在四部件中重复的位置，避免把棕条画成满面细网或把浅蓝当纯白背景。')
    p = json.loads((D / 'provenance.json').read_text())
    flat = [c for row in rows for c in row['cases']]
    assert len(flat) == len(set(flat)) == 28 and set(flat) == {c['case_key'] for c in p['cases']}
    review = {'reviewed_at': datetime.now(timezone.utc).isoformat(),
              'pages_opened': [f'icons-{i:02}.png' for i in range(1, 5)] + ['completion-01.png', 'completion-02.png'],
              'observations': rows, 'name_families_viewed': 28, 'native_icon_png_viewed': 93,
              'same_family_parts_added': 23, 'new_conservative_learning_groups': 14, 'append_to_existing_groups': 6,
              'new_artwork': 0, 'production_changes': 0, 'gate_met': False,
              'limits': '单件、反例、材料变体和版本仍在学习表；182学习组并非182套已验完整独立设计。原生图标不是身体绑定/穿戴/实机验收。'}
    (D / 'semantic-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
    print('D11: 28 names / 93 icons / 14 conservative learning groups')


if __name__ == '__main__':
    main()

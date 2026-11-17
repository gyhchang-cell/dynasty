"""Manual visual observations after opening all five native-icon contact pages."""
from datetime import datetime, timezone
from pathlib import Path
import json

D = Path(__file__).resolve().parent


def main():
    rows = []

    def add(group, namespace, cases, observation, prior=None):
        rows.append({'semantic_group': group, 'cases': [namespace + ':' + c for c in cases.split()],
                     'observation': observation,
                     'credit': 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' if prior else 'NEW_CONSERVATIVE_LEARNING_GROUP',
                     **({'prior_group': prior} if prior else {})})

    ns = 'eternal_starlight'
    add('aethersent_cowl_boots', ns, 'aethersent', '只见紫色兜帽与双靴，帽口暗负空间和两侧粗亮面建立布质身份；不虚构胸裤。两部位只算一个设计学习组，不将光泽拉成光滑渐变。')
    add('air_sac_dark_boots', ns, 'air_sac', '来源确是air_sac_boots物品图，而非单独气囊原料；深色长靴两侧少量绿色、黄色鞋头，负空间分开双腿。仅一对靴，不假称完整套装。')
    add('amaramber_cropped_vest', ns, 'amaramber', '仅黑紫短胸甲，领口是明显V形透明区，灰紫材料块围绕短躯干，不是细腰人台。与其他同色装备不能因紫色相同就说像素一致。')
    add('deepsilver_compact_center_plate', ns, 'deepsilver', '四部位：白银亮正面、蓝紫窄侧，胸中央长片与领口负空间明确；裤图是腰带加两块膝件，不是普通整条裤轮廓。借鉴部位省略的节奏，不能在项目中无条件照搬。')
    add('starlight_crystal_plate_variants', ns, 'glacite starlit_diamond', '冰蓝与紫白甲都以突出双肩、V形胸片、直腿短靴为基础；头部一套横眼口一套中央口，细节不同仍保守合并同族。中心亮块有硬台阶，避免把亮紫或浅蓝铺满甲体。')
    add('thermal_springstone_dark_fire_band', ns, 'thermal_springstone', '黑红底甲靠胸部一条橙黄横带和少量头肩热色形成材料；靴大面维持暗色。它是板片/热缝语言，不能误读成把整件涂成火焰。')
    add('unrealium_dark_purple_insets', ns, 'unrealium', '深黑主体配几处饱和紫嵌片，头盔口与靴暗部留足；胸片外沿短宽不画细腰。局部发亮纹仅从图标观察，不据此声称游戏里具有发光渲染。')
    ns = 'jerotesvillage'
    add('ancient_second_rounder_shared_kit', ns, 'ancient_second_rounder ancient_second_rounder_heavy ancient_second_rounder_noble', '普通、重型、贵族版共享青灰胸肩和暗裤基底；重型增加分片，贵族青色额部与交织胸片更亮。按同一套装进阶变体合并，不按版本或四部位计数。过碎交织仅作谨慎反例。')
    add('vanilla_outline_elemental_palette', ns, 'animated_iron', '银灰四件仍属原版帽口、短胸、直裤与L靴基础轮廓，胸前有斜亮片但不足据此新增一个独立设计组；并入已读基础材料甲组。', 'vanilla_outline_elemental_palette')
    add('jerote_warm_lamellar_variants', ns, 'carved_leader villager_metal', '两套棕红金分节胸、深裤与灰边帽共享暖色分片方向，头件装饰各异仍保守同组。胸中心大红/金面、周边棕暗条比全身均匀噪点更能读出材料。')
    add('explorer_straps_iron_variant', ns, 'explorer explorer_iron', '普通探索装是棕底交叉浅绑带，铁版只留下两列灰胸扣与白护腿；帽和鞋仍同类。两版合并学习组；轻装允许透明胸中区，不能因为不满整块而自动补色。')
    add('jerote_radiant_warm_plate_family', ns, 'fire_apostle serpon serpon_powerhouse', '橙红火使徒与金色Serpon/强力版共享开口胸肩和明亮中胸，强力版多一块红心片；保守合并，不拿冷热色或升级计三套。普通Serpon裤图一大片金色，细节不足是反例；保留短宽原版比例是可取部分。')
    add('giant_monster_visor_horn_variants', ns, 'giant_monster giant_monster_horned horned', '巨怪灰铁主体分成竖胸板和腰横条，头件有无棕色角及另一灰色有口头盔；后两项只出现头件。保守并入同类灰盔/角盔学习组，未证明三套独立设计。面口暗区是局部，不等同必须完全露脸。')
    add('magicka_scale_bright_abdomen', ns, 'magicka_scale', '深紫甲以青色下胸大亮片和少量橙侧扣区分；帽横眼缝较简单。细鳞点与极高饱和度仅是对比，不采用整套细棋盘纹来制造精致感。')
    add('meror_red_kit_variants', ns, 'meror_bounty_hunter meror_metal meror_standard', '三套粉红/红甲共享短胸双肩及矮面甲，赏金版竖带、金属版横片、标准版整块亮胸不同，但保守按材料套件变体同组。白亮肩与红暗侧的块面比中间碎粉点更有用。')
    add('mountain_realm_grid_lamellar', ns, 'mountain_realm', '暗红边、橙金网格胸片、上金下暗的头壳，直裤也有粗格。观察有节奏的甲片行列，不复制均匀噪点；靴外轮廓依然原版短L脚。')
    add('qoaiku_open_band_armor', ns, 'qoaiku', '青绿胸有横向断开的负空间、裤仅腰带与膝块；头件中央亮蓝与宽两侧分区。避免把所有空区填成大绿块；不能据二维图标推断实际穿戴UV。')
    add('jerote_brown_hunter_leather_variants', ns, 'rambler_leather wilderness_hunter', '两套棕皮装用暗衣底、粗横绑带/肩面与短靴形成轻甲，兜帽裤腿略异，保守合并。棕色大面适合原版感，但太暗的小高光不值得逐点增加。')
    add('scaly_bear_gold_hide_plate', ns, 'scaly_bear', '金黄甲的圆钝帽面、短胸大中央片与暗腰有识别度，直裤与双靴保持简单。圆钝靠像素阶梯而非平滑曲线；图标中的细鳞状亮点不建议照搬。')
    add('serpon_wizard_sparse_cloth', ns, 'serpon_wizard', '灰白袍胸外沿V形、腰边横条，裤为整块灰色，头仅三粒浅点、鞋为横条；记录为刻意极少形状的版本，不将三粒点误说成完整面甲。其头鞋过于简陋只作反例。')
    add('slavery_supervisor_black_gold_straps', ns, 'slavery_supervisor', '黑底甲以金胸横带与中竖线构成清楚的绑带/扣件，帽竖金条与裤腰对应。金块面积克制，暗区仍可读四肢；短胸短靴不因职业身份变成人台比例。')
    add('spirve_threadbare_cloth', ns, 'spirve', '棕灰短上衣两侧粗边、中间深口；矮帽、短裤与细小鞋。小部位接近背景是反例，重做时应扩大有效轮廓而不是把整张原稿缩小。只记录原始图，不在此改图。')
    add('wilderness_giant_diagonal_harness', ns, 'wilderness_giant', '胸只见棕色单斜带加腰带，头裤也为带状，鞋很小；与探索者X交叉绑带不同，单独记录。负空间表达轻装身份可取，但过小脚部不宜照搬为项目最终图标。')
    prov = json.loads((D / 'provenance.json').read_text())
    flat = [c for row in rows for c in row['cases']]
    assert len(flat) == len(set(flat)) == 35
    assert set(flat) == {c['case_key'] for c in prov['cases']}
    new_count = sum(row['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP' for row in rows)
    result = {
        'reviewed_at': datetime.now(timezone.utc).isoformat(),
        'pages_opened': [f'icons-{n:02d}.png' for n in range(1, 6)],
        'observations': rows, 'icon_name_families': 35, 'original_icon_png': 126,
        'new_conservative_learning_groups': new_count, 'append_to_existing_groups': 1,
        'prior_learning_groups_reused': 82, 'combined_conservative_learning_groups': 82 + new_count,
        'combined_name_families': 227, 'new_artwork': 0, 'production_changes': 0, 'gate_met': False,
        'limits': '126 PNG不是126套；35名称不是35独立设计。仅原始图标阅读，不推断穿戴绑定、发光材质或游戏效果。完整1000真实独立相关设计门槛未达到。',
    }
    (D / 'semantic-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['icon_name_families', 'original_icon_png', 'new_conservative_learning_groups', 'combined_conservative_learning_groups']}, ensure_ascii=False))


if __name__ == '__main__':
    main()

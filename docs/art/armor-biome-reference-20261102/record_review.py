"""Manual semantic notes after inspecting all six completed-family icon pages."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import zipfile

D = Path(__file__).resolve().parent


def main():
    rows = []

    def add(group, cases, note, prior=False):
        rows.append({'semantic_group': group, 'cases': cases.split(), 'observation': note,
                     'credit': 'APPEND_TO_PRIOR_GROUP_ZERO_NEW_DESIGNS' if prior else 'NEW_CONSERVATIVE_LEARNING_GROUP',
                     **({'prior_group': group} if prior else {})})

    add('biome_closed_diving_equipment', 'alexscaves:diving hybrid-aquatic:diving', '铜红四件潜水甲与Hybrid三件潜水装备都以封闭观察窗头壳、窄直裤/靴表达密封用途，保守同一专用潜水装备学习组。一个为金属铜圈，一个为浅亮视窗，未证明同款；不将圆视窗套到普通人类盔甲。')
    add('gingerbread_sugar_cloth_armor', 'alexscaves:gingerbread', '姜饼棕底、白糖块与红纽扣四件统一，糖霜白属于主体，不能当白底擦掉。帽檐和肩饰是节庆用途的例外，不照搬到鸿蒙金甲；离散色块的材料对应值得学习。')
    add('hazmat_yellow_dark_suit', 'alexscaves:hazmat', '黄防护衣胸分成三条大亮面，黑靴黑手套与黄色裤体形成用途对比；当前同名只见三件，面罩若用另一ID不能凭空补进来。长衣也保持短宽物品图标比例。')
    add('primordial_bone_cap_single', 'alexscaves:primordial', '仅骨色头件，灰骨大块、褐边与短角构成原始材料，刻意不对称。单件参考，不算整套，也不把每根骨刺独立计数。')
    add('creature_mobility_boots_conservative', 'alexscaves:rainbounce alexsmobs:roadrunner alexsmobs:flying_fish', '黄雨靴、棕蓝羽靴、蓝翼靴的用途靠鞋头/脚踝附件区别，按单靴功能型学习组保守合并。它们不是同像素或已证同系列；只借鉴有效双靴尺寸、负空间与少量附件，不作三套完整盔甲信用。')
    add('creature_hide_shell_vests', 'alexsmobs:crocodile alexsmobs:rocky', '鳄皮两版本棕绿鳞格与骨石胸壳有材料区别，均围绕短胸、浅领口、粗边组织；版本不另计，单件归一保守材料胸甲学习组。细密同频鳞点可作反例，避免铺满噪点。')
    add('blue_creature_cap_horn_family', 'alexsmobs:froststalker alexsmobs:straddle', '冰蓝短壳配深角与蓝灰低帽口分别提供生物材料身份；都是单头件，保守一个头件结构组，不能想象配套衣裤。黑角/浅壳对比比加满碎亮点有用。')
    add('betterend_aeternium_horned_plate', 'betterend:aeternium', '青黑四件以短侧角头盔、粗银青胸片和黑连接形成身份，靴依然短直。中后期变化集中在头顶与分片，胸腰大比例保持原版；不能把短角无限拉长。')
    add('betterend_crystalite_asymmetric_materials', 'betterend:crystalite', '青紫晶体左右材质不对称，四部位重复少数青/紫嵌块和黑底，有明确套装对应。身份清楚但色跳强，可用作多材料关系参考，不套成朱砂的杂色装甲。')
    add('vanilla_outline_elemental_palette', 'alexsmobs:centipede alexsmobs:emu betterend:terminite betterend:thallasium betternether:cincinnasite betternether:flaming_ruby betternether:nether_ruby deep_aether:skyjade', '两条材料裤、青白/浅蓝金属、金色与红宝石/火红宝石、青绿玉甲仍以原版基础轮廓组织，材料与明暗有变化，合并既有基础甲组。特别两种红宝石不能因颜色/火焰名字重复增加设计数。', True)
    add('aether_valkyrie_white_gold_crown', 'deep_aether:stormforged terramity:reverium', '风暴锻造的青白翼冠/翼靴与Reverium的浅蓝白金四件，都作为既有浅色高阶板甲分工的补充，保守不新增组。风暴与Reverium不是白金Valkyrie的同像素版本，归并仅为克制计数。圆桶头盔与大外角不按项目普通MC甲比例直接照搬。', True)
    add('aquatic_shell_single_equipment', 'hybrid-aquatic:nautilus hybrid-aquatic:turtle', '螺壳头罩与龟壳胸甲都以浅壳带、绿/棕边说明硬壳用途，保守归一个单件防护壳学习组；胸壳近圆盘，不适合作普通板甲的胸腰比例模板。只取硬壳色区，不复制图案。')
    add('malum_purple_cosmetic_plate_family', 'malum:ancient_soul_stained_steel malum:executioner malum:malignant_stronghold', '原索引缺部件，已从同一固定JAR补齐古灵钢四件、刽子手三件与恶性堡垒四件。前两者路径在cosmetic/armor_icons，不能从名字编造独立注册ID；保守紫色装甲族一组。金胸与紫腿、浅肩和暗连接有分工，胸上轮廓可作像素材料案例，不做三套新设计信用。')
    add('souls_chaos_branch_crown', 'soulsweapons:chaos', '只有黑底青色分枝冠头件，中央/侧枝形成粗阶梯，暗底保留头壳读形。单头件图形，不推断游戏骨骼、发光或全身套装。')
    add('souls_gray_plate_shared_family', 'soulsweapons:forlorn soulsweapons:soul_ingot', '暗灰板甲两套的领口、腰带与靴近似原版，Forlorn有棕斜胸带与红帽衬，Soul Ingot为均匀分节；保守同类灰板甲组。不同像素并不抹去，但不为多计设计强行拆分。')
    add('souls_teal_edged_long_robe', 'soulsweapons:soul_robes', '深灰四件以青色纵领边、腰边和靴口联系，袍胸保留长直衣缘、裤体也有竖边。条带不必满整身，图标与穿戴需分别验；不能因为长袍就将layer2所有躯干无条件填实。')
    add('conductite_copper_dark_panels', 'terramity:conductite', '同名补成胸、裤、靴三件。棕铜胸上有成块铆接/连接结构，下配黑裤；材料分工比把裤也涂满铜色更清楚。独立头件若另名未读，不猜测补齐。')
    add('terramity_dark_red_blue_plate_variants', 'terramity:exodium terramity:nyxium', '紫红胸配灰肩与蓝紫胸配红臂/红裤均沿同一紧凑分件方向，保守一个学习组。套装内异色要有材料角色，不能把颜色多当成高级或加细碎高光。')
    add('hellspec_black_red_coat', 'terramity:hellspec', '黑红开襟胸、黑靴黑裤只在上腿/胸有红布分区，三件对应清晰。用红黑大面表达衣甲，不把每一边都描亮；未见同名头件，不称全套完成。')
    add('virentium_gold_green_plate', 'terramity:virentium', '绿色板甲配黄肩/腰和棕靴，头件紫点位于中央，四件有一致主次。胸的尖肩和高饱和度是谨慎反例；低分辨率材质可读，不代表这种外挑肩适合本项目。')
    add('void_purple_inset_plate', 'terramity:void', '黑底银框、紫色袖带/靴带、直裤在三件里呼应，中心纵胸片不依赖圆环。补齐同名三件仅增加资料，不增加设计数；头件未收录不虚构。')
    prov = json.loads((D / 'provenance.json').read_text())
    bird = next(c for c in prov['cases'] if c['case_key'] == 'alexsmobs:falconry')
    with zipfile.ZipFile(bird['icons'][0]['jar']) as z:
        entry = 'assets/alexsmobs/lang/en_us.json'; data = z.read(entry); lang = json.loads(data)
        key = 'advancements.alexsmobs.falconry_hood.desc'
        assert 'Eagles wearing one' in lang[key]
        purpose = {'jar': bird['icons'][0]['jar'], 'entry': entry, 'sha256': hashlib.sha256(data).hexdigest(), 'inspected_key': key,
                   'conclusion': '原生说明明确是鹰佩戴并用于操控，排除出玩家盔甲参考。'}
    excluded = [{'case_key': 'alexsmobs:falconry', 'reason': '鹰佩戴的头罩，不是玩家穿戴盔甲。', 'source': purpose}]
    flat = [c for row in rows for c in row['cases']]
    assert len(flat) == len(set(flat)) == 39
    assert set(flat) | {e['case_key'] for e in excluded} == {c['case_key'] for c in prov['cases']}
    new = sum(r['credit'] == 'NEW_CONSERVATIVE_LEARNING_GROUP' for r in rows)
    assert new == 19
    record = {'reviewed_at': datetime.now(timezone.utc).isoformat(), 'pages_opened': [f'icons-{i:02}.png' for i in range(1, 7)],
              'observations': rows, 'excluded_cases': excluded, 'original_index_png': 90, 'same_family_added_png': 22,
              'native_icon_png_viewed': 112, 'reviewed_name_families': 40, 'armor_name_families_after_exclusion': 39,
              'new_conservative_learning_groups': 19, 'append_to_existing_groups': 2,
              'combined_reviewed_name_families': 304, 'combined_armor_name_families': 303,
              'combined_conservative_learning_groups': 136, 'gate_met': False, 'new_artwork': 0, 'production_changes': 0,
              'limits': '19新增学习组中有单件/缺部位/化妆版本，不能据此增加19套完整独立设计验收信用；112 PNG也不等于112设计。'}
    (D / 'semantic-review.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['native_icon_png_viewed', 'reviewed_name_families', 'armor_name_families_after_exclusion', 'new_conservative_learning_groups', 'combined_conservative_learning_groups']}, ensure_ascii=False))


if __name__ == '__main__':
    main()

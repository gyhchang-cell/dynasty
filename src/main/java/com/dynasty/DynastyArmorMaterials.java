package com.dynasty;

import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;

/**
 * Dynasty 盔甲材质：玉甲 / 龙鳞甲 / 将军铠。
 * Armor materials: Jade / Dragon Scale / General.
 */
@SuppressWarnings("null")
public final class DynastyArmorMaterials {

    private DynastyArmorMaterials() {
    }

    private static ArmorMaterial make(String name, int[] durability, int[] defense, int ench,
                                      float toughness, float knockback, int useMultiplier,
                                      java.util.function.Supplier<net.minecraft.world.item.Item> repair) {
        return new ArmorMaterial() {
            @Override
            public int getDurabilityForType(ArmorItem.Type type) {
                return durability[type.getSlot().getIndex()] * useMultiplier;
            }

            @Override
            public int getDefenseForType(ArmorItem.Type type) {
                return switch (type) {
                    case HELMET -> defense[0];
                    case CHESTPLATE -> defense[1];
                    case LEGGINGS -> defense[2];
                    case BOOTS -> defense[3];
                    default -> 0;
                };
            }

            @Override
            public int getEnchantmentValue() {
                return ench;
            }

            @Override
            public SoundEvent getEquipSound() {
                return SoundEvents.ARMOR_EQUIP_DIAMOND;
            }

            @Override
            public Ingredient getRepairIngredient() {
                return Ingredient.of(repair.get());
            }

            @Override
            public String getName() {
                return "dynasty:" + name;
            }

            @Override
            public float getToughness() {
                return toughness;
            }

            @Override
            public float getKnockbackResistance() {
                return knockback;
            }
        };
    }

    /**
     * 布衣：开局最基础的护甲，丝绸制成，减伤 12%（整套）/ Cloth: the starting set, made of silk.
     */
    public static final ArmorMaterial CLOTH =
            make("cloth", new int[]{5, 6, 7, 4}, new int[]{2, 4, 3, 1}, 15, 0.0F, 0.0F, 15,
                    () -> DynastyFineItems.SILK.get());

    /**
     * 将军铠：青铜重甲，减伤 64%（整套）/ General: bronze heavy armour.
     */
    public static final ArmorMaterial GENERAL =
            make("general", new int[]{13, 15, 16, 11}, new int[]{6, 9, 7, 5}, 20, 12.0F, 0.3F, 450,
                    () -> DynastyItems.BRONZE_INGOT.get());

    /**
     * 玉甲：轻盈、附魔强，减伤 80%（整套）/ Jade: light, highly enchantable.
     */
    public static final ArmorMaterial JADE =
            make("jade", new int[]{13, 15, 16, 11}, new int[]{10, 14, 12, 8}, 32, 16.0F, 0.4F, 400,
                    () -> DynastyItems.JADE.get());

    /**
     * 龙鳞甲：防御极高，减伤 96%（整套）/ Dragon Scale: best defence before the endgame set.
     */
    public static final ArmorMaterial DRAGON_SCALE =
            make("dragon_scale", new int[]{13, 15, 16, 11}, new int[]{14, 19, 16, 11}, 26, 20.0F, 0.6F, 600,
                    () -> DynastyItems.DRAGON_SCALE.get());

    /**
     * 玄天真龙甲：终盘套装（需龙帝玉玺），减伤 92% 血上限 +1520。
     * Xuantian True Dragon set: endgame armour gated behind the Dragon Emperor's seal.
     */
    public static final ArmorMaterial XUANTIAN =
            make("xuantian", new int[]{18, 22, 24, 16}, new int[]{18, 24, 20, 14}, 40, 25.0F, 0.8F, 900,
                    () -> DynastyItems.DRAGON_CRYSTAL.get());

    /**
     * 鲛绡甲：龙鳞套之上，水战向轻甲（可在龙宫材料下继续升级）。
     * Sea Silk: light armour above Dragon Scale, themed for the Dragon Palace.
     */
    public static final ArmorMaterial SEA_SILK =
            make("sea_silk", new int[]{15, 17, 18, 13}, new int[]{16, 21, 18, 13}, 36, 22.0F, 0.7F, 760,
                    () -> DynastyItems.DRAGON_SCALE.get());

    /**
     * 玄铁重铠：终盘重甲，护甲最高、抗击退最强。
     * Dark Iron: the heaviest set with the best armour and knockback resistance.
     */
    public static final ArmorMaterial DARK_IRON =
            make("dark_iron", new int[]{20, 24, 26, 18}, new int[]{22, 28, 24, 17}, 42, 27.0F, 0.9F, 1100,
                    () -> DynastyRelics.REFINED_STEEL.get());

    // ------------------------------------------------------------------
    // 第二十轮扩充：10 套新盔甲（7 → 17 套）
    // 与 tools/art/gen_armor2.py 里的 SETS 表一一对应，改一边要改另一边。
    // Ten extra sets; keep this in sync with the SETS table in gen_armor2.py.
    // ------------------------------------------------------------------

    /** 竹甲：开局第二天就能做，比布衣稍硬 / Bamboo: the first cheap upgrade. */
    public static final ArmorMaterial BAMBOO =
            make("bamboo", new int[]{7, 9, 10, 6}, new int[]{3, 5, 4, 2}, 12, 0.0F, 0.1F, 60,
                    () -> net.minecraft.world.item.Items.BAMBOO);

    /** 皮甲：皮革套，抗击退开始显现 / Leather. */
    public static final ArmorMaterial LEATHER =
            make("leather", new int[]{9, 11, 12, 8}, new int[]{4, 6, 5, 3}, 15, 2.0F, 0.15F, 120,
                    () -> net.minecraft.world.item.Items.LEATHER);

    /** 织锦袍：丝绸与织锦织成的官服型轻甲 / Brocade robe. */
    public static final ArmorMaterial BROCADE =
            make("brocade", new int[]{11, 13, 14, 10}, new int[]{5, 7, 6, 4}, 24, 6.0F, 0.2F, 200,
                    () -> DynastyFineItems.BROCADE.get());

    /** 青铜甲：与将军铠同档的制式甲 / Bronze regulation armour. */
    public static final ArmorMaterial BRONZE =
            make("bronze", new int[]{12, 14, 15, 10}, new int[]{6, 8, 7, 5}, 18, 9.0F, 0.25F, 300,
                    () -> DynastyItems.BRONZE_INGOT.get());

    /** 白银铠：官银炼成的亮甲 / Silver. */
    public static final ArmorMaterial SILVER =
            make("silver", new int[]{13, 15, 16, 11}, new int[]{9, 12, 10, 7}, 30, 14.0F, 0.35F, 420,
                    () -> DynastyItems.SILVER_INGOT.get());

    /** 朱砂符甲：符纸与朱砂糊成的符甲，抗负面状态 / Cinnabar talisman armour. */
    public static final ArmorMaterial CINNABAR =
            make("cinnabar", new int[]{13, 15, 16, 11}, new int[]{11, 15, 13, 9}, 30, 16.0F, 0.4F, 500,
                    () -> DynastyItems.CINNABAR.get());

    /** 凤凰羽衣：轻甲，火里来火里去 / Phoenix feather robe. */
    public static final ArmorMaterial PHOENIX =
            make("phoenix", new int[]{14, 16, 17, 12}, new int[]{12, 16, 14, 9}, 34, 17.0F, 0.45F, 560,
                    () -> DynastyItems.PHOENIX_FEATHER.get());

    /** 麒麟鳞甲：龙鳞 + 麒麟角，祥瑞护体 / Qilin scale armour. */
    public static final ArmorMaterial QILIN =
            make("qilin", new int[]{16, 19, 20, 14}, new int[]{15, 20, 17, 12}, 34, 21.0F, 0.55F, 700,
                    () -> DynastyItems.QILIN_HORN.get());

    /** 天将云铠：九霄天将的云甲，减伤 116%（封顶 92%）/ Sky General armour. */
    public static final ArmorMaterial SKY =
            make("sky", new int[]{18, 21, 22, 15}, new int[]{18, 23, 20, 14}, 38, 24.0F, 0.7F, 880,
                    () -> DynastyItems.SKY_TOKEN.get());

    /** 龙王鳞铠：全模组最硬的一套，龙宫的终极报酬 / Dragon King armour — the toughest set. */
    public static final ArmorMaterial DRACO_KING =
            make("draco_king", new int[]{20, 24, 26, 18}, new int[]{21, 27, 23, 16}, 42, 28.0F, 0.9F, 1150,
                    () -> DynastyItems.SEA_TOKEN.get());

    // ------------------------------------------------------------------
    // 第三十一轮扩充：10 套「四象 / 星斗 / 道门」终盘甲（17 → 27 套）
    // 每件减伤 33% → 42%，每件生命 1100 → 3200；与 tools/art/gen_armor3.py 的
    // SETS 表、DynastyBalance.SET_BONUS、DynastyTooltips.setName 四处一一对应。
    // Ten endgame sets (four symbols / star dial / Daoist); keep all four tables in sync.
    // ------------------------------------------------------------------

    /** 玄武甲：极致防御，抗击退最高 / Xuanwu — pure defence. */
    public static final ArmorMaterial XUANWU =
            make("xuanwu", new int[]{22, 26, 28, 20}, new int[]{26, 34, 30, 22}, 44, 30.0F, 1.0F, 1300,
                    () -> DynastyItems.DRAGON_SCALE.get());

    /** 朱雀羽：抗火向轻甲 / Zhuque — fire resistant light armour. */
    public static final ArmorMaterial ZHUQUE =
            make("zhuque", new int[]{20, 23, 24, 17}, new int[]{24, 31, 27, 20}, 44, 29.0F, 0.95F, 1250,
                    () -> DynastyItems.PHOENIX_FEATHER.get());

    /** 青龙鳞：攻守兼备 / Qinglong — balanced offence. */
    public static final ArmorMaterial QINGLONG =
            make("qinglong", new int[]{22, 26, 28, 20}, new int[]{28, 36, 32, 23}, 46, 31.0F, 1.0F, 1350,
                    () -> DynastyItems.DRAGON_CRYSTAL.get());

    /** 白虎铠：攻击 +15% / Baihu — offence and knockback. */
    public static final ArmorMaterial BAIHU =
            make("baihu", new int[]{23, 27, 29, 21}, new int[]{30, 39, 34, 25}, 46, 32.0F, 1.0F, 1400,
                    () -> DynastyRelics.REFINED_STEEL.get());

    /** 北斗甲：星石与玄天玉铸成，移速 +8% / Beidou — mobility. */
    public static final ArmorMaterial BEIDOU =
            make("beidou", new int[]{24, 28, 30, 22}, new int[]{30, 39, 34, 25}, 48, 33.0F, 1.05F, 1500,
                    () -> DynastyRelics.XUANTIAN_JADE.get());

    /** 天罡甲：道门天罡星力 / Tiangang. */
    public static final ArmorMaterial TIANGANG =
            make("tiangang", new int[]{25, 29, 31, 23}, new int[]{32, 42, 37, 27}, 48, 34.0F, 1.1F, 1600,
                    () -> DynastyItems.DRAGON_CRYSTAL.get());

    /** 地煞甲：帝骸骨与精钢，护甲 +40 / Disha. */
    public static final ArmorMaterial DISHA =
            make("disha", new int[]{26, 30, 32, 24}, new int[]{34, 44, 39, 28}, 50, 35.0F, 1.15F, 1700,
                    () -> DynastyRelics.EMPEROR_BONE.get());

    /** 太乙甲：全属性小幅提升 / Taiyi. */
    public static final ArmorMaterial TAIYI =
            make("taiyi", new int[]{27, 31, 33, 25}, new int[]{35, 46, 40, 29}, 52, 36.0F, 1.2F, 1800,
                    () -> DynastyRelics.XUANTIAN_JADE.get());

    /** 紫微甲：帝星紫微，幸运 +3 / Ziwei. */
    public static final ArmorMaterial ZIWEI =
            make("ziwei", new int[]{28, 32, 34, 26}, new int[]{36, 47, 41, 30}, 52, 37.0F, 1.25F, 1900,
                    () -> DynastyRelics.DRAGON_EMPEROR_SEAL.get());

    /** 混元甲：毕业套（每件减伤 42%，四件封顶 92%）/ Hunyuan — the graduation set. */
    public static final ArmorMaterial HUNYUAN =
            make("hunyuan", new int[]{30, 34, 36, 28}, new int[]{38, 50, 44, 32}, 56, 40.0F, 1.35F, 2200,
                    () -> DynastyRelics.DRAGON_EMPEROR_SEAL.get());

    // ------------------------------------------------------------------
    // 第三十二轮：毕业甲「鸿蒙帝铠」—— 甲胄谱两条流派线的终点合体
    //   竹甲流终点（龙王鳞铠）+ 将军流终点（混元甲）逐件合成，混元之上为鸿蒙。
    // The capstone set: merges both armour ladders' final pieces.
    // ------------------------------------------------------------------

    /** 鸿蒙帝铠：全模组最终一套（每件减伤 45%，四件封顶 92%）/ Hongmeng Imperial Armor. */
    public static final ArmorMaterial HONGMENG =
            make("hongmeng", new int[]{32, 36, 38, 30}, new int[]{42, 54, 48, 35}, 60, 44.0F, 1.5F, 2600,
                    () -> DynastyRelics.DRAGON_EMPEROR_SEAL.get());
}

package com.dynasty;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.Map;

/**
 * 数值平衡表（2024 大数值版）：武器 1000–2048、护甲 53–71、套装减伤 60–80%、套装生命 +600~+1000。
 * 由于原版属性上限为 攻击力 2048 / 生命 1024，超过部分改用「伤害减免」实现，
 * 这样数字好看、又不会因为几千颗心而掉帧。
 *
 * Balance table: weapons 1000-2048 damage, armor 53-71, set damage reduction 60-80%,
 * set bonus health +600 ~ +1000. Values beyond the vanilla caps (attack 2048 / health 1024)
 * are expressed as damage reduction so the HUD stays cheap to render.
 */
public final class DynastyBalance {

    private DynastyBalance() {
    }

    /** 原版攻击力属性上限 / vanilla ATTACK_DAMAGE cap */
    public static final double MAX_ATTACK_DAMAGE = 2048.0D;
    /** 原版最大生命属性上限 / vanilla MAX_HEALTH cap */
    public static final double MAX_HEALTH = 1024.0D;

    private static final Map<String, double[]> SET_BONUS = new HashMap<>();
    private static final Map<String, Double> MOB_TOUGHNESS = new HashMap<>();
    /** 名器「特攻」：命中时额外结算的固定伤害 / flat extra damage beyond the attribute cap */
    private static final Map<String, Double> WEAPON_BONUS = new HashMap<>();

    static {
        // 名器特攻（原版 ATTACK_DAMAGE 上限 2048，超出的部分走这里，所以在战斗里依然能打得更重）
        // Named weapons deal flat extra damage on hit, past the vanilla 2048 attribute cap.
        WEAPON_BONUS.put("sword_dragon_crystal", 150.0D);
        WEAPON_BONUS.put("yitian_sword", 90.0D);
        WEAPON_BONUS.put("qinggang_sword", 70.0D);
        WEAPON_BONUS.put("gilded_mace", 100.0D);
        WEAPON_BONUS.put("dragon_spear", 120.0D);
        WEAPON_BONUS.put("pojun_axe", 120.0D);
        WEAPON_BONUS.put("seven_star_saber", 220.0D);
        WEAPON_BONUS.put("halberd_fangtian", 250.0D);
        WEAPON_BONUS.put("sea_trident", 300.0D);
        WEAPON_BONUS.put("xuantian_axe", 300.0D);
        WEAPON_BONUS.put("dragon_slayer", 350.0D);
        WEAPON_BONUS.put("supreme_sword", 400.0D);
        WEAPON_BONUS.put("tianzi_sword", 500.0D);
        WEAPON_BONUS.put("sunbow", 200.0D);
        WEAPON_BONUS.put("tianlang_bow", 150.0D);
        WEAPON_BONUS.put("longyuan_sword", 200D);
        WEAPON_BONUS.put("juling_axe", 300D);
        WEAPON_BONUS.put("qinglong_dao", 350D);
        WEAPON_BONUS.put("bawang_spear", 400D);
        WEAPON_BONUS.put("houyi_bow", 250D);
        WEAPON_BONUS.put("leiting_hammer", 450D);
        WEAPON_BONUS.put("taiyi_whisk", 500D);
        // 第三十二轮的 6 把帝兵 / the six imperial weapons of round 32
        WEAPON_BONUS.put("qilin_war_axe", 250D);
        WEAPON_BONUS.put("taiyi_sword", 300D);
        WEAPON_BONUS.put("baihu_glaive", 330D);
        WEAPON_BONUS.put("thunder_spear", 360D);
        WEAPON_BONUS.put("ziwei_saber", 400D);
        WEAPON_BONUS.put("zhuque_bow", 300D);
        WEAPON_BONUS.put("xuanwu_blade", 550D);
        WEAPON_BONUS.put("zhuque_fan", 600D);
        WEAPON_BONUS.put("hunyuan_staff", 800D);
    }

    static {
        // 每件装备：{每件减伤, 每件生命加成, 头/胸/腿/靴 护甲值}
        // per piece: {damage reduction, bonus health, helmet/chest/legs/boots armour}
        SET_BONUS.put("cloth", new double[]{0.03D, 30.0D, 2.0D, 4.0D, 3.0D, 1.0D});
        SET_BONUS.put("general", new double[]{0.16D, 150.0D, 6.0D, 9.0D, 7.0D, 5.0D});
        SET_BONUS.put("jade", new double[]{0.21D, 260.0D, 12.0D, 17.0D, 14.0D, 10.0D});
        SET_BONUS.put("dragon_scale", new double[]{0.25D, 380.0D, 17.0D, 23.0D, 19.0D, 13.0D});
        SET_BONUS.put("xuantian", new double[]{0.30D, 620.0D, 26.0D, 34.0D, 30.0D, 22.0D});
        SET_BONUS.put("sea_silk", new double[]{0.28D, 640.0D, 24.0D, 31.0D, 27.0D, 20.0D});
        SET_BONUS.put("dark_iron", new double[]{0.33D, 900.0D, 34.0D, 44.0D, 39.0D, 28.0D});

        // 第二十轮扩充：10 套新盔甲（与 DynastyArmorMaterials 一一对应）
        // ten extra sets — keep in sync with DynastyArmorMaterials
        SET_BONUS.put("bamboo", new double[]{0.05D, 45.0D, 3.0D, 5.0D, 4.0D, 2.0D});
        SET_BONUS.put("leather", new double[]{0.07D, 60.0D, 4.0D, 6.0D, 5.0D, 3.0D});
        SET_BONUS.put("brocade", new double[]{0.09D, 80.0D, 5.0D, 7.0D, 6.0D, 4.0D});
        SET_BONUS.put("bronze", new double[]{0.12D, 110.0D, 6.0D, 8.0D, 7.0D, 5.0D});
        SET_BONUS.put("silver", new double[]{0.18D, 190.0D, 9.0D, 12.0D, 10.0D, 7.0D});
        SET_BONUS.put("cinnabar", new double[]{0.22D, 320.0D, 14.0D, 18.0D, 16.0D, 11.0D});
        SET_BONUS.put("phoenix", new double[]{0.23D, 430.0D, 15.0D, 20.0D, 18.0D, 13.0D});
        SET_BONUS.put("qilin", new double[]{0.27D, 700.0D, 24.0D, 31.0D, 27.0D, 20.0D});
        SET_BONUS.put("sky", new double[]{0.32D, 1000.0D, 34.0D, 44.0D, 39.0D, 28.0D});
        SET_BONUS.put("draco_king", new double[]{0.35D, 1400.0D, 44.0D, 57.0D, 50.0D, 36.0D});
        // 第三十一轮：10 套终盘甲（每件减伤 33% → 42%，生命 1100 → 3200）
        SET_BONUS.put("xuanwu", new double[]{0.33D, 1100.0D, 26.0D, 34.0D, 30.0D, 22.0D});
        SET_BONUS.put("zhuque", new double[]{0.30D, 1000.0D, 24.0D, 31.0D, 27.0D, 20.0D});
        SET_BONUS.put("qinglong", new double[]{0.34D, 1200.0D, 28.0D, 36.0D, 32.0D, 23.0D});
        SET_BONUS.put("baihu", new double[]{0.35D, 1300.0D, 30.0D, 39.0D, 34.0D, 25.0D});
        SET_BONUS.put("beidou", new double[]{0.36D, 1500.0D, 30.0D, 39.0D, 34.0D, 25.0D});
        SET_BONUS.put("tiangang", new double[]{0.37D, 1700.0D, 32.0D, 42.0D, 37.0D, 27.0D});
        SET_BONUS.put("disha", new double[]{0.38D, 1900.0D, 34.0D, 44.0D, 39.0D, 28.0D});
        SET_BONUS.put("taiyi", new double[]{0.39D, 2200.0D, 35.0D, 46.0D, 40.0D, 29.0D});
        SET_BONUS.put("ziwei", new double[]{0.40D, 2600.0D, 36.0D, 47.0D, 41.0D, 30.0D});
        SET_BONUS.put("hunyuan", new double[]{0.42D, 3200.0D, 38.0D, 50.0D, 44.0D, 32.0D});
        // 第三十二轮：毕业甲「鸿蒙帝铠」（甲胄谱两条流派线的终点合体）
        SET_BONUS.put("hongmeng", new double[]{0.45D, 3600.0D, 42.0D, 54.0D, 48.0D, 35.0D});

        // 敌方减伤：小怪几乎没有减伤（早期武器也打得动），Boss 依然厚
        // enemy damage reduction: trash mobs have almost none (so early weapons work), bosses stay tanky
        MOB_TOUGHNESS.put("dragon_emperor", 0.86D);
        MOB_TOUGHNESS.put("undead_first_emperor", 0.84D);
        MOB_TOUGHNESS.put("rebel_general", 0.78D);
        MOB_TOUGHNESS.put("eunuch_mastermind", 0.78D);
        MOB_TOUGHNESS.put("nian_beast", 0.45D);
        MOB_TOUGHNESS.put("qilin", 0.40D);
        MOB_TOUGHNESS.put("phoenix", 0.50D);
        MOB_TOUGHNESS.put("nine_tailed_fox", 0.50D);
        MOB_TOUGHNESS.put("royal_guard", 0.25D);
        MOB_TOUGHNESS.put("assassin", 0.15D);
        MOB_TOUGHNESS.put("imperial_soldier", 0.05D);
        MOB_TOUGHNESS.put("rebel_soldier", 0.05D);
        MOB_TOUGHNESS.put("terracotta_warrior", 0.10D);
        MOB_TOUGHNESS.put("archer", 0.10D);
        MOB_TOUGHNESS.put("minister", 0.0D);
    }

    /** 名器的「特攻」固定加伤（没有就是 0）/ flat extra damage for named weapons */
    public static double weaponBonus(String itemId) {
        if (itemId == null) {
            return 0.0D;
        }
        Double bonus = WEAPON_BONUS.get(itemId);
        return bonus == null ? 0.0D : bonus;
    }

    /** 装备名（如 jade / general / dragon_scale）-> 套装加成 */
    public static double[] setNameBonus(String itemId) {
        if (itemId == null || !isArmorPiece(itemId)) {
            return null;                 // 兵器/饰品的名字可能撞前缀（xuanwu_blade / taiyi_whisk），这里挡掉
        }
        for (Map.Entry<String, double[]> entry : SET_BONUS.entrySet()) {
            if (itemId.startsWith(entry.getKey())) {
                return entry.getValue();
            }
        }
        return null;
    }

    /** 只看盔甲四个部位的后缀 / only the four armour slots count as set pieces */
    private static boolean isArmorPiece(String itemId) {
        return itemId.endsWith("_helmet") || itemId.endsWith("_chestplate")
                || itemId.endsWith("_leggings") || itemId.endsWith("_boots");
    }

    public static boolean isDynastyArmor(String itemId) {
        return setNameBonus(itemId) != null;
    }

    /** 穿戴整套时总减伤：玉甲 60% / 将军铠 72% / 龙鳞甲 80% */
    public static float setDamageReduction(java.util.List<String> wornIds) {
        float reduction = 0.0F;
        for (String id : wornIds) {
            double[] bonus = setNameBonus(id);
            if (bonus != null) {
                reduction += (float) bonus[0];
            }
        }
        return Math.min(0.90F, reduction);
    }

    /** 穿戴整套时的生命加成（原版上限 1024 之内） */
    public static double setHealthBonus(java.util.List<String> wornIds) {
        double bonus = 0.0D;
        for (String id : wornIds) {
            double[] b = setNameBonus(id);
            if (b != null) {
                bonus += b[1];
            }
        }
        return bonus;
    }

    public static double armorPoints(java.util.List<String> wornIds) {
        double armor = 0.0D;
        for (String id : wornIds) {
            double[] b = setNameBonus(id);
            if (b != null) {
                armor += id.contains("helmet") ? b[2] : id.contains("chestplate") ? b[3]
                        : id.contains("leggings") ? b[4] : b[5];
            }
        }
        return armor;
    }

    /** 敌方单位伤害减免 / damage reduction of dynasty mobs */
    public static double mobToughness(EntityType<?> type) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(type);
        if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
            return 0.0D;
        }
        return MOB_TOUGHNESS.getOrDefault(id.getPath(), 0.35D);
    }

    public static boolean isBossOrBeast(EntityType<?> type) {
        return mobToughness(type) >= 0.85D;
    }

    /** 是否为本模组生物 / whether the entity belongs to this mod */
    public static boolean isDynastyMob(EntityType<?> type) {
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(type);
        return id != null && id.getNamespace().equals(Dynasty.MODID);
    }

    /** 敌方对玩家的单次伤害上限（占玩家最大生命的比例）：
     *  杂兵 25% / 精英 45% / Boss·神兽 60%。这样开局 20 血不会被一发秒。 */
    public static float playerDamageCapFactor(EntityType<?> type) {
        double toughness = mobToughness(type);
        if (toughness >= 0.90D) {
            return 0.60F;
        }
        if (toughness >= 0.70D) {
            return 0.45F;
        }
        return 0.25F;
    }
}

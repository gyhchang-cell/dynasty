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

    static {
        // 每件装备：{每件减伤, 每件生命加成} / per piece: {damage reduction, bonus health}
        SET_BONUS.put("jade", new double[]{0.15D, 150.0D});
        SET_BONUS.put("general", new double[]{0.18D, 200.0D});
        SET_BONUS.put("dragon_scale", new double[]{0.20D, 250.0D});

        // 敌方减伤：原版血量上限 1024，靠减伤把 Boss 的有效血量拉到 2.5 万左右
        // enemy damage reduction: keeps boss effective HP around 25k despite the 1024 HP cap
        MOB_TOUGHNESS.put("dragon_emperor", 0.96D);
        MOB_TOUGHNESS.put("undead_first_emperor", 0.96D);
        MOB_TOUGHNESS.put("rebel_general", 0.95D);
        MOB_TOUGHNESS.put("eunuch_mastermind", 0.95D);
        MOB_TOUGHNESS.put("nian_beast", 0.90D);
        MOB_TOUGHNESS.put("qilin", 0.85D);
        MOB_TOUGHNESS.put("phoenix", 0.92D);
        MOB_TOUGHNESS.put("nine_tailed_fox", 0.90D);
        MOB_TOUGHNESS.put("royal_guard", 0.80D);
        MOB_TOUGHNESS.put("assassin", 0.75D);
        MOB_TOUGHNESS.put("imperial_soldier", 0.50D);
        MOB_TOUGHNESS.put("rebel_soldier", 0.50D);
        MOB_TOUGHNESS.put("terracotta_warrior", 0.50D);
        MOB_TOUGHNESS.put("archer", 0.50D);
        MOB_TOUGHNESS.put("minister", 0.0D);
    }

    /** 装备名（如 jade / general / dragon_scale）-> 套装加成 */
    public static double[] setNameBonus(String itemId) {
        for (Map.Entry<String, double[]> entry : SET_BONUS.entrySet()) {
            if (itemId.startsWith(entry.getKey())) {
                return entry.getValue();
            }
        }
        return null;
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
                armor += id.contains("helmet") ? 16.0D : id.contains("chestplate") ? 24.0D
                        : id.contains("leggings") ? 19.0D : 12.0D;
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

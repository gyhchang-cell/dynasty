package com.dynasty;

import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;

/**
 * Dynasty 工具/武器的材质等级。
 * Dynasty tool &amp; weapon tiers.
 */
@SuppressWarnings("null")
public final class DynastyTiers {

    private DynastyTiers() {
    }

    private static Tier make(float speed, int uses, float damage, int level, int ench, java.util.function.Supplier<net.minecraft.world.item.Item> repair) {
        return new Tier() {
            @Override
            public int getUses() {
                return uses;
            }

            @Override
            public float getSpeed() {
                return speed;
            }

            @Override
            public float getAttackDamageBonus() {
                return damage;
            }

            @Override
            public int getLevel() {
                return level;
            }

            @Override
            public int getEnchantmentValue() {
                return ench;
            }

            @Override
            public Ingredient getRepairIngredient() {
                return Ingredient.of(repair.get());
            }
        };
    }

    /** 青铜 / Bronze（攻击伤害 ≥1000） */
    public static final Tier BRONZE =
            make(14.0F, 8000, 500.0F, 3, 20, () -> DynastyItems.BRONZE_INGOT.get());

    /** 官银 / Official Silver */
    public static final Tier OFFICIAL_SILVER =
            make(18.0F, 20000, 700.0F, 4, 26, () -> DynastyItems.SILVER_INGOT.get());

    /** 玉 / Jade */
    public static final Tier JADE =
            make(22.0F, 45000, 900.0F, 5, 32, () -> DynastyItems.JADE.get());

    /** 龙晶 / Dragon Crystal（顶级） */
    public static final Tier DRAGON_CRYSTAL =
            make(30.0F, 120000, 1300.0F, 6, 40, () -> DynastyItems.DRAGON_CRYSTAL.get());
}

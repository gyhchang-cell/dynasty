package com.dynasty;

import net.minecraft.world.item.Tier;
import net.minecraft.world.item.crafting.Ingredient;

/**
 * Dynasty 工具/武器的材质等级（重制版：从木矛到龙晶的完整成长曲线）。
 *
 * 设计说明：总攻击力 = 1（空手）+ 材质加成 + 物品参数。
 * 早期材质（木/石/铜/铁）和原版同一个数量级，之后进入王朝的高数值阶段，
 * 所以「开局不会直接拿 1000 伤害」，但后期依然能打到 Boss 的士气减伤。
 *
 * Dynasty tool &amp; weapon tiers. Attack damage = 1 (bare hand) + tier bonus + item value:
 * early tiers stay close to vanilla so the game does not start at 1000 damage, while the
 * late tiers still reach the numbers needed against boss morale reduction.
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

    /** 木 / Wood（总攻击 5 级）/ primitive */
    public static final Tier PRIMITIVE =
            make(2.0F, 90, 0.0F, 0, 15, () -> net.minecraft.world.item.Items.OAK_PLANKS);

    /** 石 / Stone */
    public static final Tier STONE =
            make(4.0F, 200, 1.0F, 1, 17, () -> net.minecraft.world.item.Items.COBBLESTONE);

    /** 铜 / Copper（原版铜锭）/ copper */
    public static final Tier COPPER =
            make(6.0F, 400, 3.0F, 1, 18, () -> net.minecraft.world.item.Items.COPPER_INGOT);

    /** 铁 / Iron（原版铁锭）/ iron */
    public static final Tier IRON =
            make(7.0F, 900, 5.0F, 2, 20, () -> net.minecraft.world.item.Items.IRON_INGOT);

    /** 青铜 / Bronze（王朝第一档稀有材质，总攻击 ≈ 34）/ first dynasty tier */
    public static final Tier BRONZE =
            make(12.0F, 8000, 22.0F, 3, 22, () -> DynastyItems.BRONZE_INGOT.get());

    /** 官银 / Official Silver */
    public static final Tier OFFICIAL_SILVER =
            make(16.0F, 20000, 40.0F, 4, 26, () -> DynastyItems.SILVER_INGOT.get());

    /** 玉 / Jade */
    public static final Tier JADE =
            make(20.0F, 45000, 70.0F, 5, 32, () -> DynastyItems.JADE.get());

    /** 龙晶 / Dragon Crystal（顶级）/ best tier */
    public static final Tier DRAGON_CRYSTAL =
            make(28.0F, 120000, 140.0F, 6, 40, () -> DynastyItems.DRAGON_CRYSTAL.get());
}

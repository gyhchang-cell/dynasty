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

    /** 玉甲：轻盈、附魔强、减伤 60% / Jade: 28 armor, 60% damage reduction */
    public static final ArmorMaterial JADE =
            make("jade", new int[]{13, 15, 16, 11}, new int[]{12, 18, 14, 9}, 32, 20.0F, 0.35F, 400,
                    () -> DynastyItems.JADE.get());

    /** 龙鳞甲：防御最高、减伤 80% / Dragon Scale: 71 armor, 80% damage reduction */
    public static final ArmorMaterial DRAGON_SCALE =
            make("dragon_scale", new int[]{13, 15, 16, 11}, new int[]{16, 24, 19, 12}, 26, 20.0F, 1.0F, 600,
                    () -> DynastyItems.DRAGON_SCALE.get());

    /** 将军铠：均衡、减伤 72% / General: 60 armor, 72% damage reduction */
    public static final ArmorMaterial GENERAL =
            make("general", new int[]{13, 15, 16, 11}, new int[]{14, 20, 16, 10}, 20, 20.0F, 0.5F, 450,
                    () -> DynastyItems.BRONZE_INGOT.get());
}

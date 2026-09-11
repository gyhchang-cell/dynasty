package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Dynasty 附魔：破军（加伤）/ 铁壁（减伤）/ 斩将（对亡灵加伤）。
 * Dynasty enchantments: Breaker (damage), Bulwark (resistance), Beheading (bonus vs undead).
 */
public class DynastyEnchantments {

    public static final DeferredRegister<Enchantment> ENCHANTMENTS =
            DeferredRegister.create(ForgeRegistries.ENCHANTMENTS, Dynasty.MODID);

    public static final RegistryObject<Enchantment> BREAKER = ENCHANTMENTS.register("breaker", BreakerEnchantment::new);
    public static final RegistryObject<Enchantment> BULWARK = ENCHANTMENTS.register("bulwark", BulwarkEnchantment::new);
    public static final RegistryObject<Enchantment> BEHEADING = ENCHANTMENTS.register("beheading", BeheadingEnchantment::new);

    /** 破军：近战附加伤害 / Breaker: bonus melee damage */
    public static class BreakerEnchantment extends Enchantment {
        public BreakerEnchantment() {
            super(Rarity.RARE, EnchantmentCategory.WEAPON, new EquipmentSlot[]{EquipmentSlot.MAINHAND});
        }

        @Override
        public int getMaxLevel() {
            return 3;
        }

        @Override
        public int getMinCost(int level) {
            return 5 + (level - 1) * 8;
        }

        @Override
        public int getMaxCost(int level) {
            return getMinCost(level) + 20;
        }
    }

    /** 铁壁：减免受到的伤害 / Bulwark: damage reduction while worn */
    public static class BulwarkEnchantment extends Enchantment {
        public BulwarkEnchantment() {
            super(Rarity.UNCOMMON, EnchantmentCategory.ARMOR,
                    new EquipmentSlot[]{EquipmentSlot.HEAD, EquipmentSlot.CHEST, EquipmentSlot.LEGS, EquipmentSlot.FEET});
        }

        @Override
        public int getMaxLevel() {
            return 2;
        }

        @Override
        public int getMinCost(int level) {
            return 8 + (level - 1) * 10;
        }

        @Override
        public int getMaxCost(int level) {
            return getMinCost(level) + 20;
        }
    }

    /** 斩将：对亡灵额外伤害 / Beheading: extra damage against undead */
    public static class BeheadingEnchantment extends Enchantment {
        public BeheadingEnchantment() {
            super(Rarity.VERY_RARE, EnchantmentCategory.WEAPON, new EquipmentSlot[]{EquipmentSlot.MAINHAND});
        }

        @Override
        public int getMaxLevel() {
            return 1;
        }

        @Override
        public int getMinCost(int level) {
            return 20;
        }

        @Override
        public int getMaxCost(int level) {
            return 50;
        }
    }
}

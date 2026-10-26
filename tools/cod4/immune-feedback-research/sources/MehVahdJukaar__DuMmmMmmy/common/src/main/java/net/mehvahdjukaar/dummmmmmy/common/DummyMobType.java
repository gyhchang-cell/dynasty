package net.mehvahdjukaar.dummmmmmy.common;

import net.mehvahdjukaar.dummmmmmy.Dummmmmmy;
import net.mehvahdjukaar.moonlight.api.util.Utils;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.raid.Raid;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CarvedPumpkinBlock;

// mimics old behavior now driven by tags in a dynamic manner
public enum DummyMobType {
    UNDEFINED,
    UNDEAD,
    AQUATIC,
    ARTHROPOD,
    NETHER_MOB,
    SCARECROW,
    DECOY;

    public static DummyMobType get(ItemStack headStack) {
        if (headStack.is(Dummmmmmy.UNDEAD_HEADS)) return UNDEAD;
        else if (headStack.is(Dummmmmmy.AQUATIC_MOB_HEADS)) return AQUATIC;
        else if (headStack.is(Dummmmmmy.ARTHROPOD_HEADS)) return ARTHROPOD;
        else if (headStack.is(Items.PLAYER_HEAD)) return DECOY;
        else if (headStack.is(Dummmmmmy.NETHER_MOB_HEADS)) return NETHER_MOB;
        else if (isPumpkin(headStack.getItem())) return SCARECROW;
        else return UNDEFINED;
    }

    private static boolean isPumpkin(Item item) {
        if (item instanceof BlockItem bi) {
            Block block = bi.getBlock();
            String name = BuiltInRegistries.ITEM.getKey(item).getPath();
            return block instanceof CarvedPumpkinBlock || name.contains("pumpkin") || name.contains("jack_o");
        }
        return false;
    }

    public boolean isInvertedHealAndHarm() {
        return this == UNDEAD;
    }

    public boolean ignoresPoisonAndRegen() {
        return this == UNDEAD;
    }

    // mimics tag behavior
    public boolean isVulnerableTo(Enchantment enchantment) {
        ResourceKey<?> id = Utils.hackyGetRegistry(Registries.ENCHANTMENT).getResourceKey(enchantment).get();
        if (id == Enchantments.SMITE) {
            return this == UNDEAD;
        }
        if (id == Enchantments.BANE_OF_ARTHROPODS) {
            return this == ARTHROPOD;
        }
        if (id == Enchantments.IMPALING) {
            return this == AQUATIC;
        }
        return false;
    }

    public boolean freezeHurtsExtra() {
        return this == NETHER_MOB;
    }
}

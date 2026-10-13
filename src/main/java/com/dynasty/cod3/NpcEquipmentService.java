package com.dynasty.cod3;

import java.util.*;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.*;
import net.minecraft.world.item.enchantment.*;
import net.minecraftforge.registries.ForgeRegistries;

/** Work on a copy, keep all item NBT, and only add compatible, useful enchantments. */
public final class NpcEquipmentService {
    public static final int REPAIR_COST=16, ENCHANT_COST=32;
    public static List<Enchantment> candidates(ItemStack gear){
        if(gear.isEmpty()||gear.getCount()!=1||!gear.isDamageableItem())return List.of();
        var current=EnchantmentHelper.getEnchantments(gear);var result=new ArrayList<Enchantment>();
        for(var enchantment:ForgeRegistries.ENCHANTMENTS){
            if(enchantment.isCurse()||enchantment.isTreasureOnly()||!enchantment.isDiscoverable()||!enchantment.canEnchant(gear)
                    ||current.getOrDefault(enchantment,0)>=enchantment.getMaxLevel())continue;
            if(current.keySet().stream().anyMatch(old->old!=enchantment&&!old.isCompatibleWith(enchantment)))continue;
            result.add(enchantment);
        }
        // Registry order is stable; selection is made only after a server-validated paid submission.
        result.sort(Comparator.comparing(e->Objects.requireNonNull(ForgeRegistries.ENCHANTMENTS.getKey(e)).toString()));return result;
    }
    public static ItemStack repair(ItemStack gear){var copy=gear.copy();copy.setDamageValue(0);return copy;}
    public static ItemStack enchant(ItemStack gear,RandomSource random){
        var copy=gear.copy();var enchants=EnchantmentHelper.getEnchantments(copy);
        int wanted=1+random.nextInt(3),added=0;
        for(int i=0;i<wanted;i++){
            var choices=candidates(copy);if(choices.isEmpty())break;
            var selected=choices.get(random.nextInt(choices.size()));
            int minimum=enchants.getOrDefault(selected,0)+1;
            int level=minimum+random.nextInt(selected.getMaxLevel()-minimum+1);
            enchants.put(selected,level);EnchantmentHelper.setEnchantments(enchants,copy);added++;
        }
        return added==0?ItemStack.EMPTY:copy;
    }
    private NpcEquipmentService(){}
}

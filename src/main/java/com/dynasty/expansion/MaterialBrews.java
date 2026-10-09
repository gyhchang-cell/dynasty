package com.dynasty.expansion;

import net.minecraft.world.item.*;
import net.minecraft.world.item.alchemy.*;
import net.minecraft.network.chat.Component;

/** Existing vanilla potion item/projectile/cloud, native merchant stock and original material IDs. */
public final class MaterialBrews {
    public static ItemStack gu(){
        var s=PotionUtils.setPotion(new ItemStack(Items.LINGERING_POTION),Potions.LONG_POISON);
        s.getOrCreateTag().putBoolean("cod4HeiPoGu",true);s.getOrCreateTag().putInt("CustomPotionColor",0x6C7758);
        s.setHoverName(Component.translatable("item.dynasty.hei_po_gu"));return s;
    }
    private MaterialBrews(){}
}

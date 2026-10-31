package org.zala.crossbowmulticharge.moditems;

import net.fabricmc.api.ModInitializer;
import net.minecraft.enchantment.Enchantment;
import net.minecraft.entity.EquipmentSlot;
import org.zala.crossbowmulticharge.moditems.enchantments.CrossbowStorageEnchantment;

public class ModContent implements ModInitializer {
    public static final Enchantment STORAGEUP = ModItems.register(new CrossbowStorageEnchantment(Enchantment.Rarity.RARE, EquipmentSlot.MAINHAND), "storageup");

    @Override
    public void onInitialize() {
        ModItems.initialize();
    }
}
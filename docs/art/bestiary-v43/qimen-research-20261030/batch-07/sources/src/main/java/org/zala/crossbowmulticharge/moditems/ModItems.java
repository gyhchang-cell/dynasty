package org.zala.crossbowmulticharge.moditems;

import net.fabricmc.fabric.api.item.v1.FabricItemSettings;
import net.minecraft.enchantment.Enchantment;
import net.minecraft.item.Item;
import net.minecraft.item.Items;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.util.Identifier;
import org.zala.crossbowmulticharge.Crossbowmulticharge;

public class ModItems {
    public static Item register(Item item, String id) {
        Identifier itemID = new Identifier(Crossbowmulticharge.MOD_ID, id);
        return Registry.register(Registries.ITEM, itemID, item);
    }

    public static Enchantment register(Enchantment enchantment, String id) {
        Identifier itemID = new Identifier(Crossbowmulticharge.MOD_ID, id);
        return Registry.register(Registries.ENCHANTMENT, itemID, enchantment);
    }

    public static Item overrideItem(Item toOverride, Item newItem){
        return Registry.register(Registries.ITEM, Registries.ITEM.getRawId(toOverride), Registries.ITEM.getId(toOverride).getPath(), newItem);
    }

    public static void initialize() {
    }
}

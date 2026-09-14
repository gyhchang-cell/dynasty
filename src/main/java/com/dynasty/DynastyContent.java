package com.dynasty;

import net.minecraftforge.eventbus.api.IEventBus;

/**
 * Dynasty 模块统一注册入口 (content registry) / Single registration entry point for the Dynasty module.
 */
public final class DynastyContent {

    private DynastyContent() {
    }

    public static void register(IEventBus modEventBus) {
        DynastyBlocks.BLOCKS.register(modEventBus);
        DynastyBlocks.BLOCK_ITEMS.register(modEventBus);
        DynastyItems.ITEMS.register(modEventBus);
        com.dynasty.DynastyFineItems.ITEMS.register(modEventBus);
        DynastyGear.ITEMS.register(modEventBus);
        DynastyWeapons.ITEMS.register(modEventBus);
        DynastyRelics.ITEMS.register(modEventBus);
        DynastyTrinkets.ITEMS.register(modEventBus);
        DynastyManual.ITEMS.register(modEventBus);
        DynastyEffects.EFFECTS.register(modEventBus);
        DynastyTabs.TABS.register(modEventBus);
        com.dynasty.entity.DynastyEntities.ENTITIES.register(modEventBus);
        com.dynasty.worldgen.DynastyFeatures.FEATURES.register(modEventBus);
        DynastyEnchantments.ENCHANTMENTS.register(modEventBus);
        DynastyPotions.POTIONS.register(modEventBus);
        com.dynasty.structure.DynastyStructures.STRUCTURE_TYPES.register(modEventBus);
        com.dynasty.structure.DynastyStructures.PIECE_TYPES.register(modEventBus);
        com.dynasty.network.DynastyNetwork.register();
    }
}

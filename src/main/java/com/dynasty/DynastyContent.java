package com.dynasty;

import net.minecraftforge.eventbus.api.IEventBus;

/**
 * Dynasty 模块统一注册入口 (content registry) / Single registration entry point for the Dynasty module.
 */
public final class DynastyContent {

    private DynastyContent() {
    }

    public static void register(IEventBus modEventBus) {
        com.dynasty.expansion.ExpansionContent.register(modEventBus);
        com.dynasty.infusion.InfusionContent.register(modEventBus);
        com.dynasty.army.ArmyContent.register(modEventBus);
        DynastyBlocks.BLOCKS.register(modEventBus);
        DynastyBlocks.BLOCK_ITEMS.register(modEventBus);
        com.dynasty.workshop.WorkshopBlockEntity.TYPES.register(modEventBus);
        com.dynasty.workshop.WorkshopMenu.MENUS.register(modEventBus);
        com.dynasty.cod3.LootableRemains.BLOCKS.register(modEventBus);
        com.dynasty.cod3.LootableRemains.ITEMS.register(modEventBus);
        com.dynasty.cod3.LootableRemains.TYPES.register(modEventBus);
        com.dynasty.cod3.NpcContent.ENTITIES.register(modEventBus);
        com.dynasty.cod3.NpcContent.ITEMS.register(modEventBus);
        com.dynasty.cod3.StoryAnchor.BLOCKS.register(modEventBus);
        com.dynasty.cod3.StoryAnchor.TYPES.register(modEventBus);
        com.dynasty.workshop.DynastyTreasures.ITEMS.register(modEventBus);
        com.dynasty.puzzle.PuzzleBlocks.BLOCKS.register(modEventBus);
        com.dynasty.puzzle.PuzzleBlocks.ITEMS.register(modEventBus);
        com.dynasty.dungeon.DungeonContent.register(modEventBus);
        com.dynasty.ritual.ZhenyuanRitualContent.register(modEventBus);
        com.dynasty.ritual.ZhenyuanBosses.ENTITIES.register(modEventBus);
        DynastyItems.ITEMS.register(modEventBus);
        com.dynasty.DynastyBasicFoods.ITEMS.register(modEventBus);
        com.dynasty.DynastyFineItems.ITEMS.register(modEventBus);
        DynastyGear.ITEMS.register(modEventBus);
        DynastyWeapons.ITEMS.register(modEventBus);
        DynastyRelics.ITEMS.register(modEventBus);
        DynastyTrinkets.ITEMS.register(modEventBus);
        DynastyManual.ITEMS.register(modEventBus);
        DynastyEffects.EFFECTS.register(modEventBus);
        DynastyTabs.TABS.register(modEventBus);
        com.dynasty.entity.DynastyEntities.ENTITIES.register(modEventBus);
        com.dynasty.blueprint.BlueprintEntities.register(modEventBus);
        com.dynasty.blueprint.EcologyBiomeModifier.SERIALIZERS.register(modEventBus);
        com.dynasty.worldevent.WorldEventItems.ITEMS.register(modEventBus);
        modEventBus.addListener(com.dynasty.blueprint.BlueprintSpawns::register);
        com.dynasty.worldgen.DynastyFeatures.FEATURES.register(modEventBus);
        DynastyEnchantments.ENCHANTMENTS.register(modEventBus);
        DynastyPotions.POTIONS.register(modEventBus);
        com.dynasty.structure.DynastyStructures.STRUCTURE_TYPES.register(modEventBus);
        com.dynasty.structure.DynastyStructures.PIECE_TYPES.register(modEventBus);
        com.dynasty.structure.megabuild.MegabuildStructures.STRUCTURE_TYPES.register(modEventBus);
        com.dynasty.structure.megabuild.MegabuildStructures.PIECE_TYPES.register(modEventBus);
        com.dynasty.structure.megabuild.NaturalSculptures.TYPES.register(modEventBus);
        com.dynasty.structure.megabuild.NaturalSculptures.PIECES.register(modEventBus);
        com.dynasty.structure.megabuild.NaturalSculptures.PLACEMENTS.register(modEventBus);
        com.dynasty.network.DynastyNetwork.register();
    }
}

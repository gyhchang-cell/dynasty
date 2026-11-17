package com.dynasty;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.MissingMappingsEvent;

/** Registry aliases only: Forge retains the original stack rather than issuing a new one. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class LegacyItemMappings {
    private static final ResourceLocation QUEST_BOOK = new ResourceLocation("ftbquests", "book");
    private static final ResourceLocation GUIDE = new ResourceLocation(Dynasty.MODID, "dynasty_guide");
    private static final ResourceLocation VAJRA = new ResourceLocation(Dynasty.MODID, "vajra_talisman");

    private LegacyItemMappings() {}

    @SubscribeEvent
    public static void missingItems(MissingMappingsEvent event) {
        for (MissingMappingsEvent.Mapping<Item> mapping : event.getMappings(Registries.ITEM, Dynasty.MODID)) {
            Item target;
            switch (mapping.getKey().getPath()) {
                case "quest_ledger" -> {
                    target = registered(QUEST_BOOK);
                    if (target == null) {
                        target = registered(GUIDE);
                        if (target != null) {
                            Dynasty.LOGGER.warn("[Dynasty] {}: FTB quest book unavailable; retaining the stack as the built-in guide",
                                    mapping.getKey());
                        }
                    }
                }
                // The historical replacement is protection, not the removed healing behavior.
                case "healing_talisman" -> target = registered(VAJRA);
                default -> { continue; }
            }
            if (target == null) {
                Dynasty.LOGGER.error("[Dynasty] No registered replacement for {}; leaving its missing mapping unresolved",
                        mapping.getKey());
                continue;
            }
            mapping.remap(target);
            Dynasty.LOGGER.info("[Dynasty] Legacy item {} -> {}", mapping.getKey(), ForgeRegistries.ITEMS.getKey(target));
        }
    }

    private static Item registered(ResourceLocation id) {
        if (!ForgeRegistries.ITEMS.containsKey(id)) return null;
        Item item = ForgeRegistries.ITEMS.getValue(id);
        return item != null && item != Items.AIR && id.equals(ForgeRegistries.ITEMS.getKey(item)) ? item : null;
    }
}

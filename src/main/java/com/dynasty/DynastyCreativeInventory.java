package com.dynasty;

import com.dynasty.block.DynastyInstrumentBlock;
import com.dynasty.block.DynastyPortalBlock;
import com.dynasty.block.OilFueledBlock;
import com.dynasty.block.RitualAltarBlock;
import com.dynasty.bounty.BountyBoardBlock;
import com.dynasty.expansion.ExpansionWeapons;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArrowItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.DiggerItem;
import net.minecraft.world.item.ElytraItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.PotionItem;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.TridentItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Set;

/** Presentation only: stable functional groups, with every Dynasty spawn egg at the end. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class DynastyCreativeInventory {
    // Declaration order is the tab order; no names, translations or pinyin are compared.
    private enum Bucket {
        EQUIPMENT, WEAPONS, ARMOR, TRINKETS, FUNCTIONAL_BLOCKS, DECORATION,
        FOOD, POTIONS, TOOLS, CURRENCY, MATERIALS, QUEST, EGGS
    }

    private record Entry(ItemStack stack, CreativeModeTab.TabVisibility visibility) { }

    private static final Set<String> CURRENCY = Set.of(
            "copper_coin", "silver_coin", "gold_coin", "jade_coin", "dragon_coin");
    private static final Set<String> QUEST = Set.of(
            "jade_seal", "official_seal", "edict", "tiger_tally", "exam_paper",
            "dynasty_guide", "dynasty_manual", "blueprint", "rebel_head", "eunuch_token",
            "emperor_bone", "dragon_emperor_seal", "sky_token", "sea_token", "thunder_token",
            "white_deer_token", "tianming_jade", "official_travel_document");
    // ExpansionSupplies all have food properties, including medicinal pills and incense.
    private static final Set<String> MEDICINE = Set.of("regen_pill", "qi_pill", "antidote_pill");
    private static final Set<String> TOOLS = Set.of(
            "ink_brush", "trinket_box", "evocation_talisman", "locust_dust",
            "soul_incense", "guide_incense");

    private DynastyCreativeInventory() { }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void arrange(BuildCreativeModeTabContentsEvent event) {
        if (event.getTab() != DynastyTabs.DYNASTY_TAB.get()) {
            return;
        }

        var groups = new EnumMap<Bucket, List<Entry>>(Bucket.class);
        for (Bucket bucket : Bucket.values()) {
            groups.put(bucket, new ArrayList<>());
        }
        Set<Item> presentEggs = Collections.newSetFromMap(new IdentityHashMap<>());
        var entries = event.getEntries();
        // Keep the original stack objects (including all NBT variants) and visibility values.
        for (var entry : entries) {
            ItemStack stack = entry.getKey();
            groups.get(bucket(stack.getItem())).add(new Entry(stack, entry.getValue()));
            if (stack.getItem() instanceof SpawnEggItem) {
                presentEggs.add(stack.getItem());
            }
        }

        // Scan the complete registry, including elite/NPC/expansion registries. Existing
        // eggs retain their original order; missing eggs follow in numeric registration order.
        List<Item> missingEggs = new ArrayList<>();
        for (var registered : ForgeRegistries.ITEMS.getEntries()) {
            Item item = registered.getValue();
            if (Dynasty.MODID.equals(registered.getKey().location().getNamespace())
                    && item instanceof SpawnEggItem && !presentEggs.contains(item)
                    && item.isEnabled(event.getFlags())) {
                missingEggs.add(item);
            }
        }
        missingEggs.sort(Comparator.comparingInt(BuiltInRegistries.ITEM::getId));
        for (Item egg : missingEggs) {
            groups.get(Bucket.EGGS).add(new Entry(egg.getDefaultInstance(),
                    CreativeModeTab.TabVisibility.PARENT_AND_SEARCH_TABS));
        }

        // MutableHashedLinkedMap has no clear(): remove through its supported iterator,
        // then reinsert into the same map to preserve Forge's stack hashing/merge policy.
        var iterator = entries.iterator();
        while (iterator.hasNext()) {
            iterator.next();
            iterator.remove();
        }
        for (Bucket bucket : Bucket.values()) {
            for (Entry entry : groups.get(bucket)) {
                entries.put(entry.stack(), entry.visibility());
            }
        }
    }

    private static Bucket bucket(Item item) {
        if (item instanceof SpawnEggItem) return Bucket.EGGS;
        if (item instanceof ArmorItem) return Bucket.ARMOR;
        if (item instanceof DynastyTrinketTips.Charm) return Bucket.TRINKETS;
        if (item instanceof SwordItem || item instanceof BowItem || item instanceof CrossbowItem
                || item instanceof TridentItem || item instanceof ArrowItem
                || item instanceof ExpansionWeapons.MeteorHammer) return Bucket.WEAPONS;
        if (item instanceof ShieldItem || item instanceof ElytraItem) return Bucket.EQUIPMENT;

        var key = ForgeRegistries.ITEMS.getKey(item);
        String id = key != null && Dynasty.MODID.equals(key.getNamespace()) ? key.getPath() : "";
        if (item instanceof BlockItem blockItem) {
            var block = blockItem.getBlock();
            return block instanceof EntityBlock || block instanceof DynastyPortalBlock
                    || block instanceof RitualAltarBlock || block instanceof DynastyInstrumentBlock
                    || block instanceof OilFueledBlock || block instanceof BountyBoardBlock
                    || id.equals("recruitment_desk")
                    ? Bucket.FUNCTIONAL_BLOCKS : Bucket.DECORATION;
        }
        if (item instanceof PotionItem || item instanceof DynastyUsables.PillItem
                || MEDICINE.contains(id)) return Bucket.POTIONS;
        if (TOOLS.contains(id)) return Bucket.TOOLS;
        if (item.isEdible()) return Bucket.FOOD;
        if (CURRENCY.contains(id)) return Bucket.CURRENCY;
        if (QUEST.contains(id) || item instanceof DynastyUsables.GuideItem) return Bucket.QUEST;
        if (item instanceof FestivalLanternItem || id.equals("roof_tile")) return Bucket.DECORATION;
        if (item instanceof DiggerItem || item instanceof TalismanCharmItem
                || item instanceof DynastyUsables.TalismanItem
                || item instanceof com.dynasty.workshop.DynastyTreasures.Treasure
                || (key != null && (key.getNamespace().equals("naturescompass")
                        || key.getNamespace().equals("explorerscompass")))) return Bucket.TOOLS;
        // Preserve unclassified entries as materials; never filter an existing stack out.
        return Bucket.MATERIALS;
    }
}

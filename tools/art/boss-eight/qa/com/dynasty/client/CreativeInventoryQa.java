package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.DynastyItems;
import com.dynasty.DynastyPotions;
import com.dynasty.DynastyTabs;
import com.google.gson.GsonBuilder;
import net.minecraft.client.Minecraft;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.flag.FeatureFlagSet;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.PotionItem;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraftforge.registries.ForgeRegistries;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Call verify(mc, outputDirectory) on the client thread after the parent loads a world. */
public final class CreativeInventoryQa {
    private CreativeInventoryQa() { }

    public static void verify(Minecraft mc, Path outputDirectory) throws IOException {
        if (!mc.isSameThread() || mc.level == null || mc.player == null) {
            throw new IllegalStateException("Creative inventory QA requires a loaded world on the client thread");
        }
        Files.createDirectories(outputDirectory);
        FeatureFlagSet features = mc.level.enabledFeatures();
        boolean rebuilt = CreativeModeTabs.tryRebuildTabContents(features, true, mc.level.registryAccess());
        var tab = DynastyTabs.DYNASTY_TAB.get();
        List<ItemStack> display = new ArrayList<>(tab.getDisplayItems());
        List<ItemStack> search = new ArrayList<>(tab.getSearchTabDisplayItems());
        List<String> expectedEggs = new ArrayList<>();
        for (var registered : ForgeRegistries.ITEMS.getEntries()) {
            var id = registered.getKey().location();
            if (Dynasty.MODID.equals(id.getNamespace())
                    && registered.getValue() instanceof SpawnEggItem
                    && registered.getValue().isEnabled(features)) {
                expectedEggs.add(id.toString());
            }
        }
        List<ItemStack> expectedPotions = List.of(
                PotionUtils.setPotion(new ItemStack(DynastyItems.DYNASTY_POTION.get()), DynastyPotions.DRAGON_MIGHT.get()),
                PotionUtils.setPotion(new ItemStack(DynastyItems.DYNASTY_POTION.get()), DynastyPotions.IRON_WALL.get()),
                PotionUtils.setPotion(new ItemStack(DynastyItems.DYNASTY_POTION.get()), DynastyPotions.SWIFT_WIND.get()),
                PotionUtils.setPotion(new ItemStack(DynastyItems.DYNASTY_SPLASH_POTION.get()), DynastyPotions.DRAGON_MIGHT.get()),
                PotionUtils.setPotion(new ItemStack(DynastyItems.DYNASTY_LINGERING_POTION.get()), DynastyPotions.LOYALTY.get()));

        List<String> failures = new ArrayList<>();
        if (expectedEggs.isEmpty()) failures.add("No enabled Dynasty spawn eggs registered");
        Map<String, Object> report = new LinkedHashMap<>();
        report.put("tab", DynastyTabs.DYNASTY_TAB.getId().toString());
        report.put("rebuilt", rebuilt); // false is valid when the cached parameters already match.
        report.put("operatorPermissions", true);
        report.put("expectedEnabledDynastyEggCount", expectedEggs.size());
        report.put("expectedEnabledDynastyEggs", expectedEggs);
        report.put("expectedPotionVariantCount", expectedPotions.size());
        report.put("display", inspect("display", display, expectedEggs, expectedPotions, failures));
        report.put("search", inspect("search", search, expectedEggs, expectedPotions, failures));
        report.put("passed", failures.isEmpty());
        report.put("failures", failures);
        // Always persist the actual order and diagnostics before asserting, including on failure.
        Files.writeString(outputDirectory.resolve("creative-inventory.json"),
                new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create().toJson(report) + "\n");
        writeTsv(outputDirectory.resolve("creative-inventory-display.tsv"), display);
        writeTsv(outputDirectory.resolve("creative-inventory-search.tsv"), search);
        if (!failures.isEmpty()) {
            throw new AssertionError("Creative inventory QA failed: " + String.join("; ", failures));
        }
    }

    private static Map<String, Object> inspect(String view, List<ItemStack> stacks,
            List<String> expectedEggs, List<ItemStack> expectedPotions, List<String> failures) {
        Map<String, Integer> eggCounts = new LinkedHashMap<>();
        List<Map<String, Object>> rows = new ArrayList<>();
        int firstEgg = -1, lastEgg = -1, eggCount = 0, potionCount = 0;
        for (int i = 0; i < stacks.size(); i++) {
            ItemStack stack = stacks.get(i);
            String id = id(stack);
            boolean egg = stack.getItem() instanceof SpawnEggItem;
            if (egg) {
                if (firstEgg < 0) firstEgg = i;
                lastEgg = i;
                eggCount++;
                eggCounts.merge(id, 1, Integer::sum);
            } else if (firstEgg >= 0) {
                failures.add(view + ": non-egg after egg group at index " + i + ": " + id);
            }
            if (stack.getItem() instanceof PotionItem) potionCount++;
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("index", i);
            row.put("id", id);
            row.put("count", stack.getCount());
            row.put("spawnEgg", egg);
            row.put("potion", potionId(stack));
            row.put("tag", stack.hasTag() ? stack.getTag().toString() : "");
            row.put("stackSnbt", stack.save(new CompoundTag()).toString());
            rows.add(row);
        }
        for (String egg : expectedEggs) {
            int count = eggCounts.getOrDefault(egg, 0);
            if (count != 1) failures.add(view + ": expected one " + egg + ", found " + count);
        }
        if (firstEgg >= 0 && lastEgg - firstEgg + 1 != eggCount) {
            failures.add(view + ": spawn eggs are not contiguous");
        }
        Map<String, Integer> potionMatches = new LinkedHashMap<>();
        for (ItemStack expected : expectedPotions) {
            int matches = 0;
            for (ItemStack stack : stacks) {
                if (ItemStack.isSameItemSameTags(stack, expected) && stack.getCount() == expected.getCount()) matches++;
            }
            String label = id(expected) + "/" + potionId(expected);
            potionMatches.put(label, matches);
            if (matches != 1) failures.add(view + ": expected one intact potion stack " + label + ", found " + matches);
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("entryCount", stacks.size());
        result.put("spawnEggCount", eggCount);
        result.put("dynastySpawnEggCount", eggCounts.entrySet().stream()
                .filter(e -> e.getKey().startsWith(Dynasty.MODID + ":")).mapToInt(Map.Entry::getValue).sum());
        result.put("firstEggIndex", firstEgg);
        result.put("lastEggIndex", lastEgg);
        result.put("potionStackCount", potionCount);
        result.put("eggOccurrences", eggCounts);
        result.put("expectedPotionOccurrences", potionMatches);
        result.put("order", rows);
        return result;
    }

    private static void writeTsv(Path path, Collection<ItemStack> stacks) throws IOException {
        StringBuilder out = new StringBuilder("index\tid\tcount\tspawn_egg\tpotion\ttag\tstack_snbt\n");
        int index = 0;
        for (ItemStack stack : stacks) {
            out.append(index++).append('\t').append(id(stack)).append('\t').append(stack.getCount())
                    .append('\t').append(stack.getItem() instanceof SpawnEggItem).append('\t')
                    .append(potionId(stack)).append('\t')
                    .append(tsv(stack.hasTag() ? stack.getTag().toString() : "")).append('\t')
                    .append(tsv(stack.save(new CompoundTag()).toString())).append('\n');
        }
        Files.writeString(path, out);
    }

    private static String id(ItemStack stack) {
        return String.valueOf(ForgeRegistries.ITEMS.getKey(stack.getItem()));
    }

    private static String potionId(ItemStack stack) {
        return stack.getItem() instanceof PotionItem
                ? String.valueOf(ForgeRegistries.POTIONS.getKey(PotionUtils.getPotion(stack))) : "";
    }

    private static String tsv(String value) {
        return value.replace("\\", "\\\\").replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n");
    }
}

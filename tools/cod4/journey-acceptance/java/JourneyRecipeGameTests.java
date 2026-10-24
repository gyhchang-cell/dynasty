package com.dynasty.expansion;

import com.google.gson.*;
import com.mojang.authlib.GameProfile;
import java.nio.file.*;
import java.util.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.item.crafting.*;
import net.minecraft.world.level.GameType;
import net.minecraftforge.gametest.*;

/** Native transaction contracts with explicit fixture ingredients; not a survival playthrough. */
@GameTestHolder("dynasty_journey_qa")
@PrefixGameTestTemplate(false)
public final class JourneyRecipeGameTests {
    private static final JsonArray RESULTS = new JsonArray();

    static ServerPlayer player(GameTestHelper h) {
        var p = new ServerPlayer(h.getLevel().getServer(), h.getLevel(), new GameProfile(UUID.randomUUID(), "journey-qa"));
        p.connection = new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),
            new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND), p);
        p.setGameMode(GameType.SURVIVAL);
        p.setPos(h.absolutePos(new net.minecraft.core.BlockPos(2, 2, 2)).getCenter());
        return p;
    }

    static void record(String id, String check, boolean pass, String detail) {
        var row = new JsonObject(); row.addProperty("id", id); row.addProperty("check", check);
        row.addProperty("pass", pass); row.addProperty("detail", detail); RESULTS.add(row);
        try {
            Files.writeString(Path.of(System.getProperty("dynasty.journey.report")),
                new GsonBuilder().setPrettyPrinting().create().toJson(RESULTS) + "\n");
        } catch (java.io.IOException e) { throw new RuntimeException(e); }
    }

    private static ItemStack ingredient(JsonElement json) {
        var values = Ingredient.fromJson(json).getItems();
        if (values.length == 0) throw new IllegalStateException("Empty registered ingredient: " + json);
        var stack = values[0].copy(); stack.setCount(1); return stack;
    }

    private static JsonArray definitions() throws Exception {
        try (var r = new java.io.InputStreamReader(JourneyRecipeGameTests.class.getResourceAsStream("/journey-recipes.json"))) {
            return JsonParser.parseReader(r).getAsJsonArray();
        }
    }

    @GameTest(template = "bow_ritual_test", batch = "journey_furnace", timeoutTicks = 300)
    public static void allOriginalSmeltingRecipesCookWithActualFuelAndPayNativeResultSlots(GameTestHelper h) throws Exception {
        var p = player(h);
        var furnaces = new ArrayList<net.minecraft.world.level.block.entity.FurnaceBlockEntity>();
        var ids = new ArrayList<String>();
        var expected = new ArrayList<ItemStack>();
        for (var element : definitions()) {
            var entry = element.getAsJsonObject(); var data = entry.getAsJsonObject("json");
            if (!data.get("type").getAsString().equals("minecraft:smelting")) continue;
            var at = h.absolutePos(new net.minecraft.core.BlockPos(3 + furnaces.size() * 2, 2, 4));
            h.getLevel().setBlockAndUpdate(at, net.minecraft.world.level.block.Blocks.FURNACE.defaultBlockState());
            var furnace = (net.minecraft.world.level.block.entity.FurnaceBlockEntity)h.getLevel().getBlockEntity(at);
            furnace.setItem(0, ingredient(data.get("ingredient")));
            furnace.setItem(1, new ItemStack(Items.CHARCOAL));
            var recipe = h.getLevel().getRecipeManager().byKey(new ResourceLocation(entry.get("id").getAsString())).orElseThrow();
            furnaces.add(furnace); ids.add(entry.get("id").getAsString()); expected.add(recipe.getResultItem(h.getLevel().registryAccess()).copy());
        }
        h.assertTrue(furnaces.size() == 4, "All four original smelting definitions included");
        h.runAfterDelay(220, () -> {
            try {
                for (int i = 0; i < furnaces.size(); i++) {
                    var furnace = furnaces.get(i);
                    h.assertTrue(furnace.getItem(0).isEmpty() && furnace.getItem(1).isEmpty()
                        && ItemStack.matches(furnace.getItem(2), expected.get(i)), "Native server ticks consumed one input/fuel and produced exact output: " + ids.get(i));
                    var menu = new FurnaceMenu(11, p.getInventory(), furnace, new SimpleContainerData(4)); p.containerMenu = menu;
                    var result = menu.getSlot(2).remove(64); menu.getSlot(2).onTake(p, result);
                    h.assertTrue(ItemStack.matches(result, expected.get(i)) && furnace.getItem(2).isEmpty(), "Native furnace take is paid once");
                    record(ids.get(i), "native_furnace_payment", true, "220 actual server ticks; original ingredient plus one charcoal fixture; exact smelted result taken through FurnaceResultSlot");
                    p.closeContainer();
                }
                h.succeed();
            } finally {
                for (var furnace : furnaces) h.getLevel().setBlockAndUpdate(furnace.getBlockPos(), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
                p.discard();
            }
        });
    }

    @GameTest(template = "bow_ritual_test", batch = "journey_investment", timeoutTicks = 100)
    public static void oldEquipmentRemainsUsableAsOriginalCraftingMaterial(GameTestHelper h) throws Exception {
        // COD4-14 requires continuing material/upgrade/synergy value, not universal NBT transfer.
        // Original quest_growth.py:69 and published build chapters explicitly distinguish
        // NBT-preserving smithing from ordinary crafting. Record NBT behavior, do not impose it.
        int checked = 0;
        for (String id : new String[]{"sword_jade", "cod4/siege_crossbow", "bamboo_chestplate"}) {
            var p = player(h);
            try {
                var recipe = (CraftingRecipe) h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty", id)).orElseThrow();
                var menu = new CraftingMenu(9, p.getInventory(), ContainerLevelAccess.create(h.getLevel(), p.blockPosition())); p.containerMenu = menu;
                ItemStack predecessor = ItemStack.EMPTY;
                for (int i = 0; i < recipe.getIngredients().size(); i++) {
                    var input = recipe.getIngredients().get(i).getItems()[0].copy(); input.setCount(1);
                    if (i == 0) {
                        input.getOrCreateTag().putString("JourneyForeignData", "old-save-fixture");
                        input.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING, 2);
                        if (com.dynasty.DynastyWeaponProgression.eligible(input)) {
                            input.getOrCreateTagElement("dynastyWeaponGrowth").putInt("level", 7);
                            input.getOrCreateTagElement("dynastyWeaponGrowth").putLong("xp", 19);
                        }
                        predecessor = input.copy();
                    }
                    menu.getSlot(1 + i).set(input);
                }
                h.assertTrue(!menu.getSlot(0).getItem().isEmpty(), "An actual old stack is accepted by " + id);
                var output = menu.getSlot(0).remove(64); menu.getSlot(0).onTake(p, output);
                h.assertTrue(menu.getSlot(1).getItem().isEmpty(), "Old equipment was actually consumed");
                h.assertTrue(output.is(recipe.getResultItem(h.getLevel().registryAccess()).getItem())
                    && output.getCount() == recipe.getResultItem(h.getLevel().registryAccess()).getCount(),
                    "Original used equipment produces the exact higher-tier item: " + id);
                boolean kept = output.isEnchanted() && output.hasTag()
                    && output.getTag().getString("JourneyForeignData").equals("old-save-fixture")
                    && (!com.dynasty.DynastyWeaponProgression.eligible(predecessor)
                        || com.dynasty.DynastyWeaponProgression.level(output) == 7);
                checked++;
                record("dynasty:" + id, "old_equipment_material_use", true,
                    "Native ResultSlot consumed " + predecessor + "; result=" + output
                    + "; oldGrowth=" + com.dynasty.DynastyWeaponProgression.level(predecessor)
                    + "; newGrowth=" + com.dynasty.DynastyWeaponProgression.level(output)
                    + "; oldEnchanted=" + predecessor.isEnchanted() + "; newEnchanted=" + output.isEnchanted()
                    + "; observedNBTKept=" + kept
                    + "; NBT behavior is observational, not a COD4-14 requirement or confirmed product defect");
            } finally { p.closeContainer(); p.discard(); }
        }
        h.assertTrue(checked == 3, "All three used-equipment material paths paid and produced their original outputs");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", batch = "journey", timeoutTicks = 400)
    public static void everyOriginalCraftingRecipeMatchesAndPaysThroughNativeResultSlot(GameTestHelper h) throws Exception {
        int checked = 0, failed = 0;
        for (var element : definitions()) {
            var entry = element.getAsJsonObject(); var data = entry.getAsJsonObject("json");
            String type = data.get("type").getAsString(), id = entry.get("id").getAsString();
            if (!type.equals("minecraft:crafting_shaped") && !type.equals("minecraft:crafting_shapeless")) continue;
            var p = player(h);
            try {
                var recipe = (CraftingRecipe) h.getLevel().getRecipeManager().byKey(new ResourceLocation(id)).orElseThrow();
                var menu = new CraftingMenu(9, p.getInventory(), ContainerLevelAccess.create(h.getLevel(), p.blockPosition())); p.containerMenu = menu;
                if (type.equals("minecraft:crafting_shaped")) {
                    var pattern = data.getAsJsonArray("pattern"); var keys = data.getAsJsonObject("key");
                    for (int y = 0; y < pattern.size(); y++) {
                        String row = pattern.get(y).getAsString();
                        for (int x = 0; x < row.length(); x++) if (row.charAt(x) != ' ')
                            menu.getSlot(1 + y * 3 + x).set(ingredient(keys.get(String.valueOf(row.charAt(x)))));
                    }
                } else {
                    int slot = 1;
                    for (var input : data.getAsJsonArray("ingredients")) menu.getSlot(slot++).set(ingredient(input));
                }
                var grid = new TransientCraftingContainer(menu, 3, 3);
                for (int i = 0; i < 9; i++) grid.setItem(i, menu.getSlot(i + 1).getItem().copy());
                var chosen = h.getLevel().getRecipeManager().getRecipeFor(RecipeType.CRAFTING, grid, h.getLevel());
                var expected = recipe.assemble(grid, h.getLevel().registryAccess());
                if (chosen.isEmpty() || !ItemStack.matches(menu.getSlot(0).getItem(), expected))
                    throw new IllegalStateException("Expected " + expected + " but got " + menu.getSlot(0).getItem()
                        + "; selected=" + chosen.map(r -> r.getId().toString()).orElse("NONE"));
                var remains = recipe.getRemainingItems(grid);
                var output = menu.getSlot(0).remove(64); menu.getSlot(0).onTake(p, output);
                if (!ItemStack.matches(output, expected)) throw new IllegalStateException("Wrong taken result");
                for (int i = 0; i < 9; i++) if (!ItemStack.matches(menu.getSlot(i + 1).getItem(), remains.get(i)))
                    throw new IllegalStateException("Payment or container remainder mismatch at " + i);
                if (!menu.getSlot(0).getItem().isEmpty()) throw new IllegalStateException("Output replay without payment");
                record(id, "native_crafting_payment", true, "Exact original grid/result/count/remainders; survival player; ingredient fixtures, no acquisition claim");
            } catch (Exception | AssertionError e) { failed++; record(id, "native_crafting_payment", false, e.toString()); }
            finally { p.closeContainer(); p.discard(); }
            checked++;
        }
        h.assertTrue(checked > 500 && failed == 0, "Native recipe transactions checked=" + checked + ", failures=" + failed);
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", batch = "journey", timeoutTicks = 200)
    public static void everyOriginalSmithingUpgradeKeepsOldInvestmentAndPaysNativeSlots(GameTestHelper h) throws Exception {
        int checked = 0, failed = 0;
        for (var element : definitions()) {
            var entry = element.getAsJsonObject(); var data = entry.getAsJsonObject("json");
            if (!data.get("type").getAsString().equals("minecraft:smithing_transform")) continue;
            String id = entry.get("id").getAsString(); var p = player(h);
            try {
                var recipe = (SmithingRecipe) h.getLevel().getRecipeManager().byKey(new ResourceLocation(id)).orElseThrow();
                var base = ingredient(data.get("base"));
                base.getOrCreateTag().putString("JourneyForeignData", "preserve");
                base.getOrCreateTagElement("dynastyWeaponGrowth").putInt("level", 7);
                base.getOrCreateTagElement("dynastyWeaponGrowth").putLong("xp", 19);
                base.enchant(net.minecraft.world.item.enchantment.Enchantments.UNBREAKING, 2);
                var menu = new SmithingMenu(10, p.getInventory(), ContainerLevelAccess.NULL); p.containerMenu = menu;
                menu.getSlot(0).set(ingredient(data.get("template"))); menu.getSlot(1).set(base.copy());
                menu.getSlot(2).set(ingredient(data.get("addition")));
                var expected = recipe.getResultItem(h.getLevel().registryAccess());
                var output = menu.getSlot(3).remove(64); menu.getSlot(3).onTake(p, output);
                if (!output.is(expected.getItem()) || !base.getTag().equals(output.getTag()))
                    throw new IllegalStateException("Original upgrade selected wrong output or lost old NBT: " + output);
                for (int i = 0; i < 4; i++) if (!menu.getSlot(i).getItem().isEmpty())
                    throw new IllegalStateException("Smithing input or output replay at " + i);
                record(id, "native_smithing_payment_and_nbt", true, "Native SmithingMenu, exact three inputs paid, old growth/enchantment/foreign NBT retained");
            } catch (Exception | AssertionError e) { failed++; record(id, "native_smithing_payment_and_nbt", false, e.toString()); }
            finally { p.closeContainer(); p.discard(); }
            checked++;
        }
        h.assertTrue(checked == 47 && failed == 0, "Native smithing checked=" + checked + ", failures=" + failed);
        h.succeed();
    }
}

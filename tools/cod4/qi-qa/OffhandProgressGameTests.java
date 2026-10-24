package com.dynasty.expansion;

import com.dynasty.DynastySlotProgression;
import com.dynasty.DynastyStats;
import com.dynasty.TalismanDiscovery;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Native inventory, advancement, recipe book and NBT; not human old-world/FTB acceptance. */
@GameTestHolder("dynasty_qi_qa")
@PrefixGameTestTemplate(false)
public final class OffhandProgressGameTests {
    private static ServerPlayer player(GameTestHelper h) {
        var p = new ServerPlayer(h.getLevel().getServer(), h.getLevel(),
                new GameProfile(UUID.randomUUID(), "offhand-book"));
        p.connection = new net.minecraft.server.network.ServerGamePacketListenerImpl(
                h.getLevel().getServer(), new net.minecraft.network.Connection(
                net.minecraft.network.protocol.PacketFlow.SERVERBOUND), p);
        return p;
    }

    private static boolean done(ServerPlayer p, String id) {
        var a = p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty", id));
        if (a == null) throw new AssertionError("Missing original advancement: " + id);
        return p.getAdvancements().getOrStartProgress(a).isDone();
    }

    private static ItemStack held(ServerPlayer p, String id) {
        var stack = new ItemStack(ExpansionContent.item(id));
        stack.getOrCreateTag().putString("ForeignData", "preserved");
        p.setItemInHand(InteractionHand.OFF_HAND, stack);
        return stack.copy();
    }

    @GameTest(template = "bow_ritual_test", batch = "offhand_progress")
    public static void offhandOnlyOwnedJadeBackfillsOriginalAdvancementAndRecipesForItsOwner(GameTestHelper h) {
        var p = player(h); var other = player(h);
        try {
            var original = held(p, "jade_pendant");
            h.assertTrue(p.getInventory().items.stream().allMatch(ItemStack::isEmpty), "No main inventory evidence");
            ContentProgress.login(new PlayerEvent.PlayerLoggedInEvent(p));
            h.assertTrue(done(p, "cod4_obtain_jade_pendant"), "Offhand original item backfills original impossible criterion");
            for (String id : new String[]{"jade_bi_disc", "jade_ring"})
                h.assertTrue(p.getRecipeBook().contains(new ResourceLocation("dynasty", id)), "Actual linked recipe discovered: " + id);
            ContentProgress.reconcile(p); ContentProgress.reconcile(p);
            h.assertTrue(ItemStack.isSameItemSameTags(original, p.getOffhandItem()) && p.getOffhandItem().getCount() == 1
                    && p.getInventory().items.stream().allMatch(ItemStack::isEmpty) && p.totalExperience == 0,
                    "Repeated reconciliation preserves stack/NBT and pays no items or XP");
            ContentProgress.reconcile(other);
            h.assertTrue(!done(other, "cod4_obtain_jade_pendant")
                    && !other.getRecipeBook().contains(new ResourceLocation("dynasty", "jade_bi_disc")),
                    "Second player cannot inherit another player's ownership");
            h.succeed();
        } finally { p.discard(); other.discard(); }
    }

    @GameTest(template = "bow_ritual_test", batch = "offhand_progress")
    public static void offhandCrownDoesNotDuplicateExistingRankGiftAndSlotReceiptIsIdempotent(GameTestHelper h) {
        var p = player(h);
        try {
            var original = held(p, "jade_crown");
            DynastyStats.setRank(p, 3);
            ContentProgress.login(new PlayerEvent.PlayerLoggedInEvent(p));
            ContentProgress.reconcile(p); ContentProgress.reconcile(p);
            h.assertTrue(done(p, "cod4_obtain_jade_crown") && DynastySlotProgression.bonusSlots(p) == 1,
                    "Actual held crown awards only its original personal slot once");
            h.assertTrue(p.getInventory().items.stream().allMatch(ItemStack::isEmpty)
                    && ItemStack.isSameItemSameTags(original, p.getOffhandItem()) && p.getOffhandItem().getCount() == 1,
                    "Existing offhand crown must not cause a second rank gift");
            h.assertTrue(EquipmentBehaviors.saved(p).getBoolean("crownGranted"), "Existing rank gift receipt retained");
            h.succeed();
        } finally { p.discard(); }
    }

    @GameTest(template = "bow_ritual_test", batch = "offhand_progress")
    public static void nativeSaveLoadOfOffhandSilkBackfillsOnlyOnePersonalSlot(GameTestHelper h) {
        var p = player(h); var restored = player(h);
        try {
            var original = held(p, "silk_pouch");
            var saved = new CompoundTag(); p.saveWithoutId(saved); restored.load(saved);
            ContentProgress.login(new PlayerEvent.PlayerLoggedInEvent(restored));
            ContentProgress.reconcile(restored);
            h.assertTrue(done(restored, "cod4_obtain_silk_pouch") && DynastySlotProgression.bonusSlots(restored) == 1,
                    "Native player save/load preserves offhand evidence and unlocks original silk slot once");
            h.assertTrue(ItemStack.isSameItemSameTags(original, restored.getOffhandItem())
                    && restored.getOffhandItem().getCount() == 1 && DynastySlotProgression.bonusSlots(p) == 0,
                    "Restored player's receipt and unchanged stack do not leak to source player");
            h.succeed();
        } finally { p.discard(); restored.discard(); }
    }

    @GameTest(template = "bow_ritual_test", batch = "offhand_progress")
    public static void offhandPaperDiscoversSevenRecipesAndConsumablePossessionStillDoesNotCountAsCrafting(GameTestHelper h) {
        var p = player(h);
        try {
            held(p, "talisman_paper");
            ContentProgress.reconcile(p);
            for (String id : TalismanDiscovery.IDS)
                h.assertTrue(p.getRecipeBook().contains(new ResourceLocation("dynasty", id)), "Original paper discovery includes offhand: " + id);
            var supply = ExpansionContent.SUPPLIES.keySet().iterator().next();
            held(p, supply);
            ContentProgress.reconcile(p);
            h.assertTrue(!done(p, "cod4_obtain_" + supply), "Possession is not proof of crafting a consumable");
            h.succeed();
        } finally { p.discard(); }
    }

    @GameTest(template = "bow_ritual_test", batch = "offhand_progress", timeoutTicks = 40)
    public static void everyOriginalObtainNodeDetectsItsActualOffhandItemAndAllSupplyNodesRequireNativeCrafting(GameTestHelper h) throws Exception {
        var stream = OffhandProgressGameTests.class.getResourceAsStream("/dynasty-cod4-node-qa.json");
        if (stream == null) throw new AssertionError("Missing original QA-only node contract");
        int owned = 0, crafted = 0;
        try (var reader = new java.io.InputStreamReader(stream, java.nio.charset.StandardCharsets.UTF_8)) {
            for (var element : com.google.gson.JsonParser.parseReader(reader).getAsJsonArray()) {
                var node = element.getAsJsonObject();
                if (node.get("interaction").getAsBoolean()) continue;
                var p = player(h);
                try {
                    String id = node.get("item").getAsString();
                    String advancement = node.get("advancement").getAsString();
                    var original = held(p, id);
                    ContentProgress.login(new PlayerEvent.PlayerLoggedInEvent(p));
                    if (ExpansionContent.SUPPLIES.containsKey(id)) {
                        crafted++;
                        h.assertTrue(!done(p, advancement), "Supply possession must not complete craft node: " + id);
                        var key = new ResourceLocation("dynasty", "cod4/" + id);
                        var recipe = h.getLevel().getRecipeManager().byKey(key).orElseThrow();
                        h.assertTrue(p.getRecipeBook().contains(key), "Original supply recipe actually discovered: " + id);
                        var menu = new net.minecraft.world.inventory.CraftingMenu(9, p.getInventory(),
                                net.minecraft.world.inventory.ContainerLevelAccess.create(h.getLevel(), p.blockPosition()));
                        p.containerMenu = menu;
                        int slot = 1;
                        for (var ingredient : recipe.getIngredients()) {
                            var input = ingredient.getItems()[0].copy(); input.setCount(1);
                            menu.getSlot(slot++).set(input);
                        }
                        var inputs = new net.minecraft.world.inventory.TransientCraftingContainer(menu, 3, 3);
                        for (int i = 1; i < slot; i++) inputs.setItem(i - 1, menu.getSlot(i).getItem().copy());
                        var remainders = ((net.minecraft.world.item.crafting.CraftingRecipe) recipe).getRemainingItems(inputs);
                        var output = menu.getSlot(0).remove(64);
                        h.assertTrue(output.is(ExpansionContent.item(id)) && !output.isEmpty(), "Original native crafting result: " + id);
                        menu.getSlot(0).onTake(p, output);
                        h.assertTrue(done(p, advancement), "Native ResultSlot must dispatch original crafting progress hook: " + id);
                        for (int i = 1; i < slot; i++)
                            h.assertTrue(ItemStack.matches(menu.getSlot(i).getItem(), remainders.get(i - 1)),
                                    "Native crafting consumes input once and preserves original bottle/bowl remainders: " + id);
                        h.assertTrue(menu.getSlot(0).getItem().isEmpty(), "Empty grid cannot replay supply output: " + id);
                    } else {
                        owned++;
                        h.assertTrue(done(p, advancement), "Every original obtain node accepts its exact native offhand stack: " + id);
                    }
                    ContentProgress.reconcile(p); ContentProgress.reconcile(p);
                    h.assertTrue(done(p, advancement) && ItemStack.isSameItemSameTags(original, p.getOffhandItem())
                            && p.getOffhandItem().getCount() == original.getCount(), "No completion reset or offhand payment/replacement: " + id);
                    if (net.minecraftforge.fml.ModList.get().isLoaded("ftbquests")) nativeFtbObjective(h, p, node);
                    p.closeContainer();
                } finally { p.discard(); }
            }
        }
        h.assertTrue(owned == 23 && crafted == 8, "All 31 original obtain/craft nodes covered, including all eight supplies");
        h.succeed();
    }

    private static void nativeFtbObjective(GameTestHelper h, ServerPlayer p, com.google.gson.JsonObject node) throws Exception {
        // Native offline team registration for detached QA players, not a network-player claim.
        com.dynasty.FtbRewardGameTests.FixtureTeams.player(new PlayerEvent.PlayerLoggedInEvent(p));
        var fileType = Class.forName("dev.ftb.mods.ftbquests.quest.ServerQuestFile");
        var taskType = Class.forName("dev.ftb.mods.ftbquests.quest.task.Task");
        var teamType = Class.forName("dev.ftb.mods.ftbquests.quest.TeamData");
        var objectType = Class.forName("dev.ftb.mods.ftbquests.quest.QuestObject");
        var baseType = Class.forName("dev.ftb.mods.ftbquests.quest.BaseQuestFile");
        Object file = fileType.getField("INSTANCE").get(null);
        Object quest = fileType.getMethod("getQuest", long.class).invoke(file, Long.parseLong(node.get("id").getAsString(), 16));
        Object task = fileType.getMethod("getTask", long.class).invoke(file, Long.parseLong(node.get("task").getAsString(), 16));
        Object team = fileType.getMethod("getOrCreateTeamData", net.minecraft.world.entity.Entity.class).invoke(file, p);
        h.assertTrue(quest != null && task != null && taskType.getMethod("getQuest").invoke(task) == quest,
                "Exact original FTB task and quest identities loaded: " + node.get("item"));
        h.assertTrue((Boolean) task.getClass().getMethod("canSubmit", teamType, ServerPlayer.class).invoke(task, team, p),
                "Real FTB advancement detector sees actual owned/crafted progress: " + node.get("item"));
        boolean ready = (Boolean) teamType.getMethod("areDependenciesComplete", quest.getClass()).invoke(team, quest);
        taskType.getMethod("submitTask", teamType, ServerPlayer.class).invoke(task, team, p);
        var progress = teamType.getMethod("getProgress", taskType);
        var complete = teamType.getMethod("isCompleted", objectType);
        if (!ready) {
            h.assertTrue((Long) progress.invoke(team, task) == 1 && !(Boolean) complete.invoke(team, quest),
                    "Native FTB keeps actual detected progress while correctly withholding locked quest completion");
            teamType.getMethod("resetProgress", taskType).invoke(team, task);
            preparePrerequisites(quest, team);
            taskType.getMethod("submitTask", teamType, ServerPlayer.class).invoke(task, team, p);
        }
        h.assertTrue((Long) progress.invoke(team, task) == 1 && (Boolean) complete.invoke(team, quest),
                "Original FTB objective and quest actually complete: " + node.get("item"));
        Object saved = teamType.getMethod("serializeNBT").invoke(team);
        Object restored = teamType.getConstructor(UUID.class, baseType).newInstance(teamType.getMethod("getTeamId").invoke(team), file);
        teamType.getMethod("deserializeNBT", saved.getClass()).invoke(restored, saved);
        h.assertTrue((Long) progress.invoke(restored, task) == 1 && (Boolean) complete.invoke(restored, quest),
                "Native TeamData save/load retains each original objective: " + node.get("item"));
    }

    /** QA fixture only: model previously completed prerequisites, never mark the tested node. */
    public static void preparePrerequisites(Object quest, Object team) throws ReflectiveOperationException {
        var teamType = Class.forName("dev.ftb.mods.ftbquests.quest.TeamData");
        var objectType = Class.forName("dev.ftb.mods.ftbquests.quest.QuestObject");
        try (var deps = (java.util.stream.Stream<?>) quest.getClass().getMethod("streamDependencies").invoke(quest)) {
            for (Object dependency : deps.toList()) {
                long id = objectType.getField("id").getLong(dependency);
                teamType.getMethod("setCompleted", long.class, java.util.Date.class).invoke(team, id, new java.util.Date());
            }
        }
        teamType.getMethod("clearCachedProgress").invoke(team);
        hAssert((Boolean) teamType.getMethod("areDependenciesComplete", quest.getClass()).invoke(team, quest),
                "Native prerequisite fixture is complete before testing unlocked submission");
    }

    private static void hAssert(boolean result, String message) {
        if (!result) throw new AssertionError(message);
    }
}

package com.dynasty.cod3;

import com.dynasty.DynastyBossCombat;
import com.dynasty.entity.DynastyEntities;
import com.google.gson.JsonObject;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.gametest.*;
import java.util.ArrayList;
import java.util.List;

@GameTestHolder("dynasty_cod3")
@PrefixGameTestTemplate(false)
public final class Cod3SequenceGameTests {
    @GameTest(template="bow_ritual_test")
    public static void sequenceTypesAndParametersRoundTrip(GameTestHelper h) {
        var params = new JsonObject();
        params.addProperty("visible", false);
        params.addProperty("phase", 2);
        params.addProperty("sound", "minecraft:block.beacon.activate");
        var origin = new com.google.gson.JsonArray(); origin.add(1); origin.add(2); origin.add(3);
        params.add("origin", origin);
        var steps = new ArrayList<BossSequenceDefinition.Step>();
        for (var type : BossSequenceDefinition.Type.values())
            steps.add(new BossSequenceDefinition.Step(0, 20, type, 1, 3, "", params));
        var def = new BossSequenceDefinition("test_sequence", "Test", 40, "dynasty:test", List.of(), steps);
        params.addProperty("phase", 99);
        var copy = BossSequenceDefinition.fromJson(def.toJson());
        h.assertTrue(copy.equals(def) && copy.steps().size() == 17, "Step types/parameters did not round trip");
        var returned = copy.steps().get(0).params(); returned.addProperty("phase", 77);
        h.assertTrue(copy.steps().get(0).params().get("phase").getAsInt() == 2, "Parameter mutation escaped the definition");
        for (String group : List.of("intros", "deaths")) for (var row : Cod3Catalog.entries(group)) {
            var legacy = BossSequenceDefinition.fromJson(row.toString());
            h.assertTrue(legacy.equals(BossSequenceDefinition.fromJson(legacy.toJson())), "Legacy catalogue changed on round trip");
            h.assertTrue(legacy.steps().stream().allMatch(s -> s.params().size() == 0), "Legacy params should default to empty");
        }
        h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void malformedSequenceDefinitionsAreRejected(GameTestHelper h) {
        String base = "{\"id\":\"test\",\"name\":\"Test\",\"totalTicks\":40,\"arenaTag\":\"dynasty:test\",\"bossIds\":[],\"steps\":[%s]}";
        for (String step : List.of(
                "{\"startTick\":0,\"duration\":10,\"type\":\"UNKNOWN\"}",
                "{\"startTick\":-1,\"duration\":10,\"type\":\"WAIT\"}",
                "{\"startTick\":39,\"duration\":2,\"type\":\"WAIT\"}",
                "{\"startTick\":0,\"duration\":10,\"type\":\"SPAWN_CLIENT_VFX\",\"vfx\":0,\"radius\":3}",
                "{\"startTick\":0,\"duration\":10,\"type\":\"SPAWN_CLIENT_VFX\",\"vfx\":1,\"radius\":1e999}")) {
            boolean rejected = false;
            try { BossSequenceDefinition.fromJson(base.formatted(step)); } catch (RuntimeException expected) { rejected = true; }
            h.assertTrue(rejected, "Malformed definition was accepted: " + step);
        }
        h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void lateSnapshotSelectsOnlyLiveVfxAndPreservesClock(GameTestHelper h) {
        var def = new BossSequenceDefinition("intro_test", "Test", 100, "dynasty:test", List.of(), List.of(
                new BossSequenceDefinition.Step(0, 40, BossSequenceDefinition.Type.WAIT, 0, 0, ""),
                new BossSequenceDefinition.Step(0, 40, BossSequenceDefinition.Type.PLAY_SOUND, 0, 0, ""),
                new BossSequenceDefinition.Step(0, 40, BossSequenceDefinition.Type.SET_BOSS_VISIBILITY, 0, 0, ""),
                new BossSequenceDefinition.Step(0, 10, BossSequenceDefinition.Type.SPAWN_CLIENT_VFX, 1, 3, ""),
                new BossSequenceDefinition.Step(10, 40, BossSequenceDefinition.Type.SPAWN_CLIENT_VFX, 2, 6, ""),
                new BossSequenceDefinition.Step(40, 40, BossSequenceDefinition.Type.SPAWN_CLIENT_VFX, 3, 3, "")));
        var snapshot = snapshot(def.id(), 25, 100);
        var active = Cod3Vfx.resume(snapshot, def);
        h.assertTrue(active.size() == 1 && active.get(0).template() == 2, "Replayed elapsed/future/non-visual steps");
        var p = active.get(0);
        h.assertTrue(p.start() == 1010 && p.seed() == 60 && p.duration() == 40 && p.scale() == 2 && p.tint() == 0x123456,
                "Late join restarted the clock or lost visual parameters");
        h.assertTrue(Cod3Vfx.resume(snapshot(def.id(), 50, 100), def).stream().noneMatch(x -> x.template() == 2), "Expired boundary was replayed");
        h.assertTrue(Cod3Vfx.resume(snapshot(def.id(), 100, 100), def).isEmpty(), "Finished sequence replayed");
        h.assertTrue(Cod3Vfx.resume(snapshot("intro_other", 25, 100), def).isEmpty(), "Wrong sequence was accepted");
        h.assertTrue(!snapshot(def.id(), -1, 100).valid(), "Negative snapshot tick accepted");
        h.succeed();
    }
    private static Cod3VisualPacket snapshot(String sequence, int tick, int duration) {
        return new Cod3VisualPacket("minecraft:overworld", 0, 42, 50, 1000, duration, 1, Vec3.ZERO,
                new Vec3(0, 0, 1), sequence, tick, 0x123456);
    }

    @GameTest(template="bow_ritual_test")
    public static void corruptCheckpointsAlwaysReleaseTheBoss(GameTestHelper h) {
        for (String damage : List.of("negativeTick", "overflowTick", "negativeWatchdog", "overflowWatchdog", "badPreview", "wrongId", "missingTick", "wrongTag")) {
            var boss = DynastyEntities.DRAGON_KING.get().create(h.getLevel());
            h.assertTrue(BossSequenceRunner.start(boss, 20), "Intro did not start");
            var n = boss.getPersistentData().getCompound(BossSequenceRunner.KEY);
            switch (damage) {
                case "negativeTick" -> n.putInt("Tick", -1);
                case "overflowTick" -> n.putInt("Tick", Integer.MAX_VALUE);
                case "negativeWatchdog" -> n.putInt("Watchdog", -1);
                case "overflowWatchdog" -> n.putInt("Watchdog", Integer.MAX_VALUE);
                case "badPreview" -> n.putInt("Preview", Integer.MAX_VALUE);
                case "wrongId" -> n.putString("Id", "intro_missing");
                case "missingTick" -> n.remove("Tick");
                case "wrongTag" -> boss.getPersistentData().putString(BossSequenceRunner.KEY, "broken");
            }
            BossSequenceRunner.tick(boss);
            h.assertTrue(!BossSequenceRunner.active(boss) && !boss.isNoAi() && !boss.isInvulnerable() && !boss.isInvisible(),
                    "Corrupt save left boss locked: " + damage);
            h.assertTrue(((DynastyBossCombat.BarHolder) boss).dynastyBossBar().isVisible(), "Fallback hid the bar");
        }
        h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void previewAndReloadDoNotRestartOrUnlockIntro(GameTestHelper h) {
        var boss = DynastyEntities.DRAGON_KING.get().create(h.getLevel());
        BossSequenceRunner.start(boss, 20);
        for (int i = 0; i < 20; i++) BossSequenceRunner.tick(boss);
        var state = boss.getPersistentData().getCompound(BossSequenceRunner.KEY);
        h.assertTrue(state.getInt("Tick") == 0 && state.getInt("Preview") == 0 && state.getInt("Watchdog") == 20,
                "Preview advanced the sequence or bypassed watchdog");
        BossSequenceRunner.tick(boss);
        var hidden = new JsonObject(); hidden.addProperty("visible", false);
        BossSequenceRunner.play(boss, new BossSequenceDefinition.Step(0, 1, BossSequenceDefinition.Type.SET_BOSS_VISIBILITY, 0, 0, "", hidden));
        BossSequenceRunner.tick(boss);
        h.assertTrue(boss.isInvisible(), "Next tick undid authored visibility");
        var copy = DynastyEntities.DRAGON_KING.get().create(h.getLevel());
        copy.load(boss.saveWithoutId(new CompoundTag()));
        copy.setNoAi(false); copy.setInvulnerable(false);
        BossSequenceRunner.join(new EntityJoinLevelEvent(copy, h.getLevel()));
        h.assertTrue(copy.isNoAi() && copy.isInvulnerable() && copy.isInvisible(), "Join failed to restore intro invariants");
        BossSequenceRunner.tick(copy);
        h.assertTrue(copy.getPersistentData().getCompound(BossSequenceRunner.KEY).getInt("Tick") == 3, "Reload replayed the beginning");
        h.assertTrue(!BossSequenceRunner.start(copy), "Reload allowed duplicate intro");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void introEndsOnTheAuthoredTick(GameTestHelper h) {
        var boss = DynastyEntities.DRAGON_KING.get().create(h.getLevel());
        BossSequenceRunner.start(boss);
        var def = Cod3Catalog.sequence("intros", "dynasty:dragon_king");
        var state = boss.getPersistentData().getCompound(BossSequenceRunner.KEY);
        state.putInt("Tick", def.totalTicks()-1);
        boss.getPersistentData().putString("dynasty_cod3_visual_stage", "STONE");
        BossSequenceRunner.tick(boss);
        h.assertTrue(!BossSequenceRunner.active(boss) && !boss.isNoAi() && !boss.isInvulnerable() && !boss.isInvisible(), "Combat unlocked a tick late");
        h.assertTrue(!boss.getPersistentData().contains("dynasty_cod3_visual_stage"), "Intro variant leaked into combat");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void deathWhitelistCannotUnlockCombat(GameTestHelper h) {
        var boss = DynastyEntities.REBEL_GENERAL.get().create(h.getLevel());
        BossSequenceRunner.start(boss);
        boss.getPersistentData().putBoolean(BossDeathState.KEY, true);
        boss.setInvulnerable(true);
        var params = new JsonObject(); params.addProperty("invulnerable", false); params.addProperty("visible", true);
        for (var type : List.of(BossSequenceDefinition.Type.SET_BOSS_INVULNERABLE, BossSequenceDefinition.Type.SHOW_BOSSBAR,
                BossSequenceDefinition.Type.SET_BOSS_PHASE, BossSequenceDefinition.Type.TRIGGER_WORLD_STATE)) {
            var step = new BossSequenceDefinition.Step(0, 1, type, 0, 0, "", params);
            h.assertTrue(!step.allowedDuringDeath(), "Unsafe death step accepted");
            BossSequenceRunner.play(boss, step);
        }
        BossSequenceRunner.tick(boss);
        h.assertTrue(boss.isInvulnerable() && boss.isNoAi() && !((DynastyBossCombat.BarHolder)boss).dynastyBossBar().isVisible(), "Death was unlocked by intro steps");
        h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void permanentRemainsRetainPartialLootAcrossReload(GameTestHelper h) {
        var pos = new BlockPos(2, 2, 2);
        h.setBlock(pos, LootableRemains.BLOCK.get());
        var remains = (LootableRemains.Remains) h.getBlockEntity(pos);
        remains.setItem(0, new ItemStack(Items.DIAMOND, 7));
        h.assertTrue(remains.removeItem(0, 3).getCount() == 3, "Could not claim remains");
        var copy = new LootableRemains.Remains(remains.getBlockPos(), remains.getBlockState());
        copy.load(remains.saveWithoutMetadata());
        h.assertTrue(copy.getItem(0).getCount() == 4, "Saved partial loot duplicated or vanished");
        h.assertTrue(copy.removeItem(0, 64).getCount() == 4 && copy.removeItem(0, 1).isEmpty(), "Claimed loot was issued twice");
        h.assertTrue(!copy.canPlaceItem(0, new ItemStack(Items.DIRT)), "Loot-only slot allowed insertion");
        h.succeed();
    }
}

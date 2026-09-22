package com.dynasty.entity;

import com.dynasty.Dynasty;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.UUID;

@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class ImperialSoldierGameTests {
    private static ImperialSoldier soldier(GameTestHelper h, MobSpawnType reason) {
        var soldier = DynastyEntities.IMPERIAL_SOLDIER.get().create(h.getLevel());
        // Exercise the same saved Forge provenance used by legacy-world migration.
        var tag = new CompoundTag();
        if (reason != null) tag.putString("forge:spawn_type", reason.name());
        soldier.readAdditionalSaveData(tag);
        soldier.setNoAi(true);
        soldier.setNoGravity(true);
        var pos = h.absolutePos(new BlockPos(3, 2, 3));
        soldier.setPos(pos.getX() + .5, pos.getY(), pos.getZ() + .5);
        return soldier;
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void onlyUnprotectedWildPatrolsCanDespawn(GameTestHelper h) {
        for (var reason : MobSpawnType.values()) {
            var soldier = soldier(h, reason);
            boolean natural = reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION;
            h.assertTrue(soldier.removeWhenFarAway(200 * 200) == natural, "Incorrect despawn eligibility: " + reason);
            soldier.setCustomName(Component.literal("My guard"));
            h.assertTrue(!soldier.removeWhenFarAway(200 * 200), "Named guard must survive");
        }
        h.assertTrue(!soldier(h, null).removeWhenFarAway(200 * 200), "Unknown old command/army origin must be preserved");
        var persistent = soldier(h, MobSpawnType.NATURAL);
        persistent.setPersistenceRequired();
        h.assertTrue(!persistent.removeWhenFarAway(200 * 200), "Persistent wild guard must survive");
        var savedLeash = new CompoundTag();
        savedLeash.putString("forge:spawn_type", "NATURAL");
        var leash = new CompoundTag(); leash.putUUID("UUID", UUID.randomUUID());
        savedLeash.put("Leash", leash);
        var leashed = soldier(h, null); leashed.readAdditionalSaveData(savedLeash);
        h.assertTrue(!leashed.isLeashed(), "Test must cover the pre-restoration join phase");
        h.assertTrue(!leashed.removeWhenFarAway(0) && leashed.requiresCustomPersistence(),
                "Unresolved saved leash must protect a guard before tickLeash restores its holder");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void armyOwnershipSurvivesSaveAndOfflinePlayer(GameTestHelper h) {
        var owner = new FakePlayer(h.getLevel(), new GameProfile(UUID.randomUUID(), "patrol-owner"));
        h.getLevel().addNewPlayer(owner);
        try {
            var original = soldier(h, MobSpawnType.NATURAL);
            original.setOwner(owner);
            var saved = new CompoundTag();
            original.addAdditionalSaveData(saved);
            var loaded = soldier(h, null);
            loaded.readAdditionalSaveData(saved);
            h.assertTrue(loaded.getOwner() == owner, "Owner UUID must resolve after reload");
            h.assertTrue(!loaded.removeWhenFarAway(200 * 200), "Owned guard must not despawn");
            owner.discard();
            h.assertTrue(loaded.requiresCustomPersistence(), "Offline owner must still protect army");
            h.assertTrue(!loaded.removeWhenFarAway(200 * 200), "Logout must not erase ownership");
        } finally { owner.discard(); }
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void naturalSpawnHasGroundAndLocalCap(GameTestHelper h) {
        h.setBlock(new BlockPos(3, 1, 3), Blocks.STONE);
        var candidate = soldier(h, null);
        h.assertTrue(candidate.getType().getCategory() == MobCategory.CREATURE, "Soldier must use creature cap");
        h.assertTrue(candidate.checkSpawnRules(h.getLevel(), MobSpawnType.NATURAL), "One patrol may spawn on ground");
        h.assertTrue(!candidate.checkSpawnRules(h.getLevel(), MobSpawnType.CHUNK_GENERATION), "WorldGenRegion cannot enforce a live cap; patrols must wait for natural spawning");
        var spawned = new java.util.ArrayList<ImperialSoldier>();
        try {
            for (int i = 0; i < ImperialSoldier.NATURAL_LOCAL_LIMIT; i++) {
                var guard = soldier(h, MobSpawnType.NATURAL);
                h.getLevel().addFreshEntity(guard);
                spawned.add(guard);
            }
            h.assertTrue(!candidate.checkSpawnRules(h.getLevel(), MobSpawnType.NATURAL), "Crowded natural spawn must be rejected");
            h.assertTrue(!candidate.checkSpawnRules(h.getLevel(), MobSpawnType.CHUNK_GENERATION), "Chunk-generation patrol must obey same cap");
            h.assertTrue(!ImperialPatrolPopulation.admitLoadedPatrol(h.getLevel(), soldier(h, MobSpawnType.NATURAL)),
                    "Old disk-loaded surplus must be rejected before AI and rendering start");
            h.assertTrue(ImperialPatrolPopulation.admitLoadedPatrol(h.getLevel(), soldier(h, null)),
                    "Unknown old army must load even in an overpopulated area");
            var named = soldier(h, MobSpawnType.NATURAL);
            named.setCustomName(Component.literal("Old named patrol"));
            h.assertTrue(ImperialPatrolPopulation.admitLoadedPatrol(h.getLevel(), named), "Named patrols must always load");
            h.assertTrue(candidate.checkSpawnRules(h.getLevel(), MobSpawnType.SPAWN_EGG), "Egg/army workflows must remain available");
            h.assertTrue(candidate.getMaxSpawnClusterSize() == 1, "Patrols spawn singly");
        } finally { spawned.forEach(ImperialSoldier::discard); }
        h.setBlock(new BlockPos(3, 1, 3), Blocks.AIR);
        h.assertTrue(!candidate.checkSpawnRules(h.getLevel(), MobSpawnType.NATURAL), "Natural patrol must not spawn in mid-air");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void oldCrowdingRecoversGraduallyWithoutTouchingArmies(GameTestHelper h) {
        var entities = new java.util.ArrayList<net.minecraft.world.entity.Entity>();
        for (int i = 0; i < ImperialPatrolPopulation.MAX_DESPAWNS_PER_PASS + 13; i++)
            entities.add(soldier(h, MobSpawnType.NATURAL));
        var oldArmy = soldier(h, null);
        var named = soldier(h, MobSpawnType.NATURAL);
        named.setCustomName(Component.literal("Keep me"));
        var owned = soldier(h, MobSpawnType.NATURAL);
        owned.setOwner(new FakePlayer(h.getLevel(), new GameProfile(UUID.randomUUID(), "offline-owner")));
        entities.add(oldArmy); entities.add(named); entities.add(owned);
        h.assertTrue(ImperialPatrolPopulation.reduceCrowding(entities) == ImperialPatrolPopulation.MAX_DESPAWNS_PER_PASS,
                "Cleanup must be bounded per pass");
        h.assertTrue(ImperialPatrolPopulation.reduceCrowding(entities) == 9, "Second pass must retain four natural patrols");
        h.assertTrue(ImperialPatrolPopulation.reduceCrowding(entities) == 0, "Stable population must not keep disappearing");
        h.assertTrue(!oldArmy.isRemoved() && !named.isRemoved() && !owned.isRemoved(), "Old armies, names and offline owners are protected");
        h.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void loadedBiomesUseCreatureNotMonsterPopulation(GameTestHelper h) {
        var registry = h.getLevel().registryAccess().registryOrThrow(net.minecraft.core.registries.Registries.BIOME);
        for (String id : new String[]{"celestial_plains", "jade_forest", "dragon_ridge", "underworld_wastes",
                "soul_river", "jiuxiao_skyland", "dragon_palace_hall"}) {
            var biome = registry.get(new net.minecraft.resources.ResourceLocation(Dynasty.MODID, id));
            var spawns = biome.getMobSettings();
            h.assertTrue(spawns.getMobs(MobCategory.MONSTER).unwrap().stream()
                    .noneMatch(s -> s.type == DynastyEntities.IMPERIAL_SOLDIER.get()), "Soldier leaked into monster cap: " + id);
            var patrols = spawns.getMobs(MobCategory.CREATURE).unwrap().stream()
                    .filter(s -> s.type == DynastyEntities.IMPERIAL_SOLDIER.get()).toList();
            h.assertTrue(patrols.size() == 1 && patrols.get(0).minCount == 1 && patrols.get(0).maxCount == 1,
                    "Missing or duplicate low-density patrol after resource loading: " + id);
        }
        h.succeed();
    }
}

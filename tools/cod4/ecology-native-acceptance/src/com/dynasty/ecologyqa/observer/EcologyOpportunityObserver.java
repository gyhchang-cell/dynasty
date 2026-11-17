package com.dynasty.ecologyqa.observer;

import com.google.gson.Gson;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.EntityLeaveLevelEvent;
import net.minecraftforge.event.entity.item.ItemExpireEvent;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.event.entity.living.MobSpawnEvent;
import net.minecraftforge.event.entity.player.EntityItemPickupEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStartedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Opt-in passive QA diagnostics. Never spawns, attacks, moves, deletes or supplies anything. */
public final class EcologyOpportunityObserver {
    private static final boolean ENABLED = Boolean.getBoolean("ecology.bounded.observe");
    private static final Set<UUID> PENDING_NATURAL = new HashSet<>();
    private static final Map<UUID, String[]> SPAWN_STACKS = new LinkedHashMap<>();
    private static final Set<UUID> NATURAL = new HashSet<>();
    private static final Set<UUID> TRACKED_LOOT = new HashSet<>();
    private static MinecraftServer server;
    private static Path output;
    private static long ticks, startedNanos;
    private static boolean budgetExceeded;
    private static final Map<String, Integer> CREATURE_PLACEMENT_CHECKS = new LinkedHashMap<>();
    private static int placementSamples;

    private static Map<String, Object> row(Object... pairs) {
        var result = new LinkedHashMap<String, Object>();
        for (int i = 0; i < pairs.length; i += 2) result.put(pairs[i].toString(), pairs[i + 1]);
        return result;
    }

    private static void record(String kind, Object... pairs) {
        if (!ENABLED || output == null) return;
        var value = row(pairs);
        value.put("kind", kind);
        value.put("observer_ticks", ticks);
        if (server != null) value.put("overworld_game_tick", server.overworld().getGameTime());
        try {
            Files.writeString(output.resolve("observer.jsonl"), new Gson().toJson(value) + "\n",
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
        } catch (Exception failure) {
            throw new IllegalStateException("Cannot preserve ecology observer evidence", failure);
        }
    }

    @SubscribeEvent
    public static void started(ServerStartedEvent event) throws Exception {
        if (!ENABLED) return;
        String target = System.getProperty("ecology.bounded.output");
        if (target == null || target.isBlank()) throw new IllegalArgumentException("Explicit fresh QA output required");
        output = Path.of(target);
        Files.createDirectory(output); // Existing evidence must never be silently appended or replaced.
        server = event.getServer();
        startedNanos = System.nanoTime();
        record("observer_started", "mutates_world", false, "controls_game_process", false,
                "budget_policy", "Writes stop request; external private-run controller must enforce it.");
    }

    private static Map<String, Object> inventory(ServerPlayer player) {
        var slots = new ArrayList<Object>();
        int empty = 0;
        for (int i = 0; i < player.getInventory().items.size(); i++) {
            var stack = player.getInventory().items.get(i);
            if (stack.isEmpty()) empty++;
            else slots.add(row("slot", i, "stack", stack.save(new CompoundTag()).toString()));
        }
        return row("player", player.getUUID().toString(), "dimension", player.level().dimension().location().toString(),
                "spectator", player.isSpectator(), "empty_main_slots", empty, "occupied", slots);
    }

    private static Map<String, Object> loot(ItemEntity item) {
        CompoundTag tag = item.saveWithoutId(new CompoundTag());
        return row("uuid", item.getUUID().toString(), "dimension", item.level().dimension().location().toString(),
                "position", item.position().toString(), "alive", item.isAlive(), "age", item.getAge(),
                "pickup_delay", tag.getShort("PickupDelay"), "owner", tag.contains("Owner") ? tag.getUUID("Owner").toString() : null,
                "stack", item.getItem().save(new CompoundTag()).toString());
    }

    private static void snapshot(ServerLevel level) {
        var state = level.getChunkSource().getLastSpawnState();
        int chunks = state == null ? 0 : state.getSpawnableChunkCount();
        int count = state == null ? 0 : state.getMobCategoryCounts().getInt(MobCategory.CREATURE);
        int cap = MobCategory.CREATURE.getMaxInstancesPerChunk() * chunks / 289;
        var players = level.players().stream().map(EcologyOpportunityObserver::inventory).toList();
        record("creature_cap_snapshot", "dimension", level.dimension().location().toString(),
                "game_tick", level.getGameTime(), "day_time", level.getDayTime(), "night", level.isNight(),
                "has_native_spawn_state", state != null, "spawnable_chunks", chunks,
                "native_creature_count", count, "calculated_global_cap", cap,
                "calculated_global_cap_open", state != null && count < cap,
                "calculated_tick_divisible_by_400", level.getGameTime() % 400 == 0,
                "local_counts", localCounts(state),
                "actual_spawn_attempt_observed", false, "players", players);
        for (UUID id : TRACKED_LOOT) {
            if (level.getEntity(id) instanceof ItemEntity item) record("tracked_loot_state", "loot", loot(item));
        }
    }

    /** Read existing native counters only: do not call canSpawn (which populates caches). */
    private static Map<String, Object> localCounts(Object state) {
        if (state == null) return row("observed", false, "reason", "no native spawn state");
        try {
            Object calculator = null;
            for (var field : state.getClass().getDeclaredFields()) {
                if (field.getType() != net.minecraft.world.level.LocalMobCapCalculator.class) continue;
                field.setAccessible(true); calculator = field.get(state); break;
            }
            if (calculator == null) return row("observed", false, "reason", "calculator unavailable");
            Map<?, ?> existing = null;
            for (var field : calculator.getClass().getDeclaredFields()) {
                if (field.getType() != Map.class) continue;
                field.setAccessible(true); existing = (Map<?, ?>) field.get(calculator); break;
            }
            if (existing == null) return row("observed", false, "reason", "native player counter map unavailable");
            var counters = new ArrayList<Object>();
            for (var entry : existing.entrySet()) {
                if (!(entry.getKey() instanceof ServerPlayer player)) continue;
                for (var field : entry.getValue().getClass().getDeclaredFields()) {
                    if (!it.unimi.dsi.fastutil.objects.Object2IntMap.class.isAssignableFrom(field.getType())) continue;
                    field.setAccessible(true);
                    var values = (it.unimi.dsi.fastutil.objects.Object2IntMap<?>) field.get(entry.getValue());
                    counters.add(row("player", player.getUUID().toString(), "native_creature_count", values.getInt(MobCategory.CREATURE),
                            "per_player_creature_limit", MobCategory.CREATURE.getMaxInstancesPerChunk()));
                }
            }
            return row("observed", true, "existing_player_counters", counters,
                    "scope", "Existing counter entries only; absence is not proof of chunk proximity or a native spawn attempt. No counters or caches modified.");
        } catch (ReflectiveOperationException | RuntimeException failure) {
            return row("observed", false, "reason", failure.toString());
        }
    }

    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) throws Exception {
        if (!ENABLED || server == null || budgetExceeded || event.phase != TickEvent.Phase.END) return;
        ticks++;
        if (ticks == 1 || ticks % 200 == 0) {
            for (var level : server.getAllLevels()) snapshot(level);
            record("native_creature_placement_check_window", "checks", new LinkedHashMap<>(CREATURE_PLACEMENT_CHECKS),
                    "scope", "Native NATURAL placement-check events only, not successful births or a count of all earlier spawn gates.");
            CREATURE_PLACEMENT_CHECKS.clear(); placementSamples = 0;
        }
        if (ticks >= 4600 || System.nanoTime() - startedNanos >= 300_000_000_000L) {
            budgetExceeded = true;
            record("observer_budget_exhausted", "stop_requested", true);
            Files.writeString(output.resolve("bounded-stop-request.txt"), "Budget exhausted; save and stop only this private QA session.\n",
                    StandardOpenOption.CREATE_NEW);
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void placementCheck(MobSpawnEvent.SpawnPlacementCheck event) {
        if (!ENABLED || server == null || budgetExceeded || event.getSpawnType() != MobSpawnType.NATURAL
                || event.getEntityType().getCategory() != MobCategory.CREATURE) return;
        var stack = Arrays.stream(Thread.currentThread().getStackTrace()).map(Object::toString)
                .filter(line -> line.contains("NaturalSpawner")).toArray(String[]::new);
        if (stack.length == 0) return;
        String species = String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(event.getEntityType()));
        String key = event.getLevel().getLevel().dimension().location() + "/" + species
                + "/default=" + event.getDefaultResult() + "/result_at_lowest=" + event.getResult();
        CREATURE_PLACEMENT_CHECKS.merge(key, 1, Integer::sum);
        if (placementSamples++ < 20) record("native_creature_placement_check_sample", "species", species,
                "dimension", event.getLevel().getLevel().dimension().location().toString(), "position", event.getPos().toShortString(),
                "default_result", event.getDefaultResult(), "result_at_observation", event.getResult().toString(),
                "native_spawner_stack", stack, "does_not_prove_birth", true);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void finalizeSpawn(MobSpawnEvent.FinalizeSpawn event) {
        if (ENABLED && server != null && event.getSpawnType() == MobSpawnType.NATURAL) {
            PENDING_NATURAL.add(event.getEntity().getUUID());
            SPAWN_STACKS.put(event.getEntity().getUUID(), Arrays.stream(Thread.currentThread().getStackTrace())
                    .map(Object::toString).filter(line -> line.contains("NaturalSpawner")).toArray(String[]::new));
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void join(EntityJoinLevelEvent event) {
        if (!ENABLED || server == null || event.getLevel().isClientSide() || event.isCanceled()) return;
        UUID id = event.getEntity().getUUID();
        if (PENDING_NATURAL.remove(id) && !event.loadedFromDisk()) {
            var stack = SPAWN_STACKS.remove(id);
            boolean actualSpawner = stack != null && stack.length > 0;
            if (actualSpawner) NATURAL.add(id);
            record("fresh_declared_natural_join", "native_spawner_stack_observed", actualSpawner, "native_spawner_stack", stack,
                    "uuid", id.toString(), "species", ForgeRegistries.ENTITY_TYPES.getKey(event.getEntity().getType()).toString(),
                    "dimension", event.getLevel().dimension().location().toString(), "game_tick", event.getLevel().getGameTime());
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void drops(LivingDropsEvent event) {
        if (!ENABLED || server == null || event.isCanceled()) return;
        for (var item : event.getDrops()) {
            var key = ForgeRegistries.ITEMS.getKey(item.getItem().getItem());
            if (key == null || !key.getNamespace().equals("dynasty") || !key.getPath().equals("lantern_oil")) continue;
            TRACKED_LOOT.add(item.getUUID());
            record("lantern_oil_drop", "source_mob", event.getEntity().getUUID().toString(),
                    "fresh_natural_provenance_observed", NATURAL.contains(event.getEntity().getUUID()),
                    "loot", loot(item), "source_player", event.getSource().getEntity() instanceof ServerPlayer p ? inventory(p) : null);
        }
    }

    @SubscribeEvent(priority = EventPriority.LOWEST, receiveCanceled = true)
    public static void pickupAttempt(EntityItemPickupEvent event) {
        if (!ENABLED || !TRACKED_LOOT.contains(event.getItem().getUUID())) return;
        record("pickup_attempt_observed_at_lowest", "canceled_at_observation", event.isCanceled(), "result_at_observation", event.getResult().toString(),
                "loot", loot(event.getItem()), "inventory", event.getEntity() instanceof ServerPlayer p ? inventory(p) : null);
    }

    @SubscribeEvent
    public static void pickedUp(PlayerEvent.ItemPickupEvent event) {
        if (!ENABLED || !TRACKED_LOOT.contains(event.getOriginalEntity().getUUID())) return;
        record("native_pickup_receipt", "loot_uuid", event.getOriginalEntity().getUUID().toString(),
                "player", event.getEntity().getUUID().toString(), "stack", event.getStack().save(new CompoundTag()).toString());
    }

    @SubscribeEvent(priority = EventPriority.LOWEST, receiveCanceled = true)
    public static void expired(ItemExpireEvent event) {
        if (ENABLED && TRACKED_LOOT.contains(event.getEntity().getUUID()))
            record("item_expire_observed_at_lowest", "canceled_at_observation", event.isCanceled(), "loot", loot(event.getEntity()));
    }

    @SubscribeEvent
    public static void left(EntityLeaveLevelEvent event) {
        if (ENABLED && TRACKED_LOOT.contains(event.getEntity().getUUID()))
            record("tracked_loot_left_level", "uuid", event.getEntity().getUUID().toString(),
                    "removal_reason_at_observation", String.valueOf(event.getEntity().getRemovalReason()));
    }
}

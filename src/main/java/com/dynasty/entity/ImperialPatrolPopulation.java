package com.dynasty.entity;

import com.dynasty.Dynasty;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.ArrayList;
import java.util.HashMap;

/** Bounded recovery of the old runaway natural spawns; never reads/loads distant chunks. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class ImperialPatrolPopulation {
    static final int CELL_SIZE = 48;
    static final int MAX_PER_CELL = 4;
    static final int MAX_DESPAWNS_PER_PASS = 256;

    @SubscribeEvent
    public static void onLoad(EntityJoinLevelEvent event) {
        if (event.loadedFromDisk() && event.getLevel() instanceof ServerLevel level
                && level.getServer().isSameThread()
                && level.dimension().location().getNamespace().equals(Dynasty.MODID)
                && event.getEntity() instanceof ImperialSoldier soldier
                && soldier.isAlive() && !soldier.isAddedToWorld()
                && !admitLoadedPatrol(level, soldier)) {
            // Reject before registration, AI and client tracking. No block/chunk access here:
            // joins can precede FULL status, when loading chunks would deadlock the server.
            event.setCanceled(true);
            soldier.discard();
        }
    }

    static boolean admitLoadedPatrol(ServerLevel level, ImperialSoldier soldier) {
        if (!soldier.removeWhenFarAway(0)) return true;
        var existing = new ArrayList<ImperialSoldier>();
        level.getEntities(net.minecraft.world.level.entity.EntityTypeTest.forClass(ImperialSoldier.class),
                soldier.getBoundingBox().inflate(ImperialSoldier.NATURAL_LOCAL_RADIUS),
                other -> other != soldier && other.isAlive() && other.removeWhenFarAway(0),
                existing, ImperialSoldier.NATURAL_LOCAL_LIMIT);
        return existing.size() < ImperialSoldier.NATURAL_LOCAL_LIMIT;
    }

    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent event) {
        if (event.phase == TickEvent.Phase.END && event.level instanceof ServerLevel level
                && level.dimension().location().getNamespace().equals(Dynasty.MODID)
                && level.getGameTime() % 10 == 0) {
            reduceCrowding(level.getAllEntities());
        }
    }

    static int reduceCrowding(Iterable<Entity> entities) {
        var counts = new HashMap<Cell, Integer>();
        var surplus = new ArrayList<ImperialSoldier>();
        for (Entity entity : entities) {
            if (!(entity instanceof ImperialSoldier soldier) || !soldier.isAlive()
                    || !soldier.removeWhenFarAway(0)) continue;
            var cell = new Cell(Math.floorDiv(soldier.getBlockX(), CELL_SIZE),
                    Math.floorDiv(soldier.getBlockY(), CELL_SIZE), Math.floorDiv(soldier.getBlockZ(), CELL_SIZE));
            if (counts.merge(cell, 1, Integer::sum) > MAX_PER_CELL) {
                surplus.add(soldier);
                if (surplus.size() == MAX_DESPAWNS_PER_PASS) break;
            }
        }
        // Do not mutate the entity iterator while scanning. Despawn, not kill: no drops,
        // kill rewards, damage events or projectile on-hit chains during lag recovery.
        surplus.forEach(ImperialSoldier::discard);
        return surplus.size();
    }

    private record Cell(int x, int y, int z) {}
    private ImperialPatrolPopulation() {}
}

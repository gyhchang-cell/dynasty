package com.dynasty.blueprint.combat;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import java.util.UUID;

/** Short-lived target handoff owned by an encounter member, never a static cross-world player cache. */
public final class TacticalMemory {
    private UUID marked;
    private long expires;
    public void mark(LivingEntity target, long now, int ttl) { marked = target.getUUID(); expires = now+Math.min(100, Math.max(1,ttl)); }
    public LivingEntity target(ServerLevel level, long now) {
        if (marked == null || now >= expires) { marked=null; return null; }
        return level.getEntity(marked) instanceof LivingEntity e && e.isAlive() ? e : null;
    }
}

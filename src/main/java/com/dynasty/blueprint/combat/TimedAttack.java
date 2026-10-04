package com.dynasty.blueprint.combat;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.phys.Vec3;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.IntConsumer;
import java.util.function.IntFunction;

/** Per-entity server clock. Checkpoints include consumed frames, so chunk reload cannot replay damage. */
public final class TimedAttack {
    private SkillDefinition current;
    private long started = -1, stunnedUntil;
    private Vec3 origin = Vec3.ZERO, direction = new Vec3(0, 0, 1);
    private UUID target;
    private final Map<Integer, Long> cooldowns = new HashMap<>();
    private final Set<Integer> fired = new HashSet<>();

    public boolean tryStart(SkillDefinition def, long now, Vec3 at, Vec3 forward, UUID victim) {
        if (def == null || state(now) != AttackState.IDLE || !ready(def.id(), now)
                || !finite(at) || !finite(forward) || forward.lengthSqr() < 1.0e-8) return false;
        current = def; started = now; origin = at; direction = forward.normalize(); target = victim; fired.clear();
        cooldowns.put(def.id(), now + def.totalTicks() + def.cooldownTicks());
        return true;
    }
    public void advance(long now, IntConsumer impact) {
        if (current == null) return;
        if (now < stunnedUntil) { cancel(); return; }
        SkillDefinition active = current;
        long actionStart = started;
        long age = now - actionStart;
        // Never dump delayed damage after an unloaded interval. A missed frame is safely cancelled.
        for (int frame : active.impactTicks()) {
            if (frame <= age && fired.add(frame) && frame == age) impact.accept(frame);
            // Damage callbacks can kill/stun the caster (e.g. thorns). Never touch or advance a new action.
            if (current != active || started != actionStart) return;
        }
        if (age >= active.totalTicks() || age < 0) cancel();
    }
    public void cancel() { current = null; started = -1; target = null; fired.clear(); }
    public void stun(long now, int ticks) { cancel(); stunnedUntil = Math.max(stunnedUntil, now + Math.max(1, ticks)); }
    public AttackState state(long now) {
        return now < stunnedUntil ? AttackState.STUN : current == null ? AttackState.IDLE
                : current.phaseAt((int)Math.min(Integer.MAX_VALUE, Math.max(-1, now - started)));
    }
    public SkillDefinition current() { return current; }
    public long started() { return started; }
    public Vec3 origin() { return origin; }
    public Vec3 direction() { return direction; }
    public UUID target() { return target; }
    public boolean ready(int id, long now) { return now >= cooldowns.getOrDefault(id, 0L); }
    public CompoundTag save() {
        var t = new CompoundTag(); t.putInt("Version", 1); t.putLong("Started", started); t.putLong("StunUntil", stunnedUntil);
        t.putInt("Skill", current == null ? 0 : current.id()); if (target != null) t.putUUID("Target", target);
        t.putDouble("X", origin.x); t.putDouble("Y", origin.y); t.putDouble("Z", origin.z);
        t.putDouble("DX", direction.x); t.putDouble("DY", direction.y); t.putDouble("DZ", direction.z);
        t.putIntArray("Fired", fired.stream().mapToInt(Integer::intValue).toArray());
        var cd = new CompoundTag(); cooldowns.forEach((k, v) -> cd.putLong(Integer.toString(k), v)); t.put("Cooldowns", cd);
        return t;
    }
    public void load(CompoundTag t, IntFunction<SkillDefinition> registry, long now) {
        cancel(); cooldowns.clear();
        stunnedUntil = Math.min(now + 1200, Math.max(0, t.getLong("StunUntil")));
        var cd = t.getCompound("Cooldowns");
        for (String key : cd.getAllKeys()) {
            try { int id = Integer.parseInt(key); if (registry.apply(id) != null)
                cooldowns.put(id, Math.min(now + 24000, Math.max(0, cd.getLong(key)))); }
            catch (NumberFormatException ignored) { /* Ignore corrupt/obsolete keys, not the whole entity. */ }
        }
        current = registry.apply(t.getInt("Skill")); started = t.getLong("Started");
        origin = new Vec3(t.getDouble("X"), t.getDouble("Y"), t.getDouble("Z"));
        direction = new Vec3(t.getDouble("DX"), t.getDouble("DY"), t.getDouble("DZ"));
        target = t.hasUUID("Target") ? t.getUUID("Target") : null;
        for (int frame : t.getIntArray("Fired")) fired.add(frame);
        if (current == null || now < started || now - started >= current.totalTicks()
                || !finite(origin) || !finite(direction) || direction.lengthSqr() < 1.0e-8) cancel();
        else direction = direction.normalize();
    }
    private static boolean finite(Vec3 p) { return Double.isFinite(p.x) && Double.isFinite(p.y) && Double.isFinite(p.z); }
}

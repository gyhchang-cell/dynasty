package com.dynasty.blueprint.combat;

import java.util.List;

/** Immutable timing and range contract shared by telegraphs and authoritative attacks. */
public record SkillDefinition(int id, String key, int windupTicks, int activeTicks,
        int recoveryTicks, int cooldownTicks, double minRange, double maxRange,
        double angleDegrees, float damageMultiplier, double knockback,
        boolean interruptible, boolean requiresSight, List<Integer> impactTicks) {
    public SkillDefinition {
        impactTicks = List.copyOf(impactTicks);
        if (id <= 0 || key == null || key.isBlank() || windupTicks < 0 || activeTicks < 1
                || recoveryTicks < 0 || cooldownTicks < 1 || !Double.isFinite(minRange) || minRange < 0 || maxRange < minRange
                || windupTicks > 1200 || activeTicks > 1200 || recoveryTicks > 1200 || cooldownTicks > 24000
                || !Double.isFinite(maxRange) || maxRange > 64 || angleDegrees < 0 || angleDegrees > 360
                || !Double.isFinite(angleDegrees) || !Float.isFinite(damageMultiplier) || damageMultiplier < 0
                || !Double.isFinite(knockback) || knockback < 0 || impactTicks.stream().distinct().count() != impactTicks.size())
            throw new IllegalArgumentException("Invalid skill: " + key);
        for (int t : impactTicks) if (t < windupTicks || t >= windupTicks + activeTicks)
            throw new IllegalArgumentException("Impact outside ACTIVE: " + key + " at " + t);
    }
    public int totalTicks() { return windupTicks + activeTicks + recoveryTicks; }
    public AttackState phaseAt(int age) {
        if (age < 0 || age >= totalTicks()) return AttackState.IDLE;
        return age < windupTicks ? AttackState.WINDUP
                : age < windupTicks + activeTicks ? AttackState.ACTIVE : AttackState.RECOVERY;
    }
}

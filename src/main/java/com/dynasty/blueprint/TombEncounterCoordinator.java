package com.dynasty.blueprint;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import java.util.UUID;

/** A finite handoff between loaded members of one authored tomb encounter. */
final class TombEncounterCoordinator {
    static void controlled(TemplateMob source, LivingEntity victim) {
        if (!(source.level() instanceof ServerLevel level) || source.encounterSite().isBlank()
                || !source.waterPool() || !source.validEnemy(victim)
                || !victim.hasEffect(BlueprintEntities.DROWNING_BIND.get())
                || !victim.getUUID().equals(source.attack().target())) return;
        for (var member : level.getEntitiesOfClass(TemplateMob.class, source.getBoundingBox().inflate(16),
                m -> m.isAlive() && (m.kind() == TemplateMob.Kind.CHILD || m.kind() == TemplateMob.Kind.PAPER)
                        && m.encounterSite().equals(source.encounterSite()) && source.distanceToSqr(m) <= 256
                        && m.hasLineOfSight(victim))) {
            member.tombSignal.mark(source, victim, level.getGameTime());
        }
    }

    static Vec3 flank(LivingEntity victim, boolean behind) {
        Vec3 forward = victim.getLookAngle().multiply(1, 0, 1).normalize();
        if (forward.lengthSqr() < .01) forward = new Vec3(0, 0, 1);
        return victim.position().add(forward.scale(behind ? -3 : 1.9));
    }

    static boolean inFront(TemplateMob member, LivingEntity victim) {
        Vec3 toward = member.position().subtract(victim.position()).multiply(1, 0, 1).normalize();
        return victim.getLookAngle().multiply(1, 0, 1).normalize().dot(toward) > .2;
    }

    static final class Signal {
        private UUID source, victim;
        private long expires, actionStart;

        void mark(TemplateMob caster, LivingEntity target, long now) {
            source = caster.getUUID(); victim = target.getUUID();
            expires = now + 12; actionStart = caster.skillStartTime();
        }

        LivingEntity target(TemplateMob member) {
            if (!(member.level() instanceof ServerLevel level) || source == null || victim == null
                    || level.getGameTime() >= expires || member.encounterSite().isBlank()) return null;
            if (!(level.getEntity(source) instanceof TemplateMob caster) || !caster.isAlive()
                    || !caster.waterPool() || caster.skillStartTime() != actionStart
                    || !caster.encounterSite().equals(member.encounterSite()) || member.distanceToSqr(caster) > 256
                    || !(level.getEntity(victim) instanceof LivingEntity target) || !member.validEnemy(target)
                    || !target.hasEffect(BlueprintEntities.DROWNING_BIND.get()) || !target.isInWater()
                    || Math.abs(caster.attack().origin().x-target.getX()) > 2
                    || Math.abs(caster.attack().origin().z-target.getZ()) > 2
                    || !member.hasLineOfSight(target) || !caster.hasLineOfSight(target)) return null;
            return target;
        }

        CompoundTag save() {
            var tag = new CompoundTag();
            if (source != null) tag.putUUID("Source", source);
            if (victim != null) tag.putUUID("Victim", victim);
            tag.putLong("Expires", expires); tag.putLong("ActionStart", actionStart);
            return tag;
        }

        void load(CompoundTag tag, long now) {
            source = tag.hasUUID("Source") ? tag.getUUID("Source") : null;
            victim = tag.hasUUID("Victim") ? tag.getUUID("Victim") : null;
            expires = Math.min(now + 12, tag.getLong("Expires"));
            actionStart = tag.getLong("ActionStart");
        }
    }

    private TombEncounterCoordinator() {}
}

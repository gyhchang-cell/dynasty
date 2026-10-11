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

    /** A bound player may stand two blocks below a dry pool rim; route to the actual floor. */
    static boolean waterAmbushNear(TemplateMob member,LivingEntity victim){
        return victim.isInWater()&&!member.encounterSite().isBlank()&&!member.level().getEntitiesOfClass(TemplateMob.class,member.getBoundingBox().inflate(16),
            m->m.kind()==TemplateMob.Kind.DROWNER&&m.isAlive()&&m.encounterSite().equals(member.encounterSite())&&member.distanceToSqr(m)<=256).isEmpty();
    }

    static net.minecraft.world.level.pathfinder.Path rearRoute(TemplateMob member,LivingEntity victim) {
        if(!(member.level() instanceof ServerLevel level))return null;
        Vec3 forward=victim.getLookAngle().multiply(1,0,1).normalize();
        if(forward.lengthSqr()<.01)forward=new Vec3(0,0,1);
        Vec3 side=new Vec3(-forward.z,0,forward.x);
        for(int radius:new int[]{3,4})for(int offset:new int[]{0,-1,1,-2,2})for(int dy:new int[]{0,1,2,-1,-2}){
            Vec3 point=victim.position().subtract(forward.scale(radius)).add(side.scale(offset));
            var feet=net.minecraft.core.BlockPos.containing(point).above(dy);
            if(!level.hasChunkAt(feet)||!level.getFluidState(feet).isEmpty()
                    ||!level.getBlockState(feet.below()).isFaceSturdy(level,feet.below(),net.minecraft.core.Direction.UP))continue;
            var box=member.getType().getDimensions().makeBoundingBox(feet.getX()+.5,feet.getY(),feet.getZ()+.5);
            if(!level.noCollision(member,box))continue;
            var path=member.getNavigation().createPath(feet,0);
            if(path!=null&&path.canReach())return path;
        }
        return null;
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

package com.yellowbrossproductions.illageandspillage.entities.goal;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.HinderEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.pathfinder.Path;

import java.util.EnumSet;
import java.util.List;

public class RunToHinderGoal extends Goal {
    private final Raider raider;
    private HinderEntity closestHinder;
    private Path path;

    public RunToHinderGoal(Raider raider) {
        this.raider = raider;
        this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
    }

    @Override
    public boolean canUse() {
        boolean initialConditions = !Config.CommonConfig.hinder_excluded.get().contains(this.raider.getEncodeId()) && raider.hasActiveRaid() && raider.getHealth() <= raider.getMaxHealth() / 2;
        if (!initialConditions) return false;

        List<HinderEntity> list2 = raider.level().getEntitiesOfClass(HinderEntity.class, raider.getBoundingBox().inflate(21.0));

        double closestDistance = Double.MAX_VALUE;
        HinderEntity closestEntity = null;

        for (HinderEntity hinder : list2) {
            double distance = this.raider.distanceToSqr(hinder);

            if (distance < 36) return false;

            if (distance < closestDistance) {
                closestDistance = distance;
                closestEntity = hinder;
            }
        }

        this.closestHinder = closestEntity;

        this.path = this.closestHinder == null ? null : this.raider.getNavigation().createPath(this.closestHinder, 0);

        return this.path != null;
    }

    @Override
    public void start() {
        this.raider.getNavigation().stop();
        this.raider.getNavigation().moveTo(this.path, 1.0);
    }

    @Override
    public boolean canContinueToUse() {
        return closestHinder != null && closestHinder.isAlive() && raider.distanceToSqr(this.closestHinder) > 16 && raider.getHealth() <= raider.getMaxHealth() / 2 && !raider.getNavigation().isDone();
    }

    @Override
    public void tick() {
        raider.setTarget(null);
        if (this.closestHinder != null) {
            raider.getLookControl().setLookAt(this.closestHinder, 100.0F, 100.0F);
        }
    }

    @Override
    public void stop() {
        this.raider.getNavigation().stop();
    }
}
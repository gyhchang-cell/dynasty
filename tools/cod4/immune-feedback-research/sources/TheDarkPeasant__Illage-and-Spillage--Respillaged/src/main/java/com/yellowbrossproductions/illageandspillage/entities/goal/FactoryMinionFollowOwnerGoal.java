package com.yellowbrossproductions.illageandspillage.entities.goal;

import com.yellowbrossproductions.illageandspillage.entities.FactoryMinion;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.pathfinder.BlockPathTypes;

import java.util.EnumSet;

public class FactoryMinionFollowOwnerGoal extends Goal {
    private final Raider mob;
    private LivingEntity owner;
    private final double followSpeed;
    private final PathNavigation navigator;
    private int timeToRecalcPath;
    private final float minDist;
    private final float maxDist;
    private float oldWaterCost;

    public FactoryMinionFollowOwnerGoal(Raider entityIn, double followSpeed, float minimumDistance, float maximumDistance) {
        this.mob = entityIn;
        this.followSpeed = followSpeed;
        this.navigator = entityIn.getNavigation();
        this.minDist = minimumDistance;
        this.maxDist = maximumDistance;
        this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
        if (!(entityIn.getNavigation() instanceof GroundPathNavigation) && !(entityIn.getNavigation() instanceof FlyingPathNavigation)) {
            throw new IllegalArgumentException("Unsupported mob type for FactoryMinionFollowOwnerGoal");
        }
    }

    public boolean canUse() {
        if (mob instanceof FactoryMinion minion && minion.getOwner() != null) {
            LivingEntity owner = minion.getOwner().getOwner();
            if (owner == null) {
                return false;
            } else if (owner.isSpectator()) {
                return false;
            } else if (this.mob.distanceToSqr(owner) <= (double) (this.minDist * this.minDist) || this.mob.distanceToSqr(owner) >= (double) (this.maxDist * this.maxDist)) {
                return false;
            } else if (this.mob.getTarget() != null) {
                return false;
            } else {
                this.owner = owner;
                return true;
            }
        }

        return false;
    }

    @Override
    public boolean canContinueToUse() {
        if (this.navigator.isDone()) {
            return false;
        } else if ((this.mob.distanceToSqr(this.owner) <= (double) (this.minDist * this.minDist)) || (this.mob.distanceToSqr(this.owner) >= (double) (this.maxDist * this.maxDist))) {
            return false;
        } else return this.mob.getTarget() == null;
    }

    @Override
    public void start() {
        this.timeToRecalcPath = 0;
        this.oldWaterCost = this.mob.getPathfindingMalus(BlockPathTypes.WATER);
        this.mob.setPathfindingMalus(BlockPathTypes.WATER, 0.0F);
    }

    @Override
    public void stop() {
        this.owner = null;
        this.navigator.stop();
        this.mob.setPathfindingMalus(BlockPathTypes.WATER, this.oldWaterCost);
    }

    @Override
    public void tick() {
        this.mob.getLookControl().setLookAt(this.owner, 10.0F, (float) this.mob.getMaxHeadXRot());
        if (--this.timeToRecalcPath <= 0) {
            this.timeToRecalcPath = 10;
            if (!this.mob.isLeashed() && !this.mob.isPassenger()) {
                this.navigator.moveTo(this.owner, this.followSpeed);
            }
        }
    }
}
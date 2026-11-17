package com.yellowbrossproductions.illageandspillage.entities.goal;

import com.yellowbrossproductions.illageandspillage.entities.MagispellerEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;

public class MeleeButStopGoal extends MeleeAttackGoal {
    protected final PathfinderMob mob;
    private final double distance;

    public MeleeButStopGoal(PathfinderMob p_25552_, double p_25553_, boolean p_25554_, double distance) {
        super(p_25552_, p_25553_, p_25554_);
        this.mob = p_25552_;
        this.distance = distance;
    }

    public void tick() {
        if (!(this.mob instanceof MagispellerEntity)) {
            if (this.mob.getTarget() != null) {
                if ((double) this.mob.distanceTo(this.mob.getTarget()) < this.distance) {
                    this.mob.getLookControl().setLookAt(this.mob.getTarget(), 30.0F, 30.0F);
                    this.mob.getNavigation().stop();
                } else {
                    super.tick();
                }
            }
        } else if (this.mob.getTarget() != null && !((MagispellerEntity) this.mob).isFaking()) {
            if ((double) this.mob.distanceTo(this.mob.getTarget()) < this.distance) {
                this.mob.getLookControl().setLookAt(this.mob.getTarget(), 30.0F, 30.0F);
                this.mob.getNavigation().stop();
            } else {
                super.tick();
            }
        }

    }
}

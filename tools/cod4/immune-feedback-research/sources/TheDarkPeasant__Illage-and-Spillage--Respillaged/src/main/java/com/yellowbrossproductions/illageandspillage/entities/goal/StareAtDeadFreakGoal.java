package com.yellowbrossproductions.illageandspillage.entities.goal;

import com.yellowbrossproductions.illageandspillage.entities.IllagerAttack;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

public class StareAtDeadFreakGoal extends Goal {
    private final Mob affectedMob;

    public StareAtDeadFreakGoal(Mob affected) {
        this.affectedMob = affected;
        this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
    }

    public boolean canUse() {
        return affectedMob instanceof IllagerAttack illagerAttack && illagerAttack.getOwner() != null && !illagerAttack.getOwner().isRemoved() && illagerAttack.getOwner().isDeadOrDying() && affectedMob.getLastHurtByMob() == null;
    }

    public boolean canContinueToUse() {
        return affectedMob instanceof IllagerAttack illagerAttack && illagerAttack.getOwner() != null && !illagerAttack.getOwner().isRemoved() && illagerAttack.getOwner().isDeadOrDying() && affectedMob.getLastHurtByMob() == null;
    }

    public void tick() {
        if (affectedMob instanceof IllagerAttack illagerAttack && illagerAttack.getOwner() != null) {
            this.affectedMob.getNavigation().stop();
            this.affectedMob.setTarget(null);
            this.affectedMob.getLookControl().setLookAt(illagerAttack.getOwner(), 100.0F, 100.0F);
            this.affectedMob.setYRot(this.affectedMob.getYHeadRot());
            this.affectedMob.yBodyRot = this.affectedMob.getYRot();
        }
    }
}

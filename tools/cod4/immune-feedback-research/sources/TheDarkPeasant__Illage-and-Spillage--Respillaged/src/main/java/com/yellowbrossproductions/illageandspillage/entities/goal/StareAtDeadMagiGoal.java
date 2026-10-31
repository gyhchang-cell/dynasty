package com.yellowbrossproductions.illageandspillage.entities.goal;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.MagispellerEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

public class StareAtDeadMagiGoal extends Goal {
    private final Mob affectedMob;
    private final MagispellerEntity magiToStareAt;

    public StareAtDeadMagiGoal(Mob affected, MagispellerEntity magiToStareAt) {
        this.affectedMob = affected;
        this.magiToStareAt = magiToStareAt;
        this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
    }

    public boolean canUse() {
        return Config.CommonConfig.magispeller_distractEnemies.get() && magiToStareAt != null && !magiToStareAt.isDead();
    }

    public boolean canContinueToUse() {
        return magiToStareAt != null && !magiToStareAt.isDead();
    }

    public void tick() {
        if (this.affectedMob != null && magiToStareAt != null) {
            this.affectedMob.getNavigation().stop();
            this.affectedMob.setTarget(null);
            this.affectedMob.getLookControl().setLookAt(magiToStareAt, 100.0F, 100.0F);
            this.affectedMob.setYRot(this.affectedMob.getYHeadRot());
            this.affectedMob.yBodyRot = this.affectedMob.getYRot();
        }
    }
}

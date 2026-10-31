package com.yellowbrossproductions.illageandspillage.entities.goal;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.FreakagerEntity;
import com.yellowbrossproductions.illageandspillage.entities.SpiritcallerEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.AbstractIllager;

import java.util.EnumSet;

public class WatchBossIntroGoal extends Goal {
    private final Mob affectedMob;
    private final AbstractIllager bossToStareAt;

    public WatchBossIntroGoal(Mob affected, AbstractIllager bossToStareAt) {
        this.affectedMob = affected;
        this.bossToStareAt = bossToStareAt;
        this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
    }

    public boolean canUse() {
        if (!Config.CommonConfig.mobs_watch_intros.get() || affectedMob.getTarget() != bossToStareAt) return false;
        if (bossToStareAt instanceof SpiritcallerEntity) {
            return affectedMob.distanceToSqr(bossToStareAt) > 64 && ((SpiritcallerEntity) bossToStareAt).isRitual();
        } else if (bossToStareAt instanceof FreakagerEntity) {
            return affectedMob.distanceToSqr(bossToStareAt) > 64 && (((FreakagerEntity) bossToStareAt).getAnimationState() == 9 || ((FreakagerEntity) bossToStareAt).getAnimationState() == 10 || ((FreakagerEntity) bossToStareAt).getAnimationState() == 11);
        }

        return false;
    }

    public boolean canContinueToUse() {
        if (bossToStareAt instanceof SpiritcallerEntity) {
            return affectedMob.distanceToSqr(bossToStareAt) > 64 && ((SpiritcallerEntity) bossToStareAt).isRitual();
        } else if (bossToStareAt instanceof FreakagerEntity) {
            return affectedMob.distanceToSqr(bossToStareAt) > 64 && ((FreakagerEntity) bossToStareAt).getAnimationState() == 1;
        }

        return false;
    }

    public void tick() {
        if (this.affectedMob != null && bossToStareAt != null) {
            this.affectedMob.getNavigation().stop();
            this.affectedMob.setTarget(null);
            this.affectedMob.getLookControl().setLookAt(bossToStareAt, 100.0F, 100.0F);
            this.affectedMob.setYRot(this.affectedMob.getYHeadRot());
            this.affectedMob.yBodyRot = this.affectedMob.getYRot();
        }
    }
}

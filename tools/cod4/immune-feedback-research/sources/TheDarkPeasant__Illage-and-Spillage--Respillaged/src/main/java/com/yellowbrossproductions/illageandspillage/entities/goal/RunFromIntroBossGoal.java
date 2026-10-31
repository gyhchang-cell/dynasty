package com.yellowbrossproductions.illageandspillage.entities.goal;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.FreakagerEntity;
import com.yellowbrossproductions.illageandspillage.entities.SpiritcallerEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.target.TargetGoal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;

public class RunFromIntroBossGoal extends AvoidEntityGoal {
    private final Map<Goal, Integer> targetGoalsWithPriorities = new HashMap<>();

    public RunFromIntroBossGoal(PathfinderMob p_25027_, Class p_25028_, float p_25029_, double p_25030_, double p_25031_) {
        super(p_25027_, p_25028_, p_25029_, p_25030_, p_25031_);
    }

    @Override
    public boolean canUse() {
        if (!Config.CommonConfig.mobs_watch_intros.get()) return false;

        boolean superUse = super.canUse();

        if (toAvoid instanceof SpiritcallerEntity) {
            return superUse && ((SpiritcallerEntity) toAvoid).isRitual();
        } else if (toAvoid instanceof FreakagerEntity) {
            return superUse && (((FreakagerEntity) toAvoid).getAnimationState() == 9 || ((FreakagerEntity) toAvoid).getAnimationState() == 10 || ((FreakagerEntity) toAvoid).getAnimationState() == 11);
        }

        return false;
    }

    @Override
    public boolean canContinueToUse() {
        if (this.toAvoid == null) return false;
        Vec3 vec3 = DefaultRandomPos.getPosAway(this.mob, 16, 7, this.toAvoid.position());
        if (vec3 == null) return false;
        return super.canContinueToUse() && this.toAvoid.distanceToSqr(vec3.x, vec3.y, vec3.z) < this.toAvoid.distanceToSqr(this.mob);
    }

    @Override
    public void start() {
        super.start();
        mob.targetSelector.getAvailableGoals().forEach(prioritizedGoal -> {
            if (prioritizedGoal.getGoal() instanceof TargetGoal) {
                targetGoalsWithPriorities.put(prioritizedGoal.getGoal(), prioritizedGoal.getPriority());
            }
        });

        targetGoalsWithPriorities.keySet().forEach(mob.targetSelector::removeGoal);
    }

    @Override
    public void stop() {
        targetGoalsWithPriorities.forEach((goal, priority) -> mob.targetSelector.addGoal(priority, goal));
        targetGoalsWithPriorities.clear();

        super.stop();
    }

    @Override
    public void tick() {
        super.tick();
        mob.setTarget(null);
    }
}


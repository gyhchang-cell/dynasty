/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.entity.ai.goal;

import moriyashiine.anthropophagy.common.entity.PigluttonEntity;
import net.minecraft.entity.ai.NoPenaltyTargeting;
import net.minecraft.entity.ai.goal.Goal;
import net.minecraft.entity.ai.pathing.Path;
import net.minecraft.util.math.Vec3d;

public class FleeGoal extends Goal {
	private final PigluttonEntity mob;
	private Path fleePath = null;

	public FleeGoal(PigluttonEntity mob) {
		this.mob = mob;
	}

	@Override
	public boolean canStart() {
		if (mob.isFleeing() && mob.getTarget() != null) {
			Vec3d fleePos = NoPenaltyTargeting.findFrom(mob, mob.fleeDistance, 7, mob.getTarget().getPos());
			if (fleePos != null) {
				fleePath = mob.getNavigation().findPathTo(fleePos.getX(), fleePos.getY(), fleePos.getZ(), 0);
				return true;
			}
		}
		return false;
	}

	@Override
	public boolean shouldContinue() {
		return mob.isFleeing() && !mob.getNavigation().isIdle();
	}

	@Override
	public void tick() {
		mob.getNavigation().startMovingAlong(fleePath, 1);
		mob.setTarget(null);
		mob.setAttacker(null);
	}
}

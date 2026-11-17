/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.entity.ai.goal;

import moriyashiine.anthropophagy.common.entity.PigluttonEntity;
import net.minecraft.entity.ai.goal.MeleeAttackGoal;

public class PigluttonMeleeAttackGoal extends MeleeAttackGoal {
	public PigluttonMeleeAttackGoal(PigluttonEntity mob, double speed, boolean pauseWhenMobIdle) {
		super(mob, speed, pauseWhenMobIdle);
	}

	@Override
	public boolean canStart() {
		PigluttonEntity piglutton = (PigluttonEntity) mob;
		return piglutton.canAttack && !piglutton.isFleeing() && super.canStart();
	}

	@Override
	public void tick() {
		PigluttonEntity piglutton = (PigluttonEntity) mob;
		if (piglutton.canAttack && !piglutton.isFleeing()) {
			super.tick();
		}
	}
}

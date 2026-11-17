/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.entity.ai.goal;

import moriyashiine.anthropophagy.common.entity.PigluttonEntity;
import net.minecraft.command.argument.EntityAnchorArgumentType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.ai.goal.Goal;
import net.minecraft.entity.player.PlayerEntity;

public class StalkGoal extends Goal {
	private static final int MAX_STALK_TICKS = 120;

	private final PigluttonEntity mob;

	public StalkGoal(PigluttonEntity mob) {
		this.mob = mob;
	}

	@Override
	public boolean canStart() {
		return !mob.isFleeing();
	}

	@Override
	public boolean shouldRunEveryTick() {
		return true;
	}

	@Override
	public void start() {
		mob.canAttack = false;
		mob.stalkTicks = 0;
	}

	@Override
	public void tick() {
		if (canAttack(mob.getTarget())) {
			if (++mob.stalkTicks >= MAX_STALK_TICKS || mob.distanceTo(mob.getTarget()) < 12 || mob.getAttacker() != null) {
				mob.canAttack = true;
			}
			mob.lookAt(EntityAnchorArgumentType.EntityAnchor.EYES, mob.getTarget().getPos());
		} else {
			mob.canAttack = false;
			mob.stalkTicks = 0;
		}
	}

	private boolean canAttack(LivingEntity entity) {
		if (entity == null || entity.isDead() || !entity.isAttackable()) {
			return false;
		}
		return !(entity instanceof PlayerEntity player) || !player.getAbilities().invulnerable;
	}
}

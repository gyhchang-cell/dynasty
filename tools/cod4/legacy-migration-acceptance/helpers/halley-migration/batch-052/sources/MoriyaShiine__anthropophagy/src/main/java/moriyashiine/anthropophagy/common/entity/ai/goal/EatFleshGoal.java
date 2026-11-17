/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.entity.ai.goal;

import moriyashiine.anthropophagy.common.entity.PigluttonEntity;
import moriyashiine.anthropophagy.common.init.ModItems;
import moriyashiine.anthropophagy.common.item.FleshItem;
import moriyashiine.anthropophagy.common.tag.ModItemTags;
import net.minecraft.component.DataComponentTypes;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.ItemEntity;
import net.minecraft.entity.ai.goal.Goal;
import net.minecraft.entity.mob.PathAwareEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.particle.ItemStackParticleEffect;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.sound.SoundEvents;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class EatFleshGoal extends Goal {
	private static final int OVERHEAL_REQUIRED = 30;

	private final PigluttonEntity mob;

	private ItemEntity closestFleshItem = null;

	public EatFleshGoal(PigluttonEntity mob) {
		this.mob = mob;
	}

	@Override
	public boolean canStart() {
		if (mob.isFleeing()) {
			closestFleshItem = null;
		} else {
			closestFleshItem = getNearestFlesh(mob);
		}
		return closestFleshItem != null;
	}

	@Override
	public void tick() {
		if (closestFleshItem != null) {
			mob.getNavigation().startMovingTo(closestFleshItem, 1);
			if (mob.distanceTo(closestFleshItem) < mob.getWidth()) {
				if (!mob.getWorld().isClient) {
					ItemStack flesh = closestFleshItem.getStack().split(1);
					((ServerWorld) mob.getWorld()).spawnParticles(new ItemStackParticleEffect(ParticleTypes.ITEM, flesh),
							closestFleshItem.getX(), closestFleshItem.getY(), closestFleshItem.getZ(),
							8,
							closestFleshItem.getWidth() / 2, closestFleshItem.getHeight() / 2, closestFleshItem.getWidth() / 2,
							0);
					mob.playSound(SoundEvents.ENTITY_GENERIC_EAT, 1, 1);
					if (!isTargetFlesh(flesh)) {
						mob.startFleeing();
					}
					int healAmount = 6;
					if (closestFleshItem.getStack().contains(DataComponentTypes.FOOD)) {
						healAmount = closestFleshItem.getStack().get(DataComponentTypes.FOOD).nutrition() * 2;
					}
					if (mob.getHealth() >= mob.getMaxHealth() && closestFleshItem.getOwner() == mob.getTarget() && !isTargetFlesh(flesh)) {
						mob.overhealAmount += healAmount;
						if (mob.overhealAmount >= OVERHEAL_REQUIRED) {
							mob.runAwayAndDespawn();
						}
					} else {
						mob.heal(healAmount);
					}
				}
			}
		}
	}

	@Nullable
	public static ItemEntity getNearestFlesh(PathAwareEntity mob) {
		List<ItemEntity> drops = mob.getWorld().getEntitiesByType(EntityType.ITEM, mob.getBoundingBox().expand(8, 4, 8), foundEntity -> foundEntity.getStack().isIn(ModItemTags.FLESH) && !foundEntity.getStack().isOf(ModItems.CORRUPT_FLESH));
		if (drops.isEmpty()) {
			return null;
		}
		return drops.getFirst();
	}

	private boolean isTargetFlesh(ItemStack flesh) {
		return mob.getTarget() != null && FleshItem.getOwnerName(flesh).equals(mob.getTarget().getName().getString());
	}
}

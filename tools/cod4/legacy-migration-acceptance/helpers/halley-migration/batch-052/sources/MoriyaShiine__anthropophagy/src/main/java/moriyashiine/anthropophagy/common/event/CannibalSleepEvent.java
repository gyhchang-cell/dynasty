/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.event;

import moriyashiine.anthropophagy.common.init.ModEntityComponents;
import net.fabricmc.fabric.api.entity.event.v1.EntitySleepEvents;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class CannibalSleepEvent implements EntitySleepEvents.AllowSleeping {
	@Nullable
	@Override
	public PlayerEntity.SleepFailureReason allowSleep(PlayerEntity player, BlockPos sleepingPos) {
		List<PlayerEntity> nearbyCannibals = player.getWorld().getEntitiesByClass(PlayerEntity.class, new Box(sleepingPos.getX() - 8, sleepingPos.getY() - 5, sleepingPos.getZ() - 8, sleepingPos.getX() + 8, sleepingPos.getY() + 5, sleepingPos.getZ() + 8), foundPlayer -> foundPlayer != player && ModEntityComponents.CANNIBAL_LEVEL.get(foundPlayer).getCannibalLevel() >= 70);
		if (!nearbyCannibals.isEmpty()) {
			return PlayerEntity.SleepFailureReason.NOT_SAFE;
		}
		return null;
	}
}

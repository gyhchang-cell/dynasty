/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.event;

import moriyashiine.anthropophagy.common.component.entity.CannibalLevelComponent;
import moriyashiine.anthropophagy.common.init.ModEntityComponents;
import net.fabricmc.fabric.api.entity.event.v1.ServerPlayerEvents;
import net.minecraft.server.network.ServerPlayerEntity;

public class CopyCannibalLevelEvent implements ServerPlayerEvents.CopyFrom {
	@Override
	public void copyFromPlayer(ServerPlayerEntity oldPlayer, ServerPlayerEntity newPlayer, boolean alive) {
		if (!alive) {
			if (ModEntityComponents.TETHERED.get(oldPlayer).isTethered()) {
				CannibalLevelComponent cannibalLevelComponent = ModEntityComponents.CANNIBAL_LEVEL.get(newPlayer);
				cannibalLevelComponent.setCannibalLevel(ModEntityComponents.CANNIBAL_LEVEL.get(oldPlayer).getCannibalLevel());
				cannibalLevelComponent.updateAttributes();
				cannibalLevelComponent.sync();
			}
		}
	}
}

/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.init;

import moriyashiine.anthropophagy.common.Anthropophagy;
import moriyashiine.anthropophagy.common.component.entity.CannibalLevelComponent;
import moriyashiine.anthropophagy.common.component.entity.TetheredComponent;
import org.ladysnake.cca.api.v3.component.ComponentKey;
import org.ladysnake.cca.api.v3.component.ComponentRegistry;
import org.ladysnake.cca.api.v3.entity.EntityComponentFactoryRegistry;
import org.ladysnake.cca.api.v3.entity.EntityComponentInitializer;
import org.ladysnake.cca.api.v3.entity.RespawnCopyStrategy;

public class ModEntityComponents implements EntityComponentInitializer {
	public static int playerCannibalLevel = -1;

	public static final ComponentKey<CannibalLevelComponent> CANNIBAL_LEVEL = ComponentRegistry.getOrCreate(Anthropophagy.id("cannibal_level"), CannibalLevelComponent.class);
	public static final ComponentKey<TetheredComponent> TETHERED = ComponentRegistry.getOrCreate(Anthropophagy.id("tethered"), TetheredComponent.class);

	@Override
	public void registerEntityComponentFactories(EntityComponentFactoryRegistry registry) {
		registry.registerForPlayers(CANNIBAL_LEVEL, CannibalLevelComponent::new, RespawnCopyStrategy.LOSSLESS_ONLY);
		registry.registerForPlayers(TETHERED, player -> new TetheredComponent(), RespawnCopyStrategy.LOSSLESS_ONLY);
	}
}

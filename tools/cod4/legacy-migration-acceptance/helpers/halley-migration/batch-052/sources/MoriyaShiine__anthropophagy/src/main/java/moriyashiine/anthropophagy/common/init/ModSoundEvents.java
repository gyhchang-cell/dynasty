/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.init;

import moriyashiine.anthropophagy.common.Anthropophagy;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.sound.SoundEvent;

public class ModSoundEvents {
	public static final SoundEvent ENTITY_PIGLUTTON_AMBIENT = SoundEvent.of(Anthropophagy.id("entity.piglutton.ambient"));
	public static final SoundEvent ENTITY_PIGLUTTON_HURT = SoundEvent.of(Anthropophagy.id("entity.piglutton.hurt"));
	public static final SoundEvent ENTITY_PIGLUTTON_DEATH = SoundEvent.of(Anthropophagy.id("entity.piglutton.death"));
	public static final SoundEvent ENTITY_PIGLUTTON_SPAWN = SoundEvent.of(Anthropophagy.id("entity.piglutton.spawn"));
	public static final SoundEvent ENTITY_PIGLUTTON_FLEE = SoundEvent.of(Anthropophagy.id("entity.piglutton.flee"));

	public static void init() {
		Registry.register(Registries.SOUND_EVENT, ENTITY_PIGLUTTON_AMBIENT.getId(), ENTITY_PIGLUTTON_AMBIENT);
		Registry.register(Registries.SOUND_EVENT, ENTITY_PIGLUTTON_HURT.getId(), ENTITY_PIGLUTTON_HURT);
		Registry.register(Registries.SOUND_EVENT, ENTITY_PIGLUTTON_DEATH.getId(), ENTITY_PIGLUTTON_DEATH);
		Registry.register(Registries.SOUND_EVENT, ENTITY_PIGLUTTON_SPAWN.getId(), ENTITY_PIGLUTTON_SPAWN);
		Registry.register(Registries.SOUND_EVENT, ENTITY_PIGLUTTON_FLEE.getId(), ENTITY_PIGLUTTON_FLEE);
	}
}

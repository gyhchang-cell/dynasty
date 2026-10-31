/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.init;

import moriyashiine.anthropophagy.common.Anthropophagy;
import moriyashiine.anthropophagy.common.ModConfig;
import moriyashiine.anthropophagy.common.entity.PigluttonEntity;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.SpawnGroup;
import net.minecraft.entity.SpawnLocationTypes;
import net.minecraft.entity.SpawnRestriction;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.registry.tag.BiomeTags;
import net.minecraft.world.Heightmap;

public class ModEntityTypes {
	public static final EntityType<PigluttonEntity> PIGLUTTON = EntityType.Builder.create(PigluttonEntity::new, SpawnGroup.MONSTER).dimensions(3, 2.6F).spawnableFarFromPlayer().build();

	public static void init() {
		Registry.register(Registries.ENTITY_TYPE, Anthropophagy.id("piglutton"), PIGLUTTON);
		FabricDefaultAttributeRegistry.register(PIGLUTTON, PigluttonEntity.buildAttributes());
		SpawnRestriction.register(PIGLUTTON, SpawnLocationTypes.ON_GROUND, Heightmap.Type.WORLD_SURFACE, PigluttonEntity::canSpawn);
		if (ModConfig.enablePiglutton) {
			BiomeModifications.addSpawn(BiomeSelectors.tag(BiomeTags.IS_FOREST), PIGLUTTON.getSpawnGroup(), PIGLUTTON, 1, 1, 1);
		}
	}
}

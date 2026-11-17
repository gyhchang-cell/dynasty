/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.data.provider;

import moriyashiine.anthropophagy.common.init.ModItems;
import net.fabricmc.fabric.api.datagen.v1.FabricDataOutput;
import net.fabricmc.fabric.api.datagen.v1.provider.FabricModelProvider;
import net.minecraft.data.client.BlockStateModelGenerator;
import net.minecraft.data.client.ItemModelGenerator;
import net.minecraft.data.client.Models;

public class ModModelProvider extends FabricModelProvider {
	public ModModelProvider(FabricDataOutput output) {
		super(output);
	}

	@Override
	public void generateBlockStateModels(BlockStateModelGenerator blockStateModelGenerator) {
	}

	@Override
	public void generateItemModels(ItemModelGenerator itemModelGenerator) {
		itemModelGenerator.register(ModItems.WOODEN_KNIFE, Models.HANDHELD);
		itemModelGenerator.register(ModItems.STONE_KNIFE, Models.HANDHELD);
		itemModelGenerator.register(ModItems.IRON_KNIFE, Models.HANDHELD);
		itemModelGenerator.register(ModItems.GOLDEN_KNIFE, Models.HANDHELD);
		itemModelGenerator.register(ModItems.DIAMOND_KNIFE, Models.HANDHELD);
		itemModelGenerator.register(ModItems.NETHERITE_KNIFE, Models.HANDHELD);
		itemModelGenerator.register(ModItems.FLESH, Models.GENERATED);
		itemModelGenerator.register(ModItems.COOKED_FLESH, Models.GENERATED);
		itemModelGenerator.register(ModItems.CORRUPT_FLESH, Models.GENERATED);
		itemModelGenerator.register(ModItems.PIGLUTTON_HEART, Models.GENERATED);
		itemModelGenerator.register(ModItems.TETHERED_HEART, Models.GENERATED);
	}
}

/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.data.provider;

import moriyashiine.anthropophagy.common.init.ModItems;
import moriyashiine.anthropophagy.common.tag.ModItemTags;
import net.fabricmc.fabric.api.datagen.v1.FabricDataOutput;
import net.fabricmc.fabric.api.datagen.v1.provider.FabricTagProvider;
import net.fabricmc.fabric.api.tag.convention.v2.ConventionalItemTags;
import net.minecraft.registry.BuiltinRegistries;
import net.minecraft.registry.RegistryWrapper;
import net.minecraft.registry.tag.ItemTags;

import java.util.concurrent.CompletableFuture;

public class ModItemTagProvider extends FabricTagProvider.ItemTagProvider {
	public ModItemTagProvider(FabricDataOutput output) {
		super(output, CompletableFuture.supplyAsync(BuiltinRegistries::createWrapperLookup));
	}

	@Override
	protected void configure(RegistryWrapper.WrapperLookup arg) {
		getOrCreateTagBuilder(ModItemTags.KNIVES)
				.add(ModItems.WOODEN_KNIFE)
				.add(ModItems.STONE_KNIFE)
				.add(ModItems.IRON_KNIFE)
				.add(ModItems.GOLDEN_KNIFE)
				.add(ModItems.DIAMOND_KNIFE)
				.add(ModItems.NETHERITE_KNIFE);
		getOrCreateTagBuilder(ModItemTags.FLESH)
				.add(ModItems.FLESH)
				.add(ModItems.COOKED_FLESH)
				.add(ModItems.CORRUPT_FLESH)
				.add(ModItems.PIGLUTTON_HEART)
				.add(ModItems.TETHERED_HEART);

		getOrCreateTagBuilder(ItemTags.MEAT)
				.addOptionalTag(ModItemTags.FLESH);
		getOrCreateTagBuilder(ItemTags.PIGLIN_LOVED)
				.add(ModItems.GOLDEN_KNIFE);
		getOrCreateTagBuilder(ItemTags.SWORDS)
				.add(ModItems.WOODEN_KNIFE)
				.add(ModItems.STONE_KNIFE)
				.add(ModItems.IRON_KNIFE)
				.add(ModItems.GOLDEN_KNIFE)
				.add(ModItems.DIAMOND_KNIFE)
				.add(ModItems.NETHERITE_KNIFE);

		getOrCreateTagBuilder(ConventionalItemTags.RAW_MEATS_FOODS)
				.add(ModItems.FLESH)
				.add(ModItems.CORRUPT_FLESH)
				.add(ModItems.PIGLUTTON_HEART)
				.add(ModItems.TETHERED_HEART);
		getOrCreateTagBuilder(ConventionalItemTags.COOKED_MEATS_FOODS)
				.add(ModItems.COOKED_FLESH);
	}
}

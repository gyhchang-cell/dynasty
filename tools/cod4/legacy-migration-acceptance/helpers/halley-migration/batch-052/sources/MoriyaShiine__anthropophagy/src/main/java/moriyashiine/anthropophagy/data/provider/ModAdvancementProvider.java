/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.data.provider;

import moriyashiine.anthropophagy.common.Anthropophagy;
import moriyashiine.anthropophagy.common.init.ModEntityTypes;
import moriyashiine.anthropophagy.common.init.ModItems;
import moriyashiine.anthropophagy.common.tag.ModItemTags;
import net.fabricmc.fabric.api.datagen.v1.FabricDataOutput;
import net.fabricmc.fabric.api.datagen.v1.provider.FabricAdvancementProvider;
import net.minecraft.advancement.Advancement;
import net.minecraft.advancement.AdvancementEntry;
import net.minecraft.advancement.AdvancementFrame;
import net.minecraft.advancement.criterion.ConsumeItemCriterion;
import net.minecraft.advancement.criterion.InventoryChangedCriterion;
import net.minecraft.advancement.criterion.OnKilledCriterion;
import net.minecraft.predicate.entity.EntityPredicate;
import net.minecraft.predicate.item.ItemPredicate;
import net.minecraft.registry.BuiltinRegistries;
import net.minecraft.registry.RegistryWrapper;
import net.minecraft.text.Text;
import net.minecraft.util.Identifier;

import java.util.concurrent.CompletableFuture;
import java.util.function.Consumer;

public class ModAdvancementProvider extends FabricAdvancementProvider {
	public ModAdvancementProvider(FabricDataOutput output) {
		super(output, CompletableFuture.supplyAsync(BuiltinRegistries::createWrapperLookup));
	}

	@Override
	public void generateAdvancement(RegistryWrapper.WrapperLookup registryLookup, Consumer<AdvancementEntry> consumer) {
		consumer.accept(Advancement.Builder.create()
				.parent(Identifier.tryParse("husbandry/root"))
				.display(ModItems.FLESH,
						Text.translatable("advancements.anthropophagy.husbandry.consume_flesh.title"),
						Text.translatable("advancements.anthropophagy.husbandry.consume_flesh.description"),
						null,
						AdvancementFrame.TASK,
						true,
						true,
						true)
				.criterion("consume_flesh", ConsumeItemCriterion.Conditions.predicate(ItemPredicate.Builder.create().tag(ModItemTags.FLESH)))
				.build(consumer, Anthropophagy.id("husbandry/consume_flesh").toString()));

		consumer.accept(Advancement.Builder.create()
				.parent(Identifier.tryParse("husbandry/root"))
				.display(ModItems.PIGLUTTON_HEART,
						Text.translatable("advancements.anthropophagy.husbandry.kill_piglutton.title"),
						Text.translatable("advancements.anthropophagy.husbandry.kill_piglutton.description"),
						null,
						AdvancementFrame.TASK,
						true,
						true,
						true)
				.criterion("killed_piglutton", OnKilledCriterion.Conditions.createPlayerKilledEntity(new EntityPredicate.Builder().type(ModEntityTypes.PIGLUTTON)))
				.build(consumer, Anthropophagy.id("husbandry/kill_piglutton").toString()));

		consumer.accept(Advancement.Builder.create()
				.parent(Identifier.tryParse("husbandry/root"))
				.display(ModItems.IRON_KNIFE,
						Text.translatable("advancements.anthropophagy.husbandry.obtain_knife.title"),
						Text.translatable("advancements.anthropophagy.husbandry.obtain_knife.description"),
						null,
						AdvancementFrame.TASK,
						true,
						true,
						false)
				.criterion("has_knife", InventoryChangedCriterion.Conditions.items(ItemPredicate.Builder.create().tag(ModItemTags.KNIVES)))
				.build(consumer, Anthropophagy.id("husbandry/obtain_knife").toString()));
	}
}
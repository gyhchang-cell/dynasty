/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import moriyashiine.anthropophagy.common.init.ModDataComponentTypes;
import moriyashiine.anthropophagy.common.item.FleshItem;
import net.minecraft.block.entity.AbstractFurnaceBlockEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.recipe.Recipe;
import net.minecraft.recipe.RecipeEntry;
import net.minecraft.registry.DynamicRegistryManager;
import net.minecraft.registry.RegistryWrapper;
import net.minecraft.util.collection.DefaultedList;
import org.jetbrains.annotations.Nullable;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(AbstractFurnaceBlockEntity.class)
public class AbstractFurnaceBlockEntityMixin {
	@WrapOperation(method = "canAcceptRecipeOutput", at = @At(value = "INVOKE", target = "Lnet/minecraft/item/ItemStack;areItemsAndComponentsEqual(Lnet/minecraft/item/ItemStack;Lnet/minecraft/item/ItemStack;)Z"))
	private static boolean anthropophagy$compareFlesh(ItemStack stack, ItemStack otherStack, Operation<Boolean> original, DynamicRegistryManager registryManager, @Nullable RecipeEntry<?> recipe, DefaultedList<ItemStack> slots) {
		boolean allow = original.call(stack, otherStack);
		ItemStack toCook = slots.getFirst();
		if (allow && toCook.contains(ModDataComponentTypes.OWNER_NAME) && !FleshItem.getOwnerName(toCook).equals(FleshItem.getOwnerName(stack))) {
			return false;
		}
		if (!allow && toCook.contains(ModDataComponentTypes.OWNER_NAME) && FleshItem.getOwnerName(toCook).equals(FleshItem.getOwnerName(stack))) {
			return true;
		}
		return allow;
	}

	@WrapOperation(method = "craftRecipe", at = @At(value = "INVOKE", target = "Lnet/minecraft/recipe/Recipe;getResult(Lnet/minecraft/registry/RegistryWrapper$WrapperLookup;)Lnet/minecraft/item/ItemStack;"))
	private static ItemStack anthropophagy$persistFleshOwner(Recipe<?> instance, RegistryWrapper.WrapperLookup wrapperLookup, Operation<ItemStack> original, DynamicRegistryManager registryManager, @Nullable RecipeEntry<?> recipe, DefaultedList<ItemStack> slots) {
		ItemStack stack = original.call(instance, wrapperLookup);
		if (stack.getItem() instanceof FleshItem) {
			ItemStack toCook = slots.getFirst();
			if (toCook.getItem() instanceof FleshItem) {
				stack = stack.copy();
				FleshItem.setOwner(stack, FleshItem.getOwnerName(toCook), FleshItem.isOwnerPlayer(toCook));
			}
		}
		return stack;
	}
}

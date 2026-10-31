/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import moriyashiine.anthropophagy.common.item.FleshItem;
import net.minecraft.inventory.Inventory;
import net.minecraft.item.ItemStack;
import net.minecraft.recipe.AbstractCookingRecipe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(AbstractCookingRecipe.class)
public class AbstractCookingRecipeMixin {
	@ModifyReturnValue(method = "craft", at = @At("RETURN"))
	private ItemStack anthropophagy$persistFleshOwner(ItemStack original, Inventory inventory) {
		if (original.getItem() instanceof FleshItem) {
			ItemStack toCook = inventory.getStack(0);
			if (toCook.getItem() instanceof FleshItem) {
				FleshItem.setOwner(original, FleshItem.getOwnerName(toCook), FleshItem.isOwnerPlayer(toCook));
			}
		}
		return original;
	}
}

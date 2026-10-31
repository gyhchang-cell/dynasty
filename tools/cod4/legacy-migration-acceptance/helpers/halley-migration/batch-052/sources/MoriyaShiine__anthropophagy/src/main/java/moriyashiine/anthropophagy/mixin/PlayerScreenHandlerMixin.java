/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import moriyashiine.anthropophagy.common.init.ModEntityComponents;
import net.minecraft.entity.player.PlayerInventory;
import net.minecraft.inventory.Inventory;
import net.minecraft.item.ItemStack;
import net.minecraft.screen.slot.Slot;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(targets = "net/minecraft/screen/PlayerScreenHandler$1")
public class PlayerScreenHandlerMixin extends Slot {
	public PlayerScreenHandlerMixin(Inventory inventory, int index, int x, int y) {
		super(inventory, index, x, y);
	}

	@ModifyReturnValue(method = "canInsert(Lnet/minecraft/item/ItemStack;)Z", at = @At("RETURN"))
	private boolean anthropophagy$preventEquipping(boolean original, ItemStack stack) {
		if (original && !ModEntityComponents.CANNIBAL_LEVEL.get(((PlayerInventory) inventory).player).canEquip(stack)) {
			return false;
		}
		return original;
	}
}

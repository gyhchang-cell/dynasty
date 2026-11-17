/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.item;

import moriyashiine.anthropophagy.common.init.ModDataComponentTypes;
import net.minecraft.entity.Entity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.text.Text;

public class FleshItem extends Item {
	public FleshItem(Settings settings) {
		super(settings);
	}

	@Override
	public Text getName(ItemStack stack) {
		String ownerName = getOwnerName(stack);
		if (!ownerName.isEmpty()) {
			return Text.translatable(getTranslationKey(stack) + "_owned", ownerName);
		}
		return super.getName(stack);
	}

	public static String getOwnerName(ItemStack stack) {
		return stack.getOrDefault(ModDataComponentTypes.OWNER_NAME, "");
	}

	public static boolean isOwnerPlayer(ItemStack stack) {
		return stack.getOrDefault(ModDataComponentTypes.FROM_PLAYER, false);
	}

	public static void setOwner(ItemStack stack, String ownerName, boolean fromPlayer) {
		if (ownerName.isEmpty()) {
			return;
		}
		stack.set(ModDataComponentTypes.OWNER_NAME, ownerName);
		stack.set(ModDataComponentTypes.FROM_PLAYER, fromPlayer);
	}

	public static void setOwner(ItemStack stack, Entity entity) {
		setOwner(stack, entity.getName().getString(), entity instanceof PlayerEntity);
	}
}

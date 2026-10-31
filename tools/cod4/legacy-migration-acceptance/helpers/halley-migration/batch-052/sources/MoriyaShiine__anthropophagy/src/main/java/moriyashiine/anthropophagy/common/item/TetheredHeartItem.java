/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.item;

import moriyashiine.anthropophagy.common.Anthropophagy;
import moriyashiine.anthropophagy.common.component.entity.TetheredComponent;
import moriyashiine.anthropophagy.common.init.ModEntityComponents;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.stat.Stats;
import net.minecraft.text.Text;
import net.minecraft.util.Hand;
import net.minecraft.util.TypedActionResult;
import net.minecraft.world.World;

public class TetheredHeartItem extends Item {
	public TetheredHeartItem(Settings settings) {
		super(settings);
	}

	@Override
	public ItemStack finishUsing(ItemStack stack, World world, LivingEntity user) {
		if (user instanceof PlayerEntity player) {
			TetheredComponent tetheredComponent = ModEntityComponents.TETHERED.get(player);
			if (!tetheredComponent.isTethered()) {
				tetheredComponent.setTethered(true);
				player.incrementStat(Stats.USED.getOrCreateStat(this));
				if (!player.isCreative()) {
					stack.decrement(1);
				}
				player.sendMessage(Text.translatable(Anthropophagy.MOD_ID + ".message.tether"), true);
			}
		}
		return super.finishUsing(stack, world, user);
	}

	@Override
	public void usageTick(World world, LivingEntity user, ItemStack stack, int remainingUseTicks) {
		if (remainingUseTicks == getMaxUseTime(stack) / 2 && user instanceof PlayerEntity player && ModEntityComponents.TETHERED.get(player).isTethered()) {
			player.sendMessage(Text.translatable(Anthropophagy.MOD_ID + ".message.tethered"), true);
			player.stopUsingItem();
		}
		super.usageTick(world, user, stack, remainingUseTicks);
	}

	@Override
	public TypedActionResult<ItemStack> use(World world, PlayerEntity user, Hand hand) {

		return super.use(world, user, hand);
	}
}

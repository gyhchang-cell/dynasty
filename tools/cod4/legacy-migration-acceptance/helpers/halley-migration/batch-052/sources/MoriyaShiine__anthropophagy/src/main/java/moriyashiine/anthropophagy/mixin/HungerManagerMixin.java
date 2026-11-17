/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.mixin;

import moriyashiine.anthropophagy.common.init.ModEntityComponents;
import net.minecraft.entity.player.HungerManager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

@Mixin(HungerManager.class)
public class HungerManagerMixin {
	@ModifyVariable(method = "addInternal", at = @At("HEAD"), argsOnly = true)
	private int anthropophagy$reduceHungerGained(int value) {
		if (ModEntityComponents.playerCannibalLevel != -1) {
			value = Math.round(value * getFoodModifier(ModEntityComponents.playerCannibalLevel));
			ModEntityComponents.playerCannibalLevel = -1;
		}
		return value;
	}

	@ModifyVariable(method = "addInternal", at = @At("HEAD"), argsOnly = true)
	private float anthropophagy$reduceSaturationGained(float value) {
		if (ModEntityComponents.playerCannibalLevel != -1) {
			value *= getFoodModifier(ModEntityComponents.playerCannibalLevel);
			ModEntityComponents.playerCannibalLevel = -1;
		}
		return value;
	}

	@Unique
	private static float getFoodModifier(int level) {
		if (level >= 70) {
			return 0.4F;
		}
		if (level >= 60) {
			return 0.5F;
		}
		if (level >= 50) {
			return 0.6F;
		}
		if (level >= 40) {
			return 0.7F;
		}
		if (level >= 30) {
			return 0.8F;
		}
		if (level >= 20) {
			return 0.9F;
		}
		return 1;
	}
}

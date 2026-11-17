/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.init;

import net.minecraft.component.type.FoodComponent;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;

public class ModFoodComponents {
	public static final FoodComponent FLESH = new FoodComponent.Builder().nutrition(3).saturationModifier(0.3F).build();
	public static final FoodComponent COOKED_FLESH = new FoodComponent.Builder().nutrition(8).saturationModifier(0.8F).build();
	public static final FoodComponent CORRUPT_FLESH = new FoodComponent.Builder().nutrition(3).saturationModifier(0.3F).statusEffect(new StatusEffectInstance(StatusEffects.INSTANT_DAMAGE, 1, 1), 1).build();
	public static final FoodComponent TETHERED_HEART = new FoodComponent.Builder().nutrition(8).saturationModifier(0.8F).alwaysEdible().build();
}

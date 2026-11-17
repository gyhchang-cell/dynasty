/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.item;

import moriyashiine.anthropophagy.common.component.entity.TetheredComponent;
import moriyashiine.anthropophagy.common.init.ModEntityComponents;
import moriyashiine.anthropophagy.common.init.ModItems;
import net.minecraft.component.type.AttributeModifierSlot;
import net.minecraft.component.type.AttributeModifiersComponent;
import net.minecraft.entity.attribute.EntityAttributeModifier;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.item.SwordItem;
import net.minecraft.item.ToolMaterial;
import net.minecraft.util.Hand;
import net.minecraft.util.TypedActionResult;
import net.minecraft.world.World;

import java.util.UUID;

public class KnifeItem extends SwordItem {
	private static final EntityAttributeModifier REACH_MODIFIER = new EntityAttributeModifier(UUID.fromString("036c3108-e940-4e06-93f0-8f826c7c4877"), "Weapon modifier", -0.5, EntityAttributeModifier.Operation.ADD_VALUE);

	public KnifeItem(ToolMaterial toolMaterial, Settings settings) {
		super(toolMaterial, settings);
	}

	public static AttributeModifiersComponent createAttributeModifiers(ToolMaterial material, int baseAttackDamage, float attackSpeed) {
		AttributeModifiersComponent sword = SwordItem.createAttributeModifiers(material, baseAttackDamage, attackSpeed);
		AttributeModifiersComponent.Builder builder = AttributeModifiersComponent.builder();
		sword.modifiers().forEach(entry -> builder.add(entry.attribute(), entry.modifier(), entry.slot()));
		builder.add(EntityAttributes.PLAYER_ENTITY_INTERACTION_RANGE, REACH_MODIFIER, AttributeModifierSlot.MAINHAND);
		return builder.build();
	}

	@Override
	public TypedActionResult<ItemStack> use(World world, PlayerEntity user, Hand hand) {
		if (user.isSneaking()) {
			user.attack(user);
			TetheredComponent tetheredComponent = ModEntityComponents.TETHERED.get(user);
			if (tetheredComponent.isTethered()) {
				tetheredComponent.setTethered(false);
				user.dropItem(ModItems.PIGLUTTON_HEART);
			}
			return TypedActionResult.success(user.getStackInHand(hand), world.isClient);
		}
		return super.use(world, user, hand);
	}
}

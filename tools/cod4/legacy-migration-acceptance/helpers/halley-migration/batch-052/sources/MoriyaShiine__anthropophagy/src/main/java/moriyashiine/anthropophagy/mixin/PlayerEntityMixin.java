/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import moriyashiine.anthropophagy.common.ModConfig;
import moriyashiine.anthropophagy.common.component.entity.CannibalLevelComponent;
import moriyashiine.anthropophagy.common.component.entity.TetheredComponent;
import moriyashiine.anthropophagy.common.entity.PigluttonEntity;
import moriyashiine.anthropophagy.common.event.DropFleshEvent;
import moriyashiine.anthropophagy.common.init.ModEntityComponents;
import moriyashiine.anthropophagy.common.item.FleshItem;
import moriyashiine.anthropophagy.common.tag.ModItemTags;
import net.minecraft.component.DataComponentTypes;
import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.effect.StatusEffectInstance;
import net.minecraft.entity.effect.StatusEffects;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.world.World;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import org.spongepowered.asm.mixin.injection.callback.LocalCapture;

@Mixin(PlayerEntity.class)
public abstract class PlayerEntityMixin extends LivingEntity {
	protected PlayerEntityMixin(EntityType<? extends LivingEntity> entityType, World world) {
		super(entityType, world);
	}

	@Inject(method = "attack", at = @At(value = "INVOKE", target = "Lnet/minecraft/entity/player/PlayerEntity;resetLastAttackedTicks()V"), locals = LocalCapture.CAPTURE_FAILHARD)
	private void anthropophagy$updateEventCooldown(Entity target, CallbackInfo ci, float attackDamage, float extraDamage, float attackCooldown) {
		DropFleshEvent.attackCooldown = attackCooldown;
	}

	@Inject(method = "attack", at = @At("TAIL"))
	private void anthropophagy$resetEventCooldown(Entity target, CallbackInfo ci) {
		DropFleshEvent.attackCooldown = -1;
	}

	@Inject(method = "eatFood", at = @At("HEAD"))
	private void anthropophagy$handleCannibalFood(World world, ItemStack stack, CallbackInfoReturnable<ItemStack> cir) {
		if (stack.contains(DataComponentTypes.FOOD)) {
			CannibalLevelComponent cannibalLevelComponent = ModEntityComponents.CANNIBAL_LEVEL.get(this);
			TetheredComponent tetheredComponent = ModEntityComponents.TETHERED.get(this);
			if (stack.isIn(ModItemTags.FLESH)) {
				if (!tetheredComponent.isTethered()) {
					if (cannibalLevelComponent.getCannibalLevel() < CannibalLevelComponent.MAX_LEVEL) {
						cannibalLevelComponent.setCannibalLevel(Math.min(CannibalLevelComponent.MAX_LEVEL, cannibalLevelComponent.getCannibalLevel() + 2));
						cannibalLevelComponent.updateAttributes();
					}
					if (!world.isClient && cannibalLevelComponent.getCannibalLevel() == 20 || cannibalLevelComponent.getCannibalLevel() == 21) {
						addStatusEffect(new StatusEffectInstance(StatusEffects.NAUSEA, 200));
						addStatusEffect(new StatusEffectInstance(StatusEffects.BLINDNESS, 200));
					}
				}
				if (ModConfig.enablePiglutton) {
					PigluttonEntity.attemptSpawn(this, cannibalLevelComponent.getCannibalLevel(), FleshItem.isOwnerPlayer(stack) && getName().getString().equals(FleshItem.getOwnerName(stack)));
				}
			} else {
				if (!tetheredComponent.isTethered() && cannibalLevelComponent.getCannibalLevel() > 0) {
					cannibalLevelComponent.setCannibalLevel(Math.max(0, cannibalLevelComponent.getCannibalLevel() - 1));
					cannibalLevelComponent.updateAttributes();
				}
				if (!world.isClient && cannibalLevelComponent.getCannibalLevel() >= 20) {
					ModEntityComponents.playerCannibalLevel = cannibalLevelComponent.getCannibalLevel();
				}
			}
		}
	}

	@ModifyReturnValue(method = "canEquip", at = @At("RETURN"))
	private boolean anthropophagy$preventArmorDispensing(boolean original, ItemStack stack) {
		if (original && !ModEntityComponents.CANNIBAL_LEVEL.get(this).canEquip(stack)) {
			return false;
		}
		return original;
	}
}

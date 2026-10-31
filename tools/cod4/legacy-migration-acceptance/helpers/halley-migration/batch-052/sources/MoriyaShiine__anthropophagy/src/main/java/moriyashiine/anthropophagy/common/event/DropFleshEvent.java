/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.event;

import moriyashiine.anthropophagy.common.ModConfig;
import moriyashiine.anthropophagy.common.entity.PigluttonEntity;
import moriyashiine.anthropophagy.common.item.FleshItem;
import moriyashiine.anthropophagy.common.tag.ModItemTags;
import moriyashiine.anthropophagy.common.util.FleshDropEntry;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.item.ItemStack;

public class DropFleshEvent implements ServerLivingEntityEvents.AllowDamage {
	public static float attackCooldown = -1;

	@Override
	public boolean allowDamage(LivingEntity entity, DamageSource source, float amount) {
		if (attackCooldown != -1 && attackCooldown < 0.7F) {
			return true;
		}
		if (source.getAttacker() instanceof PigluttonEntity || (source.getSource() instanceof LivingEntity living && living.getMainHandStack().isIn(ModItemTags.KNIVES))) {
			for (EntityType<?> entityType : FleshDropEntry.DROP_MAP.keySet()) {
				if (entity.getType() == entityType && entity.getWorld().random.nextFloat() * ModConfig.damageNeededForGuaranteedFleshDrop < amount) {
					FleshDropEntry entry = FleshDropEntry.DROP_MAP.get(entityType);
					ItemStack drop = new ItemStack(entity.getFireTicks() > 0 ? entry.cooked_drop() : entry.raw_drop());
					if (drop.getItem() instanceof FleshItem) {
						FleshItem.setOwner(drop, entity);
					}
					entity.dropStack(drop).setPickupDelay(40);
				}
			}
		}
		return true;
	}
}

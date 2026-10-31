/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.component.entity;

import moriyashiine.anthropophagy.common.init.ModEntityComponents;
import net.minecraft.entity.EquipmentSlot;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.attribute.EntityAttribute;
import net.minecraft.entity.attribute.EntityAttributeModifier;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ArmorItem;
import net.minecraft.item.ElytraItem;
import net.minecraft.item.ItemStack;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.registry.RegistryWrapper;
import net.minecraft.registry.entry.RegistryEntry;
import net.minecraft.util.Pair;
import net.minecraft.util.math.MathHelper;
import org.ladysnake.cca.api.v3.component.sync.AutoSyncedComponent;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class CannibalLevelComponent implements AutoSyncedComponent {
	public static final int MAX_LEVEL = 120;
	private static final int MIN_FUNCTIONAL_LEVEL = 30;
	private static final float MAX_FUNCTIONAL_LEVEL = MAX_LEVEL - MIN_FUNCTIONAL_LEVEL;

	private static final UUID ATTACK_DAMAGE_UUID = UUID.fromString("93e0b453-db2e-47ed-af22-c9d61f7199b9");
	private static final UUID ARMOR_UUID = UUID.fromString("5f263444-8723-45f1-bdb7-509d7c135a3c");
	private static final UUID KNOCKBACK_RESISTANCE_UUID = UUID.fromString("3372742b-db21-4824-b810-3815d738ce6b");
	private static final UUID MOVEMENT_SPEED_UUID = UUID.fromString("317f8550-84d3-405b-a1c7-34d83c3bae1c");
	private static final UUID SAFE_FALL_DISTANCE_UUID = UUID.fromString("d6842570-7e0a-4c81-83ef-9952173f6af4");
	private static final UUID STEP_HEIGHT_UUID = UUID.fromString("f96eca30-12ef-4089-a5c8-def0d38d83d0");

	private final PlayerEntity obj;
	private int cannibalLevel = 0;

	public CannibalLevelComponent(PlayerEntity obj) {
		this.obj = obj;
	}

	@Override
	public void readFromNbt(NbtCompound tag, RegistryWrapper.WrapperLookup registryLookup) {
		cannibalLevel = tag.getInt("CannibalLevel");
	}

	@Override
	public void writeToNbt(NbtCompound tag, RegistryWrapper.WrapperLookup registryLookup) {
		tag.putInt("CannibalLevel", cannibalLevel);
	}

	public void sync() {
		ModEntityComponents.CANNIBAL_LEVEL.sync(obj);
	}

	public int getCannibalLevel() {
		return cannibalLevel;
	}

	public void setCannibalLevel(int cannibalLevel) {
		this.cannibalLevel = cannibalLevel;
	}

	public boolean canEquip(ItemStack stack) {
		if ((stack.getItem() instanceof ArmorItem armorItem && armorItem.getProtection() > 0) || stack.getItem() instanceof ElytraItem) {
			EquipmentSlot slot = LivingEntity.getPreferredEquipmentSlot(stack);
			if (cannibalLevel >= 30 && slot == EquipmentSlot.LEGS) {
				return false;
			} else if (cannibalLevel >= 50 && slot == EquipmentSlot.HEAD) {
				return false;
			} else if (cannibalLevel >= 70 && slot == EquipmentSlot.FEET) {
				return false;
			} else return cannibalLevel < 90 || slot != EquipmentSlot.CHEST;
		}
		return true;
	}

	public void updateAttributes() {
		if (!obj.getWorld().isClient) {
			for (ItemStack stack : obj.getEquippedItems()) {
				if (!canEquip(stack)) {
					obj.dropStack(stack.copyAndEmpty());
				}
			}
			obj.getAttributeInstance(EntityAttributes.GENERIC_ATTACK_DAMAGE).tryRemoveModifier(ATTACK_DAMAGE_UUID);
			obj.getAttributeInstance(EntityAttributes.GENERIC_ARMOR).tryRemoveModifier(ARMOR_UUID);
			obj.getAttributeInstance(EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE).tryRemoveModifier(KNOCKBACK_RESISTANCE_UUID);
			obj.getAttributeInstance(EntityAttributes.GENERIC_MOVEMENT_SPEED).tryRemoveModifier(MOVEMENT_SPEED_UUID);
			obj.getAttributeInstance(EntityAttributes.GENERIC_SAFE_FALL_DISTANCE).tryRemoveModifier(SAFE_FALL_DISTANCE_UUID);
			obj.getAttributeInstance(EntityAttributes.GENERIC_STEP_HEIGHT).tryRemoveModifier(STEP_HEIGHT_UUID);
			getModifiersForLevel(cannibalLevel).attributes().forEach(pair -> obj.getAttributeInstance(pair.getLeft()).addPersistentModifier(pair.getRight()));
		}
	}

	public float getJumpBoost() {
		if (compareLevel(obj, 90, MAX_LEVEL + 1)) {
			return 0.3F;
		} else if (compareLevel(obj, 70, 90)) {
			return 0.23F;
		} else if (compareLevel(obj, 50, 70)) {
			return 0.16F;
		} else if (compareLevel(obj, 30, 50)) {
			return 0.09F;
		}
		return 0;
	}

	private static AttributeModifierSet getModifiersForLevel(int level) {
		AttributeModifierSet attributes = new AttributeModifierSet(new ArrayList<>());
		if (level > MIN_FUNCTIONAL_LEVEL) {
			attributes.addModifier(EntityAttributes.GENERIC_ATTACK_DAMAGE,
					new EntityAttributeModifier(ATTACK_DAMAGE_UUID,
							"Cannibal modifier",
							lerp(level, 6),
							EntityAttributeModifier.Operation.ADD_VALUE));
			attributes.addModifier(EntityAttributes.GENERIC_ARMOR,
					new EntityAttributeModifier(ARMOR_UUID,
							"Cannibal modifier",
							lerp(level, 14),
							EntityAttributeModifier.Operation.ADD_VALUE));
			attributes.addModifier(EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE,
					new EntityAttributeModifier(KNOCKBACK_RESISTANCE_UUID,
							"Cannibal modifier",
							lerp(level, 0.2F),
							EntityAttributeModifier.Operation.ADD_VALUE));
			attributes.addModifier(EntityAttributes.GENERIC_MOVEMENT_SPEED,
					new EntityAttributeModifier(MOVEMENT_SPEED_UUID,
							"Cannibal modifier",
							lerp(level, 0.5F),
							EntityAttributeModifier.Operation.ADD_MULTIPLIED_TOTAL));
			attributes.addModifier(EntityAttributes.GENERIC_SAFE_FALL_DISTANCE,
					new EntityAttributeModifier(SAFE_FALL_DISTANCE_UUID,
							"Cannibal modifier",
							lerp(level, 4),
							EntityAttributeModifier.Operation.ADD_VALUE));
			if (level >= 60) {
				attributes.addModifier(EntityAttributes.GENERIC_STEP_HEIGHT,
						new EntityAttributeModifier(STEP_HEIGHT_UUID,
								"Cannibal modifier",
								1,
								EntityAttributeModifier.Operation.ADD_VALUE));
			}
		}
		attributes.attributes().removeIf(pair -> pair.getRight().value() == 0);
		return attributes;
	}

	private static float lerp(int level, float end) {
		return MathHelper.lerp(Math.min(1, (level - MIN_FUNCTIONAL_LEVEL) / (MAX_FUNCTIONAL_LEVEL - MIN_FUNCTIONAL_LEVEL)), 0, end);
	}

	private static int lerp(int level, int end) {
		return MathHelper.lerp(Math.min(1, (level - MIN_FUNCTIONAL_LEVEL) / (MAX_FUNCTIONAL_LEVEL - MIN_FUNCTIONAL_LEVEL)), 0, end);
	}

	private static boolean compareLevel(PlayerEntity player, int minInc, int maxExc) {
		int level = ModEntityComponents.CANNIBAL_LEVEL.get(player).getCannibalLevel();
		return level >= minInc && level < maxExc;
	}

	private record AttributeModifierSet(
			List<Pair<RegistryEntry<EntityAttribute>, EntityAttributeModifier>> attributes) {
		void addModifier(RegistryEntry<EntityAttribute> attribute, EntityAttributeModifier modifier) {
			attributes().add(new Pair<>(attribute, modifier));
		}
	}
}

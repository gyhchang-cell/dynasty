/*
 * Copyright (c) MoriyaShiine. All Rights Reserved.
 */
package moriyashiine.anthropophagy.common.entity;

import moriyashiine.anthropophagy.common.entity.ai.goal.*;
import moriyashiine.anthropophagy.common.entity.ai.pathing.BetterMobNavigation;
import moriyashiine.anthropophagy.common.init.ModEntityTypes;
import moriyashiine.anthropophagy.common.init.ModSoundEvents;
import moriyashiine.anthropophagy.common.tag.ModBlockTags;
import moriyashiine.anthropophagy.common.tag.ModEntityTypeTags;
import net.minecraft.block.BlockState;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.SpawnReason;
import net.minecraft.entity.ai.goal.*;
import net.minecraft.entity.ai.pathing.PathNodeType;
import net.minecraft.entity.attribute.DefaultAttributeContainer;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.damage.DamageSource;
import net.minecraft.entity.mob.HostileEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.particle.ParticleTypes;
import net.minecraft.server.world.ServerWorld;
import net.minecraft.sound.SoundCategory;
import net.minecraft.sound.SoundEvent;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Box;
import net.minecraft.util.math.MathHelper;
import net.minecraft.util.math.random.Random;
import net.minecraft.world.GameRules;
import net.minecraft.world.ServerWorldAccess;
import net.minecraft.world.World;

public class PigluttonEntity extends HostileEntity {
	private static final int DAMAGE_THRESHOLD = 20;

	public boolean canAttack = false;
	public int fleeDistance = 0, overhealAmount = 0, stalkTicks = 0;
	private float damageTaken = 0;
	private int fleeingTicks = 0;

	public PigluttonEntity(EntityType<? extends HostileEntity> entityType, World world) {
		super(entityType, world);
		navigation = new BetterMobNavigation(this, getWorld(), 1);
		experiencePoints = 30;
		setPathfindingPenalty(PathNodeType.LEAVES, 0);
		setPathfindingPenalty(PathNodeType.WATER, -1);
	}

	public static DefaultAttributeContainer.Builder buildAttributes() {
		return HostileEntity.createHostileAttributes()
				.add(EntityAttributes.GENERIC_MAX_HEALTH, 80)
				.add(EntityAttributes.GENERIC_ARMOR, 14)
				.add(EntityAttributes.GENERIC_ATTACK_DAMAGE, 32)
				.add(EntityAttributes.GENERIC_MOVEMENT_SPEED, 0.6)
				.add(EntityAttributes.GENERIC_KNOCKBACK_RESISTANCE, 0.8)
				.add(EntityAttributes.GENERIC_FOLLOW_RANGE, 64)
				.add(EntityAttributes.GENERIC_STEP_HEIGHT, 1);
	}

	public static boolean canSpawn(EntityType<PigluttonEntity> type, ServerWorldAccess world, SpawnReason spawnReason, BlockPos pos, Random random) {
		return random.nextInt(8) == 0 && HostileEntity.canSpawnInDark(type, world, spawnReason, pos, random);
	}

	@Override
	public void readCustomDataFromNbt(NbtCompound nbt) {
		super.readCustomDataFromNbt(nbt);
		canAttack = nbt.getBoolean("CanAttack");
		damageTaken = nbt.getFloat("DamageTaken");
		if (nbt.contains("FleeDistance")) {
			fleeDistance = nbt.getInt("FleeDistance");
		} else {
			fleeDistance = 6;
		}
		overhealAmount = nbt.getInt("OverhealAmount");
		stalkTicks = nbt.getInt("StalkTicks");
		fleeingTicks = nbt.getInt("FleeingTicks");
	}

	@Override
	public void writeCustomDataToNbt(NbtCompound nbt) {
		super.writeCustomDataToNbt(nbt);
		nbt.putBoolean("CanAttack", canAttack);
		nbt.putFloat("DamageTaken", damageTaken);
		nbt.putInt("FleeDistance", fleeDistance);
		nbt.putInt("OverhealAmount", overhealAmount);
		nbt.putInt("StalkTicks", stalkTicks);
		nbt.putInt("FleeingTicks", fleeingTicks);
	}

	@Override
	protected void initGoals() {
		goalSelector.add(0, new SwimGoal(this));
		goalSelector.add(1, new EatFleshGoal(this));
		goalSelector.add(2, new StalkGoal(this));
		goalSelector.add(2, new FleeGoal(this));
		goalSelector.add(3, new PigluttonMeleeAttackGoal(this, 1, true));
		goalSelector.add(4, new PigluttonWanderAroundFarGoal(this, 1 / 6F));
		goalSelector.add(5, new LookAtEntityGoal(this, PlayerEntity.class, 16));
		goalSelector.add(5, new LookAroundGoal(this));
		targetSelector.add(0, new RevengeGoal(this));
		targetSelector.add(1, new ActiveTargetGoal<>(this, LivingEntity.class, 10, true, false, living -> !isFleeing() && living.getType().isIn(ModEntityTypeTags.PIGLUTTON_TARGETS)));
	}

	@Override
	protected void mobTick() {
		super.mobTick();
		if (fleeingTicks > 0) {
			fleeingTicks--;
			if (fleeingTicks < 160 && fleeingTicks % 20 == 0) {
				getWorld().playSound(null, getBlockPos(), ModSoundEvents.ENTITY_PIGLUTTON_FLEE, getSoundCategory(), getSoundVolume() * 4, getSoundPitch());
			}
			if (fleeingTicks == 160) {
				((ServerWorld) getWorld()).spawnParticles(ParticleTypes.SMOKE,
						getX(), getY(), getZ(),
						64,
						getWidth() / 2, getHeight() / 2, getWidth() / 2,
						0);
				discard();
			}
		}
	}

	@Override
	public void tickMovement() {
		super.tickMovement();
		if (!getWorld().isClient && horizontalCollision && getWorld().getGameRules().getBoolean(GameRules.DO_MOB_GRIEFING)) {
			Box box = getBoundingBox().expand(0.2);
			for (BlockPos pos : BlockPos.iterate(MathHelper.floor(box.minX), MathHelper.floor(box.minY), MathHelper.floor(box.minZ), MathHelper.floor(box.maxX), MathHelper.floor(box.maxY), MathHelper.floor(box.maxZ))) {
				BlockState state = getWorld().getBlockState(pos);
				float hardness = state.getHardness(getWorld(), pos);
				if (hardness >= 0 && (hardness < 0.5F || state.isIn(ModBlockTags.PIGLUTTON_BREAKABLE))) {
					getWorld().breakBlock(pos, true);
				}
			}
		}
	}

	@Override
	protected SoundEvent getAmbientSound() {
		return ModSoundEvents.ENTITY_PIGLUTTON_AMBIENT;
	}

	@Override
	protected SoundEvent getHurtSound(DamageSource source) {
		return ModSoundEvents.ENTITY_PIGLUTTON_HURT;
	}

	@Override
	protected SoundEvent getDeathSound() {
		return ModSoundEvents.ENTITY_PIGLUTTON_DEATH;
	}

	@Override
	protected Box getAttackBox() {
		return super.getAttackBox().expand(0.25, 0, 0.25);
	}

	@Override
	protected float modifyAppliedDamage(DamageSource source, float amount) {
		float damage = super.modifyAppliedDamage(source, amount);
		damageTaken += damage;
		fleeDistance = 6;
		fleeingTicks = 0;
		if (damageTaken >= DAMAGE_THRESHOLD) {
			startFleeing();
		}
		return damage;
	}

	@Override
	public boolean cannotDespawn() {
		return true;
	}

	@Override
	public boolean disablesShield() {
		return true;
	}

	public boolean isFleeing() {
		return fleeingTicks > 0;
	}

	public void startFleeing() {
		damageTaken = 0;
		fleeingTicks = 160;
	}

	public void runAwayAndDespawn() {
		fleeDistance = 64;
		fleeingTicks = 400;
	}

	public static void attemptSpawn(LivingEntity living, int cannibalLevel, boolean ownFlesh) {
		if (living.getWorld().isClient) {
			return;
		}
		float chance = (Math.min(90, cannibalLevel) - 40) / 800F;
		if (ownFlesh) {
			chance *= 3;
		}
		if (living.getRandom().nextFloat() < chance) {
			PigluttonEntity piglutton = ModEntityTypes.PIGLUTTON.create(living.getWorld());
			if (piglutton != null) {
				final int minH = 16, maxH = 32;
				for (int i = 0; i < 8; i++) {
					int dX = living.getRandom().nextBetween(minH, maxH) * (living.getRandom().nextBoolean() ? 1 : -1);
					int dY = living.getRandom().nextBetween(-6, 6);
					int dZ = living.getRandom().nextBetween(minH, maxH) * (living.getRandom().nextBoolean() ? 1 : -1);
					if (piglutton.teleport(living.getX() + dX, living.getY() + dY, living.getZ() + dZ, false)) {
						living.getWorld().spawnEntity(piglutton);
						piglutton.setTarget(living);
						living.getWorld().playSoundFromEntity(null, piglutton, ModSoundEvents.ENTITY_PIGLUTTON_SPAWN, SoundCategory.HOSTILE, 1, 1);
						return;
					}
				}
			}
		}
	}
}

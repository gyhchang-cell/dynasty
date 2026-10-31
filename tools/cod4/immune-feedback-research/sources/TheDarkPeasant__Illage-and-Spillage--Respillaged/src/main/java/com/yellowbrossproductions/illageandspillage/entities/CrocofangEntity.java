package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.Goal.Flag;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.fluids.FluidType;
import net.minecraftforge.registries.ForgeRegistries;
import org.jetbrains.annotations.Nullable;

import java.util.*;

public class CrocofangEntity extends Raider implements ICanBeAnimated {
    private static final UUID SPEED_PENALTY_UUID = UUID.fromString("5BD14A52-AB9A-42D3-A649-90FDE044281E");
    private static final AttributeModifier SPEED_PENALTY;
    private static final EntityDataAccessor<Integer> ANIMATION_STATE;
    private static final EntityDataAccessor<Boolean> TRIED_SPAWN;
    private static final EntityDataAccessor<Boolean> CHARGING;
    public AnimationState attackAnimationState = new AnimationState();
    public AnimationState prechargeAnimationState = new AnimationState();
    public AnimationState chargeAnimationState = new AnimationState();
    public AnimationState stunnedAnimationState = new AnimationState();
    private int biteTime;
    private int chargeTime;
    private int stunnedTime;
    double chargeX;
    double chargeZ;

    public CrocofangEntity(EntityType<? extends Raider> p_37839_, Level p_37840_) {
        super(p_37839_, p_37840_);
        this.xpReward = 5;
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new StunGoal());
        this.goalSelector.addGoal(0, new ChargeGoal());
        this.goalSelector.addGoal(0, new AttackGoal());
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.4));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 6.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 8.0F));
        this.targetSelector.addGoal(2, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, true, (p_199899_) -> !p_199899_.isBaby()));
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    protected void updateControlFlags() {
        boolean flag = !(this.getControllingPassenger() instanceof Mob) || this.getControllingPassenger().getType().is(EntityTypeTags.RAIDERS);
        boolean flag1 = !(this.getVehicle() instanceof Boat);
        this.goalSelector.setControlFlag(Flag.MOVE, flag);
        this.goalSelector.setControlFlag(Flag.JUMP, flag && flag1);
        this.goalSelector.setControlFlag(Flag.LOOK, flag);
        this.goalSelector.setControlFlag(Flag.TARGET, flag);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 40.0).add(Attributes.ATTACK_DAMAGE, 8.0).add(Attributes.ATTACK_KNOCKBACK, 1.5).add(Attributes.FOLLOW_RANGE, 32.0).add(Attributes.ARMOR, 3.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(TRIED_SPAWN, false);
        this.entityData.define(CHARGING, false);
    }

    public void addAdditionalSaveData(CompoundTag p_37870_) {
        super.addAdditionalSaveData(p_37870_);
        if (this.hasAlreadyTriedSpawn()) {
            p_37870_.putBoolean("HasAlreadyTriedSpawn", true);
        }

    }

    public void readAdditionalSaveData(CompoundTag p_37862_) {
        super.readAdditionalSaveData(p_37862_);
        this.setTriedSpawn(p_37862_.getBoolean("HasAlreadyTriedSpawn"));
    }

    public double getPassengersRidingOffset() {
        return this.stunnedTime > 0 ? 1.15 : super.getPassengersRidingOffset() * 1.15;
    }

    public void applyRaidBuffs(int p_37844_, boolean p_37845_) {
    }

    public boolean canBeRiddenUnderFluidType(FluidType type, Entity rider) {
        return true;
    }

    public boolean canBeLeader() {
        return false;
    }

    public boolean hasAlreadyTriedSpawn() {
        return this.entityData.get(TRIED_SPAWN);
    }

    public void setTriedSpawn(boolean triedSpawn) {
        this.entityData.set(TRIED_SPAWN, triedSpawn);
    }

    public boolean isCharging() {
        return this.entityData.get(CHARGING);
    }

    public void setCharging(boolean charging) {
        this.entityData.set(CHARGING, charging);
    }

    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_CROCOFANG_AMBIENT.get();
    }

    public float getStepHeight() {
        return 1.0F;
    }

    protected @Nullable SoundEvent getAmbientSound() {
        return IllageAndSpillageSoundEvents.ENTITY_CROCOFANG_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_33034_) {
        return IllageAndSpillageSoundEvents.ENTITY_CROCOFANG_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_CROCOFANG_DEATH.get();
    }

    public void tick() {
        super.tick();
        if (!Config.CommonConfig.ULTIMATE_NIGHTMARE.get() && !this.hasAlreadyTriedSpawn()) {
            if (this.getPassengers().isEmpty()) {
                this.spawnMob();
            }

            this.setTriedSpawn(true);
        }

        if (this.chargeTime <= 0 && this.stunnedTime <= 0) {
            (Objects.requireNonNull(this.getAttribute(Attributes.MOVEMENT_SPEED))).removeModifier(SPEED_PENALTY);
        } else {
            AttributeInstance $$4 = this.getAttribute(Attributes.MOVEMENT_SPEED);

            assert $$4 != null;

            $$4.removeModifier(SPEED_PENALTY);
            $$4.addTransientModifier(SPEED_PENALTY);
        }

        if (this.isAlive()) {
            if (this.biteTime > 0) {
                --this.biteTime;
                if (this.biteTime == 11) {
                    float f1 = (float) this.getAttributeValue(Attributes.ATTACK_KNOCKBACK);
                    float radius2 = 2.0F;
                    double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                    double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                    List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, new AABB(x - 1.0, this.getY(), z - 1.0, x + 1.0, this.getY() + 1.0, z + 1.0));

                    for (LivingEntity caught : list) {
                        if (caught != this && caught.isAlive() && EntityUtil.canHurtThisMob(caught, this)) {
                            caught.hurt(this.damageSources().mobAttack(this), (float) (Objects.requireNonNull(this.getAttribute(Attributes.ATTACK_DAMAGE))).getBaseValue());
                            caught.knockback((f1 * 0.5F), Mth.sin(this.getYRot() * 0.017453292F), (-Mth.cos(this.getYRot() * 0.017453292F)));
                        }
                    }
                }
            }

            if (this.chargeTime > 0) {
                ++this.chargeTime;
                this.setYRot(this.getYHeadRot());
                this.yBodyRot = this.getYRot();
                if (this.getTarget() != null) {
                    LivingEntity t = this.getTarget();
                    double chargeX = this.getX() - t.getX();
                    double chargeY = this.getY() - t.getY();
                    double chargeZ = this.getZ() - t.getZ();
                    double charged = Math.sqrt(chargeX * chargeX + chargeY * chargeY + chargeZ * chargeZ);
                    float power = 3.8F;
                    double motionX = this.getDeltaMovement().x - chargeX / charged * (double) power * 0.2;
                    double motionZ = this.getDeltaMovement().z - chargeZ / charged * (double) power * 0.2;
                    if (this.chargeTime == 30) {
                        if (!this.level().isClientSide) {
                            this.setCharging(true);
                        }
                        this.setAnimationState(3);
                        this.setCharge(motionX, motionZ);
                        EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_CROCOFANG_CHARGE.get(), 3.0F, 1.0F, false);
                    }

                    if (this.chargeTime > 30 && this.chargeTime <= 64) {
                        this.setDeltaMovement(this.chargeX, this.getDeltaMovement().y, this.chargeZ);

                        for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                            if (EntityUtil.canHurtThisMob(entity, this) && entity instanceof LivingEntity && entity.isAlive()) {
                                double x = this.getX() - entity.getX();
                                double y = this.getY() - entity.getY();
                                double z = this.getZ() - entity.getZ();
                                double d = Math.sqrt(x * x + y * y + z * z);
                                if (this.distanceToSqr(entity) < 9.0) {
                                    if (entity.invulnerableTime <= 0) {
                                        this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                                        entity.hurt(this.damageSources().mobAttack(this), 8.0F);
                                        entity.hurtMarked = true;
                                        entity.setDeltaMovement(-x / d * 2.0, -y / d * 2.0 + 0.5, -z / d * 2.0);
                                    }

                                    if (((LivingEntity) entity).isBlocking()) {
                                        EntityUtil.disableShield((LivingEntity) entity, 100);
                                        this.playSound(SoundEvents.SHIELD_BLOCK, 1.0F, 0.7F);
                                        this.hurt(this.damageSources().mobAttack((LivingEntity) entity), 4.0F);
                                        this.setAnimationState(4);
                                        if (!this.level().isClientSide) {
                                            this.setCharging(false);
                                        }

                                        this.chargeTime = 0;
                                        this.stunnedTime = 120;
                                    }
                                }
                            }
                        }

                        if (this.horizontalCollision) {
                            this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 0.7F);
                            this.hurt(this.damageSources().generic(), 4.0F);
                            this.setAnimationState(4);
                            if (!this.level().isClientSide) {
                                this.setCharging(false);
                            }

                            this.chargeTime = 0;
                            this.stunnedTime = 120;
                        }
                    }
                }

                if (this.chargeTime >= 70) {
                    this.chargeAnimationState.stop();
                    this.setAnimationState(0);
                    if (!this.level().isClientSide) {
                        this.setCharging(false);
                    }

                    this.chargeTime = 0;
                }
            }
        }

        if (this.stunnedTime > 0) {
            --this.stunnedTime;
        }

    }

    public void setCharge(double x, double z) {
        this.chargeX = x;
        this.chargeZ = z;
    }

    public @Nullable SpawnGroupData finalizeSpawn(ServerLevelAccessor p_37856_, DifficultyInstance p_37857_, MobSpawnType p_37858_, @Nullable SpawnGroupData p_37859_, @Nullable CompoundTag p_37860_) {
        return super.finalizeSpawn(p_37856_, p_37857_, p_37858_, p_37859_, p_37860_);
    }

    private void spawnMob() {
        BlockPos blockPos = this.getOnPos();
        this.summonMobFromConfig(blockPos);
    }

    private void summonMobFromConfig(BlockPos blockPos) {
        List<? extends String> mobSpawns = Config.CommonConfig.crocofang_rideableMobs.get();
        if (!mobSpawns.isEmpty()) {
            Collections.shuffle(mobSpawns);
            int randomIndex = this.getRandom().nextInt(mobSpawns.size());
            String randomMobID = mobSpawns.get(randomIndex);
            EntityType<?> entityType = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(randomMobID));
            if (entityType != null) {
                Entity entity = entityType.create(this.level());
                if (entity instanceof Mob mobEntity && !(entity instanceof CrocofangEntity)) {
                    DifficultyInstance difficultyForLocation = this.level().getCurrentDifficultyAt(blockPos.above());
                    mobEntity.moveTo(blockPos.above(), this.getYRot(), 0.0F);
                    mobEntity.startRiding(this, false);
                    if (!this.level().isClientSide) {
                        mobEntity.finalizeSpawn((ServerLevelAccessor) this.level(), difficultyForLocation, MobSpawnType.EVENT, null, null);
                    }

                    if (mobEntity instanceof Raider) {
                        ((Raider) mobEntity).setCanJoinRaid(true);
                    }

                    this.level().addFreshEntity(mobEntity);
                }
            }
        }
    }

    public boolean doHurtTarget(Entity p_21372_) {
        if (this.biteTime < 1 && this.chargeTime < 1 && this.stunnedTime < 1) {
            this.attackAnimationState.stop();
            this.setAnimationState(0);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_CROCOFANG_BITE.get(), 1.0F, 1.0F);
            this.biteTime = 20;
            this.setAnimationState(1);
        }

        return false;
    }

    public void setAnimationState(int input) {
        this.entityData.set(ANIMATION_STATE, input);
    }

    public AnimationState getAnimationState(String input) {
        if (Objects.equals(input, "attack")) {
            return this.attackAnimationState;
        } else if (Objects.equals(input, "precharge")) {
            return this.prechargeAnimationState;
        } else if (Objects.equals(input, "charge")) {
            return this.chargeAnimationState;
        } else {
            return Objects.equals(input, "stunned") ? this.stunnedAnimationState : new AnimationState();
        }
    }

    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                default -> {
                }
                case 0, 1 -> {
                    this.chargeAnimationState.stop();
                    this.attackAnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.attackAnimationState.stop();
                    this.prechargeAnimationState.start(this.tickCount);
                }
                case 3 -> {
                    this.prechargeAnimationState.stop();
                    this.chargeAnimationState.start(this.tickCount);
                }
                case 4 -> {
                    this.chargeAnimationState.stop();
                    this.stunnedAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    public boolean hurt(DamageSource p_37849_, float p_37850_) {
        return !this.getPassengers().contains(p_37849_.getEntity()) && super.hurt(p_37849_, p_37850_);
    }

    static {
        ANIMATION_STATE = SynchedEntityData.defineId(CrocofangEntity.class, EntityDataSerializers.INT);
        TRIED_SPAWN = SynchedEntityData.defineId(CrocofangEntity.class, EntityDataSerializers.BOOLEAN);
        CHARGING = SynchedEntityData.defineId(CrocofangEntity.class, EntityDataSerializers.BOOLEAN);
        SPEED_PENALTY = new AttributeModifier(SPEED_PENALTY_UUID, "STOP MOVING AROUND STUPID", -0.35, Operation.ADDITION);
    }

    class StunGoal extends Goal {
        public boolean canUse() {
            return CrocofangEntity.this.stunnedTime > 0;
        }

        public boolean canContinueToUse() {
            return CrocofangEntity.this.stunnedTime > 0;
        }

        public StunGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public void tick() {
            CrocofangEntity.this.getNavigation().stop();
            CrocofangEntity.this.navigation.stop();
        }

        public void stop() {
            CrocofangEntity.this.stunnedAnimationState.stop();
            CrocofangEntity.this.setAnimationState(0);
        }
    }

    class ChargeGoal extends Goal {
        public boolean canUse() {
            return CrocofangEntity.this.biteTime < 1 && CrocofangEntity.this.getTarget() != null && CrocofangEntity.this.hasLineOfSight(CrocofangEntity.this.getTarget()) && CrocofangEntity.this.random.nextFloat() * 75.0F < 0.9F && CrocofangEntity.this.distanceToSqr(CrocofangEntity.this.getTarget()) > 27.0 && CrocofangEntity.this.stunnedTime < 1;
        }

        public boolean canContinueToUse() {
            return CrocofangEntity.this.chargeTime > 0;
        }

        public void start() {
            CrocofangEntity.this.attackAnimationState.stop();
            CrocofangEntity.this.setAnimationState(2);
            CrocofangEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_CROCOFANG_PREPARE_CHARGE.get(), 3.0F, 1.0F);
            CrocofangEntity.this.chargeTime = 1;
        }

        public ChargeGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public void tick() {
            CrocofangEntity.this.getNavigation().stop();
            if (CrocofangEntity.this.getTarget() != null && CrocofangEntity.this.chargeTime < 30) {
                CrocofangEntity.this.getLookControl().setLookAt(CrocofangEntity.this.getTarget(), 100.0F, 100.0F);
            }

            CrocofangEntity.this.navigation.stop();
        }
    }

    class AttackGoal extends Goal {
        public boolean canUse() {
            return CrocofangEntity.this.biteTime > 0;
        }

        public boolean canContinueToUse() {
            return CrocofangEntity.this.biteTime > 0;
        }

        public AttackGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public void tick() {
            CrocofangEntity.this.getNavigation().stop();
            if (CrocofangEntity.this.getTarget() != null) {
                CrocofangEntity.this.getLookControl().setLookAt(CrocofangEntity.this.getTarget(), 100.0F, 100.0F);
            }

            CrocofangEntity.this.navigation.stop();
        }
    }
}

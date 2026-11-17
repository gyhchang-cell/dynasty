package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.AABB;

import javax.annotation.Nullable;
import java.util.EnumSet;
import java.util.List;
import java.util.Objects;

public class AbsorberEntity extends AbstractIllager implements ICanBeAnimated {
    private static final EntityDataAccessor<Integer> ATTACK_TICKS;
    private static final EntityDataAccessor<Integer> ANIMATION_STATE;
    public AnimationState attackAnimationState = new AnimationState();
    public AnimationState deathAnimationState = new AnimationState();

    public AbsorberEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 10;
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new AttackGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(2, new Raider.HoldGroundAttackGoal(this, 10.0F));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.15000000596046448).add(Attributes.MAX_HEALTH, 100.0).add(Attributes.ATTACK_DAMAGE, 15.0).add(Attributes.FOLLOW_RANGE, 32.0).add(Attributes.KNOCKBACK_RESISTANCE, 1.0).add(Attributes.ATTACK_KNOCKBACK, 2.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ATTACK_TICKS, 0);
        this.entityData.define(ANIMATION_STATE, 0);
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public void tick() {
        super.tick();
        if (this.hurtTime >= 3) {
            this.hurtTime = 2;
        }

        if (this.isAlive() && this.getAttackAnimationTick() > 0) {
            if (!this.level().isClientSide) {
                this.setAttackAnimationTick(this.getAttackAnimationTick() - 1);
            }

            this.setYRot(this.getYHeadRot());
            this.yBodyRot = this.getYRot();
            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
            if (this.getTarget() != null) {
                this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
            }

            if (this.getAttackAnimationTick() == 10) {
                this.playSound(SoundEvents.GENERIC_EXPLODE, 2.0F, 1.0F);
                float radius2 = 1.5F;
                double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, new AABB(x - 2.0, this.getY(), z - 2.0, x + 2.0, this.getY() + 2.0, z + 2.0));

                for (LivingEntity caught : list) {
                    if (caught != this && caught.isAlive()) {
                        caught.hurt(this.damageSources().mobAttack(this), (float) (Objects.requireNonNull(this.getAttribute(Attributes.ATTACK_DAMAGE))).getBaseValue());
                        caught.lerpMotion(caught.getDeltaMovement().x, caught.getDeltaMovement().y + 0.3, caught.getDeltaMovement().z);
                        caught.setDeltaMovement(caught.getDeltaMovement().add(0.0, 0.3, 0.0));
                        EntityUtil.disableShield(caught, 200);
                    }
                }
            }
        }

    }

    public int getAttackAnimationTick() {
        return this.entityData.get(ATTACK_TICKS);
    }

    public void setAttackAnimationTick(int attackAnimationTick) {
        this.entityData.set(ATTACK_TICKS, attackAnimationTick);
    }

    @Nullable
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor p_213386_1_, DifficultyInstance p_213386_2_, MobSpawnType p_213386_3_, @Nullable SpawnGroupData p_213386_4_, @Nullable CompoundTag p_213386_5_) {
        return super.finalizeSpawn(p_213386_1_, p_213386_2_, p_213386_3_, p_213386_4_, p_213386_5_);
    }

    public void die(DamageSource p_37847_) {
        this.setAnimationState(2);
        super.die(p_37847_);
    }

    protected void tickDeath() {
        ++this.deathTime;
        if (this.deathTime == 30) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_ABSORBER_COLLAPSE.get(), 1.0F, 1.0F);
        }

        if (this.deathTime == 90 && !this.level().isClientSide()) {
            this.level().broadcastEntityEvent(this, (byte) 60);
            this.remove(RemovalReason.KILLED);
        }

    }

    public float getStepHeight() {
        return 1.0F;
    }

    public boolean hurt(DamageSource source, float p_37850_) {
        if (!(Boolean) Config.CommonConfig.absorber_damageMode.get()) {
            if (!source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
                p_37850_ = 1.0F;
            }
        } else if (!source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL) && p_37850_ > 1.0F) {
            p_37850_ = 1.0F;
        }

        return super.hurt(source, p_37850_);
    }

    protected float getStandingEyeHeight(Pose p_21131_, EntityDimensions p_21132_) {
        return 2.5625F;
    }

    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_ABSORBER_AMBIENT.get();
    }

    protected SoundEvent getAmbientSound() {
        return IllageAndSpillageSoundEvents.ENTITY_ABSORBER_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_ABSORBER_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_ABSORBER_DEATH.get();
    }

    public float getVoicePitch() {
        return this.isDeadOrDying() ? 1.0F : super.getVoicePitch();
    }

    public boolean doHurtTarget(Entity p_21372_) {
        if (this.getAttackAnimationTick() < 1) {
            this.attackAnimationState.stop();
            this.setAnimationState(0);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_ABSORBER_ATTACK.get(), 1.0F, 1.0F);
            if (!this.level().isClientSide) {
                this.setAttackAnimationTick(30);
            }

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
        } else {
            return Objects.equals(input, "death") ? this.deathAnimationState : new AnimationState();
        }
    }

    @Override
    public void calculateEntityAnimation(boolean p_268129_) {
        super.calculateEntityAnimation(p_268129_);
    }

    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                case 0:
                default:
                    break;
                case 1:
                    this.attackAnimationState.start(this.tickCount);
                    break;
                case 2:
                    this.attackAnimationState.stop();
                    this.deathAnimationState.start(this.tickCount);
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    public boolean canBeLeader() {
        return false;
    }

    static {
        ATTACK_TICKS = SynchedEntityData.defineId(AbsorberEntity.class, EntityDataSerializers.INT);
        ANIMATION_STATE = SynchedEntityData.defineId(AbsorberEntity.class, EntityDataSerializers.INT);
    }

    class AttackGoal extends Goal {
        public boolean canUse() {
            return AbsorberEntity.this.getAttackAnimationTick() > 0;
        }

        public boolean canContinueToUse() {
            return AbsorberEntity.this.getAttackAnimationTick() > 0;
        }

        public AttackGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public void tick() {
            AbsorberEntity.this.getNavigation().stop();
            AbsorberEntity.this.navigation.stop();
        }
    }
}

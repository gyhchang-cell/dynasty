package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.entities.goal.StareAtDeadFreakGoal;
import com.yellowbrossproductions.illageandspillage.entities.projectile.BoneEntity;
import com.yellowbrossproductions.illageandspillage.util.EffectRegisterer;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;
import java.util.Objects;

public class FunnyboneEntity extends Monster implements ICanBeAnimated, IllagerAttack {
    private static final EntityDataAccessor<Integer> ANIMATION_STATE = SynchedEntityData.defineId(FunnyboneEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> FLYING = SynchedEntityData.defineId(FunnyboneEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> GOOPY = SynchedEntityData.defineId(FunnyboneEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> SHOW_BONE = SynchedEntityData.defineId(FunnyboneEntity.class, EntityDataSerializers.BOOLEAN);
    public AnimationState idleAnimationState = new AnimationState();
    public AnimationState runAnimationState = new AnimationState();
    public AnimationState flyAnimationState = new AnimationState();
    public AnimationState spawnAnimationState = new AnimationState();
    public AnimationState throwAnimationState = new AnimationState();
    private LivingEntity owner;
    public boolean isThrowing;
    private int throwTicks;
    private int introTicks;
    private boolean circleDirection = true;
    protected int circleTick = 0;

    public FunnyboneEntity(EntityType<? extends Monster> p_33002_, Level p_33003_) {
        super(p_33002_, p_33003_);
        this.xpReward = 0;
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new StareAtDeadFreakGoal(this));
        this.goalSelector.addGoal(1, new FunnyboneAttackGoal(this, 8.0F));
        this.goalSelector.addGoal(8, new FunnyboneRandomStrollGoal(this, 0.3));
        this.goalSelector.addGoal(9, new FunnyboneLookAtEntityGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new FunnyboneLookAtEntityGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.9).add(Attributes.MAX_HEALTH, 8.0).add(Attributes.FOLLOW_RANGE, 16.0);
    }

    public void setOwner(LivingEntity owner) {
        this.owner = owner;
    }

    public LivingEntity getOwner() {
        return owner;
    }

    @Override
    public MobType getMobType() {
        return MobType.UNDEAD;
    }

    @Override
    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return (!this.isGoopy() || p_21197_.getEffect() != EffectRegisterer.MUTATION.get()) && super.canBeAffected(p_21197_);
    }

    @Override
    public float getVoicePitch() {
        return (this.random.nextFloat() - this.random.nextFloat()) * 0.2F + 1.5F;
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return this.isFlying() ? null : IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_FUNNYBONE_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource p_33034_) {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_FUNNYBONE_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_FUNNYBONE_DEATH.get();
    }

    @Override
    protected void playStepSound(BlockPos p_32159_, BlockState p_32160_) {
        this.playSound(SoundEvents.SKELETON_STEP, 0.15F, 1.0F);
    }

    @Override
    public void setTarget(@Nullable LivingEntity p_21544_) {
        if (this.owner != null && this.owner.isAlive() && this.owner instanceof Mob && p_21544_ == ((Mob) this.owner).getTarget()) {
            super.setTarget(p_21544_);
        } else if (this.owner == null || !this.owner.isAlive()) {
            super.setTarget(p_21544_);
        }
    }

    public void setAnimationState(int state) {
        this.entityData.set(ANIMATION_STATE, state);
    }

    public void setGoopy(boolean goopy) {
        this.entityData.set(GOOPY, goopy);
    }

    public boolean isGoopy() {
        return this.entityData.get(GOOPY);
    }

    public void setShowBone(boolean showBone) {
        this.entityData.set(SHOW_BONE, showBone);
    }

    public boolean shouldShowBone() {
        return this.entityData.get(SHOW_BONE);
    }

    public void setFlying(boolean flying) {
        this.entityData.set(FLYING, flying);
    }

    public boolean isFlying() {
        return this.entityData.get(FLYING);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(GOOPY, false);
        this.entityData.define(SHOW_BONE, false);
        this.entityData.define(FLYING, false);
    }

    public int getAnimationState() {
        return this.entityData.get(ANIMATION_STATE);
    }

    @Override
    public AnimationState getAnimationState(String var1) {
        if (Objects.equals(var1, "idle")) {
            return idleAnimationState;
        }
        if (Objects.equals(var1, "run")) {
            return runAnimationState;
        }
        if (Objects.equals(var1, "fly")) {
            return flyAnimationState;
        }
        if (Objects.equals(var1, "spawn")) {
            return spawnAnimationState;
        }
        return Objects.equals(var1, "throw") ? throwAnimationState : new AnimationState();
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.getAnimationState()) {
                case 0 -> this.stopAllAnimationStates();
                case 1 -> {
                    this.stopAllAnimationStates();
                    this.flyAnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.stopAllAnimationStates();
                    this.spawnAnimationState.start(this.tickCount);
                }
                case 3 -> {
                    this.stopAllAnimationStates();
                    this.throwAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    private void stopAllAnimationStates() {
        this.flyAnimationState.stop();
        this.spawnAnimationState.stop();
        this.throwAnimationState.stop();
    }

    @Override
    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        if (this.isFlying()) {
            this.introTicks = 1;
            this.setFlying(false);
            return false;
        }

        return super.causeFallDamage(p_225503_1_, p_225503_2_, p_147189_);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag p_36848_) {
        super.addAdditionalSaveData(p_36848_);
        p_36848_.putBoolean("goopy", this.isGoopy());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag p_36844_) {
        super.readAdditionalSaveData(p_36844_);
        this.setGoopy(p_36844_.getBoolean("goopy"));
    }

    @Override
    public void tick() {
        if (this.introTicks == 1) {
            this.playSound(SoundEvents.SKELETON_STEP);
            this.playAmbientSound();
            this.setAnimationState(2);
        }

        if (this.introTicks > 0) {
            this.introTicks++;
        }

        if (this.introTicks == 22) {
            this.setAnimationState(0);
        }

        if (this.owner != null && this.owner.isAlive() && this.owner instanceof Mob && this.getTarget() != ((Mob) this.owner).getTarget()) {
            this.setTarget(((Mob) this.owner).getTarget());
        }

        if (this.isFlying() && getAnimationState() != 1) {
            this.setAnimationState(1);
        }

        if (this.onGround() && isFlying()) {
            if (this.introTicks < 1) this.introTicks = 1;
            this.setFlying(false);
        }

        if (this.isAlive()) {
            if (this.isThrowing) {
                this.throwTicks++;
            }

            if (this.throwTicks == 1) {
                this.setAnimationState(3);
                this.setShowBone(true);
            }

            if (this.throwTicks == 7) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_FUNNYBONE_THROW.get(), this.getSoundVolume(), this.getVoicePitch());
                this.playSound(SoundEvents.WITCH_THROW, 1.0F, 0.8F + this.random.nextFloat() * 0.4F);
                this.setShowBone(false);

                if (!this.level().isClientSide && this.getTarget() != null) {
                    double x = this.getX() - this.getTarget().getX();
                    double y = (this.getY() + 1) - (this.getTarget().getY() + (this.getTarget().getEyeHeight() / 2) + 0.5);
                    double z = this.getZ() - this.getTarget().getZ();

                    BoneEntity projectile = new BoneEntity(this.level(), this, -x, -y, -z);
                    projectile.moveTo(this.getX(), this.getY() + 1, this.getZ());
                    CompoundTag tag = this.getPersistentData().getCompound("Rotation");
                    projectile.readAdditionalSaveData(tag);

                    projectile.isGoopy = this.isGoopy();
                    projectile.setOwner(this);
                    this.level().addFreshEntity(projectile);
                }
            }

            if (this.throwTicks == 15) {
                this.setAnimationState(0);
                this.isThrowing = false;
                this.throwTicks = 0;
            }
        }

        super.tick();
    }

    private boolean canMove() {
        return !this.isFlying() && (this.introTicks == 0 || this.introTicks > 22);
    }

    protected Vec3 updateCirclingPosition(float radius, float speed) {
        LivingEntity target = getTarget();
        if (target != null) {
            if (this.random.nextInt(200) == 0) {
                this.circleDirection = !this.circleDirection;
            }
            if (this.circleDirection) {
                this.circleTick++;
            } else {
                this.circleTick--;
            }
            return this.circleEntityPosition(target, radius, speed, true, this.circleTick, 0);
        }
        return null;
    }

    public Vec3 circleEntityPosition(Entity target, float radius, float speed, boolean direction, int circleFrame, float offset) {
        int directionInt = direction ? 1 : -1;
        double t = directionInt * circleFrame * 0.5 * speed / radius + offset;
        return target.position().add(radius * Math.cos(t), 0, radius * Math.sin(t));
    }

    class FunnyboneRandomStrollGoal extends RandomStrollGoal {
        public FunnyboneRandomStrollGoal(PathfinderMob p_25734_, double p_25735_) {
            super(p_25734_, p_25735_);
        }

        @Override
        public boolean canUse() {
            return super.canUse() && FunnyboneEntity.this.canMove();
        }

        @Override
        public boolean canContinueToUse() {
            return super.canContinueToUse() && FunnyboneEntity.this.canMove();
        }
    }

    class FunnyboneLookAtEntityGoal extends LookAtPlayerGoal {
        public FunnyboneLookAtEntityGoal(Mob p_25524_, Class<? extends LivingEntity> p_25525_, float p_25526_, float p_25527_) {
            super(p_25524_, p_25525_, p_25526_, p_25527_);
        }

        public FunnyboneLookAtEntityGoal(Mob p_25524_, Class<? extends LivingEntity> p_25525_, float p_25526_) {
            super(p_25524_, p_25525_, p_25526_);
        }

        @Override
        public boolean canUse() {
            return super.canUse() && FunnyboneEntity.this.canMove();
        }

        @Override
        public boolean canContinueToUse() {
            return super.canContinueToUse() && FunnyboneEntity.this.canMove();
        }
    }

    protected static class FunnyboneAttackGoal extends Goal {
        private final FunnyboneEntity mob;
        private final float attackRadius;
        private int strafingLeftRightMul;
        private int strafingFrontBackMul;
        private boolean chasing = false;

        protected boolean attacking = false;
        private int timeSinceAttack = 0;

        public FunnyboneAttackGoal(FunnyboneEntity mob, float attackRadius) {
            this.mob = mob;
            this.attackRadius = attackRadius;
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
        }

        public boolean canUse() {
            return this.mob.getTarget() != null && this.mob.canMove() && !this.mob.isThrowing;
        }

        public boolean canContinueToUse() {
            return (this.canUse() || !this.mob.getNavigation().isDone()) && this.mob.canMove() && !this.mob.isThrowing;
        }

        public void start() {
            super.start();
            this.mob.setAggressive(true);
            this.timeSinceAttack = this.mob.random.nextInt(80);
        }

        public void stop() {
            super.stop();
            this.mob.setAggressive(false);

            this.mob.getMoveControl().strafe(0, 0);
            this.attacking = false;
        }

        public boolean requiresUpdateEveryTick() {
            return true;
        }

        public void tick() {
            LivingEntity target = this.mob.getTarget();
            if (target != null) {
                if (timeSinceAttack < 80) {
                    timeSinceAttack++;
                }

                double distToTarget = this.mob.distanceTo(target);

                float frontBackDistBuffer = 2f;
                float leftRightDistBuffer = 1.5f;
                if (chasing && distToTarget <= attackRadius) {
                    chasing = false;
                }
                if (!chasing && distToTarget >= attackRadius + frontBackDistBuffer) {
                    chasing = true;
                }

                if (chasing) {
                    this.mob.getNavigation().moveTo(target, 0.35);
                    this.mob.getLookControl().setLookAt(target, 30.0F, 30.0F);

                    this.mob.getMoveControl().strafe(0, 0);
                } else {
                    if (!attacking) {
                        this.mob.getNavigation().stop();
                        float strafeSpeed = 0.55f;
                        Vec3 circlePos = mob.updateCirclingPosition(this.attackRadius, strafeSpeed - 0.2f);
                        double distToCirclePos = this.mob.position().distanceTo(circlePos);

                        if (distToCirclePos <= leftRightDistBuffer) {

                            if (distToTarget > this.attackRadius + 0.5) {
                                this.strafingFrontBackMul = 1;
                            } else if (distToTarget < this.attackRadius - 0.5) {
                                this.strafingFrontBackMul = -1;
                            } else {
                                this.strafingFrontBackMul = 0;
                            }

                            Vec3 toTarget = target.position().subtract(this.mob.position()).multiply(1, 0, 1).normalize();
                            Vec3 toCirclePos = circlePos.subtract(this.mob.position()).multiply(1, 0, 1).normalize();
                            Vec3 cross = toTarget.cross(toCirclePos);
                            if (cross.y > 0) strafingLeftRightMul = 1;
                            else if (cross.y < 0) strafingLeftRightMul = -1;
                            else strafingLeftRightMul = 0;

                            float distScale = (float) Math.min(Math.pow(distToCirclePos * 1f / leftRightDistBuffer, 0.7), 1.0);

                            this.mob.getMoveControl().strafe(this.strafingFrontBackMul * strafeSpeed, this.strafingLeftRightMul * strafeSpeed * distScale);
                            this.mob.lookAt(target, 30.0F, 30.0F);

                        } else {

                            this.mob.getMoveControl().strafe(0, 0);
                            this.mob.getNavigation().moveTo(circlePos.x, circlePos.y, circlePos.z, 0.35);
                            this.mob.getLookControl().setLookAt(target, 30.0F, 30.0F);
                        }
                    } else {
                        this.mob.getMoveControl().strafe(0, 0);

                    }

                    if (mob.random.nextInt(80) == 0 && timeSinceAttack >= 80 && mob.getSensing().hasLineOfSight(target)) {
                        attacking = true;
                    }
                    if (attacking) {
                        mob.isThrowing = true;
                    }
                }
            }
        }
    }
}
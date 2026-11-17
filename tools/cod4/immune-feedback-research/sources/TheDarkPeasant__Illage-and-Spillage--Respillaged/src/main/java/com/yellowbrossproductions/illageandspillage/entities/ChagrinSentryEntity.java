package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import java.util.Iterator;
import java.util.Objects;

public class ChagrinSentryEntity extends Raider implements ICanBeAnimated, EngineerMachine, IllagerAttack {
    private static final EntityDataAccessor<Integer> ANIMATION_STATE = SynchedEntityData.defineId(ChagrinSentryEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> PARTIAL_TICKS = SynchedEntityData.defineId(ChagrinSentryEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Boolean> IN_MOTION = SynchedEntityData.defineId(ChagrinSentryEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> SHOW_LOCKER = SynchedEntityData.defineId(ChagrinSentryEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> STUN_TICKS = SynchedEntityData.defineId(ChagrinSentryEntity.class, EntityDataSerializers.INT);
    public AnimationState introAnimationState = new AnimationState();
    public AnimationState shootingAnimationState = new AnimationState();
    public AnimationState stunAnimationState = new AnimationState();
    private int introTicks;
    private int attackTicks;
    private boolean isPlayingIntro;
    private boolean isShooting;
    private boolean isStunned;
    private int arrowsFired;
    private LivingEntity owner;

    public ChagrinSentryEntity(EntityType<? extends Raider> p_33002_, Level p_33003_) {
        super(p_33002_, p_33003_);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new StunGoal());
        this.goalSelector.addGoal(1, new RapidFireGoal());
        this.goalSelector.addGoal(9, new ChagrinSentryLookAtEntityGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new ChagrinSentryLookAtEntityGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.MAX_HEALTH, 24.0).add(Attributes.FOLLOW_RANGE, 32);
    }

    public void setAnimationState(int state) {
        this.entityData.set(ANIMATION_STATE, state);
    }

    @Override
    public boolean isAlliedTo(Entity entity) {
        if (super.isAlliedTo(entity)) {
            return true;
        } else if (entity instanceof Raider || entity instanceof EngineerMachine || entity instanceof FactoryMinion) {
            return this.getTeam() == null && entity.getTeam() == null;
        } else {
            return false;
        }
    }

    @Override
    public LivingEntity getOwner() {
        return this.owner;
    }

    @Override
    public void setOwner(LivingEntity owner) {
        this.owner = owner;
    }

    @Override
    public boolean canJoinRaid() {
        return false;
    }

    @Override
    public boolean canJoinPatrol() {
        return false;
    }

    @Override
    public boolean canBeLeader() {
        return false;
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(IN_MOTION, false);
        this.entityData.define(SHOW_LOCKER, false);
        this.entityData.define(STUN_TICKS, 0);
        this.entityData.define(PARTIAL_TICKS, 0.0F);
    }

    @Override
    public void applyRaidBuffs(int p_37844_, boolean p_37845_) {

    }

    public boolean isInMotion() {
        return this.entityData.get(IN_MOTION);
    }

    public void setInMotion(boolean motion) {
        this.entityData.set(IN_MOTION, motion);
    }

    public boolean shouldShowLocker() {
        return this.entityData.get(SHOW_LOCKER);
    }

    public void setShowLocker(boolean showLocker) {
        this.entityData.set(SHOW_LOCKER, showLocker);
    }

    public int getStunTicks() {
        return this.entityData.get(STUN_TICKS);
    }

    public void setStunTicks(int stunTicks) {
        this.entityData.set(STUN_TICKS, stunTicks);
    }

    public float getPartialTicks() {
        return this.entityData.get(PARTIAL_TICKS);
    }

    public void setPartialTicks(float partialTicks) {
        this.entityData.set(PARTIAL_TICKS, partialTicks);
    }

    @Override
    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        if (this.isInMotion()) {
            this.introTicks = 1;
            this.isPlayingIntro = true;
            this.setAnimationState(1);
            this.setInMotion(false);
        }

        return false;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_DISPENSER_DESTROY.get();
    }

    @Override
    public AnimationState getAnimationState(String var1) {
        if (Objects.equals(var1, "intro")) {
            return introAnimationState;
        }
        if (Objects.equals(var1, "shooting")) {
            return shootingAnimationState;
        }
        if (Objects.equals(var1, "stun")) {
            return stunAnimationState;
        }

        return new AnimationState();
    }

    @Override
    public float getAnimationSpeed() {
        return this.entityData.get(ANIMATION_STATE) == 2 ? 1.25f : 1.0f;
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                case 0 -> this.stopAllAnimationStates();
                case 1 -> {
                    this.stopAllAnimationStates();
                    this.introAnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.stopAllAnimationStates();
                    this.shootingAnimationState.start(this.tickCount);
                }
                case 3 -> {
                    this.stopAllAnimationStates();
                    this.stunAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    private void stopAllAnimationStates() {
        introAnimationState.stop();
        shootingAnimationState.stop();
        stunAnimationState.stop();
    }

    @Override
    public void knockback(double p_147241_, double p_147242_, double p_147243_) {
    }

    @Override
    public void tick() {
        if (introTicks == 1) {
            this.playSound(SoundEvents.ZOMBIE_ATTACK_IRON_DOOR);
            this.setShowLocker(true);
        }

        if (introTicks > 0) {
            introTicks++;
        }

        if (introTicks == 25) {
            this.playSound(SoundEvents.PISTON_EXTEND, 1.0f, 0.8f);
        }

        if (introTicks == 30) {
            this.playSound(SoundEvents.PISTON_EXTEND, 1.0f, 0.8f);
        }

        if (introTicks == 57) {
            this.playSound(SoundEvents.ZOMBIE_ATTACK_IRON_DOOR);
        }

        if (!this.level().isClientSide && (introTicks < 1 || introTicks > 60)) {
            this.setShowLocker(this.isInMotion());
        }

        if (introTicks == 60) {
            this.setShowLocker(false);
            this.setAnimationState(0);
            this.isPlayingIntro = false;
        }

        if (this.isShooting) {
            this.attackTicks++;
        }

        if (this.isAlive()) {
            if (this.attackTicks == 6) {
                this.setAnimationState(2);
            }

            if (this.attackTicks >= 6 && this.attackTicks % 2 == 0) {
                this.fireArrow(this.getTarget(), 1.0F, 5.0F);
                this.arrowsFired++;
            }
        }

        if (!this.isShooting && this.arrowsFired > 0 && this.tickCount % 5 == 0) {
            this.arrowsFired--;
        }

        if (this.arrowsFired >= 45 && !this.isStunned && this.random.nextInt(5) == 0) {
            this.makeOverheatParticles();
        }

        if (this.isStunned) {
            if (this.getStunTicks() < 190) this.makeOverheatParticles();
            this.setStunTicks(this.getStunTicks() + 1);
        }

        if (!this.isInMotion()) {
            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
        }

        if (this.onGround() && isInMotion()) {
            if (introTicks < 1) {
                introTicks = 1;
                this.isPlayingIntro = true;
                this.setAnimationState(1);
            }
            this.setInMotion(false);
        }

        super.tick();

        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
    }

    public void makeOverheatParticles() {
        if (!this.level().isClientSide) {
            Iterator<ServerPlayer> var1 = ((ServerLevel) this.level()).players().iterator();

            while (true) {
                ServerPlayer serverPlayer;
                do {
                    if (!var1.hasNext()) {
                        return;
                    }

                    serverPlayer = var1.next();
                } while (!(serverPlayer.distanceToSqr(this) < 4096.0));

                ParticlePacket packet = new ParticlePacket();

                packet.queueParticle(ParticleTypes.SMOKE, false, new Vec3(this.getRandomX(0.15) + (-0.5 + this.random.nextDouble()) * 2.5, this.getRandomY() + (-0.5 + this.random.nextDouble()) * 1.5, this.getRandomZ(0.15) + (-0.5 + this.random.nextDouble()) * 2.5), new Vec3(0, 0, 0));

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void fireArrow(LivingEntity target, float p_82196_2_, float inaccuracy) {
        if (target == null) return;

        AbstractArrow abstractarrowentity = this.getArrow(Items.BOW.getDefaultInstance(), p_82196_2_);
        if (this.getMainHandItem().getItem() instanceof BowItem) {
            abstractarrowentity = ((BowItem) this.getMainHandItem().getItem()).customArrow(abstractarrowentity);
        }

        float f = this.yBodyRot * ((float) Math.PI / 180F) * 0.25F;
        float f1 = Mth.cos(f);
        float f2 = Mth.sin(f);

        if (this.attackTicks % 4 == 0) {
            abstractarrowentity.setPos(this.getX() + (double) f1 * 0.6D, this.getY() + 0.8D, this.getZ() + (double) f2 * 0.6D);
        } else {
            abstractarrowentity.setPos(this.getX() - (double) f1 * 0.6D, this.getY() + 0.8D, this.getZ() - (double) f2 * 0.6D);
        }

        double d0 = target.getX() - abstractarrowentity.getX();
        double d1 = target.getY(0.3333333333333333) - abstractarrowentity.getY() - (double) target.getBbHeight() / 2.0;
        double d2 = target.getZ() - abstractarrowentity.getZ();
        double d3 = Mth.sqrt((float) (d0 * d0 + d2 * d2));
        float speed;
        if (this.distanceToSqr(target) > 22.5) {
            speed = 2.5F;
        } else {
            speed = (float) (this.distanceToSqr(target) / 9.0);
        }

        abstractarrowentity.shoot(d0, d1 + d3 * 0.20000000298023224, d2, speed, inaccuracy);
        this.level().addFreshEntity(abstractarrowentity);

        this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SHOOT.get(), 0.5f, this.getVoicePitch());
        this.playSound(SoundEvents.ARROW_SHOOT, 1.0f, this.getVoicePitch());
    }

    protected AbstractArrow getArrow(ItemStack p_213624_1_, float p_213624_2_) {
        return ProjectileUtil.getMobArrow(this, p_213624_1_, p_213624_2_);
    }

    @Override
    public boolean hurt(DamageSource p_21016_, float p_21017_) {
        return p_21016_.getEntity() != this && super.hurt(p_21016_, p_21017_);
    }

    @Override
    public SoundEvent getCelebrateSound() {
        return null;
    }

    @Override
    public boolean isPersistenceRequired() {
        return true;
    }

    @Override
    public void die(DamageSource p_70645_1_) {
        super.die(p_70645_1_);
        if (this.level().isClientSide) {
            double d0 = this.random.nextGaussian() * 0.02;
            double d1 = this.random.nextGaussian() * 0.02;
            double d2 = this.random.nextGaussian() * 0.02;
            this.level().addParticle(ParticleTypes.EXPLOSION_EMITTER, this.getX(), this.getY(), this.getZ(), d0, d1, d2);
        }

        this.deathTime = 19;
    }

    class RapidFireGoal extends Goal {
        @Override
        public boolean canUse() {
            return !ChagrinSentryEntity.this.isInMotion() && ChagrinSentryEntity.this.getStunTicks() < 1 && !ChagrinSentryEntity.this.isPlayingIntro && ChagrinSentryEntity.this.getTarget() != null && ChagrinSentryEntity.this.getTarget().isAlive() && ChagrinSentryEntity.this.hasLineOfSight(ChagrinSentryEntity.this.getTarget()) && ChagrinSentryEntity.this.arrowsFired <= 100;
        }

        @Override
        public void start() {
            ChagrinSentryEntity.this.isShooting = true;
            ChagrinSentryEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_LOAD.get(), 2.0F, 1.0F);
        }

        @Override
        public void tick() {
            if (ChagrinSentryEntity.this.getTarget() != null) {
                ChagrinSentryEntity.this.getLookControl().setLookAt(ChagrinSentryEntity.this.getTarget(), 100.0F, 100.0F);
            }
        }

        @Override
        public boolean canContinueToUse() {
            return this.canUse();
        }

        @Override
        public void stop() {
            if (!ChagrinSentryEntity.this.isStunned) {
                ChagrinSentryEntity.this.setAnimationState(0);
            }
            ChagrinSentryEntity.this.isShooting = false;
            ChagrinSentryEntity.this.attackTicks = 0;
        }
    }

    class StunGoal extends Goal {
        @Override
        public boolean canUse() {
            return !ChagrinSentryEntity.this.isInMotion() && ChagrinSentryEntity.this.getStunTicks() < 1 && !ChagrinSentryEntity.this.isPlayingIntro && ChagrinSentryEntity.this.arrowsFired > 60;
        }

        @Override
        public void start() {
            ChagrinSentryEntity.this.setAnimationState(3);
            ChagrinSentryEntity.this.isStunned = true;
            ChagrinSentryEntity.this.playSound(SoundEvents.GENERIC_EXTINGUISH_FIRE, 1.0F, 0.8F);
        }

        @Override
        public boolean canContinueToUse() {
            return ChagrinSentryEntity.this.getStunTicks() <= 200;
        }

        @Override
        public void stop() {
            ChagrinSentryEntity.this.setAnimationState(0);
            ChagrinSentryEntity.this.isStunned = false;
            ChagrinSentryEntity.this.setStunTicks(0);
            ChagrinSentryEntity.this.arrowsFired = 0;
        }
    }

    class ChagrinSentryLookAtEntityGoal extends LookAtPlayerGoal {
        public ChagrinSentryLookAtEntityGoal(Mob p_25524_, Class<? extends LivingEntity> p_25525_, float p_25526_, float p_25527_) {
            super(p_25524_, p_25525_, p_25526_, p_25527_);
        }

        public ChagrinSentryLookAtEntityGoal(Mob p_25524_, Class<? extends LivingEntity> p_25525_, float p_25526_) {
            super(p_25524_, p_25525_, p_25526_);
        }

        @Override
        public boolean canUse() {
            return super.canUse() && !ChagrinSentryEntity.this.isShooting && !ChagrinSentryEntity.this.isStunned;
        }

        @Override
        public boolean canContinueToUse() {
            return super.canContinueToUse() && !ChagrinSentryEntity.this.isShooting && !ChagrinSentryEntity.this.isStunned;
        }
    }
}
package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.Level;
import net.minecraftforge.network.PacketDistributor;

import java.util.Iterator;
import java.util.List;
import java.util.Objects;

public class HinderEntity extends Raider implements ICanBeAnimated, EngineerMachine, IllagerAttack {
    private static final EntityDataAccessor<Integer> ANIMATION_STATE = SynchedEntityData.defineId(HinderEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> IN_MOTION = SynchedEntityData.defineId(HinderEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> HEALING = SynchedEntityData.defineId(HinderEntity.class, EntityDataSerializers.BOOLEAN);
    public AnimationState introAnimationState = new AnimationState();
    public AnimationState idleAnimationState = new AnimationState();
    private int introTicks;
    private LivingEntity owner;

    public HinderEntity(EntityType<? extends Raider> p_33002_, Level p_33003_) {
        super(p_33002_, p_33003_);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.MAX_HEALTH, 40.0).add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
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
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(IN_MOTION, false);
        this.entityData.define(HEALING, false);
    }

    @Override
    public boolean canJoinRaid() {
        return false;
    }

    @Override
    public boolean canBeLeader() {
        return false;
    }

    @Override
    public void applyRaidBuffs(int p_37844_, boolean p_37845_) {
    }

    public void setHealing(boolean healing) {
        this.entityData.set(HEALING, healing);
    }

    public boolean isHealing() {
        return this.entityData.get(HEALING);
    }

    @Override
    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        if (this.isInMotion()) {
            this.introTicks = 1;
            this.setAnimationState(1);
            this.setInMotion(false);
        }

        return false;
    }

    public boolean isInMotion() {
        return this.entityData.get(IN_MOTION);
    }

    public void setInMotion(boolean motion) {
        this.entityData.set(IN_MOTION, motion);
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
        if (Objects.equals(var1, "idle")) {
            return idleAnimationState;
        }
        return new AnimationState();
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
                    this.idleAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    private void stopAllAnimationStates() {
        introAnimationState.stop();
        idleAnimationState.stop();
    }

    public void makeParticleTrail(double srcX, double srcY, double srcZ, double destX, double destY, double destZ) {
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

                int particles = (int) (6 * (this.distanceToSqr(destX, destY, destZ) / this.distanceToSqr(destX, destY, destZ)));
                for (int i = 0; i < particles; i++) {
                    double trailFactor = i / (particles - 1.0D);
                    double tx = srcX + (destX - srcX) * trailFactor;
                    double ty = srcY + (destY - srcY) * trailFactor;
                    double tz = srcZ + (destZ - srcZ) * trailFactor;
                    packet.queueParticle(ParticleTypes.ENTITY_EFFECT, false, tx, ty, tz, 0.8, 0.36, 0.67);
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    @Override
    public void tick() {
        if (introTicks == 1) {
            this.playSound(SoundEvents.ZOMBIE_ATTACK_IRON_DOOR);
        }

        if (introTicks > 0) {
            introTicks++;
        }

        if (introTicks == 5) {
            this.playSound(SoundEvents.PISTON_EXTEND);
        }

        if (introTicks == 10) {
            this.playSound(SoundEvents.PISTON_EXTEND);
        }

        if (introTicks == 15) {
            this.playSound(SoundEvents.PISTON_EXTEND);
        }

        if (introTicks == 20) {
            this.setAnimationState(0);
            this.setAnimationState(2);
        }

        if (!this.isInMotion()) {
            if (this.entityData.get(ANIMATION_STATE) != 1 && this.entityData.get(ANIMATION_STATE) != 2) {
                this.setAnimationState(0);
                this.setAnimationState(2);
            }

            if (this.entityData.get(ANIMATION_STATE) == 2) {

                List<Raider> list = this.level().getEntitiesOfClass(Raider.class, this.getBoundingBox().inflate(5.0), (predicate) -> !(predicate instanceof IllagerAttack) && this.hasLineOfSight(predicate) && predicate.isAlive() && predicate.getHealth() < predicate.getMaxHealth() && predicate.getMobType() != MobType.UNDEAD);

                if (list.isEmpty()) {
                    if (this.isHealing()) {
                        this.setHealing(false);
                    }
                } else {
                    if (!this.isHealing()) {
                        this.setHealing(true);
                        EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_ENGINEER_HINDER_HEAL.get(), 0.5F, 2.0F, true);
                    }
                    for (Raider entity : list) {
                        this.makeParticleTrail(this.getX(), this.getY() + 0.6, this.getZ(), entity.getBoundingBox().getCenter().x, entity.getBoundingBox().getCenter().y, entity.getBoundingBox().getCenter().z);
                        if (this.tickCount % 2 == 0) {
                            entity.heal(1);
                            if (entity.hasActiveRaid()) entity.getCurrentRaid().updateBossbar();
                        }
                    }
                }
            }

            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
        }

        if (this.onGround() && isInMotion()) {
            if (introTicks < 1) introTicks = 1;
            this.setInMotion(false);
        }

        super.tick();
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

    @Override
    public SoundEvent getCelebrateSound() {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
    }
}
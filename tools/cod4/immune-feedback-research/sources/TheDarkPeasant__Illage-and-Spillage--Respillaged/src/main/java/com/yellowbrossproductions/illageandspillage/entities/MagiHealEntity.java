package com.yellowbrossproductions.illageandspillage.entities;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

public class MagiHealEntity extends PathfinderMob implements IllagerAttack {
    private MagispellerEntity owner;

    public MagiHealEntity(EntityType<? extends PathfinderMob> p_21683_, Level p_21684_) {
        super(p_21683_, p_21684_);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.ATTACK_DAMAGE, 0.0).add(Attributes.MAX_HEALTH, 2.0).add(Attributes.FOLLOW_RANGE, 0.0);
    }

    public void addAdditionalSaveData(CompoundTag p_21819_) {
        super.addAdditionalSaveData(p_21819_);
    }

    public void readAdditionalSaveData(CompoundTag p_21815_) {
        super.readAdditionalSaveData(p_21815_);
    }

    public boolean isAttackable() {
        return false;
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return false;
    }

    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypes.FELL_OUT_OF_WORLD) || source.is(DamageTypes.GENERIC_KILL)) {
            super.hurt(source, amount);
        }

        return false;
    }

    public void die(DamageSource p_21014_) {
        this.deathTime = 19;
        super.die(p_21014_);
    }

    public void tick() {
        this.setInvulnerable(true);
        this.noPhysics = true;
        this.setNoGravity(true);
        if (this.tickCount > 10 && this.owner != null && (!this.owner.isAlive() || !this.owner.isWavingArms()) && !this.level().isClientSide) {
            this.discard();
        }

        if (this.tickCount > 150 && !this.level().isClientSide) {
            this.discard();
        }

        super.tick();
        if (this.owner != null && this.owner.isAlive()) {
            this.setPos(this.owner.getX(), this.owner.getY(), this.owner.getZ());
            this.xOld = this.owner.xOld;
            this.yOld = this.owner.yOld;
            this.zOld = this.owner.zOld;
        }

    }

    public boolean shouldRenderAtSqrDistance(double distance) {
        return distance < 1024.0;
    }

    protected SoundEvent getHurtSound(DamageSource damageSourceIn) {
        return null;
    }

    protected SoundEvent getDeathSound() {
        return null;
    }

    public boolean canCollideWith(Entity entity) {
        return false;
    }

    public boolean canBeCollidedWith() {
        return false;
    }

    public boolean isPickable() {
        return false;
    }

    protected void doPush(Entity entityIn) {
    }

    public void push(Entity entityIn) {
    }

    public void setOwner(MagispellerEntity owner) {
        this.owner = owner;
    }
}

package com.yellowbrossproductions.illageandspillage.entities.projectile;

import com.yellowbrossproductions.illageandspillage.entities.IllagerAttack;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

public class SkullBombEntity extends PathfinderMob implements IllagerAttack {
    private static final EntityDataAccessor<Boolean> IS_SMALL;
    private LivingEntity owner;
    private int oldSwell;
    private int swell;
    private final int maxSwell = 40;

    public SkullBombEntity(EntityType<? extends PathfinderMob> p_21683_, Level p_21684_) {
        super(p_21683_, p_21684_);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(IS_SMALL, false);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.MAX_HEALTH, 2.0).add(Attributes.ATTACK_DAMAGE, 0.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    public boolean isAttackable() {
        return false;
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return false;
    }

    public void tick() {
        this.oldSwell = this.swell++;
        if (this.swell >= this.maxSwell) {
            this.swell = this.maxSwell;
        }

        super.tick();
        if (this.tickCount == 1) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_SHIVER.get(), 1.0F, 1.0F);
        }

        if (this.tickCount == 33) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_SKULLBOMB_EXPLODE.get(), 3.0F, 1.0F);
        }

        if (this.tickCount >= 40) {
            this.explode();
        }

        if (this.onGround()) {
            this.setDeltaMovement((-0.5 + this.random.nextDouble()) * 0.6, 0.3, (-0.5 + this.random.nextDouble()) * 0.6);
        }

    }

    public float getSwelling(float p_32321_) {
        return Mth.lerp(p_32321_, (float) this.oldSwell, (float) this.swell) / (float) (this.maxSwell - 2);
    }

    private void explode() {
        if (!this.level().isClientSide) {
            float f = this.isSmall() ? 1.5F : 2.5F;
            this.dead = true;
            this.level().explode(this.getOwner(), this.getX(), this.getY(), this.getZ(), f, Level.ExplosionInteraction.NONE);
            if (!this.isSmall()) {
                SkullBombEntity s1 = ModEntityTypes.SkullBomb.get().create(this.level());

                assert s1 != null;

                s1.setPos(this.getX(), this.getY() + 0.25, this.getZ());
                s1.setSmall(true);
                s1.setDeltaMovement(-0.3, 0.3, -0.3);
                s1.setOwner(this.getOwner());
                this.level().addFreshEntity(s1);
                SkullBombEntity s2 = ModEntityTypes.SkullBomb.get().create(this.level());

                assert s2 != null;

                s2.setPos(this.getX(), this.getY() + 0.25, this.getZ());
                s2.setSmall(true);
                s2.setDeltaMovement(-0.3, 0.3, 0.3);
                s1.setOwner(this.getOwner());
                this.level().addFreshEntity(s2);
                SkullBombEntity s3 = ModEntityTypes.SkullBomb.get().create(this.level());

                assert s3 != null;

                s3.setPos(this.getX(), this.getY() + 0.25, this.getZ());
                s3.setSmall(true);
                s3.setDeltaMovement(0.3, 0.3, -0.3);
                s1.setOwner(this.getOwner());
                this.level().addFreshEntity(s3);
                SkullBombEntity s4 = ModEntityTypes.SkullBomb.get().create(this.level());

                assert s4 != null;

                s4.setPos(this.getX(), this.getY() + 0.25, this.getZ());
                s4.setSmall(true);
                s4.setDeltaMovement(0.3, 0.3, 0.3);
                s1.setOwner(this.getOwner());
                this.level().addFreshEntity(s4);
            }

            this.discard();
        }

    }

    public void aiStep() {
        if (this.level().isClientSide) {
            for (int i = 0; i < 2; ++i) {
                double d0 = (-0.5 + this.random.nextGaussian()) / 12.0;
                double d1 = (-0.5 + this.random.nextGaussian()) / 12.0;
                double d2 = (-0.5 + this.random.nextGaussian()) / 12.0;
                this.level().addParticle(ParticleTypes.SMOKE, this.getRandomX(1.0), this.getRandomY() + 0.25, this.getRandomZ(1.0), d0, d1, d2);
            }
        }

        super.aiStep();
    }

    public boolean isSmall() {
        return this.entityData.get(IS_SMALL);
    }

    public void setSmall(boolean small) {
        this.entityData.set(IS_SMALL, small);
    }

    public LivingEntity getOwner() {
        return this.owner;
    }

    public void setOwner(LivingEntity owner) {
        this.owner = owner;
    }

    public boolean hurt(DamageSource source, float amount) {
        return (source.is(DamageTypes.FELL_OUT_OF_WORLD) || source.is(DamageTypes.GENERIC_KILL)) && super.hurt(source, amount);
    }

    public void die(DamageSource p_21014_) {
        this.deathTime = 19;
        super.die(p_21014_);
    }

    static {
        IS_SMALL = SynchedEntityData.defineId(SkullBombEntity.class, EntityDataSerializers.BOOLEAN);
    }
}

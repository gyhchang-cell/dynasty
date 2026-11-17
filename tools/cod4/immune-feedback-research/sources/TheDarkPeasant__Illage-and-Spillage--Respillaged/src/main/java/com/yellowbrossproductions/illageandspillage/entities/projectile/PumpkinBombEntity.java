package com.yellowbrossproductions.illageandspillage.entities.projectile;

import com.yellowbrossproductions.illageandspillage.entities.IllagerAttack;
import com.yellowbrossproductions.illageandspillage.entities.OldRagnoEntity;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import com.yellowbrossproductions.illageandspillage.util.PotionRegisterer;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

import java.util.List;

public class PumpkinBombEntity extends PathfinderMob implements IllagerAttack {
    private static final EntityDataAccessor<Boolean> GOOPY;
    private LivingEntity owner;
    private int oldSwell;
    private int swell;
    private final int maxSwell = 30;
    private int jumpTicks;
    private boolean isSwell;

    public PumpkinBombEntity(EntityType<? extends PathfinderMob> p_21683_, Level p_21684_) {
        super(p_21683_, p_21684_);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(GOOPY, false);
    }

    public boolean isAttackable() {
        return false;
    }

    public boolean getGoopy() {
        return this.entityData.get(GOOPY);
    }

    public void setGoopy() {
        this.entityData.set(GOOPY, true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.MAX_HEALTH, 2.0).add(Attributes.ATTACK_DAMAGE, 0.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return false;
    }

    public void tick() {
        if (this.jumpTicks >= 100) {
            this.isSwell = true;
        }

        if (this.isSwell) {
            this.oldSwell = this.swell++;
            if (this.swell == 1) {
                this.playSound(SoundEvents.TNT_PRIMED, 1.0F, 0.5F);
            }

            if (this.swell >= this.maxSwell) {
                this.swell = this.maxSwell;
                this.explode();
            }
        }

        if (this.tickCount > 20) {
            if (this.onGround()) {
                ++this.jumpTicks;
            }

            if (this.getTarget() != null) {
                this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                if (this.jumpTicks % 20 == 0 && this.onGround()) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_PUMPKINBOMB_BOING.get(), 1.0F, 1.0F);
                    if (!this.level().isClientSide) {
                        this.setDeltaMovement((this.getTarget().getX() - this.getX()) * 0.4 * 0.16, 0.5, (this.getTarget().getZ() - this.getZ()) * 0.4 * 0.16);
                    }
                }
            }
        }

        if (owner != null) {
            List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(100.0), (predicate) -> !(this.owner instanceof Mob) || EntityUtil.canHurtThisMob(predicate, (Mob) this.owner));
            for (Mob attacker : list) {
                if (attacker.getLastHurtByMob() == this) {
                    attacker.setLastHurtByMob(owner);
                }

                if (attacker.getTarget() == this) {
                    attacker.setTarget(owner);
                }
            }
        }

        super.tick();
    }

    protected boolean shouldDespawnInPeaceful() {
        return this.getOwner() instanceof Monster;
    }

    public float getSwelling(float p_32321_) {
        return Mth.lerp(p_32321_, (float) this.oldSwell, (float) this.swell) / (float) (this.maxSwell - 2);
    }

    private void explode() {
        this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_PUMPKINBOMB_EXPLODE.get(), 3.0F, 1.0F);
        if (!this.level().isClientSide) {
            this.dead = true;
            this.level().explode(this.getOwner(), this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);

            if (this.getGoopy() && !(this.getOwner() instanceof OldRagnoEntity)) {
                AreaEffectCloud cloud = new AreaEffectCloud(this.level(), this.getX(), this.getY(), this.getZ());
                cloud.setRadius(3.0F);
                cloud.setRadiusOnUse(-0.5F);
                cloud.setWaitTime(10);
                cloud.setRadiusPerTick(-cloud.getRadius() / (float) cloud.getDuration());
                cloud.setPotion(PotionRegisterer.MUTATION.get());
                cloud.setOwner(this);
                this.level().addFreshEntity(cloud);
            }

            this.discard();
        }

    }

    public void aiStep() {
        if (this.level().isClientSide && this.tickCount >= 60) {
            for (int i = 0; i < 2; ++i) {
                double d0 = (-0.5 + this.random.nextGaussian()) / 12.0;
                double d1 = (-0.5 + this.random.nextGaussian()) / 12.0;
                double d2 = (-0.5 + this.random.nextGaussian()) / 12.0;
                this.level().addParticle(ParticleTypes.SMOKE, this.getRandomX(1.0), this.getRandomY() + 0.25, this.getRandomZ(1.0), d0, d1, d2);
            }
        }

        super.aiStep();
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
        GOOPY = SynchedEntityData.defineId(PumpkinBombEntity.class, EntityDataSerializers.BOOLEAN);
    }
}

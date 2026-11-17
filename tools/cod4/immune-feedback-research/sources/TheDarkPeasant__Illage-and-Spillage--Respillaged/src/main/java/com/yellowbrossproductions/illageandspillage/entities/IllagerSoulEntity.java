package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;

import java.util.EnumSet;
import java.util.List;

public class IllagerSoulEntity extends Monster {
    private static final EntityDataAccessor<Boolean> CHARGING;
    private static final EntityDataAccessor<Boolean> ANGEL_OR_DEVIL;
    private LivingEntity owner;
    private int attackTicks;
    double chargeX;
    double chargeY;
    double chargeZ;
    double targetX;
    double targetY;
    double targetZ;
    private int chargeTime;
    private int oldSwell;
    private int swell;
    private static final int MAX_SWELL = 15;

    public IllagerSoulEntity(EntityType<? extends Monster> p_33002_, Level p_33003_) {
        super(p_33002_, p_33003_);
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new LookAtTargetGoal());
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 20.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(CHARGING, false);
        this.entityData.define(ANGEL_OR_DEVIL, false);
    }

    protected boolean canRide(Entity p_20339_) {
        return false;
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return false;
    }

    public void tick() {
        this.noPhysics = true;
        if (this.getTarget() != null) {
            ++this.attackTicks;
            if (this.attackTicks > 50 && this.random.nextInt(6) == 0 && this.targetX == 0.0 && this.targetY == 0.0 && this.targetZ == 0.0) {
                LivingEntity entity = this.getTarget();
                double x = this.getX() - entity.getX();
                double y = this.getY() - entity.getY();
                double z = this.getZ() - entity.getZ();
                double d = Math.sqrt(x * x + y * y + z * z);
                float power = 3.5F;
                double motionX = this.getDeltaMovement().x - x / d * (double) power * 0.2;
                double motionY = this.getDeltaMovement().y - y / d * (double) power * 0.2;
                double motionZ = this.getDeltaMovement().z - z / d * (double) power * 0.2;
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_SOULSCREAM.get(), 3.0F, this.getVoicePitch());
                CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.01F, 0, 30);
                this.setTargetPosition(entity.getX(), entity.getY(), entity.getZ());
                this.setCharge(motionX, motionY, motionZ);
            }
        }

        if (this.chargeX != 0.0 && this.chargeY != 0.0 && this.chargeZ != 0.0) {
            ++this.chargeTime;
            this.setDeltaMovement(this.chargeX, this.chargeY, this.chargeZ);
            if (!this.level().isClientSide) {
                this.setCharging(true);
            }

            if (this.getX() - this.targetX < 1.0 && this.getX() - this.targetX > -1.0 && this.getY() - this.targetY < 1.0 && this.getY() - this.targetY > -1.0 && this.getZ() - this.targetZ < 1.0 && this.getZ() - this.targetZ > -1.0 || this.chargeTime > 60) {
                if (!this.level().isClientSide) {
                    CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.01F, 0, 30);
                    this.level().explode(this, this.getX(), this.getY(), this.getZ(), 2.0F, Level.ExplosionInteraction.NONE);
                }

                this.kill();
            }
        } else {
            this.chargeTime = 0;
            if (!this.level().isClientSide) {
                this.setCharging(false);
            }
        }

        if (this.tickCount > 140) {
            if (!this.level().isClientSide) {
                CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.01F, 0, 30);
                this.level().explode(this, this.getX(), this.getY(), this.getZ(), 2.0F, Level.ExplosionInteraction.NONE);
            }

            this.kill();
        }

        super.tick();
        this.setNoGravity(true);
        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
        this.setInvulnerable(true);
        this.oldSwell = this.swell++;
        if (this.swell >= MAX_SWELL) {
            this.swell = MAX_SWELL;
        }

        LivingEntity var18 = this.getOwner();
        if (var18 instanceof Mob mob) {
            this.setTarget(mob.getTarget());
        }

        if (!this.isCharging()) {
            if (this.level().getBlockState(this.blockPosition().below()) != Blocks.AIR.defaultBlockState()) {
                this.setDeltaMovement(this.getDeltaMovement().add(0.0, 0.04, 0.0));
            } else if (this.getDeltaMovement().y > 0.0) {
                this.setDeltaMovement(this.getDeltaMovement().add(0.0, -0.04, 0.0));
            }
        }

        this.stopAttackersFromAttacking();
    }

    public void stopAttackersFromAttacking() {
        List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(100.0));

        for (Mob attacker : list) {
            if (attacker.getLastHurtByMob() == this && this.getOwner() != null) {
                attacker.setLastHurtByMob(this.getOwner());
            }

            if (attacker.getTarget() == this && this.getOwner() != null) {
                attacker.setTarget(this.getOwner());
            }
        }

    }

    public float getSwelling(float p_32321_) {
        return Mth.lerp(p_32321_, (float) this.oldSwell, (float) this.swell) / (float) (MAX_SWELL - 2);
    }

    public boolean isCharging() {
        return this.entityData.get(CHARGING);
    }

    public void setCharging(boolean charge) {
        this.entityData.set(CHARGING, charge);
    }

    public boolean isAngelOrDevil() {
        return this.entityData.get(ANGEL_OR_DEVIL);
    }

    public void setAngelOrDevil(boolean what) {
        this.entityData.set(ANGEL_OR_DEVIL, what);
    }

    public void setCharge(double x, double y, double z) {
        this.chargeX = x;
        this.chargeY = y;
        this.chargeZ = z;
    }

    public void setTargetPosition(double x, double y, double z) {
        this.targetX = x;
        this.targetY = y;
        this.targetZ = z;
    }

    public boolean ignoreExplosion() {
        return true;
    }

    public boolean hurt(DamageSource source, float p_21017_) {
        return (source.is(DamageTypes.FELL_OUT_OF_WORLD) || source.is(DamageTypes.GENERIC_KILL)) && super.hurt(source, p_21017_);
    }

    public void die(DamageSource p_21014_) {
        super.die(p_21014_);
        this.deathTime = 19;
    }

    public void setOwner(LivingEntity owner) {
        this.owner = owner;
    }

    public LivingEntity getOwner() {
        return this.owner;
    }

    public boolean isPersistenceRequired() {
        return true;
    }

    protected SoundEvent getHurtSound(DamageSource p_33034_) {
        return null;
    }

    protected SoundEvent getDeathSound() {
        return null;
    }

    static {
        CHARGING = SynchedEntityData.defineId(IllagerSoulEntity.class, EntityDataSerializers.BOOLEAN);
        ANGEL_OR_DEVIL = SynchedEntityData.defineId(IllagerSoulEntity.class, EntityDataSerializers.BOOLEAN);
    }

    class LookAtTargetGoal extends Goal {
        public LookAtTargetGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public boolean canUse() {
            return IllagerSoulEntity.this.getTarget() != null;
        }

        public boolean canContinueToUse() {
            return true;
        }

        public void start() {
        }

        public void tick() {
            if (IllagerSoulEntity.this.getTarget() != null && !IllagerSoulEntity.this.isCharging()) {
                IllagerSoulEntity.this.getLookControl().setLookAt(IllagerSoulEntity.this.getTarget(), 100.0F, 100.0F);
            }

            if (IllagerSoulEntity.this.isCharging()) {
                IllagerSoulEntity.this.getLookControl().setLookAt(IllagerSoulEntity.this.targetX, IllagerSoulEntity.this.targetY, IllagerSoulEntity.this.targetZ, 100.0F, 100.0F);
            }

        }

        public void stop() {
        }
    }
}

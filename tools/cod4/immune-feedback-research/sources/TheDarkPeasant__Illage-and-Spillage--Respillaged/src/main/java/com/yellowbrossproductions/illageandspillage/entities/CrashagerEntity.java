package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
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
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.fluids.FluidType;

import java.util.Objects;

public class CrashagerEntity extends Monster implements IllagerAttack {
    private static final EntityDataAccessor<Integer> ATTACKSTAGE;
    private int spawnTicks;
    private Mob owner;
    private double targetX;
    private double targetY;
    private double targetZ;

    public CrashagerEntity(EntityType<? extends Monster> p_i48553_1_, Level p_i48553_2_) {
        super(p_i48553_1_, p_i48553_2_);
        this.setMaxUpStep(1.0F);
    }

    public boolean isAttackable() {
        return false;
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return false;
    }

    protected void registerGoals() {
        this.goalSelector.addGoal(0, new AttackGoal());
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.800000011920929).add(Attributes.MAX_HEALTH, 500.0).add(Attributes.ATTACK_DAMAGE, 15.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ATTACKSTAGE, 0);
    }

    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        return false;
    }

    public boolean canBeRiddenUnderFluidType(FluidType type, Entity rider) {
        return true;
    }

    public void tick() {
        if (this.isAlive()) {
            if (this.getOwner() != null) {
                if (this.onGround()) {
                    ++this.spawnTicks;
                    if (this.getAttackStage() == 0) {
                        this.setAttackStage(1);
                    }

                    this.setYRot(this.getYHeadRot());
                    this.yBodyRot = this.getYRot();
                }

                if (this.spawnTicks == 15) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_RAVAGER_ROAR.get(), 3.0F, this.getVoicePitch());
                    CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.4F, 0, 20);
                    this.setAttackStage(2);
                    if (this.getTarget() != null) {
                        this.targetX = this.getTarget().getX();
                        this.targetY = this.getTarget().getY();
                        this.targetZ = this.getTarget().getZ();
                    }
                }

                if (this.spawnTicks == 30) {
                    this.setAttackStage(3);
                }

                if (this.spawnTicks > 70) {
                    this.explode();
                    this.kill();
                }

                if (this.getX() - this.targetX < 2.0 && this.getX() - this.targetX > -2.0 && this.getY() - this.targetY < 2.0 && this.getY() - this.targetY > -2.0 && this.getZ() - this.targetZ < 2.0 && this.getZ() - this.targetZ > -2.0) {
                    this.explode();
                    this.kill();
                }
            }

            for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                if (EntityUtil.canHurtThisMob(entity, this) && entity instanceof LivingEntity && entity.isAlive()) {
                    double x = this.getX() - entity.getX();
                    double y = this.getY() - entity.getY();
                    double z = this.getZ() - entity.getZ();
                    double d = Math.sqrt(x * x + y * y + z * z);
                    if (this.distanceToSqr(entity) < 9.0) {
                        if (entity.invulnerableTime <= 0) {
                            this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                        }

                        entity.hurt(this.damageSources().indirectMagic(this, this), (float) Objects.requireNonNull(this.getAttribute(Attributes.ATTACK_DAMAGE)).getBaseValue());
                        entity.hurtMarked = true;
                        entity.setDeltaMovement(-x / d * 2.0, -y / d * 2.0 + 0.5, -z / d * 2.0);
                        entity.lerpMotion(-x / d * 2.0, -y / d * 2.0 + 0.5, -z / d * 2.0);
                    }
                }
            }

            if (this.getAttackStage() < 3) {
                this.getNavigation().stop();
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                this.navigation.stop();
            } else if (this.targetX != 0.0 && this.targetY != 0.0 && this.targetZ != 0.0) {
                this.getNavigation().moveTo(this.targetX, this.targetY, this.targetZ, 1.0);
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }
            }
        }

        super.tick();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return null;
    }

    protected SoundEvent getDeathSound() {
        return null;
    }

    protected SoundEvent getStepSound() {
        return SoundEvents.RAVAGER_STEP;
    }

    protected void playStepSound(BlockPos p_180429_1_, BlockState p_180429_2_) {
        this.playSound(this.getStepSound(), 1.0F, 1.0F);
    }

    public boolean hurt(DamageSource source, float amount) {
        return (source.is(DamageTypes.FELL_OUT_OF_WORLD) || source.is(DamageTypes.GENERIC_KILL)) && super.hurt(source, amount);
    }

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

    private void explode() {
        if (!this.level().isClientSide) {
            this.level().explode(this, this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);
        }

    }

    public Mob getOwner() {
        return this.owner;
    }

    public void setOwner(Mob owner) {
        this.owner = owner;
    }

    public int getAttackStage() {
        return (Integer) this.entityData.get(ATTACKSTAGE);
    }

    public void setAttackStage(int attackStage) {
        this.entityData.set(ATTACKSTAGE, attackStage);
    }

    static {
        ATTACKSTAGE = SynchedEntityData.defineId(CrashagerEntity.class, EntityDataSerializers.INT);
    }

    class AttackGoal extends Goal {
        AttackGoal() {
        }

        public boolean canUse() {
            return CrashagerEntity.this.getAttackStage() > 0;
        }

        public void tick() {
        }
    }
}

package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;

import java.util.EnumSet;
import java.util.Iterator;
import java.util.List;

public class SpiritHandEntity extends PathfinderMob implements IllagerAttack {
    private static final EntityDataAccessor<Boolean> GOOD_OR_EVIL;
    private static final EntityDataAccessor<Integer> ATTACK_TYPE;
    private LivingEntity owner;
    private boolean attacking = false;
    private int attackTicks;
    private int actualAttackTicks;
    int power;
    double chargeX;
    double chargeY;
    double chargeZ;
    double targetX;
    double targetY;
    double targetZ;

    public SpiritHandEntity(EntityType<? extends PathfinderMob> p_33002_, Level p_33003_) {
        super(p_33002_, p_33003_);
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new AlwaysWatchTargetGoal());
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 20.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0);
    }

    public boolean isAttackable() {
        return false;
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(GOOD_OR_EVIL, true);
        this.entityData.define(ATTACK_TYPE, 0);
    }

    public void addAdditionalSaveData(CompoundTag p_21484_) {
        super.addAdditionalSaveData(p_21484_);
        p_21484_.putBoolean("IsGoodOrEvil", this.isGoodOrEvil());
    }

    public void readAdditionalSaveData(CompoundTag p_21450_) {
        super.readAdditionalSaveData(p_21450_);
        this.setGoodOrEvil(p_21450_.getBoolean("IsGoodOrEvil"));
    }

    protected boolean shouldDespawnInPeaceful() {
        return true;
    }

    public void tick() {
        this.noPhysics = true;
        super.tick();
        this.setNoGravity(true);
        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
        this.setDeltaMovement(this.getDeltaMovement().add((-0.5 + this.random.nextDouble()) / 20.0, (-0.5 + this.random.nextDouble()) / 20.0, (-0.5 + this.random.nextDouble()) / 20.0));
        if (this.getTarget() != null) {
            ++this.attackTicks;
            List<SpiritHandEntity> list = this.level().getEntitiesOfClass(SpiritHandEntity.class, this.getBoundingBox().inflate(100.0), SpiritHandEntity::isAttacking);
            if (this.attackTicks > 100 && this.actualAttackTicks < 1 && this.random.nextInt(12) == 0) {
                if (list.isEmpty()) {
                    this.setAttacking(true);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_SPIRITHAND_WARN.get(), 4.0F, this.getVoicePitch());
                    if (this.random.nextBoolean()) {
                        if (!this.level().isClientSide) {
                            this.setAttackType(1);
                        }
                    } else if (!this.level().isClientSide) {
                        this.setAttackType(2);
                    }
                } else {
                    this.attackTicks = 0;
                }
            }

            if (this.isAttacking()) {
                ++this.actualAttackTicks;
                LivingEntity entity;
                double x;
                double y;
                double z;
                double d;
                float power;
                double motionX;
                double motionY;
                double motionZ;
                if (this.getAttackType() == 1) {
                    Iterator var18;
                    if (this.isGoodOrEvil()) {
                        if (this.actualAttackTicks < 100) {
                            entity = this.getTarget();
                            x = this.getX() - entity.getX();
                            y = this.getY() - (entity.getY() - 0.3);
                            z = this.getZ() - entity.getZ();
                            d = Math.sqrt(x * x + y * y + z * z);
                            power = 0.2F;
                            motionX = this.getDeltaMovement().x - x / d * (double) power * 0.2;
                            motionY = this.getDeltaMovement().y - y / d * (double) power * 0.2;
                            motionZ = this.getDeltaMovement().z - z / d * (double) power * 0.2;
                            if (this.distanceToSqr(entity) > 1.5) {
                                this.setDeltaMovement(motionX, motionY, motionZ);
                            } else {
                                this.setDeltaMovement(this.getDeltaMovement().x / 2.0, this.getDeltaMovement().y / 2.0, this.getDeltaMovement().z / 2.0);
                            }
                        } else {
                            this.setDeltaMovement(0.0, 0.5 + (double) (this.power / 8), 0.0);
                            var18 = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(1.0)).iterator();

                            while (var18.hasNext()) {
                                entity = (LivingEntity) var18.next();
                                entity.hurtMarked = true;
                                entity.setDeltaMovement(entity.getDeltaMovement().x, 0.5 + (double) (this.power / 8), entity.getDeltaMovement().z);
                                entity.lerpMotion(entity.getDeltaMovement().x, 0.5 + (double) (this.power / 8), entity.getDeltaMovement().z);
                            }

                            if (this.actualAttackTicks > 120 - this.power * 2) {
                                this.attackTicks = 0;
                                this.actualAttackTicks = 0;
                                this.setAttacking(false);
                                if (!this.level().isClientSide) {
                                    this.setAttackType(0);
                                }
                            }
                        }
                    } else if (this.actualAttackTicks < 100) {
                        entity = this.getTarget();
                        x = this.getX() - entity.getX();
                        y = this.getY() - (entity.getY() + (double) entity.getEyeHeight() + 1.0 + (double) this.actualAttackTicks / 25.0);
                        z = this.getZ() - entity.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        power = 0.2F;
                        motionX = this.getDeltaMovement().x - x / d * (double) power * 0.2;
                        motionY = this.getDeltaMovement().y - y / d * (double) power * 0.2;
                        motionZ = this.getDeltaMovement().z - z / d * (double) power * 0.2;
                        if (this.distanceToSqr(entity) > 1.5) {
                            this.setDeltaMovement(motionX, motionY, motionZ);
                        } else {
                            this.setDeltaMovement(this.getDeltaMovement().x / 2.0, this.getDeltaMovement().y / 2.0, this.getDeltaMovement().z / 2.0);
                        }
                    } else {
                        this.setDeltaMovement(0.0, -0.7 + (double) (this.power / 8), 0.0);
                        var18 = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(1.0)).iterator();

                        while (var18.hasNext()) {
                            entity = (LivingEntity) var18.next();
                            entity.hurtMarked = true;
                            entity.setDeltaMovement(entity.getDeltaMovement().x, -0.7 + (double) (this.power / 8), entity.getDeltaMovement().z);
                            entity.lerpMotion(entity.getDeltaMovement().x, -0.7 + (double) (this.power / 8), entity.getDeltaMovement().z);
                        }

                        if (this.actualAttackTicks > 120 - this.power * 2 || !this.level().getBlockState(this.blockPosition()).isAir()) {
                            this.attackTicks = 0;
                            this.actualAttackTicks = 0;
                            this.setAttacking(false);
                            if (!this.level().isClientSide) {
                                this.setAttackType(0);
                                CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.3F, 0, 15);
                                this.level().explode(this.getOwner(), this.getX(), this.getY(), this.getZ(), 2.5F, Level.ExplosionInteraction.NONE);
                            }
                        }
                    }
                } else {
                    if (this.actualAttackTicks >= 100 && this.getTarget() != null && this.targetX == 0.0 && this.targetY == 0.0 && this.targetZ == 0.0) {
                        entity = this.getTarget();
                        x = this.getX() - entity.getX();
                        y = this.getY() - entity.getY();
                        z = this.getZ() - entity.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        power = 6.0F;
                        motionX = this.getDeltaMovement().x - x / d * (double) power * 0.2;
                        motionY = this.getDeltaMovement().y - y / d * (double) power * 0.2;
                        motionZ = this.getDeltaMovement().z - z / d * (double) power * 0.2;
                        this.setTargetPosition(entity.getX(), entity.getY(), entity.getZ());
                        this.setCharge(motionX, motionY, motionZ);
                    }

                    if (this.chargeX != 0.0 && this.chargeY != 0.0 && this.chargeZ != 0.0) {
                        this.setDeltaMovement(this.chargeX, this.chargeY, this.chargeZ);
                        if (this.getX() - this.targetX < 1.0 && this.getX() - this.targetX > -1.0 && this.getY() - this.targetY < 1.0 && this.getY() - this.targetY > -1.0 && this.getZ() - this.targetZ < 1.0 && this.getZ() - this.targetZ > -1.0) {
                            this.actualAttackTicks = 141;
                        }
                    }

                    if (this.actualAttackTicks > 140) {
                        this.attackTicks = 0;
                        this.actualAttackTicks = 0;
                        this.setAttacking(false);
                        if (!this.level().isClientSide) {
                            this.setAttackType(0);
                            CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.3F, 0, 15);
                            this.level().explode(this.getOwner(), this.getX(), this.getY(), this.getZ(), 2.5F, Level.ExplosionInteraction.NONE);
                        }

                        this.setCharge(0.0, 0.0, 0.0);
                        this.setTargetPosition(0.0, 0.0, 0.0);
                    }
                }
            }
        } else {
            this.attackTicks = 0;
            this.actualAttackTicks = 0;
            this.setAttacking(false);
            if (!this.level().isClientSide) {
                this.setAttackType(0);
            }
        }

        if (this.getOwner() instanceof Mob) {
            this.setTarget(((Mob) this.getOwner()).getTarget());
        }

        if (this.level().getBlockState(this.blockPosition().below()) != Blocks.AIR.defaultBlockState()) {
            this.setDeltaMovement(this.getDeltaMovement().add(0.0, 0.01, 0.0));
        } else if (this.getDeltaMovement().y > 0.0) {
            this.setDeltaMovement(this.getDeltaMovement().add(0.0, -0.01, 0.0));
        }

        if (this.tickCount > 600) {
            this.kill();
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

    public boolean doHurtTarget(Entity p_21372_) {
        return false;
    }

    public void setOwner(LivingEntity owner) {
        this.owner = owner;
    }

    public LivingEntity getOwner() {
        return this.owner;
    }

    public void setPower(int power) {
        this.power = power;
    }

    public boolean isPersistenceRequired() {
        return true;
    }

    public boolean isGoodOrEvil() {
        return this.entityData.get(GOOD_OR_EVIL);
    }

    public void setGoodOrEvil(boolean goodOrEvil) {
        this.entityData.set(GOOD_OR_EVIL, goodOrEvil);
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

    protected SoundEvent getHurtSound(DamageSource p_33034_) {
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

    public boolean hurt(DamageSource source, float amount) {
        return (source.is(DamageTypes.FELL_OUT_OF_WORLD) || source.is(DamageTypes.GENERIC_KILL)) && super.hurt(source, amount);
    }

    protected SoundEvent getDeathSound() {
        return null;
    }

    public boolean isAttacking() {
        return this.attacking;
    }

    public void setAttacking(boolean attacking) {
        this.attacking = attacking;
    }

    public int getAttackType() {
        return (Integer) this.entityData.get(ATTACK_TYPE);
    }

    public void setAttackType(int a) {
        this.entityData.set(ATTACK_TYPE, a);
    }

    public void handleEntityEvent(byte p_21375_) {
        if (p_21375_ != 60) {
            super.handleEntityEvent(p_21375_);
        }

    }

    static {
        GOOD_OR_EVIL = SynchedEntityData.defineId(SpiritHandEntity.class, EntityDataSerializers.BOOLEAN);
        ATTACK_TYPE = SynchedEntityData.defineId(SpiritHandEntity.class, EntityDataSerializers.INT);
    }

    class AlwaysWatchTargetGoal extends Goal {
        public AlwaysWatchTargetGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public boolean canUse() {
            return SpiritHandEntity.this.getTarget() != null;
        }

        public boolean canContinueToUse() {
            return SpiritHandEntity.this.getTarget() != null;
        }

        public void tick() {
            SpiritHandEntity.this.getNavigation().stop();
            if (SpiritHandEntity.this.getTarget() != null && SpiritHandEntity.this.actualAttackTicks < 100) {
                SpiritHandEntity.this.getLookControl().setLookAt(SpiritHandEntity.this.getTarget(), 100.0F, 100.0F);
            }

            if (SpiritHandEntity.this.actualAttackTicks >= 100) {
                SpiritHandEntity.this.getLookControl().setLookAt(SpiritHandEntity.this.targetX, SpiritHandEntity.this.targetY, SpiritHandEntity.this.targetZ, 100.0F, 100.0F);
            }

            SpiritHandEntity.this.navigation.stop();
        }
    }
}

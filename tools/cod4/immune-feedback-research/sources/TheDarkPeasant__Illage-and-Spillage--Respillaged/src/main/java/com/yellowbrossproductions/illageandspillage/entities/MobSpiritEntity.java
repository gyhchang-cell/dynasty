package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.util.EffectRegisterer;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
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

import java.util.Objects;

public class MobSpiritEntity extends Monster {
    private static final EntityDataAccessor<Boolean> GOOD_OR_EVIL;
    private static final EntityDataAccessor<Boolean> SPIRITCALLER;
    private LivingEntity owner;
    private LivingEntity originalMob;
    private int attackTicks;

    public MobSpiritEntity(EntityType<? extends Monster> p_33002_, Level p_33003_) {
        super(p_33002_, p_33003_);
        this.xpReward = 0;
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return false;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 10.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(GOOD_OR_EVIL, true);
        this.entityData.define(SPIRITCALLER, false);
    }

    public void addAdditionalSaveData(CompoundTag p_21484_) {
        super.addAdditionalSaveData(p_21484_);
        p_21484_.putBoolean("IsGoodOrEvil", this.isGoodOrEvil());
        p_21484_.putBoolean("corrupted", this.isSpiritcaller());
    }

    public void readAdditionalSaveData(CompoundTag p_21450_) {
        super.readAdditionalSaveData(p_21450_);
        this.setGoodOrEvil(p_21450_.getBoolean("IsGoodOrEvil"));
        this.setSpiritcaller(p_21450_.getBoolean("corrupted"));
    }

    protected boolean canRide(Entity entity) {
        return entity instanceof Mob && super.canRide(entity);
    }

    public boolean hurt(DamageSource source, float amount) {
        Entity attacker = source.getEntity();
        if (Config.CommonConfig.nightmare_mode.get() && (attacker instanceof SpiritcallerEntity || attacker instanceof IllagerSoulEntity))
            return false;

        return super.hurt(source, amount);
    }

    public void tick() {
        this.noPhysics = true;
        super.tick();
        this.setNoGravity(true);
        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
        if (this.getTarget() != null) {
            ++this.attackTicks;
            if (this.attackTicks < 40) {
                LivingEntity entity = this.getTarget();
                double x = this.getX() - entity.getX();
                double y = this.getY() - entity.getY();
                double z = this.getZ() - entity.getZ();
                double d = Math.sqrt(x * x + y * y + z * z);
                float power = 0.3F;
                double motionX = this.getDeltaMovement().x - x / d * (double) power * 0.2;
                double motionY = this.getDeltaMovement().y - y / d * (double) power * 0.2;
                double motionZ = this.getDeltaMovement().z - z / d * (double) power * 0.2;
                if (this.distanceToSqr(entity) > 9.0) {
                    this.setDeltaMovement(motionX, motionY, motionZ);
                }
            }

            if (this.attackTicks > 100 && this.random.nextInt(12) == 0) {
                this.attackTicks = 0;
            }
        }

        if (this.level().getBlockState(this.blockPosition().below()) != Blocks.AIR.defaultBlockState()) {
            this.setDeltaMovement(this.getDeltaMovement().add(0.0, 0.01, 0.0));
        } else if (this.getDeltaMovement().y > 0.0) {
            this.setDeltaMovement(this.getDeltaMovement().add(0.0, -0.01, 0.0));
        }

        if (this.getOriginalMob() instanceof Mob) {
            this.getOriginalMob().addEffect(new MobEffectInstance(EffectRegisterer.DISABILITY.get(), 5, 0, true, true, true));
        }

        if (this.getOwner() instanceof Mob) {
            this.setTarget(((Mob) this.getOwner()).getTarget());
            if (this.getOriginalMob() != null && !this.getOriginalMob().isAlive()) {
                LivingEntity entity = this.getOwner();
                if (entity instanceof SpiritcallerEntity spiritcaller) {
                    if (spiritcaller.getSoulPower() < 8) {
                        entity = this.getOwner();
                        double x = this.getX() - entity.getX();
                        double y = this.getY() - entity.getY();
                        double z = this.getZ() - entity.getZ();
                        double d = Math.sqrt(x * x + y * y + z * z);
                        float power = 0.3F;
                        double motionX = this.getDeltaMovement().x - x / d * (double) power * 0.2;
                        double motionY = this.getDeltaMovement().y - y / d * (double) power * 0.2;
                        double motionZ = this.getDeltaMovement().z - z / d * (double) power * 0.2;
                        this.setDeltaMovement(motionX, motionY, motionZ);
                        if (this.distanceToSqr(this.getOwner()) < 6.0) {
                            this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_SPIRITABSORB.get(), 2.0F, this.getVoicePitch());
                            spiritcaller.setSoulPower(spiritcaller.getSoulPower() + 1);
                            spiritcaller.makeParticles();
                            this.discard();
                        }
                    }
                }
            }
        }

    }

    public void push(Entity p_21294_) {
        super.push(p_21294_);
        if (this.getTarget() == p_21294_) {
            p_21294_.hurt(this.damageSources().mobAttack(this), (float) (Objects.requireNonNull(this.getAttribute(Attributes.ATTACK_DAMAGE))).getBaseValue());
        }

    }

    public void setOwner(LivingEntity owner) {
        this.owner = owner;
    }

    public LivingEntity getOwner() {
        return this.owner;
    }

    public void setOriginalMob(LivingEntity originalMob) {
        this.originalMob = originalMob;
    }

    public LivingEntity getOriginalMob() {
        return this.originalMob;
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

    public boolean isSpiritcaller() {
        return this.entityData.get(SPIRITCALLER);
    }

    public void setSpiritcaller(boolean corrupted) {
        this.entityData.set(SPIRITCALLER, corrupted);
    }

    protected SoundEvent getHurtSound(DamageSource p_33034_) {
        return this.isSpiritcaller() ? IllageAndSpillageSoundEvents.ENTITY_MOBSPIRIT_HURTCORRUPTED.get() : IllageAndSpillageSoundEvents.ENTITY_MOBSPIRIT_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return this.isSpiritcaller() ? IllageAndSpillageSoundEvents.ENTITY_MOBSPIRIT_DEATHCORRUPTED.get() : IllageAndSpillageSoundEvents.ENTITY_MOBSPIRIT_DEATH.get();
    }

    public void handleEntityEvent(byte p_21375_) {
        if (p_21375_ != 60) {
            super.handleEntityEvent(p_21375_);
        }

    }

    static {
        GOOD_OR_EVIL = SynchedEntityData.defineId(MobSpiritEntity.class, EntityDataSerializers.BOOLEAN);
        SPIRITCALLER = SynchedEntityData.defineId(MobSpiritEntity.class, EntityDataSerializers.BOOLEAN);
    }
}

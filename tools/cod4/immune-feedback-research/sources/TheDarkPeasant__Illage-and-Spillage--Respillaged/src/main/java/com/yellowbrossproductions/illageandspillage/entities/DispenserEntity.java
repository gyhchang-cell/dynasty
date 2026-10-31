package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class DispenserEntity extends Monster implements IllagerAttack {
    private final List<IllashooterEntity> shooters = new ArrayList<>();
    private static final EntityDataAccessor<Boolean> IN_MOTION;
    private int spawnTicks;
    private Mob owner;

    public DispenserEntity(EntityType<? extends Monster> p_i48553_1_, Level p_i48553_2_) {
        super(p_i48553_1_, p_i48553_2_);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.MAX_HEALTH, 15.0).add(Attributes.ATTACK_DAMAGE, 0.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(IN_MOTION, false);
    }

    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        if (this.isInMotion()) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_DISPENSER_OPEN.get(), 1.0F, 1.0F);
            this.setInMotion(false);
        }

        return false;
    }

    public void tick() {
        if (this.isAlive() && !this.isInMotion()) {
            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
            ++this.spawnTicks;
            if (this.spawnTicks > 60 && this.shooters.size() < 5) {
                this.playSound(SoundEvents.DISPENSER_LAUNCH, 1.0F, 1.0F);
                if (!this.level().isClientSide) {
                    IllashooterEntity illashooter = ModEntityTypes.Illashooter.get().create(this.level());

                    assert illashooter != null;

                    illashooter.setPos(this.getX(), this.getY(), this.getZ());
                    illashooter.setDeltaMovement(0.0, 0.5, 0.0);
                    if (this.getTeam() != null) {
                        this.level().getScoreboard().addPlayerToTeam(illashooter.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                    }

                    illashooter.setOwner(this);
                    if (this.getOwner() != null) {
                        illashooter.setTarget(this.getOwner().getTarget());
                    }

                    if (Config.CommonConfig.nightmare_mode.get()) {
                        Objects.requireNonNull(illashooter.getAttribute(Attributes.MAX_HEALTH)).setBaseValue(6.0);
                        illashooter.heal(10);
                    }

                    this.level().addFreshEntity(illashooter);
                    this.shooters.add(illashooter);
                }

                this.spawnTicks = 0;
            }

            this.updateShooterList();
        }

        if (this.onGround()) {
            this.setInMotion(false);
        }

        super.tick();
    }

    public boolean isInMotion() {
        return this.entityData.get(IN_MOTION);
    }

    public void setInMotion(boolean motion) {
        this.entityData.set(IN_MOTION, motion);
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_DISPENSER_DESTROY.get();
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

    public void updateShooterList() {
        if (!this.shooters.isEmpty()) {
            for (int i = 0; i < this.shooters.size(); ++i) {
                IllashooterEntity clone = this.shooters.get(i);
                if (!clone.isAlive()) {
                    this.shooters.remove(i);
                    --i;
                }
            }
        }

    }

    public Mob getOwner() {
        return this.owner;
    }

    public void setOwner(Mob owner) {
        this.owner = owner;
    }

    static {
        IN_MOTION = SynchedEntityData.defineId(DispenserEntity.class, EntityDataSerializers.BOOLEAN);
    }
}

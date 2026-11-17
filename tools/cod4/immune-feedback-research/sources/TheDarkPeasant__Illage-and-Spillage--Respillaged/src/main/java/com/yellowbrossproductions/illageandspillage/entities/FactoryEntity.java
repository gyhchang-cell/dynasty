package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;

import java.util.List;
import java.util.Objects;

public class FactoryEntity extends Raider implements ICanBeAnimated, EngineerMachine, IllagerAttack {
    private static final EntityDataAccessor<Integer> ANIMATION_STATE = SynchedEntityData.defineId(FactoryEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> IN_MOTION = SynchedEntityData.defineId(FactoryEntity.class, EntityDataSerializers.BOOLEAN);
    public AnimationState introAnimationState = new AnimationState();
    public AnimationState spinAnimationState = new AnimationState();
    private int introTicks;
    private int spawnTicks;
    private LivingEntity owner;

    public FactoryEntity(EntityType<? extends Raider> p_37839_, Level p_37840_) {
        super(p_37839_, p_37840_);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.MAX_HEALTH, 30.0);
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
    }

    @Override
    public void applyRaidBuffs(int p_37844_, boolean p_37845_) {
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
    public SoundEvent getCelebrateSound() {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
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
    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        if (this.isInMotion()) {
            this.introTicks = 1;
            this.setAnimationState(2);
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
    public AnimationState getAnimationState(String var1) {
        if (Objects.equals(var1, "spin")) {
            return this.spinAnimationState;
        }
        if (Objects.equals(var1, "intro")) {
            return this.introAnimationState;
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
                    this.spinAnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.stopAllAnimationStates();
                    this.introAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    private void stopAllAnimationStates() {
        this.spinAnimationState.stop();
        this.introAnimationState.stop();
    }

    @Override
    public void knockback(double p_147241_, double p_147242_, double p_147243_) {
    }

    public List<Raider> getMinions() {
        return this.level().getEntitiesOfClass(Raider.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate instanceof FactoryMinion && ((FactoryMinion) predicate).getOwner() == this);
    }

    @Override
    public void tick() {
        if (introTicks == 1) {
            this.playSound(SoundEvents.ZOMBIE_ATTACK_IRON_DOOR);
        }

        if (introTicks > 0) {
            introTicks++;
        }

        if (introTicks == 11) {
            this.playSound(SoundEvents.PISTON_EXTEND, 1.0F, 0.75F);
        }

        if (introTicks == 16) {
            this.playSound(SoundEvents.PISTON_EXTEND, 1.0F, 1.0F);
        }

        if (introTicks == 21) {
            this.playSound(SoundEvents.PISTON_EXTEND, 1.0F, 1.25F);
        }

        if (!this.isInMotion()) {
            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
            ++this.spawnTicks;
            if (this.spawnTicks > 60 && this.isAlive() && this.getMinions().size() < 5) {
                this.playSound(SoundEvents.DISPENSER_LAUNCH, 1.0F, 1.0F);
                int randomSelection = this.random.nextInt(0, 3);
                if (!this.level().isClientSide) {
                    if (randomSelection == 0) {
                        BeeperEntity beeper = ModEntityTypes.Beeper.get().create(this.level());

                        assert beeper != null;

                        float f = this.yBodyRot * ((float) Math.PI / 180F) * 0.25F;
                        float f1 = Mth.cos(f);
                        beeper.setPos(this.getX(), this.getY(), this.getZ() + (double) f1 * -0.1D);

                        beeper.setDeltaMovement(0.0, 0.5, 0.0);
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(beeper.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        beeper.setOwner(this);

                        this.level().addFreshEntity(beeper);
                    } else if (randomSelection == 1) {
                        SniperEntity sniper = ModEntityTypes.Sniper.get().create(this.level());

                        assert sniper != null;

                        float f = this.yBodyRot * ((float) Math.PI / 180F) * 0.25F;
                        float f1 = Mth.cos(f);
                        sniper.setPos(this.getX() + (double) f1 * 0.45D, this.getY(), this.getZ() + (double) f1 * -0.2D);

                        sniper.setDeltaMovement(0.0, 0.1, 0.0);
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(sniper.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        sniper.setOwner(this);

                        this.level().addFreshEntity(sniper);
                    } else {
                        PokerEntity poker = ModEntityTypes.Poker.get().create(this.level());

                        assert poker != null;

                        float f = this.yBodyRot * ((float) Math.PI / 180F) * 0.25F;
                        float f1 = Mth.cos(f);
                        poker.setPos(this.getX() + (double) f1 * -0.55D, this.getY(), this.getZ() + (double) f1 * 0.05D);

                        poker.setDeltaMovement(0.0, 0.5, 0.0);
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(poker.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        poker.setOwner(this);

                        poker.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.IRON_SWORD));
                        poker.setDropChance(EquipmentSlot.MAINHAND, 0.0F);
                        poker.setDropChance(EquipmentSlot.OFFHAND, 0.0F);

                        this.level().addFreshEntity(poker);
                    }
                }

                this.spawnTicks = 0;
            }
        }

        if (this.onGround() && isInMotion()) {
            if (introTicks < 1) introTicks = 1;
            this.setAnimationState(2);
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
}
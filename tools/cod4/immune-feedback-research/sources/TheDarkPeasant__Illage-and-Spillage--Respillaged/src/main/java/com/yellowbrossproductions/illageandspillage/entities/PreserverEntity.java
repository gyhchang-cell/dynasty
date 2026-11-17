package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.EffectRegisterer;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import javax.annotation.Nullable;
import java.util.EnumSet;
import java.util.List;

public class PreserverEntity extends AbstractIllager {
    private static final EntityDataAccessor<Boolean> TRYING_TO_PROTECT;
    private static final EntityDataAccessor<Integer> JUMP_ANIM_TICKS;
    private LivingEntity thingToProtect = null;
    private int cooldownTime;
    private LivingEntity entityToParticle;
    private int tickCountWhenProtected;

    public PreserverEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new TryToProtectGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(2, new Raider.HoldGroundAttackGoal(this, 10.0F));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 1.0));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.30000001192092896).add(Attributes.MAX_HEALTH, 20.0).add(Attributes.ATTACK_DAMAGE, 0.0).add(Attributes.FOLLOW_RANGE, 32.0).add(Attributes.KNOCKBACK_RESISTANCE, 0.7);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(TRYING_TO_PROTECT, false);
        this.entityData.define(JUMP_ANIM_TICKS, 0);
    }

    public boolean canBeLeader() {
        return false;
    }

    public boolean causeFallDamage(float p_147187_, float p_147188_, DamageSource p_147189_) {
        if (this.isTryingToProtect()) {
            if (this.getThingToProtect() != null && this.getThingToProtect().isAlive() && this.getThingToProtect().distanceToSqr(this) < 6.0) {
                this.getThingToProtect().addEffect(new MobEffectInstance(EffectRegisterer.PRESERVED.get(), MobEffectInstance.INFINITE_DURATION, 0, false, false));
                this.entityToParticle = this.getThingToProtect();
                this.tickCountWhenProtected = this.getThingToProtect().tickCount;
            }

            this.setTryingToProtect(false);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_PRESERVER_LAND.get(), 1.0F, 1.0F);
            if (!this.level().isClientSide) {
                this.setJumpAnimationTick(0);
            }

            this.cooldownTime = 200;
        }

        return false;
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public void tick() {
        super.tick();

        if (this.entityToParticle != null && !this.entityToParticle.level().isClientSide && this.entityToParticle.tickCount - 10 < this.tickCountWhenProtected) {
            for (ServerPlayer serverPlayer : ((ServerLevel) this.level()).players()) {
                if (serverPlayer.distanceToSqr(this.entityToParticle) < 4096.0D) {
                    ParticlePacket packet = new ParticlePacket();

                    for (int i = 0; i < 10; i++) {
                        double d0 = (-0.5 + this.entityToParticle.getRandom().nextGaussian()) / 4.0;
                        double d1 = (-0.5 + this.entityToParticle.getRandom().nextGaussian()) / 4.0;
                        double d2 = (-0.5 + this.entityToParticle.getRandom().nextGaussian()) / 4.0;
                        packet.queueParticle(ParticleTypes.EXPLOSION, false, new Vec3(this.entityToParticle.getRandomX(1.0), this.entityToParticle.getRandomY() + 1.0, this.entityToParticle.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                    }

                    PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> serverPlayer), packet);
                }
            }
        }

        if (this.cooldownTime > 0) {
            --this.cooldownTime;
        }

        if (this.isTryingToProtect()) {
            if (!this.level().isClientSide) {
                this.setJumpAnimationTick(this.getJumpAnimationTick() + 1);
            }

            this.setYRot(this.getYHeadRot());
            this.yBodyRot = this.getYRot();
            LivingEntity thing = this.getThingToProtect();
            if (this.getThingToProtect() != null) {
                this.getLookControl().setLookAt(this.getThingToProtect(), 100.0F, 100.0F);
            }

            if (this.getThingToProtect() != null) {
                thing.setDeltaMovement(0.0, thing.getDeltaMovement().y, 0.0);
            }

            if (this.getJumpAnimationTick() == 20 && this.getThingToProtect() != null) {
                double multiplier = 0.4;
                this.setDeltaMovement((thing.getX() - this.getX()) * multiplier, (thing.getY() - this.getY()) * multiplier, (thing.getZ() - this.getZ()) * multiplier);
            }
        }

    }

    public int getJumpAnimationTick() {
        return this.entityData.get(JUMP_ANIM_TICKS);
    }

    public void setJumpAnimationTick(int tick) {
        this.entityData.set(JUMP_ANIM_TICKS, tick);
    }

    public boolean isTryingToProtect() {
        return this.entityData.get(TRYING_TO_PROTECT);
    }

    public void setTryingToProtect(boolean trying) {
        this.entityData.set(TRYING_TO_PROTECT, trying);
    }

    public LivingEntity getThingToProtect() {
        return this.thingToProtect;
    }

    public void setThingToProtect(LivingEntity thingToProtect) {
        this.thingToProtect = thingToProtect;
    }

    @Nullable
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor p_213386_1_, DifficultyInstance p_213386_2_, MobSpawnType p_213386_3_, @Nullable SpawnGroupData p_213386_4_, @Nullable CompoundTag p_213386_5_) {
        this.cooldownTime = 100;
        return super.finalizeSpawn(p_213386_1_, p_213386_2_, p_213386_3_, p_213386_4_, p_213386_5_);
    }

    public boolean hurt(DamageSource source, float amount) {
        if (!source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL) && !source.is(DamageTypeTags.IS_FIRE)) {
            amount *= 0.5F;
        }

        return super.hurt(source, amount);
    }

    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_PRESERVER_AMBIENT.get();
    }

    protected SoundEvent getAmbientSound() {
        return IllageAndSpillageSoundEvents.ENTITY_PRESERVER_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_PRESERVER_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_PRESERVER_DEATH.get();
    }

    public boolean isSomethingProtectableNearby() {
        return !this.level().getEntitiesOfClass(Raider.class, this.getBoundingBox().inflate(12.0), (predicate) -> !(predicate instanceof IllagerAttack) && !(predicate instanceof EngineerMachine) && !(predicate instanceof FactoryMinion) && (double) predicate.getBbWidth() < 1.0 && (double) predicate.getBbHeight() < 2.5 && this.hasLineOfSight(predicate) && predicate.isAlive() && !(predicate instanceof PreserverEntity) && !predicate.hasEffect(EffectRegisterer.PRESERVED.get()) && EntityUtil.isMobNotOnOtherTeam(predicate, this) && !(Config.CommonConfig.preserver_cannotProtect.get()).contains(predicate.getEncodeId())).isEmpty();
    }

    protected float getStandingEyeHeight(Pose p_21131_, EntityDimensions p_21132_) {
        return this.isTryingToProtect() ? 1.125F : 1.75F;
    }

    static {
        TRYING_TO_PROTECT = SynchedEntityData.defineId(PreserverEntity.class, EntityDataSerializers.BOOLEAN);
        JUMP_ANIM_TICKS = SynchedEntityData.defineId(PreserverEntity.class, EntityDataSerializers.INT);
    }

    class TryToProtectGoal extends Goal {
        public boolean canUse() {
            return PreserverEntity.this.random.nextInt(8) == 0 && PreserverEntity.this.isSomethingProtectableNearby() && PreserverEntity.this.onGround() && PreserverEntity.this.cooldownTime < 1 && PreserverEntity.this.hurtTime < 1 && !PreserverEntity.this.isTryingToProtect();
        }

        public boolean canContinueToUse() {
            return PreserverEntity.this.isTryingToProtect();
        }

        public TryToProtectGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public void start() {
            List<Raider> list = PreserverEntity.this.level().getEntitiesOfClass(Raider.class, PreserverEntity.this.getBoundingBox().inflate(6.0), (predicate) -> !(predicate instanceof IllagerAttack) && !(predicate instanceof EngineerMachine) && !(predicate instanceof FactoryMinion) && (double) predicate.getBbWidth() < 1.0 && (double) predicate.getBbHeight() < 2.5 && PreserverEntity.this.hasLineOfSight(predicate) && predicate.isAlive() && !(predicate instanceof PreserverEntity) && !predicate.hasEffect(EffectRegisterer.PRESERVED.get()) && EntityUtil.isMobNotOnOtherTeam(predicate, PreserverEntity.this) && !(Config.CommonConfig.preserver_cannotProtect.get()).contains(predicate.getEncodeId()));
            if (!list.isEmpty()) {
                LivingEntity thing = list.get(PreserverEntity.this.random.nextInt(list.size()));
                PreserverEntity.this.setThingToProtect(thing);
                double multiplier = 0.2;
                PreserverEntity.this.setDeltaMovement((thing.getX() - PreserverEntity.this.getX()) * multiplier, 1.2, (thing.getZ() - PreserverEntity.this.getZ()) * multiplier);
                PreserverEntity.this.setTryingToProtect(true);
                PreserverEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_PRESERVER_JUMP.get(), 1.0F, 1.0F);
            }

        }
    }
}
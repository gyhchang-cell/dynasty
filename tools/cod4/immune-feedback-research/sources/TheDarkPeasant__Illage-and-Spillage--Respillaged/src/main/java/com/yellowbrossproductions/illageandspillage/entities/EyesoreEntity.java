package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.entities.goal.StareAtDeadFreakGoal;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.particle.ParticleRegisterer;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.util.DefaultRandomPos;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;
import java.util.Iterator;
import java.util.List;
import java.util.Objects;

public class EyesoreEntity extends Monster implements ICanBeAnimated, IllagerAttack {
    private static final EntityDataAccessor<Integer> ANIMATION_STATE = SynchedEntityData.defineId(EyesoreEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> FLYING = SynchedEntityData.defineId(EyesoreEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> SCARED = SynchedEntityData.defineId(EyesoreEntity.class, EntityDataSerializers.BOOLEAN);
    public AnimationState slitherAnimationState = new AnimationState();
    public AnimationState flyAnimationState = new AnimationState();
    private LivingEntity owner = null;
    private BlockPos targetPos;

    public EyesoreEntity(EntityType<? extends Monster> p_33002_, Level p_33003_) {
        super(p_33002_, p_33003_);
        this.xpReward = 0;
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new StareAtDeadFreakGoal(this));
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(0, new AvoidRagnoGoal(this, 16.0F, 0.65F, 0.6F));
        this.goalSelector.addGoal(1, new SlitherGoal(this, 0.5F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.75).add(Attributes.MAX_HEALTH, 5.0).add(Attributes.ATTACK_DAMAGE, 4.0).add(Attributes.FOLLOW_RANGE, 24.0);
    }

    public void setOwner(LivingEntity owner) {
        this.owner = owner;
    }

    public LivingEntity getOwner() {
        return owner;
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_EYESORE_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource p_33034_) {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_EYESORE_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_EYESORE_DEATH.get();
    }

    @Override
    public void setTarget(@Nullable LivingEntity p_21544_) {
        if (this.owner != null && this.owner.isAlive() && this.owner instanceof Mob && p_21544_ == ((Mob) this.owner).getTarget()) {
            super.setTarget(p_21544_);
        } else if (this.owner == null || !this.owner.isAlive()) {
            super.setTarget(p_21544_);
        }
    }

    public void setAnimationState(int state) {
        this.entityData.set(ANIMATION_STATE, state);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(FLYING, false);
        this.entityData.define(SCARED, false);
    }

    @Override
    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        if (this.isFlying()) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_EYESORE_LAND.get(), 2.0F, this.getVoicePitch());
            this.setFlying(false);
            return false;
        }

        return super.causeFallDamage(p_225503_1_, p_225503_2_, p_147189_);
    }

    @Override
    public AnimationState getAnimationState(String var1) {
        if (Objects.equals(var1, "fly")) {
            return this.flyAnimationState;
        }
        return Objects.equals(var1, "slither") ? this.slitherAnimationState : new AnimationState();
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                case 0 -> this.stopAllAnimationStates();
                case 1 -> {
                    this.stopAllAnimationStates();
                    this.slitherAnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.stopAllAnimationStates();
                    this.flyAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    private void stopAllAnimationStates() {
        this.slitherAnimationState.stop();
        this.flyAnimationState.stop();
    }

    @Override
    public float getAnimationSpeed() {
        return this.entityData.get(ANIMATION_STATE) == 1 ? 2.5F : 1.0F;
    }

    @Override
    public boolean hurt(DamageSource p_37849_, float p_37850_) {
        boolean superHurt = super.hurt(p_37849_, p_37850_);
        if (superHurt) {
            this.makeBloodParticles();
        }
        return superHurt;
    }

    public void makeCryParticles() {
        if (!this.level().isClientSide) {
            Iterator<ServerPlayer> var1 = ((ServerLevel) this.level()).players().iterator();

            while (true) {
                ServerPlayer serverPlayer;
                do {
                    if (!var1.hasNext()) {
                        return;
                    }

                    serverPlayer = var1.next();
                } while (!(serverPlayer.distanceToSqr(this) < 4096.0));

                ParticlePacket packet = new ParticlePacket();

                double d0 = -0.5 + this.random.nextGaussian();
                double d1 = -0.5 + this.random.nextGaussian();
                double d2 = -0.5 + this.random.nextGaussian();
                packet.queueParticle(ParticleTypes.SPLASH, false, new Vec3(this.getRandomX(0.5), this.getRandomY(), this.getRandomZ(0.5)), new Vec3(d0, d1, d2));

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeBloodParticles() {
        if (!this.level().isClientSide) {
            Iterator<ServerPlayer> var1 = ((ServerLevel) this.level()).players().iterator();

            while (true) {
                ServerPlayer serverPlayer;
                do {
                    if (!var1.hasNext()) {
                        return;
                    }

                    serverPlayer = var1.next();
                } while (!(serverPlayer.distanceToSqr(this) < 4096.0));

                ParticlePacket packet = new ParticlePacket();

                for (int i = 0; i < 5; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (1.0 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleRegisterer.BLOOD_PARTICLES.get(), false, new Vec3(this.getX(), this.getY(), this.getZ()), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    @Override
    public void tick() {
        super.tick();

        if (!this.isFlying() && this.entityData.get(ANIMATION_STATE) != 1) this.setAnimationState(1);

        this.targetPos = this.getTarget() != null && this.getTarget().isAlive() ? this.getTarget().getOnPos() : null;

        if (this.owner != null && this.owner.isAlive() && this.owner instanceof Mob && this.getTarget() != ((Mob) this.owner).getTarget()) {
            this.setTarget(((Mob) this.owner).getTarget());
        }

        List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(0.7));
        for (LivingEntity hit : list) {
            if (this.isEffectiveAi() && EntityUtil.canHurtThisMob(hit, this) && !(hit instanceof EyesoreEntity)) {
                this.dealDamage(hit);
            }
        }

        if (this.onGround()) {
            this.setFlying(false);
        }

        if (this.isScared()) {
            this.makeCryParticles();
        }
    }

    public boolean isFlying() {
        return this.entityData.get(FLYING);
    }

    public void setFlying(boolean flying) {
        this.entityData.set(FLYING, flying);
        this.setAnimationState(flying ? 2 : 1);
    }

    public boolean isScared() {
        return this.entityData.get(SCARED);
    }

    public void setScared(boolean scared) {
        this.entityData.set(SCARED, scared);
    }

    protected void dealDamage(LivingEntity entity) {
        if (this.isAlive()) {
            if (this.hasLineOfSight(entity) && entity.hurt(this.damageSources().mobAttack(this), (float) this.getAttributeValue(Attributes.ATTACK_DAMAGE))) {
                double d2 = entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE);
                double d1 = Math.max(0.0D, 1.0D - d2);
                entity.setDeltaMovement(entity.getDeltaMovement().add(0.0D, (double) 0.4F * d1, 0.0D));
                this.playSound(SoundEvents.SLIME_ATTACK, 1.0F, (this.random.nextFloat() - this.random.nextFloat()) * 0.2F + 1.0F);
                this.doEnchantDamageEffects(this, entity);
            }
        }

    }

    public boolean shouldAvoidRagno() {
        List<RagnoEntity> ragnos = this.level().getEntitiesOfClass(RagnoEntity.class, this.getBoundingBox().inflate(11.0));
        for (RagnoEntity ragno : ragnos) {
            if (ragno.isCrazy()) {
                return true;
            }
        }
        return false;
    }

    class SlitherGoal extends Goal {
        protected final EyesoreEntity eyesore;
        protected final double speedModifier;
        protected double posX;
        protected double posY;
        protected double posZ;

        public SlitherGoal(EyesoreEntity p_25691_, double p_25692_) {
            this.eyesore = p_25691_;
            this.speedModifier = p_25692_;
            this.setFlags(EnumSet.of(Goal.Flag.MOVE));
        }

        public boolean canUse() {
            if (this.eyesore.shouldAvoidRagno()) return false;

            BlockPos targetPos = EyesoreEntity.this.targetPos;

            Vec3 vec3;
            if (targetPos == null || this.eyesore.position().distanceToSqr(targetPos.getCenter()) <= 256) {
                vec3 = DefaultRandomPos.getPos(this.eyesore, 5, 4);
            } else {
                LivingEntity mob = this.eyesore.getTarget() != null ? this.eyesore.getTarget() : this.eyesore;
                vec3 = mob.getOnPos().getCenter();
            }

            if (targetPos != null && vec3 != null) {
                this.posX = vec3.x;
                this.posY = vec3.y;
                this.posZ = vec3.z;
                return true;
            } else if (targetPos == null && vec3 != null) {
                this.posX = vec3.x;
                this.posY = vec3.y;
                this.posZ = vec3.z;
                return true;
            }

            return false;
        }

        public void start() {
            this.eyesore.getNavigation().moveTo(this.posX, this.posY, this.posZ, this.speedModifier);
        }

        public boolean canContinueToUse() {
            return !this.eyesore.getNavigation().isDone() && !this.eyesore.shouldAvoidRagno();
        }
    }

    class AvoidRagnoGoal extends AvoidEntityGoal {
        public AvoidRagnoGoal(PathfinderMob p_25033_, float p_25035_, double p_25036_, double p_25037_) {
            super(p_25033_, RagnoEntity.class, p_25035_, p_25036_, p_25037_, (predicate) -> EntityUtil.isEntityCrazyRagno((Entity) predicate));
        }

        @Override
        public void start() {
            super.start();
            setScared(true);
        }

        @Override
        public void stop() {
            super.stop();
            setScared(false);
        }
    }
}
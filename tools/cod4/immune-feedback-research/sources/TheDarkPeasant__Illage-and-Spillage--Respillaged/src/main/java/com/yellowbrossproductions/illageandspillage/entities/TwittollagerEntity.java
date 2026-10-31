package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
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
import net.minecraft.world.Difficulty;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.npc.Villager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import java.util.EnumSet;
import java.util.Iterator;

public class TwittollagerEntity extends AbstractIllager {
    private static final EntityDataAccessor<Boolean> ANGRY;
    private static final EntityDataAccessor<Boolean> STARING;
    private static final EntityDataAccessor<Boolean> PHONE_DINGED;
    private static final EntityDataAccessor<Boolean> HMM;
    private static final EntityDataAccessor<Boolean> CHECKING_PHONE;
    private static final EntityDataAccessor<Integer> GRRRRRRRRRRRRR_TICKS;
    private static final EntityDataAccessor<Boolean> CAN_CHARGE;
    private static final EntityDataAccessor<Boolean> EXPLODE;
    private int checkPhoneTicks;
    private int waitTime;
    private boolean isAngry;
    private boolean canExplodeInfinitely;

    public TwittollagerEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new ChargeAtTargetGoal());
        this.goalSelector.addGoal(0, new StareAggressivelyGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(2, new Raider.HoldGroundAttackGoal(this, 10.0F));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.2, false));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 1.0));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, GlowSquid.class, true));
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Sheep.class, 10, false, false, (p_234199_0_) -> p_234199_0_ instanceof Sheep && ((Sheep) p_234199_0_).getColor() == DyeColor.PINK));
        this.targetSelector.addGoal(3, (new HurtByTargetGoal(this, TwittollagerEntity.class)).setAlertOthers());
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(5, new NearestAttackableTargetGoal<>(this, Villager.class, 10, false, false, (p_234199_0_) -> p_234199_0_ instanceof Villager && ((Villager) p_234199_0_).getAge() < 0));
        this.targetSelector.addGoal(6, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(6, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.20000000298023224).add(Attributes.MAX_HEALTH, 24.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("IsAngry", isAngry);
        tag.putBoolean("CanExplodeInfinitely", canExplodeInfinitely);
    }

    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.isAngry = tag.getBoolean("IsAngry");
        this.canExplodeInfinitely = tag.getBoolean("CanExplodeInfinitely");
        this.setAngry(isAngry);
        this.setCanCharge(isAngry);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANGRY, false);
        this.entityData.define(STARING, false);
        this.entityData.define(PHONE_DINGED, false);
        this.entityData.define(HMM, false);
        this.entityData.define(CHECKING_PHONE, false);
        this.entityData.define(GRRRRRRRRRRRRR_TICKS, 0);
        this.entityData.define(CAN_CHARGE, false);
        this.entityData.define(EXPLODE, false);
    }

    public boolean canAttack(LivingEntity p_186270_) {
        return (!(p_186270_ instanceof Player) || this.level().getDifficulty() != Difficulty.PEACEFUL) && p_186270_.canBeSeenAsEnemy();
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public void tick() {
        super.tick();
        if (this.getTarget() instanceof GlowSquid && !this.isAngry()) {
            this.checkPhoneTicks = 115;
            if (!this.level().isClientSide) {
                this.setAngry(true);
            }

            this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_ANGRY.get(), 2.0F, 1.0F);
        }

        if (this.getTarget() instanceof Sheep && ((Sheep) this.getTarget()).getColor() == DyeColor.PINK && !this.isAngry()) {
            this.checkPhoneTicks = 115;
            if (!this.level().isClientSide) {
                this.setAngry(true);
            }

            this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_ANGRY.get(), 2.0F, 1.0F);
        }

        if (this.getTarget() instanceof Villager && ((Villager) this.getTarget()).getAge() < 0 && !this.isAngry()) {
            this.checkPhoneTicks = 115;
            if (!this.level().isClientSide) {
                this.setAngry(true);
            }

            this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_ANGRY.get(), 2.0F, 1.0F);
        }

        if (this.isStaring()) {
            ++this.waitTime;
            if (this.waitTime > 60 && this.random.nextInt(25) == 0 && !this.hasPhoneDinged() && !this.isAngry()) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_DING.get(), 1.0F, 1.0F);
                this.setPhoneDinged(true);
            }
        }

        if (this.hasPhoneDinged() || this.isAngry()) {
            ++this.checkPhoneTicks;
            if (!this.isAngry()) {
                if (this.checkPhoneTicks == 15) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_HMM.get(), 1.0F, 1.0F);
                    if (!this.level().isClientSide) {
                        this.setHmm(true);
                    }
                }

                if (this.checkPhoneTicks == 35 && !this.level().isClientSide) {
                    this.setCheckingPhone(true);
                }

                if (this.checkPhoneTicks == 115) {
                    if (!this.level().isClientSide) {
                        this.setAngry(true);
                    }

                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_ANGRY.get(), 2.0F, 1.0F);
                }
            }
        }

        if (this.isAngry()) {
            if (!this.level().isClientSide && this.getGRRRRRRRRRR() < 60) {
                this.setGRRRRRRRRRRRRRR(this.getGRRRRRRRRRR() + 1);
            }

            if (this.checkPhoneTicks == 184) {
                this.setCanCharge(true);
                if (!this.level().isClientSide) {
                    this.setCheckingPhone(false);
                }
            }
        }

    }

    public boolean hurt(DamageSource source, float amount) {
        if (source.is(DamageTypeTags.IS_EXPLOSION) && source.getEntity() instanceof TwittollagerEntity) {
            return false;
        } else {
            if (source.getEntity() != null && !this.isAngry()) {
                this.checkPhoneTicks = 115;
                if (!this.level().isClientSide) {
                    this.setAngry(true);
                }

                this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_ANGRY.get(), 2.0F, 1.0F);
            }

            return super.hurt(source, amount);
        }
    }

    public boolean canBeLeader() {
        return false;
    }

    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_CELEBRATE.get();
    }

    protected SoundEvent getAmbientSound() {
        return !this.hasPhoneDinged() && !this.isAngry() ? IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_AMBIENT.get() : null;
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return this.isExplode() && !this.canExplodeInfinitely ? null : IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_DEATH.get();
    }

    public boolean isAngry() {
        return this.entityData.get(ANGRY);
    }

    public void setAngry(boolean angry) {
        this.entityData.set(ANGRY, angry);
    }

    public boolean isStaring() {
        return this.entityData.get(STARING);
    }

    public void setStaring(boolean angry) {
        this.entityData.set(STARING, angry);
    }

    public boolean hasPhoneDinged() {
        return this.entityData.get(PHONE_DINGED);
    }

    public void setPhoneDinged(boolean ding) {
        this.entityData.set(PHONE_DINGED, ding);
    }

    public boolean isHmm() {
        return this.entityData.get(HMM);
    }

    public void setHmm(boolean hmm) {
        this.entityData.set(HMM, hmm);
    }

    public boolean isCheckingPhone() {
        return this.entityData.get(CHECKING_PHONE);
    }

    public void setCheckingPhone(boolean check) {
        this.entityData.set(CHECKING_PHONE, check);
    }

    public int getGRRRRRRRRRR() {
        return this.entityData.get(GRRRRRRRRRRRRR_TICKS);
    }

    public void setGRRRRRRRRRRRRRR(int grrrrr) {
        this.entityData.set(GRRRRRRRRRRRRR_TICKS, grrrrr);
    }

    public boolean canCharge() {
        return this.entityData.get(CAN_CHARGE);
    }

    public void setCanCharge(boolean charge) {
        this.entityData.set(CAN_CHARGE, charge);
    }

    public boolean isExplode() {
        return this.entityData.get(EXPLODE);
    }

    public void setExplode(boolean boom) {
        this.entityData.set(EXPLODE, boom);
    }

    public boolean doHurtTarget(Entity p_70652_1_) {
        return false;
    }

    private void explode() {
        this.setExplode(true);
        this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_EXPLODE.get(), 6.0F, 1.0F);
        this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_SCREAM.get(), 6.0F, 1.0F);
        CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.4F, 0, 20);
        if (!this.canExplodeInfinitely) this.kill();
        this.makeExplodeParticles();
        if (!this.level().isClientSide) {
            this.level().explode(this, this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);
        }

    }

    public void die(DamageSource p_37847_) {
        if (this.isExplode() && !this.canExplodeInfinitely) {
            this.deathTime = 19;
        }

        super.die(p_37847_);
    }

    public void handleEntityEvent(byte p_21375_) {
        if (p_21375_ == 60) {
            if (!this.isExplode()) {
                super.handleEntityEvent(p_21375_);
            }
        } else {
            super.handleEntityEvent(p_21375_);
        }

    }

    public void makeExplodeParticles() {
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

                int i;
                double random;
                double d1;
                double d2;
                for (i = 0; i < 250; ++i) {
                    random = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(random, d1, d2));
                }

                for (i = 0; i < 200; ++i) {
                    random = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.POOF, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(random, d1, d2));
                }

                for (i = 0; i < 150; ++i) {
                    random = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.LARGE_SMOKE, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(random, d1, d2));
                }

                for (i = 0; i < 75; ++i) {
                    random = (-0.5 + this.random.nextDouble()) / 2.0;
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() - 2.0 + random, this.getY() + 1.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() + 2.0 + random, this.getY() + 1.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() - 1.0 + random, this.getY() + 2.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() + 1.0 + random, this.getY() + 2.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() + 0.0 + random, this.getY() + 2.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() - 2.0 + random, this.getY() + 5.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() + 2.0 + random, this.getY() + 5.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() - 1.0 + random, this.getY() + 4.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                    packet.queueParticle(ParticleTypes.CAMPFIRE_SIGNAL_SMOKE, false, new Vec3(this.getX() + 1.0 + random, this.getY() + 4.0 + random, this.getZ() + random), new Vec3(0.0, 0.14, 0.0));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    static {
        ANGRY = SynchedEntityData.defineId(TwittollagerEntity.class, EntityDataSerializers.BOOLEAN);
        STARING = SynchedEntityData.defineId(TwittollagerEntity.class, EntityDataSerializers.BOOLEAN);
        PHONE_DINGED = SynchedEntityData.defineId(TwittollagerEntity.class, EntityDataSerializers.BOOLEAN);
        HMM = SynchedEntityData.defineId(TwittollagerEntity.class, EntityDataSerializers.BOOLEAN);
        CHECKING_PHONE = SynchedEntityData.defineId(TwittollagerEntity.class, EntityDataSerializers.BOOLEAN);
        GRRRRRRRRRRRRR_TICKS = SynchedEntityData.defineId(TwittollagerEntity.class, EntityDataSerializers.INT);
        CAN_CHARGE = SynchedEntityData.defineId(TwittollagerEntity.class, EntityDataSerializers.BOOLEAN);
        EXPLODE = SynchedEntityData.defineId(TwittollagerEntity.class, EntityDataSerializers.BOOLEAN);
    }

    class ChargeAtTargetGoal extends Goal {
        public ChargeAtTargetGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return TwittollagerEntity.this.getTarget() != null && TwittollagerEntity.this.hasLineOfSight(TwittollagerEntity.this.getTarget()) && TwittollagerEntity.this.canCharge();
        }

        public void start() {
            TwittollagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_TWITTOLLAGER_CHARGE.get(), 2.0F, 1.0F);
        }

        public boolean canContinueToUse() {
            return TwittollagerEntity.this.getTarget() != null && TwittollagerEntity.this.hasLineOfSight(TwittollagerEntity.this.getTarget());
        }

        public void tick() {
            if (TwittollagerEntity.this.getTarget() != null) {
                TwittollagerEntity.this.getNavigation().moveTo(TwittollagerEntity.this.getTarget(), 2.5);
                TwittollagerEntity.this.getLookControl().setLookAt(TwittollagerEntity.this.getTarget(), 30.0F, 30.0F);
                TwittollagerEntity.this.navigation.moveTo(TwittollagerEntity.this.getTarget(), 2.5);
                if (TwittollagerEntity.this.distanceToSqr(TwittollagerEntity.this.getTarget()) < 4.5) {
                    TwittollagerEntity.this.explode();
                }
            }

        }

        public void stop() {
            TwittollagerEntity.this.getNavigation().stop();
            TwittollagerEntity.this.navigation.stop();
        }
    }

    class StareAggressivelyGoal extends Goal {
        public StareAggressivelyGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return TwittollagerEntity.this.getTarget() != null && TwittollagerEntity.this.distanceToSqr(TwittollagerEntity.this.getTarget()) < 150.0 && TwittollagerEntity.this.hasLineOfSight(TwittollagerEntity.this.getTarget()) && !TwittollagerEntity.this.canCharge();
        }

        public void start() {
            TwittollagerEntity.this.setStaring(true);
        }

        public boolean canContinueToUse() {
            return (TwittollagerEntity.this.getTarget() != null && TwittollagerEntity.this.distanceToSqr(TwittollagerEntity.this.getTarget()) < 150.0 && TwittollagerEntity.this.getTarget().isAlive() && TwittollagerEntity.this.hasLineOfSight(TwittollagerEntity.this.getTarget()) || TwittollagerEntity.this.hasPhoneDinged()) && !TwittollagerEntity.this.canCharge();
        }

        public void tick() {
            TwittollagerEntity.this.getNavigation().stop();
            if (TwittollagerEntity.this.checkPhoneTicks >= 30 && TwittollagerEntity.this.hasPhoneDinged()) {
                TwittollagerEntity.this.getLookControl().setLookAt(TwittollagerEntity.this.getX(), TwittollagerEntity.this.getY(), TwittollagerEntity.this.getZ(), 30.0F, 30.0F);
            } else if (TwittollagerEntity.this.getTarget() != null) {
                TwittollagerEntity.this.getLookControl().setLookAt(TwittollagerEntity.this.getTarget(), 30.0F, 30.0F);
            }

            TwittollagerEntity.this.navigation.stop();
        }

        public void stop() {
            TwittollagerEntity.this.setStaring(false);
        }
    }
}

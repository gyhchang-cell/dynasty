package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.client.sound.BossMusicPlayer;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.projectile.PumpkinBombEntity;
import com.yellowbrossproductions.illageandspillage.entities.projectile.WebEntity;
import com.yellowbrossproductions.illageandspillage.entities.projectile.WebNetEntity;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.particle.ParticleRegisterer;
import com.yellowbrossproductions.illageandspillage.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.util.Mth;
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.memory.MemoryModuleType;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WallClimberNavigation;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.warden.AngerLevel;
import net.minecraft.world.entity.monster.warden.Warden;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.entity.vehicle.DismountHelper;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.fluids.FluidType;
import net.minecraftforge.network.PacketDistributor;
import org.jetbrains.annotations.NotNull;

import java.util.*;

public class RagnoEntity extends Raider implements ICanBeAnimated {
    public ServerBossEvent bossEvent;
    private static final UUID SPEED_PENALTY_UUID = UUID.fromString("5CD17A52-AB9A-42D3-A629-90FDE04B281E");
    private static final AttributeModifier SPEED_PENALTY;
    private static final EntityDataAccessor<Byte> DATA_FLAGS_ID;
    private static final EntityDataAccessor<Integer> ANIMATION_STATE;
    private static final EntityDataAccessor<Boolean> CRAZY;
    private static final EntityDataAccessor<Boolean> BURROWING = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> GRABBING = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> STUN_HEALTH = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> STUNNED;
    private static final EntityDataAccessor<Integer> ATTACK_TYPE;
    private static final EntityDataAccessor<Integer> ATTACK_TICKS = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> RAGNO_FACE = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> SHAKE_MULTIPLIER = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> FRAME = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> ANTICHEESE = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.BOOLEAN);
    public AnimationState intro1AnimationState = new AnimationState();
    public AnimationState intro2AnimationState = new AnimationState();
    public AnimationState phaseAnimationState = new AnimationState();
    public AnimationState blockAnimationState = new AnimationState();
    public AnimationState attackAnimationState = new AnimationState();
    public AnimationState webAnimationState = new AnimationState();
    public AnimationState webNetAnimationState = new AnimationState();
    public AnimationState pullInAnimationState = new AnimationState();
    public AnimationState netSlamAnimationState = new AnimationState();
    public AnimationState jumpAnimationState = new AnimationState();
    public AnimationState landAnimationState = new AnimationState();
    public AnimationState leapAnimationState = new AnimationState();
    public AnimationState burrowAnimationState = new AnimationState();
    public AnimationState popupAnimationState = new AnimationState();
    public AnimationState chargeAnimationState = new AnimationState();
    public AnimationState coughAnimationState = new AnimationState();
    public AnimationState stunAnimationState = new AnimationState();
    public AnimationState fallAnimationState = new AnimationState();
    public AnimationState grabAnimationState = new AnimationState();
    public AnimationState breathAnimationState = new AnimationState();
    public AnimationState deathAnimationState = new AnimationState();
    public LivingEntity entityToStareAt;
    private int attackCooldown;
    private final int WEB_ATTACK = 1;
    private final int LEAP_ATTACK = 2;
    private final int BURROW_ATTACK = 3;
    private final int CHARGE_ATTACK = 4;
    private final int COUGH_ATTACK = 5;
    private final int ATTACK_ATTACK = 6;
    private final int JUMP_ATTACK = 7;
    private final int WEB_NET_ATTACK = 8;
    private final int BREATH_ATTACK = 9;
    private final int ANTICHEESE_ATTACK = 10;
    private int webCooldown;
    private int webNetCooldown;
    private int jumpCooldown;
    private int leapCooldown;
    private int burrowCooldown;
    private int chargeCooldown;
    private int coughCooldown;
    private int breathCooldown;
    int introTicks;
    int phaseTicks;
    private Mob owner;
    int blockTicks;
    boolean shouldHurtOnTouch;
    public boolean isPlayingIntro;
    public boolean isPlayingPhase;
    public boolean waitingForWeb;
    public int followupTicks;
    public double chargeX;
    public double chargeZ;
    public boolean circleDirection;
    public int circleTick;
    public int stunTick;
    private boolean hasNotBeenStunned = true;

    public RagnoEntity(EntityType<? extends Raider> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 40;
        bossEvent = (ServerBossEvent) (new ServerBossEvent(this.getDisplayName(), BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.PROGRESS)).setDarkenScreen(Config.CommonConfig.bosses_darken_sky.get());
        bossEvent.setVisible(false);
        this.getAttribute(Attributes.MAX_HEALTH).setBaseValue(Config.CommonConfig.ragno_health.get());
        this.heal(Float.MAX_VALUE);
    }

    public void startSeenByPlayer(ServerPlayer p_20119_) {
        super.startSeenByPlayer(p_20119_);
        this.bossEvent.addPlayer(p_20119_);
    }

    public void stopSeenByPlayer(ServerPlayer p_20119_) {
        super.stopSeenByPlayer(p_20119_);
        this.bossEvent.removePlayer(p_20119_);
    }

    protected void customServerAiStep() {
        super.customServerAiStep();
        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new StunGoal());
        this.goalSelector.addGoal(0, new WebGoal());
        this.goalSelector.addGoal(0, new LeapGoal());
        this.goalSelector.addGoal(0, new WebNetGoal());
        this.goalSelector.addGoal(0, new BurrowGoal());
        this.goalSelector.addGoal(0, new ChargeGoal());
        this.goalSelector.addGoal(0, new CoughGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, LivingEntity.class, false, (predicate) -> this.isCrazy() && predicate.isAttackable() && predicate != this && !(predicate instanceof Creeper)));
    }

    public boolean doHurtTarget(Entity p_21372_) {
        return false;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 1).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0).add(Attributes.ARMOR, 10.0).add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
    }

    public boolean causeFallDamage(float p_147187_, float p_147188_, DamageSource p_147189_) {
        return false;
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(RAGNO_FACE, 0);
        this.entityData.define(FRAME, 0);
        this.entityData.define(SHAKE_MULTIPLIER, 0);
        this.entityData.define(DATA_FLAGS_ID, (byte) 0);
        this.entityData.define(CRAZY, false);
        this.entityData.define(BURROWING, false);
        this.entityData.define(GRABBING, false);
        this.entityData.define(STUN_HEALTH, this.getMaxStunHealth());
        this.entityData.define(STUNNED, false);
        this.entityData.define(ATTACK_TYPE, 0);
        this.entityData.define(ATTACK_TICKS, 0);
        this.entityData.define(ANTICHEESE, false);
    }

    public boolean canAttack(LivingEntity target) {
        return (!(target instanceof IllagerAttack) || ((IllagerAttack) target).getOwner() != this) && super.canAttack(target);
    }

    public float getStepHeight() {
        return 2.0F;
    }

    public boolean isCrazy() {
        return this.entityData.get(CRAZY);
    }

    public void setCrazy(boolean crazy) {
        this.entityData.set(CRAZY, crazy);
    }

    public boolean isBurrowing() {
        return this.entityData.get(BURROWING);
    }

    public void setBurrowing(boolean burrowing) {
        this.entityData.set(BURROWING, burrowing);
    }

    public boolean isGrabbing() {
        return this.entityData.get(GRABBING);
    }

    public void setGrabbing(boolean grabbing) {
        this.entityData.set(GRABBING, grabbing);
    }

    public int getRagnoFace() {
        return this.entityData.get(RAGNO_FACE);
    }

    public void setRagnoFace(int face) {
        this.entityData.set(RAGNO_FACE, face);
    }

    public int getShakeMultiplier() {
        return this.entityData.get(SHAKE_MULTIPLIER);
    }

    public void setShakeMultiplier(int shake) {
        this.entityData.set(SHAKE_MULTIPLIER, shake);
    }

    public int getFrame() {
        return this.entityData.get(FRAME);
    }

    public void setFrame(int frame) {
        this.entityData.set(FRAME, frame);
    }

    public boolean isStunned() {
        return this.entityData.get(STUNNED);
    }

    public void setStunned(boolean stunned) {
        if (stunned && this.hasNotBeenStunned) this.hasNotBeenStunned = false;
        this.entityData.set(STUNNED, stunned);
    }

    public boolean isAnticheese() {
        return this.entityData.get(ANTICHEESE);
    }

    public void setAnticheese(boolean anticheese) {
        this.entityData.set(ANTICHEESE, anticheese);
    }

    protected PathNavigation createNavigation(Level p_33802_) {
        return new WallClimberNavigation(this, p_33802_);
    }

    public boolean onClimbable() {
        return this.isClimbing();
    }

    public MobType getMobType() {
        return MobType.ARTHROPOD;
    }

    public boolean isClimbing() {
        return (this.entityData.get(DATA_FLAGS_ID) & 1) != 0;
    }

    public void setClimbing(boolean p_33820_) {
        byte b0 = this.entityData.get(DATA_FLAGS_ID);
        if (p_33820_) {
            b0 = (byte) (b0 | 1);
        } else {
            b0 &= -2;
        }

        this.entityData.set(DATA_FLAGS_ID, b0);
    }

    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("hasNotBeenStunned", this.hasNotBeenStunned);
        tag.putInt("face", this.getRagnoFace());
        tag.putInt("shake", this.getShakeMultiplier());
    }

    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.bossEvent.setName(this.getDisplayName());
        if (tag.contains("Health", 99)) {
            this.entityData.set(DATA_HEALTH_ID, Mth.clamp(tag.getFloat("Health"), 0.0F, this.getMaxHealth()));
        }
        this.hasNotBeenStunned = tag.getBoolean("hasNotBeenStunned");
        this.setRagnoFace(tag.getInt("face"));
        this.setShakeMultiplier(tag.getInt("shake"));
    }

    public void setHealth(float p_21154_) {
        float healthValue = p_21154_ - this.getHealth();
        if (healthValue > 0 || (this.isCrazy() && !this.isPlayingPhase && !this.isBurrowing() && !this.isGrabbing()) || healthValue <= -1000000000000.0F) {
            if (this.isCrazy() && !this.level().isClientSide) {
                if (this.getHealth() + healthValue > this.getMaxHealth() / 2) {
                    this.setShakeMultiplier(20);
                    this.setRagnoFace(3);
                } else {
                    this.setShakeMultiplier(40);
                    this.setRagnoFace(4);
                }
            }

            super.setHealth(p_21154_);
        }
    }

    public boolean canBeRiddenUnderFluidType(FluidType type, Entity rider) {
        return true;
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public boolean canJoinRaid() {
        return (this.isCrazy() || this.phaseTicks > 0) && super.canJoinRaid();
    }

    public boolean isPickable() {
        return !this.isBurrowing() && !this.isGrabbing() && !this.isAnticheese() && super.isPickable();
    }

    public boolean isAttackable() {
        return !this.isBurrowing() && !this.isGrabbing() && !this.isAnticheese() && super.isAttackable();
    }

    public boolean attackable() {
        return !this.isBurrowing() && !this.isGrabbing() && !this.isAnticheese() && super.attackable();
    }

    public SoundEvent getTransMusic() {
        return IllageAndSpillageSoundEvents.ENTITY_RAGNO_TRANS.get();
    }

    public SoundEvent getBossMusic() {
        return IllageAndSpillageSoundEvents.ENTITY_RAGNO_MUSIC.get();
    }

    protected boolean canPlayMusic() {
        return !this.isSilent() && this.getTarget() instanceof Player && this.getTarget() != null;
    }

    public boolean canPlayerHearMusic(Player player) {
        return player != null && this.canAttack(player) && this.distanceTo(player) < 2500.0F;
    }

    public void handleEntityEvent(byte id) {
        if (id == 67) {
            BossMusicPlayer.playBossMusic(this);
        } else if (id == 68) {
            BossMusicPlayer.stopBossMusic(this);
        } else {
            super.handleEntityEvent(id);
        }

    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return p_21197_.getEffect() != EffectRegisterer.MUTATION.get() && super.canBeAffected(p_21197_);
    }

    public boolean halfHealth() {
        return this.getHealth() <= this.getMaxHealth() / 2;
    }

    public void tick() {
        if (this.isPlayingIntro) {
            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
        }

        if (this.owner == null && this.tickCount > 5 && !this.isCrazy()) {
            List<FreakagerEntity> list = this.level().getEntitiesOfClass(FreakagerEntity.class, this.getBoundingBox().inflate(2.0));
            if (!list.isEmpty()) {
                this.owner = list.get(this.random.nextInt(list.size()));
            }

            if (this.owner == null && !this.level().isClientSide) {
                this.setCrazy(true);
                this.setStunHealth(this.getMaxStunHealth());
                this.setRagnoFace(3);
                this.setShakeMultiplier(20);
            }
        }

        if (EntityUtil.displayBossBar(this) && this.isCrazy() && !this.bossEvent.isVisible()) {
            this.bossEvent.setVisible(true);
        }

        if (this.isPlayingIntro) {
            this.getNavigation().stop();
            this.getMoveControl().strafe(0.0F, 0.0F);
            if (this.entityToStareAt != null) {
                this.getLookControl().setLookAt(this.entityToStareAt, 100.0F, 100.0F);
            }

            this.getMoveControl().strafe(0.0F, 0.0F);
            this.navigation.stop();
            this.setDeltaMovement(0, this.getDeltaMovement().y, 0);
        }

        if (this.isPlayingIntro) {
            ++this.introTicks;

            if ((this.introTicks - 1) == 11) {
                this.setShakeMultiplier(0);
                this.setAnimationState(11);
                CameraShakeEntity.cameraShake(this.level(), position(), 20, 0.2f, 0, 10);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.5F);
            }

            if ((this.introTicks - 12) == 10) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_ROAR.get(), 3.0F, 1.0F);
            }
            if ((this.introTicks - 12) >= 10 && (this.introTicks - 12) < 15) {
                this.setShakeMultiplier(this.getShakeMultiplier() + 6);
            }
            if ((this.introTicks - 12) == 13) {
                this.setRagnoFace(2);
                CameraShakeEntity.cameraShake(this.level(), position(), 50, 0.05f, 48, 20);
            }
            if ((this.introTicks - 12) == 54) {
                this.setRagnoFace(1);
                this.setShakeMultiplier(10);
            }
            if ((this.introTicks - 12) == 73) {
                this.setRagnoFace(0);
            }

            if (this.introTicks - 12 == 90) {
                this.isPlayingIntro = false;
                this.introTicks = 0;
                this.setAnimationState(0);
            }
        }

        if (this.getFrame() == 10 && !this.isPlayingIntro && !this.isPlayingPhase && !this.isBurrowing() && !this.isGrabbing()) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_WEB.get(), 0.5f, this.getVoicePitch());
            if (this.getRagnoFace() == 0) {
                this.setRagnoFace(1);
            }
        }

        if (this.getFrame() == 12 && this.getRagnoFace() == 1) {
            this.setRagnoFace(0);
        }

        if (this.getFrame() > 12 && !this.isPlayingPhase && this.isAlive() && this.random.nextInt(30) == 0) {
            this.setFrame(0);
        }

        if (!this.level().isClientSide) {
            this.setFrame(this.getFrame() + 1);
        }

        if (this.getOwner() != null) {
            if (this.getOwner().isAlive()) {
                this.setTarget(this.getOwner().getTarget());
            }

            if (this.getOwner().isDeadOrDying() && this.isAlive() && this.phaseTicks < 1) {
                if (!this.level().isClientSide) {
                    this.stopAttacking();
                    this.setStunned(false);
                    this.setInvisible(false);
                    this.setBurrowing(false);
                    this.setAnticheese(false);
                }

                this.isPlayingPhase = true;
                this.setAnimationState(2);
                this.phaseTicks = 1;
            }
        }

        if (!this.level().isClientSide && (this.phaseTicks >= 27 || this.isCrazy()) && this.getBossMusic() != null) {
            if (this.canPlayMusic()) {
                this.level().broadcastEntityEvent(this, (byte) 67);
            } else {
                this.level().broadcastEntityEvent(this, (byte) 68);
            }
        }

        if (this.getAttackType() <= 0 && !this.isPlayingIntro && !isPlayingPhase && !this.isStunned()) {
            (Objects.requireNonNull(this.getAttribute(Attributes.MOVEMENT_SPEED))).removeModifier(SPEED_PENALTY);
        } else {
            AttributeInstance speedAttribute = this.getAttribute(Attributes.MOVEMENT_SPEED);
            assert speedAttribute != null;

            speedAttribute.removeModifier(SPEED_PENALTY);
            speedAttribute.addTransientModifier(SPEED_PENALTY);
        }

        if (this.random.nextInt(200) == 0) {
            this.circleDirection = !this.circleDirection;
        }

        this.circleTick += this.circleDirection ? 1 : -1;

        if (this.stunTick > 0) {
            this.getNavigation().stop();
            this.navigation.stop();
        }

        this.stopAttackersFromAttacking();

        if (this.blockTicks > 0) --this.blockTicks;

        if (!this.level().isClientSide) {
            this.setClimbing(this.horizontalCollision);
        }

        if (this.phaseTicks > 0 && this.isAlive()) {
            ++this.phaseTicks;
        }

        if (this.phaseTicks == 20 || this.phaseTicks == 30 || this.phaseTicks == 63 || this.phaseTicks == 69) {
            this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 1.0F);
        }

        if (this.phaseTicks == 40 || this.phaseTicks == 77) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_BLOCK.get(), 2.0F, 1.0F);
        }

        if (this.phaseTicks == 116) {
            if (!this.level().isClientSide) {
                this.setCrazy(true);
                this.setRagnoFace(3);
                this.setShakeMultiplier(20);
            }

            List<EyesoreEntity> eyesores = this.level().getEntitiesOfClass(EyesoreEntity.class, this.getBoundingBox().inflate(50.0F), (predicate) -> predicate.getOwner() == this.getOwner());
            for (EyesoreEntity eyesore : eyesores) {
                eyesore.setScared(true);
            }

            CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.1F, 0, 20);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.0F);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, 1.0F);

            if (!this.level().isClientSide) {
                float radius2 = 2.0F;
                double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, new AABB(x - 2, this.getY(), z - 2, x + 2, this.getY() + 2, z + 2));

                for (LivingEntity entity : list) {
                    if (EntityUtil.canHurtThisMob(entity, this) && entity.isAlive()) {
                        double x2 = this.getX() - entity.getX();
                        double y = this.getY() - entity.getY();
                        double z2 = this.getZ() - entity.getZ();
                        double d = Math.sqrt(x2 * x2 + y * y + z2 * z2);
                        if (isMobNotInCreativeMode(entity)) {
                            entity.hurtMarked = true;
                            entity.hurt(this.damageSources().mobAttack(this), 15.0F);
                            entity.setDeltaMovement(entity.getDeltaMovement().add((-x2 / d * 5.0) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-y / d * 0.3) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-z2 / d * 5.0) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));
                            if (entity.isBlocking()) {
                                EntityUtil.disableShield(entity, 100);
                            }
                        }
                    }
                }
            }
        }

        if (this.phaseTicks == 140) {
            CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.05F, 0, 30);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.5F);

            if (!this.level().isClientSide) {
                float radius2 = 2.0F;
                double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, new AABB(x - 2, this.getY(), z - 2, x + 2, this.getY() + 2, z + 2));

                for (LivingEntity entity : list) {
                    if (EntityUtil.canHurtThisMob(entity, this) && entity.isAlive()) {
                        double x2 = this.getX() - entity.getX();
                        double y = this.getY() - entity.getY();
                        double z2 = this.getZ() - entity.getZ();
                        double d = Math.sqrt(x2 * x2 + y * y + z2 * z2);
                        if (isMobNotInCreativeMode(entity)) {
                            entity.hurtMarked = true;
                            entity.hurt(this.damageSources().mobAttack(this), 10.0F);
                            entity.setDeltaMovement(entity.getDeltaMovement().add((-x2 / d * 5.0) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-y / d * 0.3) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-z2 / d * 5.0) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));
                            if (entity.isBlocking()) {
                                EntityUtil.disableShield(entity, 100);
                            }
                        }
                    }
                }
            }
        }

        if (this.phaseTicks == 151 || this.phaseTicks == 161) {
            CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.05F, 0, 30);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.4F);

            if (!this.level().isClientSide) {
                float radius2 = 2.0F;
                double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, new AABB(x - 2, this.getY(), z - 2, x + 2, this.getY() + 2, z + 2));

                for (LivingEntity entity : list) {
                    if (EntityUtil.canHurtThisMob(entity, this) && entity.isAlive()) {
                        double x2 = this.getX() - entity.getX();
                        double y = this.getY() - entity.getY();
                        double z2 = this.getZ() - entity.getZ();
                        double d = Math.sqrt(x2 * x2 + y * y + z2 * z2);
                        if (isMobNotInCreativeMode(entity)) {
                            entity.hurtMarked = true;
                            entity.hurt(this.damageSources().mobAttack(this), 10.0F);
                            entity.setDeltaMovement(entity.getDeltaMovement().add((-x2 / d * 5.0) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-y / d * 0.3) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-z2 / d * 5.0) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));
                            if (entity.isBlocking()) {
                                EntityUtil.disableShield(entity, 100);
                            }
                        }
                    }
                }
            }
        }

        if (this.phaseTicks == 183) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 1.0F);
        }

        if (this.phaseTicks == 206) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, 1.0F);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_COUGH.get(), 2.0F, 1.0F);
        }

        if (this.phaseTicks == 223) {
            this.playSound(SoundEvents.CAMEL_EAT, 3.0F, 1.0F);
        }

        if (this.phaseTicks == 250) {
            this.isPlayingPhase = false;
            this.setStunHealth(this.getMaxStunHealth());
            this.setAttackTicks(0);
            this.setAttackType(0);
            this.setAnimationState(0);

            List<EyesoreEntity> eyesores = this.level().getEntitiesOfClass(EyesoreEntity.class, this.getBoundingBox().inflate(50.0F), (predicate) -> predicate.getOwner() == this.getOwner());
            for (EyesoreEntity eyesore : eyesores) {
                eyesore.setScared(false);
            }
        }

        if (this.getAttackType() > 0) {
            this.setAttackTicks(this.getAttackTicks() + 1);
        }

        if (this.attackCooldown > 0) {
            --this.attackCooldown;
        }

        if (this.getAttackType() < 1) {
            if (this.webCooldown > 0) --this.webCooldown;
            if (this.webNetCooldown > 0) --this.webNetCooldown;
            if (this.jumpCooldown > 0) --this.jumpCooldown;
            if (this.leapCooldown > 0) --this.leapCooldown;
            if (this.burrowCooldown > 0) --this.burrowCooldown;
            if (this.chargeCooldown > 0) --this.chargeCooldown;
            if (this.coughCooldown > 0) --this.coughCooldown;
            if (this.breathCooldown > 0) --this.breathCooldown;
        }

        if (this.isAlive()) {
            if (this.canUseBreath() || this.getAttackType() == BREATH_ATTACK) {
                this.getNavigation().stop();
                this.getMoveControl().strafe(0.0F, 0.0F);
                if (this.getTarget() != null && !this.isGrabbing()) {
                    this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
                }

                this.getMoveControl().strafe(0.0F, 0.0F);
                this.navigation.stop();

                if (this.getAttackTicks() == 0) {
                    this.setAnimationState(18);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 0.9F);
                    this.setAttackType(this.BREATH_ATTACK);
                }

                if (this.getAttackTicks() == 30) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_BLOCK.get(), 2.0F, 1.0F);

                    if (!this.level().isClientSide) {
                        float radius2 = 2.0F;
                        double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, new AABB(x - 2, this.getY(), z - 2, x + 2, this.getY() + 2, z + 2), (predicate) -> EntityUtil.canHurtThisMob(predicate, this) && isMobNotInCreativeMode(predicate));

                        for (LivingEntity entity : list) {
                            entity.hurt(this.damageSources().mobAttack(this), 2);
                            if (!this.isGrabbing() && entity.isAlive() && entity.startRiding(this, true)) {
                                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, this.getVoicePitch());
                                this.setGrabbing(true);
                            }
                        }
                    }
                }

                if (this.getAttackTicks() == 40 && this.isGrabbing()) {
                    this.setAnimationState(19);
                }

                if (this.getAttackTicks() == 53) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SCREECH.get(), 2.0F, 0.75F);
                    CameraShakeEntity.cameraShake(this.level(), position(), 50, 0.05f, 48, 20);
                }

                if (this.getAttackTicks() >= 53 && this.getAttackTicks() <= 109) {
                    this.makeBreath();
                }

                if (this.getAttackTicks() == 109 && !this.getPassengers().isEmpty()) {
                    this.getPassengers().forEach(Entity::stopRiding);
                }

                if (this.isGrabbing() ? this.getAttackTicks() > 125 : this.getAttackTicks() > 45) {
                    this.setAnimationState(0);
                    this.setAttackTicks(0);
                    this.setAttackType(0);
                    this.loseStunHealth(this.isGrabbing() ? 10 : 5, false);
                    this.setGrabbing(false);
                    this.breathCooldown = 100;
                    this.attackCooldown = 20;
                }
            }

            if (this.getAttackType() == this.WEB_ATTACK && this.isCrazy()) {
                LivingEntity entity = this.getTarget();
                if (this.getAttackTicks() == 4) {
                    this.setDeltaMovement(this.getDeltaMovement().add(0.0, 0.5, 0.0));
                }

                if (this.getAttackTicks() == 7 && entity != null) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_WEB.get(), 2.0F, 1.0F);

                    for (int i = 0; i < 8; ++i) {
                        if (!this.level().isClientSide) {
                            WebEntity projectile = ModEntityTypes.Web.get().create(this.level());
                            assert projectile != null;

                            projectile.setPos(this.getX(), this.getY() + 1.0, this.getZ());
                            projectile.setYHeadRot(this.getYHeadRot());
                            projectile.setYRot(this.getYHeadRot());

                            double x = projectile.getX() - entity.getX();
                            double y = projectile.getY() - (entity.getY() + 1.5);
                            double z = projectile.getZ() - entity.getZ();
                            double distance = Math.sqrt(x * x + y * y + z * z);
                            float power = 2.5F;

                            double motionX = -(x / distance * (double) power * 0.2);
                            double motionY = -(y / distance * (double) power * 0.2);
                            double motionZ = -(z / distance * (double) power * 0.2);

                            double randomX = (-0.5 + this.random.nextDouble()) / 8.0;
                            double randomY = (-0.5 + this.random.nextDouble()) / 8.0;
                            double randomZ = (-0.5 + this.random.nextDouble()) / 8.0;

                            projectile.setAcceleration(motionX + randomX, motionY + randomY, motionZ + randomZ);
                            projectile.setShooter(this);
                            this.level().addFreshEntity(projectile);
                        }
                    }
                }

                if (this.getAttackTicks() == 10) {
                    this.setDeltaMovement(0.0, -1.0, 0.0);
                }
            }

            if (!this.isCrazy() && ((this.doesAttackMeetNormalRequirements() && this.random.nextInt(16) == 0 && this.webCooldown < 1) || getAttackType() == this.WEB_ATTACK)) {
                if (this.getAttackTicks() == 0) {
                    this.setAnimationState(4);
                    this.setAttackType(this.WEB_ATTACK);
                }

                this.getNavigation().stop();
                this.getMoveControl().strafe(0.0F, 0.0F);
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
                }

                this.getMoveControl().strafe(0.0F, 0.0F);
                this.navigation.stop();

                if (this.getAttackTicks() == 7 && this.getTarget() != null) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_WEB.get(), 2.0F, 1.0F);
                    for (int i = 0; i < 8; ++i) {
                        if (!this.level().isClientSide) {
                            WebEntity projectile = ModEntityTypes.Web.get().create(this.level());
                            assert projectile != null;

                            projectile.setPos(this.getX(), this.getY() + 1.0, this.getZ());
                            projectile.setYHeadRot(this.getYHeadRot());
                            projectile.setYRot(this.getYHeadRot());

                            double x = projectile.getX() - this.getTarget().getX();
                            double y = projectile.getY() - (this.getTarget().getY() + 1.5);
                            double z = projectile.getZ() - this.getTarget().getZ();
                            double distance = Math.sqrt(x * x + y * y + z * z);
                            float power = 2.5F;

                            double motionX = -(x / distance * (double) power * 0.2);
                            double motionY = -(y / distance * (double) power * 0.2);
                            double motionZ = -(z / distance * (double) power * 0.2);

                            double randomX = (-0.5 + this.random.nextDouble()) / 8.0;
                            double randomY = (-0.5 + this.random.nextDouble()) / 8.0;
                            double randomZ = (-0.5 + this.random.nextDouble()) / 8.0;

                            projectile.setAcceleration(motionX + randomX, motionY + randomY, motionZ + randomZ);
                            projectile.setShooter(this);
                            this.level().addFreshEntity(projectile);
                        }
                    }
                }

                if (this.getAttackTicks() > 20) {
                    this.setAnimationState(0);
                    this.setAttackTicks(0);
                    this.setAttackType(0);
                    this.webCooldown = 200;
                }
            }

            if (this.getAttackType() == this.WEB_NET_ATTACK) {
                LivingEntity entity = this.getTarget();
                if (this.getAttackTicks() == 15 && entity != null) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_WEB.get(), 2.0F, 1.0F);
                    this.waitingForWeb = true;

                    WebNetEntity webNet = ModEntityTypes.WebNet.get().create(this.level());

                    assert webNet != null;

                    webNet.setPos(this.getX(), this.getY() + 1.5, this.getZ());
                    webNet.setYHeadRot(this.getYHeadRot());
                    webNet.setYRot(this.getYHeadRot());
                    double x = webNet.getX() - entity.getX();
                    double y = webNet.getY() - (entity.getY() + 1);
                    double z = webNet.getZ() - entity.getZ();
                    double d = Math.sqrt(x * x + y * y + z * z);
                    float power = 10.0F;
                    double motionX = -(x / d * (double) power * 0.2);
                    double motionY = -(y / d * (double) power * 0.2);
                    double motionZ = -(z / d * (double) power * 0.2);
                    webNet.setAcceleration(motionX, motionY, motionZ);

                    if (!this.level().isClientSide) {
                        float radius2 = -2.0F;
                        double x2 = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        double z2 = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        webNet.setAttachPoint(x2, this.getY() + 1, z2);
                    }

                    webNet.setShooter(this);
                    this.level().addFreshEntity(webNet);
                }

                if (this.followupTicks == 1) {
                    this.setAnimationState(17);
                }

                if (followupTicks > 0) followupTicks++;

                if (followupTicks == 7) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.5F);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, this.getVoicePitch());
                    CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.2F, 0, 30);

                    if (!this.level().isClientSide) {
                        float radius2 = 2.0F;
                        double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, new AABB(x - 5, this.getY(), z - 5, x + 5, this.getY() + 5, z + 5));

                        for (LivingEntity entity2 : list) {
                            if (EntityUtil.canHurtThisMob(entity2, this) && entity2.isAlive()) {
                                double x2 = this.getX() - entity2.getX();
                                double y = this.getY() - entity2.getY();
                                double z2 = this.getZ() - entity2.getZ();
                                double d = Math.sqrt(x2 * x2 + y * y + z2 * z2);
                                if (isMobNotInCreativeMode(entity2)) {
                                    entity2.hurtMarked = true;
                                    entity2.hurt(this.damageSources().mobAttack(this), 20.0F);
                                    entity2.setDeltaMovement(entity2.getDeltaMovement().add((-x2 / d * 5.0) - entity2.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-y / d * 2.0) - entity2.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-z2 / d * 5.0) - entity2.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));
                                    if (entity2.isBlocking()) {
                                        entity2.getUseItem().hurtAndBreak(60, entity2, (p_289501_) -> p_289501_.broadcastBreakEvent(entity2.getUsedItemHand()));
                                        EntityUtil.disableShield(entity2, 400);
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if (this.getAttackType() == this.LEAP_ATTACK) {
                LivingEntity target = this.getTarget();
                double targetX = 0.0;
                double motionY = 0.0;
                double targetZ = 0.0;
                if (target != null) {
                    double deltaX = this.getX() - target.getX();
                    double deltaY = this.getY() - (target.getY() + 1.5);
                    double deltaZ = this.getZ() - target.getZ();
                    double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                    float power = 10.0F;

                    targetX = -(deltaX / distance * (double) power * 0.2);
                    motionY = -(deltaY / distance * (double) power * 0.06);
                    targetZ = -(deltaZ / distance * (double) power * 0.2);
                }

                if (this.getAttackTicks() == 19) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                }

                if (this.getAttackTicks() == 27) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                }

                if (this.getAttackTicks() == 37) {
                    this.shouldHurtOnTouch = true;
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, this.getVoicePitch());
                    this.setDeltaMovement(targetX, motionY > 0.0 ? motionY + 0.2 : 0.2, targetZ);
                }

                if (this.shouldHurtOnTouch) {
                    for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(entity, this) && entity instanceof LivingEntity && entity.isAlive() && ((!(entity instanceof TrickOrTreatEntity) && !(entity instanceof FunnyboneEntity) && !(entity instanceof EyesoreEntity)) || entity.tickCount > 20)) {
                            double deltaX = this.getX() - entity.getX();
                            double deltaY = this.getY() - entity.getY();
                            double deltaZ = this.getZ() - entity.getZ();
                            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                            if (this.distanceToSqr(entity) < 9.0) {
                                if (entity.invulnerableTime <= 0) {
                                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                                    entity.hurt(this.damageSources().mobAttack(this), 8.0F);
                                    entity.hurtMarked = true;
                                    entity.setDeltaMovement(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 0.5, -deltaZ / distance * 2.0);
                                }

                                if (((LivingEntity) entity).isBlocking()) {
                                    EntityUtil.disableShield((LivingEntity) entity, 100);
                                }
                            }
                        }
                    }
                }
            }

            if (((!this.isCrazy() && this.getOwner() instanceof FreakagerEntity && ((FreakagerEntity) this.getOwner()).halfHealth()) || (this.isCrazy() && this.halfHealth())) && ((this.doesAttackMeetNormalRequirements() && this.getRandom().nextInt(16) == 0 && this.jumpCooldown < 1) || this.getAttackType() == JUMP_ATTACK)) {
                if (this.getAttackTicks() == 0) {
                    this.setAttackType(JUMP_ATTACK);
                    this.setAnimationState(14);
                }

                this.getNavigation().stop();
                this.getMoveControl().strafe(0.0F, 0.0F);
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
                }

                this.getMoveControl().strafe(0.0F, 0.0F);
                this.navigation.stop();

                if (this.getAttackTicks() == 7 && this.getTarget() != null) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 1.0F);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, this.getVoicePitch());

                    if (this.isCrazy()) {
                        this.setDeltaMovement((this.getTarget().getX() - this.getX()) * 0.15, 1.5, (this.getTarget().getZ() - this.getZ()) * 0.15);
                    } else {
                        if (this.distanceToSqr(this.getTarget()) <= 100) {
                            this.setDeltaMovement((-4 + (this.random.nextDouble() * 3)) * 1.1, 1.5, (-4 + (this.random.nextDouble() * 3)) * 1.1);
                        } else {
                            double deltaX = this.getX() - this.getTarget().getX();
                            double deltaY = this.getY() - this.getTarget().getY();
                            double deltaZ = this.getZ() - this.getTarget().getZ();
                            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                            float power = 18;
                            double motionX = -(deltaX / distance * power * 0.2);
                            double motionZ = -(deltaZ / distance * power * 0.2);

                            this.setDeltaMovement(motionX + ((-2 + (this.random.nextDouble() * 5)) * 1.1), 1.5, motionZ + ((-2 + (this.random.nextDouble() * 5)) * 1.1));
                        }
                    }
                }

                if (this.getAttackTicks() >= 7) {
                    for (Entity hit : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(hit, this) && hit instanceof LivingEntity && hit.isAlive() && hit != this && ((!(hit instanceof TrickOrTreatEntity) && !(hit instanceof FunnyboneEntity) && !(hit instanceof EyesoreEntity)) || hit.tickCount > 20)) {
                            double deltaX = this.getX() - hit.getX();
                            double deltaY = this.getY() - hit.getY();
                            double deltaZ = this.getZ() - hit.getZ();
                            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                            if (this.distanceToSqr(hit) < 9.0 && hit.invulnerableTime <= 0) {
                                this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                                hit.hurt(this.damageSources().mobAttack(this), 8.0F);
                                hit.hurtMarked = true;
                                hit.setDeltaMovement(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 1.2, -deltaZ / distance * 2.0);
                                hit.lerpMotion(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 1.2, -deltaZ / distance * 2.0);
                            }
                        }
                    }
                }

                if (this.getAttackTicks() > 8 && this.onGround()) {
                    for (Entity hit : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(hit, this) && hit instanceof LivingEntity && hit.isAlive() && hit != this) {
                            double deltaX = this.getX() - hit.getX();
                            double deltaY = this.getY() - hit.getY();
                            double deltaZ = this.getZ() - hit.getZ();
                            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                            if (this.distanceToSqr(hit) < 36.0 && hit.invulnerableTime <= 0) {
                                this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                                hit.hurt(this.damageSources().mobAttack(this), 8.0F);
                                hit.hurtMarked = true;
                                hit.setDeltaMovement(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 1.2, -deltaZ / distance * 2.0);
                                hit.lerpMotion(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 1.2, -deltaZ / distance * 2.0);
                            }
                        }
                    }

                    CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.05F, 0, 30);
                    EntityUtil.makeCircleParticles(this.level(), this, ParticleTypes.LARGE_SMOKE, 100, 1.0D, 1.0F);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.5F);
                    this.setAnimationState(15);
                    this.setAttackTicks(0);
                    if (this.isCrazy()) this.loseStunHealth(5, false);
                    this.attackCooldown = 10;
                    this.jumpCooldown = 80;
                    this.setAttackType(0);
                }

                if (this.getAttackTicks() > 107 && this.getAttackType() == JUMP_ATTACK) {
                    this.setAnimationState(0);
                    this.setAttackTicks(0);
                    if (this.isCrazy()) this.loseStunHealth(5, false);
                    this.attackCooldown = 10;
                    this.jumpCooldown = 80;
                    this.setAttackType(0);
                }
            }

            if (!this.isCrazy() && ((this.doesAttackMeetNormalRequirements() && this.distanceToSqr(this.getTarget()) < 49.0) || getAttackType() == ATTACK_ATTACK)) {
                if (this.getAttackTicks() == 0) {
                    this.setAttackType(ATTACK_ATTACK);
                    this.setAnimationState(12);
                }

                this.getNavigation().stop();
                this.getMoveControl().strafe(0.0F, 0.0F);
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
                }

                this.getMoveControl().strafe(0.0F, 0.0F);
                this.navigation.stop();

                if (this.getAttackTicks() == 4) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 1.0F);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 1.0F, this.getVoicePitch());

                    if (!this.level().isClientSide) {
                        float radius2 = 2.0F;
                        double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, new AABB(x - 2, this.getY(), z - 2, x + 2, this.getY() + 2, z + 2));

                        for (LivingEntity entity : list) {
                            if (EntityUtil.canHurtThisMob(entity, this) && entity.isAlive()) {
                                double x2 = this.getX() - entity.getX();
                                double y = this.getY() - entity.getY();
                                double z2 = this.getZ() - entity.getZ();
                                double d = Math.sqrt(x2 * x2 + y * y + z2 * z2);
                                if (isMobNotInCreativeMode(entity)) {
                                    entity.hurtMarked = true;
                                    entity.hurt(this.damageSources().mobAttack(this), 6.0F);
                                    entity.setDeltaMovement(entity.getDeltaMovement().add((-x2 / d * 5.0) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-y / d * 0.3) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), (-z2 / d * 5.0) - entity.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE)));
                                    if (entity.isBlocking()) {
                                        EntityUtil.disableShield(entity, 100);
                                    }
                                }
                            }
                        }
                    }
                }

                if (this.getAttackTicks() > 10) {
                    this.setAnimationState(0);
                    this.setAttackTicks(0);
                    this.attackCooldown = 25;
                    this.setAttackType(0);
                }
            }

            if (!isPlayingIntro && !isPlayingPhase && !this.isCrazy() && this.isStunned()) {
                if (this.stunTick == 1) {
                    this.setAnimationState(13);
                }

                this.getNavigation().stop();
                this.getMoveControl().strafe(0.0F, 0.0F);
                if (this.getTarget() != null && this.isCrazy()) {
                    this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
                }

                this.getMoveControl().strafe(0.0F, 0.0F);
                this.navigation.stop();

                if (stunTick > 120) {
                    if (!isPlayingPhase) this.setAnimationState(0);
                    this.setAttackTicks(0);
                    this.setAttackType(0);
                    this.setStunHealth(this.getMaxStunHealth());
                    this.stunTick = 0;
                    this.setStunned(false);
                }
            }

            if (this.getAttackType() == this.BURROW_ATTACK) {
                if (this.getAttackTicks() > 6 && this.getAttackTicks() <= 30) {
                    this.playSound(SoundEvents.GRAVEL_BREAK, 2.0F, 0.7F);
                    this.makeBlockParticles(this.getBlockStateOn());
                    this.setBurrowing(true);
                }

                if (this.getAttackTicks() >= 30 && this.getTarget() != null) {
                    this.clearFire();
                    if (this.getAttackTicks() < (this.halfHealth() ? 40 : 100)) {
                        this.playSound(SoundEvents.STONE_BREAK, 2.0F, 0.5F);
                    }

                    Entity target = this.getTarget();
                    if (this.getAttackTicks() < (this.halfHealth() ? 40 : 100)) {
                        this.setInvisible(true);
                        double targetX = target.getX();
                        double targetZ = target.getZ();
                        double d0 = Math.min(target.getY(), this.getY());
                        double d1 = Math.max(target.getY(), this.getY());
                        this.setPos(this.getBurrowPosition(targetX, targetZ, d0, d1));
                    }

                    this.setDeltaMovement(0.0, 0.0, 0.0);

                    if (this.getAttackTicks() == (this.halfHealth() ? 49 : 119)) {
                        this.setAnimationState(7);
                    }

                    if (this.getAttackTicks() == (this.halfHealth() ? 50 : 120)) {
                        this.makeBlockParticles(this.getBlockStateOn());
                        this.setInvisible(false);
                        CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.05F, 0, 30);
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.6F);
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.2F);
                        for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                            if (EntityUtil.canHurtThisMob(entity, this) && entity instanceof LivingEntity && entity.isAlive() && entity != this) {
                                double deltaX = this.getX() - entity.getX();
                                double deltaY = this.getY() - entity.getY();
                                double deltaZ = this.getZ() - entity.getZ();
                                double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                                if (this.distanceToSqr(entity) < 9.0 && entity.invulnerableTime <= 0) {
                                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                                    entity.hurt(this.damageSources().mobAttack(this), 8.0F);
                                    entity.hurtMarked = true;
                                    entity.setDeltaMovement(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 0.8, -deltaZ / distance * 2.0);
                                    entity.lerpMotion(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 0.8, -deltaZ / distance * 2.0);
                                    if (((LivingEntity) entity).isBlocking()) {
                                        EntityUtil.disableShield((LivingEntity) entity, 200);
                                    }
                                }
                            }
                        }
                        this.setDeltaMovement(0.0, 0.0, 0.0);
                    }
                }
            }

            if (this.isCrazy() && this.getAttackType() == this.CHARGE_ATTACK) {
                LivingEntity target = this.getTarget();

                if (this.getAttackTicks() == 6) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                }

                if (this.getAttackTicks() == 26 && target != null) {
                    if (this.halfHealth()) {
                        AreaEffectCloud cloud = new AreaEffectCloud(this.level(), this.getX(), this.getY(), this.getZ());
                        cloud.setRadius(3.0F);
                        cloud.setRadiusOnUse(-0.5F);
                        cloud.setWaitTime(10);
                        cloud.setRadiusPerTick(-cloud.getRadius() / (float) cloud.getDuration());
                        cloud.setPotion(PotionRegisterer.MUTATION.get());
                        cloud.setOwner(this);
                        this.level().addFreshEntity(cloud);
                    }

                    this.chargeX = 0;
                    this.chargeZ = 0;

                    double deltaX = this.getX() - target.getX();
                    double deltaY = this.getY() - target.getY();
                    double deltaZ = this.getZ() - target.getZ();
                    double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                    EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_RAGNO_CHARGE.get(), 2.0F, this.getVoicePitch(), false);

                    float power = 4.5F;
                    double motionX = -(deltaX / distance * power * 0.2);
                    double motionZ = -(deltaZ / distance * power * 0.2);

                    this.chargeX = motionX;
                    this.chargeZ = motionZ;
                }

                if (this.getAttackTicks() > 26) {
                    if (this.halfHealth() && (this.getAttackTicks() - 26) % 5 == 0) {
                        AreaEffectCloud cloud = new AreaEffectCloud(this.level(), this.getX(), this.getY(), this.getZ());
                        cloud.setRadius(3.0F);
                        cloud.setRadiusOnUse(-0.5F);
                        cloud.setWaitTime(10);
                        cloud.setRadiusPerTick(-cloud.getRadius() / (float) cloud.getDuration());
                        cloud.setPotion(PotionRegisterer.MUTATION.get());
                        cloud.setOwner(this);
                        this.level().addFreshEntity(cloud);
                    }


                    this.setDeltaMovement(this.chargeX, this.getDeltaMovement().y, this.chargeZ);

                    for (Entity hit : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(hit, this) && hit instanceof LivingEntity && hit.isAlive() && hit != this && ((!(hit instanceof TrickOrTreatEntity) && !(hit instanceof FunnyboneEntity) && !(hit instanceof EyesoreEntity)) || hit.tickCount > 20)) {
                            double deltaX = this.getX() - hit.getX();
                            double deltaY = this.getY() - hit.getY();
                            double deltaZ = this.getZ() - hit.getZ();
                            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                            if (this.distanceToSqr(hit) < 9.0 && hit.invulnerableTime <= 0) {
                                this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                                hit.hurt(this.damageSources().mobAttack(this), 8.0F);
                                hit.hurtMarked = true;
                                hit.setDeltaMovement(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 1.2, -deltaZ / distance * 2.0);
                                hit.lerpMotion(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 1.2, -deltaZ / distance * 2.0);
                                if (((LivingEntity) hit).isBlocking()) {
                                    EntityUtil.disableShield((LivingEntity) hit, 200);
                                }
                            }
                        }
                    }
                }
            }

            if (!this.isPlayingIntro && !this.isPlayingPhase && !this.isCrazy() && ((this.doesAttackMeetNormalRequirements() && this.distanceToSqr(this.getTarget()) > 1225 && this.chargeCooldown < 1) || getAttackType() == CHARGE_ATTACK)) {
                if (getAttackTicks() == 0) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 0.9F);
                    this.setAnimationState(8);
                    this.setAttackType(this.CHARGE_ATTACK);
                }

                this.getNavigation().stop();
                this.getMoveControl().strafe(0.0F, 0.0F);
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
                }

                this.getMoveControl().strafe(0.0F, 0.0F);
                this.navigation.stop();

                LivingEntity target = this.getTarget();

                if (this.getAttackTicks() == 6) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                }

                if (!this.level().isClientSide && this.getAttackTicks() == 26 && target != null) {
                    this.chargeX = 0;
                    this.chargeZ = 0;

                    double deltaX = this.getX() - target.getX();
                    double deltaY = this.getY() - target.getY();
                    double deltaZ = this.getZ() - target.getZ();
                    double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                    EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_RAGNO_CHARGE.get(), 2.0F, this.getVoicePitch(), false);

                    float power = 4.5F;
                    double motionX = -(deltaX / distance * power * 0.2);
                    double motionZ = -(deltaZ / distance * power * 0.2);

                    this.chargeX = motionX;
                    this.chargeZ = motionZ;
                }

                if (!this.level().isClientSide && this.getAttackTicks() > 26) {
                    this.setDeltaMovement(this.chargeX, this.getDeltaMovement().y, this.chargeZ);

                    for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(entity, this) && entity instanceof LivingEntity && entity.isAlive() && entity != this && ((!(entity instanceof TrickOrTreatEntity) && !(entity instanceof FunnyboneEntity) && !(entity instanceof EyesoreEntity)) || entity.tickCount > 20)) {
                            double deltaX = this.getX() - entity.getX();
                            double deltaY = this.getY() - entity.getY();
                            double deltaZ = this.getZ() - entity.getZ();
                            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                            if (this.distanceToSqr(entity) < 9.0 && entity.invulnerableTime <= 0) {
                                this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                                entity.hurt(this.damageSources().mobAttack(this), 8.0F);
                                entity.hurtMarked = true;
                                entity.setDeltaMovement(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 1.2, -deltaZ / distance * 2.0);
                                entity.lerpMotion(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 1.2, -deltaZ / distance * 2.0);
                                if (((LivingEntity) entity).isBlocking()) {
                                    EntityUtil.disableShield((LivingEntity) entity, 200);
                                }
                            }
                        }
                    }
                }

                if (this.getAttackTicks() > 96) {
                    this.setAnimationState(0);
                    this.setAttackTicks(0);
                    this.setAttackType(0);
                    this.chargeX = 0;
                    this.chargeZ = 0;
                    this.chargeCooldown = 40;
                    this.attackCooldown = 20;
                }
            }

            if (this.getAttackType() == this.COUGH_ATTACK && this.getAttackTicks() == 10 && this.getTarget() != null) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_COUGH.get(), 2.0F, 1.0F);
                CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.06F, 0, 10);
                LivingEntity target = this.getTarget();
                if (this.random.nextBoolean()) {
                    for (int i = 0; i < 4; ++i) {
                        if (!this.level().isClientSide) {
                            TrickOrTreatEntity treat = ModEntityTypes.TrickOrTreat.get().create(this.level());
                            assert treat != null;

                            treat.setPos(this.getX(), this.getY(), this.getZ());

                            double deltaX = this.getX() - target.getX();
                            double deltaY = this.getY() - target.getY();
                            double deltaZ = this.getZ() - target.getZ();
                            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                            float power = 4.5F;

                            double motionX = -(deltaX / distance * (double) power * 0.2);
                            double motionY = -(deltaY / distance * (double) power * 0.2);
                            double motionZ = -(deltaZ / distance * (double) power * 0.2);

                            treat.setDeltaMovement(motionX, motionY, motionZ);
                            treat.circleTime = i * 10;
                            treat.bounceTime = i;
                            treat.setTreat(this.random.nextInt(6) + 1);
                            if (this.getTeam() != null) {
                                this.level().getScoreboard().addPlayerToTeam(treat.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                            }

                            treat.setOwner(this);
                            treat.setGoopy();
                            this.level().addFreshEntity(treat);
                        }
                    }
                } else {
                    for (int i = 0; i < 3; ++i) {
                        if (!this.level().isClientSide) {
                            if (this.halfHealth()) {
                                FunnyboneEntity funnybone = ModEntityTypes.Funnybone.get().create(this.level());
                                assert funnybone != null;

                                funnybone.setPos(this.getX(), this.getY(), this.getZ());

                                double deltaX = this.getX() - target.getX();
                                double deltaY = this.getY() - target.getY();
                                double deltaZ = this.getZ() - target.getZ();
                                double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                                float power = 4.5F;

                                double motionX = -(deltaX / distance * (double) power * 0.2);
                                double motionY = -(deltaY / distance * (double) power * 0.2);
                                double motionZ = -(deltaZ / distance * (double) power * 0.2);

                                if (this.getTeam() != null) {
                                    this.level().getScoreboard().addPlayerToTeam(funnybone.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                                }

                                funnybone.setDeltaMovement(motionX, motionY, motionZ);
                                funnybone.setOwner(this);
                                funnybone.setTarget(this.getTarget());
                                funnybone.setGoopy(true);
                                this.level().addFreshEntity(funnybone);
                            } else {
                                PumpkinBombEntity bomb = ModEntityTypes.PumpkinBomb.get().create(this.level());
                                assert bomb != null;

                                bomb.setPos(this.getX(), this.getY(), this.getZ());

                                double deltaX = this.getX() - target.getX();
                                double deltaY = this.getY() - target.getY();
                                double deltaZ = this.getZ() - target.getZ();
                                double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                                float power = 4.5F;

                                double motionX = -(deltaX / distance * (double) power * 0.2);
                                double motionY = -(deltaY / distance * (double) power * 0.2);
                                double motionZ = -(deltaZ / distance * (double) power * 0.2);

                                if (this.getTeam() != null) {
                                    this.level().getScoreboard().addPlayerToTeam(bomb.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                                }

                                bomb.setDeltaMovement(motionX, motionY, motionZ);
                                bomb.setOwner(this);
                                bomb.setTarget(this.getTarget());
                                bomb.setGoopy();
                                this.level().addFreshEntity(bomb);
                            }
                        }
                    }
                }
            }

            if (this.isAnticheese() || this.getAttackType() == this.ANTICHEESE_ATTACK) {
                if (this.getAttackTicks() == 0) {
                    this.setAttackType(RagnoEntity.this.ANTICHEESE_ATTACK);
                }

                if (this.getAttackTicks() == 30) {
                    this.setAnimationState(6);
                }

                if (this.getAttackTicks() > 36 && this.getAttackTicks() <= 60) {
                    this.playSound(SoundEvents.GRAVEL_BREAK, 2.0F, 0.7F);
                    this.makeBlockParticles(this.getBlockStateOn());
                    this.setBurrowing(true);
                }

                if (this.getAttackTicks() >= 60 && this.getTarget() != null) {
                    this.clearFire();
                    if (this.getAttackTicks() < 70) {
                        this.playSound(SoundEvents.STONE_BREAK, 2.0F, 0.5F);
                    }

                    Entity target = this.getTarget();
                    if (this.getAttackTicks() < 70) {
                        this.setInvisible(true);
                        double targetX = target.getX();
                        double targetZ = target.getZ();
                        double d0 = Math.min(target.getY(), this.getY());
                        double d1 = Math.max(target.getY(), this.getY());
                        this.setPos(this.getBurrowPosition(targetX, targetZ, d0, d1));
                    }

                    this.setDeltaMovement(0.0, 0.0, 0.0);

                    if (this.getAttackTicks() == 79) {
                        this.setAnimationState(7);
                    }

                    if (this.getAttackTicks() == 80) {
                        this.makeBlockParticles(this.getBlockStateOn());
                        this.setInvisible(false);
                        CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.05F, 0, 30);
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.6F);
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.2F);
                        for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                            if (EntityUtil.canHurtThisMob(entity, this) && entity instanceof LivingEntity && entity.isAlive() && entity != this) {
                                double deltaX = this.getX() - entity.getX();
                                double deltaY = this.getY() - entity.getY();
                                double deltaZ = this.getZ() - entity.getZ();
                                double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                                if (this.distanceToSqr(entity) < 9.0 && entity.invulnerableTime <= 0) {
                                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                                    entity.hurt(this.damageSources().mobAttack(this), 8.0F);
                                    entity.hurtMarked = true;
                                    entity.setDeltaMovement(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 0.8, -deltaZ / distance * 2.0);
                                    entity.lerpMotion(-deltaX / distance * 2.0, -deltaY / distance * 2.0 + 0.8, -deltaZ / distance * 2.0);
                                    if (((LivingEntity) entity).isBlocking()) {
                                        EntityUtil.disableShield((LivingEntity) entity, 200);
                                    }
                                }
                            }
                        }
                        this.setDeltaMovement(0.0, 0.0, 0.0);
                    }
                }

                this.getNavigation().stop();
                this.getMoveControl().strafe(0.0F, 0.0F);
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
                }

                this.getMoveControl().strafe(0.0F, 0.0F);
                this.navigation.stop();

                if (this.getAttackTicks() > 98) {
                    this.setAnimationState(0);
                    this.setAttackTicks(0);
                    this.setAttackType(0);
                    this.setInvisible(false);
                    this.setBurrowing(false);
                    if (!this.level().isClientSide) {
                        this.setAnticheese(false);
                    }
                }
            }
        }

        if (this.getAttackType() == 0 && !this.isPlayingIntro && !this.isPlayingPhase && this.getTarget() != null && !this.isStunned()) {
            this.circleTarget(this.getTarget(), 10.0F, 0.8F, true, this.circleTick, 0.0F, 1.0F);
            this.lookAt(this.getTarget(), 100.0F, 100.0F);
            this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
        }

        if (this.getStunHealth() <= 0 && !this.isStunned()) {
            this.setStunned(true);
        }

        this.regenerateStunHealth();

        if (this.getStunHealth() <= this.getMaxStunHealth() / 3 && !this.isStunned() && !this.isBurrowing() && this.random.nextInt(4) == 0) {
            this.makeSweatParticles(1);
        }

        if (this.isStunned()) {
            this.getNavigation().stop();
            ++this.stunTick;
            if (this.stunTick == 6) {
                this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_STUN.get(), 3.0F, 1.0F);
            }

            if (this.stunTick % 5 == 0) {
                this.makeSweatParticles(2);
            }

            this.navigation.stop();
        }

        if (this.getTarget() != null && this.isAlive() && (double) this.distanceTo(this.getTarget()) < 8.0 * ((double) this.getTarget().getBbWidth() + 0.4) && this.getAttackType() == 0 && this.onGround() && !this.isStunned() && !this.isPlayingIntro && !isPlayingPhase) {
            double deltaX = this.getX() - this.getTarget().getX();
            double deltaY = this.getY() - this.getTarget().getY();
            double deltaZ = this.getZ() - this.getTarget().getZ();
            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
            this.setDeltaMovement(this.getDeltaMovement().subtract(-deltaX / distance * 0.08, 0.0, -deltaZ / distance * 0.08));
        }

        if (this.isCrazy() && this.halfHealth() && !this.isBurrowing() && this.random.nextInt(5) == 0) {
            this.makePassiveMutationParticles();
        }

        super.tick();
        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
    }

    @Override
    protected void positionRider(Entity passenger, MoveFunction moveFunction) {
        if (this.isCrazy() && (this.phaseTicks < 1 || this.phaseTicks > 250)) {
            float radius = 3.0F;
            float angle = 0.017453292F * this.yBodyRot;
            double x = this.getX() + (radius * Mth.sin((float) (Math.PI + (double) angle)));
            double z = this.getZ() + (radius * Mth.cos(angle));
            moveFunction.accept(passenger, x, this.getY() + 0.75, z);
        } else {
            super.positionRider(passenger, moveFunction);
        }
    }

    @Override
    public @NotNull Vec3 getDismountLocationForPassenger(@NotNull LivingEntity p_29487_) {
        Direction direction = this.getMotionDirection();
        if (direction.getAxis() != Direction.Axis.Y) {
            int[][] aint = DismountHelper.offsetsForDirection(direction);
            BlockPos blockpos = this.blockPosition();
            BlockPos.MutableBlockPos blockpos$mutableblockpos = new BlockPos.MutableBlockPos();

            for (Pose pose : p_29487_.getDismountPoses()) {
                AABB aabb = p_29487_.getLocalBoundsForPose(pose);

                for (int[] aint1 : aint) {
                    blockpos$mutableblockpos.set(blockpos.getX() + aint1[0], blockpos.getY(), blockpos.getZ() + aint1[1]);
                    double d0 = this.level().getBlockFloorHeight(blockpos$mutableblockpos);
                    if (DismountHelper.isBlockFloorValid(d0)) {
                        Vec3 vec3 = Vec3.upFromBottomCenterOf(blockpos$mutableblockpos, d0);
                        if (DismountHelper.canDismountTo(this.level(), p_29487_, aabb.move(vec3))) {
                            p_29487_.setPose(pose);
                            return vec3;
                        }
                    }
                }
            }

        }
        return super.getDismountLocationForPassenger(p_29487_);
    }

    @Override
    public boolean shouldRiderSit() {
        return !this.isCrazy();
    }

    private Vec3 getBurrowPosition(double p_32673_, double p_32674_, double p_32675_, double p_32676_) {
        BlockPos blockpos = BlockPos.containing(p_32673_, p_32676_, p_32674_);
        boolean flag = false;

        do {
            BlockPos blockpos1 = blockpos.below();
            BlockState blockstate = this.level().getBlockState(blockpos1);
            if (blockstate.isFaceSturdy(this.level(), blockpos1, Direction.UP)) {
                flag = true;
                break;
            }

            blockpos = blockpos.below();
        } while (blockpos.getY() >= Mth.floor(p_32675_) - 1);

        return flag ? new Vec3(p_32673_, blockpos.getY(), p_32674_) : this.position();
    }

    public int getAttackType() {
        return this.entityData.get(ATTACK_TYPE);
    }

    public void setAttackType(int attackType) {
        this.entityData.set(ATTACK_TYPE, attackType);
    }

    public int getAttackTicks() {
        return this.entityData.get(ATTACK_TICKS);
    }

    public void setAttackTicks(int attackTicks) {
        this.entityData.set(ATTACK_TICKS, attackTicks);
    }

    public void stopAttacking() {
        this.setAttackType(0);
    }

    public void push(Entity p_21294_) {
        if (this.entityData.get(ANIMATION_STATE) != 6) {
            super.push(p_21294_);
        }

    }

    protected void pushEntities() {
        if (this.entityData.get(ANIMATION_STATE) != 6) {
            super.pushEntities();
        }

    }

    public void die(DamageSource source) {
        List<TrickOrTreatEntity> treats = this.level().getEntitiesOfClass(TrickOrTreatEntity.class, this.getBoundingBox().inflate(40.0));
        if (!treats.isEmpty()) {

            for (TrickOrTreatEntity treat : treats) {
                if (treat.getOwner() == this) {
                    treat.kill();
                }
            }
        }

        this.stopAttacking();
        this.setBurrowing(false);
        this.setGrabbing(false);

        if (!this.getPassengers().isEmpty()) {
            this.getPassengers().forEach(Entity::stopRiding);
        }

        if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
            this.getCurrentRaid().ticksActive = 0L;
        }

        this.clearFire();
        if (!this.level().isClientSide) {
            this.setAttackTicks(0);
            this.setAnimationState(21);
            this.goalSelector.getRunningGoals().forEach(WrappedGoal::stop);
        }

        if (this.lastHurtByPlayerTime > 0) {
            this.lastHurtByPlayerTime = 10000;
        }

    }

    protected void tickDeath() {
        ++this.deathTime;

        if (this.getShakeMultiplier() > 0 && this.deathTime % 2 == 0)
            this.setShakeMultiplier(this.getShakeMultiplier() - 1);

        if (this.deathTime > 80) this.setShakeMultiplier(3);

        if (this.deathTime == 100) {
            this.setFrame(10);

            VillagerSoulEntity soul = ModEntityTypes.VillagerSoul.get().create(this.level());

            assert soul != null;

            soul.setPos(this.getX(), this.getY() + 1.0, this.getZ());
            soul.setDeltaMovement(0.0, 0.3, 0.0);
            soul.setTarget(this.getLastHurtByMob());
            this.level().addFreshEntity(soul);
        }

        if (this.deathTime == 200 && !this.level().isClientSide()) {
            super.die(this.damageSources().generic());
            this.level().broadcastEntityEvent(this, (byte) 60);
            this.remove(RemovalReason.KILLED);
        }

    }

    protected void dropAllDeathLoot(DamageSource source) {
        if (this.shouldDropLoot() && this.level().getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT) && this.lastHurtByPlayerTime > 0 && this.hasNotBeenStunned) {
            this.level().addFreshEntity(new ItemEntity(this.level(), this.getX(), this.getY(), this.getZ(), new ItemStack(ItemRegisterer.FREAKAGER_DISC.get())));
        }
        super.dropAllDeathLoot(source);
    }

    public boolean fireImmune() {
        return super.fireImmune() && !this.isDeadOrDying();
    }

    private void circleTarget(Entity target, float radius, float speed, boolean direction, int circleFrame, float offset, float moveSpeedMultiplier) {
        if (!this.isStunned()) {
            int directionInt = 1;
            double t = (double) (directionInt * circleFrame) * 0.5 * (double) speed / (double) radius + (double) offset;
            Vec3 movePos = target.position().add((double) radius * Math.cos(t), 0.0, (double) radius * Math.sin(t));
            this.getNavigation().moveTo(movePos.x(), movePos.y(), movePos.z(), (speed * moveSpeedMultiplier));
        }
    }

    protected void playStepSound(BlockPos p_20135_, BlockState p_20136_) {
        this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_CRAWL.get(), 0.5F, 1.0F);
    }

    public void makeBlockParticles(BlockState blockstate) {
        if (!this.level().isClientSide) {
            Iterator<ServerPlayer> var2 = ((ServerLevel) this.level()).players().iterator();

            while (true) {
                ServerPlayer serverPlayer;
                do {
                    if (!var2.hasNext()) {
                        return;
                    }

                    serverPlayer = var2.next();
                } while (!(serverPlayer.distanceToSqr(this) < 4096.0));

                ParticlePacket packet = new ParticlePacket();

                for (int i = 0; i < 12; ++i) {
                    double d0 = -0.5 + this.random.nextGaussian();
                    double d1 = -0.5 + this.random.nextGaussian();
                    double d2 = -0.5 + this.random.nextGaussian();
                    ParticleOptions block = new BlockParticleOption(ParticleTypes.BLOCK, blockstate);
                    packet.queueParticle(block, false, new Vec3(this.getRandomX(0.5), this.getY(), this.getRandomZ(0.5)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeSweatParticles(int quantity) {
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

                for (int i = 0; i < quantity; ++i) {
                    double d0 = -0.5 + this.random.nextGaussian();
                    double d1 = -0.5 + this.random.nextGaussian();
                    double d2 = -0.5 + this.random.nextGaussian();
                    packet.queueParticle(ParticleTypes.SPLASH, false, new Vec3(this.getRandomX(0.5), this.getRandomY(), this.getRandomZ(0.5)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makePassiveMutationParticles() {
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

                packet.queueParticle(ParticleRegisterer.MUTATION_DRIP_PARTICLES.get(), false, new Vec3(this.getRandomX(0.6), this.getRandomY() + (this.isAlive() ? 0.75 : 0), this.getRandomZ(0.6)), new Vec3(0, 0, 0));

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeBreath() {
        if (!this.level().isClientSide) {
            double coneAngleDegrees = 50.0;
            double coneAngleRadians = Math.toRadians(coneAngleDegrees);
            double maxDistance = 8.0;

            List<LivingEntity> entitiesInRange = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(maxDistance), (predicate) -> predicate != this && EntityUtil.canHurtThisMob(predicate, this) && isMobNotInCreativeMode(predicate));

            for (LivingEntity entity : entitiesInRange) {
                Vec3 toEntity = entity.position().subtract(this.position());
                double distance = toEntity.length();
                if (distance > maxDistance) continue;
                Vec3 toEntityNormalized = toEntity.normalize();
                double dotProduct = this.getLookAngle().dot(toEntityNormalized);
                double angle = Math.acos(dotProduct);
                if (angle <= coneAngleRadians / 2) {
                    entity.addEffect(new MobEffectInstance(EffectRegisterer.MUTATION.get(), 600));
                    entity.hurt(this.level().damageSources().source(DamageTypesRegisterer.MUTATION, entity, this), 4);
                }
            }

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

                float radius2 = 1.0F;

                for (int i = 0; i < 7; i++) {
                    double x = this.getX() + 0.800000011920929 * Math.sin(-this.getYRot() * Math.PI / 180.0)
                            + radius2 * Math.sin(-this.yHeadRot * Math.PI / 180.0) * Math.cos(-this.getXRot() * Math.PI / 180.0);
                    double z = this.getZ() + 0.800000011920929 * Math.cos(-this.getYRot() * Math.PI / 180.0)
                            + radius2 * Math.cos(-this.yHeadRot * Math.PI / 180.0) * Math.cos(-this.getXRot() * Math.PI / 180.0);

                    double y = this.getY() + 1.5;

                    double coneAngle = this.random.nextInt(40, 60);
                    double randomYawOffset = (this.random.nextDouble() - 0.5) * coneAngle;
                    double randomPitchOffset = (this.random.nextDouble() - 0.5) * coneAngle / 2.0;

                    double yaw = Math.toRadians(-this.getYRot() + randomYawOffset);
                    double pitch = Math.toRadians(-this.getXRot() + randomPitchOffset);

                    double velocityX = -Math.cos(pitch) * Math.sin(yaw);
                    double velocityY = -Math.sin(pitch);
                    double velocityZ = -Math.cos(pitch) * Math.cos(yaw);

                    double speed = this.random.nextDouble() + this.random.nextDouble();
                    if (speed < 0.4) speed += this.random.nextDouble();

                    Vec3 velocity = new Vec3(-velocityX, -velocityY, -velocityZ).scale(speed);

                    if (this.random.nextInt(10) == 0) {
                        packet.queueParticle(ParticleTypes.SMOKE, false, new Vec3(x, y, z), velocity);
                    } else {
                        packet.queueParticle(this.random.nextBoolean() ? ParticleRegisterer.MUTATION_PARTICLES.get() : ParticleRegisterer.MUTATION_PARTICLES2.get(), false, new Vec3(x, y, z), velocity);
                    }
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public Mob getOwner() {
        return this.owner;
    }

    public void setOwner(Mob owner) {
        this.owner = owner;
    }

    public void stopAttackersFromAttacking() {
        List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(100.0));
        if (this.getOwner() != null && this.getOwner().isAlive()) {
            for (Mob attacker : list) {
                if (attacker.getLastHurtByMob() == this && this.getOwner() != null) {
                    attacker.setLastHurtByMob(this.getOwner());
                }

                if (attacker.getTarget() == this && this.getOwner() != null) {
                    attacker.setTarget(this.getOwner());
                }

                LivingEntity owner = this.getOwner();
                if (attacker instanceof Warden warden) {
                    if (warden.getTarget() == this) {
                        warden.increaseAngerAt(owner, AngerLevel.ANGRY.getMinimumAnger() + 100, false);
                        warden.setAttackTarget(owner);
                    }
                } else {
                    try {
                        if (attacker.getBrain().hasMemoryValue(MemoryModuleType.ATTACK_TARGET) && attacker.getBrain().getMemory(MemoryModuleType.ATTACK_TARGET).isPresent() && attacker.getBrain().getMemory(MemoryModuleType.ATTACK_TARGET).get() == this) {
                            attacker.getBrain().setMemoryWithExpiry(MemoryModuleType.ANGRY_AT, owner.getUUID(), 600L);
                            attacker.getBrain().setMemoryWithExpiry(MemoryModuleType.ATTACK_TARGET, owner, 600L);
                        }
                    } catch (NullPointerException ignored) {
                    }
                }
            }
        }

    }

    public boolean startRiding(Entity p_20330_) {
        return false;
    }

    public boolean hurt(DamageSource damageSource, float amount) {
        if (this.getOwner() != null && damageSource.getEntity() == this.getOwner()) {
            return false;
        } else if ((this.isBurrowing() || this.isGrabbing() || this.isAnticheese()) && !damageSource.is(DamageTypes.FELL_OUT_OF_WORLD) && !damageSource.is(DamageTypes.GENERIC_KILL)) {
            return false;
        } else {
            if (this.isAlive() && !damageSource.is(DamageTypes.FELL_OUT_OF_WORLD) && !damageSource.is(DamageTypes.GENERIC_KILL) && (!this.isCrazy() || isMobNotInCreativeMode(damageSource.getEntity()))) {
                boolean source;
                if (!this.isCrazy() || this.isPlayingPhase) {
                    source = !damageSource.is(DamageTypeTags.BYPASSES_ARMOR);
                    if (!this.isStunned() && source && this.blockTicks < 1 && (this.entityData.get(ANIMATION_STATE) == 0 || this.entityData.get(ANIMATION_STATE) == 3 || this.entityData.get(ANIMATION_STATE) == 15)) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_BLOCK.get(), 2.0F, 1.0F);
                        this.setAnimationState(0);
                        this.setAnimationState(3);
                        this.blockTicks = 10;
                        this.loseStunHealth((int) amount, true);
                    }

                    if (damageSource.getEntity() instanceof LivingEntity && this.getLastHurtByMob() == null) {
                        this.setLastHurtByMob((LivingEntity) damageSource.getEntity());
                    }

                    return false;
                }

                if (this.isCrazy() && (this.stunTick < 10 || this.stunTick >= 105)) {
                    source = !damageSource.is(DamageTypeTags.BYPASSES_ARMOR);
                    if (!this.isStunned() && source && this.getAttackType() == 0) {
                        if (this.blockTicks < 1 && (this.entityData.get(ANIMATION_STATE) == 0 || this.entityData.get(ANIMATION_STATE) == 3 || this.entityData.get(ANIMATION_STATE) == 15)) {
                            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_BLOCK.get(), 2.0F, 1.0F);
                            this.setAnimationState(0);
                            this.setAnimationState(3);
                            this.blockTicks = 10;
                            this.loseStunHealth((int) amount, true);
                        }

                        if (damageSource.getEntity() instanceof LivingEntity && this.getLastHurtByMob() == null) {
                            this.setLastHurtByMob((LivingEntity) damageSource.getEntity());
                        }

                        return false;
                    }

                    amount /= 3.5F;
                }
            }

            return !damageSource.is(DamageTypes.IN_WALL) && super.hurt(damageSource, amount);
        }
    }

    public static boolean isMobNotInCreativeMode(Entity entity) {
        if (!(entity instanceof Player)) {
            return true;
        } else {
            return !((Player) entity).isCreative() && !(entity).isSpectator();
        }
    }

    public SoundEvent getCelebrateSound() {
        return this.entityData.get(ANIMATION_STATE) == 6 ? null : IllageAndSpillageSoundEvents.ENTITY_RAGNO_AMBIENT.get();
    }

    protected SoundEvent getAmbientSound() {
        return this.entityData.get(ANIMATION_STATE) == 6 ? null : IllageAndSpillageSoundEvents.ENTITY_RAGNO_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_RAGNO_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_RAGNO_DEATH.get();
    }

    public boolean canBeLeader() {
        return false;
    }

    public boolean isPersistenceRequired() {
        return !Config.CommonConfig.ULTIMATE_NIGHTMARE.get();
    }

    public double getPassengersRidingOffset() {
        if (this.getAttackType() == JUMP_ATTACK) return this.getAttackTicks() >= 7 ? 3.75 : 2.5;
        return this.stunTick > 6 && this.stunTick < 115 ? 2.3 : 2.5;
    }

    public AnimationState getAnimationState(String input) {
        if (Objects.equals(input, "intro1")) {
            return this.intro1AnimationState;
        } else if (Objects.equals(input, "intro2")) {
            return this.intro2AnimationState;
        } else if (Objects.equals(input, "phase")) {
            return this.phaseAnimationState;
        } else if (Objects.equals(input, "block")) {
            return this.blockAnimationState;
        } else if (Objects.equals(input, "web")) {
            return this.webAnimationState;
        } else if (Objects.equals(input, "webNet")) {
            return this.webNetAnimationState;
        } else if (Objects.equals(input, "pullIn")) {
            return this.pullInAnimationState;
        } else if (Objects.equals(input, "netSlam")) {
            return this.netSlamAnimationState;
        } else if (Objects.equals(input, "jump")) {
            return this.jumpAnimationState;
        } else if (Objects.equals(input, "land")) {
            return this.landAnimationState;
        } else if (Objects.equals(input, "leap")) {
            return this.leapAnimationState;
        } else if (Objects.equals(input, "burrow")) {
            return this.burrowAnimationState;
        } else if (Objects.equals(input, "popup")) {
            return this.popupAnimationState;
        } else if (Objects.equals(input, "charge")) {
            return this.chargeAnimationState;
        } else if (Objects.equals(input, "cough")) {
            return this.coughAnimationState;
        } else if (Objects.equals(input, "attack")) {
            return this.attackAnimationState;
        } else if (Objects.equals(input, "stun")) {
            return this.stunAnimationState;
        } else if (Objects.equals(input, "fall")) {
            return this.fallAnimationState;
        } else if (Objects.equals(input, "grab")) {
            return this.grabAnimationState;
        } else if (Objects.equals(input, "breath")) {
            return this.breathAnimationState;
        } else if (Objects.equals(input, "death")) {
            return this.deathAnimationState;
        } else {
            return new AnimationState();
        }
    }

    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                case 0 -> this.stopAllAnimationStates();
                case 1 -> {
                    this.stopAllAnimationStates();
                    this.intro1AnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.stopAllAnimationStates();
                    this.phaseAnimationState.start(this.tickCount);
                }
                case 3 -> {
                    this.stopAllAnimationStates();
                    this.blockAnimationState.start(this.tickCount);
                }
                case 4 -> {
                    this.stopAllAnimationStates();
                    this.webAnimationState.start(this.tickCount);
                }
                case 5 -> {
                    this.stopAllAnimationStates();
                    this.leapAnimationState.start(this.tickCount);
                }
                case 6 -> {
                    this.stopAllAnimationStates();
                    this.burrowAnimationState.start(this.tickCount);
                }
                case 7 -> {
                    this.stopAllAnimationStates();
                    this.popupAnimationState.start(this.tickCount);
                }
                case 8 -> {
                    this.stopAllAnimationStates();
                    this.chargeAnimationState.start(this.tickCount);
                }
                case 9 -> {
                    this.stopAllAnimationStates();
                    this.coughAnimationState.start(this.tickCount);
                }
                case 10 -> {
                    this.stopAllAnimationStates();
                    this.fallAnimationState.start(this.tickCount);
                }
                case 11 -> {
                    this.stopAllAnimationStates();
                    this.intro2AnimationState.start(this.tickCount);
                }
                case 12 -> {
                    this.stopAllAnimationStates();
                    this.attackAnimationState.start(this.tickCount);
                }
                case 13 -> {
                    this.stopAllAnimationStates();
                    this.stunAnimationState.start(this.tickCount);
                }
                case 14 -> {
                    this.stopAllAnimationStates();
                    this.jumpAnimationState.start(this.tickCount);
                }
                case 15 -> {
                    this.stopAllAnimationStates();
                    this.landAnimationState.start(this.tickCount);
                }
                case 16 -> {
                    this.stopAllAnimationStates();
                    this.webNetAnimationState.start(this.tickCount);
                }
                case 17 -> {
                    this.stopAllAnimationStates();
                    this.netSlamAnimationState.start(this.tickCount);
                }
                case 18 -> {
                    this.stopAllAnimationStates();
                    this.grabAnimationState.start(this.tickCount);
                }
                case 19 -> {
                    this.stopAllAnimationStates();
                    this.breathAnimationState.start(this.tickCount);
                }
                case 20 -> {
                    this.stopAllAnimationStates();
                    this.pullInAnimationState.start(this.tickCount);
                }
                case 21 -> {
                    this.stopAllAnimationStates();
                    this.deathAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    public void stopAllAnimationStates() {
        this.intro1AnimationState.stop();
        this.phaseAnimationState.stop();
        this.blockAnimationState.stop();
        this.attackAnimationState.stop();
        this.webAnimationState.stop();
        this.webNetAnimationState.stop();
        this.pullInAnimationState.stop();
        this.netSlamAnimationState.stop();
        this.jumpAnimationState.stop();
        this.landAnimationState.stop();
        this.leapAnimationState.stop();
        this.burrowAnimationState.stop();
        this.popupAnimationState.stop();
        this.chargeAnimationState.stop();
        this.coughAnimationState.stop();
        this.stunAnimationState.stop();
        this.fallAnimationState.stop();
        this.grabAnimationState.stop();
        this.breathAnimationState.stop();
        this.deathAnimationState.stop();
    }

    public void playIntro() {
        this.setAnimationState(1);
        this.introTicks = 1;
        this.isPlayingIntro = true;
    }

    public void setAnimationState(int input) {
        if (!this.isAlive() && input == 0) return;
        this.entityData.set(ANIMATION_STATE, input);
    }

    public int getStunHealth() {
        return this.entityData.get(STUN_HEALTH);
    }

    public void setStunHealth(int stunHealth) {
        this.entityData.set(STUN_HEALTH, stunHealth);
    }

    public void regenerateStunHealth() {
        if (!this.level().isClientSide && !this.isStunned() && this.getStunHealth() < this.getMaxStunHealth()) {
            int rate;

            if (this.isCrazy()) {
                rate = this.halfHealth() ? 10 : 15;
            } else {
                rate = 40;
            }

            if (this.isBurrowing()) rate *= 2;

            if (this.tickCount % rate == 0) {
                this.setStunHealth(this.getStunHealth() + 1);
            }
        }
    }

    public void loseStunHealth(int amount, boolean canStun) {
        if (!this.level().isClientSide) {
            int trueAmount = Math.min(amount, 30);
            this.setStunHealth(canStun ? this.getStunHealth() - trueAmount : this.getStunHealth() - Math.min(this.getStunHealth() - 1, trueAmount));
            this.makeSweatParticles(trueAmount);
        }
    }

    public int getMaxStunHealth() {
        if (this.isCrazy()) {
            return this.halfHealth() ? 70 : 90;
        } else {
            return 50;
        }
    }

    public boolean doesAttackMeetNormalRequirements() {
        return this.getAttackType() == 0 && this.getTarget() != null && this.hasLineOfSight(this.getTarget()) && this.attackCooldown < 1 && !this.isStunned() && !this.isPlayingIntro && !this.isPlayingPhase && !this.isAnticheese() && !this.canUseBreath();
    }

    public boolean canUseBreath() {
        return this.getAttackType() == 0 && this.getTarget() != null && this.hasLineOfSight(this.getTarget()) && this.attackCooldown < 1 && !this.isStunned() && !this.isPlayingIntro && !this.isPlayingPhase && !this.isAnticheese() && this.halfHealth() && this.breathCooldown < 1 && this.isCrazy() && this.distanceToSqr(this.getTarget()) < 36.0;
    }

    static {
        ANIMATION_STATE = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.INT);
        CRAZY = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.BOOLEAN);
        STUNNED = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.BOOLEAN);
        ATTACK_TYPE = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.INT);
        DATA_FLAGS_ID = SynchedEntityData.defineId(RagnoEntity.class, EntityDataSerializers.BYTE);
        SPEED_PENALTY = new AttributeModifier(SPEED_PENALTY_UUID, "STOP MOVING AROUND STUPID", -0.35, Operation.ADDITION);
    }

    class StunGoal extends Goal {
        public StunGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return RagnoEntity.this.isStunned() && !RagnoEntity.this.isPlayingPhase;
        }

        public void start() {
            RagnoEntity.this.setAnimationState(10);
        }

        public boolean canContinueToUse() {
            return RagnoEntity.this.stunTick <= 114 && this.canUse();
        }

        public void tick() {
            RagnoEntity.this.getNavigation().stop();
            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (RagnoEntity.this.getTarget() != null && RagnoEntity.this.isCrazy()) {
                RagnoEntity.this.getLookControl().setLookAt(RagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            RagnoEntity.this.navigation.stop();
        }

        public void stop() {
            RagnoEntity.this.setAnimationState(0);
            RagnoEntity.this.setAttackTicks(0);
            RagnoEntity.this.setAttackType(0);
            RagnoEntity.this.attackCooldown = 20;
            RagnoEntity.this.setStunHealth(RagnoEntity.this.getMaxStunHealth());
            RagnoEntity.this.stunTick = 0;
            RagnoEntity.this.setStunned(false);
        }
    }

    class WebGoal extends Goal {
        public WebGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return RagnoEntity.this.doesAttackMeetNormalRequirements() && (RagnoEntity.this.halfHealth() || RagnoEntity.this.random.nextInt(16) == 0) && RagnoEntity.this.webCooldown < 1;
        }

        public void start() {
            RagnoEntity.this.setAnimationState(4);
            RagnoEntity.this.setAttackType(RagnoEntity.this.WEB_ATTACK);
        }

        public boolean canContinueToUse() {
            return RagnoEntity.this.getAttackTicks() <= 20 && RagnoEntity.this.getAttackType() == RagnoEntity.this.WEB_ATTACK;
        }

        public void tick() {
            RagnoEntity.this.getNavigation().stop();
            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (RagnoEntity.this.getTarget() != null) {
                RagnoEntity.this.getLookControl().setLookAt(RagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            RagnoEntity.this.navigation.stop();
        }

        public void stop() {
            RagnoEntity.this.setAnimationState(0);
            RagnoEntity.this.setAttackTicks(0);
            RagnoEntity.this.setAttackType(0);
            RagnoEntity.this.loseStunHealth(5, false);
            RagnoEntity.this.webCooldown = 200;
            RagnoEntity.this.attackCooldown = 20;
        }
    }

    class WebNetGoal extends Goal {
        public WebNetGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return RagnoEntity.this.doesAttackMeetNormalRequirements() && RagnoEntity.this.isCrazy() && (RagnoEntity.this.halfHealth() || RagnoEntity.this.random.nextInt(16) == 0) && RagnoEntity.this.webNetCooldown < 1 && RagnoEntity.this.distanceToSqr(RagnoEntity.this.getTarget()) > 121;
        }

        public void start() {
            RagnoEntity.this.setAnimationState(16);
            RagnoEntity.this.setAttackType(RagnoEntity.this.WEB_NET_ATTACK);
            RagnoEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 1.25F);
        }

        public boolean canContinueToUse() {
            return (RagnoEntity.this.getAttackTicks() <= 16 || RagnoEntity.this.waitingForWeb || (RagnoEntity.this.followupTicks > 0 && followupTicks <= 20)) && RagnoEntity.this.getAttackType() == RagnoEntity.this.WEB_NET_ATTACK;
        }

        public void tick() {
            RagnoEntity.this.getNavigation().stop();
            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (RagnoEntity.this.getTarget() != null && (RagnoEntity.this.getAttackTicks() < 16 || RagnoEntity.this.getEntityData().get(ANIMATION_STATE) == 20 || RagnoEntity.this.followupTicks > 0)) {
                RagnoEntity.this.getLookControl().setLookAt(RagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            RagnoEntity.this.navigation.stop();
        }

        public void stop() {
            RagnoEntity.this.setAttackTicks(0);
            RagnoEntity.this.setAnimationState(0);
            RagnoEntity.this.setAttackType(0);
            RagnoEntity.this.webNetCooldown = 200;
            RagnoEntity.this.loseStunHealth(RagnoEntity.this.followupTicks > 0 ? 7 : 5, false);
            RagnoEntity.this.attackCooldown = 20;
            RagnoEntity.this.followupTicks = 0;
        }
    }

    class LeapGoal extends Goal {
        public LeapGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return RagnoEntity.this.doesAttackMeetNormalRequirements() && (RagnoEntity.this.halfHealth() || RagnoEntity.this.random.nextInt(16) == 0) && RagnoEntity.this.leapCooldown < 1 && RagnoEntity.this.getTarget() != null && RagnoEntity.this.distanceToSqr(RagnoEntity.this.getTarget()) < 144.0 && RagnoEntity.this.isCrazy();
        }

        public void start() {
            RagnoEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 1.0F);
            RagnoEntity.this.setAnimationState(5);
            RagnoEntity.this.setAttackType(RagnoEntity.this.LEAP_ATTACK);
        }

        public boolean canContinueToUse() {
            if (RagnoEntity.this.getAttackTicks() >= 130) return false;
            return (RagnoEntity.this.getAttackTicks() <= 47 || !RagnoEntity.this.onGround()) && RagnoEntity.this.getAttackType() == RagnoEntity.this.LEAP_ATTACK;
        }

        public void tick() {
            RagnoEntity.this.getNavigation().stop();
            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (RagnoEntity.this.getTarget() != null) {
                RagnoEntity.this.getLookControl().setLookAt(RagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            RagnoEntity.this.navigation.stop();
        }

        public void stop() {
            RagnoEntity.this.setAnimationState(0);
            RagnoEntity.this.setAttackTicks(0);
            RagnoEntity.this.setAttackType(0);
            RagnoEntity.this.loseStunHealth(7, false);
            RagnoEntity.this.shouldHurtOnTouch = false;
            RagnoEntity.this.leapCooldown = 100;
            RagnoEntity.this.attackCooldown = 20;
        }
    }

    class BurrowGoal extends Goal {
        public BurrowGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return RagnoEntity.this.doesAttackMeetNormalRequirements() && RagnoEntity.this.onGround() && (RagnoEntity.this.halfHealth() || RagnoEntity.this.random.nextInt(16) == 0) && RagnoEntity.this.burrowCooldown < 1 && RagnoEntity.this.isCrazy();
        }

        public void start() {
            RagnoEntity.this.setAnimationState(6);
            RagnoEntity.this.setAttackType(RagnoEntity.this.BURROW_ATTACK);
        }

        public boolean canContinueToUse() {
            return RagnoEntity.this.getAttackTicks() <= (RagnoEntity.this.halfHealth() ? 68 : 138);
        }

        public void tick() {
            RagnoEntity.this.getNavigation().stop();
            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (RagnoEntity.this.getTarget() != null) {
                RagnoEntity.this.getLookControl().setLookAt(RagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            RagnoEntity.this.navigation.stop();
        }

        public void stop() {
            RagnoEntity.this.setAnimationState(0);
            RagnoEntity.this.setAttackTicks(0);
            RagnoEntity.this.setAttackType(0);
            RagnoEntity.this.loseStunHealth(RagnoEntity.this.halfHealth() ? 5 : 10, false);
            RagnoEntity.this.burrowCooldown = 160;
            RagnoEntity.this.attackCooldown = 20;
            RagnoEntity.this.setInvisible(false);
            RagnoEntity.this.setBurrowing(false);
        }
    }

    class ChargeGoal extends Goal {
        public ChargeGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return RagnoEntity.this.doesAttackMeetNormalRequirements() && (RagnoEntity.this.halfHealth() || RagnoEntity.this.random.nextInt(16) == 0) && RagnoEntity.this.chargeCooldown < 1 && RagnoEntity.this.isCrazy();
        }

        public void start() {
            RagnoEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 0.9F);
            RagnoEntity.this.setAnimationState(8);
            RagnoEntity.this.setAttackType(RagnoEntity.this.CHARGE_ATTACK);
        }

        public boolean canContinueToUse() {
            return RagnoEntity.this.getAttackTicks() <= 66;
        }

        public void tick() {
            RagnoEntity.this.getNavigation().stop();
            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (RagnoEntity.this.getTarget() != null) {
                RagnoEntity.this.getLookControl().setLookAt(RagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            RagnoEntity.this.navigation.stop();
        }

        public void stop() {
            RagnoEntity.this.setAnimationState(0);
            RagnoEntity.this.setAttackTicks(0);
            RagnoEntity.this.setAttackType(0);
            RagnoEntity.this.loseStunHealth(10, false);
            RagnoEntity.this.chargeCooldown = 160;
            RagnoEntity.this.attackCooldown = 20;
        }
    }

    class CoughGoal extends Goal {
        public CoughGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return RagnoEntity.this.doesAttackMeetNormalRequirements() && (RagnoEntity.this.halfHealth() || RagnoEntity.this.random.nextInt(16) == 0) && RagnoEntity.this.coughCooldown < 1 && RagnoEntity.this.isCrazy();
        }

        public void start() {
            RagnoEntity.this.setAnimationState(9);
            RagnoEntity.this.setAttackType(RagnoEntity.this.COUGH_ATTACK);
        }

        public boolean canContinueToUse() {
            return RagnoEntity.this.halfHealth() ? RagnoEntity.this.getAttackTicks() <= 20 : RagnoEntity.this.getAttackTicks() <= 70;
        }

        public void tick() {
            RagnoEntity.this.getNavigation().stop();
            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (RagnoEntity.this.getTarget() != null) {
                RagnoEntity.this.getLookControl().setLookAt(RagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            RagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            RagnoEntity.this.navigation.stop();
        }

        public void stop() {
            RagnoEntity.this.setAnimationState(0);
            RagnoEntity.this.setAttackTicks(0);
            RagnoEntity.this.setAttackType(0);
            RagnoEntity.this.loseStunHealth(5, false);
            RagnoEntity.this.coughCooldown = 200;
            RagnoEntity.this.attackCooldown = 20;
        }
    }
}
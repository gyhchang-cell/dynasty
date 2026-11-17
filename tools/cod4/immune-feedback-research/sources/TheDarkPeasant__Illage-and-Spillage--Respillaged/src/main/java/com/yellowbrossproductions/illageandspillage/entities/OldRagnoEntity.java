package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.client.sound.BossMusicPlayer;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.projectile.PumpkinBombEntity;
import com.yellowbrossproductions.illageandspillage.entities.projectile.WebEntity;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import com.yellowbrossproductions.illageandspillage.util.ItemRegisterer;
import net.minecraft.core.BlockPos;
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
import net.minecraft.world.BossEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
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
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.warden.AngerLevel;
import net.minecraft.world.entity.monster.warden.Warden;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.fluids.FluidType;
import net.minecraftforge.network.PacketDistributor;

import java.util.*;

public class OldRagnoEntity extends Raider implements ICanBeAnimated {
    public ServerBossEvent bossEvent;
    private static final UUID SPEED_PENALTY_UUID = UUID.fromString("5CD17A52-AB9A-42D3-A629-90FDE04B281E");
    private static final AttributeModifier SPEED_PENALTY;
    private static final EntityDataAccessor<Byte> DATA_FLAGS_ID;
    private static final EntityDataAccessor<Integer> ANIMATION_STATE;
    private static final EntityDataAccessor<Boolean> CRAZY;
    private static final EntityDataAccessor<Boolean> STUNNED;
    private static final EntityDataAccessor<Integer> ATTACK_TYPE;
    public AnimationState introAnimationState = new AnimationState();
    public AnimationState phaseAnimationState = new AnimationState();
    public AnimationState blockAnimationState = new AnimationState();
    public AnimationState webAnimationState = new AnimationState();
    public AnimationState leapAnimationState = new AnimationState();
    public AnimationState burrowAnimationState = new AnimationState();
    public AnimationState popupAnimationState = new AnimationState();
    public AnimationState chargeAnimationState = new AnimationState();
    public AnimationState coughAnimationState = new AnimationState();
    public AnimationState stunAnimationState = new AnimationState();
    public int attackType;
    private int attackTicks;
    private int attackCooldown;
    private final int WEB_ATTACK = 1;
    private final int LEAP_ATTACK = 2;
    private final int BURROW_ATTACK = 3;
    private final int CHARGE_ATTACK = 4;
    private final int COUGH_ATTACK = 5;
    private int webCooldown;
    private int leapCooldown;
    private int burrowCooldown;
    private int chargeCooldown;
    private int coughCooldown;
    int introTicks;
    int phaseTicks;
    private Mob owner;
    public ItemEntity item = null;
    int blockTicks;
    boolean shouldHurtOnTouch;
    public boolean isPlayingIntro;
    public double chargeX;
    public double chargeZ;
    public boolean circleDirection;
    public int circleTick;
    public int attacksUsed;
    public int stunTick;
    private boolean isBurrowing = false;
    private DamageSource lastDamageSource;
    private boolean shouldDropDisc;

    public OldRagnoEntity(EntityType<? extends Raider> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 40;
        bossEvent = (ServerBossEvent) (new ServerBossEvent(this.getDisplayName(), BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.PROGRESS)).setDarkenScreen(Config.CommonConfig.bosses_darken_sky.get());
        bossEvent.setVisible(false);
    }

    @Override
    public void startSeenByPlayer(ServerPlayer p_20119_) {
        super.startSeenByPlayer(p_20119_);
        this.bossEvent.addPlayer(p_20119_);
    }

    @Override
    public void stopSeenByPlayer(ServerPlayer p_20119_) {
        super.stopSeenByPlayer(p_20119_);
        this.bossEvent.removePlayer(p_20119_);
    }

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new StunGoal());
        this.goalSelector.addGoal(0, new WebGoal());
        this.goalSelector.addGoal(0, new LeapGoal());
        this.goalSelector.addGoal(0, new BurrowGoal());
        this.goalSelector.addGoal(0, new ChargeGoal());
        this.goalSelector.addGoal(0, new CoughGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(0, new AlwaysWatchTargetGoal());
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    public boolean doHurtTarget(Entity p_21372_) {
        return false;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 160.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0).add(Attributes.KNOCKBACK_RESISTANCE, 1.0);
    }

    public boolean causeFallDamage(float p_147187_, float p_147188_, DamageSource p_147189_) {
        return false;
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(DATA_FLAGS_ID, (byte) 0);
        this.entityData.define(CRAZY, false);
        this.entityData.define(STUNNED, false);
        this.entityData.define(ATTACK_TYPE, 0);
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

    public boolean isStunned() {
        return this.entityData.get(STUNNED);
    }

    public void setStunned(boolean stunned) {
        this.entityData.set(STUNNED, stunned);
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

    public void addAdditionalSaveData(CompoundTag p_37870_) {
        super.addAdditionalSaveData(p_37870_);
    }

    public void readAdditionalSaveData(CompoundTag p_37862_) {
        super.readAdditionalSaveData(p_37862_);
        this.bossEvent.setName(this.getDisplayName());
    }

    public boolean canBeRiddenUnderFluidType(FluidType type, Entity rider) {
        return true;
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public boolean canJoinRaid() {
        return (this.isCrazy() || this.phaseTicks > 0) && super.canJoinRaid();
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

    public void tick() {
        if (this.isPlayingIntro) {
            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
        }

        if (this.owner == null && this.tickCount > 5) {
            List<FreakagerEntity> list = this.level().getEntitiesOfClass(FreakagerEntity.class, this.getBoundingBox().inflate(2.0));
            if (!list.isEmpty()) {
                this.owner = list.get(this.random.nextInt(list.size()));
            }

            if (this.owner == null && !this.level().isClientSide) {
                this.setCrazy(true);
            }
        }

        if (EntityUtil.displayBossBar(this) && this.isCrazy() && !bossEvent.isVisible()) {
            bossEvent.setVisible(true);
        }

        if (this.getOwner() != null) {
            if (this.getOwner().isAlive()) {
                this.setTarget(this.getOwner().getTarget());
            }

            if (this.getOwner().isDeadOrDying() && this.phaseTicks < 1) {
                if (!this.level().isClientSide) {
                    this.stopAttacking();
                }

                this.isPlayingIntro = true;
                this.setAnimationState(2);
                this.phaseTicks = 1;
            }
        }

        if (!this.level().isClientSide && this.isCrazy() && this.getBossMusic() != null) {
            if (this.canPlayMusic()) {
                this.level().broadcastEntityEvent(this, (byte) 67);
            } else {
                this.level().broadcastEntityEvent(this, (byte) 68);
            }
        }

        if (this.getAttackType() <= 0 && !this.isPlayingIntro && !this.isStunned()) {
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
        if (this.introTicks > 0) ++this.introTicks;

        if (introTicks <= 80) {
            this.getNavigation().stop();
            this.getMoveControl().strafe(0.0F, 0.0F);
            if (this.getTarget() != null) {
                this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
            }

            this.getMoveControl().strafe(0.0F, 0.0F);
            this.navigation.stop();
            this.setDeltaMovement(0, this.getDeltaMovement().y, 0);
        }

        if (this.introTicks == 21) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_ROAR.get(), 3.0F, 1.0F);
        }

        if (this.introTicks == 24) {
            CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.05F, 48, 20);
        }

        if (this.introTicks == 70) {
            this.isPlayingIntro = false;
            this.setAnimationState(0);
        }

        if (!this.level().isClientSide) {
            this.setClimbing(this.horizontalCollision);
        }

        if (this.phaseTicks > 0) {
            ++this.phaseTicks;
        }

        if (this.phaseTicks == 19) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, 1.0F);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_EAT.get(), 2.0F, 1.0F);
        }

        if (this.phaseTicks == 20 && this.item != null) {
            this.makeSpitParticles(this.item);
            this.item.discard();
        }

        if (this.phaseTicks == 27) {
            if (!this.level().isClientSide) {
                this.setCrazy(true);
            }

            CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.1F, 0, 20);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.0F);
        }

        if (this.phaseTicks == 43) {
            CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.05F, 0, 30);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.5F);
        }

        if (this.phaseTicks == 60) {
            CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.05F, 0, 30);
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SLAM.get(), 2.0F, 1.4F);
        }

        if (this.phaseTicks == 50) {
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 0.7F);
        }

        if (this.phaseTicks == 80) {
            this.isPlayingIntro = false;
            this.attackTicks = 0;
            this.setAttackType(0);
            this.setAnimationState(0);
        }

        if (this.getAttackType() > 0) {
            ++this.attackTicks;
        }

        if (this.attackCooldown > 0) {
            --this.attackCooldown;
        }

        if (this.getAttackType() < 1) {
            if (this.webCooldown > 0) --this.webCooldown;
            if (this.leapCooldown > 0) --this.leapCooldown;
            if (this.burrowCooldown > 0) --this.burrowCooldown;
            if (this.chargeCooldown > 0) --this.chargeCooldown;
            if (this.coughCooldown > 0) --this.coughCooldown;
        }

        if (this.isAlive()) {
            if (this.getAttackType() == this.WEB_ATTACK && this.isCrazy()) {
                LivingEntity entity = this.getTarget();
                if (this.attackTicks == 4) {
                    this.setDeltaMovement(this.getDeltaMovement().add(0.0, 0.5, 0.0));
                }

                if (this.attackTicks == 6 && entity != null) {
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

                if (this.attackTicks == 10) {
                    this.setDeltaMovement(0.0, -1.0, 0.0);
                }
            }

            if (introTicks > 80 && !this.isCrazy() && ((this.doesAttackMeetNormalRequirements() && this.random.nextInt(16) == 0 && this.webCooldown < 1) || getAttackType() == this.WEB_ATTACK)) {
                if (attackTicks == 0) {
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

                if (attackTicks == 6 && this.getTarget() != null) {
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

                if (attackTicks > 17) {
                    if (!this.isPlayingIntro) {
                        this.setAnimationState(0);
                    }

                    this.attackTicks = 0;
                    this.setAttackType(0);
                    this.webCooldown = 200;
                    this.attackCooldown = 20;
                }
            }

            if (this.getAttackType() == this.LEAP_ATTACK && this.isCrazy()) {
                LivingEntity target = this.getTarget();
                double targetX = 0.0;
                double motionY = 0.0;
                double targetZ = 0.0;
                if (target != null) {
                    double deltaX = this.getX() - target.getX();
                    double deltaY = this.getY() - (target.getY() + 1.5);
                    double deltaZ = this.getZ() - target.getZ();
                    double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                    float power = 6.5F;

                    targetX = -(deltaX / distance * (double) power * 0.2);
                    motionY = -(deltaY / distance * (double) power * 0.02);
                    targetZ = -(deltaZ / distance * (double) power * 0.2);
                }

                if (this.attackTicks == 6) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                }

                if (this.attackTicks == 17) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                }

                if (this.attackTicks == 30) {
                    this.shouldHurtOnTouch = true;
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, this.getVoicePitch());
                    this.setDeltaMovement(targetX, motionY > 0.0 ? motionY + 0.2 : 0.2, targetZ);
                }

                if (this.shouldHurtOnTouch) {
                    for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(entity, this) && entity instanceof LivingEntity && entity.isAlive()) {
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

            if (introTicks > 80 && !this.isCrazy() && ((this.doesAttackMeetNormalRequirements() && this.random.nextInt(16) == 0 && this.leapCooldown < 1 && this.getTarget() != null && (double) this.distanceTo(this.getTarget()) < 12.0) || getAttackType() == this.LEAP_ATTACK)) {
                if (attackTicks == 0) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 1.0F);
                    this.setAnimationState(5);
                    this.setAttackType(this.LEAP_ATTACK);
                }

                this.getNavigation().stop();
                this.getMoveControl().strafe(0.0F, 0.0F);
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
                }

                this.getMoveControl().strafe(0.0F, 0.0F);
                this.navigation.stop();

                LivingEntity target = this.getTarget();
                double targetX = 0.0;
                double motionY = 0.0;
                double targetZ = 0.0;
                if (target != null) {
                    double deltaX = this.getX() - target.getX();
                    double deltaY = this.getY() - (target.getY() + 1.5);
                    double deltaZ = this.getZ() - target.getZ();
                    double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
                    float power = 6.5F;

                    targetX = -(deltaX / distance * (double) power * 0.2);
                    motionY = -(deltaY / distance * (double) power * 0.02);
                    targetZ = -(deltaZ / distance * (double) power * 0.2);
                }

                if (this.attackTicks == 6) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                }

                if (this.attackTicks == 17) {
                    this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                }

                if (this.attackTicks == 30) {
                    this.shouldHurtOnTouch = true;
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_LEAP.get(), 2.0F, this.getVoicePitch());
                    this.setDeltaMovement(targetX, motionY > 0.0 ? motionY + 0.2 : 0.2, targetZ);
                }

                if (this.shouldHurtOnTouch) {
                    for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(entity, this) && entity instanceof LivingEntity && entity.isAlive()) {
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

                if (this.attackTicks >= 130) {
                    if (!this.isPlayingIntro) {
                        this.setAnimationState(0);
                    }

                    this.attackTicks = 0;
                    this.setAttackType(0);
                    this.shouldHurtOnTouch = false;
                    this.leapCooldown = 100;
                    this.attackCooldown = 20;
                }

                if (((this.attackTicks > 40 && this.onGround()) || this.getAttackType() != this.LEAP_ATTACK) && shouldHurtOnTouch) {
                    if (!this.isPlayingIntro) {
                        this.setAnimationState(0);
                    }

                    this.attackTicks = 0;
                    this.setAttackType(0);
                    this.shouldHurtOnTouch = false;
                    this.leapCooldown = 100;
                    this.attackCooldown = 20;
                }
            }

            if (this.getAttackType() == this.BURROW_ATTACK) {
                if (this.attackTicks > 6 && this.attackTicks <= 30) {
                    this.playSound(SoundEvents.GRAVEL_BREAK, 2.0F, 0.7F);
                    this.makeBlockParticles(this.getBlockStateOn());
                    this.isBurrowing = true;
                }

                if (this.attackTicks >= 30 && this.getTarget() != null) {
                    this.clearFire();
                    if (this.attackTicks < 100) {
                        this.playSound(SoundEvents.STONE_BREAK, 2.0F, 0.5F);
                    }

                    Entity target = this.getTarget();
                    double posX = this.getX();
                    double posY = this.getY();
                    double posZ = this.getZ();
                    if (this.attackTicks < 100) {
                        this.setInvisible(true);
                        posX = target.getX();
                        posY = target.getY();
                        posZ = target.getZ();
                    }

                    this.setPos(posX, posY, posZ);
                    this.setDeltaMovement(0.0, 0.0, 0.0);
                    if (this.attackTicks == 120) {
                        this.makeBlockParticles(this.getBlockStateOn());
                        this.setAnimationState(7);
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
                                }
                            }
                        }
                        this.setDeltaMovement(0.0, 0.0, 0.0);
                    }
                }
            }

            if (this.isCrazy() && this.getAttackType() == this.CHARGE_ATTACK) {
                LivingEntity target = this.getTarget();
                if (this.attackTicks == 30 && target != null) {
                    double deltaX = this.getX() - target.getX();
                    double deltaY = this.getY() - target.getY();
                    double deltaZ = this.getZ() - target.getZ();
                    double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_CHARGE.get(), 2.0F, this.getVoicePitch());

                    float power = 4.5F;
                    double motionX = -(deltaX / distance * power * 0.2);
                    double motionZ = -(deltaZ / distance * power * 0.2);

                    this.chargeX = motionX;
                    this.chargeZ = motionZ;
                }

                if (this.attackTicks > 30) {
                    this.setDeltaMovement(this.chargeX, this.getDeltaMovement().y, this.chargeZ);

                    for (Entity hit : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(hit, this) && hit instanceof LivingEntity && hit.isAlive() && hit != this) {
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
            }

            if (introTicks > 80 && !this.isCrazy() && ((this.doesAttackMeetNormalRequirements() && this.distanceToSqr(this.getTarget()) > 1225 && this.chargeCooldown < 1) || getAttackType() == CHARGE_ATTACK)) {
                if (attackTicks == 0) {
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
                if (this.attackTicks == 30 && target != null) {
                    double deltaX = this.getX() - target.getX();
                    double deltaY = this.getY() - target.getY();
                    double deltaZ = this.getZ() - target.getZ();
                    double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);

                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_CHARGE.get(), 2.0F, this.getVoicePitch());

                    float power = 4.5F;
                    double motionX = -(deltaX / distance * power * 0.2);
                    double motionZ = -(deltaZ / distance * power * 0.2);

                    this.chargeX = motionX;
                    this.chargeZ = motionZ;
                }

                if (this.attackTicks > 30) {
                    this.setDeltaMovement(this.chargeX, this.getDeltaMovement().y, this.chargeZ);

                    for (Entity hit : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (EntityUtil.canHurtThisMob(hit, this) && hit instanceof LivingEntity && hit.isAlive() && hit != this) {
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

                if (attackTicks > 100 || !this.getPassengers().get(0).isAlive()) {
                    this.setAnimationState(0);
                    this.attackTicks = 0;
                    this.setAttackType(0);
                    this.chargeCooldown = 40;
                    this.attackCooldown = 20;
                }
            }

            if (this.getAttackType() == this.COUGH_ATTACK && this.attackTicks == 10 && this.getTarget() != null) {
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
                            treat.setTreat(this.random.nextInt(5) + 1);
                            if (this.getTeam() != null) {
                                this.level().getScoreboard().addPlayerToTeam(treat.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                            }

                            Objects.requireNonNull(treat.getAttribute(Attributes.MAX_HEALTH)).setBaseValue(12.0);
                            treat.heal(50);
                            treat.setOwner(this);
                            treat.setGoopy();
                            treat.setOld(true);
                            this.level().addFreshEntity(treat);
                        }
                    }
                } else {
                    for (int i = 0; i < 3; ++i) {
                        if (!this.level().isClientSide) {
                            PumpkinBombEntity treat = ModEntityTypes.PumpkinBomb.get().create(this.level());
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

                            if (this.getTeam() != null) {
                                this.level().getScoreboard().addPlayerToTeam(treat.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                            }

                            treat.setDeltaMovement(motionX, motionY, motionZ);
                            treat.setOwner(this);
                            treat.setTarget(this.getTarget());
                            treat.setGoopy();
                            this.level().addFreshEntity(treat);
                        }
                    }
                }
            }
        }

        if (this.attackType == 0 && !this.isPlayingIntro && this.getTarget() != null && !this.isStunned()) {
            this.circleTarget(this.getTarget(), 10.0F, 0.8F, true, this.circleTick, 0.0F, 1.0F);
            this.lookAt(this.getTarget(), 100.0F, 100.0F);
            this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
        }

        if (this.attacksUsed >= 4 && !this.isStunned()) {
            this.setStunned(true);
        }

        if (this.isStunned()) {
            this.getNavigation().stop();
            ++this.stunTick;
            if (this.stunTick == 6) {
                this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 0.9F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_STUN.get(), 3.0F, 1.0F);
            }

            if (this.stunTick % 5 == 0) {
                this.makeSweatParticles();
            }

            this.navigation.stop();
        }

        if (this.getTarget() != null && this.isAlive() && (double) this.distanceTo(this.getTarget()) < 8.0 * ((double) this.getTarget().getBbWidth() + 0.4) && this.getAttackType() == 0 && this.onGround() && !this.isStunned() && !this.isPlayingIntro) {
            double deltaX = this.getX() - this.getTarget().getX();
            double deltaY = this.getY() - this.getTarget().getY();
            double deltaZ = this.getZ() - this.getTarget().getZ();
            double distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY + deltaZ * deltaZ);
            this.setDeltaMovement(this.getDeltaMovement().subtract(-deltaX / distance * 0.08, 0.0, -deltaZ / distance * 0.08));
        }

        super.tick();
        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
    }

    public int getAttackType() {
        return this.entityData.get(ATTACK_TYPE);
    }

    public void setAttackType(int attackType) {
        this.entityData.set(ATTACK_TYPE, attackType);
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

        if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
            this.getCurrentRaid().ticksActive = 0L;
        }

        if (!this.isStunned()) {
            shouldDropDisc = true;
        }

        this.clearFire();
        if (!this.level().isClientSide) {
            this.attackTicks = 0;
            this.goalSelector.getRunningGoals().forEach(WrappedGoal::stop);
        }

        if (this.lastHurtByPlayerTime > 0) {
            this.lastHurtByPlayerTime = 10000;
        }

    }

    protected void tickDeath() {
        ++this.deathTime;
        if (this.deathTime == 100) {
            VillagerSoulEntity soul = ModEntityTypes.VillagerSoul.get().create(this.level());

            assert soul != null;

            soul.setPos(this.getX(), this.getY() + 1.0, this.getZ());
            soul.setDeltaMovement(0.0, 0.3, 0.0);
            soul.setTarget(this.getLastHurtByMob());
            this.level().addFreshEntity(soul);
        }

        if (this.deathTime == 200 && !this.level().isClientSide()) {
            super.die(lastDamageSource != null ? lastDamageSource : this.damageSources().generic());
            this.level().broadcastEntityEvent(this, (byte) 60);
            this.remove(RemovalReason.KILLED);
        }

    }

    protected void dropAllDeathLoot(DamageSource source) {
        if (this.shouldDropLoot() && this.level().getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT) && source.getEntity() instanceof Player && shouldDropDisc) {
            this.level().addFreshEntity(new ItemEntity(this.level(), this.getX(), this.getY(), this.getZ(), new ItemStack(ItemRegisterer.FREAKAGER_DISC.get())));
        }
        super.dropAllDeathLoot(source);
    }

    public boolean fireImmune() {
        return super.fireImmune() && !this.isDeadOrDying();
    }

    public void makeSpitParticles(Entity caught) {
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
                    packet.queueParticle(ParticleTypes.SPLASH, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
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

    public void makeSweatParticles() {
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

                for (int i = 0; i < 2; ++i) {
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
        } else if (this.isBurrowing) {
            return false;
        } else {
            if (this.isAlive() && !damageSource.is(DamageTypes.FELL_OUT_OF_WORLD) && !damageSource.is(DamageTypes.GENERIC_KILL) && isMobNotInCreativeMode(damageSource.getEntity())) {
                boolean source;
                if (!this.isCrazy()) {
                    source = !damageSource.is(DamageTypeTags.BYPASSES_ARMOR);
                    if (source && this.blockTicks < 1 && (this.entityData.get(ANIMATION_STATE) == 0 || this.entityData.get(ANIMATION_STATE) == 3)) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_BLOCK.get(), 2.0F, 1.0F);
                        this.setAnimationState(0);
                        this.setAnimationState(3);
                        this.blockTicks = 10;
                    }

                    if (damageSource.getEntity() instanceof LivingEntity && this.getLastHurtByMob() == null) {
                        this.setLastHurtByMob((LivingEntity) damageSource.getEntity());
                    }

                    return false;
                }

                if (!this.isStunned()) {
                    source = !damageSource.is(DamageTypeTags.BYPASSES_ARMOR);
                    if (source && this.getAttackType() == 0) {
                        if (this.blockTicks < 1 && (this.entityData.get(ANIMATION_STATE) == 0 || this.entityData.get(ANIMATION_STATE) == 3)) {
                            this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_BLOCK.get(), 2.0F, 1.0F);
                            this.setAnimationState(0);
                            this.setAnimationState(3);
                            this.blockTicks = 10;
                        }

                        if (damageSource.getEntity() instanceof LivingEntity && this.getLastHurtByMob() == null) {
                            this.setLastHurtByMob((LivingEntity) damageSource.getEntity());
                        }

                        return false;
                    }

                    amount /= 3.5F;
                }
            }

            this.lastDamageSource = damageSource;

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
        return true;
    }

    public double getPassengersRidingOffset() {
        return 2.5;
    }

    public AnimationState getAnimationState(String input) {
        if (Objects.equals(input, "intro")) {
            return this.introAnimationState;
        } else if (Objects.equals(input, "phase")) {
            return this.phaseAnimationState;
        } else if (Objects.equals(input, "block")) {
            return this.blockAnimationState;
        } else if (Objects.equals(input, "web")) {
            return this.webAnimationState;
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
        } else {
            return Objects.equals(input, "stun") ? this.stunAnimationState : new AnimationState();
        }
    }

    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                case 0 -> this.stopAllAnimationStates();
                case 1 -> {
                    this.stopAllAnimationStates();
                    this.introAnimationState.start(this.tickCount);
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
                    this.stunAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    public void stopAllAnimationStates() {
        this.phaseAnimationState.stop();
        this.blockAnimationState.stop();
        this.webAnimationState.stop();
        this.leapAnimationState.stop();
        this.burrowAnimationState.stop();
        this.popupAnimationState.stop();
        this.chargeAnimationState.stop();
        this.coughAnimationState.stop();
        this.stunAnimationState.stop();
    }

    public void playIntro() {
        this.setAnimationState(1);
        this.introTicks = 1;
        this.isPlayingIntro = true;
    }

    public void setAnimationState(int input) {
        this.entityData.set(ANIMATION_STATE, input);
    }

    public boolean doesAttackMeetNormalRequirements() {
        return this.getAttackType() == 0 && this.getTarget() != null && this.hasLineOfSight(this.getTarget()) && this.attackCooldown < 1 && !this.isStunned() && !this.isPlayingIntro;
    }

    static {
        ANIMATION_STATE = SynchedEntityData.defineId(OldRagnoEntity.class, EntityDataSerializers.INT);
        CRAZY = SynchedEntityData.defineId(OldRagnoEntity.class, EntityDataSerializers.BOOLEAN);
        STUNNED = SynchedEntityData.defineId(OldRagnoEntity.class, EntityDataSerializers.BOOLEAN);
        ATTACK_TYPE = SynchedEntityData.defineId(OldRagnoEntity.class, EntityDataSerializers.INT);
        DATA_FLAGS_ID = SynchedEntityData.defineId(OldRagnoEntity.class, EntityDataSerializers.BYTE);
        SPEED_PENALTY = new AttributeModifier(SPEED_PENALTY_UUID, "STOP MOVING AROUND STUPID", -0.35, Operation.ADDITION);
    }

    class StunGoal extends Goal {
        public StunGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldRagnoEntity.this.isStunned();
        }

        public void start() {
            OldRagnoEntity.this.setAnimationState(10);
        }

        public boolean canContinueToUse() {
            return OldRagnoEntity.this.stunTick <= 100;
        }

        public void tick() {
            OldRagnoEntity.this.getNavigation().stop();
            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (OldRagnoEntity.this.getTarget() != null) {
                OldRagnoEntity.this.getLookControl().setLookAt(OldRagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            OldRagnoEntity.this.navigation.stop();
        }

        public void stop() {
            OldRagnoEntity.this.setAnimationState(0);
            OldRagnoEntity.this.attackTicks = 0;
            OldRagnoEntity.this.setAttackType(0);
            OldRagnoEntity.this.attackCooldown = 40;
            OldRagnoEntity.this.attacksUsed = 0;
            OldRagnoEntity.this.stunTick = 0;
            OldRagnoEntity.this.setStunned(false);
        }
    }

    class WebGoal extends Goal {
        public WebGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldRagnoEntity.this.doesAttackMeetNormalRequirements() && OldRagnoEntity.this.random.nextInt(16) == 0 && OldRagnoEntity.this.webCooldown < 1;
        }

        public void start() {
            OldRagnoEntity.this.setAnimationState(4);
            OldRagnoEntity.this.setAttackType(OldRagnoEntity.this.WEB_ATTACK);
        }

        public boolean canContinueToUse() {
            return OldRagnoEntity.this.attackTicks <= 17 && OldRagnoEntity.this.getAttackType() == OldRagnoEntity.this.WEB_ATTACK;
        }

        public void tick() {
            OldRagnoEntity.this.getNavigation().stop();
            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (OldRagnoEntity.this.getTarget() != null) {
                OldRagnoEntity.this.getLookControl().setLookAt(OldRagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            OldRagnoEntity.this.navigation.stop();
        }

        public void stop() {
            if (!OldRagnoEntity.this.isPlayingIntro) {
                OldRagnoEntity.this.setAnimationState(0);
            }

            OldRagnoEntity.this.attackTicks = 0;
            OldRagnoEntity.this.setAttackType(0);
            OldRagnoEntity.this.webCooldown = 200;
            OldRagnoEntity.this.attackCooldown = 20;
            if (OldRagnoEntity.this.isCrazy()) {
                ++OldRagnoEntity.this.attacksUsed;
            }

        }
    }

    class LeapGoal extends Goal {
        public LeapGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldRagnoEntity.this.doesAttackMeetNormalRequirements() && OldRagnoEntity.this.random.nextInt(16) == 0 && OldRagnoEntity.this.leapCooldown < 1 && OldRagnoEntity.this.getTarget() != null && (double) OldRagnoEntity.this.distanceTo(OldRagnoEntity.this.getTarget()) < 12.0;
        }

        public void start() {
            OldRagnoEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 1.0F);
            OldRagnoEntity.this.setAnimationState(5);
            OldRagnoEntity.this.setAttackType(OldRagnoEntity.this.LEAP_ATTACK);
        }

        public boolean canContinueToUse() {
            if (attackTicks >= 130) return false;
            return (OldRagnoEntity.this.attackTicks <= 40 || !OldRagnoEntity.this.onGround()) && OldRagnoEntity.this.getAttackType() == OldRagnoEntity.this.LEAP_ATTACK;
        }

        public void tick() {
            OldRagnoEntity.this.getNavigation().stop();
            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (OldRagnoEntity.this.getTarget() != null) {
                OldRagnoEntity.this.getLookControl().setLookAt(OldRagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            OldRagnoEntity.this.navigation.stop();
        }

        public void stop() {
            if (!OldRagnoEntity.this.isPlayingIntro) {
                OldRagnoEntity.this.setAnimationState(0);
            }

            OldRagnoEntity.this.attackTicks = 0;
            OldRagnoEntity.this.setAttackType(0);
            OldRagnoEntity.this.shouldHurtOnTouch = false;
            OldRagnoEntity.this.leapCooldown = 100;
            OldRagnoEntity.this.attackCooldown = 20;
            if (OldRagnoEntity.this.isCrazy()) {
                ++OldRagnoEntity.this.attacksUsed;
            }

        }
    }

    class BurrowGoal extends Goal {
        public BurrowGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldRagnoEntity.this.doesAttackMeetNormalRequirements() && OldRagnoEntity.this.random.nextInt(16) == 0 && OldRagnoEntity.this.burrowCooldown < 1 && OldRagnoEntity.this.isCrazy();
        }

        public void start() {
            OldRagnoEntity.this.setAnimationState(6);
            OldRagnoEntity.this.setAttackType(OldRagnoEntity.this.BURROW_ATTACK);
        }

        public boolean canContinueToUse() {
            return OldRagnoEntity.this.attackTicks <= 138;
        }

        public void tick() {
            OldRagnoEntity.this.getNavigation().stop();
            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (OldRagnoEntity.this.getTarget() != null) {
                OldRagnoEntity.this.getLookControl().setLookAt(OldRagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            OldRagnoEntity.this.navigation.stop();
        }

        public void stop() {
            OldRagnoEntity.this.setAnimationState(0);
            OldRagnoEntity.this.attackTicks = 0;
            OldRagnoEntity.this.setAttackType(0);
            OldRagnoEntity.this.burrowCooldown = 160;
            OldRagnoEntity.this.attackCooldown = 20;
            ++OldRagnoEntity.this.attacksUsed;
            OldRagnoEntity.this.setInvisible(false);
            OldRagnoEntity.this.isBurrowing = false;
        }
    }

    class ChargeGoal extends Goal {
        public ChargeGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldRagnoEntity.this.doesAttackMeetNormalRequirements() && OldRagnoEntity.this.random.nextInt(16) == 0 && OldRagnoEntity.this.chargeCooldown < 1 && OldRagnoEntity.this.isCrazy();
        }

        public void start() {
            OldRagnoEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_PREPARECHARGE.get(), 2.0F, 0.9F);
            OldRagnoEntity.this.setAnimationState(8);
            OldRagnoEntity.this.setAttackType(OldRagnoEntity.this.CHARGE_ATTACK);
        }

        public boolean canContinueToUse() {
            return OldRagnoEntity.this.attackTicks <= 70;
        }

        public void tick() {
            OldRagnoEntity.this.getNavigation().stop();
            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (OldRagnoEntity.this.getTarget() != null) {
                OldRagnoEntity.this.getLookControl().setLookAt(OldRagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            OldRagnoEntity.this.navigation.stop();
        }

        public void stop() {
            OldRagnoEntity.this.setAnimationState(0);
            OldRagnoEntity.this.attackTicks = 0;
            OldRagnoEntity.this.setAttackType(0);
            OldRagnoEntity.this.chargeCooldown = 160;
            OldRagnoEntity.this.attackCooldown = 20;
            ++OldRagnoEntity.this.attacksUsed;
        }
    }

    class CoughGoal extends Goal {
        public CoughGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldRagnoEntity.this.doesAttackMeetNormalRequirements() && OldRagnoEntity.this.random.nextInt(16) == 0 && OldRagnoEntity.this.coughCooldown < 1 && OldRagnoEntity.this.isCrazy();
        }

        public void start() {
            OldRagnoEntity.this.setAnimationState(9);
            OldRagnoEntity.this.setAttackType(OldRagnoEntity.this.COUGH_ATTACK);
        }

        public boolean canContinueToUse() {
            return OldRagnoEntity.this.attackTicks <= 70;
        }

        public void tick() {
            OldRagnoEntity.this.getNavigation().stop();
            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (OldRagnoEntity.this.getTarget() != null) {
                OldRagnoEntity.this.getLookControl().setLookAt(OldRagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            OldRagnoEntity.this.navigation.stop();
        }

        public void stop() {
            OldRagnoEntity.this.setAnimationState(0);
            OldRagnoEntity.this.attackTicks = 0;
            OldRagnoEntity.this.setAttackType(0);
            OldRagnoEntity.this.coughCooldown = 200;
            OldRagnoEntity.this.attackCooldown = 20;
            ++OldRagnoEntity.this.attacksUsed;
        }
    }

    class AlwaysWatchTargetGoal extends Goal {
        public AlwaysWatchTargetGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public boolean canUse() {
            return OldRagnoEntity.this.isPlayingIntro;
        }

        public boolean canContinueToUse() {
            return OldRagnoEntity.this.isPlayingIntro;
        }

        public void tick() {
            OldRagnoEntity.this.getNavigation().stop();
            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            if (OldRagnoEntity.this.getTarget() != null) {
                OldRagnoEntity.this.getLookControl().setLookAt(OldRagnoEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldRagnoEntity.this.getMoveControl().strafe(0.0F, 0.0F);
            OldRagnoEntity.this.navigation.stop();
        }

        public void stop() {
            OldRagnoEntity.this.isPlayingIntro = false;
            OldRagnoEntity.this.setAnimationState(0);
        }
    }
}
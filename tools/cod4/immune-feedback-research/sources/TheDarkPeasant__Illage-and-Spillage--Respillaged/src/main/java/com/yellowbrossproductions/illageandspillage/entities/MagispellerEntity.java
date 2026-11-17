package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.client.sound.BossMusicPlayer;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.goal.MeleeButStopGoal;
import com.yellowbrossproductions.illageandspillage.entities.goal.StareAtDeadMagiGoal;
import com.yellowbrossproductions.illageandspillage.entities.projectile.MagiArrowEntity;
import com.yellowbrossproductions.illageandspillage.entities.projectile.MagiFireballEntity;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import com.yellowbrossproductions.illageandspillage.util.ItemRegisterer;
import com.yellowbrossproductions.illageandspillage.util.ModTags;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Direction.Axis;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Ravager;
import net.minecraft.world.entity.monster.Vex;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.EvokerFangs;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.entity.projectile.ThrownPotion;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.entity.EntityTeleportEvent;
import net.minecraftforge.network.PacketDistributor;

import javax.annotation.Nullable;
import java.util.*;

public class MagispellerEntity extends AbstractIllager implements ICanBeAnimated {
    public ServerBossEvent bossEvent;
    private static final EntityDataAccessor<Boolean> NEARBY_ILLAGERS;
    private static final EntityDataAccessor<Boolean> SHOULD_DELETE_ITSELF;
    private static final EntityDataAccessor<Boolean> ACTIVE;
    private static final EntityDataAccessor<Boolean> SHOW_ARMS;
    private static final EntityDataAccessor<Integer> GLOW_STATE;
    private static final EntityDataAccessor<Integer> SHAKE_AMOUNT;
    private static final EntityDataAccessor<Boolean> FAKING;
    private static final EntityDataAccessor<Integer> ARROW_STATE;
    private static final EntityDataAccessor<Boolean> WAVING_ARMS;
    private static final EntityDataAccessor<Boolean> BALLOON;
    private static final EntityDataAccessor<Boolean> DEATH;
    private static final EntityDataAccessor<Integer> ANIMATION_STATE;
    private static final EntityDataAccessor<Integer> ATTACK_TYPE;
    private static final EntityDataAccessor<Integer> ATTACK_TICKS;
    public AnimationState fireballAnimationState = new AnimationState();
    public AnimationState lifestealAnimationState = new AnimationState();
    public AnimationState fakersAnimationState = new AnimationState();
    public AnimationState vexesAnimationState = new AnimationState();
    public AnimationState fangrunAnimationState = new AnimationState();
    public AnimationState potionsAnimationState = new AnimationState();
    public AnimationState crossbowspinAnimationState = new AnimationState();
    public AnimationState crashagerAnimationState = new AnimationState();
    public AnimationState dispenserAnimationState = new AnimationState();
    public AnimationState knockbackAnimationState = new AnimationState();
    public AnimationState kaboomerAnimationState = new AnimationState();
    public AnimationState deathAnimationState = new AnimationState();
    private int fireballCooldown;
    private int lifestealCooldown;
    private int fakersCooldown;
    private int vexesCooldown;
    private int fangrunCooldown;
    private int throwPotionsCooldown;
    private int crossbowSpinCooldown;
    private int crashagerCooldown;
    private int dispenserCooldown;
    private int healCooldown;
    private int kaboomerCooldown;
    private final int FIREBALL_ATTACK = 1;
    private final int LIFESTEAL_ATTACK = 2;
    private final int FAKERS_ATTACK = 3;
    private final int VEXES_ATTACK = 4;
    private final int FANGRUN_ATTACK = 5;
    private final int POTIONS_ATTACK = 6;
    private final int CROSSBOWSPIN_ATTACK = 7;
    private final int CRASHAGER_ATTACK = 8;
    private final int DISPENSER_ATTACK = 9;
    private final int HEAL_ATTACK = 10;
    private final int KNOCKBACK_ATTACK = 11;
    private final int KABOOMER_ATTACK = 12;
    private MagiFireballEntity fireball = null;
    private int pullPower;
    private final List<FakeMagispellerEntity> clones = new ArrayList<>();
    private int waitTimeFaker;
    private int spinDirection;
    private float damageTaken;
    private boolean gotHealed;
    private int balloonCooldown;
    private Entity mobToLaughAt;
    public int customDeathTime;
    private ItemEntity totem = null;
    private DamageSource lastDamageSource;
    private boolean shouldDropDisc = false;

    public MagispellerEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 100;
        bossEvent = (ServerBossEvent) (new ServerBossEvent(this.getDisplayName(), BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.PROGRESS)).setDarkenScreen(Config.CommonConfig.bosses_darken_sky.get());
        bossEvent.setVisible(false);
        this.getAttribute(Attributes.MAX_HEALTH).setBaseValue(Config.CommonConfig.magispeller_health.get());
        this.heal(Float.MAX_VALUE);
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

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new KaboomerGoal());
        this.goalSelector.addGoal(0, new HealGoal());
        this.goalSelector.addGoal(0, new DispenserGoal());
        this.goalSelector.addGoal(0, new CrashagerGoal());
        this.goalSelector.addGoal(0, new CrossbowSpinGoal());
        this.goalSelector.addGoal(0, new ThrowPotionsGoal());
        this.goalSelector.addGoal(0, new FangRunGoal());
        this.goalSelector.addGoal(0, new SummonVexesGoal());
        this.goalSelector.addGoal(0, new FakersGoal());
        this.goalSelector.addGoal(0, new LifestealGoal());
        this.goalSelector.addGoal(0, new ShootFireballGoal());
        this.goalSelector.addGoal(0, new KnockbackGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new StareAtTargetGoal());
        this.goalSelector.addGoal(2, new Raider.HoldGroundAttackGoal(this, 10.0F));
        this.goalSelector.addGoal(3, new MeleeButStopGoal(this, 1.0, false, 10.0));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 1).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 96.0);
    }

    protected void customServerAiStep() {
        super.customServerAiStep();

        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());

        Entity entity = this.getTarget();
        if (this.isFaking() && this.random.nextInt(10) == 0 && entity != null && this.distanceToSqr(entity) > 1024.0) {
            this.teleportTowards(entity);
        }
    }

    public boolean causeFallDamage(float p_225503_1_, float p_225503_2_, DamageSource p_147189_) {
        return !this.isFaking() && super.causeFallDamage(p_225503_1_, p_225503_2_, p_147189_);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(NEARBY_ILLAGERS, false);
        this.entityData.define(SHOULD_DELETE_ITSELF, false);
        this.entityData.define(ACTIVE, false);
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(ATTACK_TYPE, 0);
        this.entityData.define(ATTACK_TICKS, 0);
        this.entityData.define(SHOW_ARMS, false);
        this.entityData.define(GLOW_STATE, 0);
        this.entityData.define(SHAKE_AMOUNT, 0);
        this.entityData.define(FAKING, false);
        this.entityData.define(ARROW_STATE, 0);
        this.entityData.define(WAVING_ARMS, false);
        this.entityData.define(BALLOON, false);
        this.entityData.define(DEATH, false);
    }

    public boolean canAttack(LivingEntity p_213336_1_) {
        return !this.areIllagersNearby() && super.canAttack(p_213336_1_);
    }

    public int getGlowState() {
        return this.entityData.get(GLOW_STATE);
    }

    public void setGlowState(int glowState) {
        this.entityData.set(GLOW_STATE, glowState);
    }

    public int getShakeAmount() {
        return this.entityData.get(SHAKE_AMOUNT);
    }

    public void setShakeAmount(int shake) {
        this.entityData.set(SHAKE_AMOUNT, shake);
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

    public boolean isFaking() {
        return this.entityData.get(FAKING);
    }

    public void setFaking(boolean faking) {
        this.entityData.set(FAKING, faking);
    }

    public int getArrowState() {
        return this.entityData.get(ARROW_STATE);
    }

    public void setArrowState(int arrow) {
        this.entityData.set(ARROW_STATE, arrow);
    }

    public boolean isCustomDeath() {
        return this.entityData.get(DEATH);
    }

    public void setCustomDeath(boolean death) {
        this.entityData.set(DEATH, death);
    }

    public void addAdditionalSaveData(CompoundTag p_213281_1_) {
        super.addAdditionalSaveData(p_213281_1_);
        if (this.isActive()) {
            p_213281_1_.putBoolean("active", true);
        }

        if (this.isBalloon()) {
            p_213281_1_.putBoolean("IsBalloon", true);
        }

    }

    public void readAdditionalSaveData(CompoundTag p_70037_1_) {
        super.readAdditionalSaveData(p_70037_1_);
        this.bossEvent.setName(this.getDisplayName());
        this.setActive(p_70037_1_.getBoolean("active"));
        this.setBalloon(p_70037_1_.getBoolean("IsBalloon"));
    }

    public void setHealth(float p_21154_) {
        float healthValue = p_21154_ - this.getHealth();
        if (healthValue > 0 || (!this.areIllagersNearby() && this.isActive()) || healthValue <= -1000000000000.0F) {
            if (healthValue < -20 && healthValue > -1000000000000.0F) {
                p_21154_ = this.getHealth() - 20.0F;
            }
            super.setHealth(p_21154_);
        }
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    protected float getStandingEyeHeight(Pose p_213348_1_, EntityDimensions p_213348_2_) {
        return 1.66F;
    }

    public SoundEvent getBossMusic() {
        return IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_MUSIC.get();
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
        List<Raider> list = this.level().getEntitiesOfClass(Raider.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.hasActiveRaid() && !predicate.getType().is(ModTags.EntityTypes.ILLAGER_BOSSES));
        if (Config.CommonConfig.magispeller_forcefield.get() && this.hasActiveRaid()) {
            if (!this.level().isClientSide) {
                this.setIllagersNearby(!list.isEmpty());
            }

            if (this.areIllagersNearby()) {
                this.setTarget(null);
            }
        }

        if (this.hasActiveRaid()) {
            if (this.getCurrentRaid() != null && this.getCurrentRaid().getGroupsSpawned() == 7 && this.shouldRemoveItself() && Config.CommonConfig.magispeller_onlyOneAllowed.get()) {
                this.getCurrentRaid().removeFromRaid(this, true);
                if (!this.level().isClientSide) {
                    this.remove(RemovalReason.DISCARDED);
                }
            }
        }

        if (EntityUtil.displayBossBar(this) && this.isActive() && !bossEvent.isVisible()) {
            bossEvent.setVisible(true);
        } else if (bossEvent.isVisible()) {
            bossEvent.setVisible(false);
        }

        if (!this.level().isClientSide && this.isActive() && this.getBossMusic() != null) {
            if (this.canPlayMusic()) {
                this.level().broadcastEntityEvent(this, (byte) 67);
            } else {
                this.level().broadcastEntityEvent(this, (byte) 68);
            }
        }

        if (this.getAttackType() > 0) {
            this.setAttackTicks(this.getAttackTicks() + 1);
        } else {
            this.setAttackTicks(0);
        }

        if (this.getAttackType() == 0) {
            if (this.fireballCooldown > 0) {
                --this.fireballCooldown;
            }

            if (this.lifestealCooldown > 0) {
                --this.lifestealCooldown;
            }

            if (this.fakersCooldown > 0 && !this.isFaking()) {
                --this.fakersCooldown;
            }

            if (this.vexesCooldown > 0) {
                --this.vexesCooldown;
            }

            if (this.fangrunCooldown > 0) {
                --this.fangrunCooldown;
            }

            if (this.throwPotionsCooldown > 0) {
                --this.throwPotionsCooldown;
            }

            if (this.crossbowSpinCooldown > 0) {
                --this.crossbowSpinCooldown;
            }

            if (this.crashagerCooldown > 0 && !this.isRidingIllusion()) {
                --this.crashagerCooldown;
            }

            if (this.dispenserCooldown > 0) {
                --this.dispenserCooldown;
            }

            if (this.kaboomerCooldown > 0 && !this.isRidingIllusion()) {
                --this.kaboomerCooldown;
            }
        }

        if (this.healCooldown > 0) {
            --this.healCooldown;
        }

        if (this.waitTimeFaker > 0) {
            --this.waitTimeFaker;
        }

        if (this.balloonCooldown > 0) {
            --this.balloonCooldown;
        }

        Iterator var2;
        if (this.getTarget() == null && !this.clones.isEmpty()) {
            var2 = this.clones.iterator();

            while (var2.hasNext()) {
                FakeMagispellerEntity clone = (FakeMagispellerEntity) var2.next();
                clone.kill();
            }
        }

        if (this.isFaking() && this.clones.isEmpty() && !this.level().isClientSide) {
            this.setFaking(false);
        }

        this.updateCloneList();
        double x;
        double y;
        double z;
        LivingEntity entity;
        float f1;
        if (this.isAlive()) {
            if (this.getAttackType() == this.FIREBALL_ATTACK) {
                entity = this.getTarget();
                if (this.getAttackTicks() == 8) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_FIREBALL_START.get(), 2.0F, 1.0F);
                    this.makeFireParticles();
                    CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.3F, 0, 15);
                    if (!this.level().isClientSide) {
                        this.setGlowState(1);
                    }

                    this.setLeftHanded(true);
                }

                if (this.getAttackTicks() == 14) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_FIREBALL.get(), 2.0F, 1.0F);
                    if (!this.level().isClientSide) {
                        this.fireball = new MagiFireballEntity(ModEntityTypes.MagiFireball.get(), this.level());
                        this.level().addFreshEntity(this.fireball);
                    }
                }

                if (this.fireball != null && this.getAttackTicks() < 58) {
                    f1 = 1.1F;
                    x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) f1 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                    y = this.getY() + 1.3 + (double) f1 * Math.sin((double) (-this.getXRot()) * Math.PI / 180.0);
                    z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) f1 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                    this.fireball.hurtMarked = true;
                    this.fireball.setPos(x, y, z);
                    this.fireball.setMagispeller(this);
                }

                if (this.getAttackTicks() == 55) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SWING_BAT.get(), 2.0F, 1.0F);
                }

                if (this.getAttackTicks() == 58) {
                    this.makeFireParticles();
                    if (!this.level().isClientSide) {
                        this.setGlowState(0);
                    }

                    if (this.fireball != null && entity != null) {
                        this.fireball.hurt(this.damageSources().mobAttack(this), 0.0F);
                    }
                }
            }

            double d;
            float power;
            double motionX;
            double motionY;
            double motionZ;
            Entity entity1;
            if (this.getAttackType() == this.LIFESTEAL_ATTACK) {
                if (this.getAttackTicks() < 30) {
                    this.makeLifestealParticles1();
                    if (!this.level().isClientSide) {
                        this.setGlowState(this.random.nextBoolean() ? 0 : 2);
                    }
                }

                if (this.getAttackTicks() == 31) {
                    if (!this.level().isClientSide) {
                        this.setGlowState(2);
                    }

                    this.pullPower = 0;
                }

                if (this.getAttackTicks() == 36) {
                    EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_LIFESTEAL.get(), 2.0F, 1.0F, false);
                }

                if (this.getAttackTicks() >= 36) {
                    ++this.pullPower;
                    if (!this.level().isClientSide && this.getAttackTicks() % 3 == 1) {
                        this.setShakeAmount(this.getShakeAmount() + 1);
                    }

                    this.makeLifestealParticles3();
                    var2 = this.level().getEntities(this, this.getBoundingBox().inflate(15.0)).iterator();

                    while (var2.hasNext()) {
                        entity1 = (Entity) var2.next();
                        if (EntityUtil.canHurtThisMob(entity1, this) && entity1.isAlive() && this.isMobNotInCreativeMode(entity1)) {
                            x = this.getX() - entity1.getX();
                            y = this.getY() - entity1.getY();
                            z = this.getZ() - entity1.getZ();
                            d = Math.sqrt(x * x + y * y + z * z);
                            power = (float) this.pullPower / 103.0F;
                            motionX = entity1.getDeltaMovement().x + x / d * (double) power * 0.2;
                            motionY = entity1.getDeltaMovement().y + y / d * (double) power * 0.2;
                            motionZ = entity1.getDeltaMovement().z + z / d * (double) power * 0.2;
                            entity1.hurtMarked = true;
                            entity1.setDeltaMovement(motionX, motionY, motionZ);
                            entity1.lerpMotion(motionX, motionY, motionZ);
                            this.makeLifestealParticles2(entity1);
                            if (this.distanceToSqr(entity1) < 9.0 && entity1 instanceof LivingEntity) {
                                if (((LivingEntity) entity1).hurtTime <= 0 && !entity1.isInvulnerable()) {
                                    float healthStolen = ((((LivingEntity) entity1).getMaxHealth() - ((LivingEntity) entity1).getHealth()) / 3.0F + 1.0F);
                                    healthStolen = Math.min(healthStolen, 10);

                                    healthStolen = Config.CommonConfig.nightmare_mode.get() ? (float) (healthStolen * Config.CommonConfig.magi_damage_multiplier.get()) : healthStolen;

                                    this.heal(healthStolen);
                                    entity1.hurt(this.damageSources().indirectMagic(this, this), healthStolen);
                                }

                                entity1.hurtMarked = true;
                                entity1.setDeltaMovement(-x / d * 2.0, -y / d * 2.0, -z / d * 2.0);
                                entity1.lerpMotion(-x / d * 2.0, -y / d * 2.0, -z / d * 2.0);
                            }
                        }
                    }
                }
            }

            if (this.getAttackType() == this.FAKERS_ATTACK) {
                if (this.getAttackTicks() < 43) {
                    if (!this.level().isClientSide && this.getAttackTicks() % 3 == 1) {
                        this.setShakeAmount(this.getShakeAmount() + 1);
                    }

                    this.makeFakerParticles();
                } else if (this.getAttackTicks() <= 48) {
                    if (!this.level().isClientSide) {
                        this.setShakeAmount(this.getShakeAmount() / 5);
                    }
                } else if (this.getAttackTicks() == 49 && !this.level().isClientSide) {
                    this.setShakeAmount(0);
                }

                if (this.getAttackTicks() == 16 && !this.level().isClientSide) {
                    this.setGlowState(3);
                }
            }

            if (this.getAttackType() == this.VEXES_ATTACK && this.getAttackTicks() == 20) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_CAST_SPELL.get(), 1.0F, 1.0F);
                if (!this.level().isClientSide) {
                    ServerLevel serverworld = (ServerLevel) this.level();
                    BlockPos blockpos = this.blockPosition();

                    for (int i = 0; i < 5; ++i) {
                        Vex vex = EntityType.VEX.create(this.level());

                        assert vex != null;

                        vex.setPos(this.getX(), this.getY() + 3.0, this.getZ());
                        vex.finalizeSpawn(serverworld, this.level().getCurrentDifficultyAt(blockpos), MobSpawnType.MOB_SUMMONED, null, null);
                        vex.setTarget(this.getTarget());
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(vex.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        (Objects.requireNonNull(vex.getAttribute(Attributes.MAX_HEALTH))).setBaseValue(2.0);
                        vex.setLimitedLife(100);
                        vex.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
                        vex.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
                        this.level().addFreshEntity(vex);
                    }
                }
            }

            if (this.getAttackType() == this.FANGRUN_ATTACK) {
                if (this.getAttackTicks() >= 6 && this.getAttackTicks() < 49) {
                    if (this.getShakeAmount() > 0 && !this.level().isClientSide) {
                        this.setShakeAmount(this.getShakeAmount() - 1);
                    }

                    this.createFangs(false);
                    if (this.getAttackTicks() == 6) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_FANGRUN_START.get(), 1.0F, 1.0F);
                        EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_FANGRUN.get(), 2.0F, 1.0F, false);
                        this.makeFangRunParticles();
                        CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.3F, 0, 20);
                        if (!this.level().isClientSide) {
                            this.setGlowState(4);
                        }

                        for (Entity value : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                            entity1 = value;
                            if (EntityUtil.canHurtThisMob(entity1, this) && entity1.isAlive()) {
                                x = this.getX() - entity1.getX();
                                y = this.getY() - entity1.getY();
                                z = this.getZ() - entity1.getZ();
                                d = Math.sqrt(x * x + y * y + z * z);
                                if (this.distanceToSqr(entity1) < 9.0) {
                                    entity1.hurtMarked = true;
                                    entity1.setDeltaMovement(-x / d * 3.0, -y / d * 0.5, -z / d * 3.0);
                                    entity1.lerpMotion(-x / d * 3.0, -y / d * 0.5, -z / d * 3.0);
                                }
                            }
                        }
                    }
                }

                if (this.getAttackTicks() >= 49) {
                    this.createFangs(true);
                    this.playSound(SoundEvents.EVOKER_FANGS_ATTACK, 1.0F, this.getVoicePitch());

                    for (Entity value : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        entity1 = value;
                        if (EntityUtil.canHurtThisMob(entity1, this) && entity1.isAlive()) {
                            x = this.getX() - entity1.getX();
                            y = this.getY() - entity1.getY();
                            z = this.getZ() - entity1.getZ();
                            d = Math.sqrt(x * x + y * y + z * z);
                            if (this.distanceToSqr(entity1) < 9.0) {
                                entity1.hurtMarked = true;
                                entity1.setDeltaMovement(-x / d * 3.0, -y / d * 0.5, -z / d * 3.0);
                                entity1.lerpMotion(-x / d * 3.0, -y / d * 0.5, -z / d * 3.0);
                            }
                        }
                    }
                }
            }

            int i;
            if (this.getAttackType() == this.POTIONS_ATTACK) {
                if (this.getAttackTicks() == 10) {
                    EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_POTIONS.get(), 2.0F, 1.0F, false);
                }

                if (this.getAttackTicks() > 22) {
                    for (i = 0; i < 2; ++i) {
                        if (!this.level().isClientSide) {
                            ThrownPotion potionentity = new ThrownPotion(this.level(), this);
                            potionentity.setItem(PotionUtils.setPotion(new ItemStack(Items.SPLASH_POTION), Potions.STRONG_SLOWNESS));
                            potionentity.setXRot(-20.0F);
                            potionentity.shoot(-2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble(), 5.0 + this.random.nextDouble() + this.random.nextDouble(), -2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble(), 0.75F, 8.0F);
                            potionentity.setDeltaMovement(potionentity.getDeltaMovement().add(0.0, 0.5, 0.0));
                            this.level().addFreshEntity(potionentity);
                        }
                    }
                }

                if (this.getAttackTicks() >= 10) {
                    this.makePotionParticles();
                }
            }

            if (this.getAttackType() == this.CROSSBOWSPIN_ATTACK) {
                MagiArrowEntity arrow;
                if (this.getAttackTicks() <= 12) {
                    for (i = 0; i < 5; ++i) {
                        if (!this.level().isClientSide) {
                            arrow = new MagiArrowEntity(this.level(), this);
                            arrow.setPos(this.getX(), this.getY() + 2.0, this.getZ());
                            arrow.noPhysics = true;
                            arrow.setNoGravity(true);
                            arrow.setDeltaMovement((-0.5 + this.random.nextDouble()) * 0.6, 0.5, (-0.5 + this.random.nextDouble()) * 0.6);
                            arrow.setOwner(this);
                            this.level().addFreshEntity(arrow);
                        }
                    }
                } else if (this.getAttackTicks() <= 41) {
                    var2 = this.level().getEntitiesOfClass(MagiArrowEntity.class, this.getBoundingBox().inflate(50.0)).iterator();

                    while (var2.hasNext()) {
                        arrow = (MagiArrowEntity) var2.next();
                        if (arrow.isNoPhysics() && arrow.getOwner() == this) {
                            x = this.getX() - arrow.getX();
                            y = this.getY() - arrow.getY();
                            z = this.getZ() - arrow.getZ();
                            d = Math.sqrt(x * x + y * y + z * z);
                            power = 2.0F;
                            motionX = x / d * (double) power * 0.2;
                            motionY = y / d * (double) power * 0.2;
                            motionZ = z / d * (double) power * 0.2;
                            arrow.setDeltaMovement(motionX, motionY, motionZ);
                            this.makeArrowParticles(arrow);
                            if (this.distanceToSqr(arrow) < 2.0) {
                                arrow.discard();
                                this.playSound(SoundEvents.CROSSBOW_LOADING_END, 2.0F, this.getVoicePitch());
                            }
                        }
                    }
                }

                if (this.getAttackTicks() == 41) {
                    this.setAnimationState(0);
                    if (this.getTarget() != null) {
                        EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SPIN.get(), 1.0F, 1.0F, false);

                        if (!this.level().isClientSide) {
                            this.setArrowState(1);
                        }

                        if (!this.level().isClientSide) {
                            this.setDeltaMovement((this.getTarget().getX() - this.getX()) * 2.0 * 0.16, 0.5, (this.getTarget().getZ() - this.getZ()) * 2.0 * 0.16);
                        }
                    }
                }

                if (this.getAttackTicks() == 49) {
                    this.playSound(SoundEvents.CROSSBOW_QUICK_CHARGE_3, 1.0F, 1.0F);
                }

                if (this.getAttackTicks() == 59 && this.getTarget() != null) {
                    if (!this.level().isClientSide) {
                        this.setArrowState(2);
                    }

                    EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_ARROWBARRAGE.get(), 2.0F, 1.0F, false);
                }

                if (this.getAttackTicks() >= 59 && this.getTarget() != null) {
                    this.fireArrow(this.getTarget(), 1.0F, 0.5F);
                }
            }

            if (this.getAttackType() == this.CRASHAGER_ATTACK) {
                if (this.getAttackTicks() < 68) {
                    this.setDeltaMovement(0.0, 0.06, 0.0);
                    this.makeCrashagerParticles1();
                    if (!this.level().isClientSide) {
                        this.setGlowState(this.random.nextBoolean() ? 0 : 3);
                    }
                }

                if (this.getAttackTicks() == 68) {
                    if (!this.level().isClientSide) {
                        this.setGlowState(0);
                        this.setShakeAmount(0);
                    }

                    if (this.getTarget() != null) {
                        CrashagerEntity ravager = null;
                        if (!this.level().isClientSide) {
                            ravager = ModEntityTypes.Crashager.get().create(this.level());
                        }

                        if (ravager != null) {
                            ravager.setPos(this.getX(), this.getY(), this.getZ());
                            ravager.setTarget(this.getTarget());
                            ravager.setOwner(this);
                            if (this.getTeam() != null) {
                                this.level().getScoreboard().addPlayerToTeam(ravager.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                            }

                            this.level().addFreshEntity(ravager);
                            this.startRiding(ravager);
                            this.makeCrashagerParticles2(ravager);
                        }
                    }
                }
            }

            if (this.getAttackType() == this.DISPENSER_ATTACK) {
                if (this.getAttackTicks() == 4) {
                    this.makeDispenserParticles();
                    if (!this.level().isClientSide) {
                        this.setGlowState(5);
                    }
                }

                if (this.getAttackTicks() == 20) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_LOAD.get(), 2.0F, 1.0F);
                }

                if (this.getAttackTicks() == 30) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SHOOT.get(), 2.0F, 1.0F);
                    if (!this.level().isClientSide) {
                        DispenserEntity dispenser = ModEntityTypes.Dispenser.get().create(this.level());

                        assert dispenser != null;

                        dispenser.setPos(this.getX(), this.getY() + 3.0, this.getZ());
                        dispenser.setDeltaMovement((double) (-2 + this.random.nextInt(5)) * 0.4, 0.6, (double) (-2 + this.random.nextInt(5)) * 0.4);
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(dispenser.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        dispenser.setOwner(this);
                        dispenser.setInMotion(true);
                        this.level().addFreshEntity(dispenser);
                    }
                }
            }

            if (this.getAttackType() == this.HEAL_ATTACK) {
                if (this.damageTaken > 30.0F) {
                    this.gotHealed = false;
                }

                this.makeHealProgressParticles();
                var2 = this.level().getEntities(this, this.getBoundingBox().inflate(15.0)).iterator();

                while (var2.hasNext()) {
                    entity1 = (Entity) var2.next();
                    if (EntityUtil.canHurtThisMob(entity1, this) && entity1.isAlive()) {
                        x = this.getX() - entity1.getX();
                        y = this.getY() - entity1.getY();
                        z = this.getZ() - entity1.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        if ((double) this.distanceTo(entity1) < 10.0 && this.isMobNotInCreativeMode(entity1)) {
                            entity1.hurtMarked = true;
                            entity1.setDeltaMovement(entity1.getDeltaMovement().add(-x / d * 0.015, -y / d * 0.03, -z / d * 0.015));
                        }
                    }
                }
            }

            if (this.getAttackType() == this.KNOCKBACK_ATTACK && this.getAttackTicks() == 5) {
                this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 2.0F, 1.0F);
                var2 = this.level().getEntities(this, this.getBoundingBox().inflate(15.0)).iterator();

                while (var2.hasNext()) {
                    entity1 = (Entity) var2.next();
                    if (EntityUtil.canHurtThisMob(entity1, this) && entity1.isAlive()) {
                        x = this.getX() - entity1.getX();
                        y = this.getY() - entity1.getY();
                        z = this.getZ() - entity1.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        if ((double) this.distanceTo(entity1) < 3.0 && this.isMobNotInCreativeMode(entity1)) {
                            entity1.hurtMarked = true;
                            entity1.setDeltaMovement(entity1.getDeltaMovement().add(-x / d * 5.0, -y / d * 0.3, -z / d * 5.0));
                            entity1.hurt(this.damageSources().mobAttack(this), 6.0F);
                        }
                    }
                }
            }

            if (this.getAttackType() == this.KABOOMER_ATTACK && this.getAttackTicks() > 5 && !this.level().isClientSide) {
                this.setGlowState(this.random.nextBoolean() ? 0 : 3);
                this.setShakeAmount(this.getShakeAmount() + 1);
            }
        }

        if (this.getTarget() != null && this.isActive() && this.isAlive() && (double) this.distanceTo(this.getTarget()) < 6.0 * ((double) this.getTarget().getBbWidth() + 0.4) && this.canAttackBackUp() && this.onGround() && !this.isFaking()) {
            x = this.getY() - this.getTarget().getY();
            y = this.getZ() - this.getTarget().getZ();
            z = Math.sqrt(x * x + x * x + y * y);
            this.setDeltaMovement(this.getDeltaMovement().subtract(-x / z * 0.06, 0.0, -y / z * 0.06));
        }

        if (this.fallDistance > 5.0F && this.balloonCooldown < 1 && (this.getAttackType() == 0 || this.getAttackType() == this.HEAL_ATTACK) && this.isActive() && Config.CommonConfig.magispeller_balloonAllowed.get() && this.isAlive()) {
            this.playSound(SoundEvents.SNOWBALL_THROW, 3.0F, 0.5F);
            if (!this.level().isClientSide) {
                this.setShowArms(true);
                this.setBalloon(true);
            }

            this.fallDistance = 0.0F;
            this.gotHealed = false;
            this.setDeltaMovement(this.getDeltaMovement().x, 0.7, this.getDeltaMovement().z);
            this.balloonCooldown = 10;
        }

        if (this.isBalloon()) {
            this.fallDistance = 0.0F;
            if (!this.level().isClientSide) {
                this.setShowArms(true);
            }

            if (this.getTarget() != null) {
                entity = this.getTarget();
                double x1 = this.getX() - entity.getX();
                double y1 = this.getY() - entity.getY();
                double z1 = this.getZ() - entity.getZ();
                double d = Math.sqrt(x1 * x1 + y1 * y1 + z1 * z1);
                float power = 0.08F;
                double motionX = this.getDeltaMovement().x - x1 / d * (double) power * 0.2;
                double motionY = this.getDeltaMovement().y - y1 / d * (double) power * 0.2;
                double motionZ = this.getDeltaMovement().z - z1 / d * (double) power * 0.2;
                this.setDeltaMovement(motionX, motionY, motionZ);
                if (this.level().getBlockState(this.blockPosition().below(5)) == Blocks.AIR.defaultBlockState() && this.level().getBlockState(this.blockPosition().below(4)) == Blocks.AIR.defaultBlockState() && this.level().getBlockState(this.blockPosition().below(3)) == Blocks.AIR.defaultBlockState() && this.level().getBlockState(this.blockPosition().below(2)) == Blocks.AIR.defaultBlockState() && this.level().getBlockState(this.blockPosition().below(1)) == Blocks.AIR.defaultBlockState()) {
                    if (this.getDeltaMovement().y > 0.0) {
                        this.setDeltaMovement(this.getDeltaMovement().add(0.0, -0.01, 0.0));
                    }
                } else {
                    this.setDeltaMovement(this.getDeltaMovement().add(0.0, 0.04, 0.0));
                }
            } else if (this.level().getBlockState(this.blockPosition().below(1)) != Blocks.AIR.defaultBlockState()) {
                this.setDeltaMovement(this.getDeltaMovement().add(0.0, 0.04, 0.0));
            } else {
                this.setDeltaMovement(this.getDeltaMovement().add(0.0, -0.01, 0.0));
            }

            if (this.getTarget() != null && (double) this.distanceTo(this.getTarget()) < 10.0 && this.hasLineOfSight(this.getTarget()) && this.balloonCooldown < 1 || !this.isAlive()) {
                this.playSound(SoundEvents.FIREWORK_ROCKET_BLAST_FAR, 3.0F, 1.0F);
                this.balloonCooldown = 200;
                if (!this.level().isClientSide) {
                    this.setBalloon(false);
                }
            }
        }

        super.tick();
        if (this.isWavingArms()) {
            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
        }

        if (this.shouldShowArms()) {
            this.setYRot(this.getYHeadRot());
            this.yBodyRot = this.getYRot();
        }

        if (this.getArrowState() == 1) {
            ++this.spinDirection;
            if (this.spinDirection > 4) {
                this.spinDirection = 1;
            }

            this.yBodyRot = (float) (this.spinDirection * 90);
        }

        if (this.isWavingArms() && this.level().isClientSide) {
            float f = this.yBodyRot * 0.017453292F + Mth.cos((float) this.tickCount * 0.6662F) * 0.25F;
            f1 = Mth.cos(f);
            float f2 = Mth.sin(f);
            this.level().addParticle(ParticleTypes.ENTITY_EFFECT, this.getX() + (double) f1 * 0.6, this.getY() + 1.8, this.getZ() + (double) f2 * 0.6, 0.1, 0.1, 0.2);
            this.level().addParticle(ParticleTypes.ENTITY_EFFECT, this.getX() - (double) f1 * 0.6, this.getY() + 1.8, this.getZ() - (double) f2 * 0.6, 0.1, 0.1, 0.2);
        }

    }

    public boolean isWavingArms() {
        return this.entityData.get(WAVING_ARMS);
    }

    public void setWavingArms(boolean waving) {
        this.entityData.set(WAVING_ARMS, waving);
    }

    public boolean isRidingIllusion() {
        return this.getVehicle() instanceof CrashagerEntity || this.getVehicle() instanceof KaboomerEntity;
    }

    public boolean startRiding(Entity p_20330_) {
        return (p_20330_ instanceof CrashagerEntity || p_20330_ instanceof KaboomerEntity || p_20330_ instanceof CrocofangEntity || p_20330_ instanceof Ravager) && super.startRiding(p_20330_);
    }

    public void updateCloneList() {
        if (!this.clones.isEmpty()) {
            for (int i = 0; i < this.clones.size(); ++i) {
                FakeMagispellerEntity clone = this.clones.get(i);
                if (!clone.isAlive()) {
                    this.clones.remove(i);
                    --i;
                }
            }
        }

    }

    public void makeFireParticles() {
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

                for (int i = 0; i < 75; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.FLAME, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeLifestealParticles1() {
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
                    double randomX = this.getX() - 5.0 + (double) this.random.nextInt(10);
                    double randomY = this.getY() - 5.0 + (double) this.random.nextInt(10);
                    double randomZ = this.getZ() - 5.0 + (double) this.random.nextInt(10);
                    double d0 = (this.getX() - randomX) / 4.0;
                    double d1 = (this.getY() - randomY) / 4.0;
                    double d2 = (this.getZ() - randomZ) / 4.0;
                    packet.queueParticle(ParticleTypes.POOF, false, new Vec3(randomX, randomY, randomZ), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeLifestealParticles2(Entity caught) {
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

                for (int i = 0; i < 2; ++i) {
                    packet.queueParticle(ParticleTypes.CRIT, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(0.0, 0.0, 0.0));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeLifestealParticles3() {
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

                for (int i = 0; i < 6; ++i) {
                    double randomX = this.getX() - 5.0 + (double) this.random.nextInt(10);
                    double randomY = this.getY() - 5.0 + (double) this.random.nextInt(10);
                    double randomZ = this.getZ() - 5.0 + (double) this.random.nextInt(10);
                    double d0 = (this.getX() - randomX) / 4.0;
                    double d1 = (this.getY() - randomY) / 4.0;
                    double d2 = (this.getZ() - randomZ) / 4.0;
                    packet.queueParticle(ParticleTypes.ELECTRIC_SPARK, false, new Vec3(randomX, randomY, randomZ), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeFakerParticles() {
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
                double d0;
                double d1;
                double d2;
                for (i = 0; i < 2; ++i) {
                    d0 = this.getX() - 5.0 + (double) this.random.nextInt(10);
                    d1 = this.getY() - 5.0 + (double) this.random.nextInt(10);
                    d2 = this.getZ() - 5.0 + (double) this.random.nextInt(10);
                    double d3 = (this.getX() - d0) / 4.0;
                    double d4 = (this.getY() - d1) / 4.0;
                    double d5 = (this.getZ() - d2) / 4.0;
                    packet.queueParticle(ParticleTypes.ELECTRIC_SPARK, false, new Vec3(d3, d4, d5), new Vec3(d3, d4, d5));
                }

                for (i = 0; i < 2; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.PORTAL, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeFangRunParticles() {
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

                for (int i = 0; i < 75; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.ELECTRIC_SPARK, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makePotionParticles() {
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

                for (int i = 0; i < 3; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.SWEEP_ATTACK, false, new Vec3(this.getRandomX(1.0) + (-0.5 + this.random.nextDouble()) * 0.8, this.getRandomY() - (-0.5 + this.random.nextDouble()) * 0.4, this.getRandomZ(1.0) + (-0.5 + this.random.nextDouble()) * 0.8), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeArrowParticles(Entity caught) {
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

                for (int i = 0; i < 2; ++i) {
                    packet.queueParticle(ParticleTypes.ELECTRIC_SPARK, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(0.0, 0.0, 0.0));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeCrashagerParticles1() {
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
                double d0;
                double d1;
                double d2;
                for (i = 0; i < 2; ++i) {
                    d0 = -0.5 + this.random.nextGaussian();
                    d1 = -0.5 + this.random.nextGaussian();
                    d2 = -0.5 + this.random.nextGaussian();
                    packet.queueParticle(ParticleTypes.ELECTRIC_SPARK, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 2; ++i) {
                    d0 = -0.5 + this.random.nextGaussian();
                    d1 = -0.5 + this.random.nextGaussian();
                    d2 = -0.5 + this.random.nextGaussian();
                    packet.queueParticle(ParticleTypes.CRIT, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeCrashagerParticles2(Entity caught) {
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

                int i;
                double d0;
                double d1;
                double d2;
                for (i = 0; i < 75; ++i) {
                    d0 = -0.5 + this.random.nextGaussian();
                    d1 = -0.5 + this.random.nextGaussian();
                    d2 = -0.5 + this.random.nextGaussian();
                    packet.queueParticle(ParticleTypes.ELECTRIC_SPARK, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 50; ++i) {
                    d0 = -0.5 + this.random.nextGaussian();
                    d1 = -0.5 + this.random.nextGaussian();
                    d2 = -0.5 + this.random.nextGaussian();
                    packet.queueParticle(ParticleTypes.POOF, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 5; ++i) {
                    d0 = -0.5 + this.random.nextGaussian();
                    d1 = -0.5 + this.random.nextGaussian();
                    d2 = -0.5 + this.random.nextGaussian();
                    packet.queueParticle(ParticleTypes.EXPLOSION_EMITTER, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeDispenserParticles() {
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
                double d0;
                double d1;
                double d2;
                for (i = 0; i < 5; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.ANGRY_VILLAGER, false, new Vec3(this.getRandomX(1.0), this.getRandomY() + (double) this.getEyeHeight(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 25; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.POOF, false, new Vec3(this.getRandomX(1.0), this.getRandomY() + (double) this.getEyeHeight(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeHealParticles() {
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

                for (int i = 0; i < 50; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.HEART, false, new Vec3(this.getRandomX(1.0) + (-0.5 + this.random.nextDouble()) * 2.5, this.getRandomY() + (-0.5 + this.random.nextDouble()) * 1.5, this.getRandomZ(1.0) + (-0.5 + this.random.nextDouble()) * 2.5), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeHealFailedParticles() {
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

                for (int i = 0; i < 50; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.ANGRY_VILLAGER, false, new Vec3(this.getRandomX(1.0) + (-0.5 + this.random.nextDouble()) * 2.5, this.getRandomY() + (-0.5 + this.random.nextDouble()) * 1.5, this.getRandomZ(1.0) + (-0.5 + this.random.nextDouble()) * 2.5), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeHealProgressParticles() {
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

                for (int i = 0; i < 1; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.HAPPY_VILLAGER, false, new Vec3(this.getRandomX(1.0) + (-0.5 + this.random.nextDouble()) * 2.5, this.getRandomY() + (-0.5 + this.random.nextDouble()) * 1.5, this.getRandomZ(1.0) + (-0.5 + this.random.nextDouble()) * 2.5), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeTotemParticles() {
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

                for (int i = 0; i < 50; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.TOTEM_OF_UNDYING, false, new Vec3(this.getRandomX(1.0) + (-0.5 + this.random.nextDouble()) * 2.5, this.getRandomY() + (-0.5 + this.random.nextDouble()) * 1.5, this.getRandomZ(1.0) + (-0.5 + this.random.nextDouble()) * 2.5), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public boolean hurt(DamageSource source, float amount) {
        if (this.areIllagersNearby() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            return false;
        } else {
            if (this.isFaking()) {
                this.setFaking(false);
                if (!this.clones.isEmpty()) {

                    for (FakeMagispellerEntity clone : this.clones) {
                        clone.kill();
                    }
                }
            }

            if (!source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
                amount = Math.min(amount, 20);
            }

            if (source.getEntity() instanceof CrashagerEntity && ((CrashagerEntity) source.getEntity()).getOwner() == this) {
                return false;
            } else if (source.getEntity() instanceof KaboomerEntity && ((KaboomerEntity) source.getEntity()).getOwner() == this) {
                return false;
            } else if (this.isBalloon() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
                return false;
            } else {
                if (!this.isActive() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL))
                    amount = 0;
                if (source.getEntity() instanceof LivingEntity && !this.isActive() && !this.areIllagersNearby()) {
                    this.setActive(true);
                    if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
                        this.getCurrentRaid().ticksActive = 0L;
                    }
                }

                this.lastDamageSource = source;
                return super.hurt(source, amount);
            }
        }
    }

    public void addDamageTaken(float damage) {
        this.damageTaken += damage;
    }

    @Nullable
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor p_213386_1_, DifficultyInstance p_213386_2_, MobSpawnType p_213386_3_, @Nullable SpawnGroupData p_213386_4_, @Nullable CompoundTag p_213386_5_) {
        RandomSource randomsource = p_213386_1_.getRandom();
        if (p_213386_3_ == MobSpawnType.EVENT) {
            this.setShouldDeleteItself(true);
        }

        this.populateDefaultEquipmentSlots(randomsource, p_213386_2_);
        this.populateDefaultEquipmentEnchantments(randomsource, p_213386_2_);
        return super.finalizeSpawn(p_213386_1_, p_213386_2_, p_213386_3_, p_213386_4_, p_213386_5_);
    }

    public void die(DamageSource p_37847_) {
        if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
            this.getCurrentRaid().ticksActive = 0L;
        }

        this.setAnimationState(0);
        if (p_37847_.getEntity() == null && this.getLastHurtByMob() == null && this.getTarget() == null) {
            super.die(p_37847_);
        } else {
            if (!this.level().isClientSide) {
                this.goalSelector.getRunningGoals().forEach(WrappedGoal::stop);
                this.setShakeAmount(0);
            }

            if (this.lastHurtByPlayerTime > 0) {
                this.lastHurtByPlayerTime = 10000;
            }

            this.setCustomDeath(true);
            if (this.getLastHurtByMob() == this && this.getTarget() != null) {
                this.mobToLaughAt = this.getTarget();
            } else if (this.getLastHurtByMob() != null) {
                this.mobToLaughAt = this.getLastHurtByMob();
            } else if (this.getTarget() != null) {
                this.mobToLaughAt = this.getTarget();
            } else if (p_37847_.getEntity() != null) {
                this.mobToLaughAt = p_37847_.getEntity();
            }
        }

    }

    protected void tickDeath() {
        if (!this.isCustomDeath()) {
            super.tickDeath();
        } else {
            this.clearFire();

            ++this.customDeathTime;
            if (this.customDeathTime < 60) {
                ++this.deathTime;
            }

            if (!this.level().isClientSide) {
                this.setShakeAmount(0);
            }

            if (this.customDeathTime == 60) {
                this.playSound(SoundEvents.SNOWBALL_THROW, 2.0F, 0.5F);
                this.playSound(SoundEvents.PLAYER_LEVELUP, 2.0F, 1.0F);

                for (int i = 0; i < 15; ++i) {
                    this.makeHealProgressParticles();
                }

                ItemEntity totem = EntityType.ITEM.create(this.level());

                assert totem != null;

                totem.setItem(Items.TOTEM_OF_UNDYING.getDefaultInstance());
                totem.setPos(this.getX(), this.getY(), this.getZ());
                totem.setDeltaMovement(0.0, 0.4, 0.0);
                totem.setNeverPickUp();
                totem.setUnlimitedLifetime();
                totem.noPhysics = true;
                this.level().addFreshEntity(totem);
                this.totem = totem;
            }

            if (this.customDeathTime == 80) {
                if (Config.CommonConfig.magispeller_distractEnemies.get()) {
                    List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(50.0));
                    for (Mob mob : list) {
                        mob.goalSelector.addGoal(0, new StareAtDeadMagiGoal(mob, this));
                    }
                }

                this.playSound(SoundEvents.TOTEM_USE, 2.0F, 1.0F);
                this.makeTotemParticles();
                CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.6F, 0, 30);
                this.setAnimationState(12);
                if (!this.level().isClientSide) {
                    this.setShowArms(true);
                }

                this.deathTime = 0;
                this.dead = false;
                this.setPose(Pose.STANDING);
                if (this.totem != null) {
                    this.totem.discard();
                }
            }

            if (this.customDeathTime == 110) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_LAUGH.get(), 1.0F, 1.0F);
            }

            if (this.customDeathTime >= 110 && this.mobToLaughAt != null) {
                this.lookAtWhileDead(this.mobToLaughAt, 30.0F, 30.0F);
            }

            if (this.customDeathTime == 200 && !this.level().isClientSide) {
                this.setGlowState(7);
            }

            if (this.customDeathTime == 232 && !this.level().isClientSide) {
                this.setGlowState(8);
            }

            if (this.customDeathTime == 248 && !this.level().isClientSide) {
                this.setGlowState(9);
            }

            if (this.customDeathTime >= 270 && this.customDeathTime < 290) {
                if (this.customDeathTime == 270) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_ESCAPE.get(), 2.0F, 1.0F);
                }

                if (!this.level().isClientSide) {
                    this.setGlowState(this.random.nextBoolean() ? 0 : 3);
                }
            }

            if (this.customDeathTime == 290 && !this.level().isClientSide) {
                this.setGlowState(3);
            }

            if (this.customDeathTime >= 300) {
                this.playSound(SoundEvents.ILLUSIONER_MIRROR_MOVE, 1.0F, 1.0F);

                if (lastDamageSource.getDirectEntity() instanceof MagiFireballEntity) {
                    shouldDropDisc = true;
                }

                super.die(lastDamageSource != null ? lastDamageSource : this.damageSources().generic());
                if (!this.level().isClientSide()) {
                    this.level().broadcastEntityEvent(this, (byte) 60);
                    this.remove(RemovalReason.KILLED);
                }
            }
        }

    }

    public boolean isDead() {
        return this.dead;
    }

    protected void dropAllDeathLoot(DamageSource source) {
        if (this.shouldDropLoot() && this.level().getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT) && this.lastHurtByPlayerTime > 0 && shouldDropDisc) {
            this.level().addFreshEntity(new ItemEntity(this.level(), this.getX(), this.getY(), this.getZ(), new ItemStack(ItemRegisterer.MAGISPELLER_DISC.get())));
        }
        super.dropAllDeathLoot(source);
    }

    public void lookAtWhileDead(Entity p_21392_, float p_21393_, float p_21394_) {
        double d0 = p_21392_.getX() - this.getX();
        double d2 = p_21392_.getZ() - this.getZ();
        double d1;
        if (p_21392_ instanceof LivingEntity livingentity) {
            d1 = livingentity.getEyeY() - this.getEyeY();
        } else {
            d1 = (p_21392_.getBoundingBox().minY + p_21392_.getBoundingBox().maxY) / 2.0 - this.getEyeY();
        }

        double d3 = Math.sqrt(d0 * d0 + d2 * d2);
        float f = (float) (Mth.atan2(d2, d0) * 57.2957763671875) - 90.0F;
        float f1 = (float) (-(Mth.atan2(d1, d3) * 57.2957763671875));
        this.setXRot(this.rotlerp(this.getXRot(), f1, p_21394_));
        this.setYRot(this.rotlerp(this.getYRot(), f, p_21393_));
        this.yHeadRot = this.rotlerp(this.getYRot(), f, p_21393_);
    }

    private float rotlerp(float p_21377_, float p_21378_, float p_21379_) {
        float f = Mth.wrapDegrees(p_21378_ - p_21377_);
        if (f > p_21379_) {
            f = p_21379_;
        }

        if (f < -p_21379_) {
            f = -p_21379_;
        }

        return p_21377_ + f;
    }

    public boolean doHurtTarget(Entity p_70652_1_) {
        if (this.isFaking() && !this.level().isClientSide && this.random.nextInt(3) != 0) {
            this.teleportTowards(p_70652_1_);
        }

        return (!this.isFaking() || this.waitTimeFaker >= 20) && super.doHurtTarget(p_70652_1_);
    }

    public boolean shouldShowArms() {
        return this.entityData.get(SHOW_ARMS);
    }

    public void setShowArms(boolean showArms) {
        this.entityData.set(SHOW_ARMS, showArms);
    }

    protected void createFangs(boolean particleOrReal) {
        if (this.getTarget() != null) {
            LivingEntity livingentity = this.getTarget();
            double d0 = Math.min(livingentity.getY(), this.getY());
            double d1 = Math.max(livingentity.getY(), this.getY()) + 1.0;
            float f = (float) Mth.atan2(livingentity.getZ() - this.getZ(), livingentity.getX() - this.getX());

            for (int l = 0; l < 16; ++l) {
                double d2 = 1.25 * (double) (l + 1);
                if (particleOrReal) {
                    this.createSpellEntity(this.getX() + (double) Mth.cos(f) * d2, this.getZ() + (double) Mth.sin(f) * d2, d0, d1, f, l);
                } else {
                    this.createSpellParticles(this.getX() + (double) Mth.cos(f) * d2, this.getZ() + (double) Mth.sin(f) * d2, d0, d1);
                }
            }
        }

    }

    private void createSpellEntity(double p_190876_1_, double p_190876_3_, double p_190876_5_, double p_190876_7_, float p_190876_9_, int p_190876_10_) {
        BlockPos blockpos = BlockPos.containing(p_190876_1_, p_190876_7_, p_190876_3_);
        boolean flag = false;
        double d0 = 0.0;

        do {
            BlockPos blockpos1 = blockpos.below();
            BlockState blockstate = this.level().getBlockState(blockpos1);
            if (blockstate.isFaceSturdy(this.level(), blockpos1, Direction.UP)) {
                if (!this.level().isEmptyBlock(blockpos)) {
                    BlockState blockstate1 = this.level().getBlockState(blockpos);
                    VoxelShape voxelshape = blockstate1.getCollisionShape(this.level(), blockpos);
                    if (!voxelshape.isEmpty()) {
                        d0 = voxelshape.max(Axis.Y);
                    }
                }

                flag = true;
                break;
            }

            blockpos = blockpos.below();
        } while (blockpos.getY() >= Mth.floor(p_190876_5_) - 1);

        if (flag) {
            EvokerFangs fangs = new EvokerFangs(this.level(), p_190876_1_, (double) blockpos.getY() + d0, p_190876_3_, p_190876_9_, p_190876_10_, this);
            fangs.setSilent(true);
            this.level().addFreshEntity(fangs);
        }

    }

    private void createSpellParticles(double p_190876_1_, double p_190876_3_, double p_190876_5_, double p_190876_7_) {
        BlockPos blockpos = BlockPos.containing(p_190876_1_, p_190876_7_, p_190876_3_);
        boolean flag = false;
        double dthing = 0.0;

        do {
            BlockPos blockpos1 = blockpos.below();
            BlockState blockstate = this.level().getBlockState(blockpos1);
            if (blockstate.isFaceSturdy(this.level(), blockpos1, Direction.UP)) {
                if (!this.level().isEmptyBlock(blockpos)) {
                    BlockState blockstate1 = this.level().getBlockState(blockpos);
                    VoxelShape voxelshape = blockstate1.getCollisionShape(this.level(), blockpos);
                    if (!voxelshape.isEmpty()) {
                        dthing = voxelshape.max(Axis.Y);
                    }
                }

                flag = true;
                break;
            }

            blockpos = blockpos.below();
        } while (blockpos.getY() >= Mth.floor(p_190876_5_) - 1);

        if (flag && !this.level().isClientSide) {
            Iterator<ServerPlayer> var25 = ((ServerLevel) this.level()).players().iterator();

            while (true) {
                ServerPlayer serverPlayer;
                do {
                    if (!var25.hasNext()) {
                        return;
                    }

                    serverPlayer = var25.next();
                } while (!(serverPlayer.distanceToSqr(this) < 4096.0));

                ParticlePacket packet = new ParticlePacket();

                for (int i = 0; i < 8; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.CRIT, false, new Vec3(p_190876_1_ + (double) this.random.nextFloat(), (double) blockpos.getY() + dthing, p_190876_3_ + (double) this.random.nextFloat()), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public boolean ignoreExplosion() {
        return this.kaboomerCooldown > 280;
    }

    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_CELEBRATE.get();
    }

    protected SoundEvent getAmbientSound() {
        return !this.isFaking() ? IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_AMBIENT.get() : IllageAndSpillageSoundEvents.ENTITY_FAKER_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_DEATH.get();
    }

    public boolean areIllagersNearby() {
        return this.entityData.get(NEARBY_ILLAGERS) && !this.isActive();
    }

    public void setIllagersNearby(boolean illagersNearby) {
        this.entityData.set(NEARBY_ILLAGERS, illagersNearby);
    }

    public boolean shouldRemoveItself() {
        return this.entityData.get(SHOULD_DELETE_ITSELF);
    }

    public void setShouldDeleteItself(boolean shouldDelete) {
        this.entityData.set(SHOULD_DELETE_ITSELF, shouldDelete);
    }

    public boolean isActive() {
        return this.entityData.get(ACTIVE);
    }

    public void setActive(boolean active) {
        this.entityData.set(ACTIVE, active);
    }

    public boolean isPersistenceRequired() {
        return !Config.CommonConfig.ULTIMATE_NIGHTMARE.get();
    }

    public boolean canBeAffected(MobEffectInstance p_70687_1_) {
        return p_70687_1_.getEffect() != MobEffects.MOVEMENT_SLOWDOWN && super.canBeAffected(p_70687_1_);
    }

    protected void populateDefaultEquipmentSlots(RandomSource random, DifficultyInstance p_180481_1_) {
        this.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.IRON_AXE));
        this.setDropChance(EquipmentSlot.MAINHAND, 0.0F);
        this.setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(Items.CROSSBOW));
        this.setDropChance(EquipmentSlot.OFFHAND, 0.0F);
    }

    public boolean doesAttackMeetNormalRequirements() {
        return this.getAttackType() == 0 && !this.areIllagersNearby() && this.getTarget() != null && this.hasLineOfSight(this.getTarget()) && this.isActive() && !this.isFaking() && !this.isRidingIllusion() && !this.isBalloon();
    }

    public boolean canAttackBackUp() {
        return this.getAttackType() == 0 || this.getAttackType() == 1 || this.getAttackType() == 2 && this.getAttackTicks() < 31 || this.getAttackType() == 4 || this.getAttackType() == 7 || this.getAttackType() == 9;
    }

    public boolean isBalloon() {
        return this.entityData.get(BALLOON);
    }

    public void setBalloon(boolean balloon) {
        this.entityData.set(BALLOON, balloon);
        if (balloon) {
            this.setNoGravity(true);
        } else if (this.isNoGravity()) {
            this.setNoGravity(false);
        }

    }

    public boolean isTargetLowEnoughForGround() {
        return this.getTarget() != null && !(this.getTarget().getY() > this.getY() + 3.0);
    }

    private boolean teleportTowards(Entity p_70816_1_) {
        Vec3 vector3d = new Vec3(this.getX() - p_70816_1_.getX(), this.getY(0.5) - p_70816_1_.getEyeY(), this.getZ() - p_70816_1_.getZ());
        vector3d = vector3d.normalize();
        double d1 = this.getX() + (this.random.nextDouble() - 0.5) * 8.0 - vector3d.x * 16.0;
        double d2 = this.getY() + (double) (this.random.nextInt(16) - 8) - vector3d.y * 16.0;
        double d3 = this.getZ() + (this.random.nextDouble() - 0.5) * 8.0 - vector3d.z * 16.0;
        return this.teleport(d1, d2, d3);
    }

    private boolean teleport(double p_70825_1_, double p_70825_3_, double p_70825_5_) {
        BlockPos.MutableBlockPos blockpos$mutable = new BlockPos.MutableBlockPos(p_70825_1_, p_70825_3_, p_70825_5_);

        while (blockpos$mutable.getY() > 0 && !this.level().getBlockState(blockpos$mutable).blocksMotion()) {
            blockpos$mutable.move(Direction.DOWN);
        }

        BlockState blockstate = this.level().getBlockState(blockpos$mutable);
        boolean flag = blockstate.blocksMotion();
        boolean flag1 = blockstate.getFluidState().is(FluidTags.WATER);
        if (flag && !flag1) {
            EntityTeleportEvent.EnderEntity event = ForgeEventFactory.onEnderTeleport(this, p_70825_1_, p_70825_3_, p_70825_5_);
            if (event.isCanceled()) {
                return false;
            } else {
                boolean flag2 = this.randomTeleport(event.getTargetX(), event.getTargetY(), event.getTargetZ(), true);
                if (flag2 && !this.isSilent()) {
                    this.level().playSound(null, this.xo, this.yo, this.zo, SoundEvents.ENDERMAN_TELEPORT, this.getSoundSource(), 1.0F, 1.0F);
                    this.playSound(SoundEvents.ENDERMAN_TELEPORT, 1.0F, 1.0F);
                }

                return flag2;
            }
        } else {
            return false;
        }
    }

    public void distractAttackers(LivingEntity entity) {
        List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(100.0));

        for (Mob attacker : list) {
            if (attacker.getLastHurtByMob() == this) {
                attacker.setLastHurtByMob(entity);
            }

            if (attacker.getTarget() == this) {
                attacker.setTarget(entity);
            }
        }

    }

    public void fireArrow(LivingEntity p_82196_1_, float p_82196_2_, float inaccuracy) {
        AbstractArrow abstractarrowentity = this.getArrow(Items.BOW.getDefaultInstance(), p_82196_2_);
        if (this.getMainHandItem().getItem() instanceof BowItem) {
            abstractarrowentity = ((BowItem) this.getMainHandItem().getItem()).customArrow(abstractarrowentity);
        }

        double d0 = p_82196_1_.getX() - this.getX();
        double d1 = p_82196_1_.getY(0.3333333333333333) - abstractarrowentity.getY() - (double) p_82196_1_.getBbHeight() / 2.0;
        double d2 = p_82196_1_.getZ() - this.getZ();
        double d3 = Mth.sqrt((float) (d0 * d0 + d2 * d2));
        abstractarrowentity.setBaseDamage(2.5);
        float speed;
        if (this.distanceToSqr(p_82196_1_) > 22.5) {
            speed = 2.5F;
        } else {
            speed = (float) (this.distanceToSqr(p_82196_1_) / 9.0);
        }

        abstractarrowentity.shoot(d0, d1 + d3 * 0.20000000298023224, d2, speed, inaccuracy);
        this.level().addFreshEntity(abstractarrowentity);
    }

    protected AbstractArrow getArrow(ItemStack p_213624_1_, float p_213624_2_) {
        return ProjectileUtil.getMobArrow(this, p_213624_1_, p_213624_2_);
    }

    public Component getName() {
        return !this.hasCustomName() && this.isFaking() ? ModEntityTypes.Faker.get().getDescription() : super.getName();
    }

    public void setAnimationState(int input) {
        this.entityData.set(ANIMATION_STATE, input);
    }

    public AnimationState getAnimationState(String input) {
        if (Objects.equals(input, "fireball")) {
            return this.fireballAnimationState;
        } else if (Objects.equals(input, "lifesteal")) {
            return this.lifestealAnimationState;
        } else if (Objects.equals(input, "fakers")) {
            return this.fakersAnimationState;
        } else if (Objects.equals(input, "vexes")) {
            return this.vexesAnimationState;
        } else if (Objects.equals(input, "fangrun")) {
            return this.fangrunAnimationState;
        } else if (Objects.equals(input, "potions")) {
            return this.potionsAnimationState;
        } else if (Objects.equals(input, "crossbowspin")) {
            return this.crossbowspinAnimationState;
        } else if (Objects.equals(input, "crashager")) {
            return this.crashagerAnimationState;
        } else if (Objects.equals(input, "dispenser")) {
            return this.dispenserAnimationState;
        } else if (Objects.equals(input, "knockback")) {
            return this.knockbackAnimationState;
        } else if (Objects.equals(input, "kaboomer")) {
            return this.kaboomerAnimationState;
        } else {
            return Objects.equals(input, "death") ? this.deathAnimationState : new AnimationState();
        }
    }

    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                case 0 -> this.stopAllAnimationStates();
                case 1 -> {
                    this.stopAllAnimationStates();
                    this.fireballAnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.stopAllAnimationStates();
                    this.lifestealAnimationState.start(this.tickCount);
                }
                case 3 -> {
                    this.stopAllAnimationStates();
                    this.fakersAnimationState.start(this.tickCount);
                }
                case 4 -> {
                    this.stopAllAnimationStates();
                    this.vexesAnimationState.start(this.tickCount);
                }
                case 5 -> {
                    this.stopAllAnimationStates();
                    this.fangrunAnimationState.start(this.tickCount);
                }
                case 6 -> {
                    this.stopAllAnimationStates();
                    this.potionsAnimationState.start(this.tickCount);
                }
                case 7 -> {
                    this.stopAllAnimationStates();
                    this.crossbowspinAnimationState.start(this.tickCount);
                }
                case 8 -> {
                    this.stopAllAnimationStates();
                    this.crashagerAnimationState.start(this.tickCount);
                }
                case 9 -> {
                    this.stopAllAnimationStates();
                    this.dispenserAnimationState.start(this.tickCount);
                }
                case 10 -> {
                    this.stopAllAnimationStates();
                    this.knockbackAnimationState.start(this.tickCount);
                }
                case 11 -> {
                    this.stopAllAnimationStates();
                    this.kaboomerAnimationState.start(this.tickCount);
                }
                case 12 -> {
                    this.stopAllAnimationStates();
                    this.deathAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    public boolean isMobNotInCreativeMode(Entity entity) {
        if (!(entity instanceof Player)) {
            return true;
        } else {
            return !((Player) entity).isCreative() && !(entity).isSpectator();
        }
    }

    public void stopAllAnimationStates() {
        this.fireballAnimationState.stop();
        this.lifestealAnimationState.stop();
        this.fakersAnimationState.stop();
        this.vexesAnimationState.stop();
        this.fangrunAnimationState.stop();
        this.potionsAnimationState.stop();
        this.crossbowspinAnimationState.stop();
        this.crashagerAnimationState.stop();
        this.dispenserAnimationState.stop();
        this.knockbackAnimationState.stop();
        this.kaboomerAnimationState.stop();
        this.deathAnimationState.stop();
    }

    static {
        NEARBY_ILLAGERS = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        SHOULD_DELETE_ITSELF = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        ACTIVE = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        SHOW_ARMS = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        GLOW_STATE = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.INT);
        SHAKE_AMOUNT = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.INT);
        FAKING = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        ARROW_STATE = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.INT);
        WAVING_ARMS = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        BALLOON = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        DEATH = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        ANIMATION_STATE = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.INT);
        ATTACK_TYPE = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.INT);
        ATTACK_TICKS = SynchedEntityData.defineId(MagispellerEntity.class, EntityDataSerializers.INT);
    }

    class KaboomerGoal extends Goal {
        public KaboomerGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.getTarget() != null && MagispellerEntity.this.getAttackType() == 0 && !MagispellerEntity.this.isFaking() && !MagispellerEntity.this.areIllagersNearby() && MagispellerEntity.this.isActive() && !MagispellerEntity.this.isBalloon() && MagispellerEntity.this.getVehicle() == null && MagispellerEntity.this.random.nextInt(10) == 0 && MagispellerEntity.this.kaboomerCooldown < 1 && !MagispellerEntity.this.isRidingIllusion();
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(11);
            EntityUtil.mobFollowingSound(level(), MagispellerEntity.this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_KABOOMER.get(), 3.0F, 1.0F, false);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.KABOOMER_ATTACK);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 43;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
            }

            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setGlowState(0);
                MagispellerEntity.this.setShakeAmount(0);
            }

            if (MagispellerEntity.this.getTarget() != null) {
                KaboomerEntity kaboomer = null;
                if (!MagispellerEntity.this.level().isClientSide) {
                    kaboomer = ModEntityTypes.Kaboomer.get().create(MagispellerEntity.this.level());
                }

                if (kaboomer != null) {
                    kaboomer.setPos(MagispellerEntity.this.getX(), MagispellerEntity.this.getY(), MagispellerEntity.this.getZ());
                    kaboomer.setTarget(MagispellerEntity.this.getTarget());
                    kaboomer.setOwner(MagispellerEntity.this);
                    if (MagispellerEntity.this.getTeam() != null) {
                        MagispellerEntity.this.level().getScoreboard().addPlayerToTeam(kaboomer.getStringUUID(), MagispellerEntity.this.level().getScoreboard().getPlayerTeam(MagispellerEntity.this.getTeam().getName()));
                    }

                    MagispellerEntity.this.level().addFreshEntity(kaboomer);
                    MagispellerEntity.this.startRiding(kaboomer);
                    kaboomer.teleport(MagispellerEntity.this.getTarget());
                }
            }

            MagispellerEntity.this.kaboomerCooldown = 400;
        }
    }

    class HealGoal extends Goal {
        public HealGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.getAttackType() == 0 && !MagispellerEntity.this.isFaking() && !MagispellerEntity.this.areIllagersNearby() && MagispellerEntity.this.healCooldown < 1 && MagispellerEntity.this.isActive() && MagispellerEntity.this.random.nextInt(14) == 0 && MagispellerEntity.this.getHealth() < MagispellerEntity.this.getMaxHealth() && !MagispellerEntity.this.hasEffect(MobEffects.REGENERATION) && !MagispellerEntity.this.isBalloon() && !MagispellerEntity.this.isRidingIllusion();
        }

        public void start() {
            MagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_HEAL.get(), 2.0F, 1.0F);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.HEAL_ATTACK);
            MagispellerEntity.this.gotHealed = true;
            MagispellerEntity.this.damageTaken = 0.0F;
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
                MagispellerEntity.this.setWavingArms(true);
                MagispellerEntity.this.setGlowState(6);
                MagiHealEntity healRing = ModEntityTypes.MagiHeal.get().create(MagispellerEntity.this.level());

                assert healRing != null;

                healRing.setPos(MagispellerEntity.this.getX(), MagispellerEntity.this.getY(), MagispellerEntity.this.getZ());
                healRing.setOwner(MagispellerEntity.this);
                MagispellerEntity.this.level().addFreshEntity(healRing);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 140 && MagispellerEntity.this.gotHealed;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
                MagispellerEntity.this.setWavingArms(false);
                MagispellerEntity.this.setGlowState(0);
            }

            if (MagispellerEntity.this.gotHealed) {
                MagispellerEntity.this.makeHealParticles();
                MagispellerEntity.this.heal(8.0F);
                MagispellerEntity.this.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 200, 3));
            } else if (!MagispellerEntity.this.isBalloon()) {
                MagispellerEntity.this.makeHealFailedParticles();
                MagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_HEAL_INTERRUPT.get(), 2.0F, 1.0F);
            }

            MagispellerEntity.this.healCooldown = 200;
        }
    }

    class DispenserGoal extends Goal {
        public DispenserGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.random.nextInt(8) == 0 && MagispellerEntity.this.dispenserCooldown < 1;
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(9);
            MagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_DISPENSER.get(), 2.0F, 1.0F);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.DISPENSER_ATTACK);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 40;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
                MagispellerEntity.this.setGlowState(0);
            }

            MagispellerEntity.this.makeDispenserParticles();
            MagispellerEntity.this.dispenserCooldown = 300;
        }
    }

    class CrashagerGoal extends Goal {
        public CrashagerGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.getVehicle() == null && MagispellerEntity.this.random.nextInt(12) == 0 && MagispellerEntity.this.crashagerCooldown < 1 && MagispellerEntity.this.isTargetLowEnoughForGround();
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(8);
            EntityUtil.mobFollowingSound(level(), MagispellerEntity.this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_RAVAGER.get(), 2.0F, 1.0F, false);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.CRASHAGER_ATTACK);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
                MagispellerEntity.this.setShakeAmount(30);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 71 || MagispellerEntity.this.isRidingIllusion();
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
            }

            MagispellerEntity.this.crashagerCooldown = 160;
        }
    }

    class CrossbowSpinGoal extends Goal {
        public CrossbowSpinGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.random.nextInt(16) == 0 && MagispellerEntity.this.crossbowSpinCooldown < 1;
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(7);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.CROSSBOWSPIN_ATTACK);
            MagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_CROSSBOWSPIN.get(), 2.0F, 1.0F);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 133;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
                MagispellerEntity.this.setArrowState(0);
            }

            MagispellerEntity.this.crossbowSpinCooldown = 300;
        }
    }

    class ThrowPotionsGoal extends Goal {
        public ThrowPotionsGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.random.nextInt(12) == 0 && MagispellerEntity.this.throwPotionsCooldown < 1 && distanceToSqr(getTarget()) < 36 && MagispellerEntity.this.isTargetLowEnoughForGround() && !(Objects.requireNonNull(MagispellerEntity.this.getTarget())).hasEffect(MobEffects.MOVEMENT_SLOWDOWN);
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(6);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.POTIONS_ATTACK);
            MagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_POTIONS_START.get(), 2.0F, 1.0F);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 68;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
            }

            MagispellerEntity.this.throwPotionsCooldown = 100;
        }
    }

    class FangRunGoal extends Goal {
        public FangRunGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.random.nextInt(10) == 0 && MagispellerEntity.this.fangrunCooldown < 1 && distanceToSqr(getTarget()) < 256.0 && MagispellerEntity.this.isTargetLowEnoughForGround();
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(5);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.FANGRUN_ATTACK);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 109;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
                MagispellerEntity.this.setGlowState(0);
                MagispellerEntity.this.setShakeAmount(0);
            }

            MagispellerEntity.this.fangrunCooldown = 160;
        }
    }

    class SummonVexesGoal extends Goal {
        public SummonVexesGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.random.nextInt(8) == 0 && MagispellerEntity.this.vexesCooldown < 1;
        }

        public void start() {
            MagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SUMMON.get(), 1.0F, 1.0F);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.VEXES_ATTACK);
            MagispellerEntity.this.setAnimationState(4);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 40;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
            }

            MagispellerEntity.this.vexesCooldown = 900;
        }
    }

    class FakersGoal extends Goal {
        public FakersGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.random.nextInt(16) == 0 && MagispellerEntity.this.getHealth() < MagispellerEntity.this.getMaxHealth() / 2.0F && MagispellerEntity.this.fakersCooldown < 1 && MagispellerEntity.this.isTargetLowEnoughForGround();
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(3);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.FAKERS_ATTACK);
            EntityUtil.mobFollowingSound(level(), MagispellerEntity.this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_PREPARE_FAKERS.get(), 2.0F, 1.0F, false);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 51;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
                MagispellerEntity.this.setGlowState(0);
                MagispellerEntity.this.setShakeAmount(0);
                MagispellerEntity.this.setFaking(true);
            }

            if (MagispellerEntity.this.getTarget() != null) {
                if (!MagispellerEntity.this.level().isClientSide) {
                    int i;
                    for (i = 0; i < 11; ++i) {
                        FakeMagispellerEntity clone = ModEntityTypes.Faker.get().create(MagispellerEntity.this.level());

                        assert clone != null;

                        clone.setPos(MagispellerEntity.this.position().x, MagispellerEntity.this.position().y, MagispellerEntity.this.position().z);
                        clone.setTarget(MagispellerEntity.this.getTarget());
                        clone.setItemSlot(EquipmentSlot.MAINHAND, MagispellerEntity.this.getItemBySlot(EquipmentSlot.MAINHAND));
                        clone.setItemSlot(EquipmentSlot.OFFHAND, MagispellerEntity.this.getItemBySlot(EquipmentSlot.OFFHAND));
                        clone.setItemSlot(EquipmentSlot.HEAD, MagispellerEntity.this.getItemBySlot(EquipmentSlot.HEAD));
                        clone.setItemSlot(EquipmentSlot.CHEST, MagispellerEntity.this.getItemBySlot(EquipmentSlot.CHEST));
                        clone.setItemSlot(EquipmentSlot.LEGS, MagispellerEntity.this.getItemBySlot(EquipmentSlot.LEGS));
                        clone.setItemSlot(EquipmentSlot.FEET, MagispellerEntity.this.getItemBySlot(EquipmentSlot.FEET));
                        clone.setDropChance(EquipmentSlot.MAINHAND, 0.0F);
                        clone.setDropChance(EquipmentSlot.OFFHAND, 0.0F);
                        clone.setDropChance(EquipmentSlot.HEAD, 0.0F);
                        clone.setDropChance(EquipmentSlot.CHEST, 0.0F);
                        clone.setDropChance(EquipmentSlot.LEGS, 0.0F);
                        clone.setDropChance(EquipmentSlot.FEET, 0.0F);
                        clone.setHealth(MagispellerEntity.this.getHealth());
                        clone.setOwner(MagispellerEntity.this);
                        if (MagispellerEntity.this.hasCustomName()) {
                            clone.setCustomName(MagispellerEntity.this.getCustomName());
                        }

                        if (MagispellerEntity.this.getTeam() != null) {
                            MagispellerEntity.this.level().getScoreboard().addPlayerToTeam(clone.getStringUUID(), MagispellerEntity.this.level().getScoreboard().getPlayerTeam(MagispellerEntity.this.getTeam().getName()));
                        }

                        clone.setLeftHanded(MagispellerEntity.this.isLeftHanded());
                        MagispellerEntity.this.level().addFreshEntity(clone);
                        clone.tryToTeleportToEntity(MagispellerEntity.this.getTarget());
                        MagispellerEntity.this.clones.add(clone);
                    }

                    for (i = 0; i < 64; ++i) {
                        if (MagispellerEntity.this.teleportTowards(MagispellerEntity.this.getTarget())) {
                            break;
                        }
                    }
                }

                MagispellerEntity.this.distractAttackers(MagispellerEntity.this.clones.get(MagispellerEntity.this.random.nextInt(MagispellerEntity.this.clones.size())));
            }

            MagispellerEntity.this.waitTimeFaker = 20;
            MagispellerEntity.this.fakersCooldown = 200;
        }
    }

    class LifestealGoal extends Goal {
        public LifestealGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.random.nextInt(10) == 0 && MagispellerEntity.this.lifestealCooldown < 1 && distanceToSqr(getTarget()) < 144.0;
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(2);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.LIFESTEAL_ATTACK);
            EntityUtil.mobFollowingSound(level(), MagispellerEntity.this, IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_LIFESTEAL_START.get(), 2.0F, 1.0F, false);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 139;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
                MagispellerEntity.this.setGlowState(0);
                MagispellerEntity.this.setShakeAmount(0);
            }

            MagispellerEntity.this.lifestealCooldown = 160;
        }
    }

    class ShootFireballGoal extends Goal {
        public ShootFireballGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.random.nextInt(16) == 0 && MagispellerEntity.this.fireballCooldown < 1;
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(1);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.FIREBALL_ATTACK);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 70;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
            }

            MagispellerEntity.this.setLeftHanded(false);
            MagispellerEntity.this.fireballCooldown = 200;
        }
    }

    class KnockbackGoal extends Goal {
        public KnockbackGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return MagispellerEntity.this.doesAttackMeetNormalRequirements() && MagispellerEntity.this.getTarget() != null && (double) MagispellerEntity.this.distanceTo(MagispellerEntity.this.getTarget()) < 3.0;
        }

        public void start() {
            MagispellerEntity.this.setAnimationState(10);
            MagispellerEntity.this.setAttackType(MagispellerEntity.this.KNOCKBACK_ATTACK);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getAttackTicks() <= 14;
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }

        public void stop() {
            MagispellerEntity.this.setAttackTicks(0);
            MagispellerEntity.this.setAttackType(0);
            MagispellerEntity.this.setAnimationState(0);
            if (!MagispellerEntity.this.level().isClientSide) {
                MagispellerEntity.this.setShowArms(false);
            }

        }
    }

    class StareAtTargetGoal extends Goal {
        public StareAtTargetGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public boolean canUse() {
            return MagispellerEntity.this.getTarget() != null && (!MagispellerEntity.this.isActive() || MagispellerEntity.this.isBalloon()) && !MagispellerEntity.this.isFaking();
        }

        public boolean canContinueToUse() {
            return MagispellerEntity.this.getTarget() != null && (!MagispellerEntity.this.isActive() || MagispellerEntity.this.isBalloon()) && !MagispellerEntity.this.isFaking();
        }

        public void tick() {
            MagispellerEntity.this.getNavigation().stop();
            if (MagispellerEntity.this.getTarget() != null) {
                MagispellerEntity.this.getLookControl().setLookAt(MagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            MagispellerEntity.this.navigation.stop();
        }
    }
}

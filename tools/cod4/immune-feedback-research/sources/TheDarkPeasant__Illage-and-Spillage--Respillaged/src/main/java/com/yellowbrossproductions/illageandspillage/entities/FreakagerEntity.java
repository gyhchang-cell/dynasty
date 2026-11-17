package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.client.sound.BossMusicPlayer;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.goal.WatchBossIntroGoal;
import com.yellowbrossproductions.illageandspillage.entities.projectile.*;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.particle.ParticleRegisterer;
import com.yellowbrossproductions.illageandspillage.util.*;
import net.minecraft.core.BlockPos;
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
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.Difficulty;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.memory.MemoryModuleType;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Ravager;
import net.minecraft.world.entity.monster.warden.AngerLevel;
import net.minecraft.world.entity.monster.warden.Warden;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import javax.annotation.Nullable;
import java.util.*;

public class FreakagerEntity extends AbstractIllager implements ICanBeAnimated {
    public ServerBossEvent bossEvent;
    private static final EntityDataAccessor<Boolean> SHOULD_DELETE_ITSELF;
    private static final EntityDataAccessor<Boolean> NEARBY_ILLAGERS;
    private static final EntityDataAccessor<Boolean> ACTIVE;
    private static final EntityDataAccessor<Integer> ANIMATION_STATE;
    private static final EntityDataAccessor<Boolean> SHOW_ARMS;
    private static final EntityDataAccessor<Boolean> SHOW_VILLAGER;
    private static final EntityDataAccessor<Integer> VILLAGER_FACE;
    private static final EntityDataAccessor<Integer> FREAKAGER_FACE = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Integer> VILLAGER_SHAKE_MULTIPLIER = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> PHASED_OUT = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> SCYTHE;
    private int introTicks;
    public AnimationState laughAnimationState = new AnimationState();
    public AnimationState bombsAnimationState = new AnimationState();
    public AnimationState minionsAnimationState = new AnimationState();
    public AnimationState intro1AnimationState = new AnimationState();
    public AnimationState intro2AnimationState = new AnimationState();
    public AnimationState intro3AnimationState = new AnimationState();
    public AnimationState axesStartAnimationState = new AnimationState();
    public AnimationState axesNormalAnimationState = new AnimationState();
    public AnimationState angryAxesAnimationState = new AnimationState();
    public AnimationState potionsAnimationState = new AnimationState();
    public AnimationState scytheAnimationState = new AnimationState();
    public AnimationState catchAnimationState = new AnimationState();
    public AnimationState trickortreatAnimationState = new AnimationState();
    public AnimationState anticheeseAnimationState = new AnimationState();
    public AnimationState phaseAnimationState = new AnimationState();
    public int attackType;
    private int attackTicks;
    private int attackCooldown;
    private static final int BOMBS_ATTACK = 1;
    private static final int AXES_ATTACK = 2;
    private static final int ANGRY_AXES_ATTACK = 3;
    private static final int POTIONS_ATTACK = 4;
    private static final int SCYTHE_ATTACK = 5;
    private static final int TRICKORTREAT_ATTACK = 6;
    private static final int MINIONS_ATTACK = 7;
    public static final int ANTICHEESE_ATTACK = 8;
    private int bombsCooldown;
    private int minionsCooldown;
    private int axesCooldown;
    private int potionsCooldown;
    private int scytheCooldown;
    private int trickOrTreatCooldown;
    private double potionThrowDistance;
    public boolean waitingForScythe;
    public int catchTicks;
    private final List<TrickOrTreatEntity> treats = new ArrayList<>();
    private LivingEntity entityToStareAt;
    public int customDeathTime;
    private int stuckTime;

    public FreakagerEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 20;
        bossEvent = (ServerBossEvent) (new ServerBossEvent(this.getDisplayName(), BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.PROGRESS)).setDarkenScreen(Config.CommonConfig.bosses_darken_sky.get());
        bossEvent.setVisible(false);
        this.getAttribute(Attributes.MAX_HEALTH).setBaseValue(Config.CommonConfig.freakager_health.get());
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

    @Override
    protected void customServerAiStep() {
        super.customServerAiStep();
        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());
    }

    @Override
    public boolean canBeAffected(MobEffectInstance effectInstance) {
        return effectInstance.getEffect() != EffectRegisterer.MUTATION.get() && super.canBeAffected(effectInstance);
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new TrickOrTreatGoal());
        this.goalSelector.addGoal(0, new ScytheGoal());
        this.goalSelector.addGoal(0, new PotionsGoal());
        this.goalSelector.addGoal(0, new AngryAxesGoal());
        this.goalSelector.addGoal(0, new AxesGoal());
        this.goalSelector.addGoal(0, new ThrowBombsGoal());
        this.goalSelector.addGoal(0, new ThrowMinionsGoal());
        this.goalSelector.addGoal(0, new AnticheeseGoal());
        this.goalSelector.addGoal(0, new IntroGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new AlwaysWatchTargetGoal());
        this.goalSelector.addGoal(2, new Raider.HoldGroundAttackGoal(this, 10.0F));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true).setUnseenMemoryTicks(300));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false).setUnseenMemoryTicks(300));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true).setUnseenMemoryTicks(300));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 1).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(SHOULD_DELETE_ITSELF, false);
        this.entityData.define(NEARBY_ILLAGERS, false);
        this.entityData.define(ACTIVE, false);
        this.entityData.define(ANIMATION_STATE, 0);
        this.entityData.define(SHOW_ARMS, false);
        this.entityData.define(SHOW_VILLAGER, false);
        this.entityData.define(VILLAGER_FACE, 0);
        this.entityData.define(FREAKAGER_FACE, 0);
        this.entityData.define(VILLAGER_SHAKE_MULTIPLIER, 0);
        this.entityData.define(PHASED_OUT, false);
        this.entityData.define(SCYTHE, false);
    }

    public void addAdditionalSaveData(CompoundTag p_37870_) {
        super.addAdditionalSaveData(p_37870_);
        if (this.isActive()) {
            p_37870_.putBoolean("active", true);
        }
    }

    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.bossEvent.setName(this.getDisplayName());
        this.setActive(tag.getBoolean("active"));
        if (tag.contains("Health", 99)) {
            this.entityData.set(DATA_HEALTH_ID, Mth.clamp(tag.getFloat("Health"), 0.0F, this.getMaxHealth()));
        }
    }

    public void setHealth(float p_21154_) {
        float healthValue = p_21154_ - this.getHealth();
        if (healthValue > 0 || (!this.areIllagersNearby() && this.isActive() && !this.isPhasedOut() && (this.ridingRideableMob() || this.level().getEntitiesOfClass(RagnoEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == this && predicate.isAlive()).isEmpty())) || healthValue <= -1000000000000.0F) {
            super.setHealth(p_21154_);
        }
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public boolean canAttack(LivingEntity p_186270_) {
        return (!(p_186270_ instanceof Player) || this.level().getDifficulty() != Difficulty.PEACEFUL) && p_186270_.canBeSeenAsEnemy() && p_186270_ != this.getVehicle();
    }

    public SoundEvent getBossMusic() {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_MUSIC.get();
    }

    protected boolean canPlayMusic() {
        return !this.isSilent() && this.getTarget() instanceof Player && this.getTarget() != null;
    }

    public boolean canPlayerHearMusic(Player player) {
        return player != null && this.canAttack(player) && this.distanceToSqr(player) < 5000.0F;
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

    public boolean halfHealth() {
        return this.getHealth() <= this.getMaxHealth() / 2;
    }

    public boolean hasFewEnoughMinions() {
        List<Monster> list = this.level().getEntitiesOfClass(Monster.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.isAlive() && (predicate instanceof EyesoreEntity || predicate instanceof FunnyboneEntity) && ((IllagerAttack) predicate).getOwner() == this);
        return list.size() < 3;
    }

    public boolean shouldPlayTransition() {
        return this.isActive() && this.getVehicle() instanceof RagnoEntity && this.getVehicle().isAlive();
    }

    public void tick() {
        List<Raider> list = this.level().getEntitiesOfClass(Raider.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.hasActiveRaid() && !predicate.getType().is(ModTags.EntityTypes.ILLAGER_BOSSES));
        if (Config.CommonConfig.freakager_forcefield.get() && this.hasActiveRaid()) {
            if (!this.level().isClientSide) {
                this.setIllagersNearby(!list.isEmpty());
            }

            if (this.areIllagersNearby()) {
                this.setTarget(null);
            }
        }

        if (this.hasActiveRaid()) {
            if (this.getCurrentRaid() != null && this.getCurrentRaid().getGroupsSpawned() == 7 && this.shouldRemoveItself() && Config.CommonConfig.freakager_onlyOneAllowed.get()) {
                this.getCurrentRaid().removeFromRaid(this, true);
                if (!this.level().isClientSide) {
                    this.remove(RemovalReason.DISCARDED);
                }
            }
        }

        if (this.introTicks > 0) {
            this.setDeltaMovement(0.0, this.getDeltaMovement().y, 0.0);
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

        if (this.customDeathTime > 0 && this.getVehicle() != null) {
            this.setYRot(this.getVehicle().getYRot());
            this.yBodyRot = this.getYRot();
            this.yHeadRot = this.getVehicle().getYHeadRot();
        }

        super.tick();

        RagnoEntity ragno;
        if (!this.isActive()) {
            if (this.introTicks > 0) {
                ++this.introTicks;
                this.setYRot(this.getYHeadRot());
                this.yBodyRot = this.getYRot();
            }

            if (this.introTicks == 21) {
                this.setAnimationState(9);
                this.setLeftHanded(false);
                setShowArms(true);
                if (Config.CommonConfig.mobs_watch_intros.get()) {
                    List<Mob> list1 = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(50.0));
                    for (Mob mob : list1) {
                        mob.goalSelector.addGoal(0, new WatchBossIntroGoal(mob, this));
                    }
                }
            }

            int minusTime = 20;

            if (this.introTicks - minusTime == 5) {
                this.setShowVillager(true);
                this.setFreakagerFace(1);
                this.setVillagerFace(1);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_CYMBAL.get(), 1.0F, 1.0F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_SKID.get(), 0.5F, 1.0F);
            }
            if (this.introTicks - minusTime == 12) {
                this.setVillagerFace(0);
            }
            if (this.introTicks - minusTime == 16) {
                this.setFreakagerFace(0);
            }
            if (this.introTicks - minusTime == 22) {
                this.setVillagerFace(2);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERPANIC.get(), 1.0F, 1.2F);
            }
            if (this.introTicks - minusTime == 30) {
                this.setVillagerFace(3);
            }
            if (this.introTicks - minusTime == 38) {
                this.setVillagerFace(4);
                this.setVillagerShakeMultiplier(40);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERPANIC.get(), 1.0F, this.getVoicePitch());
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERWAVE.get(), 1.0F, this.getVoicePitch());
            }
            if (this.introTicks - minusTime > 38) {
                if ((this.introTicks - minusTime - 38) % 5 == 0 && (this.introTicks - minusTime - 38) < 55) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERPANIC.get(), 1.0F, this.getVoicePitch());
                }
                if ((this.introTicks - minusTime - 38) % 7 == 0 && (this.introTicks - minusTime - 38) < 60) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERWAVE.get(), 1.0F, this.getVoicePitch());
                }
            }
            if (this.introTicks - minusTime == 43) {
                this.setFreakagerFace(2);
                this.playSound(SoundEvents.BOTTLE_FILL, 1.0F, 1.0F);
                this.setItemSlot(EquipmentSlot.OFFHAND, ItemRegisterer.DARK_DRINK.get().getDefaultInstance());
            }
            if (this.introTicks - minusTime == 50) {
                this.setFreakagerFace(1);
            }
            if (this.introTicks - minusTime == 65) {
                this.setVillagerFace(1);
            }
            if (this.introTicks - minusTime == 70) {
                this.setFreakagerFace(2);
            }
            if (this.introTicks - minusTime == 92) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 1.0F, 1.0F);
            }
            if (this.introTicks - minusTime == 95) {
                this.setFreakagerFace(1);
                this.setVillagerFace(3);
                this.setVillagerShakeMultiplier(0);
                this.playSound(SoundEvents.PLAYER_ATTACK_STRONG, 1.0F, 1.0F);
            }
            if (this.introTicks - minusTime == 102) {
                this.setVillagerFace(1);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_FORCEPOTION.get(), 1.0F, 1.0F);
                this.playSound(SoundEvents.PLAYER_ATTACK_KNOCKBACK, 1.0F, 1.0F);
                this.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
            }
            if (this.introTicks - minusTime == 110) {
                this.playSound(SoundEvents.WITCH_DRINK, 1.0F, 0.7F);
            }
            if (this.introTicks - minusTime == 120) {
                this.setVillagerFace(0);
                this.setFreakagerFace(0);
            }
            if (this.introTicks - minusTime == 136) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_EARTHRUMBLE.get(), 1.0F, 1.0F);
            }
            if (this.introTicks - minusTime == 142) {
                this.setVillagerFace(5);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERSIGH.get(), 1.0F, 1.0F);
            }
            if (this.introTicks - minusTime == 161) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SPAWN.get(), 1.0F, 1.0F);
            }
            if (this.introTicks - minusTime >= 136) {
                this.setVillagerShakeMultiplier(this.getVillagerShakeMultiplier() + 1);
            }

            if ((this.introTicks - minusTime) == 188) {
                EntityUtil.makeCircleParticles(this.level(), this, ParticleTypes.LARGE_SMOKE, 100, 1.0D, 1.0F);

                LightningBolt lightning = EntityType.LIGHTNING_BOLT.create(this.level());
                assert lightning != null;
                lightning.setPos(this.getX(), this.getY(), this.getZ());
                lightning.setVisualOnly(true);
                this.playSound(SoundEvents.LIGHTNING_BOLT_IMPACT, 3.0F, 1.0F);
                this.playSound(SoundEvents.LIGHTNING_BOLT_THUNDER, 10000.0F, 1.0F);
                this.level().addFreshEntity(lightning);
                CameraShakeEntity.cameraShake(this.level(), position(), 50, 0.2f, 0, 10);
                if (!this.level().isClientSide) {
                    this.level().explode(this, this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);
                }
                RagnoEntity ragnoEntity = ModEntityTypes.Ragno.get().create(this.level());
                assert ragnoEntity != null;
                ragnoEntity.moveTo(this.getX(), this.getY(), this.getZ(), this.getYHeadRot(), this.getXRot());
                ragnoEntity.setTarget(this.getTarget());
                this.level().addFreshEntity(ragnoEntity);
                if (!this.level().isClientSide) {
                    this.startRiding(ragnoEntity);
                }
                ragnoEntity.playIntro();
                ragnoEntity.setCanJoinRaid(true);
                this.makeRagnoParticles(ragnoEntity);
                if (getTeam() != null) {
                    level().getScoreboard().addPlayerToTeam(ragnoEntity.getStringUUID(),
                            level().getScoreboard().getPlayerTeam(getTeam().getName()));
                }
                this.setAnimationState(11);
                if (!this.level().isClientSide) {
                    this.setShowVillager(false);
                }
                ragnoEntity.entityToStareAt = this.entityToStareAt;
            }

            if ((this.introTicks - 189 - minusTime) == 30) {
                this.setAnimationState(10);
            }

            if ((this.introTicks - 189 - minusTime - 30) == 4) {
                this.setFreakagerFace(1);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_LAUGH.get(), 2.0F, 1.0F);
            }

            if ((this.introTicks - 189 - minusTime - 30) == 52) {
                this.setFreakagerFace(0);
            }

            if ((this.introTicks - 189 - minusTime - 30) == 65) {
                this.setActive(true);
                this.setAnimationState(0);
                if (!this.level().isClientSide) {
                    this.setShowArms(false);
                }
            }
        }

        if (this.isActive() && this.getTarget() != null && this.tickCount % 20 == 10) {
            if (!this.hasLineOfSight(this.getTarget()) || (this.getVehicle() != null && (this.getVehicle().isInWater() || this.getVehicle().isInLava() || this.getVehicle().isInPowderSnow))) {
                ++this.stuckTime;
            } else if (this.stuckTime > 0) {
                --this.stuckTime;
            }
        } else if (this.isActive() && !this.ridingRideableMob()) {
            this.stuckTime = 1000;
        }

        if (this.attackType > 0) {
            ++this.attackTicks;
        }

        if (this.attackCooldown > 0) {
            --this.attackCooldown;
        }

        if (this.attackType < 1) {
            if (this.bombsCooldown > 0) {
                --this.bombsCooldown;
            }

            if (this.minionsCooldown > 0 && this.hasFewEnoughMinions()) {
                --this.minionsCooldown;
            }

            if (this.axesCooldown > 0) {
                --this.axesCooldown;
            }

            if (this.potionsCooldown > 0) {
                --this.potionsCooldown;
            }

            if (this.scytheCooldown > 0) {
                --this.scytheCooldown;
            }

            if (this.trickOrTreatCooldown > 0) {
                --this.trickOrTreatCooldown;
            }
        }

        if (this.isActive()) {
            this.setYRot(this.getYHeadRot());
            this.yBodyRot = this.getYRot();
        }

        if (this.isActive() && !this.ridingRideableMob()) {
            List<RagnoEntity> ragnolist = this.level().getEntitiesOfClass(RagnoEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == this && predicate.isAlive());
            if (!ragnolist.isEmpty() && this.attackType == ANTICHEESE_ATTACK) {
                ragno = ragnolist.get(0);
                if (!ragno.isAnticheese()) {
                    ragno.setStunned(false);
                    ragno.setAttackType(0);
                    ragno.setAttackTicks(0);
                    ragno.setAnimationState(0);
                    ragno.setAnticheese(true);
                }
                if (this.isPhasedOut() && !this.level().isClientSide) {
                    if (this.isPassenger() && this.getVehicle() != ragno) this.stopRiding();
                    this.startRiding(ragno);
                }
            }
        }

        this.updateTreatList();
        this.distractAttackers();
        if (this.isAlive()) {
            if (this.attackType == BOMBS_ATTACK) {
                if (this.attackTicks == 20) {
                    double throwSpeed = 0.7;
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_CYMBAL.get(), 1.0F, 1.0F);
                    this.setFreakagerFace(1);

                    for (int i = 0; i < 4; ++i) {
                        if (this.halfHealth()) {
                            SkullBombEntity s1 = ModEntityTypes.SkullBomb.get().create(this.level());

                            assert s1 != null;

                            s1.setPos(this.getX(), this.getY() + 0.25, this.getZ());
                            s1.setOwner(this);
                            if (i == 0) {
                                s1.setDeltaMovement(-throwSpeed, 0.5, -throwSpeed);
                            } else if (i == 1) {
                                s1.setDeltaMovement(-throwSpeed, 0.5, throwSpeed);
                            } else if (i == 2) {
                                s1.setDeltaMovement(throwSpeed, 0.5, -throwSpeed);
                            } else {
                                s1.setDeltaMovement(throwSpeed, 0.53, throwSpeed);
                            }

                            this.level().addFreshEntity(s1);
                        } else {
                            PumpkinBombEntity s1 = ModEntityTypes.PumpkinBomb.get().create(this.level());

                            assert s1 != null;

                            s1.setPos(this.getX(), this.getY() + 0.25, this.getZ());
                            s1.setOwner(this);
                            s1.setTarget(this.getTarget());
                            if (i == 0) {
                                s1.setDeltaMovement(-throwSpeed, 0.3, -throwSpeed);
                            } else if (i == 1) {
                                s1.setDeltaMovement(-throwSpeed, 0.3, throwSpeed);
                            } else if (i == 2) {
                                s1.setDeltaMovement(throwSpeed, 0.3, -throwSpeed);
                            } else {
                                s1.setDeltaMovement(throwSpeed, 0.3, throwSpeed);
                            }

                            if (this.getTeam() != null) {
                                this.level().getScoreboard().addPlayerToTeam(s1.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                            }

                            this.level().addFreshEntity(s1);
                        }
                    }
                }

                if (this.attackTicks == 30) {
                    this.setFreakagerFace(0);
                }
            }

            if (this.attackType == MINIONS_ATTACK) {
                if (attackTicks == 10) {
                    setFreakagerFace(1);
                }

                if (attackTicks == 25) {
                    setFreakagerFace(0);
                }

                if (this.attackTicks == 40) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_CYMBAL.get(), 1.0F, 1.0F);
                    this.setFreakagerFace(1);

                    for (int i = 0; i < 5; ++i) {
                        if (this.halfHealth()) {
                            EyesoreEntity entity = ModEntityTypes.Eyesore.get().create(this.level());

                            assert entity != null;

                            entity.setPos(this.getX(), this.getY() + 0.25, this.getZ());
                            entity.setOwner(this);
                            entity.setTarget(this.getTarget());
                            entity.setFlying(true);
                            entity.setDeltaMovement((double) (-2 + this.random.nextInt(5)) * 0.4, 0.6, (double) (-2 + this.random.nextInt(5)) * 0.4);

                            if (this.getTeam() != null) {
                                this.level().getScoreboard().addPlayerToTeam(entity.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                            }

                            this.level().addFreshEntity(entity);
                        } else {
                            FunnyboneEntity entity = ModEntityTypes.Funnybone.get().create(this.level());

                            assert entity != null;

                            entity.setPos(this.getX(), this.getY() + 0.25, this.getZ());
                            entity.setOwner(this);
                            entity.setTarget(this.getTarget());
                            entity.setFlying(true);
                            entity.setDeltaMovement((double) (-2 + this.random.nextInt(5)) * 0.4, 0.6, (double) (-2 + this.random.nextInt(5)) * 0.4);

                            if (this.getTeam() != null) {
                                this.level().getScoreboard().addPlayerToTeam(entity.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                            }

                            this.level().addFreshEntity(entity);
                        }
                    }
                }

                if (this.attackTicks == 45) {
                    this.setFreakagerFace(0);
                }
            }

            double y;
            double z;
            double d;
            float power;
            double motionX;
            double motionY;
            double motionZ;
            LivingEntity entity;
            AxeEntity projectile;
            double x;
            if (this.attackType == AXES_ATTACK) {
                if (this.attackTicks == 4) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
                    this.setItemSlot(EquipmentSlot.OFFHAND, Items.IRON_AXE.getDefaultInstance());
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_AXE_DRAW.get(), 2.0F, this.getVoicePitch());
                    this.setFreakagerFace(1);
                }

                if (this.attackTicks >= 21) {
                    this.setFreakagerFace(0);
                    int trueAttackTicks = this.attackTicks - 21;
                    if (trueAttackTicks % 26 == 0) {
                        this.setAnimationState(0);
                        this.setAnimationState(4);
                    }
                    if (trueAttackTicks % 26 == 0 || trueAttackTicks % 26 == 12) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 2.0F, 1.0F);
                    }

                    if (trueAttackTicks % 26 == 0 || trueAttackTicks % 26 == 12) {
                        if (trueAttackTicks % 26 == 12) {
                            this.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
                        } else {
                            this.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
                        }
                        if (!this.level().isClientSide && this.getTarget() != null) {
                            x = this.getX() - this.getTarget().getX();
                            y = (this.getY() + 1) - (this.getTarget().getY() + (this.getTarget().getEyeHeight() / 2));
                            z = this.getZ() - this.getTarget().getZ();

                            projectile = new AxeEntity(this.level(), this, -x, -y, -z);
                            projectile.moveTo(this.getX(), this.getY() + 1, this.getZ());
                            CompoundTag tag = this.getPersistentData().getCompound("Rotation");
                            projectile.readAdditionalSaveData(tag);
                            projectile.setYHeadRot(this.getYHeadRot());
                            projectile.setYRot(this.getYHeadRot());

                            projectile.setShooter(this);
                            this.level().addFreshEntity(projectile);
                        }
                    }
                    if (trueAttackTicks % 26 == 6 || trueAttackTicks % 26 == 18) {
                        if (trueAttackTicks % 26 == 6) {
                            this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
                        } else {
                            this.setItemSlot(EquipmentSlot.OFFHAND, Items.IRON_AXE.getDefaultInstance());
                        }
                    }
                }
            }

            if (this.attackType == ANGRY_AXES_ATTACK) {
                entity = this.getTarget();
                if (this.attackTicks == 4) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
                    this.setItemSlot(EquipmentSlot.OFFHAND, Items.IRON_AXE.getDefaultInstance());
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_AXE_DRAW.get(), 2.0F, this.getVoicePitch());
                    EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_ANGRYAXES.get(), 3.0F, 1.0F, false);
                    this.setFreakagerFace(3);
                }

                if (attackTicks >= 40 && attackTicks < 96) {
                    this.setFreakagerFace(4);

                    if ((attackTicks - 40) % 7 == 0) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERWAVE.get(), 3.0F, this.getVoicePitch());
                    }

                    if (!this.level().isClientSide && entity != null) {
                        float f = this.yBodyRot * ((float) Math.PI / 180F) * 0.25F;
                        float f1 = Mth.cos(f);
                        float f2 = Mth.sin(f);

                        Vec3 vec3;

                        if (this.attackTicks % 2 == 0) {
                            vec3 = new Vec3(this.getX() + (double) f1 * 0.6D, this.getY() + 0.7D, this.getZ() + (double) f2 * 0.6D);
                        } else {
                            vec3 = new Vec3(this.getX() - (double) f1 * 0.6D, this.getY() + 0.7D, this.getZ() - (double) f2 * 0.6D);
                        }

                        x = vec3.x - entity.getX();
                        y = vec3.y - (entity.getY() + (entity.getEyeHeight() / 2));
                        z = vec3.z - entity.getZ();

                        projectile = new AxeEntity(this.level(), this, -x, -y, -z);
                        projectile.moveTo(vec3);
                        CompoundTag tag = this.getPersistentData().getCompound("Rotation");
                        projectile.readAdditionalSaveData(tag);
                        projectile.shoot(-x, -y, -z, 1.0F, 20.0F);

                        projectile.setShooter(this);
                        this.level().addFreshEntity(projectile);
                    }
                }

                if (attackTicks == 96) {
                    this.setFreakagerFace(3);
                    this.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
                    this.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
                }

                if (this.attackTicks == 110) {
                    this.setFreakagerFace(2);
                }
            }

            if (this.attackType == POTIONS_ATTACK) {
                if (attackTicks == 5) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_REVEAL.get(), 2.0F, 1.0F);
                    this.setFreakagerFace(1);
                }

                if (this.attackTicks == 20) {
                    EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_SPIN.get(), 2.0F, 1.0F, false);
                    this.setFreakagerFace(0);
                    this.potionThrowDistance = 0.0;
                }

                if (this.attackTicks >= 20 && this.attackTicks <= 60) {
                    this.makePotionParticles();
                    this.potionThrowDistance += 0.02;

                    for (int i = 0; i < 2; ++i) {
                        if (!this.level().isClientSide) {
                            DarkPotionEntity potion = ModEntityTypes.DarkPotion.get().create(this.level());

                            assert potion != null;

                            potion.setPos(this.getX(), this.getY() + 2.0, this.getZ());
                            potion.setOwner(this);
                            int lingerChance = this.halfHealth() ? this.getRandom().nextInt(0, 15) : 1;
                            potion.setItem(PotionUtils.setPotion(new ItemStack(lingerChance == 0 ? ItemRegisterer.DARK_LINGER.get() : ItemRegisterer.DARK_SPLASH.get()), PotionRegisterer.MUTATION.get()));
                            potion.setXRot(-20.0F);

                            if (this.halfHealth()) {
                                potion.shoot(-2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble(), 5.0 + this.random.nextDouble() + this.random.nextDouble(), -2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble(), 0.75F, 10.0F);
                                potion.setDeltaMovement(potion.getDeltaMovement().add(0.0, 0.5, 0.0));
                            } else {
                                potion.setDeltaMovement((-2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble()) * (this.potionThrowDistance / 4.0), 1.0, (-2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble()) * (this.potionThrowDistance / 4.0));
                            }

                            this.level().addFreshEntity(potion);
                        }
                    }
                }
            }

            if (this.attackType == SCYTHE_ATTACK) {
                entity = this.getTarget();
                if (attackTicks == 3) {
                    setShowScythe(true);
                    setFreakagerFace(1);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_AXE_DRAW.get(), 2.0F, this.getVoicePitch());
                }

                if (this.attackTicks == 13) {
                    setFreakagerFace(0);
                }

                if (attackTicks == 21) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 2.0F, 1.0F);
                }

                if (this.attackTicks == 23 && entity != null) {
                    this.waitingForScythe = true;
                    if (!this.level().isClientSide) {
                        this.setShowScythe(false);
                    }

                    ScytheEntity scythe = ModEntityTypes.Scythe.get().create(this.level());

                    assert scythe != null;

                    scythe.setPos(this.getX(), this.getY() + 1.5, this.getZ());
                    x = scythe.getX() - entity.getX();
                    y = scythe.getY() - (entity.getY() + 1);
                    z = scythe.getZ() - entity.getZ();
                    d = Math.sqrt(x * x + y * y + z * z);
                    power = 3.0F;
                    motionX = -(x / d * (double) power * 0.2);
                    motionY = -(y / d * (double) power * 0.2);
                    motionZ = -(z / d * (double) power * 0.2);
                    scythe.setAcceleration(motionX, motionY, motionZ);
                    scythe.halfHealth = this.halfHealth();
                    scythe.setGoFor(entity);
                    scythe.setShooter(this);
                    this.level().addFreshEntity(scythe);
                }

                if (attackTicks > 23 && !waitingForScythe) {
                    if (getAnimationState() != 13) {
                        this.setAnimationState(13);
                        this.setShowScythe(true);
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_SCYTHE_CATCH.get(), 1.5f, this.getVoicePitch());
                    }
                    catchTicks++;
                }

                if (catchTicks == 9) {
                    this.setShowScythe(false);
                }

                if (attackTicks >= 314) waitingForScythe = false;
            }

            if (this.attackType == TRICKORTREAT_ATTACK) {
                if (this.attackTicks == 21) {
                    this.setFreakagerFace(1);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_CYMBAL.get(), 2.0F, 1.0F);
                    int amount = 7;

                    for (int i = 0; i < amount; ++i) {
                        TrickOrTreatEntity treat = ModEntityTypes.TrickOrTreat.get().create(this.level());

                        assert treat != null;

                        treat.circleTime = i * 20;
                        treat.bounceTime = i;
                        treat.setPos(this.getX(), this.getY(), this.getZ());
                        treat.setOwner(this);
                        treat.setTreat(this.random.nextInt(6) + 1);
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(treat.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        this.circleTreat(treat, i, amount);
                        this.level().addFreshEntity(treat);
                        this.treats.add(treat);
                    }
                }

                if (this.attackTicks == 31) {
                    this.setFreakagerFace(0);
                }
            }

            if (this.attackType == ANTICHEESE_ATTACK) {
                if (this.attackTicks == 5) {
                    this.playSound(SoundEvents.BOTTLE_FILL, 1.0F, 1.0F);
                }

                if (this.attackTicks == 15) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_REVEAL.get(), 1.0F, 1.0F);
                    this.playSound(SoundEvents.WITCH_THROW, 1.0F, this.getVoicePitch());
                    this.setFreakagerFace(1);
                    this.setItemSlot(EquipmentSlot.OFFHAND, PotionUtils.setPotion(new ItemStack(Items.POTION), Potions.INVISIBILITY));
                }

                if (this.attackTicks == 25) {
                    this.playSound(SoundEvents.WITCH_DRINK, 1.0F, 0.8F + this.random.nextFloat() * 0.4F);
                    this.setFreakagerFace(2);
                }

                if (this.attackTicks == 30) {
                    this.playSound(SoundEvents.ILLUSIONER_MIRROR_MOVE, 1.0F, 1.0F);
                    this.level().broadcastEntityEvent(this, (byte) 60);
                    this.setPhasedOut(true);
                    this.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
                    this.setAnimationState(0);
                }

                if (this.attackTicks == 63) {
                    this.setAnimationState(1);
                }

                if (this.attackTicks == 98) {
                    this.playSound(SoundEvents.ILLUSIONER_MIRROR_MOVE, 1.0F, 1.0F);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_REVEAL.get(), 1.0F, 1.0F);
                    this.level().broadcastEntityEvent(this, (byte) 60);
                    this.setFreakagerFace(1);
                    this.setPhasedOut(false);
                }

                if (this.attackTicks == 108) {
                    this.setFreakagerFace(0);
                }
            }
        }

    }

    public boolean startRiding(Entity p_20330_) {
        return (p_20330_ instanceof RagnoEntity || p_20330_ instanceof CrocofangEntity || p_20330_ instanceof Ravager) && super.startRiding(p_20330_);
    }

    public boolean ridingRideableMob() {
        return this.getVehicle() instanceof RagnoEntity || this.getVehicle() instanceof CrocofangEntity || this.getVehicle() instanceof Ravager;
    }

    public void die(DamageSource p_37847_) {
        this.setPhasedOut(false);

        if (!this.treats.isEmpty()) {

            for (TrickOrTreatEntity treat : this.treats) {
                treat.kill();
            }
        }

        List<Monster> minions = this.level().getEntitiesOfClass(Monster.class, this.getBoundingBox().inflate(40.0));
        if (!minions.isEmpty()) {
            for (Monster raider : minions) {
                if (raider instanceof EyesoreEntity && ((EyesoreEntity) raider).getOwner() == this) {
                    raider.setLastHurtByMob(null);
                    raider.setTarget(null);
                }

                if (raider instanceof FunnyboneEntity && ((FunnyboneEntity) raider).getOwner() == this) {
                    raider.setLastHurtByMob(null);
                    raider.setTarget(null);
                }
            }
        }

        if (this.shouldPlayTransition()) {
            this.setAnimationState(14);
            this.setFreakagerFace(3);
            this.setShowScythe(false);
            this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
            this.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
            this.setShowArms(true);
            this.noCulling = true;
        }

        super.die(p_37847_);
    }

    @Override
    protected void tickDeath() {
        if (!shouldPlayTransition()) {
            super.tickDeath();
        } else {
            ++this.customDeathTime;

            this.clearFire();
            this.switchAttackersToRagno();

            if (this.customDeathTime == 15) {
                this.setFreakagerFace(0);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_PUMPKINBOMBS.get(), 2.0F, 1.0F);
            }

            if (this.customDeathTime == 40 || this.customDeathTime == 77) {
                this.setFreakagerFace(1);
            }

            if (this.customDeathTime == 75) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_REVEAL.get(), 2.0F, 1.0F);
            }

            if (this.customDeathTime == 45 || this.customDeathTime == 85) {
                this.setFreakagerFace(0);
            }

            if (this.customDeathTime == 98) {
                this.setFreakagerFace(2);
            }

            if (this.customDeathTime == 116 || this.customDeathTime == 145 || this.customDeathTime == 156 || this.customDeathTime == 166 || this.customDeathTime == 206) {
                this.setFreakagerFace(3);
            }

            if (this.customDeathTime == 140 || this.customDeathTime == 151 || this.customDeathTime == 161 || this.customDeathTime == 184) {
                this.setFreakagerFace(4);
            }

            if ((this.customDeathTime == 140 || this.customDeathTime == 151 || this.customDeathTime == 161) && this.getVehicle() != null && this.getVehicle() instanceof LivingEntity entity) {
                float radius2 = 2.0F;
                double x = this.getX() + 0.800000011920929 * Math.sin((double) (-entity.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-entity.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-entity.getXRot()) * Math.PI / 180.0);
                double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-entity.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-entity.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-entity.getXRot()) * Math.PI / 180.0);

                this.level().playSound(this, BlockPos.containing(x, entity.getY(), z), IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_HURT.get(), this.getSoundSource(), this.getSoundVolume(), this.getVoicePitch());
            }

            if (this.customDeathTime == 206 && this.getVehicle() != null && this.getVehicle() instanceof LivingEntity entity) {
                this.makeBloodParticles(entity);
            }

            if (this.customDeathTime == 206) {
                this.deathTime = 1;
            }

            if (!this.level().isClientSide && this.customDeathTime >= 250) {
                this.remove(RemovalReason.KILLED);
            }
        }
    }

    private void circleTreat(Entity entity, int number, int amount) {
        float yaw = (float) number * (6.2831855F / (float) amount);
        float vy = 0.3F;
        float vx = 0.5F * Mth.cos(yaw);
        float vz = 0.5F * Mth.sin(yaw);
        entity.setDeltaMovement(vx, vy, vz);
    }

    public void updateTreatList() {
        if (!this.treats.isEmpty()) {
            for (int i = 0; i < this.treats.size(); ++i) {
                TrickOrTreatEntity clone = this.treats.get(i);
                if (!clone.isAlive()) {
                    this.treats.remove(i);
                    --i;
                }
            }
        }

    }

    public void distractAttackers() {
        if (!this.treats.isEmpty()) {
            List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(100.0));

            for (Mob attacker : list) {
                TrickOrTreatEntity treat = this.treats.get(this.random.nextInt(this.treats.size()));
                if (attacker.getLastHurtByMob() == this) {
                    attacker.setLastHurtByMob(treat);
                }

                if (attacker.getTarget() == this) {
                    attacker.setTarget(treat);
                }

                if (attacker instanceof Warden warden) {
                    if (warden.getTarget() == this) {
                        warden.increaseAngerAt(treat, AngerLevel.ANGRY.getMinimumAnger() + 100, false);
                        warden.setAttackTarget(treat);
                    }
                } else {
                    try {
                        if (attacker.getBrain().hasMemoryValue(MemoryModuleType.ATTACK_TARGET) && attacker.getBrain().getMemory(MemoryModuleType.ATTACK_TARGET).isPresent() && attacker.getBrain().getMemory(MemoryModuleType.ATTACK_TARGET).get() == this) {
                            attacker.getBrain().setMemoryWithExpiry(MemoryModuleType.ANGRY_AT, treat.getUUID(), 600L);
                            attacker.getBrain().setMemoryWithExpiry(MemoryModuleType.ATTACK_TARGET, treat, 600L);
                        }
                    } catch (NullPointerException ignored) {
                    }
                }
            }
        }

    }

    public void switchAttackersToRagno() {
        if (!this.treats.isEmpty()) {
            List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(100.0));

            for (Mob attacker : list) {
                TrickOrTreatEntity treat = this.treats.get(this.random.nextInt(this.treats.size()));
                if (attacker.getLastHurtByMob() == this) {
                    attacker.setLastHurtByMob(treat);
                }

                if (attacker.getTarget() == this) {
                    attacker.setTarget(treat);
                }

                if (attacker instanceof Warden warden) {
                    if (warden.getTarget() == this) {
                        warden.increaseAngerAt(treat, AngerLevel.ANGRY.getMinimumAnger() + 100, false);
                        warden.setAttackTarget(treat);
                    }
                } else {
                    try {
                        if (attacker.getBrain().hasMemoryValue(MemoryModuleType.ATTACK_TARGET) && attacker.getBrain().getMemory(MemoryModuleType.ATTACK_TARGET).isPresent() && attacker.getBrain().getMemory(MemoryModuleType.ATTACK_TARGET).get() == this) {
                            attacker.getBrain().setMemoryWithExpiry(MemoryModuleType.ANGRY_AT, treat.getUUID(), 600L);
                            attacker.getBrain().setMemoryWithExpiry(MemoryModuleType.ATTACK_TARGET, treat, 600L);
                        }
                    } catch (NullPointerException ignored) {
                    }
                }
            }
        }

    }

    public void makeRagnoParticles(Entity caught) {
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
                    packet.queueParticle(ParticleTypes.LARGE_SMOKE, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(d0, d1, d2));
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

                for (int i = 0; i < 1; ++i) {
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

    public void makeBloodParticles(LivingEntity entity) {
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

                for (int i = 0; i < 20; ++i) {
                    float radius2 = 1.4F;
                    double x = this.getX() + 0.800000011920929 * Math.sin((double) (-entity.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-entity.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-entity.getXRot()) * Math.PI / 180.0);
                    double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-entity.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-entity.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-entity.getXRot()) * Math.PI / 180.0);

                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (1.0 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleRegisterer.BLOOD_PARTICLES.get(), false, new Vec3(x, entity.getY() + 0.5, z), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public int getVillagerFace() {
        return this.entityData.get(VILLAGER_FACE);
    }

    public void setVillagerFace(int face) {
        this.entityData.set(VILLAGER_FACE, face);
    }

    public int getVillagerShakeMultiplier() {
        return this.entityData.get(VILLAGER_SHAKE_MULTIPLIER);
    }

    public void setVillagerShakeMultiplier(int shake) {
        if (!this.level().isClientSide) {
            this.entityData.set(VILLAGER_SHAKE_MULTIPLIER, shake);
        }
    }

    public int getFreakagerFace() {
        return this.entityData.get(FREAKAGER_FACE);
    }

    public void setFreakagerFace(int face) {
        if (!this.level().isClientSide) {
            this.entityData.set(FREAKAGER_FACE, face);
        }
    }

    public boolean hurt(DamageSource source, float amount) {
        if (this.isActive() && !this.ridingRideableMob() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            List<RagnoEntity> ragnolist = this.level().getEntitiesOfClass(RagnoEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == this && predicate.isAlive());
            if (!ragnolist.isEmpty()) return false;
        }

        if (this.isPhasedOut() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            return false;
        }

        if (!this.isActive() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            amount = 0.0F;
            if (!this.level().isClientSide && source.getEntity() != null && this.introTicks == 0 && !this.areIllagersNearby()) {
                this.introTicks = 1;
                if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
                    this.getCurrentRaid().ticksActive = 0L;
                }
            }
        }

        if (source.getEntity() instanceof LivingEntity) {
            this.entityToStareAt = (LivingEntity) source.getEntity();
        }

        if (this.getVehicle() instanceof RagnoEntity && !((RagnoEntity) this.getVehicle()).isStunned() && (!(source.getEntity() instanceof Player) || !((Player) source.getEntity()).getAbilities().instabuild)) {
            amount /= 3.5;
        }

        if (this.areIllagersNearby() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            return false;
        } else {
            return !source.is(DamageTypes.IN_WALL) && super.hurt(source, amount);
        }
    }

    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_LAUGH.get();
    }

    protected SoundEvent getAmbientSound() {
        return this.introTicks > 1 || this.isPhasedOut() ? null : IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return this.shouldPlayTransition() ? IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_HURT.get() : IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_DEATH.get();
    }

    public boolean canBeLeader() {
        return false;
    }

    public void setAnimationState(int input) {
        this.entityData.set(ANIMATION_STATE, input);
    }

    public int getAnimationState() {
        return this.entityData.get(FreakagerEntity.ANIMATION_STATE);
    }

    public AnimationState getAnimationState(String input) {
        if (Objects.equals(input, "intro1")) {
            return intro1AnimationState;
        }
        if (Objects.equals(input, "intro2")) {
            return intro2AnimationState;
        }
        if (Objects.equals(input, "intro3")) {
            return intro3AnimationState;
        }
        if (Objects.equals(input, "axes_start")) {
            return axesStartAnimationState;
        }
        if (Objects.equals(input, "axes_normal")) {
            return axesNormalAnimationState;
        }
        if (Objects.equals(input, "laugh")) {
            return this.laughAnimationState;
        }
        if (Objects.equals(input, "bombs")) {
            return this.bombsAnimationState;
        }
        if (Objects.equals(input, "minions")) {
            return this.minionsAnimationState;
        }
        if (Objects.equals(input, "axes_angry")) {
            return this.angryAxesAnimationState;
        }
        if (Objects.equals(input, "potions")) {
            return this.potionsAnimationState;
        }
        if (Objects.equals(input, "scythe")) {
            return this.scytheAnimationState;
        }
        if (Objects.equals(input, "catch")) {
            return this.catchAnimationState;
        }
        if (Objects.equals(input, "trickortreat")) {
            return this.trickortreatAnimationState;
        }
        if (Objects.equals(input, "anticheese")) {
            return this.anticheeseAnimationState;
        }
        return Objects.equals(input, "phase") ? this.phaseAnimationState : new AnimationState();
    }

    protected void dropAllDeathLoot(DamageSource source) {
        if (!this.ridingRideableMob()) {
            super.dropAllDeathLoot(source);
        }
    }

    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                case 0 -> this.stopAllAnimationStates();
                case 1 -> {
                    this.stopAllAnimationStates();
                    this.minionsAnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.stopAllAnimationStates();
                    this.laughAnimationState.start(this.tickCount);
                }
                case 3 -> {
                    this.stopAllAnimationStates();
                    this.bombsAnimationState.start(this.tickCount);
                }
                case 4 -> {
                    this.stopAllAnimationStates();
                    this.axesNormalAnimationState.start(this.tickCount);
                }
                case 5 -> {
                    this.stopAllAnimationStates();
                    this.angryAxesAnimationState.start(this.tickCount);
                }
                case 6 -> {
                    this.stopAllAnimationStates();
                    this.potionsAnimationState.start(this.tickCount);
                }
                case 7 -> {
                    this.stopAllAnimationStates();
                    this.scytheAnimationState.start(this.tickCount);
                }
                case 8 -> {
                    this.stopAllAnimationStates();
                    this.trickortreatAnimationState.start(this.tickCount);
                }
                case 9 -> {
                    this.stopAllAnimationStates();
                    this.intro1AnimationState.start(this.tickCount);
                }
                case 10 -> {
                    this.stopAllAnimationStates();
                    this.intro2AnimationState.start(this.tickCount);
                }
                case 11 -> {
                    this.stopAllAnimationStates();
                    this.intro3AnimationState.start(this.tickCount);
                }
                case 12 -> {
                    this.stopAllAnimationStates();
                    this.axesStartAnimationState.start(this.tickCount);
                }
                case 13 -> {
                    this.stopAllAnimationStates();
                    this.catchAnimationState.start(this.tickCount);
                }
                case 14 -> {
                    this.stopAllAnimationStates();
                    this.phaseAnimationState.start(this.tickCount);
                }
                case 15 -> {
                    this.stopAllAnimationStates();
                    this.anticheeseAnimationState.start(this.tickCount);
                }
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    public void stopAllAnimationStates() {
        this.intro1AnimationState.stop();
        this.intro2AnimationState.stop();
        this.intro3AnimationState.stop();
        this.laughAnimationState.stop();
        this.bombsAnimationState.stop();
        this.minionsAnimationState.stop();
        this.axesStartAnimationState.stop();
        this.axesNormalAnimationState.stop();
        this.angryAxesAnimationState.stop();
        this.potionsAnimationState.stop();
        this.scytheAnimationState.stop();
        this.catchAnimationState.stop();
        this.trickortreatAnimationState.stop();
        this.anticheeseAnimationState.stop();
        this.phaseAnimationState.stop();
    }

    @Nullable
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor p_213386_1_, DifficultyInstance p_213386_2_, MobSpawnType p_213386_3_, @Nullable SpawnGroupData p_213386_4_, @Nullable CompoundTag p_213386_5_) {
        RandomSource randomsource = p_213386_1_.getRandom();
        if (p_213386_3_ == MobSpawnType.EVENT) {
            this.setShouldDeleteItself(true);
        }

        this.populateDefaultEquipmentSlots(randomsource, p_213386_2_);
        return super.finalizeSpawn(p_213386_1_, p_213386_2_, p_213386_3_, p_213386_4_, p_213386_5_);
    }

    protected void populateDefaultEquipmentSlots(RandomSource random, DifficultyInstance p_180481_1_) {
        this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
        this.setDropChance(EquipmentSlot.MAINHAND, 0.0F);
        this.setDropChance(EquipmentSlot.OFFHAND, 0.0F);
    }

    public boolean shouldRemoveItself() {
        return this.entityData.get(SHOULD_DELETE_ITSELF);
    }

    public void setShouldDeleteItself(boolean shouldDelete) {
        this.entityData.set(SHOULD_DELETE_ITSELF, shouldDelete);
    }

    public boolean areIllagersNearby() {
        return this.entityData.get(NEARBY_ILLAGERS) && this.introTicks < 1 && !this.isActive();
    }

    public void setIllagersNearby(boolean illagersNearby) {
        this.entityData.set(NEARBY_ILLAGERS, illagersNearby);
    }

    public boolean isActive() {
        return this.entityData.get(ACTIVE);
    }

    public void setActive(boolean active) {
        this.entityData.set(ACTIVE, active);
    }

    public boolean shouldShowArms() {
        return this.entityData.get(SHOW_ARMS);
    }

    public void setShowArms(boolean showArms) {
        this.entityData.set(SHOW_ARMS, showArms);
    }

    public boolean shouldShowVillager() {
        return this.entityData.get(SHOW_VILLAGER);
    }

    public void setShowVillager(boolean showVillager) {
        this.entityData.set(SHOW_VILLAGER, showVillager);
    }

    public boolean isPhasedOut() {
        return this.entityData.get(PHASED_OUT);
    }

    public void setPhasedOut(boolean phasedOut) {
        this.entityData.set(PHASED_OUT, phasedOut);
    }

    public boolean shouldShowScythe() {
        return this.entityData.get(SCYTHE);
    }

    public void setShowScythe(boolean scythe) {
        this.entityData.set(SCYTHE, scythe);
    }

    public boolean isPersistenceRequired() {
        return !Config.CommonConfig.ULTIMATE_NIGHTMARE.get();
    }

    public boolean isPickable() {
        return !this.isPhasedOut() && super.isPickable();
    }

    public boolean isAttackable() {
        return !this.isPhasedOut() && super.isAttackable();
    }

    public boolean attackable() {
        return !this.isPhasedOut() && super.attackable();
    }

    public void push(Entity p_21294_) {
        if (!isPhasedOut()) super.push(p_21294_);
    }

    protected void pushEntities() {
        if (!isPhasedOut()) super.pushEntities();
    }

    public boolean doesAttackMeetNormalRequirements() {
        return this.attackType == 0 && !this.areIllagersNearby() && this.getTarget() != null && this.hasLineOfSight(this.getTarget()) && this.isActive() && this.attackCooldown < 1;
    }

    static {
        SHOULD_DELETE_ITSELF = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        NEARBY_ILLAGERS = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        ACTIVE = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        ANIMATION_STATE = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.INT);
        SHOW_ARMS = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        SHOW_VILLAGER = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        VILLAGER_FACE = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.INT);
        SCYTHE = SynchedEntityData.defineId(FreakagerEntity.class, EntityDataSerializers.BOOLEAN);
    }

    class TrickOrTreatGoal extends Goal {
        public TrickOrTreatGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return FreakagerEntity.this.doesAttackMeetNormalRequirements() && FreakagerEntity.this.random.nextInt(16) == 0 && FreakagerEntity.this.trickOrTreatCooldown < 1 && FreakagerEntity.this.getHealth() < FreakagerEntity.this.getMaxHealth();
        }

        public void start() {
            FreakagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_TRICKORTREAT.get(), 2.0F, 1.0F);
            FreakagerEntity.this.setAnimationState(8);
            FreakagerEntity.this.attackType = TRICKORTREAT_ATTACK;
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.attackTicks <= 30;
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            FreakagerEntity.this.attackTicks = 0;
            FreakagerEntity.this.attackType = 0;
            FreakagerEntity.this.setAnimationState(0);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(false);
            }

            FreakagerEntity.this.trickOrTreatCooldown = 900;
            FreakagerEntity.this.attackCooldown = 100;
        }
    }

    class ScytheGoal extends Goal {
        public ScytheGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return FreakagerEntity.this.doesAttackMeetNormalRequirements() && FreakagerEntity.this.random.nextInt(16) == 0 && FreakagerEntity.this.scytheCooldown < 1;
        }

        public void start() {
            FreakagerEntity.this.setAnimationState(7);
            FreakagerEntity.this.attackType = SCYTHE_ATTACK;
            FreakagerEntity.this.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.attackTicks <= 24 || FreakagerEntity.this.catchTicks <= 12;
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            FreakagerEntity.this.attackTicks = 0;
            FreakagerEntity.this.catchTicks = 0;
            FreakagerEntity.this.attackType = 0;
            FreakagerEntity.this.setAnimationState(0);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(false);
                FreakagerEntity.this.setShowScythe(false);
            }
            FreakagerEntity.this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());

            FreakagerEntity.this.scytheCooldown = 200;
            FreakagerEntity.this.attackCooldown = 100;
        }
    }

    class PotionsGoal extends Goal {
        public PotionsGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return FreakagerEntity.this.doesAttackMeetNormalRequirements() && FreakagerEntity.this.random.nextInt(16) == 0 && FreakagerEntity.this.potionsCooldown < 1;
        }

        public void start() {
            FreakagerEntity.this.setAnimationState(6);
            FreakagerEntity.this.attackType = POTIONS_ATTACK;
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.attackTicks <= 75;
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            FreakagerEntity.this.attackTicks = 0;
            FreakagerEntity.this.attackType = 0;
            FreakagerEntity.this.setAnimationState(0);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(false);
            }

            FreakagerEntity.this.potionsCooldown = 200;
            FreakagerEntity.this.attackCooldown = 100;
        }
    }

    class AngryAxesGoal extends Goal {
        public AngryAxesGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return FreakagerEntity.this.doesAttackMeetNormalRequirements() && FreakagerEntity.this.random.nextInt(16) == 0 && FreakagerEntity.this.axesCooldown < 1 && FreakagerEntity.this.halfHealth();
        }

        public void start() {
            setAnimationState(5);
            setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
            setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
            FreakagerEntity.this.attackType = ANGRY_AXES_ATTACK;
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(true);
                FreakagerEntity.this.setFreakagerFace(2);
            }

        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.attackTicks <= 115;
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            FreakagerEntity.this.attackTicks = 0;
            FreakagerEntity.this.attackType = 0;
            FreakagerEntity.this.setAnimationState(0);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(false);
                FreakagerEntity.this.setFreakagerFace(0);
            }
            FreakagerEntity.this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
            setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);

            FreakagerEntity.this.axesCooldown = 200;
            FreakagerEntity.this.attackCooldown = 100;
        }
    }

    class AxesGoal extends Goal {
        public AxesGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return FreakagerEntity.this.doesAttackMeetNormalRequirements() && FreakagerEntity.this.random.nextInt(16) == 0 && FreakagerEntity.this.axesCooldown < 1 && !FreakagerEntity.this.halfHealth();
        }

        public void start() {
            setAnimationState(12);
            setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
            setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
            attackType = AXES_ATTACK;
            if (!level().isClientSide) {
                setShowArms(true);
                setFreakagerFace(2);
            }
        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.attackTicks <= 100;
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            FreakagerEntity.this.attackTicks = 0;
            FreakagerEntity.this.attackType = 0;
            FreakagerEntity.this.setAnimationState(0);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(false);
            }
            FreakagerEntity.this.setLeftHanded(false);
            FreakagerEntity.this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
            setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);

            FreakagerEntity.this.axesCooldown = 200;
            FreakagerEntity.this.attackCooldown = 100;
        }
    }

    class ThrowBombsGoal extends Goal {
        public ThrowBombsGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return FreakagerEntity.this.doesAttackMeetNormalRequirements() && FreakagerEntity.this.random.nextInt(16) == 0 && FreakagerEntity.this.bombsCooldown < 1;
        }

        public void start() {
            FreakagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_PUMPKINBOMBS.get(), 2.0F, 1.0F);
            FreakagerEntity.this.setAnimationState(3);
            FreakagerEntity.this.attackType = BOMBS_ATTACK;
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.attackTicks <= 40;
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            FreakagerEntity.this.attackTicks = 0;
            FreakagerEntity.this.attackType = 0;
            FreakagerEntity.this.setAnimationState(0);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(false);
            }

            FreakagerEntity.this.bombsCooldown = 200;
            FreakagerEntity.this.attackCooldown = 90;
        }
    }

    class ThrowMinionsGoal extends Goal {
        public ThrowMinionsGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return FreakagerEntity.this.doesAttackMeetNormalRequirements() && FreakagerEntity.this.random.nextInt(16) == 0 && FreakagerEntity.this.minionsCooldown < 1 && FreakagerEntity.this.hasFewEnoughMinions();
        }

        public void start() {
            FreakagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_MINIONS.get(), 2.0F, 1.0F);
            FreakagerEntity.this.setAnimationState(1);
            FreakagerEntity.this.attackType = MINIONS_ATTACK;
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.attackTicks <= 50;
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            FreakagerEntity.this.attackTicks = 0;
            FreakagerEntity.this.attackType = 0;
            FreakagerEntity.this.setAnimationState(0);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(false);
            }

            FreakagerEntity.this.minionsCooldown = 400;
            FreakagerEntity.this.attackCooldown = 100;
        }
    }

    class AnticheeseGoal extends Goal {
        public AnticheeseGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            if (attackType == 0 && getTarget() != null && stuckTime > 5 && !ridingRideableMob()) {
                List<RagnoEntity> ragnolist = level().getEntitiesOfClass(RagnoEntity.class, getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == FreakagerEntity.this && predicate.isAlive());
                return !ragnolist.isEmpty();
            } else if (attackType == 0 && getTarget() != null && stuckTime > 5 && getVehicle() instanceof RagnoEntity ragno) {
                return !ragno.isStunned() && ragno.getAttackType() == 0;
            }

            return false;
        }

        public void start() {
            if (getVehicle() instanceof RagnoEntity ragno && !ragno.level().isClientSide) {
                ragno.setAnticheese(true);
            }
            FreakagerEntity.this.setAnimationState(15);
            FreakagerEntity.this.setFreakagerFace(2);
            FreakagerEntity.this.attackType = ANTICHEESE_ATTACK;
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.attackTicks <= 110;
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            FreakagerEntity.this.attackTicks = 0;
            FreakagerEntity.this.attackType = 0;
            FreakagerEntity.this.setAnimationState(0);
            if (!FreakagerEntity.this.level().isClientSide) {
                FreakagerEntity.this.setShowArms(false);
            }

            FreakagerEntity.this.minionsCooldown = 400;
            FreakagerEntity.this.attackCooldown = 10;
            FreakagerEntity.this.stuckTime = 0;
        }
    }

    class IntroGoal extends Goal {

        public IntroGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.MOVE, Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            return FreakagerEntity.this.getAnimationState() == 9 || FreakagerEntity.this.getAnimationState() == 10 || FreakagerEntity.this.getAnimationState() == 11;
        }

        @Override
        public void start() {
            FreakagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_REVEAL.get(), 1.0F, 1.0F);
        }

        @Override
        public boolean requiresUpdateEveryTick() {
            return true;
        }

        @Override
        public void tick() {
            getNavigation().stop();

            if (entityToStareAt != null) {
                getLookControl().setLookAt(entityToStareAt, 100.0F, 100.0F);
            }

            navigation.stop();
        }

        @Override
        public boolean canContinueToUse() {
            return canUse();
        }
    }

    class AlwaysWatchTargetGoal extends Goal {
        public AlwaysWatchTargetGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public boolean canUse() {
            return FreakagerEntity.this.getTarget() != null && (FreakagerEntity.this.introTicks < 40 || FreakagerEntity.this.isActive());
        }

        public boolean canContinueToUse() {
            return FreakagerEntity.this.getTarget() != null && (FreakagerEntity.this.introTicks < 40 || FreakagerEntity.this.isActive());
        }

        public void tick() {
            FreakagerEntity.this.getNavigation().stop();
            if (FreakagerEntity.this.getTarget() != null) {
                FreakagerEntity.this.getLookControl().setLookAt(FreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            FreakagerEntity.this.navigation.stop();
        }
    }
}
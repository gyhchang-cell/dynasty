package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.client.sound.BossMusicPlayer;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.goal.WatchBossIntroGoal;
import com.yellowbrossproductions.illageandspillage.entities.projectile.*;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.*;
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
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.memory.MemoryModuleType;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.item.ItemEntity;
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
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import javax.annotation.Nullable;
import java.util.*;

public class OldFreakagerEntity extends AbstractIllager implements ICanBeAnimated {
    public ServerBossEvent bossEvent;
    private static final EntityDataAccessor<Boolean> SHOULD_DELETE_ITSELF;
    private static final EntityDataAccessor<Boolean> NEARBY_ILLAGERS;
    private static final EntityDataAccessor<Boolean> ACTIVE;
    private static final EntityDataAccessor<Integer> ANIMATION_STATE;
    private static final EntityDataAccessor<Boolean> SHOW_ARMS;
    private static final EntityDataAccessor<Boolean> SHOW_VILLAGER;
    private static final EntityDataAccessor<Integer> VILLAGER_FACE;
    private static final EntityDataAccessor<Boolean> SCYTHE;
    private int introTicks;
    public AnimationState introAnimationState = new AnimationState();
    public AnimationState laughAnimationState = new AnimationState();
    public AnimationState bombsAnimationState = new AnimationState();
    public AnimationState axesAnimationState = new AnimationState();
    public AnimationState fastaxesAnimationState = new AnimationState();
    public AnimationState potionsAnimationState = new AnimationState();
    public AnimationState scytheAnimationState = new AnimationState();
    public AnimationState trickortreatAnimationState = new AnimationState();
    private int attackType;
    private int attackTicks;
    private int attackCooldown;
    private static final int BOMBS_ATTACK = 1;
    private static final int AXES_ATTACK = 2;
    private static final int FAST_AXES_ATTACK = 3;
    private static final int POTIONS_ATTACK = 4;
    private static final int SCYTHE_ATTACK = 5;
    private static final int TRICKORTREAT_ATTACK = 6;
    private int bombsCooldown;
    private int axesCooldown;
    private int potionsCooldown;
    private int scytheCooldown;
    private int trickOrTreatCooldown;
    private double potionThrowDistance;
    public boolean waitingForScythe;
    private final List<TrickOrTreatEntity> treats = new ArrayList<>();
    private OldRagnoEntity ragno = null;

    public OldFreakagerEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 20;
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
        this.goalSelector.addGoal(0, new TrickOrTreatGoal());
        this.goalSelector.addGoal(0, new ScytheGoal());
        this.goalSelector.addGoal(0, new PotionsGoal());
        this.goalSelector.addGoal(0, new FastAxesGoal());
        this.goalSelector.addGoal(0, new AxesGoal());
        this.goalSelector.addGoal(0, new ThrowBombsGoal());
        this.goalSelector.addGoal(0, new IntroGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new AlwaysWatchTargetGoal());
        this.goalSelector.addGoal(2, new HoldGroundAttackGoal(this, 10.0F));
        this.goalSelector.addGoal(3, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(8, new RandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new LookAtPlayerGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new LookAtPlayerGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 160.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0);
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
        this.entityData.define(SCYTHE, false);
    }

    public void addAdditionalSaveData(CompoundTag p_37870_) {
        super.addAdditionalSaveData(p_37870_);
        if (this.isActive()) {
            p_37870_.putBoolean("active", true);
        }

    }

    public void readAdditionalSaveData(CompoundTag p_37862_) {
        super.readAdditionalSaveData(p_37862_);
        this.bossEvent.setName(this.getDisplayName());
        this.setActive(p_37862_.getBoolean("active"));
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public SoundEvent getBossMusic() {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_MUSIC.get();
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
        if (Config.CommonConfig.freakager_forcefield.get() && this.hasActiveRaid()) {
            if (!this.level().isClientSide) {
                this.setIllagersNearby(!list.isEmpty());
            }

            if (!list.isEmpty()) {
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

        super.tick();
        OldRagnoEntity ragno;
        if (!this.isActive()) {
            if (this.introTicks > 0) {
                ++this.introTicks;
                this.setYRot(this.getYHeadRot());
                this.yBodyRot = this.getYRot();
            }

            if (this.introTicks == 21 && Config.CommonConfig.mobs_watch_intros.get()) {
                List<Mob> list1 = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(50.0));
                for (Mob mob : list1) {
                    mob.goalSelector.addGoal(0, new WatchBossIntroGoal(mob, this));
                }

                this.setAnimationState(1);
            }

            if (this.introTicks - 20 == 5) {
                if (!this.level().isClientSide) {
                    this.setShowVillager(true);
                }

                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_CYMBAL.get(), 1.0F, 1.0F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERPANIC.get(), 1.0F, 1.0F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_SHIVER.get(), 1.0F, 1.0F);
            }

            if (this.introTicks > 32 && (this.introTicks - 32) % 5 == 0 && this.introTicks - 32 < 32) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERPANIC.get(), 1.0F, 1.0F);
            }

            if (this.introTicks - 20 == 34) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 1.0F, 1.0F);
            }

            if (this.introTicks - 20 == 36) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERPANIC.get(), 1.0F, 1.2F);
                this.setItemSlot(EquipmentSlot.OFFHAND, PotionUtils.setPotion(new ItemStack(Items.POTION), PotionRegisterer.MUTATION.get()));
            }

            if (this.introTicks - 20 == 44) {
                if (!this.level().isClientSide) {
                    this.setVillagerFace(1);
                }

                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_FORCEPOTION.get(), 1.0F, 1.0F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERPANIC.get(), 1.0F, 1.3F);
                this.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
            }

            if (this.introTicks - 20 == 52 || this.introTicks - 20 == 58 || this.introTicks - 20 == 65) {
                this.playSound(SoundEvents.WITCH_DRINK, 1.0F, 1.0F);
            }

            if (this.introTicks - 20 == 74 && !this.level().isClientSide) {
                this.setVillagerFace(2);
            }

            if (this.introTicks - 20 == 93) {
                if (!this.level().isClientSide) {
                    this.setVillagerFace(3);
                }

                this.playSound(SoundEvents.VILLAGER_TRADE, 1.0F, 1.0F);
            }

            if (this.introTicks - 20 == 104) {
                this.playSound(SoundEvents.TNT_PRIMED, 1.0F, 1.0F);
            }

            if (this.introTicks - 20 == 108) {
                if (!this.level().isClientSide) {
                    this.setVillagerFace(0);
                }

                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_VILLAGERHISS.get(), 1.0F, 1.0F);
            }

            if (this.introTicks - 20 == 116 && !this.level().isClientSide) {
                this.setVillagerFace(4);
            }

            if (this.introTicks - 20 == 132) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SPAWN.get(), 1.0F, 1.0F);
            }

            if (this.introTicks - 20 == 158) {
                LightningBolt lightning = EntityType.LIGHTNING_BOLT.create(this.level());

                assert lightning != null;

                lightning.setPos(this.getX(), this.getY(), this.getZ());
                lightning.setVisualOnly(true);
                this.playSound(SoundEvents.LIGHTNING_BOLT_IMPACT, 3.0F, 1.0F);
                this.playSound(SoundEvents.LIGHTNING_BOLT_THUNDER, 10000.0F, 1.0F);
                this.level().addFreshEntity(lightning);
                CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.2F, 0, 10);
                if (!this.level().isClientSide) {
                    this.level().explode(this, this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX(), this.getY(), this.getZ(), 4.0F, Level.ExplosionInteraction.NONE);
                }

                ragno = ModEntityTypes.OldRagno.get().create(this.level());

                assert ragno != null;

                ragno.setPos(this.getX(), this.getY(), this.getZ());
                ragno.setDeltaMovement(0.0, 0.6, 0.0);
                ragno.setTarget(this.getTarget());
                ragno.setOwner(this);
                if (this.getTarget() != null) {
                    ragno.lookAt(this.getTarget(), 30.0F, 30.0F);
                }

                this.ragno = ragno;
                this.level().addFreshEntity(ragno);
                if (!this.level().isClientSide) {
                    this.startRiding(ragno);
                }

                ragno.playIntro();
                this.makeRagnoParticles(ragno);
                ragno.setCanJoinRaid(true);
                if (this.getTeam() != null) {
                    this.level().getScoreboard().addPlayerToTeam(ragno.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                }

                this.setAnimationState(0);
                if (!this.level().isClientSide) {
                    this.setShowVillager(false);
                }
            }

            if (this.introTicks - 158 == 50) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_LAUGH.get(), 2.0F, 1.0F);
                this.setAnimationState(2);
            }

            if (this.introTicks - 208 == 50) {
                this.setActive(true);
                this.setAnimationState(0);
                if (!this.level().isClientSide) {
                    this.setShowArms(false);
                }
            }

            if (this.introTicks - 20 == 5 && !this.level().isClientSide) {
                this.setShowVillager(true);
            }
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

        if (!this.isPassenger()) {
            List<OldRagnoEntity> ragnolist = this.level().getEntitiesOfClass(OldRagnoEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == this && predicate.isAlive());
            if (!ragnolist.isEmpty()) {
                ragno = ragnolist.get(0);
                this.getNavigation().moveTo(ragno, 2.0);
                if (this.distanceToSqr(ragno) < 9.0 && !this.level().isClientSide) {
                    this.startRiding(ragno);
                }
            }
        }

        this.updateTreatList();
        this.distractAttackers();
        if (this.isAlive()) {
            if (this.attackType == BOMBS_ATTACK && this.attackTicks == 20) {
                double throwSpeed = 0.7;
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_CYMBAL.get(), 1.0F, 1.0F);

                for (int i = 0; i < 4; ++i) {
                    if (this.getHealth() < this.getMaxHealth() / 2.0F) {
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

            double y;
            double z;
            double d;
            float power;
            double motionX;
            double motionY;
            double motionZ;
            LivingEntity entity;
            OldAxeEntity projectile;
            double x;
            if (this.attackType == AXES_ATTACK) {
                entity = this.getTarget();
                if (this.attackTicks % 28 == 0) {
                    this.setAnimationState(0);
                    this.setAnimationState(4);
                }

                if (this.attackTicks % 28 == 2) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 2.0F, 1.0F);
                }

                if (entity != null && this.attackTicks % 28 == 6) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
                    if (!this.level().isClientSide) {
                        projectile = ModEntityTypes.OldAxe.get().create(this.level());

                        assert projectile != null;

                        projectile.setPos(this.getX(), this.getY() + 1.0, this.getZ());
                        projectile.setYHeadRot(this.getYHeadRot());
                        projectile.setYRot(this.getYHeadRot());
                        x = projectile.getX() - entity.getX();
                        y = projectile.getY() - (entity.getY() + 1.5);
                        z = projectile.getZ() - entity.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        power = 3.5F;
                        motionX = -(x / d * (double) power * 0.2);
                        motionY = -(y / d * (double) power * 0.2);
                        motionZ = -(z / d * (double) power * 0.2);
                        projectile.setAcceleration(motionX, motionY, motionZ);
                        projectile.setShooter(this);
                        this.level().addFreshEntity(projectile);
                    }
                }

                if (this.attackTicks % 28 == 14) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
                    this.setLeftHanded(true);
                }

                if (this.attackTicks % 28 == 16) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 2.0F, 1.0F);
                }

                if (entity != null && this.attackTicks % 28 == 22) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
                    if (!this.level().isClientSide) {
                        projectile = ModEntityTypes.OldAxe.get().create(this.level());

                        assert projectile != null;

                        projectile.setPos(this.getX(), this.getY() + 1.0, this.getZ());
                        projectile.setYHeadRot(this.getYHeadRot());
                        projectile.setYRot(this.getYHeadRot());
                        x = projectile.getX() - entity.getX();
                        y = projectile.getY() - (entity.getY() + 1.5);
                        z = projectile.getZ() - entity.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        power = 3.5F;
                        motionX = -(x / d * (double) power * 0.2);
                        motionY = -(y / d * (double) power * 0.2);
                        motionZ = -(z / d * (double) power * 0.2);
                        projectile.setAcceleration(motionX, motionY, motionZ);
                        projectile.setShooter(this);
                        this.level().addFreshEntity(projectile);
                    }
                }

                if (this.attackTicks % 28 == 27) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
                    this.setLeftHanded(false);
                }
            }

            if (this.attackType == FAST_AXES_ATTACK) {
                entity = this.getTarget();
                if (this.attackTicks % 12 == 0) {
                    this.setAnimationState(0);
                    this.setAnimationState(5);
                }

                if (this.attackTicks % 12 == 1) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 2.0F, 1.0F);
                }

                if (entity != null && this.attackTicks % 12 == 3) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
                    if (!this.level().isClientSide) {
                        projectile = ModEntityTypes.OldAxe.get().create(this.level());

                        assert projectile != null;

                        projectile.setPos(this.getX(), this.getY() + 1.0, this.getZ());
                        projectile.setYHeadRot(this.getYHeadRot());
                        projectile.setYRot(this.getYHeadRot());
                        x = projectile.getX() - entity.getX();
                        y = projectile.getY() - (entity.getY() + 1.5);
                        z = projectile.getZ() - entity.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        power = 3.5F;
                        motionX = -(x / d * (double) power * 0.2);
                        motionY = -(y / d * (double) power * 0.2);
                        motionZ = -(z / d * (double) power * 0.2);
                        projectile.setAcceleration(motionX, motionY, motionZ);
                        projectile.setShooter(this);
                        this.level().addFreshEntity(projectile);
                    }
                }

                if (this.attackTicks % 12 == 6) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
                    this.setLeftHanded(true);
                }

                if (this.attackTicks % 12 == 7) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 2.0F, 1.0F);
                }

                if (entity != null && this.attackTicks % 12 == 10) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
                    if (!this.level().isClientSide) {
                        projectile = ModEntityTypes.OldAxe.get().create(this.level());

                        assert projectile != null;

                        projectile.setPos(this.getX(), this.getY() + 1.0, this.getZ());
                        projectile.setYHeadRot(this.getYHeadRot());
                        projectile.setYRot(this.getYHeadRot());
                        x = projectile.getX() - entity.getX();
                        y = projectile.getY() - (entity.getY() + 1.5);
                        z = projectile.getZ() - entity.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        power = 3.5F;
                        motionX = -(x / d * (double) power * 0.2);
                        motionY = -(y / d * (double) power * 0.2);
                        motionZ = -(z / d * (double) power * 0.2);
                        projectile.setAcceleration(motionX, motionY, motionZ);
                        projectile.setShooter(this);
                        this.level().addFreshEntity(projectile);
                    }
                }

                if (this.attackTicks % 12 == 11) {
                    this.setItemSlot(EquipmentSlot.MAINHAND, Items.IRON_AXE.getDefaultInstance());
                    this.setLeftHanded(false);
                }
            }

            if (this.attackType == POTIONS_ATTACK) {
                if (this.attackTicks == 10) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_SPIN.get(), 2.0F, 1.0F);
                    this.potionThrowDistance = 0.0;
                }

                if (this.attackTicks >= 10 && this.attackTicks <= 50) {
                    this.makePotionParticles();
                }

                if (this.attackTicks >= 20 && this.attackTicks <= 50) {
                    this.potionThrowDistance += 0.02;

                    for (int i = 0; i < 2; ++i) {
                        if (!this.level().isClientSide) {
                            DarkPotionEntity potionentity = ModEntityTypes.DarkPotion.get().create(this.level());

                            assert potionentity != null;

                            potionentity.setPos(this.getX(), this.getY() + 2.0, this.getZ());
                            potionentity.setOwner(this);
                            potionentity.setItem(PotionUtils.setPotion(new ItemStack(Items.SPLASH_POTION), PotionRegisterer.MUTATION.get()));
                            potionentity.setXRot(-20.0F);
                            potionentity.setDeltaMovement((-2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble()) * (this.potionThrowDistance / 4.0), 1.0, (-2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble()) * (this.potionThrowDistance / 4.0));
                            this.level().addFreshEntity(potionentity);
                        }
                    }
                }
            }

            if (this.attackType == SCYTHE_ATTACK) {
                entity = this.getTarget();
                if (entity != null) {
                    if (this.attackTicks == 14) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_THROW.get(), 2.0F, 1.0F);
                    }

                    if (this.attackTicks == 16) {
                        this.waitingForScythe = true;
                        if (!this.level().isClientSide) {
                            this.setShowScythe(false);
                        }

                        OldScytheEntity scythe = ModEntityTypes.OldScythe.get().create(this.level());

                        assert scythe != null;

                        scythe.setPos(this.getX(), this.getY() + 1.5, this.getZ());
                        x = scythe.getX() - entity.getX();
                        y = scythe.getY() - entity.getY();
                        z = scythe.getZ() - entity.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        power = 3.0F;
                        motionX = -(x / d * (double) power * 0.2);
                        motionY = -(y / d * (double) power * 0.2);
                        motionZ = -(z / d * (double) power * 0.2);
                        scythe.setAcceleration(motionX, motionY, motionZ);
                        scythe.halfHealth = this.getHealth() < this.getMaxHealth() / 2.0F;
                        scythe.setGoFor(entity);
                        scythe.setShooter(this);
                        this.level().addFreshEntity(scythe);
                    }
                }
            }

            if (this.attackType == TRICKORTREAT_ATTACK && this.attackTicks == 21) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_CYMBAL.get(), 2.0F, 1.0F);
                int amount = 7;

                for (int i = 0; i < amount; ++i) {
                    TrickOrTreatEntity treat = ModEntityTypes.TrickOrTreat.get().create(this.level());

                    assert treat != null;

                    treat.circleTime = i * 20;
                    treat.bounceTime = i;
                    treat.setPos(this.getX(), this.getY(), this.getZ());
                    treat.setOwner(this);
                    treat.setOld(true);
                    Objects.requireNonNull(treat.getAttribute(Attributes.MAX_HEALTH)).setBaseValue(12.0);
                    treat.heal(50);
                    treat.setTreat(this.random.nextInt(5) + 1);
                    if (this.getTeam() != null) {
                        this.level().getScoreboard().addPlayerToTeam(treat.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                    }

                    this.circleTreat(treat, i, amount);
                    this.level().addFreshEntity(treat);
                    this.treats.add(treat);
                }
            }
        }

    }

    public boolean startRiding(Entity p_20330_) {
        return (p_20330_ instanceof OldRagnoEntity || p_20330_ instanceof CrocofangEntity || p_20330_ instanceof Ravager) && super.startRiding(p_20330_);
    }

    public void die(DamageSource p_37847_) {
        if (!this.treats.isEmpty()) {

            for (TrickOrTreatEntity treat : this.treats) {
                treat.kill();
            }
        }

        Entity var5 = this.getVehicle();
        if (var5 instanceof OldRagnoEntity ragno) {
            ItemEntity bag = EntityType.ITEM.create(this.level());

            assert bag != null;

            bag.setItem(ItemRegisterer.BAG_OF_HORRORS.get().getDefaultInstance());
            bag.setPos(this.getX(), this.getY(), this.getZ());
            bag.setDeltaMovement(0.0, 0.6, 0.0);
            bag.setNeverPickUp();
            bag.setUnlimitedLifetime();
            bag.noPhysics = true;
            this.level().addFreshEntity(bag);
            ragno.item = bag;
        }

        super.die(p_37847_);
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

    public int getVillagerFace() {
        return this.entityData.get(VILLAGER_FACE);
    }

    public void setVillagerFace(int face) {
        this.entityData.set(VILLAGER_FACE, face);
    }

    public boolean hurt(DamageSource source, float p_37850_) {
        if (!this.isActive() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            p_37850_ = 0.0F;
            if (source.getEntity() != null && this.introTicks == 0 && !this.areIllagersNearby()) {
                this.introTicks = 1;
                if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
                    this.getCurrentRaid().ticksActive = 0L;
                }
            }
        }

        if (this.areIllagersNearby() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            return false;
        } else {
            return !source.is(DamageTypes.IN_WALL) && super.hurt(source, p_37850_);
        }
    }

    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_LAUGH.get();
    }

    protected SoundEvent getAmbientSound() {
        return this.introTicks > 1 ? null : IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_DEATH.get();
    }

    public boolean canBeLeader() {
        return false;
    }

    public void setAnimationState(int input) {
        this.entityData.set(ANIMATION_STATE, input);
    }

    public int getAnimationState() {
        return this.entityData.get(OldFreakagerEntity.ANIMATION_STATE);
    }

    public AnimationState getAnimationState(String input) {
        if (Objects.equals(input, "intro")) {
            return this.introAnimationState;
        } else if (Objects.equals(input, "laugh")) {
            return this.laughAnimationState;
        } else if (Objects.equals(input, "bombs")) {
            return this.bombsAnimationState;
        } else if (Objects.equals(input, "axes")) {
            return this.axesAnimationState;
        } else if (Objects.equals(input, "fastaxes")) {
            return this.fastaxesAnimationState;
        } else if (Objects.equals(input, "potions")) {
            return this.potionsAnimationState;
        } else if (Objects.equals(input, "scythe")) {
            return this.scytheAnimationState;
        } else {
            return Objects.equals(input, "trickortreat") ? this.trickortreatAnimationState : new AnimationState();
        }
    }

    protected void dropAllDeathLoot(DamageSource source) {
        if (this.getVehicle() == null) {
            if (this.shouldDropLoot() && this.level().getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT) && source.getDirectEntity() instanceof ScytheEntity) {
                this.level().addFreshEntity(new ItemEntity(this.level(), this.getX(), this.getY(), this.getZ(), new ItemStack(ItemRegisterer.FREAKAGER_DISC.get())));
            }
            super.dropAllDeathLoot(source);
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
                    this.laughAnimationState.start(this.tickCount);
                }
                case 3 -> {
                    this.stopAllAnimationStates();
                    this.bombsAnimationState.start(this.tickCount);
                }
                case 4 -> {
                    this.stopAllAnimationStates();
                    this.axesAnimationState.start(this.tickCount);
                }
                case 5 -> {
                    this.stopAllAnimationStates();
                    this.fastaxesAnimationState.start(this.tickCount);
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
            }
        }

        super.onSyncedDataUpdated(p_21104_);
    }

    public void stopAllAnimationStates() {
        this.introAnimationState.stop();
        this.laughAnimationState.stop();
        this.bombsAnimationState.stop();
        this.axesAnimationState.stop();
        this.fastaxesAnimationState.stop();
        this.potionsAnimationState.stop();
        this.scytheAnimationState.stop();
        this.trickortreatAnimationState.stop();
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

    protected void populateDefaultEquipmentSlots(RandomSource random, DifficultyInstance p_180481_1_) {
        this.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.IRON_AXE));
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

    public boolean shouldShowScythe() {
        return this.entityData.get(SCYTHE);
    }

    public void setShowScythe(boolean scythe) {
        this.entityData.set(SCYTHE, scythe);
    }

    public boolean isPersistenceRequired() {
        return true;
    }

    public boolean doesAttackMeetNormalRequirements() {
        return this.attackType == 0 && !this.areIllagersNearby() && this.getTarget() != null && this.hasLineOfSight(this.getTarget()) && this.isActive() && this.attackCooldown < 1;
    }

    static {
        SHOULD_DELETE_ITSELF = SynchedEntityData.defineId(OldFreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        NEARBY_ILLAGERS = SynchedEntityData.defineId(OldFreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        ACTIVE = SynchedEntityData.defineId(OldFreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        ANIMATION_STATE = SynchedEntityData.defineId(OldFreakagerEntity.class, EntityDataSerializers.INT);
        SHOW_ARMS = SynchedEntityData.defineId(OldFreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        SHOW_VILLAGER = SynchedEntityData.defineId(OldFreakagerEntity.class, EntityDataSerializers.BOOLEAN);
        VILLAGER_FACE = SynchedEntityData.defineId(OldFreakagerEntity.class, EntityDataSerializers.INT);
        SCYTHE = SynchedEntityData.defineId(OldFreakagerEntity.class, EntityDataSerializers.BOOLEAN);
    }

    class TrickOrTreatGoal extends Goal {
        public TrickOrTreatGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldFreakagerEntity.this.doesAttackMeetNormalRequirements() && OldFreakagerEntity.this.random.nextInt(16) == 0 && OldFreakagerEntity.this.trickOrTreatCooldown < 1 && OldFreakagerEntity.this.getHealth() < OldFreakagerEntity.this.getMaxHealth();
        }

        public void start() {
            OldFreakagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_TRICKORTREAT.get(), 2.0F, 1.0F);
            OldFreakagerEntity.this.setAnimationState(8);
            OldFreakagerEntity.this.attackType = TRICKORTREAT_ATTACK;
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return OldFreakagerEntity.this.attackTicks <= 30;
        }

        public void tick() {
            OldFreakagerEntity.this.getNavigation().stop();
            if (OldFreakagerEntity.this.getTarget() != null) {
                OldFreakagerEntity.this.getLookControl().setLookAt(OldFreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldFreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            OldFreakagerEntity.this.attackTicks = 0;
            OldFreakagerEntity.this.attackType = 0;
            OldFreakagerEntity.this.setAnimationState(0);
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(false);
            }

            OldFreakagerEntity.this.trickOrTreatCooldown = 900;
            OldFreakagerEntity.this.attackCooldown = 100;
        }
    }

    class ScytheGoal extends Goal {
        public ScytheGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldFreakagerEntity.this.doesAttackMeetNormalRequirements() && OldFreakagerEntity.this.random.nextInt(16) == 0 && OldFreakagerEntity.this.scytheCooldown < 1;
        }

        public void start() {
            OldFreakagerEntity.this.setAnimationState(7);
            OldFreakagerEntity.this.attackType = SCYTHE_ATTACK;
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowScythe(true);
                OldFreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return OldFreakagerEntity.this.attackTicks <= 24 || OldFreakagerEntity.this.waitingForScythe;
        }

        public void tick() {
            OldFreakagerEntity.this.getNavigation().stop();
            if (OldFreakagerEntity.this.getTarget() != null) {
                OldFreakagerEntity.this.getLookControl().setLookAt(OldFreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldFreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            OldFreakagerEntity.this.attackTicks = 0;
            OldFreakagerEntity.this.attackType = 0;
            OldFreakagerEntity.this.setAnimationState(0);
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(false);
            }

            OldFreakagerEntity.this.scytheCooldown = 200;
            OldFreakagerEntity.this.attackCooldown = 100;
        }
    }

    class PotionsGoal extends Goal {
        public PotionsGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldFreakagerEntity.this.doesAttackMeetNormalRequirements() && OldFreakagerEntity.this.random.nextInt(16) == 0 && OldFreakagerEntity.this.potionsCooldown < 1;
        }

        public void start() {
            OldFreakagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_REVEAL.get(), 2.0F, 1.0F);
            OldFreakagerEntity.this.setAnimationState(6);
            OldFreakagerEntity.this.attackType = POTIONS_ATTACK;
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return OldFreakagerEntity.this.attackTicks <= 60;
        }

        public void tick() {
            OldFreakagerEntity.this.getNavigation().stop();
            if (OldFreakagerEntity.this.getTarget() != null) {
                OldFreakagerEntity.this.getLookControl().setLookAt(OldFreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldFreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            OldFreakagerEntity.this.attackTicks = 0;
            OldFreakagerEntity.this.attackType = 0;
            OldFreakagerEntity.this.setAnimationState(0);
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(false);
            }

            OldFreakagerEntity.this.potionsCooldown = 200;
            OldFreakagerEntity.this.attackCooldown = 100;
        }
    }

    class FastAxesGoal extends Goal {
        public FastAxesGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldFreakagerEntity.this.doesAttackMeetNormalRequirements() && OldFreakagerEntity.this.random.nextInt(16) == 0 && OldFreakagerEntity.this.axesCooldown < 1 && OldFreakagerEntity.this.getHealth() < OldFreakagerEntity.this.getMaxHealth() / 2.0F;
        }

        public void start() {
            OldFreakagerEntity.this.setAnimationState(5);
            OldFreakagerEntity.this.attackType = FAST_AXES_ATTACK;
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return OldFreakagerEntity.this.attackTicks <= 60;
        }

        public void tick() {
            OldFreakagerEntity.this.getNavigation().stop();
            if (OldFreakagerEntity.this.getTarget() != null) {
                OldFreakagerEntity.this.getLookControl().setLookAt(OldFreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldFreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            OldFreakagerEntity.this.attackTicks = 0;
            OldFreakagerEntity.this.attackType = 0;
            OldFreakagerEntity.this.setAnimationState(0);
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(false);
            }

            OldFreakagerEntity.this.axesCooldown = 200;
            OldFreakagerEntity.this.attackCooldown = 100;
        }
    }

    class AxesGoal extends Goal {
        public AxesGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldFreakagerEntity.this.doesAttackMeetNormalRequirements() && OldFreakagerEntity.this.random.nextInt(16) == 0 && OldFreakagerEntity.this.axesCooldown < 1 && OldFreakagerEntity.this.getHealth() >= OldFreakagerEntity.this.getMaxHealth() / 2.0F;
        }

        public void start() {
            OldFreakagerEntity.this.setAnimationState(4);
            OldFreakagerEntity.this.attackType = AXES_ATTACK;
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return OldFreakagerEntity.this.attackTicks <= 82;
        }

        public void tick() {
            OldFreakagerEntity.this.getNavigation().stop();
            if (OldFreakagerEntity.this.getTarget() != null) {
                OldFreakagerEntity.this.getLookControl().setLookAt(OldFreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldFreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            OldFreakagerEntity.this.attackTicks = 0;
            OldFreakagerEntity.this.attackType = 0;
            OldFreakagerEntity.this.setAnimationState(0);
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(false);
            }

            OldFreakagerEntity.this.axesCooldown = 200;
            OldFreakagerEntity.this.attackCooldown = 100;
        }
    }

    class ThrowBombsGoal extends Goal {
        public ThrowBombsGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldFreakagerEntity.this.doesAttackMeetNormalRequirements() && OldFreakagerEntity.this.random.nextInt(16) == 0 && OldFreakagerEntity.this.bombsCooldown < 1;
        }

        public void start() {
            OldFreakagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_PUMPKINBOMBS.get(), 2.0F, 1.0F);
            OldFreakagerEntity.this.setAnimationState(3);
            OldFreakagerEntity.this.attackType = BOMBS_ATTACK;
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean canContinueToUse() {
            return OldFreakagerEntity.this.attackTicks <= 30;
        }

        public void tick() {
            OldFreakagerEntity.this.getNavigation().stop();
            if (OldFreakagerEntity.this.getTarget() != null) {
                OldFreakagerEntity.this.getLookControl().setLookAt(OldFreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldFreakagerEntity.this.navigation.stop();
        }

        public void stop() {
            OldFreakagerEntity.this.attackTicks = 0;
            OldFreakagerEntity.this.attackType = 0;
            OldFreakagerEntity.this.setAnimationState(0);
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(false);
            }

            OldFreakagerEntity.this.bombsCooldown = 200;
            OldFreakagerEntity.this.attackCooldown = 100;
        }
    }

    class IntroGoal extends Goal {
        public IntroGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.MOVE, Flag.LOOK));
        }

        public boolean canUse() {
            return OldFreakagerEntity.this.entityData.get(OldFreakagerEntity.ANIMATION_STATE) == 1;
        }

        public void start() {
            OldFreakagerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_REVEAL.get(), 1.0F, 1.0F);
            if (!OldFreakagerEntity.this.level().isClientSide) {
                OldFreakagerEntity.this.setShowArms(true);
            }

        }

        public boolean requiresUpdateEveryTick() {
            return true;
        }

        public void tick() {
            OldFreakagerEntity.this.getNavigation().stop();
            if (OldFreakagerEntity.this.getTarget() != null && OldFreakagerEntity.this.introTicks < 40) {
                OldFreakagerEntity.this.getLookControl().setLookAt(OldFreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldFreakagerEntity.this.navigation.stop();
        }

        public boolean canContinueToUse() {
            return OldFreakagerEntity.this.entityData.get(OldFreakagerEntity.ANIMATION_STATE) == 1;
        }
    }

    class AlwaysWatchTargetGoal extends Goal {
        public AlwaysWatchTargetGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public boolean canUse() {
            return OldFreakagerEntity.this.getTarget() != null && (OldFreakagerEntity.this.introTicks < 40 || OldFreakagerEntity.this.isActive());
        }

        public boolean canContinueToUse() {
            return OldFreakagerEntity.this.getTarget() != null && (OldFreakagerEntity.this.introTicks < 40 || OldFreakagerEntity.this.isActive());
        }

        public void tick() {
            OldFreakagerEntity.this.getNavigation().stop();
            if (OldFreakagerEntity.this.getTarget() != null) {
                OldFreakagerEntity.this.getLookControl().setLookAt(OldFreakagerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldFreakagerEntity.this.navigation.stop();
        }
    }
}

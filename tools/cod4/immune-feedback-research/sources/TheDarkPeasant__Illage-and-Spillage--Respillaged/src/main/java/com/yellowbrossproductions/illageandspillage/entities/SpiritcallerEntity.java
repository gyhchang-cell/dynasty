package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.sound.BossMusicPlayer;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.goal.WatchBossIntroGoal;
import com.yellowbrossproductions.illageandspillage.entities.projectile.SoulBeamEntity;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Direction.Axis;
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
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Ravager;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.network.PacketDistributor;

import javax.annotation.Nullable;
import java.time.LocalDate;
import java.time.temporal.ChronoField;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.Iterator;
import java.util.List;

public class SpiritcallerEntity extends AbstractIllager {
    public ServerBossEvent bossEvent;
    private static final EntityDataAccessor<Boolean> SHOULD_DELETE_ITSELF;
    private static final EntityDataAccessor<Boolean> NEARBY_ILLAGERS;
    private static final EntityDataAccessor<Boolean> ACTIVE;
    private static final EntityDataAccessor<Integer> WINGS_FRAME;
    private static final EntityDataAccessor<Boolean> RITUAL;
    private static final EntityDataAccessor<Boolean> ARMS_UPWARD;
    private static final EntityDataAccessor<Boolean> SPINNING;
    private static final EntityDataAccessor<Boolean> PHASED_OUT;
    private static final EntityDataAccessor<Integer> SOUL_POWER;
    private static final EntityDataAccessor<Boolean> FAKING;
    private static final EntityDataAccessor<Boolean> CHARGING;
    private static final EntityDataAccessor<Boolean> FORCEFIELD;
    private static final EntityDataAccessor<Boolean> CLAP;
    private static final EntityDataAccessor<Boolean> SHOW_SPIRIT_HANDS;
    private static final EntityDataAccessor<Boolean> CHARGING_LASER;
    private static final EntityDataAccessor<Boolean> SHOOTING_LASER;
    private float clientSideWingsAnimationO;
    private float clientSideWingsAnimation;
    private int ritualTicks;
    private int attackTicks;
    private int attackType;
    private int stealSoulsCooldown;
    private int spinDirection;
    private final List<LivingEntity> stolen_mobs = new ArrayList<>();
    private final List<MobSpiritEntity> spirits = new ArrayList<>();
    int SPIRIT_STEAL = 1;
    int SOUL_SWARM = 2;
    int IMP_RISE = 3;
    int SPIRIT_HANDS = 4;
    int SOUL_LASER = 5;
    int ANTICHEESE = 6;
    double chargeX;
    double chargeY;
    double chargeZ;
    double targetX;
    double targetY;
    double targetZ;
    private int chargeTime;
    private int attackCooldown;
    private int spiritSwarmCooldown;
    private int impRiseCooldown;
    private int spiritHandsCooldown;
    private int soulLaserCooldown;
    private int antiCheeseCooldown;
    private int dodgeCooldown;
    private int impAttacks;
    double laserX;
    double laserY;
    double laserZ;
    int stuckTime;
    private DamageSource lastDamageSource;

    public SpiritcallerEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 50;
        bossEvent = (ServerBossEvent) (new ServerBossEvent(this.getDisplayName(), BossEvent.BossBarColor.PURPLE, BossEvent.BossBarOverlay.PROGRESS)).setDarkenScreen(true);
        bossEvent.setVisible(false);
        this.getAttribute(Attributes.MAX_HEALTH).setBaseValue(Config.CommonConfig.spiritcaller_health.get());
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
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new AntiCheeseGoal());
        this.goalSelector.addGoal(0, new StealSoulsGoal());
        this.goalSelector.addGoal(0, new SoulSwarmGoal());
        this.goalSelector.addGoal(0, new ImpRiseGoal());
        this.goalSelector.addGoal(0, new SpiritHandsGoal());
        this.goalSelector.addGoal(0, new SoulLaserGoal());
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
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 1).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 96.0);
    }

    public boolean causeFallDamage(float p_147187_, float p_147188_, DamageSource p_147189_) {
        return false;
    }

    public boolean canAttack(LivingEntity p_213336_1_) {
        return !this.areIllagersNearby() && super.canAttack(p_213336_1_);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(SHOULD_DELETE_ITSELF, false);
        this.entityData.define(NEARBY_ILLAGERS, false);
        this.entityData.define(ACTIVE, false);
        this.entityData.define(WINGS_FRAME, 0);
        this.entityData.define(RITUAL, false);
        this.entityData.define(ARMS_UPWARD, false);
        this.entityData.define(SPINNING, false);
        this.entityData.define(PHASED_OUT, false);
        this.entityData.define(SOUL_POWER, 0);
        this.entityData.define(FAKING, false);
        this.entityData.define(CHARGING, false);
        this.entityData.define(FORCEFIELD, false);
        this.entityData.define(CLAP, false);
        this.entityData.define(SHOW_SPIRIT_HANDS, false);
        this.entityData.define(CHARGING_LASER, false);
        this.entityData.define(SHOOTING_LASER, false);
    }

    public void addAdditionalSaveData(CompoundTag p_37870_) {
        super.addAdditionalSaveData(p_37870_);
        if (this.isActive()) {
            p_37870_.putBoolean("active", true);
        }

        p_37870_.putInt("SoulPower", this.getSoulPower());
    }

    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        this.bossEvent.setName(this.getDisplayName());
        this.setActive(tag.getBoolean("active"));
        this.setSoulPower(tag.getInt("SoulPower"));
        if (tag.contains("Health", 99)) {
            this.entityData.set(DATA_HEALTH_ID, Mth.clamp(tag.getFloat("Health"), 0.0F, this.getMaxHealth()));
        }
    }

    public void setHealth(float p_21154_) {
        float healthValue = p_21154_ - this.getHealth();
        if (healthValue > 0 || (!this.areIllagersNearby() && this.isActive()) || healthValue <= -1000000000000.0F) {
            super.setHealth(p_21154_);
        }
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public SoundEvent getBossMusic() {
        LocalDate localdate = LocalDate.now();
        int i = localdate.get(ChronoField.DAY_OF_MONTH);
        int j = localdate.get(ChronoField.MONTH_OF_YEAR);
        return j == 4 && i == 1 ? IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_MUSIC_APRIL.get() : IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_MUSIC.get();
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
                double d0;
                double d1;
                double d2;
                for (i = 0; i < 250; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.DRAGON_BREATH, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 200; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.POOF, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 150; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.LARGE_SMOKE, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeCheeseParticles() {
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
                for (i = 0; i < 250; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.FLAME, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 200; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.FLAME, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 150; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
                    packet.queueParticle(ParticleTypes.FLAME, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
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

    public void makePoofParticles(Entity entity, Level level) {
        if (!level.isClientSide) {
            for (int i = 0; i < 20; ++i) {
                double d0 = this.random.nextGaussian() * 0.02D;
                double d1 = this.random.nextGaussian() * 0.02D;
                double d2 = this.random.nextGaussian() * 0.02D;
                ((ServerLevel) level).sendParticles(ParticleTypes.POOF, entity.getRandomX(1.0D), entity.getRandomY(), entity.getRandomZ(1.0D), 1, d0, d1, d2, 0);
            }
        }
    }

    public void tick() {
        this.bossEvent.setProgress(this.getHealth() / this.getMaxHealth());

        this.updateMobList();
        List<Raider> list = this.level().getEntitiesOfClass(Raider.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.hasActiveRaid() && !predicate.getType().is(ModTags.EntityTypes.ILLAGER_BOSSES));
        if (Config.CommonConfig.spiritcaller_forcefield.get() && this.hasActiveRaid()) {
            if (!this.level().isClientSide) {
                this.setIllagersNearby(!list.isEmpty());
            }

            if (this.areIllagersNearby()) {
                this.setTarget(null);
            }
        }

        if (this.hasActiveRaid()) {
            if (this.getCurrentRaid() != null && this.getCurrentRaid().getGroupsSpawned() == 7 && this.shouldRemoveItself() && Config.CommonConfig.spiritcaller_onlyOneAllowed.get()) {
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

        if (this.ritualTicks > 0 && !this.isActive() && this.isAlive()) {
            ++this.ritualTicks;
            if (this.ritualTicks == 30) {
                if (Config.CommonConfig.mobs_watch_intros.get()) {
                    List<Mob> list1 = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(50.0));
                    for (Mob mob : list1) {
                        mob.goalSelector.addGoal(0, new WatchBossIntroGoal(mob, this));
                    }
                }

                EntityUtil.mobFollowingSound(this.level(), this, IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_INTRO.get(), 2.0F, 1.0F, false);

                if (!this.level().isClientSide) {
                    this.setRitual(true);
                }
            }

            if (this.ritualTicks >= 145) {
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

                this.attackCooldown = 100;
                this.setActive(true);
                this.setRitual(false);
            }
        }

        if (!this.level().isClientSide && this.isActive() && this.getBossMusic() != null) {
            if (this.canPlayMusic()) {
                this.level().broadcastEntityEvent(this, (byte) 67);
            } else {
                this.level().broadcastEntityEvent(this, (byte) 68);
            }
        }

        if (this.attackType > 0) {
            ++this.attackTicks;
        } else {
            this.attackTicks = 0;
        }

        if (this.stealSoulsCooldown > 0 && this.stolen_mobs.isEmpty()) {
            --this.stealSoulsCooldown;
        }

        if (this.attackCooldown > 0) {
            --this.attackCooldown;
        }

        if (this.isActive() && this.attackType == 0 && this.getTarget() != null && this.tickCount % 20 == 10) {
            if (!this.hasLineOfSight(this.getTarget())) {
                ++this.stuckTime;
            } else if (this.stuckTime > 0) {
                --this.stuckTime;
            }
        }

        if (this.spiritSwarmCooldown > 0) {
            --this.spiritSwarmCooldown;
        }

        if (this.impRiseCooldown > 0) {
            --this.impRiseCooldown;
        }

        if (this.spiritHandsCooldown > 0) {
            --this.spiritHandsCooldown;
        }

        if (this.soulLaserCooldown > 0) {
            --this.soulLaserCooldown;
        }

        if (this.antiCheeseCooldown > 0) {
            --this.antiCheeseCooldown;
        }

        LivingEntity toBeAttacked;
        float power;
        float radius2;
        if (this.isAlive()) {
            if (this.attackType == this.SPIRIT_STEAL && !this.stolen_mobs.isEmpty()) {

                for (LivingEntity stolen_mob : this.stolen_mobs) {
                    toBeAttacked = stolen_mob;
                    toBeAttacked.hurt(this.damageSources().mobAttack(this), 0.0F);
                    toBeAttacked.setDeltaMovement(-0.5 + this.random.nextDouble(), toBeAttacked.getDeltaMovement().y, -0.5 + this.random.nextDouble());
                }
            }

            if (this.attackType == this.SOUL_SWARM) {
                if (this.attackTicks > 10 && this.attackTicks <= 55) {
                    for (int i = 0; i < this.getSoulPower() + 1; ++i) {
                        if (!this.level().isClientSide) {
                            IllagerSoulEntity soul = ModEntityTypes.IllagerSoul.get().create(this.level());

                            assert soul != null;

                            soul.setPos(this.getX() + (double) (-10 - this.getSoulPower() + this.random.nextInt(20 + this.getSoulPower() * 2)), this.getY() + (double) (-1 + this.random.nextInt(10 + this.getSoulPower() * 2)), this.getZ() + (double) (-10 - this.getSoulPower() + this.random.nextInt(20 + this.getSoulPower() * 2)));
                            soul.setOwner(this);
                            soul.setAngelOrDevil(this.random.nextBoolean());
                            soul.setTarget(this.getTarget());
                            soul.setDeltaMovement(0.0, 0.1, 0.0);
                            if (this.getTeam() != null) {
                                this.level().getScoreboard().addPlayerToTeam(soul.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                            }

                            this.level().addFreshEntity(soul);
                        }
                    }
                }

                if (this.attackTicks == 18 && !this.level().isClientSide) {
                    this.setArmsUpward(false);
                    this.setSpinning(true);
                }

                if (this.attackTicks > 18 && this.attackTicks < 55 && !this.level().isClientSide) {
                    this.setFaking(this.random.nextBoolean());
                }

                if (this.attackTicks == 55) {
                    if (!this.level().isClientSide) {
                        this.setSpinning(false);
                        this.setArmsUpward(true);
                        this.setFaking(true);
                    }

                    this.setDeltaMovement(0.0, 0.3, 0.0);
                }
            }

            if (this.attackType == this.IMP_RISE) {
                if (this.attackTicks == 37) {
                    this.setArmsUpward(false);
                    this.setClap(true);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_CLAP.get(), 2.0F, 1.0F);
                }

                if (this.attackTicks == 40) {
                    this.impAttacks = this.random.nextInt(3) + 1;
                    if (this.impAttacks == 1) {
                        this.createLineImps();
                    }

                    if (this.impAttacks == 2) {
                        this.createRandomImps();
                    }

                    if (this.impAttacks == 3) {
                        this.createRingImps();
                    }
                }

                if (this.attackTicks == 50) {
                    this.setArmsUpward(true);
                    this.setClap(false);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_IMPRISE.get(), 2.0F, 1.0F);
                }

                if (this.attackTicks == 87) {
                    this.setArmsUpward(false);
                    this.setClap(true);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_CLAP.get(), 2.0F, 1.0F);
                }

                if (this.attackTicks == 90) {
                    this.impAttacks = this.random.nextInt(3) + 1;
                    if (this.impAttacks == 1) {
                        this.createLineImps();
                    }

                    if (this.impAttacks == 2) {
                        this.createRandomImps();
                    }

                    if (this.impAttacks == 3) {
                        this.createRingImps();
                    }
                }

                if (this.attackTicks == 100) {
                    this.setArmsUpward(true);
                    this.setClap(false);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_IMPRISE.get(), 2.0F, 1.0F);
                }

                if (this.attackTicks == 137) {
                    this.setArmsUpward(false);
                    this.setClap(true);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_CLAP.get(), 2.0F, 1.0F);
                }

                if (this.attackTicks == 140) {
                    this.impAttacks = this.random.nextInt(3) + 1;
                    if (this.impAttacks == 1) {
                        this.createLineImps();
                    }

                    if (this.impAttacks == 2) {
                        this.createRandomImps();
                    }

                    if (this.impAttacks == 3) {
                        this.createRingImps();
                    }
                }
            }

            if (this.attackType == this.SPIRIT_HANDS) {
                if (this.attackTicks == 19) {
                    this.setShowSpiritHands(true);
                }

                if (this.attackTicks == 37) {
                    this.setSpinning(false);
                    this.setClap(true);
                }

                if (this.attackTicks == 40) {
                    this.setShowSpiritHands(false);
                    SpiritHandEntity hand1 = ModEntityTypes.SpiritHand.get().create(this.level());

                    assert hand1 != null;

                    hand1.setPos(this.getX(), this.getY() + 1.0, this.getZ());
                    hand1.setGoodOrEvil(true);
                    hand1.setDeltaMovement((-0.5 + this.random.nextDouble()) / 2.0, (-0.5 + this.random.nextDouble()) / 2.0, (-0.5 + this.random.nextDouble()) / 2.0);
                    hand1.setOwner(this);
                    hand1.setTarget(this.getTarget());
                    hand1.setPower(this.getSoulPower());
                    if (this.getTeam() != null) {
                        this.level().getScoreboard().addPlayerToTeam(hand1.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                    }

                    this.level().addFreshEntity(hand1);
                    SpiritHandEntity hand2 = ModEntityTypes.SpiritHand.get().create(this.level());

                    assert hand2 != null;

                    hand2.setPos(this.getX(), this.getY() + 1.0, this.getZ());
                    hand2.setGoodOrEvil(false);
                    hand2.setDeltaMovement((-0.5 + this.random.nextDouble()) / 2.0, (-0.5 + this.random.nextDouble()) / 2.0, (-0.5 + this.random.nextDouble()) / 2.0);
                    hand2.setOwner(this);
                    hand2.setTarget(this.getTarget());
                    if (this.getTeam() != null) {
                        this.level().getScoreboard().addPlayerToTeam(hand2.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                    }

                    hand2.setPower(this.getSoulPower());
                    this.level().addFreshEntity(hand2);
                }
            }

            if (this.attackType == this.SOUL_LASER) {
                SoulBeamEntity beam = null;
                if (this.getTarget() != null && this.attackTicks < 85) {
                    this.setLaserPosition(this.getTarget().getX(), this.getTarget().getY() + (double) this.getTarget().getEyeHeight(), this.getTarget().getZ());
                }

                if (this.laserX != 0.0 || this.laserY != 0.0 || this.laserZ != 0.0) {
                    this.getLookControl().setLookAt(this.laserX, this.laserY, this.laserZ, 100.0F, 100.0F);
                }

                if (this.attackTicks == 100) {
                    this.setChargingLaser(false);
                    this.setShootingLaser(true);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_LASER.get(), 2.0F, 1.0F);
                    if (!this.level().isClientSide) {
                        beam = new SoulBeamEntity(ModEntityTypes.SoulBeam.get(), this.level(), this, this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0), this.getY() + 1.0, this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0), (float) ((double) (this.yHeadRot + 90.0F) * Math.PI / 180.0), (float) ((double) (-this.getXRot()) * Math.PI / 180.0), 40, this.getSoulPower());
                        this.level().addFreshEntity(beam);
                    }
                }

                if (this.attackTicks >= 100) {
                    this.setDeltaMovement(0.0, 0.0, 0.0);
                    if (beam != null) {
                        radius2 = 1.1F;
                        double x = this.getX() + 0.800000011920929 * Math.sin((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        double y = this.getY() + 1.0 + (double) radius2 * Math.sin((double) (-this.getXRot()) * Math.PI / 180.0);
                        double z = this.getZ() + 0.800000011920929 * Math.cos((double) (-this.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-this.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-this.getXRot()) * Math.PI / 180.0);
                        beam.setPos(x, y, z);
                        float yaw = this.yHeadRot + 90.0F;
                        power = -this.getXRot();
                        beam.setYaw((float) ((double) yaw * Math.PI / 180.0));
                        beam.setPitch((float) ((double) power * Math.PI / 180.0));
                        beam.setPower(this.getSoulPower());
                    }
                }
            }

            if (this.attackType == this.ANTICHEESE) {
                if (attackTicks % 2 == 1 && attackTicks < 40) {
                    if (isFaking())
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_MOBSPIRIT_HURT.get(), 0.5f, 1.0f);
                    setFaking(!this.isFaking());
                }

                if (attackTicks == 40 && this.getTarget() != null) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_ANTICHEESE.get(), 2.0F, 1.0F);
                    setArmsUpward(false);
                    makePoofParticles(this, this.level());
                    setPhasedOut(true);
                }

                if (isPhasedOut() && this.getTarget() != null) {
                    if (attackTicks <= 100) this.setPos(this.getTarget().position());
                    this.clearFire();
                    this.setDeltaMovement(0, 0, 0);
                }

                if (attackTicks == 120) {
                    CameraShakeEntity.cameraShake(this.level(), this.position(), 30.0F, 0.3F, 0, 15);
                    for (Entity entity : this.level().getEntities(this, this.getBoundingBox().inflate(15.0))) {
                        if (entity.isAlive()) {
                            if (this.distanceToSqr(entity) < 36.0) {
                                entity.hurtMarked = true;
                                entity.setSecondsOnFire(8);
                            }
                        }
                    }
                    if (!this.level().isClientSide) {
                        makeCheeseParticles();
                        this.level().explode(this, this.getX(), this.getY(), this.getZ(), 3.0F, Level.ExplosionInteraction.NONE);
                        this.level().explode(this, this.getX(), this.getY(), this.getZ(), 3.0F, Level.ExplosionInteraction.NONE);
                        this.level().explode(this, this.getX(), this.getY(), this.getZ(), 3.0F, Level.ExplosionInteraction.NONE);
                    }

                    this.setPhasedOut(false);
                    setFaking(false);
                    this.setClap(true);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_CLAP.get(), 2.0F, 1.0F);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_ANTICHEESE.get(), 2.0F, 1.0F);
                    this.createRandomImps();
                }

            }
        }

        if (this.isAlive()) {
            if (this.chargeX != 0.0 && this.chargeY != 0.0 && this.chargeZ != 0.0) {
                ++this.chargeTime;
                this.setDeltaMovement(this.chargeX, this.chargeY, this.chargeZ);
                if (!this.level().isClientSide) {
                    this.setCharging(true);
                }

                if (this.getX() - this.targetX < 1.0 && this.getX() - this.targetX > -1.0 && this.getY() - this.targetY < 1.0 && this.getY() - this.targetY > -1.0 && this.getZ() - this.targetZ < 1.0 && this.getZ() - this.targetZ > -1.0 || this.chargeTime > 60) {
                    if (!this.level().isClientSide) {
                        this.level().explode(this, this.getX(), this.getY(), this.getZ(), 2.0F, Level.ExplosionInteraction.NONE);
                        this.setFaking(false);
                    }

                    this.setCharge(0.0, 0.0, 0.0);
                    this.setTargetPosition(0.0, 0.0, 0.0);
                    this.setDeltaMovement(0.0, 0.5, 0.0);
                }
            } else {
                this.chargeTime = 0;
                if (!this.level().isClientSide) {
                    this.setCharging(false);
                }
            }
        }

        if (!this.level().isClientSide) {
            this.setForcefield(!this.stolen_mobs.isEmpty());
        }

        List attackingMobs;
        if (this.isActive()) {
            attackingMobs = this.level().getEntitiesOfClass(Projectile.class, this.getBoundingBox().inflate(10.0), (predicate) -> this.distanceToSqr(predicate) <= 90.0);

            for (Object attackingMob : attackingMobs) {
                Projectile thing = (Projectile) attackingMob;
                Vec3 aActualMotion = new Vec3(thing.getX() - thing.xo, thing.getY() - thing.yOld, thing.getZ() - thing.zo);
                if (!(aActualMotion.length() < 0.1) && thing.tickCount > 1) {
                    float dot = (float) thing.getDeltaMovement().normalize().dot(this.position().add(0.0, 1.5, 0.0).subtract(thing.position()).normalize());
                    if (this.dodgeCooldown < 1) {
                        if ((double) dot > 0.94) {
                            Vec3 dodgeVec = thing.getDeltaMovement().cross(new Vec3(0.0, 1.0, 0.0)).normalize().scale(1.2);
                            Vec3 newPosLeft = this.getPosition(1.0F).add(dodgeVec.scale(2.0));
                            Vec3 newPosRight = this.getPosition(1.0F).add(dodgeVec.scale(-2.0));
                            Vec3 diffLeft = newPosLeft.subtract(thing.position());
                            Vec3 diffRight = newPosRight.subtract(thing.position());
                            if (diffRight.dot(thing.getDeltaMovement()) > diffLeft.dot(thing.getDeltaMovement())) {
                                dodgeVec = dodgeVec.scale(-1.0);
                            }

                            this.setDeltaMovement(this.getDeltaMovement().add(dodgeVec.scale(0.5)));
                        }

                        this.dodgeCooldown = 10;
                    }
                }
            }

            if (this.dodgeCooldown > 0) {
                --this.dodgeCooldown;
            }
        }

        super.tick();
        if (this.isActive() || this.isRitual()) {
            this.setYRot(this.getYHeadRot());
            this.yBodyRot = this.getYRot();
        }

        if (this.isSpinning()) {
            ++this.spinDirection;
            if (this.spinDirection > 4) {
                this.spinDirection = 1;
            }

            this.yBodyRot = (float) (this.spinDirection * 90);
        }

        if (this.isChargingLaser() && this.level().isClientSide) {
            float f = this.yBodyRot * 0.017453292F + Mth.cos((float) this.tickCount * 0.6662F) * 0.25F;
            radius2 = Mth.cos(f);
            float f2 = Mth.sin(f);
            this.level().addParticle(ParticleTypes.ENTITY_EFFECT, this.getX() - (double) radius2 * 0.8, this.getY() + 2.5, this.getZ() - (double) f2 * 0.8, 0.1, 0.1, 0.2);
        }

        if (this.isActive()) {
            this.setNoGravity(true);
            this.nextWingsFrame();
            if (this.getWingsFrames() == 12 && this.isAlive() && !isPhasedOut()) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_WINGS.get(), 2.0F, 1.0F);
            }

            if (this.getWingsFrames() >= 25) {
                this.resetWingsFrame();
            }

            if (this.level().isClientSide) {
                this.clientSideWingsAnimationO = this.clientSideWingsAnimation;
                this.clientSideWingsAnimation = Mth.clamp(this.clientSideWingsAnimation + 1.0F, 0.0F, 25.0F);
            }

            if (!this.isCharging() && this.getTarget() != null) {
                LivingEntity entity = this.getTarget();
                double x = this.getX() - entity.getX();
                double y = this.getY() - entity.getY();
                double z = this.getZ() - entity.getZ();
                double d = Math.sqrt(x * x + y * y + z * z);
                power = 0.08F;
                double motionX = this.getDeltaMovement().x - x / d * (double) power * 0.2;
                double motionY = this.getDeltaMovement().y - y / d * (double) power * 0.2;
                double motionZ = this.getDeltaMovement().z - z / d * (double) power * 0.2;
                if (this.distanceToSqr(entity) > 120.0) {
                    this.setDeltaMovement(motionX, motionY, motionZ);
                }
            }

            if (!this.isCharging()) {
                if (this.getTarget() != null) {
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
            }
        }

        attackingMobs = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getTarget() == this);
        if (!this.stolen_mobs.isEmpty() && !this.isArmsUpward()) {
            toBeAttacked = this.stolen_mobs.get(this.random.nextInt(this.stolen_mobs.size()));

            for (Object attackingMob : attackingMobs) {
                Mob attacker = (Mob) attackingMob;
                if (this.random.nextInt(2) == 0 && !this.spirits.isEmpty()) {
                    attacker.setTarget(this.spirits.get(this.random.nextInt(this.spirits.size())));
                } else if (this.canStolenMobBeAttacked(toBeAttacked, attacker)) {
                    attacker.setTarget(toBeAttacked);
                } else if (!this.spirits.isEmpty()) {
                    attacker.setTarget(this.spirits.get(this.random.nextInt(this.spirits.size())));
                } else {
                    attacker.setTarget(null);
                }
            }
        }
    }

    public void push(Entity p_21294_) {
        if (!isPhasedOut()) super.push(p_21294_);
    }

    protected void pushEntities() {
        if (!isPhasedOut()) super.pushEntities();
    }

    public boolean startRiding(Entity p_20330_) {
        return (p_20330_ instanceof CrocofangEntity || p_20330_ instanceof Ravager) && super.startRiding(p_20330_);
    }

    protected void createLineImps() {
        if (this.getTarget() != null) {
            LivingEntity livingentity = this.getTarget();
            double d0 = Math.min(livingentity.getY(), this.getY() - 5.0);
            double d1 = Math.max(livingentity.getY(), this.getY() - 5.0) + 1.0;
            float f = (float) Mth.atan2(livingentity.getZ() - this.getZ(), livingentity.getX() - this.getX());

            for (int l = 0; l < 16; ++l) {
                double d2 = 1.25 * (double) (l + 1);
                this.createSpellEntity(this.getX() + (double) Mth.cos(f) * d2, this.getZ() + (double) Mth.sin(f) * d2, d0, d1, l);
            }
        }

    }

    protected void createRandomImps() {
        if (this.getTarget() != null) {
            LivingEntity livingentity = this.getTarget();
            double d0 = Math.min(livingentity.getY(), this.getY() - 5.0);
            double d1 = Math.max(livingentity.getY(), this.getY() - 5.0) + 1.0;

            for (int l = 0; l < 30; ++l) {
                this.createSpellEntity(this.getX() + (double) (-15 + this.random.nextInt(30)), this.getZ() + (double) (-15 + this.random.nextInt(30)), d0, d1, l);
            }
        }

    }

    protected void createRingImps() {
        if (this.getTarget() != null) {
            LivingEntity livingentity = this.getTarget();
            double d0 = Math.min(livingentity.getY(), this.getY() - 5.0);
            double d1 = Math.max(livingentity.getY(), this.getY() - 5.0) + 1.0;
            this.createSpellEntity(livingentity.getX() - 3.0, livingentity.getZ() - 0.0, d0, d1, 0);
            this.createSpellEntity(livingentity.getX() - 2.0, livingentity.getZ() + 1.0, d0, d1, 1);
            this.createSpellEntity(livingentity.getX() - 1.0, livingentity.getZ() + 2.0, d0, d1, 2);
            this.createSpellEntity(livingentity.getX() - 0.0, livingentity.getZ() + 3.0, d0, d1, 3);
            this.createSpellEntity(livingentity.getX() + 1.0, livingentity.getZ() + 2.0, d0, d1, 4);
            this.createSpellEntity(livingentity.getX() + 2.0, livingentity.getZ() + 1.0, d0, d1, 5);
            this.createSpellEntity(livingentity.getX() + 3.0, livingentity.getZ() - 0.0, d0, d1, 6);
            this.createSpellEntity(livingentity.getX() + 2.0, livingentity.getZ() - 1.0, d0, d1, 7);
            this.createSpellEntity(livingentity.getX() + 1.0, livingentity.getZ() - 2.0, d0, d1, 8);
            this.createSpellEntity(livingentity.getX() - 0.0, livingentity.getZ() - 3.0, d0, d1, 9);
            this.createSpellEntity(livingentity.getX() - 1.0, livingentity.getZ() - 2.0, d0, d1, 10);
            this.createSpellEntity(livingentity.getX() - 2.0, livingentity.getZ() - 1.0, d0, d1, 11);
            this.createSpellEntity(livingentity.getX() - 0.0, livingentity.getZ() - 0.0, d0, d1, 12);
        }

    }

    private void createSpellEntity(double p_190876_1_, double p_190876_3_, double p_190876_5_, double p_190876_7_, int time) {
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
            ImpEntity imp = ModEntityTypes.Imp.get().create(this.level());

            assert imp != null;

            imp.setPos((double) blockpos.getX() + 0.5, (double) blockpos.getY() + d0, (double) blockpos.getZ() + 0.5);
            imp.setOwner(this);
            imp.setPower(this.getSoulPower());
            imp.setTarget(this.getTarget());
            imp.setWaitTime(time);
            imp.setInvisible(true);
            if (this.getTeam() != null) {
                this.level().getScoreboard().addPlayerToTeam(imp.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
            }

            this.level().addFreshEntity(imp);
        }

    }

    public boolean ignoreExplosion() {
        return this.isCharging() || this.spiritSwarmCooldown > 140;
    }

    public boolean canStolenMobBeAttacked(LivingEntity entity, LivingEntity attacker) {
        if (Config.CommonConfig.spiritcaller_wontAttack.get().contains(entity.getEncodeId())) {
            return false;
        } else if (entity.getTeam() != null) {
            return entity.getTeam().isAllowFriendlyFire();
        } else if (entity instanceof MobSpiritEntity) {
            return ((MobSpiritEntity) entity).getOwner() != attacker;
        } else {
            return attacker != entity;
        }
    }

    public void die(DamageSource p_37847_) {
        if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
            this.getCurrentRaid().ticksActive = 0L;
        }

        if (this.isActive()) {
            if (!this.level().isClientSide) {
                setPhasedOut(false);
                this.attackTicks = 0;
                this.goalSelector.getRunningGoals().forEach(WrappedGoal::stop);
            }

            if (this.lastHurtByPlayerTime > 0) {
                this.lastHurtByPlayerTime = 10000;
            }

            this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_DEATHANIMATION.get(), 3.0F, 1.0F);
        } else {
            super.die(p_37847_);
        }

    }

    protected void tickDeath() {
        if (this.isActive()) {
            this.setCharging(false);
            this.setFaking(false);
            this.setSpinning(false);
            this.setArmsUpward(false);
            this.setClap(false);
            ++this.deathTime;
            this.setDeltaMovement(0.0, 0.05, 0.0);
            List<MobSpiritEntity> list1 = this.level().getEntitiesOfClass(MobSpiritEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == this);
            List<IllagerSoulEntity> list2 = this.level().getEntitiesOfClass(IllagerSoulEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == this);
            List<ImpEntity> list3 = this.level().getEntitiesOfClass(ImpEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == this);
            List<SpiritHandEntity> list4 = this.level().getEntitiesOfClass(SpiritHandEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == this);
            Iterator var5 = list1.iterator();

            while (var5.hasNext()) {
                MobSpiritEntity spirit = (MobSpiritEntity) var5.next();
                spirit.kill();
            }

            var5 = list2.iterator();

            while (var5.hasNext()) {
                IllagerSoulEntity soul = (IllagerSoulEntity) var5.next();
                soul.kill();
            }

            var5 = list3.iterator();

            while (var5.hasNext()) {
                ImpEntity imp = (ImpEntity) var5.next();
                imp.discard();
            }

            var5 = list4.iterator();

            while (var5.hasNext()) {
                SpiritHandEntity hand = (SpiritHandEntity) var5.next();
                hand.kill();
            }

            if (this.deathTime == 131) {
                LightningBolt lightning = EntityType.LIGHTNING_BOLT.create(this.level());

                assert lightning != null;

                lightning.setPos(this.getX(), this.getY(), this.getZ());
                lightning.setVisualOnly(true);
                this.playSound(SoundEvents.LIGHTNING_BOLT_IMPACT, 3.0F, 1.0F);
                this.playSound(SoundEvents.LIGHTNING_BOLT_THUNDER, 10000.0F, 1.0F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_KABOOMER_EXPLODE.get(), 6.0F, 1.0F);
                this.level().addFreshEntity(lightning);
                CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.6F, 0, 20);

                if (!this.level().isClientSide) {
                    this.makeExplodeParticles();
                    double range = 4.0;
                    this.level().explode(this, this.getX(), this.getY(), this.getZ(), 5.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX() + range, this.getY(), this.getZ() + range, 5.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX() + range, this.getY(), this.getZ() - range, 5.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX() - range, this.getY(), this.getZ() + range, 5.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX() - range, this.getY(), this.getZ() - range, 5.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX(), this.getY() + range, this.getZ(), 5.0F, Level.ExplosionInteraction.NONE);
                    this.level().explode(this, this.getX(), this.getY() - range, this.getZ(), 5.0F, Level.ExplosionInteraction.NONE);

                }

                this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_DEATH.get(), 3.0F, 1.0F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_DESCENT.get(), 3.0F, 1.0F);
                super.die(lastDamageSource != null ? lastDamageSource : this.damageSources().generic());
                if (!this.level().isClientSide) {
                    this.remove(RemovalReason.KILLED);
                }
            }
        } else {
            super.tickDeath();
        }

    }

    protected void dropAllDeathLoot(DamageSource source) {
        if (this.shouldDropLoot() && this.level().getGameRules().getBoolean(GameRules.RULE_DOMOBLOOT) && this.lastHurtByPlayerTime > 0 && (source.getDirectEntity() instanceof IllagerSoulEntity || source.getDirectEntity() instanceof SoulBeamEntity || source.getDirectEntity() instanceof ImpEntity)) {
            this.level().addFreshEntity(new ItemEntity(this.level(), this.getX(), this.getY(), this.getZ(), new ItemStack(ItemRegisterer.SPIRITCALLER_DISC.get())));
        }
        super.dropAllDeathLoot(source);
    }

    public boolean isForcefieldProtected() {
        return this.entityData.get(FORCEFIELD);
    }

    public void setForcefield(boolean forcefield) {
        this.entityData.set(FORCEFIELD, forcefield);
    }

    public boolean shouldRemoveItself() {
        return this.entityData.get(SHOULD_DELETE_ITSELF);
    }

    public void setShouldDeleteItself(boolean shouldDelete) {
        this.entityData.set(SHOULD_DELETE_ITSELF, shouldDelete);
    }

    public boolean areIllagersNearby() {
        return this.entityData.get(NEARBY_ILLAGERS) && this.ritualTicks < 1 && !this.isActive();
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

    public void nextWingsFrame() {
        this.entityData.set(WINGS_FRAME, this.getWingsFrames() + 1);
    }

    public int getWingsFrames() {
        return this.entityData.get(WINGS_FRAME);
    }

    public boolean isRitual() {
        return this.entityData.get(RITUAL);
    }

    public void setRitual(boolean ritual) {
        this.entityData.set(RITUAL, ritual);
    }

    public boolean isArmsUpward() {
        return this.entityData.get(ARMS_UPWARD);
    }

    public void setArmsUpward(boolean arms) {
        this.entityData.set(ARMS_UPWARD, arms);
    }

    public void setSoulPower(int souls) {
        this.entityData.set(SOUL_POWER, souls);
    }

    public int getSoulPower() {
        return this.entityData.get(SOUL_POWER);
    }

    public void resetWingsFrame() {
        this.entityData.set(WINGS_FRAME, 0);
        if (this.level().isClientSide) {
            this.clientSideWingsAnimation = 0.0F;
        }

    }

    public boolean isSpinning() {
        return this.entityData.get(SPINNING);
    }

    public void setSpinning(boolean spinning) {
        this.entityData.set(SPINNING, spinning);
    }

    public boolean isPhasedOut() {
        return this.entityData.get(PHASED_OUT);
    }

    public void setPhasedOut(boolean phasedOut) {
        this.entityData.set(PHASED_OUT, phasedOut);
    }

    public boolean isFaking() {
        return this.entityData.get(FAKING);
    }

    public void setFaking(boolean faking) {
        this.entityData.set(FAKING, faking);
    }

    public boolean isCharging() {
        return this.entityData.get(CHARGING);
    }

    public void setCharging(boolean charge) {
        this.entityData.set(CHARGING, charge);
    }

    public boolean isClap() {
        return this.entityData.get(CLAP);
    }

    public void setClap(boolean spinning) {
        this.entityData.set(CLAP, spinning);
    }

    public float getWingsAnimationScale(float p_29570_) {
        return Mth.lerp(p_29570_, this.clientSideWingsAnimationO, this.clientSideWingsAnimation) / 3.0F;
    }

    public boolean canBeLeader() {
        return false;
    }

    public boolean shouldShowSpiritHands() {
        return this.entityData.get(SHOW_SPIRIT_HANDS);
    }

    public void setShowSpiritHands(boolean hands) {
        this.entityData.set(SHOW_SPIRIT_HANDS, hands);
    }

    public boolean isChargingLaser() {
        return this.entityData.get(CHARGING_LASER);
    }

    public void setChargingLaser(boolean chargingLaser) {
        this.entityData.set(CHARGING_LASER, chargingLaser);
    }

    public boolean isShootingLaser() {
        return this.entityData.get(SHOOTING_LASER);
    }

    public void setShootingLaser(boolean laser) {
        this.entityData.set(SHOOTING_LASER, laser);
    }

    public void updateMobList() {
        int i;
        if (!this.stolen_mobs.isEmpty()) {
            for (i = 0; i < this.stolen_mobs.size(); ++i) {
                LivingEntity mob = this.stolen_mobs.get(i);
                if (!mob.isAlive()) {
                    this.stolen_mobs.remove(i);
                    --i;
                }
            }
        }

        if (!this.spirits.isEmpty()) {
            for (i = 0; i < this.spirits.size(); ++i) {
                MobSpiritEntity spirit = this.spirits.get(i);
                if (!spirit.isAlive()) {
                    if (spirit.getOriginalMob() != null) {
                        this.stolen_mobs.removeIf((original) -> original == spirit.getOriginalMob());
                    }

                    this.spirits.remove(i);
                    --i;
                }
            }
        }

    }

    public void makeParticles() {
        for (int i = 0; i < 250; ++i) {
            double d0 = (-0.5 + this.random.nextGaussian()) / 2.0;
            double d1 = (-0.5 + this.random.nextGaussian()) / 2.0;
            double d2 = (-0.5 + this.random.nextGaussian()) / 2.0;
            this.level().addParticle(ParticleTypes.HAPPY_VILLAGER, this.getRandomX(1.0), this.getRandomY() + 1.0, this.getRandomZ(1.0), d0, d1, d2);
        }

    }

    public boolean hurt(DamageSource source, float amount) {
        if (this.isPhasedOut() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            return false;
        }

        if (!this.isActive() && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            amount = 0.0F;
            if (source.getEntity() != null && this.ritualTicks == 0 && !this.areIllagersNearby()) {
                this.ritualTicks = 1;
                if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
                    this.getCurrentRaid().ticksActive = 0L;
                }
            }
        }

        if ((this.areIllagersNearby() || this.isForcefieldProtected()) && !source.is(DamageTypes.FELL_OUT_OF_WORLD) && !source.is(DamageTypes.GENERIC_KILL)) {
            return false;
        } else if (source.getEntity() instanceof IllagerSoulEntity && ((IllagerSoulEntity) source.getEntity()).getOwner() == this) {
            return false;
        } else {
            if (source.is(DamageTypeTags.IS_PROJECTILE)) {
                amount /= 2.0F;
            }

            this.lastDamageSource = source;
            return super.hurt(source, amount);
        }
    }

    public int getRitualTicks() {
        return this.ritualTicks;
    }

    public boolean isPersistenceRequired() {
        return !Config.CommonConfig.ULTIMATE_NIGHTMARE.get();
    }

    @Nullable
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor p_213386_1_, DifficultyInstance p_213386_2_, MobSpawnType p_213386_3_, @Nullable SpawnGroupData p_213386_4_, @Nullable CompoundTag p_213386_5_) {
        if (p_213386_3_ == MobSpawnType.EVENT) {
            this.setShouldDeleteItself(true);
        }

        return super.finalizeSpawn(p_213386_1_, p_213386_2_, p_213386_3_, p_213386_4_, p_213386_5_);
    }

    public SoundEvent getCelebrateSound() {
        return isRitual() || isPhasedOut() ? null : IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_CELEBRATE.get();
    }

    protected SoundEvent getAmbientSound() {
        return this.isRitual() || this.isPhasedOut() ? null : IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return this.isActive() ? null : IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_DEATH.get();
    }

    public boolean doesAttackMeetNormalRequirements() {
        return this.attackType == 0 && !this.areIllagersNearby() && this.getTarget() != null && this.hasLineOfSight(this.getTarget()) && this.isActive() && !this.isFaking();
    }

    public boolean isTargetOnGround() {
        return this.getTarget() != null && this.getTarget().onGround();
    }

    public boolean areStealableMobsNearby() {
        List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(15.0), (predicate) -> Config.CommonConfig.spiritcaller_stealableMobs.get().contains(predicate.getEncodeId()) && !predicate.isInvulnerable() && predicate != this);
        return !list.isEmpty();
    }

    public boolean checkForStolenMobs() {
        return this.stolen_mobs.isEmpty() || !this.areStolenMobsNearby();
    }

    public boolean areStolenMobsNearby() {
        List<LivingEntity> list = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(100.0), (predicate) -> Config.CommonConfig.spiritcaller_stealableMobs.get().contains(predicate.getEncodeId()) && !predicate.isInvulnerable() && predicate.hasEffect(EffectRegisterer.DISABILITY.get()));
        return !list.isEmpty();
    }

    public void setCharge(double x, double y, double z) {
        this.chargeX = x;
        this.chargeY = y;
        this.chargeZ = z;
    }

    public void setTargetPosition(double x, double y, double z) {
        this.targetX = x;
        this.targetY = y;
        this.targetZ = z;
    }

    public void setLaserPosition(double x, double y, double z) {
        this.laserX = x;
        this.laserY = y;
        this.laserZ = z;
    }

    static {
        SHOULD_DELETE_ITSELF = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        NEARBY_ILLAGERS = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        ACTIVE = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        WINGS_FRAME = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.INT);
        RITUAL = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        ARMS_UPWARD = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        SPINNING = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        PHASED_OUT = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        SOUL_POWER = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.INT);
        FAKING = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        CHARGING = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        FORCEFIELD = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        CLAP = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        SHOW_SPIRIT_HANDS = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        CHARGING_LASER = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
        SHOOTING_LASER = SynchedEntityData.defineId(SpiritcallerEntity.class, EntityDataSerializers.BOOLEAN);
    }

    class AntiCheeseGoal extends Goal {
        public boolean canUse() {
            return SpiritcallerEntity.this.stuckTime > 5 && SpiritcallerEntity.this.attackType == 0 && !SpiritcallerEntity.this.areIllagersNearby() && SpiritcallerEntity.this.getTarget() != null && SpiritcallerEntity.this.isActive() && !SpiritcallerEntity.this.isFaking() && SpiritcallerEntity.this.antiCheeseCooldown < 1 && SpiritcallerEntity.this.attackCooldown < 1;
        }

        public boolean canContinueToUse() {
            if (SpiritcallerEntity.this.attackTicks == 40 && SpiritcallerEntity.this.getTarget() == null) return false;

            return attackTicks <= 140;
        }

        public void start() {
            SpiritcallerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_IMPRISE.get(), 4.0f, 1.0f);
            SpiritcallerEntity.this.setArmsUpward(true);
            SpiritcallerEntity.this.setFaking(true);
            SpiritcallerEntity.this.attackType = SpiritcallerEntity.this.ANTICHEESE;
        }

        public void stop() {
            SpiritcallerEntity.this.attackType = 0;
            SpiritcallerEntity.this.attackCooldown = 20;
            SpiritcallerEntity.this.antiCheeseCooldown = 40;
            SpiritcallerEntity.this.stuckTime = 0;
            SpiritcallerEntity.this.setFaking(false);
            SpiritcallerEntity.this.setArmsUpward(false);
            SpiritcallerEntity.this.setClap(false);
        }
    }

    class StealSoulsGoal extends Goal {
        StealSoulsGoal() {
        }

        public boolean canUse() {
            return SpiritcallerEntity.this.doesAttackMeetNormalRequirements() && (!SpiritcallerEntity.this.stolen_mobs.isEmpty() || SpiritcallerEntity.this.areStealableMobsNearby()) && SpiritcallerEntity.this.stealSoulsCooldown < 1 && SpiritcallerEntity.this.attackCooldown < 1;
        }

        public boolean canContinueToUse() {
            return SpiritcallerEntity.this.attackTicks <= 55;
        }

        public void start() {
            EntityUtil.mobFollowingSound(level(), SpiritcallerEntity.this, IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_STEALSPIRITS.get(), 2.0F, 1.0F, false);
            SpiritcallerEntity.this.setArmsUpward(true);
            SpiritcallerEntity.this.attackType = SpiritcallerEntity.this.SPIRIT_STEAL;
            List<Mob> stealingMobs = SpiritcallerEntity.this.level().getEntitiesOfClass(Mob.class, SpiritcallerEntity.this.getBoundingBox().inflate(15.0), (predicate) -> Config.CommonConfig.spiritcaller_stealableMobs.get().contains(predicate.getEncodeId()) && !predicate.isInvulnerable() && predicate != SpiritcallerEntity.this);
            if (!stealingMobs.isEmpty()) {
                for (int i = 0; i < stealingMobs.size(); ++i) {
                    LivingEntity mob = stealingMobs.get(i);
                    if (!mob.isAlive()) {
                        stealingMobs.remove(i);
                        --i;
                    }

                    SpiritcallerEntity.this.stolen_mobs.add(mob);
                }
            }

            List<SpiritHandEntity> hands = SpiritcallerEntity.this.level().getEntitiesOfClass(SpiritHandEntity.class, SpiritcallerEntity.this.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == SpiritcallerEntity.this);

            for (SpiritHandEntity hand : hands) {
                hand.kill();
            }

        }

        public void stop() {
            SpiritcallerEntity.this.setArmsUpward(false);
            SpiritcallerEntity.this.attackType = 0;
            SpiritcallerEntity.this.attackCooldown = 20;
            SpiritcallerEntity.this.stealSoulsCooldown = 900;
            if (!SpiritcallerEntity.this.stolen_mobs.isEmpty()) {

                for (LivingEntity entity : SpiritcallerEntity.this.stolen_mobs) {
                    if (!SpiritcallerEntity.this.level().isClientSide) {
                        MobSpiritEntity spirit = ModEntityTypes.MobSpirit.get().create(SpiritcallerEntity.this.level());

                        assert spirit != null;

                        spirit.setPos(entity.getX(), entity.getY() + 1.0, entity.getZ());
                        spirit.setOwner(SpiritcallerEntity.this);
                        spirit.setOriginalMob(entity);
                        spirit.setDeltaMovement(0.0, 0.5, 0.0);
                        spirit.setTarget(SpiritcallerEntity.this.getTarget());
                        if (SpiritcallerEntity.this.getTeam() != null) {
                            SpiritcallerEntity.this.level().getScoreboard().addPlayerToTeam(spirit.getStringUUID(), SpiritcallerEntity.this.level().getScoreboard().getPlayerTeam(SpiritcallerEntity.this.getTeam().getName()));
                        }

                        spirit.setGoodOrEvil(!(entity instanceof Enemy));
                        if (entity instanceof SpiritcallerEntity) {
                            spirit.setSpiritcaller(true);
                        }

                        SpiritcallerEntity.this.level().addFreshEntity(spirit);
                        entity.setDeltaMovement(0.0, 0.3, 0.0);
                        SpiritcallerEntity.this.spirits.add(spirit);
                    }
                }
            }

        }
    }

    class SoulSwarmGoal extends Goal {
        SoulSwarmGoal() {
        }

        public boolean canUse() {
            return SpiritcallerEntity.this.doesAttackMeetNormalRequirements() && SpiritcallerEntity.this.checkForStolenMobs() && SpiritcallerEntity.this.random.nextInt(12) == 0 && SpiritcallerEntity.this.stealSoulsCooldown >= 0 && SpiritcallerEntity.this.spiritSwarmCooldown < 1 && SpiritcallerEntity.this.getHealth() < SpiritcallerEntity.this.getMaxHealth() / 2.0F && SpiritcallerEntity.this.attackCooldown < 1;
        }

        public boolean canContinueToUse() {
            return SpiritcallerEntity.this.attackTicks <= 70;
        }

        public void start() {
            EntityUtil.mobFollowingSound(level(), SpiritcallerEntity.this, IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_SPIRITSWARM.get(), 2.0F, 1.0F, false);
            SpiritcallerEntity.this.setArmsUpward(true);
            SpiritcallerEntity.this.attackType = SpiritcallerEntity.this.SOUL_SWARM;
        }

        public void stop() {
            SpiritcallerEntity.this.attackType = 0;
            SpiritcallerEntity.this.attackCooldown = 20;
            SpiritcallerEntity.this.spiritSwarmCooldown = 200;
            SpiritcallerEntity.this.setArmsUpward(false);
            if (SpiritcallerEntity.this.getTarget() != null) {
                SpiritcallerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_SOULSCREAM.get(), 3.0F, SpiritcallerEntity.this.getVoicePitch());
                LivingEntity entity = SpiritcallerEntity.this.getTarget();
                double x = SpiritcallerEntity.this.getX() - entity.getX();
                double y = SpiritcallerEntity.this.getY() - entity.getY();
                double z = SpiritcallerEntity.this.getZ() - entity.getZ();
                double d = Math.sqrt(x * x + y * y + z * z);
                float power = 3.5F;
                double motionX = SpiritcallerEntity.this.getDeltaMovement().x - x / d * (double) power * 0.2;
                double motionY = SpiritcallerEntity.this.getDeltaMovement().y - y / d * (double) power * 0.2;
                double motionZ = SpiritcallerEntity.this.getDeltaMovement().z - z / d * (double) power * 0.2;
                SpiritcallerEntity.this.setTargetPosition(entity.getX(), entity.getY(), entity.getZ());
                SpiritcallerEntity.this.setCharge(motionX, motionY, motionZ);
            } else if (!level().isClientSide) {
                SpiritcallerEntity.this.setFaking(false);
            }

            if (SpiritcallerEntity.this.getSoulPower() > 0) {
                SpiritcallerEntity.this.setSoulPower(SpiritcallerEntity.this.getSoulPower() - 1);
            }

        }
    }

    class ImpRiseGoal extends Goal {
        ImpRiseGoal() {
        }

        public boolean canUse() {
            return SpiritcallerEntity.this.doesAttackMeetNormalRequirements() && SpiritcallerEntity.this.checkForStolenMobs() && SpiritcallerEntity.this.random.nextInt(8) == 0 && SpiritcallerEntity.this.stealSoulsCooldown >= 0 && SpiritcallerEntity.this.impRiseCooldown < 1 && SpiritcallerEntity.this.isTargetOnGround() && SpiritcallerEntity.this.attackCooldown < 1;
        }

        public boolean canContinueToUse() {
            return SpiritcallerEntity.this.attackTicks <= 150;
        }

        public void start() {
            SpiritcallerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_IMPRISE.get(), 2.0F, 1.0F);
            SpiritcallerEntity.this.setArmsUpward(true);
            SpiritcallerEntity.this.attackType = SpiritcallerEntity.this.IMP_RISE;
        }

        public void stop() {
            SpiritcallerEntity.this.attackType = 0;
            SpiritcallerEntity.this.attackCooldown = 20;
            SpiritcallerEntity.this.impRiseCooldown = 100;
            SpiritcallerEntity.this.setArmsUpward(false);
            SpiritcallerEntity.this.setClap(false);
            if (SpiritcallerEntity.this.getSoulPower() > 0) {
                SpiritcallerEntity.this.setSoulPower(SpiritcallerEntity.this.getSoulPower() - 1);
            }

        }
    }

    class SpiritHandsGoal extends Goal {
        SpiritHandsGoal() {
        }

        public boolean canUse() {
            return SpiritcallerEntity.this.doesAttackMeetNormalRequirements() && SpiritcallerEntity.this.checkForStolenMobs() && SpiritcallerEntity.this.random.nextInt(8) == 0 && SpiritcallerEntity.this.stealSoulsCooldown >= 0 && SpiritcallerEntity.this.spiritHandsCooldown < 1 && SpiritcallerEntity.this.attackCooldown < 1;
        }

        public boolean canContinueToUse() {
            return SpiritcallerEntity.this.attackTicks <= 50;
        }

        public void start() {
            EntityUtil.mobFollowingSound(level(), SpiritcallerEntity.this, IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_SPIRITHANDS.get(), 2.0F, 1.0F, false);
            SpiritcallerEntity.this.setSpinning(true);
            SpiritcallerEntity.this.attackType = SpiritcallerEntity.this.SPIRIT_HANDS;
        }

        public void stop() {
            SpiritcallerEntity.this.attackType = 0;
            SpiritcallerEntity.this.attackCooldown = 20;
            SpiritcallerEntity.this.spiritHandsCooldown = 900;
            SpiritcallerEntity.this.setClap(false);
            if (SpiritcallerEntity.this.getSoulPower() > 0) {
                SpiritcallerEntity.this.setSoulPower(SpiritcallerEntity.this.getSoulPower() - 1);
            }

        }
    }

    class SoulLaserGoal extends Goal {
        public SoulLaserGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK));
        }

        public boolean canUse() {
            return SpiritcallerEntity.this.doesAttackMeetNormalRequirements() && SpiritcallerEntity.this.checkForStolenMobs() && SpiritcallerEntity.this.random.nextInt(8) == 0 && SpiritcallerEntity.this.stealSoulsCooldown >= 0 && SpiritcallerEntity.this.soulLaserCooldown < 1 && SpiritcallerEntity.this.attackCooldown < 1;
        }

        public boolean canContinueToUse() {
            return SpiritcallerEntity.this.attackTicks <= 140;
        }

        public void start() {
            EntityUtil.mobFollowingSound(level(), SpiritcallerEntity.this, IllageAndSpillageSoundEvents.ENTITY_SPIRITCALLER_CHARGELASER.get(), 2.0F, 1.0F, false);
            SpiritcallerEntity.this.setChargingLaser(true);
            SpiritcallerEntity.this.attackType = SpiritcallerEntity.this.SOUL_LASER;
        }

        public void stop() {
            SpiritcallerEntity.this.attackType = 0;
            SpiritcallerEntity.this.attackCooldown = 20;
            SpiritcallerEntity.this.soulLaserCooldown = 100;
            SpiritcallerEntity.this.setLaserPosition(0.0, 0.0, 0.0);
            SpiritcallerEntity.this.setShootingLaser(false);
            if (SpiritcallerEntity.this.getSoulPower() > 0) {
                SpiritcallerEntity.this.setSoulPower(SpiritcallerEntity.this.getSoulPower() - 1);
            }

        }
    }

    class AlwaysWatchTargetGoal extends Goal {
        public AlwaysWatchTargetGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public boolean canUse() {
            return SpiritcallerEntity.this.getTarget() != null;
        }

        public boolean canContinueToUse() {
            return SpiritcallerEntity.this.getTarget() != null;
        }

        public void tick() {
            SpiritcallerEntity.this.getNavigation().stop();
            if (SpiritcallerEntity.this.getTarget() != null) {
                SpiritcallerEntity.this.getLookControl().setLookAt(SpiritcallerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            SpiritcallerEntity.this.navigation.stop();
        }
    }
}

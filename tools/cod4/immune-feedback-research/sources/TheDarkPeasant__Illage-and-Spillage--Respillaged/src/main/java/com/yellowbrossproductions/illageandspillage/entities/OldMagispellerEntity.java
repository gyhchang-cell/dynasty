package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
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
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.Vex;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.*;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.event.ForgeEventFactory;
import net.minecraftforge.event.entity.EntityTeleportEvent;

import javax.annotation.Nullable;
import java.util.*;

public class OldMagispellerEntity extends AbstractIllager {
    public ServerBossEvent bossEvent;
    private final List<FakeMagispellerEntity> clones = new ArrayList<>();
    private static final EntityDataAccessor<Boolean> FAKING;
    private static final EntityDataAccessor<Boolean> NEARBY_ILLAGERS;
    private static final EntityDataAccessor<Boolean> SHOULD_DELETE_ITSELF;
    private static final EntityDataAccessor<Boolean> WAVING_ARMS;
    private static final EntityDataAccessor<Boolean> SPINNING;
    private static final EntityDataAccessor<Boolean> VINDICATOR_ATTACKING;
    private static final EntityDataAccessor<Boolean> CROSSBOW_ATTACKING;
    private static final EntityDataAccessor<Boolean> FORCEFIELD;
    private static final EntityDataAccessor<Boolean> WEEEEEEEEEEEE;
    private static final EntityDataAccessor<Boolean> ACTIVE;
    private int attackTicks;
    private int attackType;
    private final int CLONES_ATTACK = 1;
    private final int CROSSBOWSPIN_ATTACK = 2;
    private final int HEAL_ATTACK = 3;
    private final int DISPENSER_ATTACK = 4;
    private final int FANGRUN_ATTACK = 5;
    private final int SUMMON_ATTACK = 6;
    private final int POTIONS_ATTACK = 7;
    private final int FIREBALL_ATTACK = 8;
    private final int LIFESTEAL_ATTACK = 9;
    private final int RAVAGER_ATTACK = 10;
    private int spinDirection;
    private int dispenserCooldown;
    private int vexCooldown;
    private int pullPower;
    private int waitTimeFaker;

    public OldMagispellerEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
        this.xpReward = 100;
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

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new RavagerGoal());
        this.goalSelector.addGoal(0, new LifeStealGoal());
        this.goalSelector.addGoal(0, new ShootFireballGoal());
        this.goalSelector.addGoal(0, new ThrowPotionsGoal());
        this.goalSelector.addGoal(0, new SummonVexesGoal());
        this.goalSelector.addGoal(0, new FangRunGoal());
        this.goalSelector.addGoal(0, new DispenserGoal());
        this.goalSelector.addGoal(0, new HealGoal());
        this.goalSelector.addGoal(0, new CrossbowSpinGoal());
        this.goalSelector.addGoal(0, new ClonesGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new StareAtTargetGoal());
        this.goalSelector.addGoal(2, new Raider.HoldGroundAttackGoal(this, 10.0F));
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
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 250.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 32.0);
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
        this.entityData.define(FAKING, false);
        this.entityData.define(NEARBY_ILLAGERS, false);
        this.entityData.define(SHOULD_DELETE_ITSELF, false);
        this.entityData.define(WAVING_ARMS, false);
        this.entityData.define(SPINNING, false);
        this.entityData.define(VINDICATOR_ATTACKING, false);
        this.entityData.define(CROSSBOW_ATTACKING, false);
        this.entityData.define(FORCEFIELD, false);
        this.entityData.define(WEEEEEEEEEEEE, false);
        this.entityData.define(ACTIVE, false);
    }

    public boolean canAttack(LivingEntity p_213336_1_) {
        return !this.areIllagersNearby() && super.canAttack(p_213336_1_);
    }

    public void addAdditionalSaveData(CompoundTag p_213281_1_) {
        super.addAdditionalSaveData(p_213281_1_);
        if (this.isFaking()) {
            p_213281_1_.putBoolean("IsFaking", true);
        }

        if (this.isActive()) {
            p_213281_1_.putBoolean("active", true);
        }

    }

    public void readAdditionalSaveData(CompoundTag p_70037_1_) {
        super.readAdditionalSaveData(p_70037_1_);
        this.bossEvent.setName(this.getDisplayName());
        this.setFaking(p_70037_1_.getBoolean("IsFaking"));
        this.setActive(p_70037_1_.getBoolean("active"));
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    protected float getStandingEyeHeight(Pose p_213348_1_, EntityDimensions p_213348_2_) {
        return 1.66F;
    }

    public void tick() {
        List<Raider> list = this.level().getEntitiesOfClass(Raider.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate.hasActiveRaid() && !predicate.getType().is(ModTags.EntityTypes.ILLAGER_BOSSES));
        if (Config.CommonConfig.magispeller_forcefield.get() && this.hasActiveRaid()) {
            if (!this.level().isClientSide) {
                this.setIllagersNearby(!list.isEmpty());
            }

            if (!list.isEmpty()) {
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

        if (this.attackType > 0) {
            ++this.attackTicks;
        } else {
            this.attackTicks = 0;
        }

        --this.dispenserCooldown;
        if (this.dispenserCooldown < 0) {
            this.dispenserCooldown = 0;
        }

        --this.vexCooldown;
        if (this.vexCooldown < 0) {
            this.vexCooldown = 0;
        }

        if (this.attackType == this.LIFESTEAL_ATTACK && this.attackTicks > 36) {
            ++this.pullPower;
        } else {
            this.pullPower = 0;
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
            this.setVindicatorAttacking(false);
        }

        this.updateCloneList();
        if (this.isSpinning()) {
            ++this.spinDirection;
            if (this.spinDirection > 4) {
                this.spinDirection = 1;
            }

            this.yBodyRot = (float) (this.spinDirection * 90);
        }

        if (this.isWavingArms() && this.level().isClientSide) {
            float f = this.yBodyRot * 0.017453292F + Mth.cos((float) this.tickCount * 0.6662F) * 0.25F;
            float f1 = Mth.cos(f);
            float f2 = Mth.sin(f);
            this.level().addParticle(ParticleTypes.ENTITY_EFFECT, this.getX() + (double) f1 * 0.6, this.getY() + 1.8, this.getZ() + (double) f2 * 0.6, 0.1, 0.1, 0.2);
            this.level().addParticle(ParticleTypes.ENTITY_EFFECT, this.getX() - (double) f1 * 0.6, this.getY() + 1.8, this.getZ() - (double) f2 * 0.6, 0.1, 0.1, 0.2);
        }

        if (EntityUtil.displayBossBar(this) && this.isActive() && !bossEvent.isVisible()) {
            bossEvent.setVisible(true);
        } else if (bossEvent.isVisible()) {
            bossEvent.setVisible(false);
        }

        if (this.isFaking()) {
            ++this.waitTimeFaker;
        } else {
            this.waitTimeFaker = 0;
        }

        double y;
        double z;
        double d;
        Entity entity;
        double x;
        if (this.isForcefieldProtected()) {
            var2 = this.level().getEntities(this, this.getBoundingBox().inflate(15.0)).iterator();

            while (var2.hasNext()) {
                entity = (Entity) var2.next();
                if (EntityUtil.canHurtThisMob(entity, this) && entity.isAlive()) {
                    x = this.getX() - entity.getX();
                    y = this.getY() - entity.getY();
                    z = this.getZ() - entity.getZ();
                    d = Math.sqrt(x * x + y * y + z * z);
                    if (this.distanceToSqr(entity) < 9.0) {
                        entity.hurtMarked = true;
                        entity.setDeltaMovement(-x / d * 2.0, -y / d * 2.0, -z / d * 2.0);
                        entity.lerpMotion(-x / d * 2.0, -y / d * 2.0, -z / d * 2.0);
                    }
                }
            }
        }

        if (this.isGoingWEEEEEEEEEEE() && !this.isPassenger()) {
            this.setWEEEEEEEEEEEEE(false);
        }

        if (this.isAlive()) {
            if (this.attackType == this.CLONES_ATTACK) {
                this.getNavigation().stop();
                if (this.attackTicks == 18) {
                    this.setWavingArms(false);
                    this.setSpinning(true);
                }

                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                this.navigation.stop();
            }

            if (this.attackType == this.CROSSBOWSPIN_ATTACK) {
                this.getNavigation().stop();
                if (this.attackTicks == 8) {
                    this.playSound(SoundEvents.CROSSBOW_QUICK_CHARGE_3, 1.0F, 1.0F);
                }

                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                if (this.attackTicks == 18) {
                    this.setSpinning(false);
                    this.setCrossbowAttacking(true);
                    if (this.getTarget() != null) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_ARROWBARRAGE.get(), 2.0F, 1.0F);
                    }
                }

                if (this.attackTicks >= 18 && this.getTarget() != null) {
                    this.fireArrow(this.getTarget(), 1.0F, 0.5F);
                }

                this.navigation.stop();
            }

            if (this.attackType == this.HEAL_ATTACK) {
                this.getNavigation().stop();
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                this.navigation.stop();
            }

            if (this.attackType == this.DISPENSER_ATTACK) {
                this.getNavigation().stop();
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                this.navigation.stop();
            }

            if (this.attackType == this.FANGRUN_ATTACK) {
                this.getNavigation().stop();
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                if (this.attackTicks >= 43) {
                    if (this.attackTicks == 43) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_FORCEFIELD.get(), 1.0F, 1.0F);
                        if (!this.level().isClientSide) {
                            this.setForcefield(true);
                        }

                        if (this.level().isClientSide) {
                            for (int i = 0; i < 25; ++i) {
                                this.level().addParticle(ParticleTypes.EXPLOSION_EMITTER, this.getX(), this.getY(), this.getZ(), 0.0, 0.0, 0.0);
                            }
                        }
                    }

                    this.createFangs();
                    this.playSound(SoundEvents.EVOKER_FANGS_ATTACK, 1.0F, this.getVoicePitch());
                }

                this.navigation.stop();
            }

            if (this.attackType == this.SUMMON_ATTACK) {
                this.getNavigation().stop();
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                this.navigation.stop();
            }

            if (this.attackType == this.POTIONS_ATTACK) {
                this.getNavigation().stop();
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                if (this.attackTicks == 18 || this.attackTicks == 36) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SPIN.get(), 1.0F, 1.0F);
                }

                if (this.attackTicks > 17 && !this.level().isClientSide) {
                    ThrownPotion potionentity = new ThrownPotion(this.level(), this);
                    potionentity.setItem(PotionUtils.setPotion(new ItemStack(Items.SPLASH_POTION), Potions.STRONG_SLOWNESS));
                    potionentity.setXRot(-20.0F);
                    potionentity.shoot(-2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble(), 2.0 + this.random.nextDouble() + this.random.nextDouble(), -2.0 + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble() + this.random.nextDouble(), 0.75F, 8.0F);
                    this.level().addFreshEntity(potionentity);
                }

                this.navigation.stop();
            }

            if (this.attackType == this.FIREBALL_ATTACK) {
                this.getNavigation().stop();
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                if (this.attackTicks == 44 && !this.level().isClientSide) {
                    LivingEntity livingentity = this.getTarget();
                    if (livingentity != null) {
                        Vec3 vector3d = this.getViewVector(1.0F);
                        y = livingentity.getX() - (this.getX() + vector3d.x * 4.0);
                        z = livingentity.getY(0.5) - (0.5 + this.getY(0.5));
                        d = livingentity.getZ() - (this.getZ() + vector3d.z * 4.0);
                        LargeFireball fireballentity = new LargeFireball(this.level(), this, y, z, d, 3);
                        fireballentity.setPos(this.getX() + vector3d.x, this.getY() + 1.5, this.getZ() + vector3d.z);
                        fireballentity.setOwner(this);
                        this.level().addFreshEntity(fireballentity);
                    }
                }

                this.navigation.stop();
            }

            if (this.attackType == this.LIFESTEAL_ATTACK) {
                this.getNavigation().stop();
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                if (this.attackTicks == 18) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SPIN.get(), 1.0F, 1.0F);
                }

                if (this.attackTicks == 36) {
                    this.setSpinning(false);
                    this.setWavingArms(true);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_LIFESTEAL.get(), 2.0F, 1.0F);
                }

                if (this.attackTicks >= 36) {
                    var2 = this.level().getEntities(this, this.getBoundingBox().inflate(15.0)).iterator();

                    label260:
                    while (true) {
                        do {
                            do {
                                do {
                                    if (!var2.hasNext()) {
                                        break label260;
                                    }

                                    entity = (Entity) var2.next();
                                } while (!EntityUtil.canHurtThisMob(entity, this));
                            } while (!entity.isAlive());
                        } while (!this.isMobNotInCreativeMode(entity));

                        x = this.getX() - entity.getX();
                        y = this.getY() - entity.getY();
                        z = this.getZ() - entity.getZ();
                        d = Math.sqrt(x * x + y * y + z * z);
                        float power = (float) this.pullPower / 103.0F;
                        double motionX = entity.getDeltaMovement().x + x / d * (double) power * 0.2;
                        double motionY = entity.getDeltaMovement().y + y / d * (double) power * 0.2;
                        double motionZ = entity.getDeltaMovement().z + z / d * (double) power * 0.2;
                        entity.hurtMarked = true;
                        entity.setDeltaMovement(motionX, motionY, motionZ);
                        entity.lerpMotion(motionX, motionY, motionZ);
                        if (this.level().isClientSide) {
                            for (int i = 0; i < 2; ++i) {
                                this.level().addParticle(ParticleTypes.CRIT, entity.getRandomX(0.5), entity.getRandomY(), entity.getRandomZ(0.5), 0.0, 0.0, 0.0);
                            }
                        }

                        if (this.distanceToSqr(entity) < 9.0 && entity instanceof LivingEntity) {
                            if (((LivingEntity) entity).hurtTime <= 0) {
                                double healthStolen = ((((LivingEntity) entity).getMaxHealth() - ((LivingEntity) entity).getHealth()) / 3.0F + 1.0F);
                                if (healthStolen > 10.0) {
                                    healthStolen = 10.0;
                                }

                                this.heal((float) healthStolen);
                                entity.hurt(this.damageSources().indirectMagic(this, this), (float) healthStolen);
                            }

                            entity.hurtMarked = true;
                            entity.setDeltaMovement(-x / d * 2.0, -y / d * 2.0, -z / d * 2.0);
                            entity.lerpMotion(-x / d * 2.0, -y / d * 2.0, -z / d * 2.0);
                        }
                    }
                }

                this.navigation.stop();
            }

            if (this.attackType == this.RAVAGER_ATTACK) {
                this.getNavigation().stop();
                this.setDeltaMovement(0.0, 0.06, 0.0);
                if (this.getTarget() != null) {
                    this.getLookControl().setLookAt(this.getTarget(), 30.0F, 30.0F);
                }

                this.navigation.stop();
            }
        }

        super.tick();
    }

    public boolean hurt(DamageSource damageSource, float p_70097_2_) {
        if ((this.areIllagersNearby() || this.isForcefieldProtected()) && !damageSource.is(DamageTypes.GENERIC_KILL) && !damageSource.is(DamageTypes.FELL_OUT_OF_WORLD)) {
            return false;
        } else {
            if (this.isFaking()) {
                this.setFaking(false);
                this.setVindicatorAttacking(false);
                if (!this.clones.isEmpty()) {

                    for (FakeMagispellerEntity clone : this.clones) {
                        clone.kill();
                    }
                }
            }

            if (!damageSource.is(DamageTypes.GENERIC_KILL) && !damageSource.is(DamageTypes.FELL_OUT_OF_WORLD) && p_70097_2_ > 20.0F) {
                p_70097_2_ = 20.0F;
            }

            if (damageSource.getDirectEntity() instanceof LargeFireball) {
                p_70097_2_ = 5.0F;
            }

            if (damageSource.getEntity() instanceof CrashagerEntity && ((CrashagerEntity) damageSource.getEntity()).getOwner() == this) {
                return false;
            } else {
                if (damageSource.getEntity() instanceof LivingEntity && !this.isActive() && !this.areIllagersNearby()) {
                    this.setActive(true);
                    if (this.hasActiveRaid() && this.getCurrentRaid() != null) {
                        this.getCurrentRaid().ticksActive = 0L;
                    }
                }

                return super.hurt(damageSource, p_70097_2_);
            }
        }
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

        super.die(p_37847_);
    }

    public boolean doHurtTarget(Entity p_70652_1_) {
        if (this.isFaking() && !this.level().isClientSide && this.random.nextInt(3) != 0) {
            this.teleportTowards(p_70652_1_);
        }

        return (!this.isFaking() || this.waitTimeFaker >= 20) && super.doHurtTarget(p_70652_1_);
    }

    protected void createFangs() {
        if (this.getTarget() != null) {
            LivingEntity livingentity = this.getTarget();
            double d0 = Math.min(livingentity.getY(), this.getY());
            double d1 = Math.max(livingentity.getY(), this.getY()) + 1.0;
            float f = (float) Mth.atan2(livingentity.getZ() - this.getZ(), livingentity.getX() - this.getX());

            for (int l = 0; l < 16; ++l) {
                double d2 = 1.25 * (double) (l + 1);
                this.createSpellEntity(this.getX() + (double) Mth.cos(f) * d2, this.getZ() + (double) Mth.sin(f) * d2, d0, d1, f, l);
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

    public Component getName() {
        return !this.hasCustomName() && this.isFaking() ? (ModEntityTypes.Faker.get()).getDescription() : super.getName();
    }

    public boolean isFaking() {
        return this.entityData.get(FAKING);
    }

    public void setFaking(boolean faking) {
        this.entityData.set(FAKING, faking);
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

    public boolean isWavingArms() {
        return this.entityData.get(WAVING_ARMS);
    }

    public void setWavingArms(boolean waving) {
        this.entityData.set(WAVING_ARMS, waving);
    }

    public boolean isSpinning() {
        return this.entityData.get(SPINNING);
    }

    public void setSpinning(boolean spinning) {
        this.entityData.set(SPINNING, spinning);
    }

    public boolean isVindicatorAttacking() {
        return this.entityData.get(VINDICATOR_ATTACKING);
    }

    public void setVindicatorAttacking(boolean attacking) {
        this.entityData.set(VINDICATOR_ATTACKING, attacking);
    }

    public boolean isCrossbowAttacking() {
        return this.entityData.get(CROSSBOW_ATTACKING);
    }

    public void setCrossbowAttacking(boolean attacking) {
        this.entityData.set(CROSSBOW_ATTACKING, attacking);
    }

    public boolean isForcefieldProtected() {
        return this.entityData.get(FORCEFIELD);
    }

    public void setForcefield(boolean forcefield) {
        this.entityData.set(FORCEFIELD, forcefield);
    }

    public boolean isGoingWEEEEEEEEEEE() {
        return this.entityData.get(WEEEEEEEEEEEE);
    }

    public void setWEEEEEEEEEEEEE(boolean weeeeeeee) {
        this.entityData.set(WEEEEEEEEEEEE, weeeeeeee);
    }

    public boolean isActive() {
        return this.entityData.get(ACTIVE);
    }

    public void setActive(boolean active) {
        this.entityData.set(ACTIVE, active);
    }

    public boolean isPersistenceRequired() {
        return true;
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
        return this.attackType == 0 && !this.isFaking() && !this.areIllagersNearby() && this.getTarget() != null && this.hasLineOfSight(this.getTarget()) && this.isActive();
    }

    public boolean isTargetLowEnoughForGround() {
        return this.getTarget() != null && !(this.getTarget().getY() > this.getY() + 3.0);
    }

    public boolean isTargetCloseEnoughForRange() {
        return this.getTarget() != null && this.distanceToSqr(this.getTarget()) < 26.0;
    }

    protected boolean teleport() {
        if (!this.level().isClientSide() && this.isAlive()) {
            double d0 = this.getX() + (this.random.nextDouble() - 0.5) * 64.0;
            double d1 = this.getY() + (double) (this.random.nextInt(64) - 32);
            double d2 = this.getZ() + (this.random.nextDouble() - 0.5) * 64.0;
            return this.teleport(d0, d1, d2);
        } else {
            return false;
        }
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
        double d1 = p_82196_1_.getY(0.3333333333333333) - abstractarrowentity.getY() - 0.1;
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

    public boolean isMobNotInCreativeMode(Entity entity) {
        if (!(entity instanceof Player)) {
            return true;
        } else {
            return !((Player) entity).isCreative() && !entity.isSpectator();
        }
    }

    static {
        FAKING = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        NEARBY_ILLAGERS = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        SHOULD_DELETE_ITSELF = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        WAVING_ARMS = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        SPINNING = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        VINDICATOR_ATTACKING = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        CROSSBOW_ATTACKING = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        FORCEFIELD = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        WEEEEEEEEEEEE = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
        ACTIVE = SynchedEntityData.defineId(OldMagispellerEntity.class, EntityDataSerializers.BOOLEAN);
    }

    class RavagerGoal extends Goal {
        public RavagerGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 75.0F < 0.9F && OldMagispellerEntity.this.isTargetLowEnoughForGround() && !OldMagispellerEntity.this.isPassenger();
        }

        public void start() {
            OldMagispellerEntity.this.setSpinning(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_RAVAGER.get(), 2.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.RAVAGER_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 68;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            if (OldMagispellerEntity.this.getTarget() != null && !OldMagispellerEntity.this.level().isClientSide) {
                CrashagerEntity ravager = ModEntityTypes.Crashager.get().create(OldMagispellerEntity.this.level());

                assert ravager != null;

                ravager.setPos(OldMagispellerEntity.this.getX(), OldMagispellerEntity.this.getY(), OldMagispellerEntity.this.getZ());
                ravager.setTarget(OldMagispellerEntity.this.getTarget());
                ravager.setOwner(OldMagispellerEntity.this);
                if (OldMagispellerEntity.this.getTeam() != null) {
                    OldMagispellerEntity.this.level().getScoreboard().addPlayerToTeam(ravager.getStringUUID(), OldMagispellerEntity.this.level().getScoreboard().getPlayerTeam(OldMagispellerEntity.this.getTeam().getName()));
                }

                OldMagispellerEntity.this.level().addFreshEntity(ravager);
                OldMagispellerEntity.this.startRiding(ravager);
            }

            OldMagispellerEntity.this.setWEEEEEEEEEEEEE(true);
            OldMagispellerEntity.this.setSpinning(false);
        }
    }

    class LifeStealGoal extends Goal {
        public LifeStealGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 75.0F < 0.9F && !OldMagispellerEntity.this.isPassenger();
        }

        public void start() {
            OldMagispellerEntity.this.setSpinning(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SPIN.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.LIFESTEAL_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 139;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            OldMagispellerEntity.this.setWavingArms(false);
        }
    }

    class ShootFireballGoal extends Goal {
        public ShootFireballGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 75.0F < 0.9F;
        }

        public void start() {
            OldMagispellerEntity.this.setWavingArms(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_FIREBALL.get(), 2.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.FIREBALL_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 50;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            OldMagispellerEntity.this.setWavingArms(false);
        }
    }

    class ThrowPotionsGoal extends Goal {
        public ThrowPotionsGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 75.0F < 0.9F && !OldMagispellerEntity.this.getTarget().hasEffect(MobEffects.MOVEMENT_SLOWDOWN) && OldMagispellerEntity.this.isTargetLowEnoughForGround() && OldMagispellerEntity.this.isTargetCloseEnoughForRange();
        }

        public void start() {
            OldMagispellerEntity.this.setSpinning(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SPIN.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.POTIONS_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 53;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            OldMagispellerEntity.this.setSpinning(false);
        }
    }

    class SummonVexesGoal extends Goal {
        public SummonVexesGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 100.0F < 0.9F && OldMagispellerEntity.this.vexCooldown < 1;
        }

        public void start() {
            OldMagispellerEntity.this.setWavingArms(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SUMMON.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.SUMMON_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 20;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_CAST_SPELL.get(), 1.0F, 1.0F);
            if (!OldMagispellerEntity.this.level().isClientSide) {
                ServerLevel serverworld = (ServerLevel) OldMagispellerEntity.this.level();
                BlockPos blockpos = OldMagispellerEntity.this.blockPosition();

                for (int i = 0; i < 5; ++i) {
                    Vex vex = EntityType.VEX.create(OldMagispellerEntity.this.level());

                    assert vex != null;

                    vex.setPos(OldMagispellerEntity.this.getX(), OldMagispellerEntity.this.getY() + 3.0, OldMagispellerEntity.this.getZ());
                    vex.finalizeSpawn(serverworld, OldMagispellerEntity.this.level().getCurrentDifficultyAt(blockpos), MobSpawnType.MOB_SUMMONED, null, null);
                    vex.setTarget(OldMagispellerEntity.this.getTarget());
                    if (OldMagispellerEntity.this.getTeam() != null) {
                        OldMagispellerEntity.this.level().getScoreboard().addPlayerToTeam(vex.getStringUUID(), OldMagispellerEntity.this.level().getScoreboard().getPlayerTeam(OldMagispellerEntity.this.getTeam().getName()));
                    }

                    Objects.requireNonNull(vex.getAttribute(Attributes.MAX_HEALTH)).setBaseValue(1.0);
                    vex.setLimitedLife(100);
                    vex.setItemSlot(EquipmentSlot.MAINHAND, ItemStack.EMPTY);
                    vex.setItemSlot(EquipmentSlot.OFFHAND, ItemStack.EMPTY);
                    OldMagispellerEntity.this.level().addFreshEntity(vex);
                }
            }

            OldMagispellerEntity.this.setWavingArms(false);
            OldMagispellerEntity.this.vexCooldown = 900;
        }
    }

    class FangRunGoal extends Goal {
        public FangRunGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 75.0F < 0.9F && OldMagispellerEntity.this.isTargetLowEnoughForGround() && OldMagispellerEntity.this.isTargetCloseEnoughForRange() && !OldMagispellerEntity.this.isPassenger();
        }

        public void start() {
            OldMagispellerEntity.this.setWavingArms(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_FANGRUN.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.FANGRUN_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 103;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            OldMagispellerEntity.this.setWavingArms(false);
            if (!OldMagispellerEntity.this.level().isClientSide) {
                OldMagispellerEntity.this.setForcefield(false);
            }

        }
    }

    class DispenserGoal extends Goal {
        public DispenserGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 75.0F < 0.9F && OldMagispellerEntity.this.dispenserCooldown < 1 && OldMagispellerEntity.this.isTargetLowEnoughForGround() && !OldMagispellerEntity.this.isPassenger();
        }

        public void start() {
            OldMagispellerEntity.this.setSpinning(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SPIN.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.DISPENSER_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 17;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_DISPENSER.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.setSpinning(false);
            if (!OldMagispellerEntity.this.level().isClientSide) {
                DispenserEntity dispenser = ModEntityTypes.Dispenser.get().create(OldMagispellerEntity.this.level());

                assert dispenser != null;

                dispenser.setPos(OldMagispellerEntity.this.getX(), OldMagispellerEntity.this.getY() + 3.0, OldMagispellerEntity.this.getZ());
                dispenser.setDeltaMovement((double) (-2 + OldMagispellerEntity.this.random.nextInt(5)) * 0.3, 0.3, (double) (-2 + OldMagispellerEntity.this.random.nextInt(5)) * 0.3);
                if (OldMagispellerEntity.this.getTeam() != null) {
                    OldMagispellerEntity.this.level().getScoreboard().addPlayerToTeam(dispenser.getStringUUID(), OldMagispellerEntity.this.level().getScoreboard().getPlayerTeam(OldMagispellerEntity.this.getTeam().getName()));
                }

                dispenser.setOwner(OldMagispellerEntity.this);
                dispenser.setInMotion(true);
                OldMagispellerEntity.this.level().addFreshEntity(dispenser);
            }

            OldMagispellerEntity.this.dispenserCooldown = 300;
        }
    }

    class HealGoal extends Goal {
        public HealGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.attackType == 0 && !OldMagispellerEntity.this.isFaking() && !OldMagispellerEntity.this.areIllagersNearby() && OldMagispellerEntity.this.random.nextFloat() * 25.0F < 0.9F && OldMagispellerEntity.this.getHealth() < OldMagispellerEntity.this.getMaxHealth() && !OldMagispellerEntity.this.hasEffect(MobEffects.REGENERATION) && !OldMagispellerEntity.this.isGoingWEEEEEEEEEEE();
        }

        public void start() {
            OldMagispellerEntity.this.setWavingArms(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_HEAL.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.HEAL_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 34;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            OldMagispellerEntity.this.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 200, 3));
            OldMagispellerEntity.this.setWavingArms(false);
        }
    }

    class CrossbowSpinGoal extends Goal {
        public CrossbowSpinGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 75.0F < 0.9F && !OldMagispellerEntity.this.isGoingWEEEEEEEEEEE();
        }

        public void start() {
            OldMagispellerEntity.this.setSpinning(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_SPIN.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.CROSSBOWSPIN_ATTACK;
            if (OldMagispellerEntity.this.getTarget() != null && !OldMagispellerEntity.this.level().isClientSide) {
                OldMagispellerEntity.this.setDeltaMovement((OldMagispellerEntity.this.getTarget().getX() - OldMagispellerEntity.this.getX()) * 2.0 * 0.16, 0.5, (OldMagispellerEntity.this.getTarget().getZ() - OldMagispellerEntity.this.getZ()) * 2.0 * 0.16);
            }

        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 93;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            OldMagispellerEntity.this.setSpinning(false);
            OldMagispellerEntity.this.setCrossbowAttacking(false);
        }
    }

    class ClonesGoal extends Goal {
        public ClonesGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.doesAttackMeetNormalRequirements() && OldMagispellerEntity.this.random.nextFloat() * 50.0F < 0.9F && OldMagispellerEntity.this.getHealth() < OldMagispellerEntity.this.getMaxHealth() / 2.0F && OldMagispellerEntity.this.isTargetLowEnoughForGround() && !OldMagispellerEntity.this.isPassenger();
        }

        public void start() {
            OldMagispellerEntity.this.setWavingArms(true);
            OldMagispellerEntity.this.playSound(IllageAndSpillageSoundEvents.ENTITY_MAGISPELLER_PREPARE_FAKERS.get(), 1.0F, 1.0F);
            OldMagispellerEntity.this.attackType = OldMagispellerEntity.this.CLONES_ATTACK;
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.attackTicks <= 51;
        }

        public void tick() {
        }

        public void stop() {
            OldMagispellerEntity.this.attackTicks = 0;
            OldMagispellerEntity.this.attackType = 0;
            if (OldMagispellerEntity.this.getTarget() != null) {
                if (!OldMagispellerEntity.this.level().isClientSide) {
                    int i;
                    for (i = 0; i < 11; ++i) {
                        FakeMagispellerEntity clone = ModEntityTypes.Faker.get().create(OldMagispellerEntity.this.level());

                        assert clone != null;

                        clone.setPos(OldMagispellerEntity.this.position().x, OldMagispellerEntity.this.position().y, OldMagispellerEntity.this.position().z);
                        clone.setTarget(OldMagispellerEntity.this.getTarget());
                        clone.setItemSlot(EquipmentSlot.MAINHAND, OldMagispellerEntity.this.getItemBySlot(EquipmentSlot.MAINHAND));
                        clone.setItemSlot(EquipmentSlot.OFFHAND, OldMagispellerEntity.this.getItemBySlot(EquipmentSlot.OFFHAND));
                        clone.setItemSlot(EquipmentSlot.HEAD, OldMagispellerEntity.this.getItemBySlot(EquipmentSlot.HEAD));
                        clone.setItemSlot(EquipmentSlot.CHEST, OldMagispellerEntity.this.getItemBySlot(EquipmentSlot.CHEST));
                        clone.setItemSlot(EquipmentSlot.LEGS, OldMagispellerEntity.this.getItemBySlot(EquipmentSlot.LEGS));
                        clone.setItemSlot(EquipmentSlot.FEET, OldMagispellerEntity.this.getItemBySlot(EquipmentSlot.FEET));
                        clone.setDropChance(EquipmentSlot.MAINHAND, 0.0F);
                        clone.setDropChance(EquipmentSlot.OFFHAND, 0.0F);
                        clone.setDropChance(EquipmentSlot.HEAD, 0.0F);
                        clone.setDropChance(EquipmentSlot.CHEST, 0.0F);
                        clone.setDropChance(EquipmentSlot.LEGS, 0.0F);
                        clone.setDropChance(EquipmentSlot.FEET, 0.0F);
                        clone.setHealth(OldMagispellerEntity.this.getHealth());
                        clone.setOwner(OldMagispellerEntity.this);
                        if (OldMagispellerEntity.this.hasCustomName()) {
                            clone.setCustomName(OldMagispellerEntity.this.getCustomName());
                        }

                        if (OldMagispellerEntity.this.getTeam() != null) {
                            OldMagispellerEntity.this.level().getScoreboard().addPlayerToTeam(clone.getStringUUID(), OldMagispellerEntity.this.level().getScoreboard().getPlayerTeam(OldMagispellerEntity.this.getTeam().getName()));
                        }

                        OldMagispellerEntity.this.level().addFreshEntity(clone);
                        clone.tryToTeleportToEntity(OldMagispellerEntity.this.getTarget());
                        OldMagispellerEntity.this.clones.add(clone);
                    }

                    for (i = 0; i < 5; ++i) {
                        OldMagispellerEntity.this.teleportTowards(OldMagispellerEntity.this.getTarget());
                    }
                }

                OldMagispellerEntity.this.distractAttackers(OldMagispellerEntity.this.clones.get(OldMagispellerEntity.this.random.nextInt(OldMagispellerEntity.this.clones.size())));
            }

            OldMagispellerEntity.this.setFaking(true);
            OldMagispellerEntity.this.setVindicatorAttacking(true);
            OldMagispellerEntity.this.setSpinning(false);
        }
    }

    class StareAtTargetGoal extends Goal {
        public StareAtTargetGoal() {
            this.setFlags(EnumSet.of(Flag.LOOK, Flag.MOVE, Flag.JUMP));
        }

        public boolean canUse() {
            return OldMagispellerEntity.this.getTarget() != null && !OldMagispellerEntity.this.isActive();
        }

        public boolean canContinueToUse() {
            return OldMagispellerEntity.this.getTarget() != null && !OldMagispellerEntity.this.isActive();
        }

        public void tick() {
            OldMagispellerEntity.this.getNavigation().stop();
            if (OldMagispellerEntity.this.getTarget() != null) {
                OldMagispellerEntity.this.getLookControl().setLookAt(OldMagispellerEntity.this.getTarget(), 100.0F, 100.0F);
            }

            OldMagispellerEntity.this.navigation.stop();
        }
    }
}

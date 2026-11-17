package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraftforge.registries.ForgeRegistries;

import javax.annotation.Nullable;
import java.time.LocalDate;
import java.time.temporal.ChronoField;
import java.util.Collections;
import java.util.List;

public class BossRandomizerEntity extends AbstractIllager {
    private static final EntityDataAccessor<Boolean> SHOULD_DELETE_ITSELF;

    public BossRandomizerEntity(EntityType<? extends AbstractIllager> p_i48556_1_, Level p_i48556_2_) {
        super(p_i48556_1_, p_i48556_2_);
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new FloatGoal(this));
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
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 24.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(SHOULD_DELETE_ITSELF, false);
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public void tick() {
        super.tick();
        if (this.getCurrentRaid() != null && this.getCurrentRaid().getGroupsSpawned() == 7 && this.shouldRemoveItself() && Config.CommonConfig.bossrandomizer_onlyOneAllowed.get()) {
            this.getCurrentRaid().removeFromRaid(this, true);
            if (!this.level().isClientSide) {
                this.remove(RemovalReason.DISCARDED);
            }
        }

        if (this.tickCount >= 15 && this.getCurrentRaid() != null) {
            if (this.getCurrentRaid().getGroupsSpawned() <= 7) {
                if (Config.CommonConfig.bossrandomizer_broadcastBossSpawn.get()) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_BOSSRANDOMIZER_BOSS.get(), 15.0F, 1.0F);
                }

                this.spawnBoss();
            } else {
                if (Config.CommonConfig.bossrandomizer_broadcastBossSpawn.get()) {
                    LocalDate localdate = LocalDate.now();
                    int i = localdate.get(ChronoField.DAY_OF_MONTH);
                    int j = localdate.get(ChronoField.MONTH_OF_YEAR);
                    if (j == 4 && i == 1) {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_BOSSRANDOMIZER_GOOFY.get(), 15.0F, 1.0F);
                    } else {
                        this.playSound(IllageAndSpillageSoundEvents.ENTITY_BOSSRANDOMIZER_FINALBOSS.get(), 15.0F, 1.0F);
                    }
                }

                this.spawnFinalBoss();
            }
        }

    }

    public boolean shouldRemoveItself() {
        return this.entityData.get(SHOULD_DELETE_ITSELF);
    }

    public void setShouldDeleteItself(boolean shouldDelete) {
        this.entityData.set(SHOULD_DELETE_ITSELF, shouldDelete);
    }

    public boolean canBeLeader() {
        return false;
    }

    @Nullable
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor p_213386_1_, DifficultyInstance p_213386_2_, MobSpawnType p_213386_3_, @Nullable SpawnGroupData p_213386_4_, @Nullable CompoundTag p_213386_5_) {
        if (p_213386_3_ == MobSpawnType.EVENT) {
            this.setShouldDeleteItself(true);
        }

        return super.finalizeSpawn(p_213386_1_, p_213386_2_, p_213386_3_, p_213386_4_, p_213386_5_);
    }

    private void spawnBoss() {
        BlockPos blockPos = this.getOnPos();
        boolean summonedMobFromConfig = this.summonMobFromConfig(blockPos);
        if (!summonedMobFromConfig) {
            if (this.tickCount == 15) {
                IllageAndSpillage.LOGGER.warn("Illage and Spillage couldn't spawn a boss! Check the config file for invalid registry names!");
            }

            this.setCustomName(Component.translatable("entity.illageandspillage.boss_randomizer.check_configs"));
        }

        if (summonedMobFromConfig && this.getCurrentRaid() != null) {
            this.getCurrentRaid().removeFromRaid(this, true);
            if (!this.level().isClientSide) {
                this.remove(RemovalReason.DISCARDED);
            }
        }

    }

    private void spawnFinalBoss() {
        BlockPos blockPos = this.getOnPos();
        boolean summonedMobFromConfig = this.summonFinalBossFromConfig(blockPos);
        if (!summonedMobFromConfig) {
            if (this.tickCount == 15) {
                IllageAndSpillage.LOGGER.warn("Illage and Spillage couldn't spawn a boss! Check the config file for invalid registry names!");
            }

            this.setCustomName(Component.translatable("entity.illageandspillage.boss_randomizer.check_configs"));
        }

        if (summonedMobFromConfig && this.getCurrentRaid() != null) {
            this.getCurrentRaid().removeFromRaid(this, true);
            if (!this.level().isClientSide) {
                this.remove(RemovalReason.DISCARDED);
            }
        }

    }

    private boolean summonMobFromConfig(BlockPos blockPos) {
        List<? extends String> mobSpawns = Config.CommonConfig.bossrandomizer_bosstypes.get();
        if (mobSpawns.isEmpty()) {
            return false;
        } else {
            Collections.shuffle(mobSpawns);
            int randomIndex = this.getRandom().nextInt(mobSpawns.size());
            String randomMobID = mobSpawns.get(randomIndex);
            EntityType<?> entityType = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(randomMobID));
            if (entityType == null) {
                return false;
            } else {
                Entity entity = entityType.create(this.level());
                if (!(entity instanceof Mob mobEntity)) {
                    return false;
                } else {
                    DifficultyInstance difficultyForLocation = this.level().getCurrentDifficultyAt(blockPos.above());
                    mobEntity.moveTo(blockPos.above(), 0.0F, 0.0F);
                    if (!this.level().isClientSide) {
                        mobEntity.finalizeSpawn((ServerLevelAccessor) this.level(), difficultyForLocation, MobSpawnType.EVENT, null, null);
                    }

                    if (mobEntity instanceof Raider) {
                        ((Raider) mobEntity).setCanJoinRaid(true);
                    }

                    return this.level().addFreshEntity(mobEntity);
                }
            }
        }
    }

    private boolean summonFinalBossFromConfig(BlockPos blockPos) {
        List<? extends String> mobSpawns = Config.CommonConfig.bossrandomizer_finalbosstypes.get();
        if (mobSpawns.isEmpty()) {
            return false;
        } else {
            Collections.shuffle(mobSpawns);
            int randomIndex = this.getRandom().nextInt(mobSpawns.size());
            String randomMobID = mobSpawns.get(randomIndex);
            EntityType<?> entityType = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(randomMobID));
            if (entityType == null) {
                return false;
            } else {
                Entity entity = entityType.create(this.level());
                if (!(entity instanceof Mob mobEntity)) {
                    return false;
                } else {
                    DifficultyInstance difficultyForLocation = this.level().getCurrentDifficultyAt(blockPos.above());
                    mobEntity.moveTo(blockPos.above(), 0.0F, 0.0F);
                    if (!this.level().isClientSide) {
                        mobEntity.finalizeSpawn((ServerLevelAccessor) this.level(), difficultyForLocation, MobSpawnType.EVENT, (SpawnGroupData) null, (CompoundTag) null);
                    }

                    if (mobEntity instanceof Raider) {
                        ((Raider) mobEntity).setCanJoinRaid(true);
                    }

                    return this.level().addFreshEntity(mobEntity);
                }
            }
        }
    }

    public SoundEvent getCelebrateSound() {
        return SoundEvents.PILLAGER_CELEBRATE;
    }

    protected SoundEvent getAmbientSound() {
        return IllageAndSpillageSoundEvents.ENTITY_BOSSRANDOMIZER_AMBIENT.get();
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return IllageAndSpillageSoundEvents.ENTITY_BOSSRANDOMIZER_HURT.get();
    }

    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_BOSSRANDOMIZER_DEATH.get();
    }

    public boolean isCustomNameVisible() {
        return true;
    }

    static {
        SHOULD_DELETE_ITSELF = SynchedEntityData.defineId(BossRandomizerEntity.class, EntityDataSerializers.BOOLEAN);
    }
}

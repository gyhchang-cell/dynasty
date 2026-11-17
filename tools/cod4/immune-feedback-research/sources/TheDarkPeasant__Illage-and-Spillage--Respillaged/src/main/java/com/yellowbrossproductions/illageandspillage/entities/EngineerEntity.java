package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.client.model.animation.ICanBeAnimated;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.AbstractIllager;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.pathfinder.Path;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.Objects;

public class EngineerEntity extends AbstractIllager implements ICanBeAnimated {
    private static final EntityDataAccessor<Integer> ANIMATION_STATE = SynchedEntityData.defineId(EngineerEntity.class, EntityDataSerializers.INT);
    public AnimationState throwAnimationState = new AnimationState();
    public AnimationState repairAnimationState = new AnimationState();
    private int throwCooldown = 100;
    private int repairCooldown;
    private int attackTicks;
    private int repairTicks;
    private int attackType;
    private Monster toRepair;
    private final int THROW_ATTACK = 1;
    private final int REPAIR_ATTACK = 2;

    public EngineerEntity(EntityType<? extends AbstractIllager> p_32105_, Level p_32106_) {
        super(p_32105_, p_32106_);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 30.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 64.0);
    }

    @Override
    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new EngineerAvoidEntityGoal(this, Player.class, 8.0F, 0.8, 1.0));
        this.goalSelector.addGoal(1, new EngineerAvoidEntityGoal(this, IronGolem.class, 8.0F, 0.8, 1.0));
        this.goalSelector.addGoal(3, new Raider.HoldGroundAttackGoal(this, 10.0F));
        this.goalSelector.addGoal(2, new ThrowMachineGoal());
        this.goalSelector.addGoal(2, new RepairGoal());
        this.goalSelector.addGoal(8, new EngineerRandomStrollGoal(this, 0.6));
        this.goalSelector.addGoal(9, new EngineerLookAtEntityGoal(this, Player.class, 15.0F, 1.0F));
        this.goalSelector.addGoal(10, new EngineerLookAtEntityGoal(this, Mob.class, 15.0F));
        this.targetSelector.addGoal(1, (new HurtByTargetGoal(this, Raider.class)).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ANIMATION_STATE, 0);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> p_21104_) {
        super.onSyncedDataUpdated(p_21104_);
        if (ANIMATION_STATE.equals(p_21104_) && this.level().isClientSide) {
            switch (this.entityData.get(ANIMATION_STATE)) {
                case 0 -> this.stopAllAnimationStates();
                case 1 -> {
                    this.stopAllAnimationStates();
                    this.throwAnimationState.start(this.tickCount);
                }
                case 2 -> {
                    this.stopAllAnimationStates();
                    this.repairAnimationState.start(this.tickCount);
                }
            }
        }
    }

    private void stopAllAnimationStates() {
        this.throwAnimationState.stop();
        this.repairAnimationState.stop();
    }

    @Override
    public void applyRaidBuffs(int p_37844_, boolean p_37845_) {
    }

    @Override
    public SoundEvent getCelebrateSound() {
        return IllageAndSpillageSoundEvents.ENTITY_ENGINEER_AMBIENT.get();
    }

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return IllageAndSpillageSoundEvents.ENTITY_ENGINEER_AMBIENT.get();
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource p_33034_) {
        return IllageAndSpillageSoundEvents.ENTITY_ENGINEER_HURT.get();
    }

    @Override
    protected SoundEvent getDeathSound() {
        return IllageAndSpillageSoundEvents.ENTITY_ENGINEER_DEATH.get();
    }

    public void setAnimationState(int state) {
        this.entityData.set(ANIMATION_STATE, state);
    }

    public int getAnimationState() {
        return this.entityData.get(ANIMATION_STATE);
    }

    @Override
    public AnimationState getAnimationState(String input) {
        if (Objects.equals(input, "throw")) {
            return this.throwAnimationState;
        }
        if (Objects.equals(input, "repair")) {
            return this.repairAnimationState;
        }
        return new AnimationState();
    }

    public List<Raider> getMachines() {
        return this.level().getEntitiesOfClass(Raider.class, this.getBoundingBox().inflate(100.0), (predicate) -> predicate instanceof EngineerMachine && ((EngineerMachine) predicate).getOwner() == this);
    }

    @Override
    public void tick() {
        super.tick();

        if (this.attackType < 1 && (Config.CommonConfig.engineer_machine_limit.get() < 0 || this.getMachines().size() < Config.CommonConfig.engineer_machine_limit.get())) {
            --this.throwCooldown;
        }

        if (this.attackType < 1) {
            --this.repairCooldown;
        } else {
            this.attackTicks++;
        }

        if (this.repairTicks > 0) {
            this.repairTicks++;
        }

        if (this.isAlive()) {
            if (this.attackType == THROW_ATTACK && attackTicks == 5) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_ENGINEER_THROW.get(), 2.0f, this.getVoicePitch());
                this.playSound(SoundEvents.WITCH_THROW, 1.0f, this.getVoicePitch());
                if (!this.level().isClientSide) {
                    int randomSelection = this.random.nextInt(0, 3);
                    if (randomSelection == 0) {
                        HinderEntity hinder = ModEntityTypes.Hinder.get().create(this.level());

                        assert hinder != null;

                        hinder.setPos(this.getX(), this.getY() + 1, this.getZ());
                        hinder.setDeltaMovement((double) (-2 + this.random.nextInt(5)) * 0.4, 0.6, (double) (-2 + this.random.nextInt(5)) * 0.4);
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(hinder.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        hinder.setInMotion(true);
                        hinder.setOwner(this);
                        this.level().addFreshEntity(hinder);
                    } else if (randomSelection == 1) {
                        ChagrinSentryEntity sentry = ModEntityTypes.ChagrinSentry.get().create(this.level());

                        assert sentry != null;

                        sentry.setPos(this.getX(), this.getY() + 1, this.getZ());
                        sentry.setDeltaMovement((double) (-2 + this.random.nextInt(5)) * 0.4, 0.6, (double) (-2 + this.random.nextInt(5)) * 0.4);
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(sentry.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        sentry.setInMotion(true);
                        sentry.setOwner(this);
                        this.level().addFreshEntity(sentry);
                    } else {
                        FactoryEntity factory = ModEntityTypes.Factory.get().create(this.level());

                        assert factory != null;

                        factory.setPos(this.getX(), this.getY() + 1, this.getZ());
                        factory.setDeltaMovement((double) (-2 + this.random.nextInt(5)) * 0.4, 0.6, (double) (-2 + this.random.nextInt(5)) * 0.4);
                        if (this.getTeam() != null) {
                            this.level().getScoreboard().addPlayerToTeam(factory.getStringUUID(), this.level().getScoreboard().getPlayerTeam(this.getTeam().getName()));
                        }

                        factory.setInMotion(true);
                        factory.setOwner(this);
                        factory.setAnimationState(1);
                        this.level().addFreshEntity(factory);
                    }
                }
            }

            if (this.attackType == REPAIR_ATTACK) {
                if (this.repairTicks < 1 && this.distanceToSqr(this.toRepair) <= 4) {
                    repairTicks = 1;
                    this.setAnimationState(2);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_ENGINEER_THROW.get(), 2.0f, this.getVoicePitch());
                }
                if (this.repairTicks == 8 || this.repairTicks == 21 || this.repairTicks == 31) {
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_ENGINEER_REPAIR.get(), 2.0f, this.getVoicePitch());
                    this.toRepair.heal(5);
                }
            }
        }
    }

    class ThrowMachineGoal extends Goal {
        @Override
        public boolean canUse() {
            return EngineerEntity.this.attackType == 0 && EngineerEntity.this.getTarget() != null && EngineerEntity.this.throwCooldown < 1 && (Config.CommonConfig.engineer_machine_limit.get() < 0 || EngineerEntity.this.getMachines().size() < Config.CommonConfig.engineer_machine_limit.get());
        }

        @Override
        public void start() {
            super.start();
            EngineerEntity.this.setAnimationState(1);
            EngineerEntity.this.attackType = THROW_ATTACK;
        }

        @Override
        public boolean canContinueToUse() {
            return attackTicks <= 20;
        }

        @Override
        public void stop() {
            EngineerEntity.this.attackType = 0;
            EngineerEntity.this.attackTicks = 0;
            EngineerEntity.this.setAnimationState(0);
            EngineerEntity.this.throwCooldown = EngineerEntity.this.random.nextInt(300, 501);
        }
    }

    class RepairGoal extends Goal {
        private Path path;

        @Override
        public boolean canUse() {
            boolean initialConditions = EngineerEntity.this.attackType == 0 && EngineerEntity.this.repairCooldown < 1;
            if (!initialConditions) return false;

            double closestDistance = Double.MAX_VALUE;
            Raider closestToRepair = null;

            for (Raider machine : EngineerEntity.this.getMachines()) {
                if (machine.getHealth() <= machine.getMaxHealth() / 2) {
                    double distance = EngineerEntity.this.distanceToSqr(machine);

                    if (distance < closestDistance) {
                        closestDistance = distance;
                        closestToRepair = machine;
                    }
                }
            }

            EngineerEntity.this.toRepair = closestToRepair;

            this.path = EngineerEntity.this.toRepair == null ? null : EngineerEntity.this.getNavigation().createPath(EngineerEntity.this.toRepair, 0);

            return this.path != null;
        }

        @Override
        public void start() {
            EngineerEntity.this.attackType = REPAIR_ATTACK;
            EngineerEntity.this.getNavigation().stop();
            EngineerEntity.this.getNavigation().moveTo(this.path, 1.0);
        }

        @Override
        public boolean canContinueToUse() {
            if ((repairTicks > 0 && EngineerEntity.this.distanceToSqr(EngineerEntity.this.toRepair) > 4) || !EngineerEntity.this.toRepair.isAlive()) {
                EngineerEntity.this.getNavigation().stop();
                return false;
            }

            return EngineerEntity.this.toRepair != null && EngineerEntity.this.isAlive() && EngineerEntity.this.toRepair.getHealth() < EngineerEntity.this.toRepair.getMaxHealth() && EngineerEntity.this.repairTicks > 0 ? EngineerEntity.this.repairTicks <= 40 : EngineerEntity.this.attackTicks <= 300;
        }

        @Override
        public void tick() {
            if (repairTicks > 0) EngineerEntity.this.getNavigation().stop();
            EngineerEntity.this.setTarget(null);
            if (EngineerEntity.this.toRepair != null) {
                EngineerEntity.this.getLookControl().setLookAt(EngineerEntity.this.toRepair, 100.0F, 100.0F);
            }
        }

        @Override
        public void stop() {
            EngineerEntity.this.attackType = 0;
            if (attackTicks > 300 && repairTicks < 1) EngineerEntity.this.getNavigation().stop();
            EngineerEntity.this.attackTicks = 0;
            EngineerEntity.this.repairTicks = 0;
            EngineerEntity.this.setAnimationState(0);
            EngineerEntity.this.repairCooldown = 300;
        }
    }

    class EngineerAvoidEntityGoal extends AvoidEntityGoal {
        public EngineerAvoidEntityGoal(PathfinderMob p_25027_, Class p_25028_, float p_25029_, double p_25030_, double p_25031_) {
            super(p_25027_, p_25028_, p_25029_, p_25030_, p_25031_);
        }

        @Override
        public boolean canUse() {
            return super.canUse() && EngineerEntity.this.attackType == 0;
        }

        @Override
        public boolean canContinueToUse() {
            return super.canContinueToUse() && EngineerEntity.this.attackType == 0;
        }
    }

    class EngineerRandomStrollGoal extends RandomStrollGoal {
        public EngineerRandomStrollGoal(PathfinderMob p_25734_, double p_25735_) {
            super(p_25734_, p_25735_);
        }

        @Override
        public boolean canUse() {
            return super.canUse() && EngineerEntity.this.attackType == 0;
        }

        @Override
        public boolean canContinueToUse() {
            return super.canContinueToUse() && EngineerEntity.this.attackType == 0;
        }

        @Override
        public void stop() {
            if (EngineerEntity.this.attackType != REPAIR_ATTACK) super.stop();
        }
    }

    class EngineerLookAtEntityGoal extends LookAtPlayerGoal {
        public EngineerLookAtEntityGoal(Mob p_25524_, Class<? extends LivingEntity> p_25525_, float p_25526_, float p_25527_) {
            super(p_25524_, p_25525_, p_25526_, p_25527_);
        }

        public EngineerLookAtEntityGoal(Mob p_25524_, Class<? extends LivingEntity> p_25525_, float p_25526_) {
            super(p_25524_, p_25525_, p_25526_);
        }

        @Override
        public boolean canUse() {
            return super.canUse() && EngineerEntity.this.attackType == 0;
        }

        @Override
        public boolean canContinueToUse() {
            return super.canContinueToUse() && EngineerEntity.this.attackType == 0;
        }
    }
}
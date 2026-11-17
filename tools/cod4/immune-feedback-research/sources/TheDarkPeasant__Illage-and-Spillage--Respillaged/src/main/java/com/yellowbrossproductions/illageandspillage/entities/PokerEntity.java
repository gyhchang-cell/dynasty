package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.entities.goal.FactoryMinionFollowOwnerGoal;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.RandomSource;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import org.jetbrains.annotations.Nullable;

public class PokerEntity extends Raider implements FactoryMinion, IllagerAttack {
    private FactoryEntity owner;

    public PokerEntity(EntityType<? extends Raider> p_37839_, Level p_37840_) {
        super(p_37839_, p_37840_);
        this.xpReward = 0;
    }

    @Nullable
    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor p_37856_, DifficultyInstance p_37857_, MobSpawnType p_37858_, @Nullable SpawnGroupData p_37859_, @Nullable CompoundTag p_37860_) {
        this.populateDefaultEquipmentSlots(p_37856_.getRandom(), p_37857_);
        return super.finalizeSpawn(p_37856_, p_37857_, p_37858_, p_37859_, p_37860_);
    }

    @Override
    protected void populateDefaultEquipmentSlots(RandomSource p_217055_, DifficultyInstance p_217056_) {
        this.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.IRON_SWORD));
        this.setDropChance(EquipmentSlot.MAINHAND, 0.0F);
        this.setDropChance(EquipmentSlot.OFFHAND, 0.0F);
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.0, false));
        this.goalSelector.addGoal(2, new FactoryMinionFollowOwnerGoal(this, 1.0D, 2.0F, 100.0F));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
        this.goalSelector.addGoal(6, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this, Raider.class).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMobAttributes().add(Attributes.MAX_HEALTH, 6.0).add(Attributes.MOVEMENT_SPEED, 0.4).add(Attributes.ATTACK_DAMAGE, 1.0);
    }

    @Override
    public boolean isAlliedTo(Entity entity) {
        if (super.isAlliedTo(entity)) {
            return true;
        } else if (entity instanceof Raider || entity instanceof EngineerMachine || entity instanceof FactoryMinion) {
            return this.getTeam() == null && entity.getTeam() == null;
        } else {
            return false;
        }
    }

    @Override
    public void applyRaidBuffs(int p_37844_, boolean p_37845_) {
    }

    @Override
    public SoundEvent getCelebrateSound() {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
    }

    @Override
    public boolean canJoinRaid() {
        return false;
    }

    @Override
    public boolean canBeLeader() {
        return false;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource damageSourceIn) {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
    }

    @Override
    public void tick() {
        super.tick();
    }

    @Override
    public boolean doHurtTarget(Entity p_21372_) {
        boolean superHurt = super.doHurtTarget(p_21372_);
        if (superHurt)
            this.playSound(IllageAndSpillageSoundEvents.ENTITY_ENGINEER_POKER_POKE.get(), 2.0F, this.getVoicePitch());
        return superHurt;
    }

    @Override
    public FactoryEntity getOwner() {
        return this.owner;
    }

    @Override
    public void setOwner(FactoryEntity owner) {
        this.owner = owner;
    }
}
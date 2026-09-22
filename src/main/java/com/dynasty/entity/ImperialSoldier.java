package com.dynasty.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;

import java.util.EnumSet;
import java.util.UUID;

/**
 * 帝国士兵：用虎符召唤的友方部队，会跟随主人并攻击怪物。
 * Imperial Soldier: friendly troops summoned by the Tiger Tally; they follow their owner and hunt monsters.
 */
@SuppressWarnings("null")
public class ImperialSoldier extends PathfinderMob {

    static final int NATURAL_LOCAL_LIMIT = 4;
    static final double NATURAL_LOCAL_RADIUS = 48.0D;
    private UUID ownerId;

    public ImperialSoldier(EntityType<? extends ImperialSoldier> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 1024.0D)
                .add(Attributes.ATTACK_DAMAGE, 300.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.28D)
                .add(Attributes.ARMOR, 20.0D)
                .add(Attributes.FOLLOW_RANGE, 24.0D);
    }

    public void setOwner(Player owner) {
        this.ownerId = owner == null ? null : owner.getUUID();
    }

    public Player getOwner() {
        return this.ownerId == null ? null : this.level().getPlayerByUUID(this.ownerId);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (ownerId != null) tag.putUUID("DynastyOwner", ownerId);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        ownerId = tag.hasUUID("DynastyOwner") ? tag.getUUID("DynastyOwner") : null;
    }

    private static boolean natural(MobSpawnType reason) {
        return reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION;
    }

    @Override
    public boolean checkSpawnRules(LevelAccessor level, MobSpawnType reason) {
        if (!super.checkSpawnRules(level, reason)) return false;
        if (!natural(reason)) return true; // Commands, eggs and the player's army are not wild patrols.
        if (!Mob.checkMobSpawnRules(getType(), level, reason, blockPosition(), level.getRandom())) return false;
        return level.getEntitiesOfClass(ImperialSoldier.class,
                getBoundingBox().inflate(NATURAL_LOCAL_RADIUS),
                soldier -> soldier != this && soldier.isAlive() && natural(soldier.getSpawnType()))
                .size() < NATURAL_LOCAL_LIMIT;
    }

    @Override
    public int getMaxSpawnClusterSize() {
        return 1;
    }

    @Override
    public boolean requiresCustomPersistence() {
        return ownerId != null || hasCustomName() || super.requiresCustomPersistence();
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        // Forge saves forge:spawn_type even for old worlds. Unknown/command origins are
        // deliberately preserved: the old army did not save its owner's UUID.
        return natural(getSpawnType()) && ownerId == null && !hasCustomName()
                && !isPersistenceRequired() && !isLeashed() && !isPassenger() && !isVehicle();
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.2D, true));
        this.goalSelector.addGoal(6, new FollowOwnerGoal());
        this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 8.0F));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Monster.class, true));
    }

    /** 跟随召唤者；离得太远直接传送过去。 / Follows the summoner, teleporting when far away. */
    private class FollowOwnerGoal extends Goal {
        private int nextPathTick;

        FollowOwnerGoal() {
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            Player owner = ImperialSoldier.this.getOwner();
            return owner != null && owner.isAlive()
                    && ImperialSoldier.this.distanceToSqr(owner) > 16.0D;
        }

        @Override
        public boolean canContinueToUse() {
            return canUse();
        }

        @Override
        public void tick() {
            Player owner = ImperialSoldier.this.getOwner();
            if (owner == null) {
                return;
            }
            double dist = ImperialSoldier.this.distanceToSqr(owner);
            if (dist > 256.0D && !ImperialSoldier.this.level().isClientSide) {
                ImperialSoldier.this.teleportTo(owner.getX(), owner.getY(), owner.getZ());
            } else if (ImperialSoldier.this.tickCount >= nextPathTick) {
                ImperialSoldier.this.getNavigation().moveTo(owner, 1.1D);
                nextPathTick = ImperialSoldier.this.tickCount + 10;
            }
            ImperialSoldier.this.getLookControl().setLookAt(owner, 10.0F, ImperialSoldier.this.getMaxHeadXRot());
        }
    }
}

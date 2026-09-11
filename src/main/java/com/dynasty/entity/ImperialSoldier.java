package com.dynasty.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
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

import java.util.EnumSet;

/**
 * 帝国士兵：用虎符召唤的友方部队，会跟随主人并攻击怪物。
 * Imperial Soldier: friendly troops summoned by the Tiger Tally; they follow their owner and hunt monsters.
 */
@SuppressWarnings("null")
public class ImperialSoldier extends PathfinderMob {

    private Player owner;

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
        this.owner = owner;
    }

    public Player getOwner() {
        return this.owner;
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        return false;
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

        FollowOwnerGoal() {
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            return ImperialSoldier.this.owner != null && ImperialSoldier.this.owner.isAlive()
                    && ImperialSoldier.this.distanceToSqr(ImperialSoldier.this.owner) > 16.0D;
        }

        @Override
        public boolean canContinueToUse() {
            return canUse();
        }

        @Override
        public void tick() {
            Player owner = ImperialSoldier.this.owner;
            if (owner == null) {
                return;
            }
            double dist = ImperialSoldier.this.distanceToSqr(owner);
            if (dist > 256.0D && !ImperialSoldier.this.level().isClientSide) {
                ImperialSoldier.this.teleportTo(owner.getX(), owner.getY(), owner.getZ());
            } else {
                ImperialSoldier.this.getNavigation().moveTo(owner, 1.1D);
            }
            ImperialSoldier.this.getLookControl().setLookAt(owner, 10.0F, ImperialSoldier.this.getMaxHeadXRot());
        }
    }
}


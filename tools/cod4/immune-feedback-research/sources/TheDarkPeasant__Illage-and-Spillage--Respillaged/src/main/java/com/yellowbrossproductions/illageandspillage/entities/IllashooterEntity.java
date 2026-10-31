package com.yellowbrossproductions.illageandspillage.entities;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.*;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.IronGolem;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.npc.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;

import java.util.EnumSet;

public class IllashooterEntity extends Raider {
    private static final EntityDataAccessor<Boolean> ATTACKING;
    private int attackTicks;
    private Mob owner;

    public IllashooterEntity(EntityType<? extends Raider> p_i48553_1_, Level p_i48553_2_) {
        super(p_i48553_1_, p_i48553_2_);
    }

    protected void registerGoals() {
        super.registerGoals();
        this.goalSelector.addGoal(0, new AttackGoal());
        this.goalSelector.addGoal(0, new FloatGoal(this));
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
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.4000000059604645).add(Attributes.MAX_HEALTH, 2.0).add(Attributes.ATTACK_DAMAGE, 0.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ATTACKING, false);
    }

    public void applyRaidBuffs(int p_213660_1_, boolean p_213660_2_) {
    }

    public SoundEvent getCelebrateSound() {
        return null;
    }

    public boolean causeFallDamage(float p_147187_, float p_147188_, DamageSource p_147189_) {
        return false;
    }

    public void tick() {
        if (this.isAlive()) {
            if (this.isAttacking()) {
                ++this.attackTicks;
                if (this.attackTicks > 30) {
                    if (this.getTarget() != null) {
                        this.playSound(SoundEvents.DISPENSER_LAUNCH, 1.0F, 1.0F);
                        this.fireArrow(this.getTarget(), 1.0F, 1.0F);
                    }

                    this.attackTicks = 0;
                }
            } else {
                this.attackTicks = 0;
            }

            if (this.getOwner() instanceof DispenserEntity && ((DispenserEntity) this.getOwner()).getOwner() != null) {
                this.setTarget(((DispenserEntity) this.getOwner()).getOwner().getTarget());
            }
        }

        super.tick();
    }

    public boolean isAttacking() {
        return this.entityData.get(ATTACKING);
    }

    public void setAttacking(boolean attacking) {
        this.entityData.set(ATTACKING, attacking);
    }

    protected SoundEvent getHurtSound(DamageSource p_184601_1_) {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
    }

    protected SoundEvent getDeathSound() {
        return SoundEvents.ZOMBIE_ATTACK_IRON_DOOR;
    }

    public void fireArrow(LivingEntity p_82196_1_, float p_82196_2_, float inaccuracy) {
        AbstractArrow abstractarrowentity = this.getArrow(Items.BOW.getDefaultInstance(), p_82196_2_);
        if (this.getMainHandItem().getItem() instanceof BowItem) {
            abstractarrowentity = ((BowItem) this.getMainHandItem().getItem()).customArrow(abstractarrowentity);
        }

        double d0 = p_82196_1_.getX() - this.getX();
        double d1 = p_82196_1_.getY(0.3333333333333333) - abstractarrowentity.getY();
        double d2 = p_82196_1_.getZ() - this.getZ();
        double d3 = Mth.sqrt((float) (d0 * d0 + d2 * d2));
        abstractarrowentity.setBaseDamage(1.0);
        abstractarrowentity.shoot(d0, d1 + d3 * 0.20000000298023224, d2, 1.6F, inaccuracy);
        this.level().addFreshEntity(abstractarrowentity);
    }

    protected AbstractArrow getArrow(ItemStack p_213624_1_, float p_213624_2_) {
        return ProjectileUtil.getMobArrow(this, p_213624_1_, p_213624_2_);
    }

    public boolean canJoinRaid() {
        return false;
    }

    public void die(DamageSource p_70645_1_) {
        super.die(p_70645_1_);
        if (p_70645_1_.getEntity() instanceof Mob && !(p_70645_1_.getEntity() instanceof Raider) && this.getOwner() != null && ((Mob) p_70645_1_.getEntity()).getTarget() == this) {
            ((Mob) p_70645_1_.getEntity()).setTarget(this.getOwner());
        }

    }

    public Mob getOwner() {
        return this.owner;
    }

    public void setOwner(Mob owner) {
        this.owner = owner;
    }

    public boolean canBeLeader() {
        return false;
    }

    static {
        ATTACKING = SynchedEntityData.defineId(IllashooterEntity.class, EntityDataSerializers.BOOLEAN);
    }

    class AttackGoal extends Goal {
        public AttackGoal() {
            this.setFlags(EnumSet.of(Flag.JUMP, Flag.LOOK, Flag.MOVE));
        }

        public boolean canUse() {
            return IllashooterEntity.this.getTarget() != null && IllashooterEntity.this.getTarget().isAlive() && IllashooterEntity.this.distanceToSqr(IllashooterEntity.this.getTarget()) < 90.0 && IllashooterEntity.this.hasLineOfSight(IllashooterEntity.this.getTarget());
        }

        public void start() {
            IllashooterEntity.this.playSound(SoundEvents.PISTON_EXTEND, 1.0F, 1.5F);
            IllashooterEntity.this.setAttacking(true);
        }

        public boolean canContinueToUse() {
            return IllashooterEntity.this.getTarget() != null && IllashooterEntity.this.distanceToSqr(IllashooterEntity.this.getTarget()) < 90.0 && IllashooterEntity.this.getTarget().isAlive() && IllashooterEntity.this.hasLineOfSight(IllashooterEntity.this.getTarget());
        }

        public void tick() {
            IllashooterEntity.this.getNavigation().stop();
            if (IllashooterEntity.this.getTarget() != null) {
                IllashooterEntity.this.getLookControl().setLookAt(IllashooterEntity.this.getTarget(), 30.0F, 30.0F);
            }

            IllashooterEntity.this.navigation.stop();
        }

        public void stop() {
            IllashooterEntity.this.setAttacking(false);
            IllashooterEntity.this.playSound(SoundEvents.PISTON_CONTRACT, 1.0F, 1.5F);
        }
    }
}

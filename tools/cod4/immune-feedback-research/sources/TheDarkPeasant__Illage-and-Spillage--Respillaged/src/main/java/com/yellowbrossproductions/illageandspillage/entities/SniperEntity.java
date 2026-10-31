package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
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
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import java.util.Iterator;

public class SniperEntity extends Raider implements FactoryMinion, IllagerAttack {
    private FactoryEntity owner;
    private int attackTicks;

    public SniperEntity(EntityType<? extends Raider> p_37839_, Level p_37840_) {
        super(p_37839_, p_37840_);
        this.xpReward = 0;
    }

    @Override
    protected void registerGoals() {
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this, Raider.class).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMobAttributes().add(Attributes.MAX_HEALTH, 4.0).add(Attributes.FOLLOW_RANGE, 50.0);
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
    public boolean causeFallDamage(float distance, float damageMultiplier, DamageSource source) {
        return false;
    }

    @Override
    public void die(DamageSource p_37847_) {
        this.makeDeathParticles();
        this.deathTime = 19;
        if (!this.isAlive()) this.playSound(SoundEvents.GENERIC_EXPLODE, 0.5F, 3.0F);

        super.die(p_37847_);
    }

    public void makeDeathParticles() {
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

                for (int i = 0; i < 15; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(new ItemParticleOption(ParticleTypes.ITEM, Items.IRON_BARS.getDefaultInstance()), false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }
                packet.queueParticle(ParticleTypes.EXPLOSION, false, this.getX(), this.getY(), this.getZ(), 1.0D, 0.0D, 0.0D);

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
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
        this.setNoGravity(true);

        ++this.attackTicks;

        LivingEntity flyTo = this.getTarget() != null ? this.getTarget() : this.getOwner() != null && this.getOwner().getOwner() != null && this.getOwner().getOwner().isAlive() ? this.getOwner().getOwner() : null;
        if (flyTo != null) {
            if (this.attackTicks > 40 && flyTo == this.getTarget() && this.distanceToSqr(flyTo) <= 400 && this.hasLineOfSight(flyTo)) {
                this.playSound(SoundEvents.DISPENSER_LAUNCH, 1.0F, 1.0F);
                this.fireArrow(this.getTarget(), 1.0F, 1.0F);

                this.attackTicks = 0;
            }

            this.getLookControl().setLookAt(flyTo, 100.0F, 100.0F);
            double x = this.getX() - flyTo.getX();
            double y = this.getY() - flyTo.getY();
            double z = this.getZ() - flyTo.getZ();
            double d = Math.sqrt(x * x + y * y + z * z);
            float power = 0.08F;
            double motionX = this.getDeltaMovement().x - x / d * (double) power * 0.2;
            double motionY = this.getDeltaMovement().y - y / d * (double) power * 0.2;
            double motionZ = this.getDeltaMovement().z - z / d * (double) power * 0.2;
            if (this.distanceToSqr(flyTo) > 120.0) {
                this.setDeltaMovement(motionX, motionY, motionZ);
            }

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

        super.tick();

        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
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
        abstractarrowentity.setPos(this.getX(), this.getY() + 0.5, this.getZ());
        abstractarrowentity.shoot(d0, d1 + d3 * 0.20000000298023224, d2, 1.6F, inaccuracy);
        this.level().addFreshEntity(abstractarrowentity);
    }

    protected AbstractArrow getArrow(ItemStack p_213624_1_, float p_213624_2_) {
        return ProjectileUtil.getMobArrow(this, p_213624_1_, p_213624_2_);
    }

    @Override
    public boolean doHurtTarget(Entity p_21372_) {
        return true;
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
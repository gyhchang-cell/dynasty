package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.entities.goal.FactoryMinionFollowOwnerGoal;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
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
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.network.PacketDistributor;

import java.util.Collection;
import java.util.EnumSet;
import java.util.Iterator;

public class BeeperEntity extends Raider implements FactoryMinion, IllagerAttack {
    private static final EntityDataAccessor<Integer> STATE = SynchedEntityData.defineId(BeeperEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> POWERED = SynchedEntityData.defineId(BeeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> IGNITED = SynchedEntityData.defineId(BeeperEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Float> PARTIAL_TICKS = SynchedEntityData.defineId(BeeperEntity.class, EntityDataSerializers.FLOAT);
    public int lastActiveTime;
    public int timeSinceIgnited;
    public int fuseTime = 30;
    private float explosionRadius;
    private FactoryEntity owner;

    public BeeperEntity(EntityType<? extends Raider> p_37839_, Level p_37840_) {
        super(p_37839_, p_37840_);
        this.explosionRadius = 1.2f;
        this.xpReward = 0;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(1, new FloatGoal(this));
        this.goalSelector.addGoal(2, new BeeperSwellGoal(this));
        this.goalSelector.addGoal(4, new MeleeAttackGoal(this, 1.0D, false));
        this.goalSelector.addGoal(3, new FactoryMinionFollowOwnerGoal(this, 1.0D, 2.0F, 100.0F));
        this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.8D));
        this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 8.0F));
        this.goalSelector.addGoal(6, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new HurtByTargetGoal(this, Raider.class).setAlertOthers());
        this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
        this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMobAttributes().add(Attributes.MAX_HEALTH, 6.0).add(Attributes.MOVEMENT_SPEED, 0.35D);
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
        boolean flag = super.causeFallDamage(distance, damageMultiplier, source);
        this.timeSinceIgnited = (int) ((float) this.timeSinceIgnited + distance * 1.5F);
        if (this.timeSinceIgnited > this.fuseTime - 5) {
            this.timeSinceIgnited = this.fuseTime - 5;
        }

        return flag;
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(STATE, -1);
        this.entityData.define(POWERED, false);
        this.entityData.define(IGNITED, false);
        this.entityData.define(PARTIAL_TICKS, 1.0F);
    }

    public float getPartialTicks() {
        return this.entityData.get(PARTIAL_TICKS);
    }

    public void setPartialTicks(float partialTicks) {
        this.entityData.set(PARTIAL_TICKS, partialTicks);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag compound) {
        super.addAdditionalSaveData(compound);
        compound.putShort("Fuse", (short) this.fuseTime);
        compound.putFloat("ExplosionRadius", this.explosionRadius);
        compound.putBoolean("Ignited", this.hasIgnited());
        if (this.entityData.get(POWERED)) {
            compound.putBoolean("Powered", true);
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag compound) {
        super.readAdditionalSaveData(compound);
        if (compound.contains("Fuse", 99))
            this.fuseTime = compound.getShort("Fuse");
        if (compound.contains("ExplosionRadius", 99))
            this.explosionRadius = compound.getFloat("ExplosionRadius");
        if (compound.getBoolean("Ignited")) this.ignite();
        this.entityData.set(POWERED, compound.getBoolean("Powered"));
    }

    @Override
    protected float getStandingEyeHeight(Pose poseIn, EntityDimensions sizeIn) {
        return sizeIn.height * 0.8F;
    }

    protected void explode() {
        if (!this.level().isClientSide()) {
            this.dead = true;
            this.makeFireParticles();
            this.level().explode(this, this.getX(), this.getY(), this.getZ(), this.explosionRadius, Level.ExplosionInteraction.NONE);
            this.discard();
            this.spawnLingeringCloud();
            for (LivingEntity hit : this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(1.75))) {
                hit.setSecondsOnFire(5);
            }
        }
    }

    public void makeFireParticles() {
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
                    packet.queueParticle(ParticleTypes.FLAME, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

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
        if (this.isAlive()) {
            this.lastActiveTime = this.timeSinceIgnited;
            if (this.hasIgnited()) {
                this.setCreeperState(1);
            }
            int i = this.getCreeperState();
            if (i > 0 && this.timeSinceIgnited == 0) {
                this.playSound(SoundEvents.TNT_PRIMED, 1.0F, 0.5F);
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_ENGINEER_BEEPER_BEEP.get(), 1.0F, 1.0F);
            }
            this.timeSinceIgnited += i;
            if (this.timeSinceIgnited < 0) {
                this.timeSinceIgnited = 0;
            }

            if (this.timeSinceIgnited >= this.fuseTime) {
                this.timeSinceIgnited = this.fuseTime;
                this.explode();
            }
        }
        super.tick();
    }

    @Override
    public boolean doHurtTarget(Entity p_21372_) {
        return true;
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack itemstack = player.getItemInHand(hand);
        if (itemstack.getItem() == Items.FLINT_AND_STEEL) {
            this.level().playSound(player, this.getX(), this.getY(), this.getZ(), SoundEvents.FLINTANDSTEEL_USE, this.getSoundSource(), 1.0F, this.random.nextFloat() * 0.4F + 0.8F);
            if (!this.level().isClientSide()) {
                this.ignite();
                itemstack.hurtAndBreak(1, player, (p_213625_1_) -> p_213625_1_.broadcastBreakEvent(hand));
            }

            return InteractionResult.SUCCESS;
        } else {
            return InteractionResult.FAIL;
        }
    }

    @OnlyIn(Dist.CLIENT)
    public float getCreeperFlashIntensity(float partialTicks) {
        return Mth.lerp(partialTicks, (float) this.lastActiveTime, (float) this.timeSinceIgnited) / (float) (this.fuseTime - 2);
    }

    public int getCreeperState() {
        return this.entityData.get(STATE);
    }

    public void setCreeperState(int state) {
        this.entityData.set(STATE, state);
    }

    public boolean hasIgnited() {
        return this.entityData.get(IGNITED);
    }

    public void ignite() {
        this.entityData.set(IGNITED, true);
    }

    protected void spawnLingeringCloud() {
        Collection<MobEffectInstance> collection = this.getActiveEffects();
        if (!collection.isEmpty()) {
            AreaEffectCloud areaeffectcloudentity = new AreaEffectCloud(this.level(), this.getX(), this.getY(), this.getZ());
            areaeffectcloudentity.setRadius(1.0F);
            areaeffectcloudentity.setRadiusOnUse(-0.5F);
            areaeffectcloudentity.setWaitTime(10);
            areaeffectcloudentity.setDuration(areaeffectcloudentity.getDuration() / 2);
            areaeffectcloudentity.setRadiusPerTick(-areaeffectcloudentity.getRadius() / (float) areaeffectcloudentity.getDuration());

            for (MobEffectInstance effectinstance : collection) {
                areaeffectcloudentity.addEffect(new MobEffectInstance(effectinstance));
            }

            this.level().addFreshEntity(areaeffectcloudentity);
        }

    }

    @Override
    public FactoryEntity getOwner() {
        return this.owner;
    }

    @Override
    public void setOwner(FactoryEntity owner) {
        this.owner = owner;
    }

    private static class BeeperSwellGoal extends Goal {

        private final BeeperEntity swellingBeeper;
        private LivingEntity beeperAttackTarget;

        public BeeperSwellGoal(BeeperEntity entityIn) {
            this.swellingBeeper = entityIn;
            this.setFlags(EnumSet.of(Goal.Flag.MOVE));
        }

        @Override
        public boolean canUse() {
            LivingEntity livingEntity = this.swellingBeeper.getTarget();
            return this.swellingBeeper.getCreeperState() > 0 || livingEntity != null && this.swellingBeeper.distanceToSqr(livingEntity) < 4.0D;
        }

        @Override
        public void start() {
            this.beeperAttackTarget = this.swellingBeeper.getTarget();
        }

        @Override
        public void stop() {
            this.beeperAttackTarget = null;
        }

        @Override
        public void tick() {
            if (this.beeperAttackTarget == null) {
                this.swellingBeeper.setCreeperState(-1);
            } else if (this.swellingBeeper.distanceToSqr(this.beeperAttackTarget) > 6.25D) {
                this.swellingBeeper.setCreeperState(-1);
            } else if (!this.swellingBeeper.getSensing().hasLineOfSight(this.beeperAttackTarget)) {
                this.swellingBeeper.setCreeperState(-1);
            } else {
                this.swellingBeeper.setCreeperState(1);
                this.swellingBeeper.getNavigation().moveTo(beeperAttackTarget, 0.8D);
            }
        }
    }
}
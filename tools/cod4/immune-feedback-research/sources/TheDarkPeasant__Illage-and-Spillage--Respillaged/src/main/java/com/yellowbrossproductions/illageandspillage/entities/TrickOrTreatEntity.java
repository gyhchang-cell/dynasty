package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import com.yellowbrossproductions.illageandspillage.util.EffectRegisterer;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import com.yellowbrossproductions.illageandspillage.util.ItemRegisterer;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.memory.MemoryModuleType;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.monster.warden.AngerLevel;
import net.minecraft.world.entity.monster.warden.Warden;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

import java.util.Iterator;
import java.util.List;

public class TrickOrTreatEntity extends PathfinderMob implements IllagerAttack {
    private static final EntityDataAccessor<Integer> TREAT;
    private static final EntityDataAccessor<Boolean> BOUNCE;
    private static final EntityDataAccessor<Boolean> GOOPY;
    private static final EntityDataAccessor<Boolean> OLD;
    private LivingEntity owner;
    public int circleTime;
    public int bounceTime;
    public double accelerationX;
    public double accelerationY;
    public double accelerationZ;

    public TrickOrTreatEntity(EntityType<? extends PathfinderMob> p_21683_, Level p_21684_) {
        super(p_21683_, p_21684_);
        this.xpReward = 0;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 6.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0);
    }

    public float getStepHeight() {
        return 2.0F;
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(TREAT, 1);
        this.entityData.define(BOUNCE, false);
        this.entityData.define(GOOPY, false);
        this.entityData.define(OLD, false);
    }

    public boolean getBounce() {
        return this.entityData.get(BOUNCE);
    }

    public void setBounce() {
        this.entityData.set(BOUNCE, true);
    }

    public boolean getGoopy() {
        return this.entityData.get(GOOPY);
    }

    public void setGoopy() {
        this.entityData.set(GOOPY, true);
    }

    public boolean isOld() {
        return this.entityData.get(OLD);
    }

    public void setOld(boolean old) {
        this.entityData.set(OLD, old);
    }

    public void addAdditionalSaveData(CompoundTag p_21484_) {
        super.addAdditionalSaveData(p_21484_);
        p_21484_.putInt("Treat", this.getTreat());
    }

    public void readAdditionalSaveData(CompoundTag p_21450_) {
        super.readAdditionalSaveData(p_21450_);
        this.setTreat(p_21450_.getInt("Treat"));
    }

    public boolean causeFallDamage(float p_147187_, float p_147188_, DamageSource p_147189_) {
        return this.isOld() && super.causeFallDamage(p_147187_, p_147188_, p_147189_);
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return (this.isOld() || !this.getGoopy() || p_21197_.getEffect() != EffectRegisterer.MUTATION.get()) && super.canBeAffected(p_21197_);
    }

    public void tick() {
        super.tick();
        if (this.tickCount % 15 == 0) {
            ++this.circleTime;
        }

        if (this.getOwner() != null) {
            if ((double) this.distanceTo(this.getOwner()) > 30.0) {
                this.getNavigation().moveTo(this.getOwner(), 2.0);
            } else {
                this.circleOwner(this.getOwner(), this.circleTime, Mth.cos((float) this.tickCount / 15.0F));
            }

            this.getLookControl().setLookAt(this.getOwner(), 100.0F, 100.0F);
            int timeLimit = 300 + this.bounceTime * 20;
            if (this.tickCount >= timeLimit) {
                if (this.tickCount == timeLimit) {
                    if (!this.level().isClientSide) {
                        this.setBounce();
                    }

                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_TRICKORTREAT_BOUNCE.get(), 2.0F, 1.9F);
                    this.setDeltaMovement(this.getDeltaMovement().add(0.0, 0.6, 0.0));
                    this.makeTreatParticles();
                }

                if (this.tickCount >= timeLimit + 10) {
                    LivingEntity entity = this.getOwner();
                    double x = this.getX() - entity.getX();
                    double y = this.getY() - (entity.getY() + 2.2);
                    double z = this.getZ() - entity.getZ();
                    double d = Math.sqrt(x * x + y * y + z * z);
                    float power = 5.0F;
                    double motionX = -(x / d * (double) power * 0.2);
                    double motionY = -(y / d * (double) power * 0.2);
                    double motionZ = -(z / d * (double) power * 0.2);
                    this.setAcceleration(motionX, motionY, motionZ);
                    this.noPhysics = true;
                    this.setDeltaMovement(this.accelerationX, this.accelerationY, this.accelerationZ);
                    this.makeTreatParticles();
                    if (this.distanceToSqr(entity) < 6.0) {
                        entity.heal(5.0F);
                        this.makeHealParticles(entity);
                        this.kill();
                    }
                }
            }
        }

        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
    }

    protected boolean shouldDespawnInPeaceful() {
        return this.getOwner() instanceof Monster;
    }

    protected float getStandingEyeHeight(Pose p_21131_, EntityDimensions p_21132_) {
        return 1.06F;
    }

    public void setAcceleration(double x, double y, double z) {
        this.accelerationX = x;
        this.accelerationY = y;
        this.accelerationZ = z;
    }

    public void makeTreatParticles() {
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

                for (int i = 0; i < 10; ++i) {
                    double d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    double d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    ParticleOptions $$1 = this.getParticle();
                    packet.queueParticle($$1, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void makeHealParticles(Entity caught) {
        if (!this.level().isClientSide) {
            Iterator<ServerPlayer> var2 = ((ServerLevel) this.level()).players().iterator();

            while (true) {
                ServerPlayer serverPlayer;
                do {
                    if (!var2.hasNext()) {
                        return;
                    }

                    serverPlayer = var2.next();
                } while (!(serverPlayer.distanceToSqr(this) < 4096.0));

                ParticlePacket packet = new ParticlePacket();

                for (int i = 0; i < 6; ++i) {
                    double d0 = -0.5 + this.random.nextGaussian();
                    double d1 = -0.5 + this.random.nextGaussian();
                    double d2 = -0.5 + this.random.nextGaussian();
                    packet.queueParticle(ParticleTypes.HEART, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public void resetTargeters() {
        List<Mob> list = this.level().getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(100.0));
        if (this.getOwner() != null) {

            for (Mob attacker : list) {
                if (attacker.getLastHurtByMob() == this && this.getOwner() != null) {
                    attacker.setLastHurtByMob(this.getOwner());
                }

                if (attacker.getTarget() == this && this.getOwner() != null) {
                    attacker.setTarget(this.getOwner());
                }

                LivingEntity owner = this.getOwner();
                if (attacker instanceof Warden warden) {
                    if (warden.getTarget() == this) {
                        warden.increaseAngerAt(owner, AngerLevel.ANGRY.getMinimumAnger() + 100, false);
                        warden.setAttackTarget(owner);
                    }
                } else {
                    try {
                        if (attacker.getBrain().hasMemoryValue(MemoryModuleType.ATTACK_TARGET) && attacker.getBrain().getMemory(MemoryModuleType.ATTACK_TARGET).isPresent() && attacker.getBrain().getMemory(MemoryModuleType.ATTACK_TARGET).get() == this) {
                            attacker.getBrain().setMemoryWithExpiry(MemoryModuleType.ANGRY_AT, owner.getUUID(), 600L);
                            attacker.getBrain().setMemoryWithExpiry(MemoryModuleType.ATTACK_TARGET, owner, 600L);
                        }
                    } catch (NullPointerException ignored) {

                    }
                }
            }
        }

    }

    public LivingEntity getOwner() {
        return this.owner;
    }

    public void setOwner(LivingEntity owner) {
        this.owner = owner;
    }

    public int getTreat() {
        return this.entityData.get(TREAT);
    }

    public void setTreat(int t) {
        this.entityData.set(TREAT, t);
    }

    protected void pushEntities() {
    }

    public void die(DamageSource p_21014_) {
        super.die(p_21014_);
        this.deathTime = 19;
        this.playSound(IllageAndSpillageSoundEvents.ENTITY_FREAKAGER_TRICKORTREAT_DESTROY.get(), 1.5F, 1.0F);
        this.makeTreatDestroyedParticles();
        this.resetTargeters();
    }

    private void circleOwner(Entity target, int circleFrame, float offset) {
        int directionInt = 1;
        double t = (double) (directionInt * circleFrame) * 0.5 * (double) (float) 1.0 / (double) (float) 8.0 + (double) offset;
        Vec3 movePos = target.position().add((double) (float) 8.0 * Math.cos(t), 0.0, (double) (float) 8.0 * Math.sin(t));
        this.getNavigation().moveTo(movePos.x(), movePos.y(), movePos.z(), 1.0f);
    }

    private ParticleOptions getParticle() {
        ItemStack a = ItemRegisterer.TREAT1.get().getDefaultInstance();
        ItemStack b = ItemRegisterer.TREAT2.get().getDefaultInstance();
        ItemStack c = ItemRegisterer.TREAT3.get().getDefaultInstance();
        ItemStack d = ItemRegisterer.TREAT4.get().getDefaultInstance();
        ItemStack e = ItemRegisterer.TREAT5.get().getDefaultInstance();
        ItemStack f = ItemRegisterer.TREAT6.get().getDefaultInstance();

        return switch (this.getTreat()) {
            case 2 -> new ItemParticleOption(ParticleTypes.ITEM, b);
            case 3 -> new ItemParticleOption(ParticleTypes.ITEM, c);
            case 4 -> new ItemParticleOption(ParticleTypes.ITEM, d);
            case 5 -> new ItemParticleOption(ParticleTypes.ITEM, e);
            case 6 -> new ItemParticleOption(ParticleTypes.ITEM, f);
            default -> new ItemParticleOption(ParticleTypes.ITEM, a);
        };
    }

    public void makeTreatDestroyedParticles() {
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
                for (i = 0; i < 15; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    packet.queueParticle(ParticleTypes.EXPLOSION, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                for (i = 0; i < 150; ++i) {
                    d0 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d1 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    d2 = (-0.5 + this.random.nextGaussian()) / 4.0;
                    ParticleOptions $$1 = this.getParticle();
                    packet.queueParticle($$1, false, new Vec3(this.getRandomX(1.0), this.getRandomY(), this.getRandomZ(1.0)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    static {
        TREAT = SynchedEntityData.defineId(TrickOrTreatEntity.class, EntityDataSerializers.INT);
        BOUNCE = SynchedEntityData.defineId(TrickOrTreatEntity.class, EntityDataSerializers.BOOLEAN);
        GOOPY = SynchedEntityData.defineId(TrickOrTreatEntity.class, EntityDataSerializers.BOOLEAN);
        OLD = SynchedEntityData.defineId(TrickOrTreatEntity.class, EntityDataSerializers.BOOLEAN);
    }
}

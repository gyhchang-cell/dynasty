package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.packet.JumpscareSyncPacket;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraftforge.network.PacketDistributor;

public class VillagerSoulEntity extends PathfinderMob {
    private static final EntityDataAccessor<Boolean> CHARGING;
    private int attackTicks;
    double chargeX;
    double chargeY;
    double chargeZ;
    private int oldSwell;
    private int swell;
    private final int maxSwell = 15;

    public VillagerSoulEntity(EntityType<? extends PathfinderMob> p_21683_, Level p_21684_) {
        super(p_21683_, p_21684_);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.3499999940395355).add(Attributes.MAX_HEALTH, 12.0).add(Attributes.ATTACK_DAMAGE, 5.0).add(Attributes.FOLLOW_RANGE, 50.0);
    }

    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(CHARGING, false);
    }

    public void tick() {
        this.noPhysics = true;
        this.setNoGravity(true);
        super.tick();
        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
        this.setInvulnerable(true);
        this.oldSwell = this.swell++;
        if (this.swell >= this.maxSwell) {
            this.swell = this.maxSwell;
        }

        if (this.getTarget() != null) {
            this.getLookControl().setLookAt(this.getTarget(), 100.0F, 100.0F);
        }

        if (this.isCharging()) {
            this.setDeltaMovement(this.chargeX, this.chargeY, this.chargeZ);
        }

        if (this.getTarget() != null) {
            ++this.attackTicks;

            if (attackTicks == 50) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_SCREECH.get(), 3.0F, this.getVoicePitch());
            }

            if (this.attackTicks > 50) {
                LivingEntity entity = this.getTarget();
                double x = this.getX() - entity.getX();
                double y = this.getY() - entity.getY();
                double z = this.getZ() - entity.getZ();
                double d = Math.sqrt(x * x + y * y + z * z);
                float power = 6.5F;
                double motionX = -(x / d * (double) power * 0.2);
                double motionY = -(y / d * (double) power * 0.2);
                double motionZ = -(z / d * (double) power * 0.2);
                this.setCharge(motionX, motionY, motionZ);
                if (!this.level().isClientSide) {
                    this.setCharging(true);
                }
            }

            if (this.distanceToSqr(this.getTarget()) < 4.0) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_JUMPSCARE.get(), 3.0F, this.getVoicePitch());
                CameraShakeEntity.cameraShake(this.level(), this.position(), 50.0F, 0.2F, 0, 40);
                this.getTarget().addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 60, 0));

                if (this.getTarget() instanceof ServerPlayer player) {
                    PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), new JumpscareSyncPacket());
                }

                this.discard();
            }
        }

        if (this.tickCount > 100) {
            this.discard();
        }

    }

    public float getSwelling(float p_32321_) {
        return Mth.lerp(p_32321_, (float) this.oldSwell, (float) this.swell) / (float) (this.maxSwell - 2);
    }

    protected boolean isAffectedByFluids() {
        return false;
    }

    public void setCharge(double x, double y, double z) {
        this.chargeX = x;
        this.chargeY = y;
        this.chargeZ = z;
    }

    public boolean hurt(DamageSource source, float amount) {
        return (source.is(DamageTypes.FELL_OUT_OF_WORLD) || source.is(DamageTypes.GENERIC_KILL)) && super.hurt(source, amount);
    }

    public void die(DamageSource p_21014_) {
        super.die(p_21014_);
        this.deathTime = 19;
    }

    public boolean isCharging() {
        return this.entityData.get(CHARGING);
    }

    public void setCharging(boolean charge) {
        this.entityData.set(CHARGING, charge);
    }

    static {
        CHARGING = SynchedEntityData.defineId(VillagerSoulEntity.class, EntityDataSerializers.BOOLEAN);
    }
}

package com.yellowbrossproductions.illageandspillage.entities.projectile;

import com.yellowbrossproductions.illageandspillage.entities.IllagerAttack;
import com.yellowbrossproductions.illageandspillage.entities.RagnoEntity;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import com.yellowbrossproductions.illageandspillage.util.IllageAndSpillageSoundEvents;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.List;

public class WebNetEntity extends PathfinderMob implements IllagerAttack {
    private static final EntityDataAccessor<Float> ATTACH_POINT_X = SynchedEntityData.defineId(WebNetEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> ATTACH_POINT_Y = SynchedEntityData.defineId(WebNetEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> ATTACH_POINT_Z = SynchedEntityData.defineId(WebNetEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Boolean> CAUGHT = SynchedEntityData.defineId(WebNetEntity.class, EntityDataSerializers.BOOLEAN);
    public double accelerationX;
    public double accelerationY;
    public double accelerationZ;
    public LivingEntity shooter = null;
    private boolean shouldReturn = false;
    private LivingEntity pullingEntity;
    private int pullPower;

    public WebNetEntity(EntityType<? extends PathfinderMob> p_21683_, Level p_21684_) {
        super(p_21683_, p_21684_);
        this.noCulling = true;
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Monster.createMonsterAttributes().add(Attributes.MOVEMENT_SPEED, 0.0).add(Attributes.MAX_HEALTH, 2.0).add(Attributes.ATTACK_DAMAGE, 0.0).add(Attributes.FOLLOW_RANGE, 32.0);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(ATTACH_POINT_X, 0.0F);
        this.entityData.define(ATTACH_POINT_Y, 0.0F);
        this.entityData.define(ATTACH_POINT_Z, 0.0F);
        this.entityData.define(CAUGHT, false);
    }

    public boolean causeFallDamage(float distance, float damageMultiplier, DamageSource bullcrap) {
        if (!this.level().isClientSide) {
            this.discard();
        }

        return false;
    }

    public boolean isAttackable() {
        return false;
    }

    public boolean canBeAffected(MobEffectInstance p_21197_) {
        return false;
    }

    public boolean isCaught() {
        return entityData.get(CAUGHT);
    }

    public void setCaught(boolean caught) {
        this.entityData.set(CAUGHT, caught);
    }

    public void tick() {
        this.setInvulnerable(true);
        this.setNoGravity(true);
        this.noPhysics = true;
        EntityUtil.makeWebParticles(this.level(), this);

        LivingEntity attacker = this.shooter != null ? this.shooter : this;
        List<Entity> list = this.level().getEntities(this, new AABB(this.getX() - 1.0, this.getY() - 1.0, this.getZ() - 1.0, this.getX() + 1.0, this.getY() + 1.0, this.getZ() + 1.0), Entity::isAlive);

        for (Entity entity : list) {
            if (!this.shouldReturn && !this.isCaught() && entity instanceof LivingEntity living) {
                boolean canHurt = attacker instanceof Mob ? EntityUtil.canHurtThisMob(living, (Mob) attacker) : living != this.shooter;
                if (canHurt && entity.isAlive() && !entity.isInvulnerable() && !entity.isSpectator()) {
                    if (!this.level().isClientSide) {
                        this.setCaught(true);
                    }
                    living.hurt(this.damageSources().thrown(living, attacker), 2.0F);
                    this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_WEB_HIT.get(), 1.0F, this.getVoicePitch());
                    this.pullingEntity = living;
                }
            }
        }

        if (!this.level().isClientSide && shooter != null && shooter.isAlive()) {
            float radius2 = -2.0F;
            double x2 = shooter.getX() + 0.800000011920929 * Math.sin((double) (-shooter.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.sin((double) (-shooter.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-shooter.getXRot()) * Math.PI / 180.0);
            double z2 = shooter.getZ() + 0.800000011920929 * Math.cos((double) (-shooter.getYRot()) * Math.PI / 180.0) + (double) radius2 * Math.cos((double) (-shooter.yHeadRot) * Math.PI / 180.0) * Math.cos((double) (-shooter.getXRot()) * Math.PI / 180.0);
            this.setAttachPoint(x2, shooter.getY() + 1, z2);
        }

        if (!this.isCaught()) {
            this.setDeltaMovement(this.accelerationX, this.accelerationY, this.accelerationZ);
        } else if (this.pullingEntity != null && pullingEntity.isAlive()) {
            this.setPos(this.pullingEntity.getBoundingBox().getCenter());
        } else if (!this.level().isClientSide) {
            this.setCaught(false);
        }

        if (this.pullingEntity != null && this.distanceToSqr(this.pullingEntity) <= 4) {
            if (this.tickCount % 10 == 0) {
                this.playSound(IllageAndSpillageSoundEvents.ENTITY_RAGNO_WEB_HIT.get(), 1.0F, this.getVoicePitch());
            }
            this.pullPower += 2;
            double x = this.getAttachPoint().x - this.pullingEntity.getX();
            double y = this.getAttachPoint().y - this.pullingEntity.getY();
            double z = this.getAttachPoint().z - this.pullingEntity.getZ();
            double d = Math.sqrt(x * x + y * y + z * z);
            float power = (float) this.pullPower / 80.0F;
            double motionX = this.pullingEntity.getDeltaMovement().x + x / d * (double) power * 0.2;
            double motionY = this.pullingEntity.getDeltaMovement().y + y / d * (double) power * 0.2;
            double motionZ = this.pullingEntity.getDeltaMovement().z + z / d * (double) power * 0.2;
            this.pullingEntity.hurtMarked = true;
            this.pullingEntity.setDeltaMovement(motionX, motionY, motionZ);
            this.pullingEntity.lerpMotion(motionX, motionY, motionZ);
        }

        if (this.tickCount > 20 || this.pullingEntity != null) {
            this.shouldReturn = true;
            if (this.shooter instanceof RagnoEntity) ((RagnoEntity) this.shooter).setAnimationState(20);
        }

        if (this.shouldReturn && this.shooter != null) {
            double x = this.getX() - this.getAttachPoint().x;
            double y = this.getY() - this.getAttachPoint().y;
            double z = this.getZ() - this.getAttachPoint().z;
            double d = Math.sqrt(x * x + y * y + z * z);
            float power = 10.0F;
            double motionX = -(x / d * (double) power * 0.2);
            double motionY = -(y / d * (double) power * 0.2);
            double motionZ = -(z / d * (double) power * 0.2);
            this.setAcceleration(motionX, motionY, motionZ);
            if (this.distanceToSqr(this.shooter) < 12.25) {
                if (this.pullingEntity != null) {
                    this.pullingEntity.setDeltaMovement(0, 0, 0);

                    if (this.pullingEntity instanceof ServerPlayer serverPlayer) {
                        serverPlayer.connection.send(new ClientboundSetEntityMotionPacket(this.pullingEntity.getId(), new Vec3(0, 0, 0)));
                    }
                }

                if (this.shooter instanceof RagnoEntity ragno) {
                    if (ragno.getAttackTicks() > 15 && ragno.waitingForWeb && this.pullingEntity != null && this.pullingEntity.isAlive()) {
                        ragno.followupTicks = 1;
                    }
                    ragno.waitingForWeb = false;
                }

                if (!this.level().isClientSide) {
                    this.setCaught(false);
                    this.discard();
                }
            }
        }

        if (this.tickCount >= 100 && !this.level().isClientSide) {
            if (this.shooter instanceof RagnoEntity) ((RagnoEntity) this.shooter).waitingForWeb = false;
            this.discard();
        }

        if (this.shooter != null && !this.shooter.isAlive()) {
            this.discard();
        }

        super.tick();
        this.setYRot(this.getYHeadRot());
        this.yBodyRot = this.getYRot();
    }

    public void setAttachPoint(double x, double y, double z) {
        this.entityData.set(ATTACH_POINT_X, (float) x);
        this.entityData.set(ATTACH_POINT_Y, (float) y);
        this.entityData.set(ATTACH_POINT_Z, (float) z);
    }

    public Vec3 getAttachPoint() {
        return new Vec3(this.entityData.get(ATTACH_POINT_X), this.entityData.get(ATTACH_POINT_Y), this.entityData.get(ATTACH_POINT_Z));
    }

    public void setAcceleration(double x, double y, double z) {
        this.accelerationX = x;
        this.accelerationY = y;
        this.accelerationZ = z;
    }

    public void setShooter(LivingEntity shooter) {
        this.shooter = shooter;
    }

    protected SoundEvent getHurtSound(DamageSource damageSourceIn) {
        return null;
    }

    protected SoundEvent getDeathSound() {
        return null;
    }

    public boolean shouldRenderAtSqrDistance(double distance) {
        return distance < 1024.0;
    }

    public boolean hurt(DamageSource source, float amount) {
        return (source.is(DamageTypes.FELL_OUT_OF_WORLD) || source.is(DamageTypes.GENERIC_KILL)) && super.hurt(source, amount);
    }

    public boolean canCollideWith(Entity entity) {
        return false;
    }

    public boolean canBeCollidedWith() {
        return false;
    }

    public boolean isPickable() {
        return false;
    }

    protected void doPush(Entity entityIn) {
    }

    public void push(Entity entityIn) {
    }
}

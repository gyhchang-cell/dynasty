package com.yellowbrossproductions.illageandspillage.entities.projectile;

import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.ClipContext.Block;
import net.minecraft.world.level.ClipContext.Fluid;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.HitResult.Type;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.network.NetworkHooks;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class SoulBeamEntity extends Entity {
    public LivingEntity caster;
    public double endPosX;
    public double endPosY;
    public double endPosZ;
    public double collidePosX;
    public double collidePosY;
    public double collidePosZ;
    public double prevCollidePosX;
    public double prevCollidePosY;
    public double prevCollidePosZ;
    public float renderYaw;
    public float renderPitch;
    public boolean on;
    public Direction blockSide;
    private int power;
    private static final EntityDataAccessor<Float> YAW;
    private static final EntityDataAccessor<Float> PITCH;
    private static final EntityDataAccessor<Integer> DURATION;
    private static final EntityDataAccessor<Integer> CASTER;
    public float prevYaw;
    public float prevPitch;
    @OnlyIn(Dist.CLIENT)
    private Vec3[] attractorPos;

    public SoulBeamEntity(EntityType<? extends SoulBeamEntity> p_19870_, Level p_19871_) {
        super(p_19870_, p_19871_);
        this.on = true;
        this.blockSide = null;
        this.noCulling = true;
        if (p_19871_.isClientSide) {
            this.attractorPos = new Vec3[]{new Vec3(0.0, 0.0, 0.0)};
        }

    }

    public SoulBeamEntity(EntityType<? extends SoulBeamEntity> type, Level world, LivingEntity caster, double x, double y, double z, float yaw, float pitch, int duration, int pow) {
        this(type, world);
        this.caster = caster;
        this.setYaw(yaw);
        this.setPitch(pitch);
        this.setDuration(duration);
        this.setPos(x, y, z);
        this.calculateEndPos();
        this.setPower(pow);
        if (!world.isClientSide) {
            this.setCasterID(caster.getId());
        }

    }

    protected void defineSynchedData() {
        this.entityData.define(YAW, 0.0F);
        this.entityData.define(PITCH, 0.0F);
        this.entityData.define(DURATION, 0);
        this.entityData.define(CASTER, -1);
    }

    protected void readAdditionalSaveData(CompoundTag p_20052_) {
    }

    protected void addAdditionalSaveData(CompoundTag p_20139_) {
    }

    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }

    public PushReaction getPistonPushReaction() {
        return PushReaction.IGNORE;
    }

    public float getYaw() {
        return this.getEntityData().get(YAW);
    }

    public void setYaw(float yaw) {
        this.getEntityData().set(YAW, yaw);
    }

    public float getPitch() {
        return this.getEntityData().get(PITCH);
    }

    public void setPitch(float pitch) {
        this.getEntityData().set(PITCH, pitch);
    }

    public int getDuration() {
        return this.getEntityData().get(DURATION);
    }

    public void setDuration(int duration) {
        this.getEntityData().set(DURATION, duration);
    }

    public int getCasterID() {
        return this.getEntityData().get(CASTER);
    }

    public void setCasterID(int id) {
        this.getEntityData().set(CASTER, id);
    }

    public void setPower(int power) {
        this.power = power;
    }

    private void calculateEndPos() {
        double radius = 30.0;
        if (this.level().isClientSide()) {
            this.endPosX = this.getX() + radius * Math.cos(this.renderYaw) * Math.cos(this.renderPitch);
            this.endPosZ = this.getZ() + radius * Math.sin(this.renderYaw) * Math.cos(this.renderPitch);
            this.endPosY = this.getY() + radius * Math.sin(this.renderPitch);
        } else {
            this.endPosX = this.getX() + radius * Math.cos(this.getYaw()) * Math.cos(this.getPitch());
            this.endPosZ = this.getZ() + radius * Math.sin(this.getYaw()) * Math.cos(this.getPitch());
            this.endPosY = this.getY() + radius * Math.sin(this.getPitch());
        }

    }

    public SolarbeamHitResult raytraceEntities(Level world, Vec3 from, Vec3 to, boolean stopOnLiquid, boolean ignoreBlockWithoutBoundingBox, boolean returnLastUncollidableBlock) {
        SolarbeamHitResult result = new SolarbeamHitResult();
        result.setBlockHit(world.clip(new ClipContext(from, to, Block.COLLIDER, Fluid.NONE, this)));
        if (result.blockHit != null) {
            Vec3 hitVec = result.blockHit.getLocation();
            this.collidePosX = hitVec.x;
            this.collidePosY = hitVec.y;
            this.collidePosZ = hitVec.z;
            this.blockSide = result.blockHit.getDirection();
        } else {
            this.collidePosX = this.endPosX;
            this.collidePosY = this.endPosY;
            this.collidePosZ = this.endPosZ;
            this.blockSide = null;
        }

        List<LivingEntity> entities = world.getEntitiesOfClass(LivingEntity.class, (new AABB(Math.min(this.getX(), this.collidePosX), Math.min(this.getY(), this.collidePosY), Math.min(this.getZ(), this.collidePosZ), Math.max(this.getX(), this.collidePosX), Math.max(this.getY(), this.collidePosY), Math.max(this.getZ(), this.collidePosZ))).inflate(1.0, 1.0, 1.0));

        for (LivingEntity entity : entities) {
            if (entity != this.caster) {
                float pad = entity.getPickRadius() + 0.5F;
                AABB aabb = entity.getBoundingBox().inflate(pad, pad, pad);
                Optional<Vec3> hit = aabb.clip(from, to);
                if (aabb.contains(from)) {
                    result.addEntityHit(entity);
                } else if (hit.isPresent()) {
                    result.addEntityHit(entity);
                }
            }
        }

        return result;
    }

    public void push(Entity entityIn) {
    }

    public boolean isPickable() {
        return false;
    }

    public boolean isPushable() {
        return false;
    }

    public boolean shouldRenderAtSqrDistance(double distance) {
        return distance < 1024.0;
    }

    public void tick() {
        super.tick();
        this.prevCollidePosX = this.collidePosX;
        this.prevCollidePosY = this.collidePosY;
        this.prevCollidePosZ = this.collidePosZ;
        this.prevYaw = this.renderYaw;
        this.prevPitch = this.renderPitch;
        this.xo = this.getX();
        this.yo = this.getY();
        this.zo = this.getZ();
        if (this.tickCount == 1 && this.level().isClientSide) {
            this.caster = (LivingEntity) this.level().getEntity(this.getCasterID());
        }

        if (this.caster != null) {
            this.renderYaw = (float) (((double) this.caster.yHeadRot + 90.0) * Math.PI / 180.0);
            this.renderPitch = (float) ((double) (-this.caster.getXRot()) * Math.PI / 180.0);
        }

        if (!this.on) {
            this.discard();
        }

        if (this.caster != null && !this.caster.isAlive()) {
            this.discard();
        }

        if (this.level().isClientSide && this.tickCount <= 10 && this.caster != null) {
            int particleCount = 8;

            while (true) {
                --particleCount;
                if (particleCount == 0) {
                    break;
                }

                double radius = (2.0F * this.caster.getBbWidth());
                double yaw = (double) (this.random.nextFloat() * 2.0F) * Math.PI;
                double pitch = (double) (this.random.nextFloat() * 2.0F) * Math.PI;
                double ox = radius * Math.sin(yaw) * Math.sin(pitch);
                double var10000 = radius * Math.cos(pitch);
                double oz = radius * Math.cos(yaw) * Math.sin(pitch);
                double rootX = this.caster.getX();
                double rootY = this.caster.getY() + (double) (this.caster.getBbHeight() / 2.0F) + 0.30000001192092896;
                double rootZ = this.caster.getZ();
                this.attractorPos[0] = new Vec3(rootX, rootY, rootZ);
            }
        }

        this.calculateEndPos();
        List<LivingEntity> hit = this.raytraceEntities(this.level(), new Vec3(this.getX(), this.getY(), this.getZ()), new Vec3(this.endPosX, this.endPosY, this.endPosZ), false, true, true).entities;
        if (!this.level().isClientSide) {

            for (LivingEntity target : hit) {
                target.hurt(damageSources().indirectMagic(this, this.caster), 4.0F + (float) this.power);
                target.hurtMarked = true;
                target.setDeltaMovement(0.0, 0.0, 0.0);
                target.lerpMotion(0.0, 0.0, 0.0);
            }
        }

        if (this.tickCount > this.getDuration()) {
            this.on = false;
        }

    }

    static {
        YAW = SynchedEntityData.defineId(SoulBeamEntity.class, EntityDataSerializers.FLOAT);
        PITCH = SynchedEntityData.defineId(SoulBeamEntity.class, EntityDataSerializers.FLOAT);
        DURATION = SynchedEntityData.defineId(SoulBeamEntity.class, EntityDataSerializers.INT);
        CASTER = SynchedEntityData.defineId(SoulBeamEntity.class, EntityDataSerializers.INT);
    }

    public static class SolarbeamHitResult {
        private BlockHitResult blockHit;
        private final List<LivingEntity> entities = new ArrayList<>();

        public SolarbeamHitResult() {
        }

        public BlockHitResult getBlockHit() {
            return this.blockHit;
        }

        public void setBlockHit(HitResult rayTraceResult) {
            if (rayTraceResult.getType() == Type.BLOCK) {
                this.blockHit = (BlockHitResult) rayTraceResult;
            }

        }

        public void addEntityHit(LivingEntity entity) {
            this.entities.add(entity);
        }
    }
}

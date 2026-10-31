package com.yellowbrossproductions.illageandspillage.entities;

import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.network.NetworkHooks;

public class CameraShakeEntity extends Entity {
    private static final EntityDataAccessor<Float> RADIUS;
    private static final EntityDataAccessor<Float> MAGNITUDE;
    private static final EntityDataAccessor<Integer> DURATION;
    private static final EntityDataAccessor<Integer> FADE_DURATION;

    public CameraShakeEntity(EntityType<?> p_19870_, Level p_19871_) {
        super(p_19870_, p_19871_);
    }

    public CameraShakeEntity(Level world, Vec3 position, float radius, float magnitude, int duration, int fadeDuration) {
        super(ModEntityTypes.CameraShake.get(), world);
        this.setRadius(radius);
        this.setMagnitude(magnitude);
        this.setDuration(duration);
        this.setFadeDuration(fadeDuration);
        this.setPos(position.x(), position.y(), position.z());
    }

    @OnlyIn(Dist.CLIENT)
    public float getShakeAmount(Player player, float delta) {
        float ticksDelta = (float)this.tickCount + delta;
        float timeFrac = 1.0F - (ticksDelta - (float)this.getDuration()) / ((float)this.getFadeDuration() + 1.0F);
        float baseAmount = ticksDelta < (float)this.getDuration() ? this.getMagnitude() : timeFrac * timeFrac * this.getMagnitude();
        Vec3 playerPos = player.getEyePosition(delta);
        float distFrac = (float)(1.0 - Mth.clamp(this.position().distanceTo(playerPos) / (double)this.getRadius(), 0.0, 1.0));
        return baseAmount * distFrac * distFrac;
    }

    public void tick() {
        super.tick();
        if (this.tickCount > this.getDuration() + this.getFadeDuration()) {
            this.discard();
        }

    }

    protected void defineSynchedData() {
        this.getEntityData().define(RADIUS, 10.0F);
        this.getEntityData().define(MAGNITUDE, 1.0F);
        this.getEntityData().define(DURATION, 0);
        this.getEntityData().define(FADE_DURATION, 5);
    }

    public float getRadius() {
        return this.getEntityData().get(RADIUS);
    }

    public void setRadius(float radius) {
        this.getEntityData().set(RADIUS, radius);
    }

    public float getMagnitude() {
        return this.getEntityData().get(MAGNITUDE);
    }

    public void setMagnitude(float magnitude) {
        this.getEntityData().set(MAGNITUDE, magnitude);
    }

    public int getDuration() {
        return this.getEntityData().get(DURATION);
    }

    public void setDuration(int duration) {
        this.getEntityData().set(DURATION, duration);
    }

    public int getFadeDuration() {
        return this.getEntityData().get(FADE_DURATION);
    }

    public void setFadeDuration(int fadeDuration) {
        this.getEntityData().set(FADE_DURATION, fadeDuration);
    }

    protected void readAdditionalSaveData(CompoundTag compound) {
        this.setRadius(compound.getFloat("radius"));
        this.setMagnitude(compound.getFloat("magnitude"));
        this.setDuration(compound.getInt("duration"));
        this.setFadeDuration(compound.getInt("fade_duration"));
        this.tickCount = compound.getInt("ticks_existed");
    }

    protected void addAdditionalSaveData(CompoundTag compound) {
        compound.putFloat("radius", this.getRadius());
        compound.putFloat("magnitude", this.getMagnitude());
        compound.putInt("duration", this.getDuration());
        compound.putInt("fade_duration", this.getFadeDuration());
        compound.putInt("ticks_existed", this.tickCount);
    }

    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }

    public static void cameraShake(Level world, Vec3 position, float radius, float magnitude, int duration, int fadeDuration) {
        if (!world.isClientSide) {
            CameraShakeEntity cameraShake = new CameraShakeEntity(world, position, radius, magnitude, duration, fadeDuration);
            world.addFreshEntity(cameraShake);
        }

    }

    static {
        RADIUS = SynchedEntityData.defineId(CameraShakeEntity.class, EntityDataSerializers.FLOAT);
        MAGNITUDE = SynchedEntityData.defineId(CameraShakeEntity.class, EntityDataSerializers.FLOAT);
        DURATION = SynchedEntityData.defineId(CameraShakeEntity.class, EntityDataSerializers.INT);
        FADE_DURATION = SynchedEntityData.defineId(CameraShakeEntity.class, EntityDataSerializers.INT);
    }
}

package com.sammy.malum.client;

import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import com.sammy.malum.registry.common.magic.*;
import it.unimi.dsi.fastutil.floats.*;
import it.unimi.dsi.fastutil.ints.*;
import net.minecraft.client.particle.*;
import net.minecraft.core.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.phys.*;
import net.minecraft.world.phys.shapes.*;
import org.joml.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.type.*;
import team.lodestar.lodestone.systems.rendering.LodestoneRenderLayer;

import javax.annotation.*;
import java.util.function.*;

public class SpiritBasedParticleBuilder extends WorldParticleBuilder {

    public static SpiritBasedParticleBuilder createSpirit(Holder<? extends LodestoneWorldParticleType> particle) {
        return createSpirit(particle.value());
    }

    public static SpiritBasedParticleBuilder createSpirit(Supplier<? extends LodestoneWorldParticleType> particle) {
        return createSpirit(particle.get());
    }

    public static SpiritBasedParticleBuilder createSpirit(LodestoneWorldParticleType particle) {
        return createSpirit(new WorldParticleOptions(particle));
    }

    public static SpiritBasedParticleBuilder createSpirit(WorldParticleOptions options) {
        return new SpiritBasedParticleBuilder(options);
    }

    @Nullable
    public SpiritArcanaType spiritType;

    protected SpiritBasedParticleBuilder(WorldParticleOptions options) {
        super(options);
    }

    public SpiritBasedParticleBuilder setSpirit(SpiritLike spirit) {
        this.spiritType = spirit.getSpirit();
        if (isUmbral()) {
            super.setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT);
        }
        return setColorData(spiritType.createColorData().build());
    }

    public boolean isUmbral() {
        return spiritType != null && spiritType.matches(MalumSpiritTypes.UMBRAL_SPIRIT);
    }

    @Override
    public SpiritBasedParticleBuilder setRenderType(ParticleRenderType renderType) {
        if (isUmbral()) {
            return (SpiritBasedParticleBuilder) super.setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT);
        }
        return (SpiritBasedParticleBuilder)super.setRenderType(renderType);
    }

    @Override
    public SpiritBasedParticleBuilder setLifetime(Supplier<Integer> lifetimeSupplier) {
        return (SpiritBasedParticleBuilder)super.setLifetime(lifetimeSupplier);
    }

    @Override
    public SpiritBasedParticleBuilder setScaleData(GenericParticleDataWrapper scaleData) {
        if (isUmbral()) {
            scaleData.unwrap().multiplyCoefficient(1.5f);
        }
        return (SpiritBasedParticleBuilder)super.setScaleData(scaleData);
    }

    @Override
    public SpiritBasedParticleBuilder setTransparencyData(GenericParticleDataWrapper transparencyData) {
        if (isUmbral()) {
            transparencyData.unwrap().multiplyValue(4f).multiplyCoefficient(1.5f);
        }
        return (SpiritBasedParticleBuilder)super.setTransparencyData(transparencyData);
    }

    @Override
    public <T extends LodestoneParticleBehavior> SpiritBasedParticleBuilder setBehavior(Class<T> targetClass, Function<T, LodestoneParticleBehavior> tLodestoneParticleBehaviorFunction) {
        return (SpiritBasedParticleBuilder) super.setBehavior(targetClass, tLodestoneParticleBehaviorFunction);
    }

    @Override
    public SpiritBasedParticleBuilder setBehavior(LodestoneParticleBehavior behavior) {
        return (SpiritBasedParticleBuilder) super.setBehavior(behavior);
    }

    @Override
    public SpiritBasedParticleBuilder enableNoClip() {
        return (SpiritBasedParticleBuilder) super.enableNoClip();
    }

    @Override
    public SpiritBasedParticleBuilder disableNoClip() {
        return (SpiritBasedParticleBuilder) super.disableNoClip();
    }

    @Override
    public SpiritBasedParticleBuilder setNoClip(boolean noClip) {
        return (SpiritBasedParticleBuilder) super.setNoClip(noClip);
    }

    @Override
    public SpiritBasedParticleBuilder setRenderTarget(LodestoneRenderLayer renderLayer) {
        return (SpiritBasedParticleBuilder) super.setRenderTarget(renderLayer);
    }

    @Override
    public SpiritBasedParticleBuilder enableForcedSpawn() {
        return (SpiritBasedParticleBuilder) super.enableForcedSpawn();
    }

    @Override
    public SpiritBasedParticleBuilder disableForcedSpawn() {
        return (SpiritBasedParticleBuilder) super.disableForcedSpawn();
    }

    @Override
    public SpiritBasedParticleBuilder setForceSpawn(boolean forceSpawn) {
        return (SpiritBasedParticleBuilder) super.setForceSpawn(forceSpawn);
    }

    @Override
    public SpiritBasedParticleBuilder setRandomMotion(double maxSpeed) {
        return (SpiritBasedParticleBuilder) super.setRandomMotion(maxSpeed);
    }

    @Override
    public SpiritBasedParticleBuilder setRandomMotion(double maxHSpeed, double maxVSpeed) {
        return (SpiritBasedParticleBuilder) super.setRandomMotion(maxHSpeed, maxVSpeed);
    }

    @Override
    public SpiritBasedParticleBuilder setRandomMotion(double maxXSpeed, double maxYSpeed, double maxZSpeed) {
        return (SpiritBasedParticleBuilder) super.setRandomMotion(maxXSpeed, maxYSpeed, maxZSpeed);
    }

    @Override
    public SpiritBasedParticleBuilder addMotion(Vector3f motion) {
        return (SpiritBasedParticleBuilder) super.addMotion(motion);
    }

    @Override
    public SpiritBasedParticleBuilder addMotion(Vec3 motion) {
        return (SpiritBasedParticleBuilder) super.addMotion(motion);
    }

    @Override
    public SpiritBasedParticleBuilder addMotion(double vx, double vy, double vz) {
        return (SpiritBasedParticleBuilder) super.addMotion(vx, vy, vz);
    }

    @Override
    public SpiritBasedParticleBuilder setMotion(Vector3f motion) {
        return (SpiritBasedParticleBuilder) super.setMotion(motion);
    }

    @Override
    public SpiritBasedParticleBuilder setMotion(Vec3 motion) {
        return (SpiritBasedParticleBuilder) super.setMotion(motion);
    }

    @Override
    public SpiritBasedParticleBuilder setMotion(double vx, double vy, double vz) {
        return (SpiritBasedParticleBuilder) super.setMotion(vx, vy, vz);
    }

    @Override
    public SpiritBasedParticleBuilder setRandomOffset(double maxDistance) {
        return (SpiritBasedParticleBuilder) super.setRandomOffset(maxDistance);
    }

    @Override
    public SpiritBasedParticleBuilder setRandomOffset(double maxHDist, double maxVDist) {
        return (SpiritBasedParticleBuilder) super.setRandomOffset(maxHDist, maxVDist);
    }

    @Override
    public SpiritBasedParticleBuilder setRandomOffset(double maxXDist, double maxYDist, double maxZDist) {
        return (SpiritBasedParticleBuilder) super.setRandomOffset(maxXDist, maxYDist, maxZDist);
    }

    @Override
    public SpiritBasedParticleBuilder act(Consumer<WorldParticleBuilder> particleBuilderConsumer) {
        return (SpiritBasedParticleBuilder) super.act(particleBuilderConsumer);
    }

    @Override
    public SpiritBasedParticleBuilder addTickActor(Consumer<LodestoneWorldParticle> particleActor) {
        return (SpiritBasedParticleBuilder) super.addTickActor(particleActor);
    }

    @Override
    public SpiritBasedParticleBuilder addSpawnActor(Consumer<LodestoneWorldParticle> particleActor) {
        return (SpiritBasedParticleBuilder) super.addSpawnActor(particleActor);
    }

    @Override
    public SpiritBasedParticleBuilder addRenderActor(Consumer<LodestoneWorldParticle> particleActor) {
        return (SpiritBasedParticleBuilder) super.addRenderActor(particleActor);
    }

    @Override
    public SpiritBasedParticleBuilder clearActors() {
        return (SpiritBasedParticleBuilder) super.clearActors();
    }

    @Override
    public SpiritBasedParticleBuilder clearTickActors() {
        return (SpiritBasedParticleBuilder) super.clearTickActors();
    }

    @Override
    public SpiritBasedParticleBuilder clearSpawnActors() {
        return (SpiritBasedParticleBuilder) super.clearSpawnActors();
    }

    @Override
    public SpiritBasedParticleBuilder clearRenderActors() {
        return (SpiritBasedParticleBuilder) super.clearRenderActors();
    }

    @Override
    public SpiritBasedParticleBuilder setNaturalLighting() {
        return (SpiritBasedParticleBuilder) super.setNaturalLighting();
    }

    @Override
    public SpiritBasedParticleBuilder setFullBrightLighting() {
        return (SpiritBasedParticleBuilder) super.setFullBrightLighting();
    }

    @Override
    public SpiritBasedParticleBuilder setLightLevel(int particleLight) {
        return (SpiritBasedParticleBuilder) super.setLightLevel(particleLight);
    }

    @Override
    public SpiritBasedParticleBuilder spawn(Level level, double x, double y, double z) {
        return (SpiritBasedParticleBuilder) super.spawn(level, x, y, z);
    }

    @Override
    public SpiritBasedParticleBuilder repeat(Level level, double x, double y, double z, int n) {
        return (SpiritBasedParticleBuilder) super.repeat(level, x, y, z, n);
    }

    @Override
    public SpiritBasedParticleBuilder surroundBlock(Level level, BlockPos pos, Direction... directions) {
        return (SpiritBasedParticleBuilder) super.surroundBlock(level, pos, directions);
    }

    @Override
    public SpiritBasedParticleBuilder repeatSurroundBlock(Level level, BlockPos pos, int n) {
        return (SpiritBasedParticleBuilder) super.repeatSurroundBlock(level, pos, n);
    }

    @Override
    public SpiritBasedParticleBuilder repeatSurroundBlock(Level level, BlockPos pos, int n, Direction... directions) {
        return (SpiritBasedParticleBuilder) super.repeatSurroundBlock(level, pos, n, directions);
    }

    @Override
    public SpiritBasedParticleBuilder surroundVoxelShape(Level level, BlockPos pos, VoxelShape voxelShape, int max) {
        return (SpiritBasedParticleBuilder) super.surroundVoxelShape(level, pos, voxelShape, max);
    }

    @Override
    public SpiritBasedParticleBuilder surroundVoxelShape(Level level, BlockPos pos, BlockState state, int max) {
        return (SpiritBasedParticleBuilder) super.surroundVoxelShape(level, pos, state, max);
    }

    @Override
    public SpiritBasedParticleBuilder spawnAtRandomFace(Level level, BlockPos pos) {
        return (SpiritBasedParticleBuilder) super.spawnAtRandomFace(level, pos);
    }

    @Override
    public SpiritBasedParticleBuilder repeatRandomFace(Level level, BlockPos pos, int n) {
        return (SpiritBasedParticleBuilder) super.repeatRandomFace(level, pos, n);
    }

    @Override
    public SpiritBasedParticleBuilder createBlockOutline(Level level, BlockPos pos, BlockState state) {
        return (SpiritBasedParticleBuilder) super.createBlockOutline(level, pos, state);
    }

    @Override
    public SpiritBasedParticleBuilder spawnLine(Level level, Vec3 one, Vec3 two) {
        return (SpiritBasedParticleBuilder) super.spawnLine(level, one, two);
    }

    @Override
    public SpiritBasedParticleBuilder modifyColorData(Consumer<ColorParticleData> dataConsumer) {
        return (SpiritBasedParticleBuilder) super.modifyColorData(dataConsumer);
    }

    @Override
    public SpiritBasedParticleBuilder setColorData(ColorParticleDataWrapper colorData) {
        return (SpiritBasedParticleBuilder) super.setColorData(colorData);
    }

    @Override
    public SpiritBasedParticleBuilder modifyScaleData(Consumer<GenericParticleData> dataConsumer) {
        return (SpiritBasedParticleBuilder) super.modifyScaleData(dataConsumer);
    }

    @Override
    public SpiritBasedParticleBuilder modifyLengthData(Consumer<GenericParticleData> dataConsumer) {
        return (SpiritBasedParticleBuilder) super.modifyLengthData(dataConsumer);
    }

    @Override
    public SpiritBasedParticleBuilder setLengthData(GenericParticleDataWrapper lengthData) {
        return (SpiritBasedParticleBuilder) super.setLengthData(lengthData);
    }

    @Override
    public SpiritBasedParticleBuilder setLifeDelay(int lifeDelay) {
        return (SpiritBasedParticleBuilder) super.setLifeDelay(lifeDelay);
    }

    @Override
    public SpiritBasedParticleBuilder setLifeDelay(Supplier<Integer> supplier) {
        return (SpiritBasedParticleBuilder) super.setLifeDelay(supplier);
    }

    @Override
    public SpiritBasedParticleBuilder setLifetime(int lifetime) {
        return (SpiritBasedParticleBuilder) super.setLifetime(lifetime);
    }

    @Override
    public SpiritBasedParticleBuilder setGravity(float gravity) {
        return (SpiritBasedParticleBuilder) super.setGravity(gravity);
    }

    @Override
    public SpiritBasedParticleBuilder setGravity(Supplier<Float> supplier) {
        return (SpiritBasedParticleBuilder) super.setGravity(supplier);
    }

    @Override
    public SpiritBasedParticleBuilder setFriction(float friction) {
        return (SpiritBasedParticleBuilder) super.setFriction(friction);
    }

    @Override
    public SpiritBasedParticleBuilder setFriction(Supplier<Float> supplier) {
        return (SpiritBasedParticleBuilder) super.setFriction(supplier);
    }

    @Override
    public SpiritBasedParticleBuilder multiplyLifeDelay(float multiplier) {
        return (SpiritBasedParticleBuilder) super.multiplyLifeDelay(multiplier);
    }

    @Override
    public SpiritBasedParticleBuilder modifyLifeDelay(Int2IntFunction modifier) {
        return (SpiritBasedParticleBuilder) super.modifyLifeDelay(modifier);
    }

    @Override
    public SpiritBasedParticleBuilder multiplyLifetime(float multiplier) {
        return (SpiritBasedParticleBuilder) super.multiplyLifetime(multiplier);
    }

    @Override
    public SpiritBasedParticleBuilder modifyLifetime(Int2IntFunction modifier) {
        return (SpiritBasedParticleBuilder) super.modifyLifetime(modifier);
    }

    @Override
    public SpiritBasedParticleBuilder multiplyGravity(float multiplier) {
        return (SpiritBasedParticleBuilder) super.multiplyGravity(multiplier);
    }

    @Override
    public SpiritBasedParticleBuilder modifyGravity(Float2FloatFunction modifier) {
        return (SpiritBasedParticleBuilder) super.modifyGravity(modifier);
    }

    @Override
    public SpiritBasedParticleBuilder multiplyFriction(float multiplier) {
        return (SpiritBasedParticleBuilder) super.multiplyFriction(multiplier);
    }

    @Override
    public SpiritBasedParticleBuilder modifyFriction(Float2FloatFunction modifier) {
        return (SpiritBasedParticleBuilder) super.modifyFriction(modifier);
    }

    @Override
    public SpiritBasedParticleBuilder setSpinData(SpinParticleDataWrapper spinData) {
        return (SpiritBasedParticleBuilder) super.setSpinData(spinData);
    }

    @Override
    public SpiritBasedParticleBuilder modifySpinData(Consumer<SpinParticleData> dataConsumer) {
        return (SpiritBasedParticleBuilder) super.modifySpinData(dataConsumer);
    }

    @Override
    public SpiritBasedParticleBuilder modifyTransparencyData(Consumer<GenericParticleData> dataConsumer) {
        return (SpiritBasedParticleBuilder) super.modifyTransparencyData(dataConsumer);
    }

    @Override
    public SpiritBasedParticleBuilder setSpritePicker(SimpleParticleOptions.ParticleSpritePicker spritePicker) {
        return (SpiritBasedParticleBuilder) super.setSpritePicker(spritePicker);
    }
}
package com.sammy.malum.visual_effects;

import com.sammy.malum.common.block.curiosities.weeping_well.*;
import com.sammy.malum.registry.common.*;
import net.minecraft.core.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.phys.*;
import net.minecraft.world.phys.shapes.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.rendering.LodestoneRenderingSystem;
import team.lodestar.lodestone.registry.common.particle.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;

import java.awt.*;
import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.*;

public class WeepingWellParticleEffects {

    private static final VoxelShape WELL_SHAPE = Block.box(-64.0D, 4f, -64.0D, 80.0D, 5f, 80.0D);

    public static Color getWeepingWellSmokeColor(RandomSource rand) {
        float colorMultiplier = Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.6f, 1.2f);
        return new Color((int) (4 * colorMultiplier), (int) (3 * colorMultiplier), (int) (6 * colorMultiplier));
    }

    public static void spitOutItemParticles(Level level, NetworkedParticleEffectPositionData positionEffectData) {
        double posX = positionEffectData.getPosX();
        double posY = positionEffectData.getPosY();
        double posZ = positionEffectData.getPosZ();
        Vec3 pos = new Vec3(posX, posY, posZ);
        RandomSource rand = level.random;
        Color color = getWeepingWellSmokeColor(rand);
        ColorParticleData colorData = ColorParticleData.create(color, color.darker()).setCoefficient(0.5f).build();
        Consumer<LodestoneWorldParticle> spawnBehavior = p -> p.tick(2);
        for (int i = 0; i < 64; i++) {
            float xVelocity = Easing.SINE_IN_OUT.asWeighedRandom(rand, 0f, 0.15f) * (rand.nextBoolean() ? 1 : -1);
            float yVelocity = Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.5f, 1f);
            float zVelocity = Easing.SINE_IN_OUT.asWeighedRandom(rand, 0f, 0.15f) * (rand.nextBoolean() ? 1 : -1);
            float gravityStrength = Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.75f, 1f);
            if (rand.nextFloat() < 0.85f) {
                var sparkParticles = weepingWellSparks(level, pos, colorData, LodestoneWorldParticleRenderType.LUMITRANSPARENT);
                sparkParticles.getBuilder()
                        .addSpawnActor(spawnBehavior)
                        .disableNoClip()
                        .setGravity(gravityStrength / 2f)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .setRenderTarget(LodestoneRenderingSystem.LATE_DEFERRED_RENDER)
                        .modifyTransparencyData(d -> d.multiplyValue(2f))
                        .modifyScaleData(d -> d.multiplyValue(1.5f));
                sparkParticles.getBloomBuilder()
                        .addSpawnActor(spawnBehavior)
                        .disableNoClip()
                        .setGravity(gravityStrength / 2f)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .setRenderTarget(LodestoneRenderingSystem.LATE_DEFERRED_RENDER)
                        .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                sparkParticles.spawnParticles();
            }
            if (rand.nextFloat() < 0.85f) {
                xVelocity *= 1.25f;
                yVelocity *= 0.75f;
                zVelocity *= 1.25f;
                var lightSpecs = weepingWellSpecs(level, pos, colorData, LodestoneWorldParticleRenderType.LUMITRANSPARENT);
                lightSpecs.getBuilder()
                        .addSpawnActor(spawnBehavior)
                        .disableNoClip()
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .setRenderTarget(LodestoneRenderingSystem.LATE_DEFERRED_RENDER)
                        .modifyScaleData(d -> d.multiplyValue(2.5f));
                lightSpecs.getBloomBuilder()
                        .addSpawnActor(spawnBehavior)
                        .disableNoClip()
                        .setGravity(gravityStrength)
                        .setMotion(xVelocity, yVelocity, zVelocity)
                        .setRenderTarget(LodestoneRenderingSystem.LATE_DEFERRED_RENDER)
                        .modifyTransparencyData(d -> d.multiplyValue(1.25f));
                lightSpecs.spawnParticles();
            }
        }
        int spinOffset = rand.nextInt(360);
        for (int i = 0; i < 4; i++) {
            int spinDirection = (rand.nextBoolean() ? 1 : -1);
            float scaleMultiplier = (float) (1 + Math.pow(rand.nextFloat(), 2));
            WorldParticleBuilder.create(LodestoneParticleTypes.SPARKLE_PARTICLE)
                    .setTransparencyData(GenericParticleData.create(0.7f, 0.5f, 0).setEasing(Easing.SINE_IN, Easing.CIRC_IN).build())
                    .setSpinData(SpinParticleData.create((0.125f + rand.nextFloat() * 0.075f) * spinDirection).setSpinOffset(spinOffset).build())
                    .setScaleData(GenericParticleData.create(2.4f * scaleMultiplier, 0.8f, 0).setEasing(Easing.QUAD_IN, Easing.SINE_IN).build())
                    .setColorData(colorData)
                    .setLifetime(25)
                    .setRandomOffset(0.6f)
                    .enableNoClip()
                    .setRandomMotion(0.02f, 0.02f)
                    .setRenderTarget(LodestoneRenderingSystem.LATE_DEFERRED_RENDER)
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                    .repeat(level, posX, posY + 0.25f, posZ, 5);
        }
        for (int i = 0; i < 8; i++) {
            int finalI = 4 + i / 2;
            var squares = weepingWellSquare(level, pos, colorData);
            squares.getBuilder().multiplyLifetime(0.5f).addSpawnActor(p -> p.tick(finalI));
            squares.spawnParticles();
        }
    }

    public static void passiveWeepingWellParticles(VoidConduitBlockEntity voidConduit) {
        Level level = voidConduit.getLevel();
        if (level.getGameTime() % 6L == 0) {
            var blockPos = voidConduit.getBlockPos();
            var rand = level.random;
            float yMotion = 0.004f;

            for (int i = 0; i < 4; i++) {
                var direction = Direction.from2DDataValue(i);
                var offset = new Vec3(direction.getStepX()*4.48f, 0f, direction.getStepZ()*4.48f);
                var offsetPosition = new Vec3(blockPos.getX() + 0.5f, blockPos.getY() + 0.5f, blockPos.getZ() + 0.5f).add(offset);
                WorldParticleBuilder.create(LodestoneParticleTypes.WISP_PARTICLE)
                        .setBehavior(DirectionalParticleBehavior.directional(offset))
                        .setTransparencyData(GenericParticleData.create(0.1f, 0.3f, 0f).setEasing(Easing.SINE_IN, Easing.SINE_OUT).build())
                        .setScaleData(GenericParticleData.create(0f, 16f, 0.3f).setEasing(Easing.SINE_IN, Easing.SINE_OUT).build())
                        .setLengthData(GenericParticleData.create(0f, 3f, 0.3f).setEasing(Easing.SINE_IN, Easing.SINE_OUT).build())
                        .setColorData(ColorParticleData.create(0f, 0f, 0f).build())
                        .setLifetime(80)
                        .addMotion(0, yMotion, 0)
                        .enableNoClip()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .setRenderTarget(LodestoneRenderingSystem.LATE_DEFERRED_RENDER)
                        .spawn(level, offsetPosition.x, offsetPosition.y, offsetPosition.z);
            }
        }
    }

    public static ParticleEffectSpawner weepingWellSparks(Level level, Vec3 pos) {
        RandomSource rand = level.random;
        Color color = getWeepingWellSmokeColor(rand);
        ColorParticleData colorData = ColorParticleData.create(color, color.darker()).setCoefficient(0.5f).build();
        return weepingWellSparks(level, pos, colorData, LodestoneWorldParticleRenderType.LUMITRANSPARENT);
    }

    public static ParticleEffectSpawner weepingWellSparks(Level level, Vec3 pos, ColorParticleData colorData, LodestoneWorldParticleRenderType renderType) {
        RandomSource rand = level.random;
        var lightSpecs = SparkParticleEffects.spiritMotionSparks(level, pos, colorData);
        lightSpecs.getBuilder()
                .setRenderType(renderType)
                .multiplyLifetime(6f)
                .modifyLengthData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1.75f, 2.5f)))
                .modifyTransparencyData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.75f, 1f)))
                .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1.5f, 3.5f)));
        lightSpecs.getBloomBuilder()
                .setRenderType(renderType)
                .multiplyLifetime(6f)
                .setTransparencyData(GenericParticleData.create(0f, 0.75f, 0.25f).build())
                .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1f, 1.25f)));
        return lightSpecs;
    }

    public static ParticleEffectSpawner weepingWellSpecs(Level level, Vec3 pos) {
        var rand = level.random;
        Color color = getWeepingWellSmokeColor(rand);
        ColorParticleData colorData = ColorParticleData.create(color, color.darker()).setCoefficient(0.5f).build();
        return weepingWellSpecs(level, pos, colorData, LodestoneWorldParticleRenderType.LUMITRANSPARENT);
    }

    public static ParticleEffectSpawner weepingWellSpecs(Level level, Vec3 pos, ColorParticleData colorData, LodestoneWorldParticleRenderType renderType) {
        var rand = level.random;
        var lightSpecs = spiritLightSpecs(level, pos, colorData, new WorldParticleOptions(MalumParticles.LIGHT_SPEC.get()));
        lightSpecs.getBuilder().act(b -> b
                .setRenderType(renderType)
                .multiplyLifetime(6f)
                .modifyTransparencyData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.75f, 1f)))
                .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1.5f, 3.5f))));
        lightSpecs.getBloomBuilder().act(b -> b
                .setRenderType(renderType)
                .multiplyLifetime(6f)
                .setTransparencyData(GenericParticleData.create(0f, 0.75f, 0.25f).build())
               
                .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1f, 1.25f))));
        return lightSpecs;
    }

    public static ParticleEffectSpawner weepingWellSquare(Level level, Vec3 pos, ColorParticleData colorData) {
        RandomSource rand = level.random;
        final GenericParticleData scaleData = GenericParticleData.create(0.1f, Easing.SINE_IN_OUT.asWeighedRandom(rand, 1.7f, 1.8f), 0.5f).setEasing(Easing.SINE_OUT, Easing.SINE_IN).setCoefficient(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1f, 1.25f)).build();
        final Consumer<LodestoneWorldParticle> behavior = p -> p.setParticleSpeed(p.getParticleSpeed().scale(0.95f));
        float yMotion = Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.04f, 0.06f);
        Vec3 motion = new Vec3(0f, yMotion, 0f);
        var squares = WorldParticleBuilder.create(MalumParticles.SQUARE.get())
                .setBehavior(DirectionalParticleBehavior.directional())
                .setTransparencyData(GenericParticleData.create(0.9f, 0.05f, 0f).setEasing(Easing.CUBIC_OUT, Easing.EXPO_IN).build())
                .setRenderTarget(LodestoneRenderingSystem.LATE_DEFERRED_RENDER)
                .setScaleData(scaleData)
                .setColorData(colorData)
                .addTickActor(behavior)
                .setMotion(motion)
                .setLifetime(100)
                .enableNoClip();
        Consumer<WorldParticleBuilder> squareSpawner = b -> b
                .spawn(level, pos.x, pos.y, pos.z)
                .setTransparencyData(GenericParticleData.create(0.1f, 0.6f, 0f).setEasing(Easing.CUBIC_OUT, Easing.EXPO_OUT).build())
                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                .spawn(level, pos.x, pos.y, pos.z);

        return new ParticleEffectSpawner(squares, squareSpawner);
    }
}
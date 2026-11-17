package com.sammy.malum.visual_effects;

import team.lodestar.lodestone.modules.rendering.LodestoneRenderingSystem;
import team.lodestar.lodestone.systems.network.*;
import net.minecraft.client.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.handlers.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.registry.common.particle.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;

import java.awt.*;

public class GluttonyParticleEffects {

    private static final Color GLUTTONY_GREEN = new Color(47, 81, 28);
    private static final Color GLUTTONY_DARK = new Color(31, 35, 30);
    private static final Color GLUTTONY_SHADE = new Color(14, 14, 16);

    public static void incrementGluttonyStatusEffect(NetworkedParticleEffectPositionData positionData, float gluttonyPotency) {
        Level level = Minecraft.getInstance().level;
        var random = level.random;

        for (int i = 0; i < 2; i++) {
            int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(random, 20, 30);
            WorldParticleBuilder.create(LodestoneParticleTypes.WISP_PARTICLE)
                    .setTransparencyData(GenericParticleData.create(0.2f, 0.7f, 0).build())
                    .setSpinData(SpinParticleData.createRandomDirection(random, 0.05f).build())
                    .setScaleData(GenericParticleData.create(0.2f, 0.75f, 0f).setCoefficient(1.25f).setEasing(Easing.SINE_IN, Easing.SINE_IN_OUT).build())
                    .setLifetime(lifetime)
                    .setColorData(ColorParticleData.create(GLUTTONY_DARK, GLUTTONY_SHADE).setCoefficient(2f).build())
                    .enableNoClip()
                    .setRandomOffset(0.2f, 0f)
                    .setMotion(0, 0.001f, 0)
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT.withDepthFade())
                    .repeat(level, positionData.getPosX(), positionData.getPosY(), positionData.getPosZ(), 2);
        }
        float distance = 0.5f + gluttonyPotency * 0.25f;
        float length = 1.4f * gluttonyPotency;
        float scale = 0.6f * gluttonyPotency;
        int count = 6;

        var options = new WorldParticleOptions(LodestoneParticleTypes.SPARKLE_PARTICLE).setBehavior(SparkParticleBehavior.sparkBehavior());
        var ring = gluttonyRing(positionData.getAsVector(), options, distance, count);
        ring.getBuilder()
                .modifyLengthData(d -> d.multiplyValue(length))
                .setScaleData(GenericParticleData.create(scale, 0f).setEasing(Easing.EXPO_IN).build());
        ring.spawnParticles();
    }

    public static void thrownGluttonySplash(NetworkedParticleEffectPositionData positionData) {
        Level level = Minecraft.getInstance().level;
        var random = level.random;

        for (int i = 0; i < 4; i++) {
            int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(random, 40, 50);
            float upwardsOffset = 0.1f + i * 0.05f;
            WorldParticleBuilder.create(LodestoneParticleTypes.WISP_PARTICLE)
                    .setBehavior(DirectionalParticleBehavior.directional())
                    .setTransparencyData(GenericParticleData.create(0.5f, 0.7f, 0).build())
                    .setColorData(ColorParticleData.create(GLUTTONY_DARK, GLUTTONY_SHADE).setCoefficient(2f).build())
                    .setScaleData(GenericParticleData.create(2f, 0f).setEasing(Easing.EXPO_IN).build())
                    .setSpinData(SpinParticleData.createRandomDirection(random, 0.05f).build())
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT.withDepthFade())
                    .setRandomOffset(1f, 0f)
                    .setMotion(0, 0.001f, 0)
                    .setLifetime(lifetime)
                    .enableNoClip()
                    .repeat(level, positionData.getPosX(), positionData.getPosY() + upwardsOffset, positionData.getPosZ(), 2);
        }
        var particle = LodestoneParticleTypes.THIN_EXTRUDING_SPARK_PARTICLE;
        var farRing = gluttonyRing(positionData.getAsVector(), new WorldParticleOptions(particle), 1.2f, 32, 1.5f);
        farRing.spawnParticles();
        var tallRing = gluttonyRing(positionData.getAsVector(), new WorldParticleOptions(particle), 0.4f, 16, 2f);
        tallRing.getBuilder().modifyLengthData(d -> d.multiplyValue(1.5f));
        tallRing.spawnParticles();
    }

    public static ParticleEffectSpawner gluttonyRing(Vec3 center, WorldParticleOptions options, float distance, int count) {
        return gluttonyRing(center, options, distance, count, 1f);
    }

    public static ParticleEffectSpawner gluttonyRing(Vec3 center, WorldParticleOptions options, float distance, int count, float lifetimeScalar) {
        Level level = Minecraft.getInstance().level;
        var random = level.random;
        var builder = WorldParticleBuilder.create(options.setBehaviorIfDefault(SparkParticleBehavior.sparkBehavior().setLengthCenter(1f)))
                .setLengthData(GenericParticleData.create(0.1f, 0.5f, 0f).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).setCoefficient(1.25f).build())
                .setScaleData(GenericParticleData.create(0.025f, Easing.SINE_IN_OUT.asWeighedRandom(random, 0.2f, 0.3f), 0).build())
                .setTransparencyData(GenericParticleData.create(0.4f, 1f, 0f).setEasing(Easing.EXPO_OUT, Easing.EXPO_IN).build());
        return gluttonyRing(center, builder, distance, count, lifetimeScalar);
    }

    public static ParticleEffectSpawner gluttonyRing(Vec3 center, WorldParticleBuilder builder, float distance, int count) {
        return gluttonyRing(center, builder, distance, count, 1f);
    }

    public static ParticleEffectSpawner gluttonyRing(Vec3 center, WorldParticleBuilder builder, float distance, int count, float lifetimeScalar) {
        return new ParticleEffectSpawner(builder, b -> {
            Level level = Minecraft.getInstance().level;
            long gameTime = level.getGameTime();
            var random = level.random;
            for (int i = 0; i < count; i++) {
                Vec3 offsetPosition = VecHelper.rotatingRadialOffset(center, distance, i, count, gameTime, 320);
                for (int j = 0; j < 3; j++) {
                    boolean isAdditive = j == 0;
                    Color bright = j < 2 ? GLUTTONY_GREEN : GLUTTONY_DARK;
                    Color dark = j < 2 ? GLUTTONY_GREEN : GLUTTONY_SHADE;
                    float alphaMultiplier = isAdditive ? 1.5f : 3f;
                    float scaleMultiplier = (isAdditive ? 1.25f : 2.5f) * Easing.SINE_IN_OUT.asWeighedRandom(random, 0.8f, 1.2f);
                    float lengthMultiplier = (isAdditive ? 0.75f : 1.25f) * Easing.SINE_IN_OUT.asWeighedRandom(random, 0.8f, 1.2f);;
                    float colorCoefficient = isAdditive ? 1f : 1.75f;
                    var renderType = isAdditive ? LodestoneWorldParticleRenderType.ADDITIVE : LodestoneWorldParticleRenderType.LUMITRANSPARENT;
                    var renderTarget = j < 2 ? LodestoneRenderingSystem.LATE_DEFERRED_RENDER : LodestoneRenderingSystem.DEFERRED_RENDER;
                    builder
                            .modifyLengthData(d -> d.copy().multiplyValue(lengthMultiplier))
                            .modifyTransparencyData(d -> d.copy().multiplyValue(alphaMultiplier))
                            .modifyScaleData(d -> d.copy().multiplyValue(scaleMultiplier))
                            .setColorData(ColorParticleData.create(bright, dark).setCoefficient(colorCoefficient).build())
                            .setLifetime((int) (Easing.SINE_IN_OUT.asWeighedRandom(random, 30, 60) * lifetimeScalar))
                            .setMotion(0, 0.001f, 0)
                            .setRenderTarget(renderTarget)
                            .setRenderType(renderType)
                            .enableNoClip()
                            .spawn(level, offsetPosition.x, offsetPosition.y, offsetPosition.z);
                }
            }
        });
    }
}
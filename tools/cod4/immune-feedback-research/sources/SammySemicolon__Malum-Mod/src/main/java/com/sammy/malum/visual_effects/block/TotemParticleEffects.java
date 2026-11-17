package com.sammy.malum.visual_effects.block;

import com.sammy.malum.client.*;
import com.sammy.malum.common.block.curiosities.totem.*;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import net.minecraft.core.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.registry.common.particle.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

import java.awt.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.*;

public class TotemParticleEffects {

    public static void activeTotemPoleParticles(TotemPoleBlockEntity totemPole) {
        var spiritType = totemPole.getSpirit();
        var level = totemPole.getLevel();
        long gameTime = level.getGameTime();
        var random = level.random;
        if (gameTime % 12L == 0) {
            int offset = totemPole.getBlockPos().getY() * 40;
            gameTime += offset;
            final float time = 480;
            for (int i = 0; i < 2; i++) {
                float velocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.005f, 0.015f);
                Vec3 offsetPosition = VecHelper.rotatingRadialOffset(totemPole.getBlockPos().getCenter(), 0.9f, i, 2, gameTime, time);
                offsetPosition = offsetPosition.add(0, (Math.cos(((gameTime + i * 240) % time) / time) * 0.25f) - 0.25f, 0);
                var lightSpecs = spiritLightSpecs(level, offsetPosition, spiritType);
                lightSpecs.getBuilder()
                        .multiplyLifetime(4.5f)
                        .setMotion(0, velocity, 0)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(3f)
                        .setMotion(0, velocity, 0)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void activateTotemPoleParticles(Level level, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectPositionData positionData) {
        long gameTime = level.getGameTime();
        var random = level.random;
        float time = 16;
        var position = positionData.getAsBlockPos().getCenter();
        for (int i = 0; i < 16; i++) {
            float velocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.005f, 0.015f);
            Vec3 offsetPosition = VecHelper.rotatingRadialOffset(position, 0.85f, i, 16, gameTime, time);
            offsetPosition = offsetPosition.add(0, (Math.cos(((gameTime + i * 240) % time) / time) * 0.25f) - 0.25f, 0);
            var lightSpecs = spiritLightSpecs(level, offsetPosition, colorData.getSpirit());
            lightSpecs.getBuilder()
                    .multiplyLifetime(2.5f)
                    .setMotion(0, velocity, 0)
                    .setLifeDelay(i)
                    .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
            lightSpecs.getBloomBuilder()
                    .multiplyLifetime(1.5f)
                    .setMotion(0, velocity, 0)
                    .setLifeDelay(i)
                    .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
            lightSpecs.spawnParticles();
        }
    }

    public static void triggerRiteUnweaver(Level level, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectPositionData positionData) {
        long gameTime = level.getGameTime();
        int count = 8;
        var position = positionData.getAsBlockPos().getBottomCenter();
        float distance = 0.45f;
        var voidColorData = ColorParticleData.create(new Color(12, 14, 52), new Color(6, 8, 12));
        for (int i = 0; i < count; i++) {
            var offsetPosition = VecHelper.rotatingRadialOffset(position, distance, i, count, gameTime, 320);
            WorldParticleBuilder.create(LodestoneParticleTypes.EXTRUDING_SPARK_PARTICLE)
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                    .setBehavior(SparkParticleBehavior.sparkBehavior().setForcedDirection(SparkParticleBehavior.UP).setLengthCenter(1f))
                    .setTransparencyData(GenericParticleData.create(0.8f, 0.4f, 0).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                    .setLengthData(GenericParticleData.create(0.6f, 0.2f).setEasing(Easing.SINE_IN_OUT).build())
                    .setScaleData(GenericParticleData.create(0.4f, 0f).setEasing(Easing.EXPO_IN).build())
                    .setColorData(voidColorData)
                    .setRandomOffset(0.1f)
                    .setLifetime(15)
                    .enableNoClip()
                    .repeat(level, offsetPosition, 3);
        }
    }

    public static void triggerRiteAnchor(Level level, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectPositionData positionData) {
        int count = 8;
        var position = positionData.getAsBlockPos().getBottomCenter().add(0, 0.25f, 0);
        for (int i = 0; i < count; i++) {
            int finalI = i;
            SpiritBasedParticleBuilder.createSpirit(LodestoneParticleTypes.EXTRUDING_SPARK_PARTICLE)
                    .setSpirit(colorData.getSpirit())
                    .setBehavior(DirectionalParticleBehavior.directional())
                    .setTransparencyData(GenericParticleData.create(0.15f, 0.2f, 0).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                    .setLengthData(GenericParticleData.create(0.1f, 0.5f).setEasing(Easing.SINE_IN_OUT).build())
                    .setScaleData(GenericParticleData.create(0.3f, 0f).setEasing(Easing.EXPO_IN).build())
                    .setRandomOffset(0.1f)
                    .setLifetime(15)
                    .enableNoClip()
                    .addTickActor(p -> {
                        long gameTime = level.getGameTime();
                        float distance = 0.6f - 0.4f * (p.getAge() / (float)p.getLifetime());
                        var offsetPosition = VecHelper.rotatingRadialOffset(position, distance, finalI, count, gameTime, 40);
                        p.setParticlePosition(offsetPosition);
                        p.setParticleSpeed(position.subtract(offsetPosition).normalize().scale(0.001f));
                    })
                    .repeat(level, position, 3);
        }
    }

    public static void triggerRiteAnchorFailure(Level level, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectPositionData positionData) {
        int count = 8;
        var position = positionData.getAsBlockPos().getBottomCenter().add(0, 0.25f, 0);
        for (int i = 0; i < count; i++) {
            int finalI = i;
            WorldParticleBuilder.create(LodestoneParticleTypes.EXTRUDING_SPARK_PARTICLE)
                    .setBehavior(DirectionalParticleBehavior.directional())
                    .setTransparencyData(GenericParticleData.create(0.15f, 0.2f, 0).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                    .setLengthData(GenericParticleData.create(0.5f, 0.1f).setEasing(Easing.SINE_IN_OUT).build())
                    .setScaleData(GenericParticleData.create(0.1f, 0.3f).setEasing(Easing.EXPO_IN).build())
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                    .setColorData(colorData.getColor())
                    .setRandomOffset(0.1f)
                    .setLifetime(15)
                    .enableNoClip()
                    .addTickActor(p -> {
                        long gameTime = level.getGameTime();
                        float distance = 0.6f - 0.4f * (p.getAge() / (float)p.getLifetime());
                        var offsetPosition = VecHelper.rotatingRadialOffset(position, distance, finalI, count, gameTime, 40);
                        p.setParticlePosition(offsetPosition);
                        p.setParticleSpeed(position.subtract(offsetPosition).normalize().scale(0.001f));
                    })
                    .repeat(level, position, 3);
        }
    }

    public static void triggerEntityEffect(Level level, MalumNetworkedParticleEffectColorData colorData, Vec3 position) {
        long gameTime = level.getGameTime();
        var random = level.random;
        final float time = 16;
        for (int i = 0; i < 8; i++) {
            var offsetPosition = VecHelper.rotatingRadialOffset(position, 0.7f, i, 8, gameTime, time);
            offsetPosition = offsetPosition.add(0, (Math.cos(((gameTime + i * 480) % time) / time) * 0.25f) - 0.25f, 0);
            for (int j = 0; j < 3; j++) {
                var lightSpecs = spiritLightSpecs(level, offsetPosition, colorData.getColor());
                float velocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.02f, 0.03f);
                var motion = offsetPosition.subtract(position).normalize().scale(velocity);
                lightSpecs.getBuilder()
                        .multiplyLifetime(2.5f)
                        .setMotion(motion)
                        .setLifeDelay(j * 6)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(1.5f)
                        .setMotion(motion)
                        .setLifeDelay(j * 6)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void triggerBlockEffect(Level level, MalumNetworkedParticleEffectColorData colorData, BlockPos position) {
        var random = level.random;
        for (int i = 0; i < 4; i++) {
            int xOffset = Mth.clamp(i%3, 0, 1);
            int zOffset = Mth.clamp((i-1)%4, 0, 1);
            float xMotion = (i%2) * (i > 1 ? 0.06f : -0.06f);
            float zMotion = ((i + 1) % 2) * (i > 1 ? -0.06f : 0.06f);
            var spirit = colorData.getSpirit();
            for (int j = 0; j < 2; j++) {
                Vec3 offsetPosition = new Vec3(position.getX()+xOffset, position.getY()+j, position.getZ()+zOffset);
                var lightSpecs = spiritLightSpecs(level, offsetPosition, spirit);
                lightSpecs.getBuilder()
                        .multiplyLifetime(2.5f)
                        .setMotion(xMotion, 0, zMotion)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(1.5f)
                        .setMotion(xMotion, 0, zMotion)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void triggerBlockFallEffect(Level level, MalumNetworkedParticleEffectColorData colorData, BlockPos position) {
        var random = level.random;
        for (int i = 0; i < 4; i++) {
            int xOffset = Mth.clamp(i%3, 0, 1);
            int zOffset = Mth.clamp((i-1)%4, 0, 1);
            for (int j = 0; j < 2; j++) {
                Vec3 offsetPosition = new Vec3(position.getX()+xOffset, position.getY()+j, position.getZ()+zOffset);
                float motion = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.05f, 0.06f);
                Vec3 velocity = position.getCenter().subtract(offsetPosition).add(0, -2, 0).normalize().scale(motion);
                var lightSpecs = spiritLightSpecs(level, offsetPosition, colorData.getSpirit());
                lightSpecs.getBuilder()
                        .multiplyLifetime(2.5f)
                        .setMotion(velocity)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void triggerBlockGrowEffect(Level level, MalumNetworkedParticleEffectColorData colorData, BlockPos position) {
        var random = level.random;
        for (int i = 0; i < 4; i++) {
            int xOffset = Mth.clamp(i%3, 0, 1);
            int zOffset = Mth.clamp((i-1)%4, 0, 1);
            float xMotion = (i%2) * (i > 1 ? 0.06f : -0.06f);
            float yMotion = 0.05f;
            float zMotion = ((i + 1) % 2) * (i > 1 ? -0.06f : 0.06f);
            for (int j = 0; j < 2; j++) {
                Vec3 offsetPosition = new Vec3(position.getX()+xOffset, position.getY()+0.5f, position.getZ()+zOffset);
                var lightSpecs = spiritLightSpecs(level, offsetPosition, colorData.getSpirit());
                lightSpecs.getBuilder()
                        .multiplyLifetime(3.5f)
                        .setMotion(xMotion, yMotion, zMotion)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(2.5f)
                        .setMotion(xMotion, yMotion, zMotion)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void triggerBlockInfusionEffect(Level level, MalumNetworkedParticleEffectColorData colorData, BlockPos position) {
        var random = level.random;
        for (int i = 0; i < 4; i++) {
            int xOffset = Mth.clamp(i%3, 0, 1);
            int zOffset = Mth.clamp((i-1)%4, 0, 1);
            float xMotion = (i%2) * (i > 1 ? 0.06f : -0.06f);
            float zMotion = ((i + 1) % 2) * (i > 1 ? -0.06f : 0.06f);
            for (int j = 0; j < 6; j++) {
                float yMotion = -0.12f + j * -0.01f;
                float yOffset = 2.5f + j%2 + Mth.floor(j/4f);
                int lifeDelay = (j / 2) * 6;
                Vec3 offsetPosition = new Vec3(position.getX()+xOffset, position.getY()+yOffset, position.getZ()+zOffset);
                var lightSpecs = spiritLightSpecs(level, offsetPosition, colorData.getSpirit());
                lightSpecs.getBuilder()
                        .multiplyLifetime(3.5f)
                        .setMotion(xMotion, yMotion, zMotion)
                        .setLifeDelay(lifeDelay)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(2.5f)
                        .setMotion(xMotion, yMotion, zMotion)
                        .setLifeDelay(lifeDelay)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }
}
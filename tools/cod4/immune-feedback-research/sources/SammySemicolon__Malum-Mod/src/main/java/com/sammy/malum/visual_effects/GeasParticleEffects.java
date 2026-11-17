package com.sammy.malum.visual_effects;

import com.sammy.malum.client.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.geas.*;
import net.minecraft.client.*;
import net.minecraft.util.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.handlers.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.rendering.LodestoneRenderingSystem;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.LodestoneWorldParticle;
import team.lodestar.lodestone.registry.common.particle.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.*;
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
import team.lodestar.lodestone.systems.rendering.LodestoneRenderSystem;
import team.lodestar.lodestone.systems.rendering.renderpass.RenderPassHandler;

import java.awt.*;
import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;
import static net.minecraft.util.Mth.*;

public class GeasParticleEffects {

    public static void lifeWeaverHealingBeam(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, LifeweaverHealingBeamParticleEffect.LifeweaverHealingBeamEffectData extraData) {
        var target = level.getEntity(extraData.targetId());
        var source = level.getEntity(extraData.sourceId());
        if (target != null && source != null) {
            var pos = positionData.getAsVector();
            final Vec3 targetPos = target.position().add(0, target.getBbHeight() / 2f, 0);
            var direction = targetPos.subtract(pos).normalize();
            float yRot = ((float) (Mth.atan2(direction.x, direction.z) * (double) (180F / (float) Math.PI)));
            float yaw = (float) Math.toRadians(yRot);
            Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
            Vec3 up = left.cross(direction);

            final Consumer<LodestoneWorldParticle> behavior = p -> {
                float partialTick = Minecraft.getInstance().getTimer().getGameTimeDeltaPartialTick(true);
                var spark = (SparkParticleBehavior) p.behavior;
                final Vec3 distance = target.getPosition(partialTick).add(0, target.getBbHeight()/2f, 0).subtract(p.getParticlePosition());
                spark.setForcedDirection(distance.normalize());
                final float length = (float) Math.clamp(distance.length(), 2, 4);
                p.lengthData.overrideValueMultiplier(length / 6f);
                p.scaleData.overrideValueMultiplier(length / 4f);
            };
            for (int i = 0; i < 4; i++) {
                SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
                float spread = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 0.8f);
                float speed = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 0.8f);
                float angle = i / 4f * (float) Math.PI * 2f;
                Vec3 particleDirection = direction
                        .add(left.scale(Math.sin(angle) * spread))
                        .add(up.scale(Math.cos(angle) * spread))
                        .normalize().scale(speed);
                Vec3 particlePosition = pos.add(particleDirection.scale(0.4f));
                final int lifeDelay = i * 2;
                SpiritBasedParticleBuilder.createSpirit(LodestoneParticleTypes.EXTRUDING_SPARK_PARTICLE)
                        .setSpirit(cyclingSpiritType)
                        .setTransparencyData(GenericParticleData.create(0f, 0.7f, 0).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                        .setLengthData(GenericParticleData.create(0.8f, 2.6f, 0.4f).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                        .setScaleData(GenericParticleData.create(0.2f, 0.4f, 0.2f).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                        .setBehavior(SparkParticleBehavior.sparkBehavior().setForcedDirection(direction).setLengthCenter(1f))
                        .setRandomOffset(0.1f)
                        .setLifetime(15)
                        .setLifeDelay(lifeDelay)
                        .enableNoClip()
                        .addRenderActor(behavior)
                        .spawn(level, particlePosition.x, particlePosition.y, particlePosition.z);


                SpiritBasedParticleBuilder.createSpirit(MalumParticles.GIANT_GLOWING_STAR)
                        .setSpirit(cyclingSpiritType)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.3f, 0).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                        .setScaleData(GenericParticleData.create(0.3f, 0.6f, 0.2f).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                        .setLifetime(15)
                        .setLifeDelay(lifeDelay)
                        .enableNoClip()
                        .spawn(level, particlePosition.x, particlePosition.y, particlePosition.z);
                SpiritBasedParticleBuilder.createSpirit(MalumParticles.STAR)
                        .setSpirit(cyclingSpiritType)
                        .setTransparencyData(GenericParticleData.create(0.15f, 0.5f, 0).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                        .setScaleData(GenericParticleData.create(0.05f, 0.2f, 0.1f).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).build())
                        .setLifetime(15)
                        .setLifeDelay(lifeDelay)
                        .enableNoClip()
                        .spawn(level, particlePosition.x, particlePosition.y, particlePosition.z);
            }

            long gameTime = level.getGameTime();
            float time = 16;
            for (int i = 0; i < 6; i++) {
                var offsetTargetPosition = VecHelper.rotatingRadialOffset(targetPos, 1.1f, i, 6, gameTime, time);
                double timeOffset = (Math.cos(((gameTime + i * 480) % time) / time) * 0.25f) - 0.25f;
                offsetTargetPosition = offsetTargetPosition.add(0, timeOffset, 0);
                 for (int j = 0; j < 2; j++) {
                    var lightSpecs = spiritLightSpecs(level, offsetTargetPosition, colorData.getColor());
                    float velocity = -Easing.SINE_IN_OUT.asWeighedRandom(random, 0.05f, 0.1f);
                    var motion = offsetTargetPosition.subtract(targetPos).normalize().scale(velocity);
                    lightSpecs.getBuilder()
                            .multiplyLifetime(0.8f)
                            .setMotion(motion)
                            .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                            .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                    lightSpecs.getBloomBuilder()
                            .multiplyLifetime(0.6f)
                            .setMotion(motion)
                            .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                            .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                    lightSpecs.spawnParticles();
                }
            }
        }
    }


    public static void warlockBlast(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, WeaponParticleEffectType.WeaponParticleEffectData extraData) {
        var pos = positionData.getAsVector();
        var direction = extraData.getDirection();
        float yRot = ((float) (Mth.atan2(direction.x, direction.z) * (double) (180F / (float) Math.PI)));
        float yaw = (float) Math.toRadians(yRot);
        Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
        Vec3 up = left.cross(direction);

        float scaleMultiplier = (float) (1 + Math.pow(random.nextFloat(), 2) * 0.5f);
        WorldParticleBuilder.create(MalumParticles.STAR.get())
                .setTransparencyData(GenericParticleData.create(0.5f, 0.07f, 0).setEasing(Easing.SINE_IN, Easing.CIRC_IN).build())
                .setLifetime(15)
                .setSpinData(SpinParticleData.createRandomDirection(random, nextFloat(random, 0.05f, 0.1f)).randomSpinOffset(random).build())
                .setScaleData(GenericParticleData.create(1.25f * scaleMultiplier, 0.5f, 0).setEasing(Easing.EXPO_OUT, Easing.SINE_IN).build())
                .setColorData(colorData.getColor())
                .setRandomOffset(0.2f)
                .enableNoClip()
                .setRandomMotion(0.02f, 0.02f)
                .repeat(level, pos.x, pos.y, pos.z, 3)
                .modifyScaleData(d -> d.multiplyValue(0.6f))
                .repeat(level, pos.x, pos.y, pos.z, 2);

        for (int i = 0; i < 16; i++) {
            var color = colorData.getColor();
            float spread = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.1f, 0.2f);
            float speed = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 0.8f);
            float distance = -Easing.SINE_IN_OUT.asWeighedRandom(random, 4f, 6f);
            float angle = i / 16f * (float) Math.PI * 2f;

            Vec3 particleDirection = direction
                    .add(left.scale(Math.sin(angle) * spread))
                    .add(up.scale(Math.cos(angle) * spread))
                    .normalize().scale(speed);
            Vec3 spawnPosition = pos.add(particleDirection.scale(distance));
            float lifetimeMultiplier = 0.7f;
            if (random.nextFloat() < 0.8f) {
                var lightSpecs = spiritLightSpecs(level, spawnPosition, color);
                lightSpecs.getBuilder()
                        .multiplyLifetime(lifetimeMultiplier)
                        .enableForcedSpawn()
                        .modifyScaleData(d -> d.multiplyValue(1.25f))
                        .setMotion(particleDirection);
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(lifetimeMultiplier)
                        .setMotion(particleDirection);
                lightSpecs.spawnParticles();
            }
            if (random.nextFloat() < 0.8f) {
                var sparks = SparkParticleEffects.spiritMotionSparks(level, spawnPosition, color);
                sparks.getBuilder()
                        .multiplyLifetime(lifetimeMultiplier)
                        .enableForcedSpawn()
                        .setMotion(particleDirection.scale(1.5f))
                        .modifyScaleData(d -> d.multiplyValue(1.25f))
                        .modifyLengthData(d -> d.multiplyValue(4f));
                sparks.getBloomBuilder()
                        .multiplyLifetime(lifetimeMultiplier)
                        .setMotion(particleDirection.scale(1.5f));
                sparks.spawnParticles();
            }
        }
    }

    public static void berserkerBlast(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        var pos = positionData.getAsVector();

        float scaleMultiplier = (float) (1 + Math.pow(random.nextFloat(), 2) * 0.5f);
        WorldParticleBuilder.create(MalumParticles.STAR.get())
                .setTransparencyData(GenericParticleData.create(0.4f, 0.07f, 0).setEasing(Easing.SINE_IN, Easing.CIRC_IN).build())
                .setLifetime(12)
                .setSpinData(SpinParticleData.createRandomDirection(random, nextFloat(random, 0.05f, 0.1f)).randomSpinOffset(random).build())
                .setScaleData(GenericParticleData.create(1.5f * scaleMultiplier, 0.5f, 0).setEasing(Easing.EXPO_OUT, Easing.SINE_IN).build())
                .setColorData(colorData.getColor())
                .setRandomOffset(0.2f)
                .enableNoClip()
                .setRandomMotion(0.02f, 0.02f)
                .repeat(level, pos.x, pos.y, pos.z, 3)
                .modifyScaleData(d -> d.multiplyValue(0.6f))
                .repeat(level, pos.x, pos.y, pos.z, 2);

        long gameTime = level.getGameTime();
        float time = 16;
        for (int i = 0; i < 8; i++) {
            var offsetTargetPosition = VecHelper.rotatingRadialOffset(pos, 1.5f, i, 8, gameTime, time);
            float angleOffset = random.nextFloat() * 6.28f;
            var direction = pos.subtract(offsetTargetPosition).normalize();
            float yRot = ((float) (Mth.atan2(direction.x, direction.z) * (double) (180F / (float) Math.PI)));
            float yaw = (float) Math.toRadians(yRot);
            Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
            Vec3 up = left.cross(direction);
            for (int j = 0; j < 3; j++) {
                var color = colorData.getColor();
                float spread = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.1f, 0.2f);
                float speed = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 0.8f);
                float distance = -Easing.SINE_IN_OUT.asWeighedRandom(random, 4f, 6f);
                float angle = angleOffset + j / 3f * (float) Math.PI * 2f;

                Vec3 particleDirection = direction
                        .add(left.scale(Math.sin(angle) * spread))
                        .add(up.scale(Math.cos(angle) * spread))
                        .normalize().scale(speed);
                Vec3 spawnPosition = pos.add(particleDirection.scale(distance));
                float lifetimeMultiplier = 0.4f;
                if (random.nextFloat() < 0.8f) {
                    var lightSpecs = spiritLightSpecs(level, spawnPosition, color);
                    lightSpecs.getBuilder()
                            .multiplyLifetime(lifetimeMultiplier)
                            .enableForcedSpawn()
                            .modifyScaleData(d -> d.multiplyValue(1.75f))
                            .setMotion(particleDirection);
                    lightSpecs.getBloomBuilder()
                            .multiplyLifetime(lifetimeMultiplier)
                            .setMotion(particleDirection);
                    lightSpecs.spawnParticles();
                }
                if (random.nextFloat() < 0.8f) {
                    var sparks = SparkParticleEffects.spiritMotionSparks(level, spawnPosition, color);
                    sparks.getBuilder()
                            .multiplyLifetime(lifetimeMultiplier)
                            .enableForcedSpawn()
                            .setMotion(particleDirection.scale(1.5f))
                            .modifyScaleData(d -> d.multiplyValue(1.75f))
                            .modifyLengthData(d -> d.multiplyValue(3f));
                    sparks.getBloomBuilder()
                            .multiplyLifetime(lifetimeMultiplier)
                            .setMotion(particleDirection.scale(1.5f));
                    sparks.spawnParticles();
                }
            }
        }
    }

    public static void highPriestPenanceFaith(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        var pos = positionData.getAsVector();
        long gameTime = level.getGameTime();
        float time = 16;
        for (int i = 0; i < 12; i++) {
            var offsetTargetPosition = VecHelper.rotatingRadialOffset(pos, 1.5f, i, 12, gameTime, time);
            double timeOffset = (Math.cos(((gameTime + i * 480) % time) / time) * 0.25f) - 0.25f;
            offsetTargetPosition = offsetTargetPosition.add(0, timeOffset, 0);
            for (int j = 0; j < 3; j++) {
                var lightSpecs = spiritLightSpecs(level, offsetTargetPosition, colorData.getColor());
                float velocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.45f, 0.55f);
                var motion = offsetTargetPosition.subtract(pos).normalize().scale(-velocity);
                lightSpecs.getBuilder()
                        .multiplyLifetime(0.6f)
                        .setMotion(motion)
                        .setLifeDelay(j*3)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(0.6f)
                        .setMotion(motion)
                        .setLifeDelay(j*3)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void patienceRepaid(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        var pos = positionData.getAsVector();
        long gameTime = level.getGameTime();
        float time = 64;
        for (int i = 0; i < 12; i++) {
            for (int j = 0; j < 4; j++) {
                var offsetTargetPosition = VecHelper.rotatingRadialOffset(pos, 1.25f-0.05f*j, i, 12, gameTime+j, time);
                var lightSpecs = spiritLightSpecs(level, offsetTargetPosition, colorData.getColor());
                float velocity = 0.075f;
                var motion = offsetTargetPosition.subtract(pos).normalize().scale(-velocity);
                lightSpecs.getBuilder()
                        .multiplyLifetime(0.8f)
                        .setMotion(motion)
                        .setLifeDelay(j*2)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(0.8f)
                        .setMotion(motion)
                        .setLifeDelay(j*2)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void combustionBurn(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        var pos = positionData.getAsVector();
        for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 2; j++) {
                var offsetTargetPosition = VecHelper.radialOffset(pos, 1f-j*0.1f, i, 16);
                var lightSpecs = spiritLightSpecs(level, offsetTargetPosition, colorData.getColor());
                float velocity = 0.075f;
                int delay = (int) (j * 2 + i * 0.75f);
                lightSpecs.getBuilder()
                        .multiplyLifetime(0.8f)
                        .setMotion(0, velocity, 0)
                        .setLifeDelay(delay)
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(0.8f)
                        .setMotion(0, velocity, 0)
                        .setLifeDelay(delay)
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void prospectorsGreedBurn(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        var pos = positionData.getAsVector();
        for (int i = 0; i < 16; i++) {
            for (int j = 0; j < 6; j++) {
                var offsetTargetPosition = VecHelper.radialOffset(pos, 1.4f-j*0.1f, i, 8);
                float velocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.01f, 0.02f);
                var motion = offsetTargetPosition.subtract(pos).normalize().scale(-velocity);

                var lightSpecs = spiritLightSpecs(level, offsetTargetPosition, colorData.getColor());
                int delay = j * 2;
                lightSpecs.getBuilder()
                        .setTransparencyData(GenericParticleData.create(0.2f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)))
                        .multiplyLifetime(0.4f)
                        .setLifeDelay(delay)
                        .setFriction(2f)
                        .setMotion(motion);
                lightSpecs.getBloomBuilder()
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)))
                        .multiplyLifetime(0.4f)
                        .setLifeDelay(delay)
                        .setFriction(2f)
                        .setMotion(motion);
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void wyrdReconstructionRevive(Level level, Entity entity, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        double posX = positionData.getPosX();
        double posY = positionData.getPosY();
        double posZ = positionData.getPosZ();
        Vec3 pos = new Vec3(posX, posY, posZ);
        final Color smokeColor = new Color(45, 15, 15);

        for (int i = 0; i < 12; i++) {
            Color primaryColor = colorData.getColor().getStartingColor();
            int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(random, 20, 40);
            final boolean isAdditive = i % 2 == 0;
            final float scale = (2f + i * 0.5f) * (isAdditive ? 1 : 2);
            final LodestoneWorldParticleRenderType renderType = (isAdditive ? LodestoneWorldParticleRenderType.ADDITIVE : LodestoneWorldParticleRenderType.LUMITRANSPARENT).withDepthFade();
            final float spin = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.04f, 0.08f);
            float randomOffset = i * 0.2f;
            for (int j = 0; j < 2; j++) {
                var options = new WorldParticleOptions(MalumParticles.GIANT_GLOWING_STAR);
                if (j == 1) {
                    options.setBehavior(DirectionalParticleBehavior.directional());
                }
                WorldParticleBuilder.create(options)
                        .setTransparencyData(GenericParticleData.create(0.1f, 0.4f, 0).build())
                        .setColorData(ColorParticleData.create(primaryColor, smokeColor).setCoefficient(4f).build())
                        .setScaleData(GenericParticleData.create(scale / 2f, scale, 0.5f).setCoefficient(1.25f).setEasing(Easing.EXPO_OUT, Easing.EXPO_IN).build())
                        .setSpinData(SpinParticleData.createRandomDirection(random, spin).build())
                        .setRenderType(renderType)
                        .setRandomOffset(randomOffset, 0)
                        .setMotion(0, 0.001f, 0)
                        .setLifetime(lifetime)
                        .enableNoClip()
                        .repeat(level, posX, posY - 0.3f, posZ, 2);
            }
        }

        int sparkCount = 64;
        float distance = 0.7f;
        long gameTime = level.getGameTime();
        Consumer<LodestoneWorldParticle> behavior = p -> {
            Vec3 offset = entity.position().add(0, entity.getBbHeight() / 2f, 0).subtract(p.getParticlePosition());
            float length = (float) offset.length();
            if (length == 0) {
                offset = new Vec3(0, 0.02f, 0);
            }
            float delta = Math.max(p.getAge() / (float) p.getLifetime(), 0) * 2;
            float lerp = Easing.QUINTIC_IN.lerp(delta, 0, 0.3f);
            float velocity = Easing.CIRC_IN.lerp(delta, 0f, 0.3f + length * 0.6f);
            final Vec3 speed = p.getParticleSpeed().lerp(offset.normalize().scale(velocity), lerp);
            p.setParticleSpeed(speed);
        };
        for (int i = 0; i < sparkCount; i++) {
            ColorParticleData color = colorData.getColor();
            Color primaryColor = color.getStartingColor();
            Color secondaryColor = color.getEndingColor();
            Vec3 offsetPosition = VecHelper.rotatingRadialOffset(pos, distance, i, sparkCount, gameTime, 320);
            final float motionFactor = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.06f, 0.12f);
            int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(random, 20, 40);
            Vec3 motion = offsetPosition.subtract(pos).normalize().scale(motionFactor);
            distance += 0.03f;
            gameTime += 10;
            for (int j = 0; j < 12; j++) {
                boolean isAdditive = j % 2 == 0;
                Color start = isAdditive ? primaryColor : secondaryColor;
                Color end = isAdditive ? secondaryColor : smokeColor;
                float lengthMultiplier = (isAdditive ? 0.5f : 1f) * Easing.SINE_IN_OUT.asWeighedRandom(random, 0.4f, 1.8f);
                float scaleMultiplier = (isAdditive ? 1.75f : 5.5f) * Easing.SINE_IN_OUT.asWeighedRandom(random, 0.4f, 1.8f);
                float alphaMultiplier = isAdditive ? 1.5f : 3f;
                float colorCoefficient = isAdditive ? 1f : 1.75f;
                var renderType = isAdditive ? LodestoneWorldParticleRenderType.ADDITIVE : LodestoneWorldParticleRenderType.LUMITRANSPARENT;
                var renderTarget = isAdditive ? LodestoneRenderingSystem.LATE_DEFERRED_RENDER : LodestoneRenderingSystem.DEFERRED_RENDER;
                WorldParticleBuilder.create(new WorldParticleOptions(MalumParticles.GIANT_GLOWING_STAR))
                        .setBehavior(SparkParticleBehavior.sparkBehavior().setForcedDirection(new Vec3(0, 1, 0)))
                        .setLengthData(GenericParticleData.create(0.1f, 0.6f, 0.3f).setEasing(Easing.SINE_IN_OUT, Easing.SINE_IN_OUT).setCoefficient(1.25f).build().multiplyValue(lengthMultiplier))
                        .setScaleData(GenericParticleData.create(0.025f, 0.25f, 0.6f).build().multiplyValue(scaleMultiplier))
                        .setTransparencyData(GenericParticleData.create(0.8f, 0f).build().multiplyValue(alphaMultiplier))
                        .setColorData(ColorParticleData.create(start, end).setCoefficient(colorCoefficient).build())
                        .setRenderTarget(renderTarget)
                        .setRenderType(renderType)
                        .setLifeDelay(j + i / 2)
                        .addTickActor(behavior)
                        .setLifetime(lifetime)
                        .enableNoClip()
                        .setMotion(motion)
                        .spawn(level, offsetPosition.x, offsetPosition.y, offsetPosition.z);
            }
        }
    }

    public static void invertedHeartDamageEffect(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        double posX = positionData.getPosX();
        double posY = positionData.getPosY();
        double posZ = positionData.getPosZ();
        Vec3 pos = new Vec3(posX, posY, posZ);
        Vec3 directionToPlayer = Minecraft.getInstance().player.getEyePosition().subtract(pos).normalize();
        Vec3 behindPos = pos.subtract(directionToPlayer.scale(2f));
        Vec3 inFrontPos = pos.add(directionToPlayer.scale(0.75f));
        for (int i = 0; i < 3; i++) {
            final ColorParticleData color = colorData.getColor();
            final SpinParticleData spinData = SpinParticleData.createRandomDirection(random, nextFloat(random, 0.15f, 0.3f)).randomSpinOffset(random).build();
            float scaleMultiplier = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f);
            WorldParticleBuilder.create(MalumParticles.SHINE.get())
                    .setScaleData(GenericParticleData.create(0.8f * scaleMultiplier, 0.25f, 0).setEasing(Easing.EXPO_OUT, Easing.SINE_IN).build())
                    .setTransparencyData(GenericParticleData.create(0.6f, 0.07f, 0).setEasing(Easing.SINE_IN, Easing.CIRC_IN).build())
                    .setSpritePicker(SimpleParticleOptions.ParticleSpritePicker.WITH_AGE)
                    .setLifetime(Easing.SINE_IN_OUT.asWeighedRandom(random, 5, 15))
                    .setRandomMotion(0.02f, 0.02f)
                    .setColorData(color)
                    .setSpinData(spinData)
                    .setRandomOffset(1f)
                    .enableNoClip()
                    .repeat(level, inFrontPos.x, inFrontPos.y, inFrontPos.z, 2);

            WorldParticleBuilder.create(MalumParticles.GIANT_GLOWING_STAR.get())
                    .setScaleData(GenericParticleData.create(5f * scaleMultiplier, 0.25f, 0).setEasing(Easing.SINE_IN, Easing.SINE_IN).build())
                    .setTransparencyData(GenericParticleData.create(0.4f, 0.07f, 0).setEasing(Easing.SINE_IN, Easing.CIRC_IN).build())
                    .setColorData(color.invert().build())
                    .setLifetime(Easing.SINE_IN_OUT.asWeighedRandom(random, 10, 20))
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                    .setRandomMotion(0.02f, 0.02f)
                    .setSpinData(spinData)
                    .setRandomOffset(1f)
                    .enableNoClip()
                    .repeat(level, behindPos.x, behindPos.y, behindPos.z, 1);
        }
    }
}
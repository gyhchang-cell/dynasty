package com.sammy.malum.visual_effects;

import com.sammy.malum.common.entity.mob.cultist.cardinal.projectile.EntropyChargeProjectile;
import com.sammy.malum.common.entity.mob.cultist.cardinal.CardinalCultist;
import com.sammy.malum.registry.common.MalumParticles;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import team.lodestar.lodestone.helpers.VecHelper;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.WorldParticleBuilder;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.GenericParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.ColorParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.SpinParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.LodestoneWorldParticleRenderType;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.LodestoneWorldParticle;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.DirectionalParticleBehavior;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.SparkParticleBehavior;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.WorldParticleOptions;

import java.util.function.Consumer;
import java.util.function.Function;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;
import static net.minecraft.util.Mth.nextFloat;

public class CultistParticleEffects {

    public static void altarFireProjectile(Level level, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        var random = level.random;
        var position = positionData.getAsVector();

        for (int i = 0; i < 4; i++) {
            int lifeDelay = i * 2;
            cultistSigil(level, colorData)
                    .setSpinData(SpinParticleData.createRandomDirection(random, 0.3f, 0).setEasing(Easing.EXPO_OUT).build())
                    .modifyScaleData(d -> d.multiplyValue(1.25f))
                    .setLifeDelay(lifeDelay)
                    .spawn(level, position);
        }
        long gameTime = level.getGameTime();
        float time = 16;
        for (int i = 0; i < 8; i++) {
            var offsetPosition = VecHelper.rotatingRadialOffset(position, 0.8f, i, 8, gameTime, time);
            offsetPosition = offsetPosition.add(0, (Math.cos(((gameTime + i * 480) % time) / time) * 0.25f) - 0.25f, 0);
            for (int j = 0; j < 3; j++) {
                var lightSpecs = spiritLightSpecs(level, offsetPosition, colorData.getColor());
                float velocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.02f, 0.03f);
                var motion = offsetPosition.subtract(position).normalize().scale(velocity);
                int lifeDelay = j * 6;
                lightSpecs.getBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .multiplyLifetime(2.5f)
                        .setMotion(motion)
                        .setLifeDelay(lifeDelay)
                        .setTransparencyData(GenericParticleData.create(0.9f, 0.5f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .multiplyLifetime(1.5f)
                        .setMotion(motion)
                        .setLifeDelay(lifeDelay)
                        .setTransparencyData(GenericParticleData.create(0.6f, 0.35f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
        for (int i = 0; i < 16; i++) {
            var offsetPosition = VecHelper.rotatingRadialOffset(position, 0.4f, i, 16, gameTime, time);
            offsetPosition = offsetPosition.add(0, (Math.cos(((gameTime + i * 480) % time) / time) * 0.25f) - 0.25f, 0);
            float upwardsVelocity = 0.02f;
            for (int j = 0; j < 2; j++) {
                var lightSpecs = SparkParticleEffects.spiritMotionSparks(level, offsetPosition, colorData.getColor(), new WorldParticleOptions(MalumParticles.MOTION_LINES));
                float velocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.02f, 0.03f);
                var motion = offsetPosition.subtract(position).normalize().scale(velocity);
                int lifeDelay = j * 3;
                lightSpecs.getBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .multiplyLifetime(1.5f)
                        .setMotion(motion)
                        .addMotion(0, upwardsVelocity, 0)
                        .setLifeDelay(lifeDelay)
                        .setTransparencyData(GenericParticleData.create(0.9f, 0.6f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .multiplyLifetime(1.5f)
                        .setMotion(motion)
                        .addMotion(0, upwardsVelocity, 0)
                        .setLifeDelay(lifeDelay)
                        .setTransparencyData(GenericParticleData.create(0.9f, 0.35f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void altarBlessTarget(Level level, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, LivingEntity target) {
        var random = level.random;
        var position = positionData.getAsVector();

        Function<Vec3, Consumer<LodestoneWorldParticle>> behavior = initialOffset -> p -> {
            var targetPosition = target.getPosition(p.partialTicksCache);
            p.setParticlePosition(targetPosition.add(initialOffset).add(p.getInterpolatedTravelledDistance()));
        };
        var offset = behavior.apply(position.subtract(target.position()));
        for (int i = 0; i < 5; i++) {
            int lifeDelay = i * 2;
            float upwardsMotion = 0.01f * i;
            float scale = 2f + i * 0.25f;
            cultistSigil(level, colorData)
                    .setSpinData(SpinParticleData.createRandomDirection(random, 0.3f, 0).setEasing(Easing.EXPO_OUT).build())
                    .modifyScaleData(d -> d.multiplyValue(scale))
                    .setBehavior(DirectionalParticleBehavior.directional(new Vec3(0, 1, 0)))
                    .setFriction(0.9f)
                    .addRenderActor(offset)
                    .addMotion(0, upwardsMotion, 0f)
                    .setLifetime(15)
                    .setLifeDelay(lifeDelay)
                    .spawn(level, position);
        }
        long gameTime = level.getGameTime();
        float time = 16;
        for (int i = 0; i < 8; i++) {
            var offsetPosition = VecHelper.rotatingRadialOffset(position, 0.9f, i, 8, gameTime, time);
            offsetPosition = offsetPosition.add(0, (Math.cos(((gameTime + i * 480) % time) / time) * 0.25f) + 0.5f, 0);
            offset = behavior.apply(offsetPosition.subtract(position));
            float upwardsVelocity = 0.2f;
            for (int j = 0; j < 3; j++) {
                var lightSpecs = SparkParticleEffects.spiritMotionSparks(level, offsetPosition, colorData.getColor(), new WorldParticleOptions(MalumParticles.MOTION_LINES));
                float velocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.05f, 0.1f);
                var motion = offsetPosition.subtract(position).normalize().scale(velocity);
                int lifeDelay = j * 3;
                lightSpecs.getBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .addRenderActor(offset)
                        .multiplyLifetime(1.25f)
                        .setMotion(motion)
                        .addMotion(0, upwardsVelocity, 0)
                        .setLifeDelay(lifeDelay)
                        .setLengthData(GenericParticleData.create(2f, 0.5f).setEasing(Easing.EXPO_OUT).build())
                        .setTransparencyData(GenericParticleData.create(0.6f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 3f, 4f)));
                lightSpecs.getBloomBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .addRenderActor(offset)
                        .multiplyLifetime(0.75f)
                        .setMotion(motion)
                        .addMotion(0, upwardsVelocity, 0)
                        .setLifeDelay(lifeDelay)
                        .setScaleData(GenericParticleData.create(1f, 0.25f).setEasing(Easing.EXPO_OUT).build())
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build());
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void entropyChargeDetonates(Level level, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        var random = level.random;
        var position = positionData.getAsVector();

        for (int i = 0; i < 5; i++) {
            int lifeDelay = i * 2;
            float scale = 6f + i * 1f;
            cultistSigil(level, colorData)
                    .setSpinData(SpinParticleData.createRandomDirection(random, 0.3f, 0).setEasing(Easing.EXPO_OUT).build())
                    .modifyScaleData(d -> d.multiplyValue(scale))
                    .setLifetime(14)
                    .setLifeDelay(lifeDelay)
                    .spawn(level, position);
        }

        spawnExplosionSparks(level, position, colorData, 24, 3f);
        float scaleMultiplier = (float) (1.5f + Math.pow(random.nextFloat(), 2) * 0.75f);
        WorldParticleBuilder.create(MalumParticles.GIANT_GLOWING_STAR.get())
                .setScaleData(GenericParticleData.create(5f * scaleMultiplier, 0.5f, 0).setEasing(Easing.EXPO_OUT, Easing.SINE_IN))
                .setTransparencyData(GenericParticleData.create(0.9f, 0).setEasing(Easing.CIRC_IN))
                .setSpinData(SpinParticleData.createRandomDirection(random, nextFloat(random, 0.05f, 0.1f)).randomSpinOffset(random))
                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                .setRandomMotion(0.02f, 0.02f)
                .setColorData(colorData.getColor())
                .setRandomOffset(0.6f)
                .setLifetime(12)
                .enableNoClip()
                .repeat(level, position, 3);
    }

    public static void cardinalFiresDetonationBlast(Level level, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, CardinalCultist cardinalCultist, EntropyChargeProjectile entropyCharge) {
        var random = level.random;
        var position = positionData.getAsVector();

        Function<Vec3, Consumer<LodestoneWorldParticle>> behavior = initialOffset -> p -> {
            var targetPosition = cardinalCultist.getDetonationBlastPos(p.partialTicksCache);
            p.setParticlePosition(targetPosition.add(initialOffset).add(p.getInterpolatedTravelledDistance()));
        };
        var direction = entropyCharge.getEyePosition().subtract(cardinalCultist.getEyePosition()).normalize();
        var offset = behavior.apply(Vec3.ZERO);
        for (int i = 0; i < 5; i++) {
            float scale = 1.5f + i * 0.25f;
            cultistSigil(level, colorData)
                    .setSpinData(SpinParticleData.createRandomDirection(random, 0.7f, 0).setEasing(Easing.EXPO_OUT).build())
                    .modifyScaleData(d -> d.multiplyValue(scale))
                    .setBehavior(DirectionalParticleBehavior.directional(direction))
                    .setMotion(direction.scale(0.1f))
                    .setFriction(0.9f)
                    .addRenderActor(offset)
                    .setLifetime(8)
                    .setLifeDelay(i)
                    .spawn(level, position);
        }

        float scaleMultiplier = (float) (1.5f + Math.pow(random.nextFloat(), 2) * 0.75f);
        WorldParticleBuilder.create(MalumParticles.GIANT_GLOWING_STAR.get())
                .setScaleData(GenericParticleData.create(5f * scaleMultiplier, 0.5f, 0).setEasing(Easing.EXPO_OUT, Easing.SINE_IN))
                .setTransparencyData(GenericParticleData.create(0.9f, 0).setEasing(Easing.CIRC_IN))
                .setSpinData(SpinParticleData.createRandomDirection(random, nextFloat(random, 0.05f, 0.1f)).randomSpinOffset(random))
                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                .setRandomMotion(0.02f, 0.02f)
                .setColorData(colorData.getColor())
                .setRandomOffset(0.6f)
                .setLifetime(12)
                .enableNoClip()
                .repeat(level, position, 3);

        float yRot = ((float) (Mth.atan2(direction.x, direction.z) * (double) (180F / (float) Math.PI)));
        float yaw = (float) Math.toRadians(yRot);
        Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
        Vec3 up = left.cross(direction);
        for (int i = 0; i < 8; i++) {
            float spread = Easing.SINE_IN_OUT.asWeighedRandom(random, 0f, 0.1f);
            float speed = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 2f);
            float distance = Easing.SINE_IN_OUT.asWeighedRandom(random, 3f, 5f);
            float angle = i / 8f * 6.28f;

            var particleDirection = direction
                    .add(left.scale(Math.sin(angle) * spread))
                    .add(up.scale(Math.cos(angle) * spread))
                    .normalize();
            var particleVelocity = particleDirection.scale(speed);
            var particlePosition = position.add(particleDirection.scale(distance));
            offset = behavior.apply(particlePosition.subtract(position));
            for (int j = 0; j < 3; j++) {
                var lightSpecs = SparkParticleEffects.spiritMotionSparks(level, particlePosition, colorData.getColor(), new WorldParticleOptions(MalumParticles.MOTION_LINES));
                int lifeDelay = j * 2;
                lightSpecs.getBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .addRenderActor(offset)
                        .multiplyLifetime(0.6f)
                        .setMotion(particleVelocity)
                        .setLifeDelay(lifeDelay)
                        .setLengthData(GenericParticleData.create(4f, 0.5f).setEasing(Easing.EXPO_OUT).build())
                        .setTransparencyData(GenericParticleData.create(0.6f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 3f, 4f)));
                lightSpecs.getBloomBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .addRenderActor(offset)
                        .multiplyLifetime(0.4f)
                        .setMotion(particleVelocity)
                        .setLifeDelay(lifeDelay)
                        .setScaleData(GenericParticleData.create(2f, 0.25f).setEasing(Easing.EXPO_OUT).build())
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build());
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void cardinalFiresRetaliationBlast(Level level, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, CardinalCultist cardinalCultist, Vec3 direction) {
        var random = level.random;
        var position = positionData.getAsVector();

        Function<Vec3, Consumer<LodestoneWorldParticle>> behavior = initialOffset -> p -> {
            var targetPosition = cardinalCultist.getRetaliationBlastPos(p.partialTicksCache);
            p.setParticlePosition(targetPosition.add(initialOffset).add(p.getInterpolatedTravelledDistance()));
        };
        var offset = behavior.apply(Vec3.ZERO);
        for (int i = 0; i < 3; i++) {
            float scale = 1f + i * 0.25f;
            cultistSigil(level, colorData)
                    .setSpinData(SpinParticleData.createRandomDirection(random, 0.7f, 0).setEasing(Easing.EXPO_OUT).build())
                    .modifyScaleData(d -> d.multiplyValue(scale))
                    .setBehavior(DirectionalParticleBehavior.directional(direction))
                    .setMotion(direction.scale(0.05f))
                    .setFriction(0.9f)
                    .addRenderActor(offset)
                    .setLifetime(8)
                    .setLifeDelay(i)
                    .spawn(level, position);
        }

        float scaleMultiplier = (float) (1.5f + Math.pow(random.nextFloat(), 2) * 0.75f);
        WorldParticleBuilder.create(MalumParticles.GIANT_GLOWING_STAR.get())
                .setScaleData(GenericParticleData.create(3f * scaleMultiplier, 0.5f, 0).setEasing(Easing.EXPO_OUT, Easing.SINE_IN))
                .setTransparencyData(GenericParticleData.create(0.9f, 0).setEasing(Easing.CIRC_IN))
                .setSpinData(SpinParticleData.createRandomDirection(random, nextFloat(random, 0.05f, 0.1f)).randomSpinOffset(random))
                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                .setRandomMotion(0.02f, 0.02f)
                .setColorData(colorData.getColor())
                .setRandomOffset(0.6f)
                .setLifetime(12)
                .enableNoClip()
                .repeat(level, position, 3);

        float yRot = ((float) (Mth.atan2(direction.x, direction.z) * (double) (180F / (float) Math.PI)));
        float yaw = (float) Math.toRadians(yRot);
        Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
        Vec3 up = left.cross(direction);
        for (int i = 0; i < 16; i++) {
            float spread = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.1f, 0.5f);
            float speed = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 0.8f);
            float distance = Easing.SINE_IN_OUT.asWeighedRandom(random, 2f, 4f);
            float angle = i / 16f * 6.28f;

            var particleDirection = direction
                    .add(left.scale(Math.sin(angle) * spread))
                    .add(up.scale(Math.cos(angle) * spread))
                    .normalize();
            var particleVelocity = particleDirection.scale(speed);
            var particlePosition = position.add(particleDirection.scale(distance));
            offset = behavior.apply(particlePosition.subtract(position));
            for (int j = 0; j < 2; j++) {
                var lightSpecs = SparkParticleEffects.spiritMotionSparks(level, particlePosition, colorData.getColor(), new WorldParticleOptions(MalumParticles.MOTION_LINES));
                int lifeDelay = j * 2;
                lightSpecs.getBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .addRenderActor(offset)
                        .multiplyLifetime(0.5f)
                        .setMotion(particleVelocity)
                        .setLifeDelay(lifeDelay)
                        .setLengthData(GenericParticleData.create(2f, 0.5f).setEasing(Easing.EXPO_OUT).build())
                        .setTransparencyData(GenericParticleData.create(0.6f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 3f, 4f)));
                lightSpecs.getBloomBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .addRenderActor(offset)
                        .multiplyLifetime(0.25f)
                        .setMotion(particleVelocity)
                        .setLifeDelay(lifeDelay)
                        .setScaleData(GenericParticleData.create(1f, 0.25f).setEasing(Easing.EXPO_OUT).build())
                        .setTransparencyData(GenericParticleData.create(0.05f, 0.35f, 0f).build());
                lightSpecs.spawnParticles();
            }
        }
    }

    public static void cardinalFiresImmolationBlast(Level level, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, CardinalCultist cardinalCultist) {
        var random = level.random;
        var position = positionData.getAsVector();

        for (int i = 0; i < 7; i++) {
            float scale = 7f + i;
            cultistSigil(level, colorData)
                    .setSpinData(SpinParticleData.createRandomDirection(random, 0.7f, 0).setEasing(Easing.EXPO_OUT).build())
                    .modifyScaleData(d -> d.multiplyValue(scale))
                    .setLifetime(12)
                    .setLifeDelay(i)
                    .spawn(level, position)
                    .setBehavior(DirectionalParticleBehavior.directional(new Vec3(0, 1, 0)))
                    .spawn(level, position);
        }

        spawnExplosionSparks(level, position, colorData, 8, 2f);
        spawnExplosionSparks(level, position, colorData, 64, 5f);
        float scaleMultiplier = (float) (1.5f + Math.pow(random.nextFloat(), 2) * 0.75f);
        WorldParticleBuilder.create(MalumParticles.GIANT_GLOWING_STAR.get())
                .setScaleData(GenericParticleData.create(12f * scaleMultiplier, 0.5f, 0).setEasing(Easing.EXPO_OUT, Easing.SINE_IN))
                .setTransparencyData(GenericParticleData.create(0.9f, 0).setEasing(Easing.CIRC_IN))
                .setSpinData(SpinParticleData.createRandomDirection(random, nextFloat(random, 0.05f, 0.1f)).randomSpinOffset(random))
                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                .setRandomMotion(0.02f, 0.02f)
                .setColorData(colorData.getColor())
                .setRandomOffset(0.6f)
                .setLifetime(12)
                .enableNoClip()
                .repeat(level, position, 3)
                .setBehavior(DirectionalParticleBehavior.directional(new Vec3(0, 1, 0)))
                .repeat(level, position, 3);
    }

    public static void spawnExplosionSparks(Level level, Vec3 position, MalumNetworkedParticleEffectColorData colorData, int amount, float speed) {
        var random = level.random;
        for (int i = 0; i < amount; i++) {
            var color = colorData.getColor();
            float lifetimeMultiplier = Easing.SINE_IN_OUT.asWeighedRandom(random, 2f, 2.5f);
            float gravityStrength = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.03f, 0.06f);
            double horizontalAngle = random.nextDouble() * Math.PI * 2;
            double x = Math.sin(horizontalAngle);
            double y = Mth.nextFloat(random, 0.35f, 1);
            double z = Math.cos(horizontalAngle);
            Vec3 direction = new Vec3(x, y, z);
            Vec3 motion = direction.scale(speed * Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 1.25f));
            Vec3 spawnPosition = position.add(direction.scale(0.25f));
            Consumer<LodestoneWorldParticle> sparkBehavior = p -> {
                Vec3 velocity = p.getParticleSpeed().scale(0.75f);
                if (velocity.equals(Vec3.ZERO)) {
                    velocity = p.getParticleSpeed();
                }
                p.setParticleSpeed(velocity.x, (velocity.y - gravityStrength) * 0.98f, velocity.z);
                if (p.getAge() < p.getLifetime() * 0.7f) {
                    if (level.getGameTime() % 2 == 0) {
                        var lightSpecs = spiritLightSpecs(level, p.getParticlePosition(), p.colorData);
                        lightSpecs.getBuilder()
                                .setTransparencyData(GenericParticleData.create(0.9f))
                                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                                .multiplyLifetime(lifetimeMultiplier / 2f)
                                .enableForcedSpawn();
                        lightSpecs.getBloomBuilder()
                                .setTransparencyData(GenericParticleData.create(0.9f))
                                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                                .multiplyLifetime(lifetimeMultiplier / 4f);
                        lightSpecs.spawnParticles();
                    }
                }
            };
            float scalar = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.8f, 1.1f);
            var sparks = SparkParticleEffects.spiritMotionSparks(level, spawnPosition, color).act(b -> b.getParticleOptions().setBehavior(SparkParticleBehavior.sparkBehavior()));
            sparks.getBuilder()
                    .setLengthData(GenericParticleData.create(3f * scalar, 0.75f * scalar, 0f).setEasing(Easing.QUARTIC_OUT, Easing.SINE_IN_OUT))
                    .setScaleData(GenericParticleData.create(0.4f * scalar, 0.2f * scalar, 0f).setEasing(Easing.SINE_IN, Easing.QUAD_IN))
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                    .setTransparencyData(GenericParticleData.create(0.9f))
                    .multiplyLifetime(lifetimeMultiplier)
                    .addTickActor(sparkBehavior)
                    .enableForcedSpawn()
                    .setMotion(motion);
            sparks.getBloomBuilder()
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                    .setTransparencyData(GenericParticleData.create(0.9f))
                    .modifyScaleData(d -> d.multiplyValue(2f))
                    .multiplyLifetime(lifetimeMultiplier)
                    .addTickActor(sparkBehavior)
                    .setMotion(motion);
            sparks.spawnParticles();
        }
    }

    public static WorldParticleBuilder cultistSigil(Level level, MalumNetworkedParticleEffectColorData colorData) {
        return cultistSigil(level, colorData.getColor());
    }

    public static WorldParticleBuilder cultistSigil(Level level, ColorParticleData colorData) {
        RandomSource rand = level.random;
        var scaleData = GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.5f, 0.6f), 0.5f)
                .setEasing(Easing.SINE_IN)
                .setCoefficient(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1f, 1.25f)).build();
        return WorldParticleBuilder.create(MalumParticles.CULTIST_SIGIL.get())
                .setTransparencyData(GenericParticleData.create(0.95f, 0.7f).setEasing(Easing.SINE_IN_OUT).build())
                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                .setScaleData(scaleData)
                .setColorData(colorData)
                .setLifetime(35)
                .enableNoClip()
                .setFriction(0.98f);
    }
}
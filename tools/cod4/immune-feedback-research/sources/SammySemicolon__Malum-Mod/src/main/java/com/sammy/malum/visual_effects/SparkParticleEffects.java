package com.sammy.malum.visual_effects;

import com.sammy.malum.client.*;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import com.sammy.malum.registry.common.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.registry.common.particle.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;

import java.util.function.*;

import static net.minecraft.util.Mth.*;

public class SparkParticleEffects {

    public static ParticleEffectSpawner spiritMotionSparks(Level level, Vec3 pos, SpiritLike spirit) {
        return spiritMotionSparks(level, pos, spirit, new WorldParticleOptions(MalumParticles.SPARK));
    }

    public static ParticleEffectSpawner spiritMotionSparks(Level level, Vec3 pos, ColorParticleDataWrapper colorData) {
        return spiritMotionSparks(level, pos, colorData, new WorldParticleOptions(MalumParticles.SPARK));
    }

    public static ParticleEffectSpawner spiritMotionSparks(Level level, Vec3 pos, SpiritLike spirit, WorldParticleOptions options) {
        return spiritMotionSparks(level, pos, options, o -> SpiritBasedParticleBuilder.createSpirit(o).setSpirit(spirit));
    }

    public static ParticleEffectSpawner spiritMotionSparks(Level level, Vec3 pos, ColorParticleDataWrapper colorData, WorldParticleOptions options) {
        return spiritMotionSparks(level, pos, options, o -> WorldParticleBuilder.create(o).setColorData(colorData));
    }

    public static ParticleEffectSpawner spiritMotionSparks(Level level, Vec3 pos, WorldParticleOptions options, Function<WorldParticleOptions, WorldParticleBuilder> builderSupplier) {
        var builder = builderSupplier.apply(options.setBehaviorIfDefault(SparkParticleBehavior.sparkBehavior()));
        var bloomBuilder = builderSupplier.apply(new WorldParticleOptions(LodestoneParticleTypes.WISP_PARTICLE));
        return spiritMotionSparks(level, pos, builder, bloomBuilder);
    }

    public static ParticleEffectSpawner spiritMotionSparks(Level level, Vec3 pos, WorldParticleBuilder builder, WorldParticleBuilder bloomBuilder) {
        RandomSource rand = level.getRandom();
        final SpinParticleData spinData = SpinParticleData.createRandomDirection(rand, nextFloat(rand, 0.05f, 0.1f)).randomSpinOffset(rand).build();
        final Consumer<LodestoneWorldParticle> slowDown = p -> p.setParticleSpeed(p.getParticleSpeed().scale(0.95f));
        int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(rand, 10, 20);
        final WorldParticleBuilder sparkParticleBuilder = builder
                .setLengthData(GenericParticleData.create(0.1f, 0.2f, 0f).setEasing(Easing.SINE_IN, Easing.SINE_IN_OUT).build())
                .setScaleData(GenericParticleData.create(0.1f, Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.2f, 0.3f), 0).build())
                .setTransparencyData(GenericParticleData.create(0.8f, 0f).build())
                .addTickActor(slowDown)
                .setLifetime(lifetime)
                .enableNoClip();
        final WorldParticleBuilder bloomParticleBuilder = SpiritLightSpecs.spiritBloom(level, bloomBuilder, lifetime).modifyScaleData(d -> d.multiplyValue(0.5f)).setSpinData(spinData).addTickActor(slowDown);
        return new ParticleEffectSpawner(level, pos, sparkParticleBuilder, bloomParticleBuilder);
    }
}
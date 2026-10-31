package com.sammy.malum.visual_effects;

import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import net.minecraft.client.particle.*;
import net.minecraft.util.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.registry.common.particle.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;

import java.util.function.*;

import static net.minecraft.util.Mth.*;

public class ItemCrumbleParticleEffects {

    public static ParticleEffectSpawner spawnItemCrumbs(Level level, Vec3 pos, ItemStack stack) {
        var rand = level.getRandom();
        final SpinParticleData spinData = SpinParticleData.createRandomDirection(rand, nextFloat(rand, 0.5f, 0.75f), 0).setCoefficient(0.6f).randomSpinOffset(rand).build();
        final Consumer<LodestoneWorldParticle> slowDown = p -> p.setParticleSpeed(p.getParticleSpeed().scale(0.925f));
        int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(rand, 30, 40);
        var crumbs = makeCrumbs(rand, stack, spinData, lifetime, slowDown);
        return new ParticleEffectSpawner(level, pos, crumbs);
    }

    public static ParticleEffectSpawner spawnGlowingItemCrumbs(Level level, Vec3 pos, ItemStack stack, SpiritArcanaType spiritType) {
        var rand = level.getRandom();
        final SpinParticleData spinData = SpinParticleData.createRandomDirection(rand, 0, nextFloat(rand, 0.5f, 0.75f), 0).setCoefficient(0.6f).randomSpinOffset(rand).build();
        final Consumer<LodestoneWorldParticle> slowDown = p -> p.setParticleSpeed(p.getParticleSpeed().scale(0.925f));
        int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(rand, 30, 40);
        var crumbs = makeCrumbs(rand, stack, spinData, lifetime, slowDown);
        var bloom = SpiritLightSpecs.spiritBloom(level, spiritType, lifetime).setSpinData(spinData).addTickActor(slowDown);
        return new ParticleEffectSpawner(level, pos, crumbs, bloom);
    }

    public static WorldParticleBuilder makeCrumbs(RandomSource rand, ItemStack stack, SpinParticleData spinData, int lifetime, Consumer<LodestoneWorldParticle> slowDown) {
        var options = new LodestoneItemCrumbsParticleOptions(LodestoneParticleTypes.ITEM_PARTICLE.get(), stack);
        return WorldParticleBuilder.create(options)
                .setSpinData(spinData)
                .setTransparencyData(GenericParticleData.create(0.5f, 1f, 0.25f).setEasing(Easing.EXPO_IN, Easing.SINE_IN_OUT).build())
                .setScaleData(GenericParticleData.create(0.05f, Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.06f, 0.07f), 0f).build())
                .setLifetime(lifetime)
                .setRenderType(ParticleRenderType.TERRAIN_SHEET)
                .addTickActor(slowDown);
    }
}

package com.sammy.malum.visual_effects.networked.spirit_mote;

import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectType;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;

import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.registry.common.particle.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectType;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.WorldParticleBuilder;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.GenericParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.SpinParticleData;

import java.util.function.Supplier;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;
import static net.minecraft.util.Mth.nextFloat;

public class SpiritMotePlaceParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public SpiritMotePlaceParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        var position = positionData.getAsBlockPos();
        var center = position.getCenter();
        for (int i = 0; i < 4; i++) {
            int xOffset = Mth.clamp(i%3, 0, 1);
            int zOffset = Mth.clamp((i-1)%4, 0, 1);
            float xMotion = (i%2) * (i > 1 ? 0.06f : -0.06f);
            float zMotion = ((i + 1) % 2) * (i > 1 ? -0.06f : 0.06f);
            var spirit = colorData.getSpirit();
            for (int j = 0; j < 20; j++) {
                int delay = j * 2;
                int upwards = j % 2;
                var offsetPosition = new Vec3(position.getX() + xOffset, position.getY() + upwards, position.getZ() + zOffset);
                var lightSpecs = spiritLightSpecs(level, offsetPosition, spirit);
                lightSpecs.getBuilder()
                        .setLifeDelay(delay)
                        .multiplyLifetime(2.5f)
                        .setMotion(xMotion, 0, zMotion)
                        .setTransparencyData(GenericParticleData.create(0.4f, 0.8f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)));
                lightSpecs.getBloomBuilder()
                        .setLifeDelay(delay)
                        .multiplyLifetime(1.5f)
                        .setMotion(xMotion, 0, zMotion)
                        .setTransparencyData(GenericParticleData.create(0.1f, 0.35f, 0f).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 1f)));
                lightSpecs.spawnParticles();
            }
        }
        final SpinParticleData spinData = SpinParticleData.createRandomDirection(random, nextFloat(random, 0.05f, 0.1f)).randomSpinOffset(random).build();
        WorldParticleBuilder.create(MalumParticles.GIANT_GLOWING_STAR.get())
                .setTransparencyData(GenericParticleData.create(0.9f, 0.07f, 0).setEasing(Easing.SINE_IN, Easing.CIRC_IN).build())
                .setLifetime(25)
                .setSpinData(spinData)
                .setScaleData(GenericParticleData.create(4f, 0.5f, 0).setEasing(Easing.EXPO_OUT, Easing.SINE_IN).build())
                .setColorData(colorData.getColor())
                .setRandomOffset(0.2f)
                .enableNoClip()
                .repeat(level, center, 3);
    }
}
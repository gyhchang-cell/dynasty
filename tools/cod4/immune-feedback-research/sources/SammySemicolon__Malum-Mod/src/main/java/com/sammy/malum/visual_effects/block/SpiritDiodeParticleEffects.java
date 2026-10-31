package com.sammy.malum.visual_effects.block;

import com.sammy.malum.registry.common.MalumParticles;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.ParticleEffectSpawner;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.WorldParticleBuilder;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.GenericParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.ColorParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.SpinParticleData;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.LodestoneWorldParticleRenderType;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.LodestoneWorldParticle;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

import java.util.function.Consumer;

public class SpiritDiodeParticleEffects {

    public static void openSpiritDiode(NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        ClientLevel level = Minecraft.getInstance().level;
        var random = level.random;

        for (int i = 0; i < 2; i++) {
            int lifeDelay = i * 3;
            float yVelocity = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.01f, 0.02f);
            var square = waveformSquare(level, positionData.getAsVector(), colorData.getColor());
            square.getBuilder()
                    .setBehavior(DirectionalParticleBehavior.directional())
                    .setLifeDelay(lifeDelay)
                    .setMotion(0, yVelocity, 0);
            square.spawnParticles();
        }
    }
    public static void closeSpiritDiode(NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData) {
        ClientLevel level = Minecraft.getInstance().level;
        var random = level.random;

        for (int i = 0; i < 4; i++) {
            int lifeDelay = i * 2;
            var square = waveformSquare(level, positionData.getAsVector(), colorData.getColor());
            square.getBuilder()
                    .setSpinData(SpinParticleData.createRandomDirection(random, 2f, 0).setEasing(Easing.EXPO_OUT).build())
                    .modifyScaleData(d -> d.multiplyValue(2f))
                    .setLifeDelay(lifeDelay);
            square.spawnParticles();
        }
    }


    public static ParticleEffectSpawner waveformSquare(Level level, Vec3 pos, ColorParticleData colorData) {
        RandomSource rand = level.random;
        final GenericParticleData scaleData = GenericParticleData.create(0.1f, Easing.SINE_IN_OUT.asWeighedRandom(rand, 0.5f, 0.6f), 0.5f)
                .setEasing(Easing.SINE_OUT, Easing.SINE_IN)
                .setCoefficient(Easing.SINE_IN_OUT.asWeighedRandom(rand, 1f, 1.25f)).build();
        final Consumer<LodestoneWorldParticle> behavior = p -> p.setParticleSpeed(p.getParticleSpeed().scale(0.99f));
        var squares = WorldParticleBuilder.create(MalumParticles.SQUARE.get())
                .setTransparencyData(GenericParticleData.create(0.7f, 0f).setEasing(Easing.SINE_IN_OUT).build())
                .setScaleData(scaleData)
                .setColorData(colorData)
                .setLifetime(15)
                .enableNoClip()
                .addTickActor(behavior);
        Consumer<WorldParticleBuilder> squareSpawner = b -> b
                .spawn(level, pos.x, pos.y, pos.z)
                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                .spawn(level, pos.x, pos.y, pos.z);

        return new ParticleEffectSpawner(squares, squareSpawner);
    }
}

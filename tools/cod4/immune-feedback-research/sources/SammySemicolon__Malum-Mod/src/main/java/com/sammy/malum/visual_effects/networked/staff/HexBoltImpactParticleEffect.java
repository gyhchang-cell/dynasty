package com.sammy.malum.visual_effects.networked.staff;

import com.sammy.malum.core.systems.spirit.*;
import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.world.level.Level;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.*;
import net.minecraft.nbt.*;
import net.minecraft.util.*;
import net.minecraft.world.phys.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectType;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;

public class HexBoltImpactParticleEffect extends BoltImpactParticleEffect {

    public HexBoltImpactParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, Vec3 projectileDirection, Vec3 left, Vec3 up) {
        Vec3 pos = positionData.getAsVector();
        for (int i = 0; i < 32; i++) {
            var color = colorData.getColor();
            float spread = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.1f, 0.5f);
            float speed = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.3f, 0.4f);
            float distance = Easing.SINE_IN_OUT.asWeighedRandom(random, 3f, 6f);
            float angle = i / 32f * (float) Math.PI * 2f;

            Vec3 direction = projectileDirection
                    .add(left.scale(Math.sin(angle) * spread))
                    .add(up.scale(Math.cos(angle) * spread))
                    .normalize().scale(speed);
            Vec3 spawnPosition = pos.add(direction.scale(distance));
            direction = direction.reverse();
            float lifetimeMultiplier = 0.7f;
            if (random.nextFloat() < 0.8f) {
                var lightSpecs = spiritLightSpecs(level, spawnPosition, color);
                lightSpecs.getBuilder()
                        .multiplyLifetime(lifetimeMultiplier)
                        .enableForcedSpawn()
                        .modifyScaleData(d -> d.multiplyValue(1.75f))
                        .setMotion(direction);
                lightSpecs.getBloomBuilder()
                        .multiplyLifetime(lifetimeMultiplier)
                        .setMotion(direction);
                lightSpecs.spawnParticles();
            }
            if (random.nextFloat() < 0.8f) {
                var sparks = SparkParticleEffects.spiritMotionSparks(level, spawnPosition, color);
                sparks.getBuilder()
                        .multiplyLifetime(lifetimeMultiplier)
                        .enableForcedSpawn()
                        .setMotion(direction.scale(1.5f))
                        .modifyScaleData(d -> d.multiplyValue(1.75f))
                        .modifyLengthData(d -> d.multiplyValue(3f));
                sparks.getBloomBuilder()
                        .multiplyLifetime(lifetimeMultiplier)
                        .setMotion(direction.scale(1.5f));
                sparks.spawnParticles();
            }
        }
    }
}
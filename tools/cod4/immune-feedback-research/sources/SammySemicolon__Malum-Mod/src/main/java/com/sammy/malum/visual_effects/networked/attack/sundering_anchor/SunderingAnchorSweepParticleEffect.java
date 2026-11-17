package com.sammy.malum.visual_effects.networked.attack.sundering_anchor;

import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

public class SunderingAnchorSweepParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public SunderingAnchorSweepParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        float angle = random.nextFloat() * 6.28f;
        float x = Mth.sin(angle);
        float z = Mth.cos(angle);
        Vec3 direction = new Vec3(x, 0, z);

        ParticleEffectSpawner slash = WeaponParticleEffects.spawnSlashParticle(level, positionData.getAsVector(), random.nextBoolean() ? MalumParticles.THIN_ROUNDABOUT_SLASH : MalumParticles.ROUNDABOUT_SLASH, colorData);
        int lifetime = Easing.SINE_IN_OUT.asWeighedRandom(random, 8, 12);
        int directionScalar = random.nextBoolean() ? -1 : 1;
        slash.getBuilder()
                .setSpinData(SpinParticleData.create(0).randomSpinOffset(random).build())
                .setLifetime(lifetime)
                .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 2f, 3f)).build())
                .setMotion(direction.scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.02f, 0.05f)))
                .setRandomOffset(0.5f)
                .setBehavior(PointyDirectionalParticleBehavior.pointyDirectional(direction.scale(directionScalar)));
        slash.spawnParticles();
        slash.getBuilder()
                .setTransparencyData(GenericParticleData.create(0.6f, 0.3f).build())
                .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 1.5f, 2f)).build())
                .setLifeDelay(lifetime);
        slash.spawnParticles();
        slash.getBuilder()
                .setTransparencyData(GenericParticleData.create(0.3f, 0f).build())
                .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 1.2f, 1.6f)).build())
                .setLifeDelay(lifetime*2);
        slash.spawnParticles();
    }
}
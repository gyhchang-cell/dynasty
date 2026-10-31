package com.sammy.malum.visual_effects.networked.attack.scythe;

import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.WeaponParticleEffectType;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

public class AscensionRadialSlashParticleEffect extends MalumNetworkedWeaponParticleEffectType<WeaponParticleEffectType.WeaponParticleEffectData> {

    public AscensionRadialSlashParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, WeaponParticleEffectData extraData) {
        var direction = extraData.getDirection();
        float yRot = ((float) (Mth.atan2(direction.x, direction.z) * (double) (180F / (float) Math.PI)));
        float yaw = (float) Math.toRadians(yRot);
        Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
        for(int i = 0; i < 3; i++) {
            final Vec3 pos = positionData.getAsVector();
            for (int j = 0; j < 16; j++) {
                float spinOffset = extraData.getSlashRotation() + Easing.SINE_IN_OUT.asWeighedRandom(random, -0.5f, 0.5f) + (extraData.isMirrored() ? 3.14f : 0);
                float slashAngle = (i*0.33f+j) / 16f * (float) Math.PI * 2f;
                var slashDirection = left.scale(Math.sin(slashAngle))
                        .add(direction.scale(Math.cos(slashAngle)))
                        .normalize();
                var slashPosition = pos.add(slashDirection.scale(0.14f));

                var slash = WeaponParticleEffects.spawnSlashParticle(level, slashPosition, MalumParticles.ROUNDABOUT_SLASH, colorData);
                slash.getBuilder()
                        .setSpinData(SpinParticleData.create(0).setSpinOffset(spinOffset).build())
                        .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 2.5f, 5f)).build())
                        .setMotion(slashDirection.scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.05f, 0.2f)).add(0, 0.2f, 0))
                        .setLifetime(12+i)
                        .setLifeDelay(i+j/4)
                        .setBehavior(PointyDirectionalParticleBehavior.pointyDirectional(slashDirection));
                slash.spawnParticles();
            }
            var slash = WeaponParticleEffects.spawnSlashParticle(level, pos, MalumParticles.ROUNDABOUT_SLASH, colorData);
            slash.getBuilder()
                    .setSpinData(SpinParticleData.create(0).setSpinOffset(i * 1.57f).build())
                    .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 4.5f, 5f)).build())
                    .setLifetime(12)
                    .setLifeDelay(i*2)
                    .setBehavior(DirectionalParticleBehavior.directional(new Vec3(0, 1, 0)));
            slash.spawnParticles();
        }
    }
}
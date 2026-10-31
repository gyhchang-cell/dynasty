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

public class AscensionUppercutParticleEffect extends MalumNetworkedWeaponParticleEffectType<WeaponParticleEffectType.WeaponParticleEffectData> {

    public AscensionUppercutParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, WeaponParticleEffectData extraData) {
        var direction = extraData.getDirection();
        float yRot = ((float) (Mth.atan2(direction.x, direction.z) * (double) (180F / (float) Math.PI)));
        float yaw = (float) Math.toRadians(yRot);
        Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
        Vec3 up = left.cross(direction);
        for(int i = 0; i < 6; i++) {
            float upwardsOffset = i*0.4f;
            float slashOffset = 2 - i*0.6f;
            for (int j = 0; j < 2; j++) {
                float spinOffset = extraData.getSlashRotation() + Easing.SINE_IN_OUT.asWeighedRandom(random, -0.25f, 0.25f) + (extraData.isMirrored() ? 3.14f : 0);

                var slashPosition = positionData.getAsVector().add(direction.scale(slashOffset)).add(up.scale(upwardsOffset));

                var slash = WeaponParticleEffects.spawnSlashParticle(level, slashPosition, MalumParticles.SLASH, colorData);
                slash.getBuilder()
                        .setSpinData(SpinParticleData.create(0).setSpinOffset(spinOffset).build())
                        .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 2.5f, 3f)).build())
                        .setMotion(direction.scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.2f, 0.4f)).add(0, 0.8f, 0))
                        .setLifetime(3+i)
                        .setLifeDelay(i/2)
                        .setBehavior(PointyDirectionalParticleBehavior.pointyDirectional(direction));
                slash.spawnParticles();
            }
        }
    }
}
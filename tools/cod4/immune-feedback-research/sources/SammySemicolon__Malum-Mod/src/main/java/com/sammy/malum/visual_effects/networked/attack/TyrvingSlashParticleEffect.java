package com.sammy.malum.visual_effects.networked.attack;

import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.WeaponParticleEffectType;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

public class TyrvingSlashParticleEffect extends MalumNetworkedWeaponParticleEffectType<WeaponParticleEffectType.WeaponParticleEffectData> {

    public TyrvingSlashParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, WeaponParticleEffectData extraData) {
        float offsetBase = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.4f, 0.8f) * (random.nextBoolean() ? 1 : -1) + (extraData.isMirrored() ? 3.14f : 0);
        for (int i = 0; i < 8; i++) {
            ParticleEffectSpawner slash;
            if (i >= 6) {
                slash = WeaponParticleEffects.spawnSlashParticle(level, positionData.getAsVector(), MalumParticles.SLASH, ColorParticleData.create(0.15f, 0.05f, 0.1f).build());
                slash.getBuilder().setRenderType(LodestoneWorldParticleRenderType.TRANSPARENT);
            } else {
                slash = WeaponParticleEffects.spawnSlashParticle(level, positionData.getAsVector(), MalumParticles.SLASH, colorData);
            }
            var direction = extraData.getDirection();
            float spinOffset = extraData.getSlashRotation() + (i % 2 == 0 ? 1 : -1) * offsetBase;
            int lifeDelay = (i % 2 == 0 ? 3 : 0);
            slash.getBuilder()
                    .setSpinData(SpinParticleData.create(0).setSpinOffset(spinOffset).build())
                    .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 1f, 2f)).build())
                    .setMotion(direction.scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 0.7f)))
                    .setLifeDelay(lifeDelay)
                    .setBehavior(PointyDirectionalParticleBehavior.pointyDirectional(direction));
            slash.spawnParticles();
        }
    }
}
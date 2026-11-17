package com.sammy.malum.visual_effects.networked.attack.scythe;

import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

public class ScytheSlashParticleEffect extends MalumNetworkedWeaponParticleEffectType<WeaponParticleEffectType.WeaponParticleEffectData> {

    public ScytheSlashParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, WeaponParticleEffectData extraData) {
        var slash = WeaponParticleEffects.spawnSlashParticle(level, positionData.getAsVector(), MalumParticles.SLASH, colorData);
        var direction = extraData.getDirection();
        slash.getBuilder()
                .setSpinData(SpinParticleData.create(0).setSpinOffset(extraData.getSlashRotation()+(extraData.isMirrored()?3.14f:0)).build())
                .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 2f, 3f)).build())
                .setMotion(direction.scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.3f, 0.4f)))
                .setBehavior(PointyDirectionalParticleBehavior.pointyDirectional(direction));
        slash.spawnParticles();
    }
}
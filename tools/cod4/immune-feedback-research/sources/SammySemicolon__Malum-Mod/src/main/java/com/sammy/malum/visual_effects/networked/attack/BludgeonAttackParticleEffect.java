package com.sammy.malum.visual_effects.networked.attack;

import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.core.*;
import net.minecraft.core.particles.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.phys.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.*;
import team.lodestar.lodestone.systems.network.particle.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.spin.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

public class BludgeonAttackParticleEffect extends MalumNetworkedWeaponParticleEffectType<WeaponParticleEffectType.WeaponParticleEffectData> {

    public BludgeonAttackParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, WeaponParticleEffectData extraData) {
        var position = positionData.getAsVector();
        var slam = WeaponParticleEffects.spawnSlamParticle(level, position, MalumParticles.SLAM, colorData);
        var direction = extraData.getDirection();
        slam.getBuilder()
                .setSpinData(SpinParticleData.create(0).setSpinOffset(extraData.getSlashRotation()).build())
                .setScaleData(GenericParticleData.create(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 0.8f)).build())
                .setMotion(direction.scale(Easing.SINE_IN_OUT.asWeighedRandom(random, 1.4f, 2f)))
                .setBehavior(DirectionalParticleBehavior.directional(direction));
        slam.spawnParticles();

        var pos = BlockPos.containing(Math.round(position.x), Math.round(position.y)-3, Math.round(position.z));
        var state = level.getBlockState(pos);
        var particle = new BlockParticleOption(ParticleTypes.BLOCK, state);

        double radialOffset = 0.2f;
        float forwardsOffset = 2f;
        for (int i = 0; i < 40; i++) {
            double xPos = position.x + radialOffset * Math.cos(i) + random.nextGaussian() / 2.0 + direction.x * forwardsOffset;
            double yPos = position.y - 0.5f + direction.y * forwardsOffset;
            double zPos = position.z + radialOffset * Math.sin(i) + random.nextGaussian() / 2.0 + direction.z * forwardsOffset;
            double xVelocity = random.nextGaussian() * 0.075F;
            double yVelocity = random.nextGaussian() * 0.01F;
            double zVelocity = random.nextGaussian() * 0.075F;
            level.addParticle(particle, xPos, yPos, zPos, xVelocity, yVelocity, zVelocity);
        }
        
    }
}
package com.sammy.malum.visual_effects.block;

import com.sammy.malum.common.block.curiosities.artifice.elemental_artifice.aerial.GustIgniterBlockEntity;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.networked.*;
import com.sammy.malum.visual_effects.networked.wind_gust.*;
import net.minecraft.util.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.rendering.particle.standard.builder.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;

public class WindTunnelParticleEffects {

//    private static final InstanceFormat POS_COLOR = new InstanceFormat.Builder()
//            .add(StandardInstanceWriters.POSITION)
//            .add(StandardInstanceWriters.COLOR)
//            .add(StandardInstanceWriters.MODEL_MATRIX)
//            .build();
//
//    private static final ParticleSpec SPEC2 = ParticleBuilder.create()
//            .withVisual(LodestoneParticleVisuals.QUAD, v -> {
//                v.renderType(LodestoneRenderTypes.DEBUG_POS_TEX);
//                v.instanceFormat(POS_COLOR);
//            })
//            .build();


    public static void passiveWindTunnelParticles(GustIgniterBlockEntity igniter) {
//        var connectionData = igniter.getConnectionData();
//        if (connectionData == null) {
//            return;
//        }
//        var array = connectionData.getArray();
//        Set<BlockPos> blocks = array.getConnectedBlocks();
//        Direction direction = array.getSharedDirection();
//        for (BlockPos block : blocks) {
//            BlockPos offset = block.relative(direction);
//            var profile = CuboidDistributionProfile.centeredOn(offset, 0.5f);
//            var chain = new ParticleSpawnContextChain(profile);
//            var ctx = new ParticleSpawnContext().lifetime(20);
//            ParticleHandler.spawn(SPEC2, chain.apply(ctx));
//        }
    }

    public static void windTrailParticles(Level level, RandomSource random, Entity target, Vec3 pos, MalumNetworkedParticleEffectColorData colorData, WindTrailParticleEffect.WindTrailParticleEffectData extraData) {
        int delay = extraData.delay();
        int duration = extraData.duration();
        var transparencyData = GenericParticleData.create(1f, 0.4f).setEasing(Easing.QUAD_IN).build();
        var builder = WorldParticleBuilder.create(MalumParticles.MOTION_LINES.get())
                .setBehavior(SparkParticleBehavior.sparkBehavior())
                .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                .setScaleData(GenericParticleData.create(1f, 0f))
                .setLengthData(GenericParticleData.create(0.75f))
                .setTransparencyData(transparencyData)
                .setColorData(colorData.getColor())
                .enableForcedSpawn()
                .setLifetime(30)
                .enableNoClip();
        for (int i = 0; i < duration; i++) {
            builder.setLifeDelay(delay + i)
                    .clearSpawnActors()
                    .addSpawnActor(p -> {
                        float offsetScale = 0.2f;
                        Vec3 offset = new Vec3(
                                Easing.SINE_IN_OUT.asWeighedRandom(random, -offsetScale, offsetScale),
                                Easing.SINE_IN_OUT.asWeighedRandom(random, -offsetScale, offsetScale),
                                Easing.SINE_IN_OUT.asWeighedRandom(random, -offsetScale, offsetScale)
                        );
                        var position = target.position().add(0, target.getBbHeight() / 2, 0).add(offset);
                        p.setParticlePosition(position);
                        p.setParticleSpeed(target.getDeltaMovement().scale(0.3f));
                    })
                    .spawn(level, pos);
        }
    }
}

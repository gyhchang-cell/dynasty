package com.sammy.malum.visual_effects;

import com.mojang.datafixers.util.Either;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.sap.SapCollectionParticleEffect;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Vec3i;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.LodestoneWorldParticleRenderType;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.LodestoneWorldParticle;

import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Supplier;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;

public class SapParticleEffects {

    public static void act(Level level, BlockPos blockPos, RandomSource random, MalumNetworkedParticleEffectColorData colorData, Direction direction, int trackedEntity) {
        Entity entity = level.getEntity(trackedEntity);
        if (entity == null) {
            return;
        }

        var spawnPos = blockPos.getCenter().relative(direction, 0.5f);
        var normal = direction.getNormal();
        float yRot = ((float) (Mth.atan2(normal.getX(), normal.getZ()) * (double) (180F / (float) Math.PI)));
        float yaw = (float) Math.toRadians(yRot);
        var left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
        var up = left.cross(new Vec3(normal.getX(), normal.getY(), normal.getZ()));
        Consumer<LodestoneWorldParticle> tracking = p -> {
            var targetPos = entity.position().add(0, entity.getBbHeight() / 2f, 0);
            var toEntity = targetPos.subtract(p.getParticlePosition()).normalize();
            if (toEntity.length() < 0.2f) {
                return;
            }
            Vec3 addedVelocity = toEntity.scale((0.05f * toEntity.length()));
            p.setParticleSpeed(p.getParticleSpeed().add(addedVelocity).scale(0.95f));
        };
        var targetPos = entity.position().add(0, entity.getBbHeight() / 2f, 0);
        float offsetScale = 0.5f;
        for (int i = 0; i < 12; i++) {
            float angle = i / 12f * 6.28f;

            float leftOffset = Mth.sin(angle) * offsetScale;
            float upOffset = Mth.cos(angle) * offsetScale;

            var particlePosition = spawnPos.add(left.scale(leftOffset)).add(up.scale(upOffset));
            var particleMotion = targetPos.subtract(particlePosition).normalize();
            var targetPosition = spawnPos.add(particleMotion.scale(offsetScale));
            var actualMotion = targetPosition.subtract(particlePosition).normalize().scale(0.01f);
            var lightSpecs = spiritLightSpecs(level, particlePosition, colorData.getColor());
            lightSpecs.getBuilder()
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                    .addTickActor(tracking)
                    .setMotion(actualMotion)
                    .setLifeDelay(i/2)
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 1.5f, 2f)));
            lightSpecs.getBloomBuilder()
                    .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                    .addTickActor(tracking)
                    .setMotion(actualMotion)
                    .setLifeDelay(i/2)
                    .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 1.5f)));
            lightSpecs.spawnParticles();
        }
    }
}

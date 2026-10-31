package com.sammy.malum.visual_effects.networked.staff;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.registry.common.particle.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.data.color.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.render_types.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.behaviors.*;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.options.*;

import java.awt.*;
import java.util.*;
import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;

public class UnwindingChaosChargeParticleEffect extends MalumNetworkedParticleEffectType<UnwindingChaosChargeParticleEffect.UnwindingChaosChargeEffectData> {

    public record UnwindingChaosChargeEffectData(int entityId) implements NetworkedParticleEffectExtraData {
        public static final Codec<UnwindingChaosChargeEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.INT.fieldOf("entityId").forGetter(UnwindingChaosChargeEffectData::entityId)
        ).apply(instance, UnwindingChaosChargeEffectData::new));

        public static final StreamCodec<ByteBuf, UnwindingChaosChargeEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }

    public UnwindingChaosChargeParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(UnwindingChaosChargeEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, UnwindingChaosChargeEffectData extraData) {
        final Entity entity = level.getEntity(extraData.entityId);
        if (entity != null) {
            var smokeColor = new Color(45, 15, 15);
            long gameTime = level.getGameTime();
            var pos = positionData.getAsVector();
            var direction = pos.subtract(entity.position()).normalize();
            float yRot = ((float) (Mth.atan2(direction.x, direction.z) * (double) (180F / (float) Math.PI)));
            float yaw = (float) Math.toRadians(yRot);
            Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
            Vec3 up = left.cross(direction);

            Consumer<LodestoneWorldParticle> behavior = p -> {
                Vec3 distance = entity.position().add(0, entity.getBbHeight() / 2f, 0).subtract(p.getParticlePosition());
                if (distance.length() == 0) {
                    distance = new Vec3(0, 0.02f, 0);
                }
                float delta = Math.max(p.getAge() / (float) p.getLifetime(), 0);
                float lerp = Easing.QUINTIC_IN_OUT.lerp(delta, 0.05f, 0.5f);
                float velocity = (float) Easing.CIRC_IN.lerp(delta, 0.05f, 0.2f + distance.length() * 1.2f);
                final Vec3 speed = p.getParticleSpeed().lerp(distance.normalize().scale(velocity), lerp);
                p.setParticleSpeed(speed);
            };

            for (int i = 0; i < 16; i++) {
                SpiritArcanaType cyclingSpiritType = colorData.getSpirit();
                float spread = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.5f, 0.6f);
                float speed = Easing.SINE_IN_OUT.asWeighedRandom(random, 0.6f, 0.8f);
                float angle = i / 16f * (float) Math.PI * 2f;
                Vec3 particleDirection = direction
                        .add(left.scale(Math.sin(angle) * spread))
                        .add(up.scale(Math.cos(angle) * spread))
                        .normalize().scale(speed);
                Vec3 particlePosition = pos.add(particleDirection.scale(2f));
                var lightSpecs = spiritLightSpecs(level, particlePosition, cyclingSpiritType, new WorldParticleOptions(MalumParticles.SPARK.get()));
                var transparencyData = GenericParticleData.create(0.4f, 0.8f, 0f).setEasing(Easing.SINE_IN_OUT, Easing.EXPO_IN_OUT).build();
                int lifeDelay = i * 2;
                int lifetime = 20;
                lightSpecs.getBuilder()
                        .setBehavior(SparkParticleBehavior.sparkBehavior())
                        .setLengthData(GenericParticleData.create(0.2f, 2f, 0f).setEasing(Easing.SINE_IN, Easing.SINE_IN_OUT).build())
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 2, 2.5f)))
                        .modifyColorData(c -> c.multiplyCoefficient(0.5f))
                        .setTransparencyData(transparencyData)
                        .setLifeDelay(lifeDelay)
                        .setLifetime(lifetime)
                        .addTickActor(behavior);
                lightSpecs.getBloomBuilder()
                        .setTransparencyData(transparencyData)
                        .setLifeDelay(lifeDelay)
                        .setLifetime(lifetime)
                        .addTickActor(behavior)
                        .modifyColorData(c -> c.multiplyCoefficient(0.5f))
                        .modifyScaleData(d -> d.multiplyValue(Easing.SINE_IN_OUT.asWeighedRandom(random, 0.7f, 1.1f)))
                        .modifyTransparencyData(d -> d.multiplyCoefficient(1.4f));
                lightSpecs.spawnParticles();

                lightSpecs = spiritLightSpecs(level, particlePosition, cyclingSpiritType, new WorldParticleOptions(LodestoneParticleTypes.WISP_PARTICLE.get()));
                transparencyData = GenericParticleData.create(1f, 0f).setCoefficient(1.5f).build();
                lightSpecs.getBuilder()
                        .setRenderType(LodestoneWorldParticleRenderType.LUMITRANSPARENT)
                        .setColorData(ColorParticleData.create(smokeColor).build())
                        .setTransparencyData(transparencyData)
                        .setLifeDelay(lifeDelay)
                        .addTickActor(behavior)
                        .setLifetime(lifetime);
                lightSpecs.spawnParticlesRaw();
            }
        }
    }
}
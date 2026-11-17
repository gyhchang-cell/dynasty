package com.sammy.malum.visual_effects.networked.staff;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectType;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;

import java.util.Optional;

public abstract class BoltImpactParticleEffect extends MalumNetworkedParticleEffectType<BoltImpactParticleEffect.BoltImpactEffectData> {

    public record BoltImpactEffectData(Vec3 direction) implements NetworkedParticleEffectExtraData {
        public static final Codec<BoltImpactEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Vec3.CODEC.fieldOf("direction").forGetter(BoltImpactEffectData::direction)
        ).apply(instance, BoltImpactEffectData::new));

        public static final StreamCodec<ByteBuf, BoltImpactEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }

    public BoltImpactParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(BoltImpactEffectData.STREAM_CODEC);
    }

    @Override
    public final void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, BoltImpactEffectData extraData) {
        Vec3 projectileDirection = extraData.direction();
        float yRot = ((float) (Mth.atan2(projectileDirection.x, projectileDirection.z) * (double) (180F / (float) Math.PI)));
        float yaw = (float) Math.toRadians(yRot);
        Vec3 left = new Vec3(-Math.cos(yaw), 0, Math.sin(yaw));
        Vec3 up = left.cross(projectileDirection);

        act(level, random, positionData, colorData, projectileDirection, left, up);
    }

    public abstract void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, Vec3 projectileDirection, Vec3 left, Vec3 up);
}
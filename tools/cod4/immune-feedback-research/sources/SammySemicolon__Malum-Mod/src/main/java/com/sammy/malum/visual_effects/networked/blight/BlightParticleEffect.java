package com.sammy.malum.visual_effects.networked.blight;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.*;
import net.minecraft.core.*;
import net.minecraft.network.codec.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;

public abstract class BlightParticleEffect extends MalumNetworkedParticleEffectType<BlightParticleEffect.BlightEffectData> {

    public record BlightEffectData(List<BlockPos> affectedArea) implements NetworkedParticleEffectExtraData {
        public static final Codec<BlightEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                BlockPos.CODEC.listOf().fieldOf("affectedArea").forGetter(BlightEffectData::affectedArea)
        ).apply(instance, BlightEffectData::new));

        public static final StreamCodec<ByteBuf, BlightEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }
    public BlightParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(BlightEffectData.STREAM_CODEC);
    }
}
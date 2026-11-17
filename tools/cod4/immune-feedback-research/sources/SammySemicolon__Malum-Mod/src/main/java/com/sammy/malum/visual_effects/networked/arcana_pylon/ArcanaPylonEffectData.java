package com.sammy.malum.visual_effects.networked.arcana_pylon;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import io.netty.buffer.*;
import net.minecraft.core.*;
import net.minecraft.network.codec.*;
import team.lodestar.lodestone.systems.network.particle.*;

public record ArcanaPylonEffectData(float intensity) implements NetworkedParticleEffectExtraData {
    public static final Codec<ArcanaPylonEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            Codec.FLOAT.fieldOf("intensity").forGetter(data -> data.intensity)
    ).apply(instance, ArcanaPylonEffectData::new));

    public static final StreamCodec<ByteBuf, ArcanaPylonEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
}
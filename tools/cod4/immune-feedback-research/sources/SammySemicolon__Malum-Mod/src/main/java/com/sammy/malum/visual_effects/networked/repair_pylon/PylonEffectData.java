package com.sammy.malum.visual_effects.networked.repair_pylon;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import io.netty.buffer.*;
import net.minecraft.core.*;
import net.minecraft.network.codec.*;
import team.lodestar.lodestone.systems.network.particle.*;

public record PylonEffectData(BlockPos holderPos) implements NetworkedParticleEffectExtraData {
    public static final Codec<PylonEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            BlockPos.CODEC.fieldOf("holderPos").forGetter(data -> data.holderPos)
    ).apply(instance, PylonEffectData::new));

    public static final StreamCodec<ByteBuf, PylonEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
}
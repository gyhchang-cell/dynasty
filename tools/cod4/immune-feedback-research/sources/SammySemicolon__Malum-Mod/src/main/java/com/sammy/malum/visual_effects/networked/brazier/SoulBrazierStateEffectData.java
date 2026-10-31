package com.sammy.malum.visual_effects.networked.brazier;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.sammy.malum.common.block.curiosities.sorcery.soul_brazier.SoulBrazierBlockEntity;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.StringRepresentable;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;

public record SoulBrazierStateEffectData(
        SoulBrazierBlockEntity.BrazierState state) implements NetworkedParticleEffectExtraData {
    public static final Codec<SoulBrazierStateEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            StringRepresentable.fromEnum(SoulBrazierBlockEntity.BrazierState::values).fieldOf("size").forGetter(SoulBrazierStateEffectData::state)
    ).apply(instance, SoulBrazierStateEffectData::new));

    public static final StreamCodec<ByteBuf, SoulBrazierStateEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
}

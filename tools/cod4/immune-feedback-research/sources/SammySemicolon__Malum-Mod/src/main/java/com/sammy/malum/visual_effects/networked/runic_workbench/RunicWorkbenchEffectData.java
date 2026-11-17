package com.sammy.malum.visual_effects.networked.runic_workbench;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import io.netty.buffer.*;
import net.minecraft.core.*;
import net.minecraft.network.codec.*;
import net.minecraft.world.item.*;
import team.lodestar.lodestone.systems.network.particle.*;

public record RunicWorkbenchEffectData(ItemStack primaryInput, ItemStack secondaryInput) implements NetworkedParticleEffectExtraData {
    public static final Codec<RunicWorkbenchEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            ItemStack.CODEC.fieldOf("primaryInput").forGetter(RunicWorkbenchEffectData::primaryInput),
            ItemStack.CODEC.fieldOf("secondaryInput").forGetter(RunicWorkbenchEffectData::secondaryInput)
    ).apply(instance, RunicWorkbenchEffectData::new));

    public static final StreamCodec<ByteBuf, RunicWorkbenchEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
}
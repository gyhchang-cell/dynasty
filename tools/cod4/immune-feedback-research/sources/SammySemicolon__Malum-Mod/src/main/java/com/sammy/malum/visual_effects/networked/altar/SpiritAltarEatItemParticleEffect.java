package com.sammy.malum.visual_effects.networked.altar;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.sammy.malum.common.block.curiosities.sorcery.spirit_altar.SpiritAltarBlockEntity;
import com.sammy.malum.common.block.storage.*;
import com.sammy.malum.visual_effects.block.SpiritAltarParticleEffects;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectType;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.BlockPos;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;

import java.util.*;

public class SpiritAltarEatItemParticleEffect extends MalumNetworkedParticleEffectType<SpiritAltarEatItemParticleEffect.SpiritAltarEatItemEffectData> {

    public record SpiritAltarEatItemEffectData(BlockPos holderPos, ItemStack stack) implements NetworkedParticleEffectExtraData {
        public static final Codec<SpiritAltarEatItemEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                BlockPos.CODEC.fieldOf("holderPos").forGetter(data -> data.holderPos),
                ItemStack.CODEC.fieldOf("stack").forGetter(data -> data.stack)
        ).apply(instance, SpiritAltarEatItemEffectData::new));

        public static final StreamCodec<ByteBuf, SpiritAltarEatItemEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }

    public SpiritAltarEatItemParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(SpiritAltarEatItemEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, SpiritAltarEatItemEffectData extraData) {
        if (!(level.getBlockEntity(positionData.getAsBlockPos()) instanceof SpiritAltarBlockEntity spiritAltar)) {
            return;
        }
        if (!(level.getBlockEntity(extraData.holderPos) instanceof IMalumSpecialItemAccessPoint holder)) {
            return;
        }
        SpiritAltarParticleEffects.eatItemParticles(level, spiritAltar, holder, colorData, extraData.stack);
    }
}
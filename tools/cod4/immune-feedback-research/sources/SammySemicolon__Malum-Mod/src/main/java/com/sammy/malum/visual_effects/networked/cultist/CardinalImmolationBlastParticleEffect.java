package com.sammy.malum.visual_effects.networked.cultist;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.sammy.malum.common.entity.mob.cultist.cardinal.CardinalCultist;
import com.sammy.malum.visual_effects.CultistParticleEffects;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectType;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;

import java.util.Optional;

public class CardinalImmolationBlastParticleEffect extends MalumNetworkedParticleEffectType<CardinalImmolationBlastParticleEffect.CardinalImmolationBlastParticleData> {

    public record CardinalImmolationBlastParticleData(int cardinalId) implements NetworkedParticleEffectExtraData {
        public static final Codec<CardinalImmolationBlastParticleData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.INT.fieldOf("cardinalId").forGetter(CardinalImmolationBlastParticleData::cardinalId)
        ).apply(instance, CardinalImmolationBlastParticleData::new));

        public static final StreamCodec<ByteBuf, CardinalImmolationBlastParticleData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);

    }

    public CardinalImmolationBlastParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(CardinalImmolationBlastParticleData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, CardinalImmolationBlastParticleData extraData) {
        if (level.getEntity(extraData.cardinalId) instanceof CardinalCultist cardinal) {
            CultistParticleEffects.cardinalFiresImmolationBlast(level, positionData, colorData, cardinal);
        }
    }
}
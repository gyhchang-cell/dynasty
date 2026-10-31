package com.sammy.malum.visual_effects.networked.cultist;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.sammy.malum.common.entity.mob.cultist.cardinal.projectile.EntropyChargeProjectile;
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

public class CardinalDetonationBlastParticleEffect extends MalumNetworkedParticleEffectType<CardinalDetonationBlastParticleEffect.CardinalDetonationBlastParticleData> {

    public record CardinalDetonationBlastParticleData(int cardinalId, int entropyChargeId) implements NetworkedParticleEffectExtraData {
        public static final Codec<CardinalDetonationBlastParticleData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.INT.fieldOf("cardinalId").forGetter(CardinalDetonationBlastParticleData::cardinalId),
                Codec.INT.fieldOf("entropyChargeId").forGetter(CardinalDetonationBlastParticleData::entropyChargeId)
        ).apply(instance, CardinalDetonationBlastParticleData::new));

        public static final StreamCodec<ByteBuf, CardinalDetonationBlastParticleData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);

    }

    public CardinalDetonationBlastParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(CardinalDetonationBlastParticleData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, CardinalDetonationBlastParticleData extraData) {
        if (level.getEntity(extraData.cardinalId) instanceof CardinalCultist cardinal) {
            if (level.getEntity(extraData.entropyChargeId) instanceof EntropyChargeProjectile entropyCharge) {
                CultistParticleEffects.cardinalFiresDetonationBlast(level, positionData, colorData, cardinal, entropyCharge);

            }
        }
    }
}
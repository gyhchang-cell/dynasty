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
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;

import java.util.Optional;

public class CardinalRetaliationBlastParticleEffect extends MalumNetworkedParticleEffectType<CardinalRetaliationBlastParticleEffect.CardinalRetaliationBlastParticleData> {

    public record CardinalRetaliationBlastParticleData(int cardinalId, Vec3 direction) implements NetworkedParticleEffectExtraData {
        public static final Codec<CardinalRetaliationBlastParticleData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.INT.fieldOf("cardinalId").forGetter(CardinalRetaliationBlastParticleData::cardinalId),
                Vec3.CODEC.fieldOf("direction").forGetter(CardinalRetaliationBlastParticleData::direction)
        ).apply(instance, CardinalRetaliationBlastParticleData::new));

        public static final StreamCodec<ByteBuf, CardinalRetaliationBlastParticleData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);

    }

    public CardinalRetaliationBlastParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(CardinalRetaliationBlastParticleData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, CardinalRetaliationBlastParticleData extraData) {
        if (level.getEntity(extraData.cardinalId) instanceof CardinalCultist cardinal) {
            CultistParticleEffects.cardinalFiresRetaliationBlast(level, positionData, colorData, cardinal, extraData.direction);
        }
    }
}
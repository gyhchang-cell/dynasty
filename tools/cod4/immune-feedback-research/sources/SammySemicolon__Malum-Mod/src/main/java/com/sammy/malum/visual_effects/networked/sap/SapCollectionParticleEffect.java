package com.sammy.malum.visual_effects.networked.sap;

import com.mojang.datafixers.util.Either;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.EitherCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.sammy.malum.visual_effects.SapParticleEffects;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectType;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.level.Level;
import net.minecraft.core.*;
import net.minecraft.util.*;
import net.minecraft.world.phys.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;
import team.lodestar.lodestone.modules.rendering.particle.standard.world.*;

import java.util.*;
import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;

public class SapCollectionParticleEffect extends MalumNetworkedParticleEffectType<SapCollectionParticleEffect.SapCollectionEffectData> {

    public record SapCollectionEffectData(Direction direction, int trackedEntity) implements NetworkedParticleEffectExtraData {
        public static final Codec<SapCollectionEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Direction.CODEC.fieldOf("direction").forGetter(SapCollectionEffectData::direction),
                Codec.INT.fieldOf("trackedEntity").forGetter(SapCollectionEffectData::trackedEntity)
        ).apply(instance, SapCollectionEffectData::new));

        public static final StreamCodec<ByteBuf, SapCollectionEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }

    public SapCollectionParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(SapCollectionEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, SapCollectionParticleEffect.SapCollectionEffectData extraData) {
        SapParticleEffects.act(level, positionData.getAsBlockPos(), random, colorData, extraData.direction, extraData.trackedEntity);
    }
}
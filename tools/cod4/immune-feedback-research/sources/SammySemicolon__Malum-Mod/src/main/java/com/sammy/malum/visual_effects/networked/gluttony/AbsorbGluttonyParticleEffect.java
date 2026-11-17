package com.sammy.malum.visual_effects.networked.gluttony;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import com.sammy.malum.visual_effects.networked.geas.*;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import team.lodestar.lodestone.systems.network.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;
import java.util.function.*;

public class AbsorbGluttonyParticleEffect extends MalumNetworkedParticleEffectType<AbsorbGluttonyParticleEffect.AbsorbGluttonyEffectData> {

    public record AbsorbGluttonyEffectData(float potency) implements NetworkedParticleEffectExtraData {
        public static final Codec<AbsorbGluttonyEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.FLOAT.fieldOf("potency").forGetter(AbsorbGluttonyEffectData::potency)
        ).apply(instance, AbsorbGluttonyEffectData::new));

        public static final StreamCodec<ByteBuf, AbsorbGluttonyEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }

    public AbsorbGluttonyParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectColorData>> getColorCodec() {
        return Optional.empty();
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(AbsorbGluttonyEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, AbsorbGluttonyEffectData extraData) {
        GluttonyParticleEffects.incrementGluttonyStatusEffect(positionData, extraData.potency);
    }
}
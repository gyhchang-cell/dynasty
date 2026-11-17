package com.sammy.malum.visual_effects.networked.wind_gust;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import com.sammy.malum.visual_effects.block.WindTunnelParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;

public class WindTrailParticleEffect extends MalumNetworkedParticleEffectType<WindTrailParticleEffect.WindTrailParticleEffectData> {

    public record WindTrailParticleEffectData(int target, int delay, int duration) implements NetworkedParticleEffectExtraData {
        public static final Codec<WindTrailParticleEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.INT.fieldOf("target").forGetter(WindTrailParticleEffectData::target),
                Codec.INT.fieldOf("delay").forGetter(WindTrailParticleEffectData::delay),
                Codec.INT.fieldOf("duration").forGetter(WindTrailParticleEffectData::duration)
        ).apply(instance, WindTrailParticleEffectData::new));

        public static final StreamCodec<ByteBuf, WindTrailParticleEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }

    public WindTrailParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(WindTrailParticleEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, WindTrailParticleEffectData extraData) {
        if (level.getEntity(extraData.target()) instanceof Entity target) {
            WindTunnelParticleEffects.windTrailParticles(level, random, target, positionData.getAsVector(), colorData, extraData);
        }
    }
}
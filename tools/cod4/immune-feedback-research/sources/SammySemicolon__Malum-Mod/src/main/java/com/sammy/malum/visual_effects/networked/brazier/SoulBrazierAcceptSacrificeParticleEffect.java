package com.sammy.malum.visual_effects.networked.brazier;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.sammy.malum.common.block.curiosities.sorcery.soul_brazier.*;
import com.sammy.malum.visual_effects.block.SoulBindingBrazierParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.entity.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;

import java.util.Optional;

public class SoulBrazierAcceptSacrificeParticleEffect extends MalumNetworkedParticleEffectType<SoulBrazierAcceptSacrificeParticleEffect.SoulBrazierEntityEffectData> {

    public record SoulBrazierEntityEffectData(int entityId) implements NetworkedParticleEffectExtraData {
        public static final Codec<SoulBrazierEntityEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.INT.fieldOf("entityId").forGetter(SoulBrazierEntityEffectData::entityId)
        ).apply(instance, SoulBrazierEntityEffectData::new));

        public static final StreamCodec<ByteBuf, SoulBrazierEntityEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }

    public SoulBrazierAcceptSacrificeParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(SoulBrazierEntityEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, SoulBrazierEntityEffectData extraData) {
        if (!(level.getBlockEntity(positionData.getAsBlockPos()) instanceof SoulBrazierBlockEntity brazier)) {
            return;
        }
        if (level.getEntity(extraData.entityId) instanceof LivingEntity entity) {
            SoulBindingBrazierParticleEffects.acceptSacrificeParticles(brazier, entity, colorData);
        }
    }
}
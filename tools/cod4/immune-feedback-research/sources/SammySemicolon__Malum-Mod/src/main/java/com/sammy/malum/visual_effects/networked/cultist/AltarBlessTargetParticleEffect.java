package com.sammy.malum.visual_effects.networked.cultist;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.sammy.malum.visual_effects.CultistParticleEffects;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectType;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import team.lodestar.lodestone.systems.network.WeaponParticleEffectType;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;

import java.util.Optional;

public class AltarBlessTargetParticleEffect extends MalumNetworkedParticleEffectType<AltarBlessTargetParticleEffect.AltarBlessTargetParticleData> {

    public record AltarBlessTargetParticleData(int targetId) implements NetworkedParticleEffectExtraData {
        public static final Codec<AltarBlessTargetParticleData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.INT.fieldOf("targetId").forGetter(AltarBlessTargetParticleData::targetId)
        ).apply(instance, AltarBlessTargetParticleData::new));

        public static final StreamCodec<ByteBuf, AltarBlessTargetParticleData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);

    }

    public AltarBlessTargetParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(AltarBlessTargetParticleData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, AltarBlessTargetParticleData extraData) {
        if (level.getEntity(extraData.targetId) instanceof LivingEntity target) {
            CultistParticleEffects.altarBlessTarget(level, positionData, colorData, target);
        }
    }
}
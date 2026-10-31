package com.sammy.malum.visual_effects.networked.geas;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import com.sammy.malum.visual_effects.GeasParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import com.sammy.malum.visual_effects.networked.sap.*;
import io.netty.buffer.*;
import net.minecraft.core.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import team.lodestar.lodestone.systems.network.*;
import net.minecraft.nbt.*;
import net.minecraft.world.entity.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;
import java.util.function.*;

public class WyrdReconstructionReviveParticleEffect extends MalumNetworkedParticleEffectType<WyrdReconstructionReviveParticleEffect.WyrdReconstructionEffectData> {

    public record WyrdReconstructionEffectData(int entityID) implements NetworkedParticleEffectExtraData {
        public static final Codec<WyrdReconstructionEffectData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
                Codec.INT.fieldOf("entityID").forGetter(WyrdReconstructionEffectData::entityID)
        ).apply(instance, WyrdReconstructionEffectData::new));

        public static final StreamCodec<ByteBuf, WyrdReconstructionEffectData> STREAM_CODEC = ByteBufCodecs.fromCodec(CODEC);
    }

    public WyrdReconstructionReviveParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(WyrdReconstructionEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, WyrdReconstructionEffectData extraData) {
        var entity = level.getEntity(extraData.entityID);
        if (entity != null) {
            GeasParticleEffects.wyrdReconstructionRevive(level, entity, random, positionData, colorData);
        }
    }
}
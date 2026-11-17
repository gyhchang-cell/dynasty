package com.sammy.malum.visual_effects.networked.brazier;

import com.sammy.malum.common.block.curiosities.sorcery.soul_brazier.SoulBrazierBlockEntity;
import com.sammy.malum.visual_effects.block.SoulBindingBrazierParticleEffects;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectType;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;

import java.util.*;

public class SoulBrazierEndParticleEffect extends MalumNetworkedParticleEffectType<SoulBrazierStateEffectData> {

    public SoulBrazierEndParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(SoulBrazierStateEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, SoulBrazierStateEffectData extraData) {
        if (!(level.getBlockEntity(positionData.getAsBlockPos()) instanceof SoulBrazierBlockEntity brazier)) {
            return;
        }
        brazier.state = extraData.state();
        SoulBindingBrazierParticleEffects.finishSoulBindingParticles(brazier, colorData);
    }
}
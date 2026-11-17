package com.sammy.malum.visual_effects.networked.arcana_pylon;

import com.sammy.malum.common.block.curiosities.obelisk.rite_pylon.*;
import com.sammy.malum.visual_effects.block.ArcanaPylonParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;

public class ArcanaPylonEatSpiritParticleEffect extends MalumNetworkedParticleEffectType<ArcanaPylonEffectData> {

    public ArcanaPylonEatSpiritParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(ArcanaPylonEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, ArcanaPylonEffectData extraData) {
        if (!(level.getBlockEntity(positionData.getAsBlockPos()) instanceof ArcanaPylonBlockEntity arcanaPylon)) {
            return;
        }
        ArcanaPylonParticleEffects.eatSpiritParticles(level, arcanaPylon, colorData, extraData);
    }
}
package com.sammy.malum.visual_effects.networked.blight;

import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.*;
import net.minecraft.core.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;

public class BlightPlantGrowthParticleEffect extends BlightParticleEffect {

    public BlightPlantGrowthParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectColorData>> getColorCodec() {
        return Optional.empty();
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, BlightEffectData extraData) {
        BlockPos sourcePos = positionData.getAsBlockPos();
        for (BlockPos targetPos : extraData.affectedArea()) {
            BlightParticleEffects.blightPlantGrows(level, sourcePos, targetPos);
        }
    }
}
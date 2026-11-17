package com.sammy.malum.visual_effects.networked.blight;

import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.core.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

public class StrangeCrystalParticleEffect extends BlightParticleEffect {

    public StrangeCrystalParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, BlightEffectData extraData) {
        BlockPos sourcePos = positionData.getAsBlockPos();
        for (BlockPos targetPos : extraData.affectedArea()) {
            BlightParticleEffects.strangeCrystalForms(level, colorData, sourcePos, targetPos);
        }
    }
}
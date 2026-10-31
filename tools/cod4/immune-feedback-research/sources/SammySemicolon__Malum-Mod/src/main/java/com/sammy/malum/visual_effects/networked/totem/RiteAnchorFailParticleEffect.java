package com.sammy.malum.visual_effects.networked.totem;

import com.sammy.malum.visual_effects.block.TotemParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

public class RiteAnchorFailParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public RiteAnchorFailParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        TotemParticleEffects.triggerRiteAnchorFailure(level, colorData, positionData);
    }
}
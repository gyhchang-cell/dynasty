package com.sammy.malum.visual_effects.networked.geas;

import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

public class CombustionBurnParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public CombustionBurnParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        GeasParticleEffects.combustionBurn(level, random, positionData, colorData);
    }
}
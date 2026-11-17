package com.sammy.malum.visual_effects.networked.geas;

import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

public class BerserkerSpiritImpactParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public BerserkerSpiritImpactParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        GeasParticleEffects.berserkerBlast(level, random, positionData, colorData);
    }
}
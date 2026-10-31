package com.sammy.malum.visual_effects.networked.geas;

import com.sammy.malum.visual_effects.GeasParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.function.*;

import static com.sammy.malum.visual_effects.SpiritLightSpecs.spiritLightSpecs;

public class InvertedHeartGeasImpactParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public InvertedHeartGeasImpactParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        GeasParticleEffects.invertedHeartDamageEffect(level, random, positionData, colorData);
    }
}
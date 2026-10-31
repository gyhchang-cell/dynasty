package com.sammy.malum.visual_effects.networked.crucible;

import com.sammy.malum.common.block.curiosities.artifice.spirit_crucible.*;
import com.sammy.malum.visual_effects.block.SpiritCrucibleParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

public class SpiritCrucibleCraftParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public SpiritCrucibleCraftParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        if (!(level.getBlockEntity(positionData.getAsBlockPos()) instanceof SpiritCrucibleCoreBlockEntity crucible)) {
            return;
        }
        SpiritCrucibleParticleEffects.craftItemParticles(crucible, colorData);
    }
}
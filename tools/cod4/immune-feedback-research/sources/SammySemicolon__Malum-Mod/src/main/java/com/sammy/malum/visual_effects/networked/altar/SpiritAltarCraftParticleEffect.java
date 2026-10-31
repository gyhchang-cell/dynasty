package com.sammy.malum.visual_effects.networked.altar;

import com.sammy.malum.common.block.curiosities.sorcery.spirit_altar.SpiritAltarBlockEntity;
import com.sammy.malum.visual_effects.block.SpiritAltarParticleEffects;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectColorData;
import com.sammy.malum.visual_effects.networked.MalumNetworkedParticleEffectType;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectExtraData;
import team.lodestar.lodestone.systems.network.particle.NetworkedParticleEffectPositionData;

public class SpiritAltarCraftParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public SpiritAltarCraftParticleEffect(String id) {
        super(id);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        if (!(level.getBlockEntity(positionData.getAsBlockPos()) instanceof SpiritAltarBlockEntity spiritAltar)) {
            return;
        }
        SpiritAltarParticleEffects.craftItemParticles(level, spiritAltar, colorData);
    }
}
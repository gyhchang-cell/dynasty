package com.sammy.malum.visual_effects.networked.runic_workbench;

import com.sammy.malum.common.block.curiosities.sorcery.runic_workbench.*;
import com.sammy.malum.visual_effects.block.RunicWorkbenchParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;

public class RunicWorkbenchCraftSpiritlessItemParticleEffect extends MalumNetworkedParticleEffectType<RunicWorkbenchEffectData> {

    public RunicWorkbenchCraftSpiritlessItemParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectColorData>> getColorCodec() {
        return Optional.empty();
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(RunicWorkbenchEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, RunicWorkbenchEffectData extraData) {
        if (!(level.getBlockEntity(positionData.getAsBlockPos()) instanceof RunicWorkbenchBlockEntity runicWorkbench)) {
            return;
        }
        RunicWorkbenchParticleEffects.craftItemParticles(level, runicWorkbench, extraData);
    }
}
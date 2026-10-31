package com.sammy.malum.visual_effects.networked.repair_pylon;

import com.sammy.malum.common.block.curiosities.artifice.repair_pylon.*;
import com.sammy.malum.common.block.storage.*;
import com.sammy.malum.visual_effects.block.RepairPylonParticleEffects;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.level.*;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;

public class PylonRepairParticleEffect extends MalumNetworkedParticleEffectType<PylonEffectData> {

    public PylonRepairParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectExtraData>> getExtraCodec() {
        return Optional.of(PylonEffectData.STREAM_CODEC);
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, PylonEffectData extraData) {
        if (!(level.getBlockEntity(positionData.getAsBlockPos()) instanceof RepairPylonCoreBlockEntity pylon)) {
            return;
        }
        if (!(level.getBlockEntity(extraData.holderPos()) instanceof IMalumSpecialItemAccessPoint holder)) {
            return;
        }
        RepairPylonParticleEffects.repairItemParticles(pylon, holder, colorData);
    }
}
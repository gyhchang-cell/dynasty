package com.sammy.malum.visual_effects.networked.weeping_well;

import com.sammy.malum.visual_effects.*;
import com.sammy.malum.visual_effects.networked.*;
import io.netty.buffer.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.neoforged.api.distmarker.*;
import team.lodestar.lodestone.systems.network.particle.*;

import java.util.*;
import java.util.function.Supplier;

public class WeepingWellReactionParticleEffect extends MalumNetworkedParticleEffectType<NetworkedParticleEffectExtraData> {

    public WeepingWellReactionParticleEffect(String id) {
        super(id);
    }

    @Override
    public Optional<StreamCodec<ByteBuf, ? extends NetworkedParticleEffectColorData>> getColorCodec() {
        return Optional.empty();
    }

    @OnlyIn(Dist.CLIENT)
    @Override
    public void act(Level level, RandomSource random, NetworkedParticleEffectPositionData positionData, MalumNetworkedParticleEffectColorData colorData, NetworkedParticleEffectExtraData extraData) {
        WeepingWellParticleEffects.spitOutItemParticles(level, positionData);
    }
}
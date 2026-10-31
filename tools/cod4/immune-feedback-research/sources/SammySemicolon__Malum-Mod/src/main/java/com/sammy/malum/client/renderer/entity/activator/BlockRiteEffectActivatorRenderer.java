package com.sammy.malum.client.renderer.entity.activator;

import com.sammy.malum.common.entity.activator.rite.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import net.minecraft.client.renderer.entity.*;
import team.lodestar.lodestone.systems.rendering.trail.*;

public class BlockRiteEffectActivatorRenderer extends AbstractEffectActivatorEntityRenderer<BlockRiteEffectActivator> {
    public BlockRiteEffectActivatorRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public SpiritArcanaType getSpiritType(BlockRiteEffectActivator entity) {
        return entity.getSpiritType();
    }

    @Override
    public float getScale(BlockRiteEffectActivator entity, boolean longTrail) {
        return 0.8f * entity.getVisualEffectScalar() * (longTrail ? 1f : 0.75f);
    }

    @Override
    public float getAlpha(BlockRiteEffectActivator entity, boolean longTrail) {
        return 0.45f * entity.getVisualEffectScalar() * (longTrail ? 1f : 2f);
    }

    @Override
    public TrailPointBuilder getTrail(BlockRiteEffectActivator entity) {
        return entity.trail;
    }

    @Override
    public TrailPointBuilder getLongTrail(BlockRiteEffectActivator entity) {
        return entity.longTrail;
    }
}

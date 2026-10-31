package com.sammy.malum.client.renderer.entity.activator;

import com.sammy.malum.common.entity.activator.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import net.minecraft.client.renderer.entity.*;
import team.lodestar.lodestone.systems.rendering.trail.*;

public class SpellweaverToolEffectActivatorRenderer extends AbstractEffectActivatorEntityRenderer<SpellweaverToolEffectActivator> {

    public SpellweaverToolEffectActivatorRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public SpiritArcanaType getSpiritType(SpellweaverToolEffectActivator entity) {
        return entity.getSpiritType();
    }

    @Override
    public float getScale(SpellweaverToolEffectActivator entity, boolean longTrail) {
        return 0.5f * entity.getVisualEffectScalar() * (longTrail ? 0.5f : 0.75f);
    }

    @Override
    public float getAlpha(SpellweaverToolEffectActivator entity, boolean longTrail) {
        return 0.5f * entity.getVisualEffectScalar() * (longTrail ? 0.75f : 1.5f);
    }

    @Override
    public TrailPointBuilder getTrail(SpellweaverToolEffectActivator entity) {
        return entity.trail;
    }

    @Override
    public TrailPointBuilder getLongTrail(SpellweaverToolEffectActivator entity) {
        return entity.longTrail;
    }
}

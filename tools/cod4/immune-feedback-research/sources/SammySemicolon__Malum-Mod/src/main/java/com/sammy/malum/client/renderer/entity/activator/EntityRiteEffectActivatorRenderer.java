package com.sammy.malum.client.renderer.entity.activator;

import com.sammy.malum.common.entity.activator.rite.*;
import com.sammy.malum.core.systems.spirit.SpiritArcanaType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import team.lodestar.lodestone.systems.rendering.trail.*;

import static com.sammy.malum.client.renderer.entity.FloatingItemRenderer.renderSpiritGlimmer;

public class EntityRiteEffectActivatorRenderer extends AbstractEffectActivatorEntityRenderer<EntityRiteEffectActivator> {

    public EntityRiteEffectActivatorRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public SpiritArcanaType getSpiritType(EntityRiteEffectActivator entity) {
        return entity.getSpiritType();
    }

    @Override
    public float getScale(EntityRiteEffectActivator entity, boolean longTrail) {
        return 1.2f * entity.getVisualEffectScalar() * (longTrail ? 1f : 0.75f);
    }

    @Override
    public float getAlpha(EntityRiteEffectActivator entity, boolean longTrail) {
        return 0.3f * entity.getVisualEffectScalar() * (longTrail ? 1f : 2f);
    }

    @Override
    public TrailPointBuilder getTrail(EntityRiteEffectActivator entity) {
        return entity.trail;
    }

    @Override
    public TrailPointBuilder getLongTrail(EntityRiteEffectActivator entity) {
        return entity.longTrail;
    }
}

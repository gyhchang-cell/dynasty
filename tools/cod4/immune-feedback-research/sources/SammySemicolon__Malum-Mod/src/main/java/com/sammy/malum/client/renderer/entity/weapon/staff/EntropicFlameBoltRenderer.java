package com.sammy.malum.client.renderer.entity.weapon.staff;

import com.mojang.blaze3d.vertex.PoseStack;
import com.sammy.malum.client.RenderUtils;
import com.sammy.malum.client.renderer.entity.AbstractBoltEntityRenderer;
import com.sammy.malum.common.entity.bolt.*;
import com.sammy.malum.common.entity.nitrate.*;
import com.sammy.malum.registry.common.magic.MalumSpiritTypes;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.util.Mth;
import team.lodestar.lodestone.helpers.ColorHelper;
import team.lodestar.lodestone.systems.rendering.builder.VFXBuilders;
import team.lodestar.lodestone.systems.rendering.builder.WorldVFXBuilder;

import java.awt.*;

public class EntropicFlameBoltRenderer extends AbstractBoltEntityRenderer<EntropicFlameBolt> {
    public EntropicFlameBoltRenderer(EntityRendererProvider.Context context) {
        super(context, EthericNitrate.AURIC_YELLOW, EthericNitrate.AURIC_RED);
    }

    @Override
    public Color getPrimaryColor(int trailIndex) {
        if (trailIndex == 2) {
            return MalumSpiritTypes.SACRED_SPIRIT.getPrimaryColor();
        }
        if (trailIndex == 0) {
            return ColorHelper.darker(MalumSpiritTypes.EARTHEN_SPIRIT.getPrimaryColor(), 2);
        }
        return super.getPrimaryColor(trailIndex);
    }

    @Override
    public Color getSecondaryColor(int trailIndex) {
        if (trailIndex == 2) {
            return MalumSpiritTypes.SACRED_SPIRIT.getSecondaryColor();
        }
        if (trailIndex == 0) {
            return ColorHelper.darker(MalumSpiritTypes.EARTHEN_SPIRIT.getSecondaryColor(), 2);
        }
        return super.getSecondaryColor(trailIndex);
    }

    @Override
    public void render(EntropicFlameBolt entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int packedLightIn) {
        if (entity.isAwaitingSpawn()) {
            return;
        }
        float delta = entity.getVisualEffectScalar();
        float scale = delta * getScaleMultiplier();
        float alpha = Mth.clamp(delta * getAlphaMultiplier() * 0.5f, 0, 1);
        WorldVFXBuilder builder = VFXBuilders.createWorld().setRenderType(getTrailRenderType(true));
        Color aqueousPrimaryColor = MalumSpiritTypes.AQUEOUS_SPIRIT.getPrimaryColor();
        Color darkerPrimary = ColorHelper.darker(aqueousPrimaryColor, 2);
        Color aqueousSecondaryColor = MalumSpiritTypes.EARTHEN_SPIRIT.getSecondaryColor();
        Color darkerSecondary = ColorHelper.darker(aqueousSecondaryColor, 2);
        RenderUtils.renderEntityTrail(poseStack, builder, entity.secondarySpinningTrailPointBuilder, entity, darkerPrimary, darkerSecondary, scale * 2f, alpha, partialTicks);
        builder.setRenderType(getTrailRenderType(false));
        RenderUtils.renderEntityTrail(poseStack, builder, entity.secondarySpinningTrailPointBuilder, entity, aqueousPrimaryColor, aqueousSecondaryColor, scale, alpha, partialTicks);
        super.render(entity, entityYaw, partialTicks, poseStack, bufferIn, packedLightIn);
    }
}

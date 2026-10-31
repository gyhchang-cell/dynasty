package com.sammy.malum.client.renderer.entity.activator;

import com.mojang.blaze3d.vertex.*;
import com.sammy.malum.client.*;
import com.sammy.malum.client.renderer.entity.*;
import com.sammy.malum.common.entity.activator.*;
import com.sammy.malum.registry.client.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.texture.*;
import net.minecraft.resources.*;
import team.lodestar.lodestone.registry.client.*;
import team.lodestar.lodestone.systems.rendering.trail.*;

import java.awt.*;

import static com.sammy.malum.registry.common.magic.MalumSpiritTypes.*;

public class SpiritCollectionActivatorRenderer extends EntityRenderer<SpiritCollectionActivator> {

    public final ItemRenderer itemRenderer;

    public SpiritCollectionActivatorRenderer(EntityRendererProvider.Context context) {
        super(context);
        this.itemRenderer = context.getItemRenderer();
        this.shadowRadius = 0;
        this.shadowStrength = 0;
    }

    @Override
    public void render(SpiritCollectionActivator entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int packedLightIn) {
        var spiritType = UMBRAL_SPIRIT;
        var secondarySpiritType = ELDRITCH_SPIRIT;
        var additive = LodestoneRenderTypes.ADDITIVE_TWO_SIDED_TEXTURE_TRIANGLE.apply(MalumRenderTypeTokens.CONCENTRATED_TRAIL);
        var transparent = LodestoneRenderTypes.TRANSPARENT_TWO_SIDED_TEXTURE_TRIANGLE.apply(MalumRenderTypeTokens.CONCENTRATED_TRAIL);
        var trailBuilder = SpiritBasedWorldVFXBuilder.create(spiritType).setRenderType(additive);
        float yOffset = entity.getYOffset(partialTicks);

        for (int i = 0; i < 2; i++) {

            poseStack.pushPose();
            poseStack.translate(0.0D, yOffset, 0.0D);
            FloatingItemRenderer.renderSpiritGlimmer(poseStack, secondarySpiritType, 1f, 0.1f, partialTicks);
            FloatingItemRenderer.renderSpiritGlimmer(poseStack, secondarySpiritType, 0.2f, 0.7f, partialTicks);
            FloatingItemRenderer.renderSpiritGlimmer(poseStack, spiritType, 2f, 3f, partialTicks);
            poseStack.popPose();

            Color primaryColor = spiritType.getPrimaryColor();
            Color secondaryColor = spiritType.getSecondaryColor();
            RenderUtils.renderEntityTrail(poseStack, trailBuilder, entity.trail, entity, primaryColor, secondaryColor, 0.7f, 1f, partialTicks);
            RenderUtils.renderEntityTrail(poseStack, trailBuilder, entity.longTrail, entity, primaryColor, secondaryColor, 0.4f, 0.3f, partialTicks);
            for (TrailPointBuilder trail : entity.orbitingTrails) {
                RenderUtils.renderEntityTrail(poseStack, trailBuilder, trail, entity, primaryColor, secondaryColor, 0.9f, 1f, partialTicks);
            }
            trailBuilder.setRenderType(transparent);
            RenderUtils.renderEntityTrail(poseStack, trailBuilder, entity.trail, entity, primaryColor, secondaryColor, 0.7f, 1.25f, partialTicks);
            RenderUtils.renderEntityTrail(poseStack, trailBuilder, entity.longTrail, entity, primaryColor, secondaryColor, 0.2f, 0.5f, partialTicks);
            for (TrailPointBuilder trail : entity.orbitingTrails) {
                RenderUtils.renderEntityTrail(poseStack, trailBuilder, trail, entity, primaryColor, secondaryColor, 0.4f, 1.25f, partialTicks);
            }
        }
        super.render(entity, entityYaw, partialTicks, poseStack, bufferIn, packedLightIn);
    }

    @Override
    public ResourceLocation getTextureLocation(SpiritCollectionActivator entity) {
        return TextureAtlas.LOCATION_BLOCKS;
    }
}
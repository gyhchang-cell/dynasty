package com.sammy.malum.client.renderer.entity;

import com.mojang.blaze3d.vertex.*;
import com.mojang.math.*;
import com.sammy.malum.client.*;
import com.sammy.malum.common.entity.*;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import com.sammy.malum.registry.client.*;
import net.minecraft.client.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.texture.*;
import net.minecraft.resources.*;
import net.minecraft.util.*;
import net.minecraft.world.item.*;
import team.lodestar.lodestone.registry.client.*;
import team.lodestar.lodestone.systems.rendering.*;
import team.lodestar.lodestone.systems.rendering.builder.VFXBuilders;
import team.lodestar.lodestone.systems.rendering.builder.WorldVFXBuilder;

import java.awt.*;

public class FloatingItemRenderer extends EntityRenderer<FloatingItemEntity> {
    public final ItemRenderer itemRenderer;

    public FloatingItemRenderer(EntityRendererProvider.Context context) {
        super(context);
        this.itemRenderer = context.getItemRenderer();
        this.shadowRadius = 0;
        this.shadowStrength = 0;
    }

    @Override
    public void render(FloatingItemEntity entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int packedLightIn) {
        var spiritType = entity.getSpiritType();
        var trail = LodestoneRenderTypes.ADDITIVE_TEXTURE_TRIANGLE.apply(MalumRenderTypeTokens.CONCENTRATED_TRAIL);
        var longTrail = LodestoneRenderTypes.ADDITIVE_ROUNDED_TEXTURE_TRIANGLE.apply(MalumRenderTypeTokens.CONCENTRATED_TRAIL);
        var builder = SpiritBasedWorldVFXBuilder.create(spiritType);
        float effectScalar = entity.getVisualEffectScalar();

        RenderUtils.renderEntityTrail(poseStack, builder.setRenderType(trail), entity.trail, entity, spiritType.getPrimaryColor(), spiritType.getSecondaryColor(), effectScalar, partialTicks);
        RenderUtils.renderEntityTrail(poseStack, builder.setRenderType(longTrail), entity.longTrail, entity, spiritType.getSecondaryColor(), spiritType.getPrimaryColor(), effectScalar*0.6f, effectScalar*0.2f, partialTicks);
        renderSpiritEntity(entity, itemRenderer, partialTicks, poseStack, bufferIn, packedLightIn);
        super.render(entity, entityYaw, partialTicks, poseStack, bufferIn, packedLightIn);
    }

    public static void renderSpiritEntity(FloatingItemEntity entity, ItemRenderer itemRenderer, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int packedLightIn) {
        var level = entity.level();
        var stack = entity.getItem();
        var model = itemRenderer.getModel(stack, level, null, entity.getItem().getCount());
        float yOffset = entity.getYOffset(partialTicks);
        float scale = model.getTransforms().getTransform(ItemDisplayContext.GROUND).scale.y();
        float rotation = entity.getRotation(partialTicks);

        poseStack.pushPose();
        poseStack.translate(0.0D, yOffset, 0.0D);
        renderSpiritGlimmer(poseStack, entity.getSpiritType(), partialTicks);
        poseStack.translate(0.0D, -0.25F * scale, 0.0D);
        poseStack.mulPose(Axis.YP.rotation(rotation));
        itemRenderer.render(stack, ItemDisplayContext.GROUND, false, poseStack, bufferIn, packedLightIn, OverlayTexture.NO_OVERLAY, model);
        poseStack.popPose();
    }

    public static void renderSpiritGlimmer(PoseStack poseStack, SpiritLike spirit, float partialTicks) {
        renderSpiritGlimmer(poseStack, spirit, 1f, partialTicks);
    }

    public static void renderSpiritGlimmer(PoseStack poseStack, SpiritLike spirit, float scalar, float partialTicks) {
        renderSpiritGlimmer(poseStack, SpiritBasedWorldVFXBuilder.create(spirit), spirit.getPrimaryColor(), spirit.getSecondaryColor(), scalar, scalar, partialTicks);
    }

    public static void renderSpiritGlimmer(PoseStack poseStack, SpiritLike spirit, float scaleScalar, float alphaScalar, float partialTicks) {
        renderSpiritGlimmer(poseStack, SpiritBasedWorldVFXBuilder.create(spirit), spirit.getPrimaryColor(), spirit.getSecondaryColor(), scaleScalar, alphaScalar, partialTicks);
    }

    public static void renderSpiritGlimmer(PoseStack poseStack, Color primaryColor, Color secondaryColor, float partialTicks) {
        renderSpiritGlimmer(poseStack, primaryColor, secondaryColor, 1f, partialTicks);
    }

    public static void renderSpiritGlimmer(PoseStack poseStack, Color primaryColor, Color secondaryColor, float scalar, float partialTicks) {
        renderSpiritGlimmer(poseStack, VFXBuilders.createWorld(), primaryColor, secondaryColor, scalar, scalar, partialTicks);
    }

    public static void renderSpiritGlimmer(PoseStack poseStack, Color primaryColor, Color secondaryColor, float scaleScalar, float alphaScalar, float partialTicks) {
        renderSpiritGlimmer(poseStack, VFXBuilders.createWorld(), primaryColor, secondaryColor, scaleScalar, alphaScalar, partialTicks);
    }

    public static void renderSpiritGlimmer(PoseStack poseStack, WorldVFXBuilder builder, Color primaryColor, Color secondaryColor, float scaleScalar, float alphaScalar, float partialTicks) {
        var minecraft = Minecraft.getInstance();
        var level = minecraft.level;
        var star = LodestoneRenderTypes.ADDITIVE_TEXTURE.apply(MalumRenderTypeTokens.STAR);
        var twinkle = LodestoneRenderTypes.ADDITIVE_TEXTURE.apply(MalumRenderTypeTokens.TWINKLE);

        float gameTime = level.getGameTime() + partialTicks;
        double sine = Math.abs(((Math.sin((gameTime / 80f) % 360)) * 0.075f));
        float scale = (float) ((0.12f + sine) * scaleScalar);

        poseStack.pushPose();
        poseStack.mulPose(minecraft.getEntityRenderDispatcher().cameraOrientation());
        builder.setAlpha(Mth.clamp(0.6f * alphaScalar, 0, 1))
                .setColor(primaryColor)
                .setRenderType(star)
                .renderQuad(poseStack, scale * 0.8f);
        builder.setAlpha(Mth.clamp(0.8f * alphaScalar, 0, 1))
                .setRenderType(twinkle)
                .renderQuad(poseStack, scale * 0.6f);
        builder.setAlpha(Mth.clamp(0.2f * alphaScalar, 0, 1))
                .setColor(secondaryColor)
                .renderQuad(poseStack, scale * 0.6f);
        poseStack.popPose();
    }

    @Override
    public ResourceLocation getTextureLocation(FloatingItemEntity entity) {
        return TextureAtlas.LOCATION_BLOCKS;
    }
}
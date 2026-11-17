package com.sammy.malum.client.renderer.entity;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.sammy.malum.common.entity.soulTag.SoulTagEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;

public class SoulTagRenderer extends EntityRenderer<SoulTagEntity> {

    public SoulTagRenderer(EntityRendererProvider.Context context) {
        super(context);

        shadowRadius = 0.0F;
    }

    @Override
    public void render(SoulTagEntity entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();

        float time =
                entity.tickCount + partialTick;

        float hover =
                (float) Math.sin(time * 0.08F) * 0.05F;

        poseStack.translate(
                0.0F,
                hover,
                0.0F
        );

        float rotation = (entity.tickCount + partialTick) * 4.0F;

        poseStack.mulPose(
                Axis.YP.rotationDegrees(rotation)
        );

        Minecraft.getInstance()
                .getItemRenderer()
                .renderStatic(
                        entity.getItem(),
                        ItemDisplayContext.GROUND,
                        packedLight,
                        OverlayTexture.NO_OVERLAY,
                        poseStack,
                        buffer,
                        entity.level(),
                        entity.getId()
                );

        poseStack.popPose();

        super.render(entity, entityYaw, partialTick, poseStack, buffer, packedLight
        );
    }

    @Override
    public ResourceLocation getTextureLocation(SoulTagEntity soulTagEntity) {
        return null;
    }
}
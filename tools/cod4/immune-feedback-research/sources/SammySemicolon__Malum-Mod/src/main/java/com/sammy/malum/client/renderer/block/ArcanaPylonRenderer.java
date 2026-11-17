package com.sammy.malum.client.renderer.block;

import com.mojang.blaze3d.vertex.*;
import com.mojang.math.*;
import com.sammy.malum.client.*;
import com.sammy.malum.common.block.curiosities.obelisk.rite_pylon.*;
import com.sammy.malum.registry.client.*;
import net.minecraft.client.*;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.blockentity.*;
import net.minecraft.util.*;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.*;
import org.jetbrains.annotations.*;
import org.joml.*;
import team.lodestar.lodestone.registry.client.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.rendering.builder.data.CubeVertexData;

import java.lang.Math;

import static net.minecraft.client.renderer.texture.OverlayTexture.*;


public class ArcanaPylonRenderer implements BlockEntityRenderer<ArcanaPylonBlockEntity> {

    public ArcanaPylonRenderer(BlockEntityRendererProvider.Context context) {
    }

    @Override
    public AABB getRenderBoundingBox(ArcanaPylonBlockEntity blockEntityIn) {
        var pos = blockEntityIn.getBlockPos();
        return new AABB(pos.getX() - 1, pos.getY(), pos.getZ() - 1, pos.getX() + 2, pos.getY() + 5, pos.getZ() + 2);
    }

    @Override
    public void render(ArcanaPylonBlockEntity blockEntityIn, float partialTicks, PoseStack poseStack, MultiBufferSource bufferIn, int combinedLightIn, int combinedOverlayIn) {
        var level = Minecraft.getInstance().level;
        var itemRenderer = Minecraft.getInstance().getItemRenderer();
        var stack = blockEntityIn.inventory.getStackInSlot(0);
        if (!stack.isEmpty()) {
            poseStack.pushPose();
            Vec3 offset = blockEntityIn.getCentralItemOffset();
            poseStack.translate(offset.x, offset.y, offset.z);
            poseStack.mulPose(Axis.YP.rotationDegrees(((level.getGameTime() % 360) + partialTicks) * 3));
            poseStack.scale(0.45f, 0.45f, 0.45f);
            itemRenderer.renderStatic(stack, ItemDisplayContext.FIXED, combinedLightIn, NO_OVERLAY, poseStack, bufferIn, level, 0);
            poseStack.popPose();
        }

        var spirit = blockEntityIn.spirit;
        if (spirit == null) {
            return;
        }

        float delta = blockEntityIn.getGlowDelta();
        float ease = Easing.SINE_OUT.ease(delta);
        float offsetDistance = 0.2f - ease * 0.2f;
        float wobbleStrength = 0.1f - ease * 0.075f;
        float gameTime = level.getGameTime() + partialTicks;

        poseStack.pushPose();
        poseStack.translate(0.5f, 0, 0.5f);
        for (int i = 0; i < 5; i++) {
            float alpha = delta * 0.7f;
            var token = i == 4 ? MalumRenderTypeTokens.PYLON_GLOW_TOP : MalumRenderTypeTokens.PYLON_GLOW_SIDE;
            var renderType = LodestoneRenderTypes.ADDITIVE_TEXTURE.apply(token);
            var vertices = getVertexPositions(i);
            poseStack.pushPose();
            if (i < 4) {
                poseStack.mulPose(Axis.YN.rotationDegrees(i * 90));
            }

            int time = 160;
            for (int j = 0; j < 4; j++) {
                var color = j <= 1 ? spirit.getPrimaryColor() : spirit.getSecondaryColor();
                double offset = 0;
                if (offsetDistance > 0) {
                    double angle = j / 4f * (Math.PI * 2);
                    angle += ((gameTime % time) / time) * (Math.PI * 2);
                    offset = (offsetDistance * Math.cos(angle));
                    if (j % 2 == 0) {
                        offset *= -1;
                    }
                }

                poseStack.pushPose();
                poseStack.translate(offset, 0, 0);
                CubeVertexData.applyVertexWobble(vertices, j*2f, wobbleStrength);
                SpiritBasedWorldVFXBuilder.create(spirit)
                        .setColor(color, alpha)
                        .setRenderType(renderType)
                        .renderQuad(poseStack, vertices, 1f);
                poseStack.popPose();
                alpha *= (1 - (delta + 0.2f) * 0.4f);
            }
            poseStack.popPose();
        }
        poseStack.popPose();
    }

    private static Vector3f @NotNull [] getVertexPositions(int direction) {
        Vector3f[] positions;
        if (direction < 4) {
            positions = new Vector3f[]{
                    new Vector3f(-0.5f, 0.625f, 0.35f), new Vector3f(0.5f, 0.625f, 0.35f),
                    new Vector3f(0.5f, 1.625f, 0.35f), new Vector3f(-0.5f, 1.625f, 0.35f)};
        }
        else {
            positions = new Vector3f[]{
                    new Vector3f(-0.5f, 1.65f, 0.5f), new Vector3f(0.5f, 1.65f, 0.5f),
                    new Vector3f(0.5f, 1.65f, -0.5f), new Vector3f(-0.5f, 1.65f, -0.5f)};
        }
        return positions;
    }
}

package com.sammy.malum.client;

import com.mojang.blaze3d.vertex.*;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import net.minecraft.util.*;
import net.minecraft.world.entity.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.systems.rendering.*;
import team.lodestar.lodestone.systems.rendering.builder.WorldVFXBuilder;
import team.lodestar.lodestone.systems.rendering.trail.*;

import java.awt.*;
import java.util.function.*;

public class RenderUtils {

    public static void renderEntityTrail(PoseStack poseStack, WorldVFXBuilder builder, TrailPointBuilder trailPointBuilder, Entity entity, SpiritLike spirit, float effectScalar, float partialTicks) {
        renderEntityTrail(poseStack, builder, trailPointBuilder, entity, spirit.getPrimaryColor(), spirit.getSecondaryColor(), effectScalar, effectScalar, partialTicks);
    }

    public static void renderEntityTrail(PoseStack poseStack, WorldVFXBuilder builder, TrailPointBuilder trailPointBuilder, Entity entity, Color primaryColor, Color secondaryColor, float effectScalar, float partialTicks) {
        renderEntityTrail(poseStack, builder, trailPointBuilder, entity, t -> primaryColor, t -> secondaryColor, effectScalar, effectScalar, partialTicks);
    }

    public static void renderEntityTrail(PoseStack poseStack, WorldVFXBuilder builder, TrailPointBuilder trailPointBuilder, Entity entity, Function<Float, Color> primaryColor, Function<Float, Color> secondaryColor, float effectScalar, float partialTicks) {
        renderEntityTrail(poseStack, builder, trailPointBuilder, entity, primaryColor, secondaryColor, effectScalar, effectScalar, partialTicks);
    }

    public static void renderEntityTrail(PoseStack poseStack, WorldVFXBuilder builder, TrailPointBuilder trailPointBuilder, Entity entity, SpiritLike spirit, float scaleScalar, float alphaScalar, float partialTicks) {
        renderEntityTrail(poseStack, builder, trailPointBuilder, entity, spirit.getPrimaryColor(), spirit.getSecondaryColor(), scaleScalar, alphaScalar, partialTicks);
    }

    public static void renderEntityTrail(PoseStack poseStack, WorldVFXBuilder builder, TrailPointBuilder trailPointBuilder, Entity entity, Color primaryColor, Color secondaryColor, float scaleScalar, float alphaScalar, float partialTicks) {
        renderEntityTrail(poseStack, builder, trailPointBuilder, entity, t -> primaryColor, t -> secondaryColor, scaleScalar, alphaScalar, partialTicks);
    }

    public static void renderEntityTrail(PoseStack poseStack, WorldVFXBuilder builder, TrailPointBuilder trailPointBuilder, Entity entity, Function<Float, Color> primaryColor, Function<Float, Color> secondaryColor, float scaleScalar, float alphaScalar, float partialTicks) {
        poseStack.pushPose();
        float trailOffsetX = (float) Mth.lerp(partialTicks, entity.xOld, entity.getX());
        float trailOffsetY = (float) Mth.lerp(partialTicks, entity.yOld, entity.getY());
        float trailOffsetZ = (float) Mth.lerp(partialTicks, entity.zOld, entity.getZ());
        poseStack.translate(-trailOffsetX, -trailOffsetY, -trailOffsetZ);
        float size = 0.5f * scaleScalar;
        float alpha = 0.9f * alphaScalar;
        builder.setAlpha(alpha)
                .renderTrail(trailPointBuilder, f -> size, f -> builder.setAlpha(alpha * f).setColor(ColorHelper.colorLerp(Easing.SINE_IN, f * 2f, secondaryColor.apply(f), primaryColor.apply(f))));
        poseStack.translate(trailOffsetX, trailOffsetY, trailOffsetZ);
        poseStack.popPose();
    }
}

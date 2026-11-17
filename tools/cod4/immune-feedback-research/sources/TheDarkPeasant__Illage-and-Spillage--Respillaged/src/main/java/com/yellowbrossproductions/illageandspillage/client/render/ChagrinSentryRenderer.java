package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.yellowbrossproductions.illageandspillage.client.model.ChagrinSentryModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.engineer.ChagrinSentryGlowLayer;
import com.yellowbrossproductions.illageandspillage.entities.ChagrinSentryEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Pose;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class ChagrinSentryRenderer extends MobRenderer<ChagrinSentryEntity, ChagrinSentryModel<ChagrinSentryEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/engineer/chagrin_sentry.png");

    public ChagrinSentryRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new ChagrinSentryModel<>(renderManagerIn.bakeLayer(ChagrinSentryModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new ChagrinSentryGlowLayer<>(this));
    }

    @Override
    protected float getFlipDegrees(ChagrinSentryEntity p_115337_) {
        return 0;
    }

    @Override
    protected void setupRotations(ChagrinSentryEntity entity, PoseStack poseStack, float ageInTicks, float rotationYaw, float partialTicks) {
        if (!entity.hasPose(Pose.SLEEPING)) {
            poseStack.mulPose(Axis.YP.rotationDegrees(180.0F));
        }

        entity.setPartialTicks(partialTicks);

        if (entity.deathTime > 0) {
            float v = ((float) entity.deathTime + partialTicks - 1.0F) / 20.0F * 1.6F;
            v = Mth.sqrt(v);
            if (v > 1.0F) {
                v = 1.0F;
            }

            poseStack.mulPose(Axis.ZP.rotationDegrees(v * this.getFlipDegrees(entity)));
        } else if (isEntityUpsideDown(entity)) {
            poseStack.translate(0.0F, entity.getBbHeight() + 0.1F, 0.0F);
            poseStack.mulPose(Axis.ZP.rotationDegrees(180.0F));
        }
    }

    public ResourceLocation getTextureLocation(ChagrinSentryEntity p_110775_1_) {
        return TEXTURE;
    }
}

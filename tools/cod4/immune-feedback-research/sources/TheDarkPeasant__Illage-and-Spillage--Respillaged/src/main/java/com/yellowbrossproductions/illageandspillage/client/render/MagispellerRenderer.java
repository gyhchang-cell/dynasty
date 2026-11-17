package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.MagispellerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.HeadItemLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.magispeller.*;
import com.yellowbrossproductions.illageandspillage.entities.MagispellerEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;

import java.util.Calendar;

@OnlyIn(Dist.CLIENT)
public class MagispellerRenderer extends MobRenderer<MagispellerEntity, MagispellerModel<MagispellerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller.png");
    private static final ResourceLocation NOTHING = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");
    private static final ResourceLocation CHRISTMAS = new ResourceLocation("illageandspillage", "textures/entity/magispeller/christmas/magispeller_christmas.png");
    private static final ResourceLocation BALLOON = new ResourceLocation("illageandspillage", "textures/entity/magispeller/balloon.png");

    public MagispellerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new MagispellerModel<>(renderManagerIn.bakeLayer(MagispellerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new MagispellerArmorLayer<>(this));
        this.addLayer(new MagispellerFakerLayer<>(this));
        this.addLayer(new MagispellerFireLayer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new MagispellerFireGlowLayer<>(this));
        this.addLayer(new MagispellerLifestealLayer<>(this));
        this.addLayer(new MagispellerFakerGlowLayer<>(this));
        this.addLayer(new MagispellerFangrunLayer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new MagispellerFangrunGlowLayer<>(this));
        this.addLayer(new MagispellerDispenserLayer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new MagispellerDispenserGlowLayer<>(this));
        this.addLayer(new MagispellerHealLayer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new MagispellerHealGlowLayer<>(this));
        this.addLayer(new MagispellerCough1Layer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new MagispellerCough2Layer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new MagispellerCough3Layer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new HeadItemLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
        this.addLayer(new ItemInHandLayer<>(this, renderManagerIn.getItemInHandRenderer()) {
            public void render(PoseStack p_116352_, MultiBufferSource p_116353_, int p_116354_, MagispellerEntity p_116355_, float p_116356_, float p_116357_, float p_116358_, float p_116359_, float p_116360_, float p_116361_) {
                if (p_116355_.shouldShowArms() || p_116355_.isFaking()) {
                    super.render(p_116352_, p_116353_, p_116354_, p_116355_, p_116356_, p_116357_, p_116358_, p_116359_, p_116360_, p_116361_);
                }

            }
        });
    }

    public void render(MagispellerEntity p_115455_, float p_115456_, float p_115457_, PoseStack poseStack, MultiBufferSource p_115459_, int light) {
        super.render(p_115455_, p_115456_, p_115457_, poseStack, p_115459_, light);
        float f1 = p_115455_.isBalloon() ? 1.0F : 0.0F;
        VertexConsumer ivertexbuilder = p_115459_.getBuffer(RenderType.entityTranslucent(this.getBalloonTextureLocation()));
        poseStack.pushPose();
        poseStack.translate(0.0, 3.2, 0.0);
        this.renderBall(f1, poseStack, ivertexbuilder, light);
        poseStack.popPose();
    }

    private void renderBall(float f1, PoseStack matrixStackIn, VertexConsumer builder, int packedLightIn) {
        matrixStackIn.pushPose();
        Quaternionf quat = this.entityRenderDispatcher.cameraOrientation();
        matrixStackIn.mulPose(quat);
        this.renderFlatQuad(f1, matrixStackIn, builder, packedLightIn);
        matrixStackIn.popPose();
    }

    private void renderFlatQuad(float f1, PoseStack matrixStackIn, VertexConsumer builder, int packedLightIn) {
        float minU = 10.0F;
        float minV = 0.0F;
        float maxU = minU + 1.0F;
        float maxV = minV + 1.0F;
        PoseStack.Pose matrixstack$entry = matrixStackIn.last();
        Matrix4f matrix4f = matrixstack$entry.pose();
        Matrix3f matrix3f = matrixstack$entry.normal();
        this.drawVertex(matrix4f, matrix3f, builder, -0.75F * -f1, -0.75F * -f1, 0.0F, minU, minV, 1.0F, packedLightIn);
        this.drawVertex(matrix4f, matrix3f, builder, -0.75F * -f1, 0.75F * -f1, 0.0F, minU, maxV, 1.0F, packedLightIn);
        this.drawVertex(matrix4f, matrix3f, builder, 0.75F * -f1, 0.75F * -f1, 0.0F, maxU, maxV, 1.0F, packedLightIn);
        this.drawVertex(matrix4f, matrix3f, builder, 0.75F * -f1, -0.75F * -f1, 0.0F, maxU, minV, 1.0F, packedLightIn);
    }

    public void drawVertex(Matrix4f matrix, Matrix3f normals, VertexConsumer vertexBuilder, float offsetX, float offsetY, float offsetZ, float textureX, float textureY, float alpha, int packedLightIn) {
        vertexBuilder.vertex(matrix, offsetX, offsetY, offsetZ).color(1.0F, 1.0F, 1.0F, alpha).uv(textureX, textureY).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(packedLightIn).normal(normals, 0.0F, 1.0F, 0.0F).endVertex();
    }

    public ResourceLocation getBalloonTextureLocation() {
        return BALLOON;
    }

    public ResourceLocation getTextureLocation(MagispellerEntity p_110775_1_) {
        if (p_110775_1_.isFaking()) {
            return NOTHING;
        } else {
            Calendar calendar = Calendar.getInstance();
            return calendar.get(Calendar.MONTH) + 1 == 12 ? CHRISTMAS : TEXTURE;
        }
    }

    protected float getFlipDegrees(MagispellerEntity p_115337_) {
        return super.getFlipDegrees(p_115337_);
    }
}

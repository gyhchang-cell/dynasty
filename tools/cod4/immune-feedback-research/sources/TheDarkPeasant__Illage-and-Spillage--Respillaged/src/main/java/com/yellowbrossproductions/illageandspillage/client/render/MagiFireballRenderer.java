package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.entities.projectile.MagiFireballEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;

import java.util.Random;

public class MagiFireballRenderer extends EntityRenderer<MagiFireballEntity> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magi_fireball.png");
    private final Random random = new Random();

    public MagiFireballRenderer(EntityRendererProvider.Context p_174008_) {
        super(p_174008_);
    }

    public Vec3 getRenderOffset(MagiFireballEntity p_114483_, float p_114484_) {
        return new Vec3(this.random.nextGaussian() * 0.02, this.random.nextGaussian() * 0.02, this.random.nextGaussian() * 0.02);
    }

    public void render(MagiFireballEntity fireball, float entityYaw, float delta, PoseStack poseStack, MultiBufferSource p_114489_, int light) {
        float f = (float) fireball.tickCount / 35.0F;
        float f1 = Math.min(f, 1.0F);
        VertexConsumer ivertexbuilder = p_114489_.getBuffer(RenderType.entityTranslucent(this.getTextureLocation(fireball)));
        poseStack.pushPose();
        poseStack.translate(0.0, 0.2, 0.0);
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
        this.drawVertex(matrix4f, matrix3f, builder, -0.75F * f1, -0.75F * f1, 0.0F, minU, minV, 1.0F, packedLightIn);
        this.drawVertex(matrix4f, matrix3f, builder, -0.75F * f1, 0.75F * f1, 0.0F, minU, maxV, 1.0F, packedLightIn);
        this.drawVertex(matrix4f, matrix3f, builder, 0.75F * f1, 0.75F * f1, 0.0F, maxU, maxV, 1.0F, packedLightIn);
        this.drawVertex(matrix4f, matrix3f, builder, 0.75F * f1, -0.75F * f1, 0.0F, maxU, minV, 1.0F, packedLightIn);
    }

    public void drawVertex(Matrix4f matrix, Matrix3f normals, VertexConsumer vertexBuilder, float offsetX, float offsetY, float offsetZ, float textureX, float textureY, float alpha, int packedLightIn) {
        vertexBuilder.vertex(matrix, offsetX, offsetY, offsetZ).color(1.0F, 1.0F, 1.0F, alpha).uv(textureX, textureY).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(packedLightIn).normal(normals, 0.0F, 1.0F, 0.0F).endVertex();
    }

    public ResourceLocation getTextureLocation(MagiFireballEntity magiFireballEntity) {
        return TEXTURE;
    }
}

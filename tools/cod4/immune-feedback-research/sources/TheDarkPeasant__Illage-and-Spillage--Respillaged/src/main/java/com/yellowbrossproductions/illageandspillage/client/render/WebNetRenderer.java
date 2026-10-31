package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.WebNetModel;
import com.yellowbrossproductions.illageandspillage.entities.projectile.WebNetEntity;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;

public class WebNetRenderer extends MobRenderer<WebNetEntity, WebNetModel<WebNetEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/web_net.png");

    public WebNetRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new WebNetModel<>(renderManagerIn.bakeLayer(WebNetModel.LAYER_LOCATION)), 0.0F);
    }

    public ResourceLocation getTextureLocation(WebNetEntity p_114482_) {
        return TEXTURE;
    }

    public void render(WebNetEntity p_114485_, float p_114486_, float p_114487_, PoseStack p_114488_, MultiBufferSource p_114489_, int p_114490_) {
        if (!p_114485_.isInvisible()) {
            this.renderLeash(p_114485_, p_114487_, p_114488_, p_114489_, p_114485_);
        }

        super.render(p_114485_, p_114486_, p_114487_, p_114488_, p_114489_, p_114490_);
    }

    private void renderLeash(WebNetEntity web, float partialTicks, PoseStack poseStack, MultiBufferSource bufferSource, WebNetEntity netEntity) {
        poseStack.pushPose();
        double rotation = (double) (Mth.lerp(partialTicks, web.yRotO, web.getYRot()) * ((float) Math.PI / 180F)) + (Math.PI / 2D);
        Vec3 vec31 = new Vec3(0.0D, web.getEyeHeight() + 0.75, 0);
        double d1 = Math.cos(rotation) * vec31.z + Math.sin(rotation) * vec31.x;
        double d2 = Math.sin(rotation) * vec31.z - Math.cos(rotation) * vec31.x;
        double d3 = Mth.lerp(partialTicks, web.xo, web.getX()) + d1;
        double d4 = Mth.lerp(partialTicks, web.yo, web.getY()) + vec31.y;
        double d5 = Mth.lerp(partialTicks, web.zo, web.getZ()) + d2;
        poseStack.translate(d1, vec31.y, d2);
        float deltaX = (float) (netEntity.getAttachPoint().x - d3);
        float deltaY = (float) (netEntity.getAttachPoint().y - d4);
        float deltaZ = (float) (netEntity.getAttachPoint().z - d5);
        VertexConsumer vertexConsumer = bufferSource.getBuffer(RenderType.leash());
        Matrix4f matrix4f = poseStack.last().pose();
        float f4 = (float) (Mth.fastInvSqrt(deltaX * deltaX + deltaZ * deltaZ) * 0.025F / 2.0F);
        float offsetX = deltaZ * f4;
        float offsetZ = deltaX * f4;
        BlockPos blockpos = BlockPos.containing(web.getEyePosition(partialTicks));
        BlockPos blockpos1 = BlockPos.containing(netEntity.getAttachPoint());
        int blockLightStart = this.getBlockLightLevel(web, blockpos);
        int blockLightEnd = blockLightLevel(netEntity, blockpos1);
        int skyLightStart = web.level().getBrightness(LightLayer.SKY, blockpos);
        int skyLightEnd = web.level().getBrightness(LightLayer.SKY, blockpos1);

        for (int i = 0; i <= 24; ++i) {
            addVertexPair(vertexConsumer, matrix4f, deltaX, deltaY, deltaZ, blockLightStart, blockLightEnd, skyLightStart, skyLightEnd, 0.025F, 0.025F, offsetX, offsetZ, i, false);
        }

        for (int i = 24; i >= 0; --i) {
            addVertexPair(vertexConsumer, matrix4f, deltaX, deltaY, deltaZ, blockLightStart, blockLightEnd, skyLightStart, skyLightEnd, 0.025F, 0.0F, offsetX, offsetZ, i, true);
        }

        poseStack.popPose();
    }

    private static void addVertexPair(VertexConsumer vertexConsumer, Matrix4f matrix4f, float deltaX, float deltaY, float deltaZ, int blockLightStart, int blockLightEnd, int skyLightStart, int skyLightEnd, float widthStart, float widthEnd, float offsetX, float offsetZ, int segment, boolean flag) {
        float f = (float) segment / 24.0F;
        int blockLight = (int) Mth.lerp(f, (float) blockLightStart, (float) blockLightEnd);
        int skyLight = (int) Mth.lerp(f, (float) skyLightStart, (float) skyLightEnd);
        int packedLight = LightTexture.pack(blockLight, skyLight);
        float brightness = segment % 2 == (flag ? 1 : 0) ? 0.7F : 1.0F;
        float posX = deltaX * f;
        float posY = deltaY * f;
        float posZ = deltaZ * f;
        vertexConsumer.vertex(matrix4f, posX - offsetX, posY + widthEnd, posZ + offsetZ).color(brightness, brightness, brightness, 1.0F).uv2(packedLight).endVertex();
        vertexConsumer.vertex(matrix4f, posX + offsetX, posY + widthStart - widthEnd, posZ - offsetZ).color(brightness, brightness, brightness, 1.0F).uv2(packedLight).endVertex();
    }

    private int blockLightLevel(Entity p_114496_, BlockPos p_114497_) {
        return p_114496_.level().getBrightness(LightLayer.BLOCK, p_114497_);
    }

    @Override
    public Vec3 getRenderOffset(WebNetEntity p_114483_, float p_114484_) {
        return new Vec3(0, -0.8, 0);
    }
}
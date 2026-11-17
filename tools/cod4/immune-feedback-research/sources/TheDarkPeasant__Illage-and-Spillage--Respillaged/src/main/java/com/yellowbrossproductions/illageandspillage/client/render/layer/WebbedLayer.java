package com.yellowbrossproductions.illageandspillage.client.render.layer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class WebbedLayer<T extends LivingEntity, M extends EntityModel<T>> extends RenderLayer<T, M> {
    public static final ResourceLocation WEBBED = new ResourceLocation("illageandspillage", "textures/entity/freakager/webbed_layer.png");

    public WebbedLayer(RenderLayerParent<?, ?> parent) {
        super((RenderLayerParent<T, M>) parent);
    }

    public void render(PoseStack poseStackIn, MultiBufferSource bufferIn, int packedLightIn, T entitylivingbaseIn,
                       float limbSwing, float limbSwingAmount, float partialTicks, float ageInTicks, float netHeadYaw,
                       float headPitch) {
        if (EntityUtil.isWebbed(entitylivingbaseIn) && !entitylivingbaseIn.isInvisible()) {
            EntityModel<T> entityModel = this.getParentModel();
            entityModel.prepareMobModel(entitylivingbaseIn, limbSwing, limbSwingAmount, partialTicks);
            this.getParentModel().copyPropertiesTo(entityModel);
            VertexConsumer vertexConsumer = bufferIn.getBuffer(RenderType.entityTranslucent(WEBBED));
            entityModel.setupAnim(entitylivingbaseIn, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
            entityModel.renderToBuffer(poseStackIn, vertexConsumer, packedLightIn, OverlayTexture.NO_OVERLAY,
                    1.0F, 1.0F, 1.0F, 1.0F);
        }
    }
}
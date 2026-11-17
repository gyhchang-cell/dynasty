package com.yellowbrossproductions.illageandspillage.client.render.layer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.HayArmorModel;
import com.yellowbrossproductions.illageandspillage.util.EntityUtil;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class HayArmorLayer<T extends LivingEntity, M extends EntityModel<T>> extends RenderLayer<T, M> {
    public static final ResourceLocation HAY_ARMOR = new ResourceLocation("illageandspillage", "textures/entity/preserver.png");
    private final EntityModel<T> hayModel;

    public HayArmorLayer(RenderLayerParent<?, ?> parent) {
        super((RenderLayerParent<T, M>) parent);
        this.hayModel = new HayArmorModel<>(Minecraft.getInstance().getEntityModels().bakeLayer(HayArmorModel.LAYER_LOCATION));
    }

    @Override
    public void render(PoseStack matrixStackIn, MultiBufferSource bufferIn, int packedLightIn, T entitylivingbaseIn, float limbSwing, float limbSwingAmount, float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
        if (EntityUtil.isPreserved(entitylivingbaseIn) && !entitylivingbaseIn.isInvisible()) {
            this.getParentModel().copyPropertiesTo(this.hayModel);
            this.hayModel.prepareMobModel(entitylivingbaseIn, limbSwing, limbSwingAmount, partialTicks);
            this.hayModel.setupAnim(entitylivingbaseIn, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
            VertexConsumer ivertexbuilder = bufferIn.getBuffer(RenderType.entityTranslucent(HAY_ARMOR));
            this.hayModel.renderToBuffer(matrixStackIn, ivertexbuilder, packedLightIn, LivingEntityRenderer.getOverlayCoords(entitylivingbaseIn, 0.0F), 1.0F, 1.0F, 1.0F, 1.0F);
        }
    }
}
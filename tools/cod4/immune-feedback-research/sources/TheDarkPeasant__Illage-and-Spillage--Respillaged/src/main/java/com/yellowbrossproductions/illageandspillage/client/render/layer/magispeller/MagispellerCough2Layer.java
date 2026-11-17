package com.yellowbrossproductions.illageandspillage.client.render.layer.magispeller;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.MagispellerModel;
import com.yellowbrossproductions.illageandspillage.entities.MagispellerEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.EntityModelSet;
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
public class MagispellerCough2Layer<T extends LivingEntity> extends RenderLayer<T, MagispellerModel<T>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_cough2.png");
    private final EntityModel<T> magiModel;

    public MagispellerCough2Layer(RenderLayerParent<T, MagispellerModel<T>> p_i226039_1_, EntityModelSet crap) {
        super(p_i226039_1_);
        this.magiModel = new MagispellerModel<>(crap.bakeLayer(MagispellerModel.LAYER_LOCATION));
    }

    public void render(PoseStack matrixStackIn, MultiBufferSource bufferIn, int packedLightIn, T entitylivingbaseIn, float limbSwing, float limbSwingAmount, float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entitylivingbaseIn instanceof MagispellerEntity && ((MagispellerEntity)entitylivingbaseIn).getGlowState() == 8 && !entitylivingbaseIn.isInvisible()) {
            this.getParentModel().copyPropertiesTo(this.magiModel);
            this.magiModel.prepareMobModel(entitylivingbaseIn, limbSwing, limbSwingAmount, partialTicks);
            this.magiModel.setupAnim(entitylivingbaseIn, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
            VertexConsumer ivertexbuilder = bufferIn.getBuffer(RenderType.entityTranslucent(TEXTURE));
            this.magiModel.renderToBuffer(matrixStackIn, ivertexbuilder, packedLightIn, LivingEntityRenderer.getOverlayCoords(entitylivingbaseIn, 0.0F), 1.0F, 1.0F, 1.0F, 1.0F);
        }

    }
}

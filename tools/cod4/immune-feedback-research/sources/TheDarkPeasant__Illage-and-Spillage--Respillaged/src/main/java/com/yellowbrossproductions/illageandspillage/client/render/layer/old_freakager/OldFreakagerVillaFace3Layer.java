package com.yellowbrossproductions.illageandspillage.client.render.layer.old_freakager;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.client.model.OldFreakagerModel;
import com.yellowbrossproductions.illageandspillage.entities.OldFreakagerEntity;
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
public class OldFreakagerVillaFace3Layer<T extends LivingEntity> extends RenderLayer<T, OldFreakagerModel<T>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/old/intro3.png");
    private final EntityModel<T> freakamodel;

    public OldFreakagerVillaFace3Layer(RenderLayerParent<T, OldFreakagerModel<T>> p_i226039_1_, EntityModelSet crap) {
        super(p_i226039_1_);
        this.freakamodel = new OldFreakagerModel<>(crap.bakeLayer(OldFreakagerModel.LAYER_LOCATION));
    }

    public void render(PoseStack matrixStackIn, MultiBufferSource bufferIn, int packedLightIn, T entitylivingbaseIn, float limbSwing, float limbSwingAmount, float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entitylivingbaseIn instanceof OldFreakagerEntity && ((OldFreakagerEntity) entitylivingbaseIn).getVillagerFace() == 3 && !entitylivingbaseIn.isInvisible()) {
            (this.getParentModel()).copyPropertiesTo(this.freakamodel);
            this.freakamodel.prepareMobModel(entitylivingbaseIn, limbSwing, limbSwingAmount, partialTicks);
            this.freakamodel.setupAnim(entitylivingbaseIn, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
            VertexConsumer ivertexbuilder = bufferIn.getBuffer(RenderType.entityTranslucent(TEXTURE));
            this.freakamodel.renderToBuffer(matrixStackIn, ivertexbuilder, packedLightIn, LivingEntityRenderer.getOverlayCoords(entitylivingbaseIn, 0.0F), 1.0F, 1.0F, 1.0F, 1.0F);
        }

    }
}

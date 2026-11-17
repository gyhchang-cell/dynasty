package com.yellowbrossproductions.illageandspillage.client.render.layer.freakager;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.client.model.FreakagerModel;
import com.yellowbrossproductions.illageandspillage.entities.FreakagerEntity;
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
public class FreakagerVillaFaceLayer<T extends LivingEntity> extends RenderLayer<T, FreakagerModel<T>> {
    private static final ResourceLocation FACE1 = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/villaface/villager3.png");
    private static final ResourceLocation FACE2 = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/villaface/villager2.png");
    private static final ResourceLocation FACE3 = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/villaface/villager4.png");
    private static final ResourceLocation FACE4 = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/villaface/villager6.png");
    private static final ResourceLocation FACE5 = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/villaface/villager1.png");
    private static final ResourceLocation FACE6 = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/villaface/villager5.png");
    private final EntityModel<T> freakamodel;

    public FreakagerVillaFaceLayer(RenderLayerParent<T, FreakagerModel<T>> p_i226039_1_, EntityModelSet crap) {
        super(p_i226039_1_);
        this.freakamodel = new FreakagerModel<>(crap.bakeLayer(FreakagerModel.LAYER_LOCATION));
    }

    @Override
    public void render(PoseStack matrixStackIn, MultiBufferSource bufferIn, int packedLightIn, T entitylivingbaseIn, float limbSwing, float limbSwingAmount, float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
        if (entitylivingbaseIn instanceof FreakagerEntity freakager && !freakager.isInvisible()) {
            this.getParentModel().copyPropertiesTo(this.freakamodel);
            this.freakamodel.prepareMobModel(entitylivingbaseIn, limbSwing, limbSwingAmount, partialTicks);
            this.freakamodel.setupAnim(entitylivingbaseIn, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
            VertexConsumer ivertexbuilder = bufferIn.getBuffer(RenderType.entityTranslucent(this.getFace(freakager.getVillagerFace())));
            this.freakamodel.renderToBuffer(matrixStackIn, ivertexbuilder, packedLightIn, LivingEntityRenderer.getOverlayCoords(entitylivingbaseIn, 0.0F), 1.0F, 1.0F, 1.0F, 1.0F);
        }
    }

    private ResourceLocation getFace(int get) {
        return switch (get) {
            case 1 -> FACE2;
            case 2 -> FACE3;
            case 3 -> FACE4;
            case 4 -> FACE5;
            case 5 -> FACE6;
            default -> FACE1;
        };
    }
}
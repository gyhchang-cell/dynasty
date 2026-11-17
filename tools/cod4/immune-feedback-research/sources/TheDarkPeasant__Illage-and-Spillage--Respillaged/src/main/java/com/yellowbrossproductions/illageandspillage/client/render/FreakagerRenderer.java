package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.client.model.FreakagerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.HeadItemLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.freakager.FreakagerArmorLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.freakager.FreakagerVillaFaceLayer;
import com.yellowbrossproductions.illageandspillage.entities.FreakagerEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class FreakagerRenderer<T extends FreakagerEntity> extends MobRenderer<T, FreakagerModel<T>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/freakager.png");
    private static final ResourceLocation EYE = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/eye.png");
    private static final ResourceLocation ANNOYED = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/annoyed.png");
    private static final ResourceLocation ANGRY = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/angry.png");
    private static final ResourceLocation ANGRY_EYE = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/angry_eye.png");

    public FreakagerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new FreakagerModel<>(renderManagerIn.bakeLayer(FreakagerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new FreakagerVillaFaceLayer<>(this, renderManagerIn.getModelSet()));
        this.addLayer(new FreakagerArmorLayer<>(this));
        this.addLayer(new HeadItemLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
        this.addLayer(new ItemInHandLayer<>(this, renderManagerIn.getItemInHandRenderer()) {
            public void render(PoseStack p_116352_, MultiBufferSource p_116353_, int p_116354_, T p_116355_, float p_116356_, float p_116357_, float p_116358_, float p_116359_, float p_116360_, float p_116361_) {
                if (p_116355_.shouldShowArms()) {
                    super.render(p_116352_, p_116353_, p_116354_, p_116355_, p_116356_, p_116357_, p_116358_, p_116359_, p_116360_, p_116361_);
                }

            }
        });
    }

    @Override
    public boolean shouldRender(T p_115468_, Frustum p_115469_, double p_115470_, double p_115471_, double p_115472_) {
        return !p_115468_.isPhasedOut() && super.shouldRender(p_115468_, p_115469_, p_115470_, p_115471_, p_115472_);
    }

    @Override
    protected float getFlipDegrees(T p_115337_) {
        return p_115337_.shouldPlayTransition() ? 0 : super.getFlipDegrees(p_115337_);
    }

    @Override
    public ResourceLocation getTextureLocation(FreakagerEntity p_110775_1_) {
        return switch (p_110775_1_.getFreakagerFace()) {
            case 1 -> EYE;
            case 2 -> ANNOYED;
            case 3 -> ANGRY;
            case 4 -> ANGRY_EYE;
            default -> TEXTURE;
        };
    }
}

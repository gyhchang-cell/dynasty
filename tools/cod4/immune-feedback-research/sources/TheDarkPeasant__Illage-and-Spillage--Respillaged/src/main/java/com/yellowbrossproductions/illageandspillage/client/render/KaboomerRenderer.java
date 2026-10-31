package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.KaboomerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.KaboomerHissLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.KaboomerLayer;
import com.yellowbrossproductions.illageandspillage.entities.KaboomerEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class KaboomerRenderer extends MobRenderer<KaboomerEntity, KaboomerModel<KaboomerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");

    public KaboomerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new KaboomerModel<>(renderManagerIn.bakeLayer(KaboomerModel.LAYER_LOCATION)), 0.0F);
        this.addLayer(new KaboomerLayer<>(this));
        this.addLayer(new KaboomerHissLayer<>(this));
    }

    protected void scale(KaboomerEntity p_114046_, PoseStack p_114047_, float p_114048_) {
        float $$3 = p_114046_.getSwelling(p_114048_);
        float $$4 = 1.0F + Mth.sin($$3 * 200.0F) * $$3 * 0.01F;
        $$3 = Mth.clamp($$3, 0.0F, 1.0F);
        $$3 *= $$3;
        $$3 *= $$3;
        float $$5 = (1.0F + $$3 * 0.6F) * $$4;
        float $$6 = (1.0F + $$3 * 0.2F) / $$4;
        p_114047_.scale($$5, $$6, $$5);
    }

    protected float getWhiteOverlayProgress(KaboomerEntity p_114043_, float p_114044_) {
        float $$2 = p_114043_.getSwelling(p_114044_);
        return (int) ($$2 * 20.0F) % 2 == 0 ? 0.0F : Mth.clamp($$2, 0.5F, 1.0F);
    }

    public ResourceLocation getTextureLocation(KaboomerEntity p_110775_1_) {
        return TEXTURE;
    }
}

package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.IllagerSoulModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.IllagerSoulAngelLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.IllagerSoulDevilLayer;
import com.yellowbrossproductions.illageandspillage.entities.IllagerSoulEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class IllagerSoulRenderer extends MobRenderer<IllagerSoulEntity, IllagerSoulModel<IllagerSoulEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");

    public IllagerSoulRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new IllagerSoulModel<>(renderManagerIn.bakeLayer(IllagerSoulModel.LAYER_LOCATION)), 0.0F);
        this.addLayer(new IllagerSoulAngelLayer<>(this));
        this.addLayer(new IllagerSoulDevilLayer<>(this));
    }

    protected void scale(IllagerSoulEntity p_114046_, PoseStack p_114047_, float p_114048_) {
        float f = p_114046_.getSwelling(p_114048_);
        float f1 = 1.0F + Mth.sin(f * 100.0F) * f * 0.01F;
        f = Mth.clamp(f, 0.0F, 1.0F);
        f *= f;
        f *= f;
        float f3 = (f + 0.01F) / f1;
        p_114047_.scale(1.0F, f3, 1.0F);
    }

    public ResourceLocation getTextureLocation(IllagerSoulEntity p_110775_1_) {
        return TEXTURE;
    }
}

package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.MagiHealModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.magispeller.MagiHealRingLayer;
import com.yellowbrossproductions.illageandspillage.entities.MagiHealEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class MagiHealRenderer extends MobRenderer<MagiHealEntity, MagiHealModel<MagiHealEntity>> {
    public static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");

    public MagiHealRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new MagiHealModel<>(renderManagerIn.bakeLayer(MagiHealModel.LAYER_LOCATION)), 0.0F);
        this.addLayer(new MagiHealRingLayer<>(this));
    }

    protected void scale(MagiHealEntity p_115314_, PoseStack p_115315_, float p_115316_) {
        float p = Math.min((float) p_115314_.tickCount / 6.0F, 1.0F);
        float p2 = 1.0F + (float) (p_115314_.tickCount - 6) / 200.0F;
        float multiplier = Math.max(0.0F, 1.0F - (float) (p_115314_.tickCount - 130) / 10.0F);
        float p4 = p2 * multiplier;
        float p3 = p_115314_.tickCount <= 6 ? p : p2;
        float p5 = p_115314_.tickCount <= 130 ? p3 : p4;
        p_115315_.scale(p5, 1.0F, p5);
    }

    public ResourceLocation getTextureLocation(MagiHealEntity p_110775_1_) {
        return TEXTURE;
    }
}

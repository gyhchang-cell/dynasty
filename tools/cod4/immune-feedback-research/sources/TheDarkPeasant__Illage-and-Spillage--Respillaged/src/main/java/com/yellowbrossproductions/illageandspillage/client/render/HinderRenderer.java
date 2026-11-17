package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.HinderModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.engineer.HinderGlowLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.engineer.HinderHealLayer;
import com.yellowbrossproductions.illageandspillage.entities.HinderEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class HinderRenderer extends MobRenderer<HinderEntity, HinderModel<HinderEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/engineer/hinder.png");
    private static final ResourceLocation HEALING = new ResourceLocation("illageandspillage", "textures/entity/engineer/hinder_heal.png");

    public HinderRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new HinderModel<>(renderManagerIn.bakeLayer(HinderModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new HinderGlowLayer<>(this));
        this.addLayer(new HinderHealLayer<>(this));
    }

    @Override
    protected float getFlipDegrees(HinderEntity p_115337_) {
        return 0;
    }

    public ResourceLocation getTextureLocation(HinderEntity p_110775_1_) {
        return p_110775_1_.isHealing() ? HEALING : TEXTURE;
    }
}

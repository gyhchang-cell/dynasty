package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.SniperModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.engineer.SniperGlowLayer;
import com.yellowbrossproductions.illageandspillage.entities.SniperEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;

public class SniperRenderer extends MobRenderer<SniperEntity, SniperModel<SniperEntity>> {
    private static final ResourceLocation SNIPER = new ResourceLocation("illageandspillage", "textures/entity/engineer/factory/sniper.png");

    public SniperRenderer(EntityRendererProvider.Context context) {
        super(context, new SniperModel<>(context.bakeLayer(SniperModel.LAYER_LOCATION)), 0.3F);
        this.addLayer(new SniperGlowLayer<>(this));
    }

    @Override
    protected float getFlipDegrees(SniperEntity p_115337_) {
        return 0.0F;
    }

    @Override
    public ResourceLocation getTextureLocation(SniperEntity entity) {
        return SNIPER;
    }
}
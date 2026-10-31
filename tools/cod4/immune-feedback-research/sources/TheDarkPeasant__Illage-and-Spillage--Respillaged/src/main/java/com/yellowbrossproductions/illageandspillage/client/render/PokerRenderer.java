package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.PokerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.engineer.PokerGlowLayer;
import com.yellowbrossproductions.illageandspillage.entities.PokerEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.resources.ResourceLocation;

public class PokerRenderer extends MobRenderer<PokerEntity, PokerModel<PokerEntity>> {
    private static final ResourceLocation POKER = new ResourceLocation("illageandspillage", "textures/entity/engineer/factory/poker.png");

    public PokerRenderer(EntityRendererProvider.Context context) {
        super(context, new PokerModel<>(context.bakeLayer(PokerModel.LAYER_LOCATION)), 0.3F);
        this.addLayer(new PokerGlowLayer<>(this));
        this.addLayer(new ItemInHandLayer<>(this, context.getItemInHandRenderer()));
    }

    @Override
    public ResourceLocation getTextureLocation(PokerEntity entity) {
        return POKER;
    }
}
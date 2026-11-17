package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.PreserverModel;
import com.yellowbrossproductions.illageandspillage.entities.PreserverEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class PreserverRenderer extends MobRenderer<PreserverEntity, PreserverModel<PreserverEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/preserver.png");

    public PreserverRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new PreserverModel<>(renderManagerIn.bakeLayer(PreserverModel.LAYER_LOCATION)), 0.6F);
        this.addLayer(new CustomHeadLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
    }

    public ResourceLocation getTextureLocation(PreserverEntity p_110775_1_) {
        return TEXTURE;
    }
}

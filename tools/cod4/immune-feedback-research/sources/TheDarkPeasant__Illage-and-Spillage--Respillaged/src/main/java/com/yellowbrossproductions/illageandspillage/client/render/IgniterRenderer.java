package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.IgniterModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.igniter.IgniterOverheatLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.igniter.IgniterTorchLayer;
import com.yellowbrossproductions.illageandspillage.entities.IgniterEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class IgniterRenderer extends MobRenderer<IgniterEntity, IgniterModel<IgniterEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/igniter/igniter.png");

    public IgniterRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new IgniterModel<>(renderManagerIn.bakeLayer(IgniterModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new CustomHeadLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
        this.addLayer(new IgniterOverheatLayer<>(this));
        this.addLayer(new IgniterTorchLayer<>(this));
    }

    public ResourceLocation getTextureLocation(IgniterEntity p_110775_1_) {
        return TEXTURE;
    }
}

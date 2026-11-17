package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.EngineerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.HeadItemLayer;
import com.yellowbrossproductions.illageandspillage.entities.EngineerEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class EngineerRenderer extends MobRenderer<EngineerEntity, EngineerModel<EngineerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/engineer/engineer.png");

    public EngineerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new EngineerModel<>(renderManagerIn.bakeLayer(EngineerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new HeadItemLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
    }

    public ResourceLocation getTextureLocation(EngineerEntity p_110775_1_) {
        return TEXTURE;
    }
}

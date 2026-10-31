package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.FactoryModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.engineer.FactoryGlowLayer;
import com.yellowbrossproductions.illageandspillage.entities.FactoryEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class FactoryRenderer extends MobRenderer<FactoryEntity, FactoryModel<FactoryEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/engineer/factory.png");

    public FactoryRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new FactoryModel<>(renderManagerIn.bakeLayer(FactoryModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new FactoryGlowLayer<>(this));
    }

    @Override
    protected float getFlipDegrees(FactoryEntity p_115337_) {
        return 0;
    }

    public ResourceLocation getTextureLocation(FactoryEntity p_110775_1_) {
        return TEXTURE;
    }
}

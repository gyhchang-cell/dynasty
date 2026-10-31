package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.IllashooterModel;
import com.yellowbrossproductions.illageandspillage.entities.IllashooterEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class IllashooterRenderer extends MobRenderer<IllashooterEntity, IllashooterModel<IllashooterEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/illashooter.png");

    public IllashooterRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new IllashooterModel<>(renderManagerIn.bakeLayer(IllashooterModel.LAYER_LOCATION)), 0.5F);
    }

    public ResourceLocation getTextureLocation(IllashooterEntity p_110775_1_) {
        return TEXTURE;
    }
}

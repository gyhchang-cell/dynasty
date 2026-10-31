package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.CrocofangModel;
import com.yellowbrossproductions.illageandspillage.entities.CrocofangEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class CrocofangRenderer extends MobRenderer<CrocofangEntity, CrocofangModel<CrocofangEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/crocofang.png");

    public CrocofangRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new CrocofangModel<>(renderManagerIn.bakeLayer(CrocofangModel.LAYER_LOCATION)), 1.1F);
    }

    public ResourceLocation getTextureLocation(CrocofangEntity p_110775_1_) {
        return TEXTURE;
    }
}

package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.FakerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.FakerLayer;
import com.yellowbrossproductions.illageandspillage.entities.FakeMagispellerEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class FakeMagispellerRenderer extends MobRenderer<FakeMagispellerEntity, FakerModel<FakeMagispellerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");

    public FakeMagispellerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new FakerModel<>(renderManagerIn.bakeLayer(FakerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new FakerLayer<>(this));
        this.addLayer(new CustomHeadLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
        this.addLayer(new ItemInHandLayer<>(this, renderManagerIn.getItemInHandRenderer()));
    }

    @Override
    protected float getFlipDegrees(FakeMagispellerEntity p_115337_) {
        return 0;
    }

    public ResourceLocation getTextureLocation(FakeMagispellerEntity p_110775_1_) {
        return TEXTURE;
    }
}

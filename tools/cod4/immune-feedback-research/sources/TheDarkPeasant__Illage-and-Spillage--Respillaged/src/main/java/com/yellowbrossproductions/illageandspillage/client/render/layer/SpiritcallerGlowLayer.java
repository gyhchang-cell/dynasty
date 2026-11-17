package com.yellowbrossproductions.illageandspillage.client.render.layer;

import com.yellowbrossproductions.illageandspillage.client.model.SpiritcallerModel;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class SpiritcallerGlowLayer<T extends LivingEntity> extends EyesLayer<T, SpiritcallerModel<T>> {
    private static final RenderType LAYER = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/spiritcaller/spiritcaller_overlay.png"));

    public SpiritcallerGlowLayer(RenderLayerParent<T, SpiritcallerModel<T>> p_i226039_1_) {
        super(p_i226039_1_);
    }

    public RenderType renderType() {
        return LAYER;
    }
}

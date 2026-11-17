package com.yellowbrossproductions.illageandspillage.client.render.layer;

import com.yellowbrossproductions.illageandspillage.client.model.ImpModel;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class ImpLayer<T extends LivingEntity> extends EyesLayer<T, ImpModel<T>> {
    private static final RenderType LAYER = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/spiritcaller/imp.png"));

    public ImpLayer(RenderLayerParent<T, ImpModel<T>> p_i226039_1_) {
        super(p_i226039_1_);
    }

    public RenderType renderType() {
        return LAYER;
    }
}

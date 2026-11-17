package com.yellowbrossproductions.illageandspillage.client.render.layer.magispeller;

import com.yellowbrossproductions.illageandspillage.client.model.MagiHealModel;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class MagiHealRingLayer<T extends LivingEntity> extends EyesLayer<T, MagiHealModel<T>> {
    private static final RenderType LAYER = RenderType.eyes(new ResourceLocation("illageandspillage", "textures/entity/magispeller/heal_ring.png"));

    public MagiHealRingLayer(RenderLayerParent<T, MagiHealModel<T>> p_i226039_1_) {
        super(p_i226039_1_);
    }

    public RenderType renderType() {
        return LAYER;
    }
}

package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.ImpModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.ImpLayer;
import com.yellowbrossproductions.illageandspillage.entities.ImpEntity;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class ImpRenderer extends MobRenderer<ImpEntity, ImpModel<ImpEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");

    public ImpRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new ImpModel<>(renderManagerIn.bakeLayer(ImpModel.LAYER_LOCATION)), 0.0F);
        this.addLayer(new ImpLayer<>(this));
    }

    @Override
    public boolean shouldRender(ImpEntity imp, Frustum p_115469_, double p_115470_, double p_115471_, double p_115472_) {
        return imp.tickCount >= 1 + imp.getWaitTime() && super.shouldRender(imp, p_115469_, p_115470_, p_115471_, p_115472_);
    }

    public ResourceLocation getTextureLocation(ImpEntity p_110775_1_) {
        return TEXTURE;
    }
}

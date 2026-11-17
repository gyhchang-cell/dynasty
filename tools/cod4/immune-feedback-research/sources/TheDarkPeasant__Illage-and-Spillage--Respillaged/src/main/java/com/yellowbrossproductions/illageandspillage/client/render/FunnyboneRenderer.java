package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.FunnyboneModel;
import com.yellowbrossproductions.illageandspillage.entities.FunnyboneEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class FunnyboneRenderer extends MobRenderer<FunnyboneEntity, FunnyboneModel<FunnyboneEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/funnybone.png");
    private static final ResourceLocation GOOPY = new ResourceLocation("illageandspillage", "textures/entity/freakager/funnybone_ragno.png");

    public FunnyboneRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new FunnyboneModel<>(renderManagerIn.bakeLayer(FunnyboneModel.LAYER_LOCATION)), 0.4F);
    }

    @Override
    public Vec3 getRenderOffset(FunnyboneEntity p_114483_, float p_114484_) {
        return p_114483_.isGoopy() ? new Vec3(p_114483_.getRandom().nextGaussian() * 0.03, -0.15, p_114483_.getRandom().nextGaussian() * 0.03) : new Vec3(0.0, -0.15, 0.0);
    }

    @Override
    public ResourceLocation getTextureLocation(FunnyboneEntity p_110775_1_) {
        return p_110775_1_.isGoopy() ? GOOPY : TEXTURE;
    }
}

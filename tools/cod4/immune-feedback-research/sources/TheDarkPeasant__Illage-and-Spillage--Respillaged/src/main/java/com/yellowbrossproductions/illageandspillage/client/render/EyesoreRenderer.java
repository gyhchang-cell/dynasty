package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.EyesoreModel;
import com.yellowbrossproductions.illageandspillage.entities.EyesoreEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class EyesoreRenderer extends MobRenderer<EyesoreEntity, EyesoreModel<EyesoreEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/eyesore.png");
    private static final ResourceLocation SCARED = new ResourceLocation("illageandspillage", "textures/entity/freakager/eyesore_shocked.png");

    public EyesoreRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new EyesoreModel<>(renderManagerIn.bakeLayer(EyesoreModel.LAYER_LOCATION)), 0.5F);
    }

    @Override
    public Vec3 getRenderOffset(EyesoreEntity p_114483_, float p_114484_) {
        return p_114483_.isScared() ? new Vec3(p_114483_.getRandom().nextGaussian() * 0.015, 0.0, p_114483_.getRandom().nextGaussian() * 0.015) : super.getRenderOffset(p_114483_, p_114484_);
    }

    @Override
    public ResourceLocation getTextureLocation(EyesoreEntity p_110775_1_) {
        return p_110775_1_.isScared() ? SCARED : TEXTURE;
    }
}

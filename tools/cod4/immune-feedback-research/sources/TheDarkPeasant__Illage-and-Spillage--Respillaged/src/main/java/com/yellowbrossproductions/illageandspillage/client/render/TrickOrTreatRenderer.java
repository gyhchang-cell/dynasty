package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.TrickOrTreatModel;
import com.yellowbrossproductions.illageandspillage.entities.TrickOrTreatEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class TrickOrTreatRenderer extends MobRenderer<TrickOrTreatEntity, TrickOrTreatModel<TrickOrTreatEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/trickortreat.png");
    private static final ResourceLocation GOOPY = new ResourceLocation("illageandspillage", "textures/entity/freakager/trickortreat_ragno.png");
    private static final ResourceLocation OLD = new ResourceLocation("illageandspillage", "textures/entity/freakager/old/trickortreat.png");
    private static final ResourceLocation GOOPY_OLD = new ResourceLocation("illageandspillage", "textures/entity/freakager/old/trickortreat_ragno.png");

    public TrickOrTreatRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new TrickOrTreatModel<>(renderManagerIn.bakeLayer(TrickOrTreatModel.LAYER_LOCATION)), 0.6F);
    }

    protected float getFlipDegrees(TrickOrTreatEntity p_115337_) {
        return 0.0F;
    }

    public Vec3 getRenderOffset(TrickOrTreatEntity p_114483_, float p_114484_) {
        return p_114483_.getGoopy() ? new Vec3(p_114483_.getRandom().nextGaussian() * 0.03, 0.0, p_114483_.getRandom().nextGaussian() * 0.03) : super.getRenderOffset(p_114483_, p_114484_);
    }

    public ResourceLocation getTextureLocation(TrickOrTreatEntity p_110775_1_) {
        return p_110775_1_.isOld() ? p_110775_1_.getGoopy() ? GOOPY_OLD : OLD : p_110775_1_.getGoopy() ? GOOPY : TEXTURE;
    }
}

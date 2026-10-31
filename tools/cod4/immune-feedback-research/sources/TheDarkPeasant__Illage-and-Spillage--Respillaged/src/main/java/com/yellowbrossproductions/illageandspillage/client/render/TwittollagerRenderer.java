package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.TwittollagerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.TwittollagerPhoneLayer;
import com.yellowbrossproductions.illageandspillage.entities.TwittollagerEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class TwittollagerRenderer extends MobRenderer<TwittollagerEntity, TwittollagerModel<TwittollagerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/twittollager/twittollager.png");

    public TwittollagerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new TwittollagerModel<>(renderManagerIn.bakeLayer(TwittollagerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new CustomHeadLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()));
        this.addLayer(new TwittollagerPhoneLayer<>(this));
    }

    public Vec3 getRenderOffset(TwittollagerEntity twittollager, float p_114337_) {
        double d0 = 0.01;
        if (twittollager.getGRRRRRRRRRR() > 0) {
            return new Vec3(twittollager.getRandom().nextGaussian() * 6.666666666666666E-4 * (double) twittollager.getGRRRRRRRRRR(), 0.0, twittollager.getRandom().nextGaussian() * 6.666666666666666E-4 * (double) twittollager.getGRRRRRRRRRR());
        } else if (twittollager.isHmm()) {
            return super.getRenderOffset(twittollager, p_114337_);
        } else {
            return twittollager.isStaring() ? new Vec3(twittollager.getRandom().nextGaussian() * 0.04, 0.0, twittollager.getRandom().nextGaussian() * 0.04) : new Vec3(twittollager.getRandom().nextGaussian() * d0, 0.0, twittollager.getRandom().nextGaussian() * d0);
        }
    }

    public ResourceLocation getTextureLocation(TwittollagerEntity p_110775_1_) {
        return TEXTURE;
    }
}

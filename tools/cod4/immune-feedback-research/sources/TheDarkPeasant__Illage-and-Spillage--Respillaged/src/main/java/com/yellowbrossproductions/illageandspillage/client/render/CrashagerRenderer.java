package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.CrashagerModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.CrashagerGlowLayer;
import com.yellowbrossproductions.illageandspillage.entities.CrashagerEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

import java.util.Random;

@OnlyIn(Dist.CLIENT)
public class CrashagerRenderer extends MobRenderer<CrashagerEntity, CrashagerModel<CrashagerEntity>> {
    private final Random random = new Random();
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");

    public CrashagerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new CrashagerModel<>(renderManagerIn.bakeLayer(CrashagerModel.LAYER_LOCATION)), 0.5F);
        this.addLayer(new CrashagerGlowLayer<>(this));
    }

    public Vec3 getRenderOffset(CrashagerEntity p_225627_1_, float p_225627_2_) {
        if (p_225627_1_.getAttackStage() == 2) {
            return new Vec3(this.random.nextGaussian() * 0.05, 0.0, this.random.nextGaussian() * 0.05);
        } else {
            return super.getRenderOffset(p_225627_1_, p_225627_2_);
        }
    }

    public ResourceLocation getTextureLocation(CrashagerEntity p_110775_1_) {
        return TEXTURE;
    }
}

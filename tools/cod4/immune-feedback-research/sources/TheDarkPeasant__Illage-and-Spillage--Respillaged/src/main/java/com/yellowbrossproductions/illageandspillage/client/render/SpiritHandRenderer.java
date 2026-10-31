package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.SpiritHandModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.SpiritHandEvilLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.SpiritHandLayer;
import com.yellowbrossproductions.illageandspillage.entities.SpiritHandEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

import java.util.Random;

@OnlyIn(Dist.CLIENT)
public class SpiritHandRenderer extends MobRenderer<SpiritHandEntity, SpiritHandModel<SpiritHandEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");
    private final Random random = new Random();

    public SpiritHandRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new SpiritHandModel<>(renderManagerIn.bakeLayer(SpiritHandModel.LAYER_LOCATION)), 0.0F);
        this.addLayer(new SpiritHandLayer<>(this));
        this.addLayer(new SpiritHandEvilLayer<>(this));
    }

    protected void scale(SpiritHandEntity p_115314_, PoseStack p_115315_, float p_115316_) {
        p_115315_.scale(p_115314_.isDeadOrDying() ? 1.0F - (float) p_115314_.deathTime / 20.0F : 1.0F, p_115314_.isDeadOrDying() ? 1.0F + (float) p_115314_.deathTime / 5.0F : 1.0F, p_115314_.isDeadOrDying() ? 1.0F - (float) p_115314_.deathTime / 20.0F : 1.0F);
    }

    protected float getFlipDegrees(SpiritHandEntity p_115337_) {
        return 0.0F;
    }

    public Vec3 getRenderOffset(SpiritHandEntity p_114483_, float p_114484_) {
        return p_114483_.getAttackType() == 2 ? new Vec3(this.random.nextGaussian() * 0.06, this.random.nextGaussian() * 0.06, this.random.nextGaussian() * 0.06) : new Vec3(0.0, (double) (-((float) p_114483_.deathTime / 5.0F) / 2.0F), 0.0);
    }

    public ResourceLocation getTextureLocation(SpiritHandEntity p_110775_1_) {
        return TEXTURE;
    }
}
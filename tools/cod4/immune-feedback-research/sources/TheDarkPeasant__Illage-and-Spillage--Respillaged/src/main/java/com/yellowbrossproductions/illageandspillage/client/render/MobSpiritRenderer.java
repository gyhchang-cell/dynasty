package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.MobSpiritModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.MobSpiritCorruptedLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.MobSpiritEvilLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.MobSpiritGlowLayer;
import com.yellowbrossproductions.illageandspillage.entities.MobSpiritEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

import java.util.Random;

@OnlyIn(Dist.CLIENT)
public class MobSpiritRenderer extends MobRenderer<MobSpiritEntity, MobSpiritModel<MobSpiritEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/magispeller_nothing.png");
    private final Random random = new Random();

    public MobSpiritRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new MobSpiritModel<>(renderManagerIn.bakeLayer(MobSpiritModel.LAYER_LOCATION)), 0.0F);
        this.addLayer(new MobSpiritGlowLayer<>(this));
        this.addLayer(new MobSpiritEvilLayer<>(this));
        this.addLayer(new MobSpiritCorruptedLayer<>(this));
    }

    protected void scale(MobSpiritEntity p_115314_, PoseStack p_115315_, float p_115316_) {
        p_115315_.scale(p_115314_.isDeadOrDying() ? 1.0F - (float) p_115314_.deathTime / 20.0F : 1.0F, p_115314_.isDeadOrDying() ? 1.0F + (float) p_115314_.deathTime / 5.0F : 1.0F, p_115314_.isDeadOrDying() ? 1.0F - (float) p_115314_.deathTime / 20.0F : 1.0F);
    }

    protected float getFlipDegrees(MobSpiritEntity p_115337_) {
        return 0.0F;
    }

    public Vec3 getRenderOffset(MobSpiritEntity p_114483_, float p_114484_) {
        return p_114483_.isSpiritcaller() ? new Vec3(this.random.nextGaussian() * 0.06, this.random.nextGaussian() * 0.06, this.random.nextGaussian() * 0.06) : new Vec3(0.0, (double) (-((float) p_114483_.deathTime / 5.0F) / 2.0F), 0.0);
    }

    public ResourceLocation getTextureLocation(MobSpiritEntity p_110775_1_) {
        return TEXTURE;
    }
}

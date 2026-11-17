package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.yellowbrossproductions.illageandspillage.client.model.AbsorberModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.HeadItemLayer;
import com.yellowbrossproductions.illageandspillage.entities.AbsorberEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class AbsorberRenderer extends MobRenderer<AbsorberEntity, AbsorberModel<AbsorberEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/absorber/absorber1.png");
    private static final ResourceLocation DEGRADE1 = new ResourceLocation("illageandspillage", "textures/entity/absorber/absorber2.png");
    private static final ResourceLocation DEGRADE2 = new ResourceLocation("illageandspillage", "textures/entity/absorber/absorber3.png");
    private static final ResourceLocation DEGRADE3 = new ResourceLocation("illageandspillage", "textures/entity/absorber/absorber4.png");

    public AbsorberRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new AbsorberModel<>(renderManagerIn.bakeLayer(AbsorberModel.LAYER_LOCATION)), 0.8F);
        this.addLayer(new HeadItemLayer<>(this, renderManagerIn.getModelSet(), renderManagerIn.getItemInHandRenderer()) {
            public void render(PoseStack p_116731_, MultiBufferSource p_116732_, int p_116733_, AbsorberEntity p_116734_, float p_116735_, float p_116736_, float p_116737_, float p_116738_, float p_116739_, float p_116740_) {
                super.render(p_116731_, p_116732_, p_116733_, p_116734_, p_116735_, p_116736_, p_116737_, p_116738_, p_116739_, p_116740_);
            }
        });
    }

    protected void setupRotations(AbsorberEntity p_115014_, PoseStack p_115015_, float p_115016_, float p_115017_, float p_115018_) {
        super.setupRotations(p_115014_, p_115015_, p_115016_, p_115017_, p_115018_);
        if (!((double) p_115014_.walkAnimation.speed() < 0.01D)) {
            float f1 = p_115014_.walkAnimation.position(p_115018_) + 6.0F;
            float f2 = (Math.abs(f1 % 13.0F - 6.5F) - 3.25F) / 3.25F;
            p_115015_.mulPose(Axis.ZP.rotationDegrees(6.5F * f2));
        }
    }

    protected float getFlipDegrees(AbsorberEntity p_115337_) {
        return 0.0F;
    }

    public ResourceLocation getTextureLocation(AbsorberEntity p_110775_1_) {
        if (p_110775_1_.getHealth() < p_110775_1_.getMaxHealth() / 4.0F) {
            return DEGRADE3;
        } else if (p_110775_1_.getHealth() < p_110775_1_.getMaxHealth() / 4.0F * 2.0F) {
            return DEGRADE2;
        } else {
            return p_110775_1_.getHealth() < p_110775_1_.getMaxHealth() / 4.0F * 3.0F ? DEGRADE1 : TEXTURE;
        }
    }
}

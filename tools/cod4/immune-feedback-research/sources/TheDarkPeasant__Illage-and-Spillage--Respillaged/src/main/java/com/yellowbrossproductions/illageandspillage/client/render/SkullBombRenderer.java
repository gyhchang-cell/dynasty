package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.SkullBombModel;
import com.yellowbrossproductions.illageandspillage.entities.projectile.SkullBombEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class SkullBombRenderer extends MobRenderer<SkullBombEntity, SkullBombModel<SkullBombEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/skull_bomb.png");

    public SkullBombRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new SkullBombModel<>(renderManagerIn.bakeLayer(SkullBombModel.LAYER_LOCATION)), 0.3F);
    }

    protected void scale(SkullBombEntity p_114046_, PoseStack p_114047_, float p_114048_) {
        float $$3 = p_114046_.getSwelling(p_114048_);
        float $$4 = 1.0F + Mth.sin($$3 * 100.0F) * $$3 * 0.01F;
        $$3 = Mth.clamp($$3, 0.0F, 1.0F);
        $$3 *= $$3;
        $$3 *= $$3;
        float $$5 = (1.0F + $$3 * 0.4F) * $$4;
        float $$6 = (1.0F + $$3 * 0.1F) / $$4;
        p_114047_.scale($$5, $$6, $$5);
    }

    protected float getWhiteOverlayProgress(SkullBombEntity p_114043_, float p_114044_) {
        float $$2 = p_114043_.getSwelling(p_114044_);
        return (int) ($$2 * 10.0F) % 2 == 0 ? 0.0F : Mth.clamp($$2, 0.5F, 1.0F);
    }

    public ResourceLocation getTextureLocation(SkullBombEntity p_110775_1_) {
        return TEXTURE;
    }
}

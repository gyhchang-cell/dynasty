package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.PumpkinBombModel;
import com.yellowbrossproductions.illageandspillage.entities.projectile.PumpkinBombEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class PumpkinBombRenderer extends MobRenderer<PumpkinBombEntity, PumpkinBombModel<PumpkinBombEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/pumpkin_bomb.png");
    private static final ResourceLocation GOOPY = new ResourceLocation("illageandspillage", "textures/entity/freakager/pumpkin_bomb_ragno.png");

    public PumpkinBombRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new PumpkinBombModel<>(renderManagerIn.bakeLayer(PumpkinBombModel.LAYER_LOCATION)), 0.5F);
    }

    protected void scale(PumpkinBombEntity p_114046_, PoseStack p_114047_, float p_114048_) {
        float $$3 = p_114046_.getSwelling(p_114048_);
        float $$4 = 1.0F + Mth.sin($$3 * 100.0F) * $$3 * 0.01F;
        $$3 = Mth.clamp($$3, 0.0F, 1.0F);
        $$3 *= $$3;
        $$3 *= $$3;
        float $$5 = (1.0F + $$3 * 0.4F) * $$4;
        float $$6 = (1.0F + $$3 * 0.1F) / $$4;
        p_114047_.scale($$5, $$6, $$5);
    }

    protected float getWhiteOverlayProgress(PumpkinBombEntity p_114043_, float p_114044_) {
        float $$2 = p_114043_.getSwelling(p_114044_);
        return (int) ($$2 * 10.0F) % 2 == 0 ? 0.0F : Mth.clamp($$2, 0.5F, 1.0F);
    }

    public Vec3 getRenderOffset(PumpkinBombEntity p_114483_, float p_114484_) {
        return p_114483_.getGoopy() ? new Vec3(p_114483_.getRandom().nextGaussian() * 0.03, 0.0, p_114483_.getRandom().nextGaussian() * 0.03) : super.getRenderOffset(p_114483_, p_114484_);
    }

    public ResourceLocation getTextureLocation(PumpkinBombEntity p_110775_1_) {
        return p_110775_1_.getGoopy() ? GOOPY : TEXTURE;
    }
}

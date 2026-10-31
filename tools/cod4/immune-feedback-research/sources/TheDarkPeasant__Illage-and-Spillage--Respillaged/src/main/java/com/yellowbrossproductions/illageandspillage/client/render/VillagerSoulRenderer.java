package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.VillagerSoulModel;
import com.yellowbrossproductions.illageandspillage.entities.VillagerSoulEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class VillagerSoulRenderer extends MobRenderer<VillagerSoulEntity, VillagerSoulModel<VillagerSoulEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/villager_soul.png");
    private static final ResourceLocation CRYOUT = new ResourceLocation("illageandspillage", "textures/entity/freakager/villager_soul_cryout.png");

    public VillagerSoulRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new VillagerSoulModel<>(renderManagerIn.bakeLayer(VillagerSoulModel.LAYER_LOCATION)), 0.0F);
    }

    protected int getBlockLightLevel(VillagerSoulEntity p_114496_, BlockPos p_114497_) {
        return 15;
    }

    protected void scale(VillagerSoulEntity p_114046_, PoseStack p_114047_, float p_114048_) {
        float f = p_114046_.getSwelling(p_114048_);
        float f1 = 1.0F + Mth.sin(f * 100.0F) * f * 0.01F;
        f = Mth.clamp(f, 0.0F, 1.0F);
        f *= f;
        f *= f;
        float f3 = (f + 0.01F) / f1;
        p_114047_.scale(1.0F, f3, 1.0F);
    }

    public ResourceLocation getTextureLocation(VillagerSoulEntity p_110775_1_) {
        return p_110775_1_.isCharging() ? CRYOUT : TEXTURE;
    }
}

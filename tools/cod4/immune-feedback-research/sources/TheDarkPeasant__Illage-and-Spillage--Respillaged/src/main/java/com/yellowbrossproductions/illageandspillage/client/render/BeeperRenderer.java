package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.yellowbrossproductions.illageandspillage.client.model.BeeperModel;
import com.yellowbrossproductions.illageandspillage.client.render.layer.engineer.BeeperBeepLayer;
import com.yellowbrossproductions.illageandspillage.client.render.layer.engineer.BeeperGlowLayer;
import com.yellowbrossproductions.illageandspillage.entities.BeeperEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

public class BeeperRenderer extends MobRenderer<BeeperEntity, BeeperModel<BeeperEntity>> {
    private static final ResourceLocation BEEPER = new ResourceLocation("illageandspillage", "textures/entity/engineer/factory/beeper.png");
    private static final ResourceLocation BEEPING = new ResourceLocation("illageandspillage", "textures/entity/engineer/factory/beeping.png");

    public BeeperRenderer(EntityRendererProvider.Context context) {
        super(context, new BeeperModel<>(context.bakeLayer(BeeperModel.LAYER_LOCATION)), 0.3F);
        this.addLayer(new BeeperGlowLayer<>(this));
        this.addLayer(new BeeperBeepLayer(this));
    }

    @Override
    protected void scale(BeeperEntity entityLivingBaseIn, PoseStack matrixStackIn, float partialTickTime) {
        entityLivingBaseIn.setPartialTicks(partialTickTime);
        float creeperFlashIntensity = entityLivingBaseIn.getCreeperFlashIntensity(partialTickTime);
        float mathsThing = 1.0f + Mth.sin(creeperFlashIntensity * 100.0f) * creeperFlashIntensity * 0.01f;
        creeperFlashIntensity = Mth.clamp(creeperFlashIntensity, 0.0f, 1.0f);
        creeperFlashIntensity = creeperFlashIntensity * creeperFlashIntensity;
        creeperFlashIntensity = creeperFlashIntensity * creeperFlashIntensity;
        float multipliedByMathsThing = (1.0f + creeperFlashIntensity * 0.4f) * mathsThing;
        float dividedByMathsThing = (1.0f + creeperFlashIntensity * 0.1f) / mathsThing;
        matrixStackIn.scale(multipliedByMathsThing, dividedByMathsThing, multipliedByMathsThing);
    }

    @Override
    protected float getWhiteOverlayProgress(BeeperEntity livingEntityIn, float partialTicks) {
        float flashIntensity = livingEntityIn.getCreeperFlashIntensity(partialTicks);
        return (int) (flashIntensity * 10.0F) % 2 == 0 ? 0.0F : Mth.clamp(flashIntensity, 0.5F, 1.0F);
    }

    @Override
    public ResourceLocation getTextureLocation(BeeperEntity entity) {
        return entity.getCreeperFlashIntensity(entity.getPartialTicks()) > 0 ? BEEPING : BEEPER;
    }
}
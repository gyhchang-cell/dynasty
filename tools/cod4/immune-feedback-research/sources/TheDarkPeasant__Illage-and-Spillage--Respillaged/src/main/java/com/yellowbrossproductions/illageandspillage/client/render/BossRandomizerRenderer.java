package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.BossRandomizerModel;
import com.yellowbrossproductions.illageandspillage.entities.BossRandomizerEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class BossRandomizerRenderer extends MobRenderer<BossRandomizerEntity, BossRandomizerModel<BossRandomizerEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/boss_randomizer.png");

    public BossRandomizerRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new BossRandomizerModel<>(renderManagerIn.bakeLayer(BossRandomizerModel.LAYER_LOCATION)), 0.5F);
    }

    public ResourceLocation getTextureLocation(BossRandomizerEntity p_110775_1_) {
        return TEXTURE;
    }
}

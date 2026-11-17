package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.ScytheModel;
import com.yellowbrossproductions.illageandspillage.entities.projectile.ScytheEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class ScytheRenderer extends MobRenderer<ScytheEntity, ScytheModel<ScytheEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/scythe.png");

    public ScytheRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new ScytheModel<>(renderManagerIn.bakeLayer(ScytheModel.LAYER_LOCATION)), 0.3F);
    }

    protected int getBlockLightLevel(ScytheEntity p_114496_, BlockPos p_114497_) {
        return 15;
    }

    public ResourceLocation getTextureLocation(ScytheEntity p_110775_1_) {
        return TEXTURE;
    }
}

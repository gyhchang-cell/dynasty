package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.OldScytheModel;
import com.yellowbrossproductions.illageandspillage.entities.projectile.OldScytheEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class OldScytheRenderer extends MobRenderer<OldScytheEntity, OldScytheModel<OldScytheEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/old/scythe.png");

    public OldScytheRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new OldScytheModel<>(renderManagerIn.bakeLayer(OldScytheModel.LAYER_LOCATION)), 0.3F);
    }

    protected int getBlockLightLevel(OldScytheEntity p_114496_, BlockPos p_114497_) {
        return 15;
    }

    public ResourceLocation getTextureLocation(OldScytheEntity p_110775_1_) {
        return TEXTURE;
    }
}

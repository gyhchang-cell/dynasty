package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.entities.projectile.MagiArrowEntity;
import net.minecraft.client.renderer.entity.ArrowRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;

public class MagiArrowRenderer extends ArrowRenderer<MagiArrowEntity> {
    public static final ResourceLocation ARROW_LOCATION = new ResourceLocation("textures/entity/projectiles/arrow.png");

    public MagiArrowRenderer(EntityRendererProvider.Context p_173917_) {
        super(p_173917_);
    }

    public ResourceLocation getTextureLocation(MagiArrowEntity magiArrowEntity) {
        return ARROW_LOCATION;
    }
}

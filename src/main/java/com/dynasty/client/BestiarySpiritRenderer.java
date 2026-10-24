package com.dynasty.client;

import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;

/** The base fox and phoenix own their atlas, separate from approved Boss assets. */
public final class BestiarySpiritRenderer<T extends Mob> extends MobRenderer<T, BestiarySpiritModel<T>> {
    private final ResourceLocation texture;

    public BestiarySpiritRenderer(EntityRendererProvider.Context context, ModelLayerLocation layer,
                                   boolean phoenix) {
        super(context, new BestiarySpiritModel<>(context.bakeLayer(layer), phoenix), phoenix ? 0.45F : 0.4F);
        texture = new ResourceLocation("dynasty", "textures/entity/bestiary/" +
                (phoenix ? "phoenix" : "nine_tailed_fox") + ".png");
    }

    @Override
    public ResourceLocation getTextureLocation(T entity) { return texture; }
}

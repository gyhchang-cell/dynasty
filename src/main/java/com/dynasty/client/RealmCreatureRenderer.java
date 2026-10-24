package com.dynasty.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Mob;

/** Independent realm atlases; ordinary mobs have no added domain/rune particle layer. */
public final class RealmCreatureRenderer<T extends Mob> extends MobRenderer<T, RealmCreatureModel<T>> {
    private final ResourceLocation texture;
    private final float visualScale;

    public RealmCreatureRenderer(EntityRendererProvider.Context context, ModelLayerLocation layer,
                                  String kind, float scale) {
        super(context, new RealmCreatureModel<>(context.bakeLayer(layer), kind), 0.5F);
        texture = new ResourceLocation("dynasty", "textures/entity/bestiary/" + kind + ".png");
        visualScale = scale;
    }

    @Override protected void scale(T entity, PoseStack pose, float partialTick) {
        pose.scale(visualScale, visualScale, visualScale);
    }

    @Override public ResourceLocation getTextureLocation(T entity) { return texture; }
}

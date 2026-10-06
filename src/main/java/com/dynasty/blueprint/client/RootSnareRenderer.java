package com.dynasty.blueprint.client;

import com.dynasty.blueprint.RootSnare;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class RootSnareRenderer extends GeoEntityRenderer<RootSnare> {
    public RootSnareRenderer(EntityRendererProvider.Context context){
        super(context,new GeoModel<RootSnare>(){
            @Override public ResourceLocation getModelResource(RootSnare cage){return new ResourceLocation("dynasty","geo/blueprint/root_snare.geo.json");}
            @Override public ResourceLocation getAnimationResource(RootSnare cage){return new ResourceLocation("dynasty","animations/blueprint/root_snare.animation.json");}
            @Override public ResourceLocation getTextureResource(RootSnare cage){return new ResourceLocation("dynasty","textures/entity/nian_beast.png");}
        });shadowRadius=0;
    }
}

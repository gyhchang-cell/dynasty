package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.*;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public final class WhiteDeerRenderer extends GeoEntityRenderer<WhiteDeerEntity> {
    public WhiteDeerRenderer(EntityRendererProvider.Context c){super(c,new Model());shadowRadius=.4f;}
    public static final class Model extends GeoModel<WhiteDeerEntity> {
        public ResourceLocation getModelResource(WhiteDeerEntity e){return new ResourceLocation(Dynasty.MODID,"geo/cod3/white_deer.geo.json");}
        public ResourceLocation getTextureResource(WhiteDeerEntity e){return new ResourceLocation(Dynasty.MODID,"textures/entity/cod3/white_deer.png");}
        public ResourceLocation getAnimationResource(WhiteDeerEntity e){return new ResourceLocation(Dynasty.MODID,"animations/cod3/white_deer.animation.json");}
    }
}

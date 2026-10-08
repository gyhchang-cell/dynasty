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

public final class Cod3NpcRenderer extends GeoEntityRenderer<DynastyNpcEntity> {
    public Cod3NpcRenderer(EntityRendererProvider.Context context){super(context,new Model());shadowRadius=.4f;}
    private static final class Model extends GeoModel<DynastyNpcEntity> {
        public ResourceLocation getModelResource(DynastyNpcEntity e){return new ResourceLocation(Dynasty.MODID,"geo/npc/"+e.role+".geo.json");}
        public ResourceLocation getTextureResource(DynastyNpcEntity e){return new ResourceLocation(Dynasty.MODID,"textures/entity/npc/"+e.role+".png");}
        public ResourceLocation getAnimationResource(DynastyNpcEntity e){return new ResourceLocation(Dynasty.MODID,"animations/npc/"+e.role+".animation.json");}
    }
    @Mod.EventBusSubscriber(modid=Dynasty.MODID,bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
    public static final class Registration {
        @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){for(var type:NpcContent.NPCS.values())e.registerEntityRenderer(type.get(),Cod3NpcRenderer::new);}
    }
}

package com.dynasty.blueprint.elite.client;

import com.dynasty.blueprint.elite.*;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class SpiderWomanRenderer extends GeoEntityRenderer<SpiderWoman> {
    public SpiderWomanRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(SpiderWoman e){return resource("geo/blueprint/elite/",SpiderWoman.ID,".geo.json");}
        @Override public ResourceLocation getTextureResource(SpiderWoman e){return resource("textures/entity/blueprint/elite/",SpiderWoman.ID,".png");}
        @Override public ResourceLocation getAnimationResource(SpiderWoman e){return resource("animations/blueprint/elite/",SpiderWoman.ID,".animation.json");}
        @Override public void setCustomAnimations(SpiderWoman e,long instanceId,software.bernie.geckolib.core.animation.AnimationState<SpiderWoman> state){super.setCustomAnimations(e,instanceId,state);getBone("root").ifPresent(b->b.setRotZ(e.attachedToCeiling()?(float)Math.PI:0));}
    });shadowRadius=1.35F;}
    @Override protected float getDeathMaxRotation(SpiderWoman e){return 0;}
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    public static final class BroodRenderer extends GeoEntityRenderer<SpiderBrood>{
        public BroodRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
            @Override public ResourceLocation getModelResource(SpiderBrood e){return resource("geo/blueprint/elite/",SpiderBrood.ID,".geo.json");}
            @Override public ResourceLocation getTextureResource(SpiderBrood e){return resource("textures/entity/blueprint/elite/",SpiderWoman.ID,".png");}
            @Override public ResourceLocation getAnimationResource(SpiderBrood e){return resource("animations/blueprint/elite/",SpiderBrood.ID,".animation.json");}
            @Override public void setCustomAnimations(SpiderBrood e,long instanceId,software.bernie.geckolib.core.animation.AnimationState<SpiderBrood> state){super.setCustomAnimations(e,instanceId,state);for(String name:new String[]{"egg","spider"})getBone(name).ifPresent(b->{boolean hidden=name.equals("egg")==e.hatched();b.setHidden(hidden);b.setChildrenHidden(hidden);});}
        });shadowRadius=.3F;}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){event.registerEntityRenderer(EliteContent.SPIDER_WOMAN.get(),SpiderWomanRenderer::new);event.registerEntityRenderer(EliteContent.SPIDER_BROOD.get(),BroodRenderer::new);}
}

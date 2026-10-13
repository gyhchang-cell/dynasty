package com.dynasty.blueprint.elite.client;

import com.dynasty.blueprint.elite.*;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class RageCorpseRenderer extends GeoEntityRenderer<RageCorpse> {
    private static ResourceLocation resource(String folder,String suffix){return new ResourceLocation("dynasty",folder+RageCorpse.ID+suffix);}
    public RageCorpseRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(RageCorpse e){return resource("geo/blueprint/elite/",".geo.json");}
        @Override public ResourceLocation getTextureResource(RageCorpse e){return resource("textures/entity/blueprint/elite/",".png");}
        @Override public ResourceLocation getAnimationResource(RageCorpse e){return resource("animations/blueprint/elite/",".animation.json");}
        @Override public void setCustomAnimations(RageCorpse e,long id,software.bernie.geckolib.core.animation.AnimationState<RageCorpse> state){super.setCustomAnimations(e,id,state);getBone("death_mud").ifPresent(b->b.setHidden(!e.isDeadOrDying()));}
    });shadowRadius=1.7F;}
    @Override protected float getDeathMaxRotation(RageCorpse e){return 0;}
    @Override public boolean shouldRender(RageCorpse e,Frustum camera,double x,double y,double z){return super.shouldRender(e,camera,x,y,z)||e.shouldRender(x,y,z)&&camera.isVisible(e.getBoundingBoxForCulling().inflate(1.4D,1.4D,1.4D));}
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){event.registerEntityRenderer(EliteContent.RAGE_CORPSE.get(),RageCorpseRenderer::new);}
}

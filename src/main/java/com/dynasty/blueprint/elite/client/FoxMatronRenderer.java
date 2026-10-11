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
public final class FoxMatronRenderer extends GeoEntityRenderer<FoxMatron> {
    public FoxMatronRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(FoxMatron e){return resource("geo/blueprint/elite/",".geo.json");}
        @Override public ResourceLocation getTextureResource(FoxMatron e){return resource("textures/entity/blueprint/elite/",".png");}
        @Override public ResourceLocation getAnimationResource(FoxMatron e){return resource("animations/blueprint/elite/",".animation.json");}
        @Override public void setCustomAnimations(FoxMatron e,long instance,software.bernie.geckolib.core.animation.AnimationState<FoxMatron> state){
            super.setCustomAnimations(e,instance,state);
            getBone("mask_crack").ifPresent(b->b.setHidden(e.isDecoy()));
            boolean showFox=e.isDeadOrDying()&&e.level().getGameTime()-e.skillStart()>=24;
            getBone("death_fox").ifPresent(b->{b.setHidden(!showFox);b.setChildrenHidden(!showFox);});
        }
    });shadowRadius=.4F;}
    private static ResourceLocation resource(String folder,String extension){return new ResourceLocation("dynasty",folder+FoxMatron.ID+extension);}
    @Override protected float getDeathMaxRotation(FoxMatron e){return 0;}
    @Override public int getPackedOverlay(FoxMatron e,float u,float partial){return net.minecraft.client.renderer.texture.OverlayTexture.pack(u,e.hurtTime>0);}
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(EliteContent.FOX.get(),FoxMatronRenderer::new);}
}

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
public final class JinwuRenderer extends GeoEntityRenderer<Jinwu> {
    public JinwuRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(Jinwu e){return resource("geo/blueprint/elite/",".geo.json");}
        @Override public ResourceLocation getTextureResource(Jinwu e){return resource("textures/entity/blueprint/elite/",".png");}
        @Override public ResourceLocation getAnimationResource(Jinwu e){return resource("animations/blueprint/elite/",".animation.json");}
    });shadowRadius=.65F;}
    private static ResourceLocation resource(String folder,String extension){return new ResourceLocation("dynasty",folder+Jinwu.ID+extension);}
    @Override protected float getDeathMaxRotation(Jinwu e){return 0;}
    @Override public int getPackedOverlay(Jinwu e,float u,float partial){return net.minecraft.client.renderer.texture.OverlayTexture.pack(u,e.hurtTime>0);}
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(EliteContent.JINWU.get(),JinwuRenderer::new);}
}

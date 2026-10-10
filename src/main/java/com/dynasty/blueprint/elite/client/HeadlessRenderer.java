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
public final class HeadlessRenderer extends GeoEntityRenderer<HeadlessGeneral> {
    public HeadlessRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(HeadlessGeneral e){return new ResourceLocation("dynasty","geo/blueprint/elite/"+HeadlessGeneral.ID+".geo.json");}
        @Override public ResourceLocation getTextureResource(HeadlessGeneral e){return new ResourceLocation("dynasty","textures/entity/royal_guard.png");}
        @Override public ResourceLocation getAnimationResource(HeadlessGeneral e){return new ResourceLocation("dynasty","animations/blueprint/elite/"+HeadlessGeneral.ID+".animation.json");}
    });shadowRadius=.7F;}
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){event.registerEntityRenderer(EliteContent.HEADLESS.get(),HeadlessRenderer::new);}
    @Override protected float getDeathMaxRotation(HeadlessGeneral e){return 0;}
}

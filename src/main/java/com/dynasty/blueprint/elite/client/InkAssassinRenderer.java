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
public final class InkAssassinRenderer extends GeoEntityRenderer<InkAssassin> {
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    public InkAssassinRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(InkAssassin e){return resource("geo/blueprint/elite/",InkAssassin.ID,".geo.json");}
        @Override public ResourceLocation getTextureResource(InkAssassin e){return resource("textures/entity/blueprint/elite/",InkAssassin.ID,".png");}
        @Override public ResourceLocation getAnimationResource(InkAssassin e){return resource("animations/blueprint/elite/",InkAssassin.ID,".animation.json");}
        @Override public void setCustomAnimations(InkAssassin e,long id,software.bernie.geckolib.core.animation.AnimationState<InkAssassin> state){super.setCustomAnimations(e,id,state);getBone("root").ifPresent(b->{b.setHidden(e.concealed());b.setChildrenHidden(e.concealed());});getBone("death_wash").ifPresent(b->b.setHidden(!e.isDeadOrDying()));}
    });shadowRadius=.5F;}
    @Override protected float getDeathMaxRotation(InkAssassin e){return 0;}
    @Override public boolean shouldRender(InkAssassin e,Frustum camera,double x,double y,double z){return super.shouldRender(e,camera,x,y,z)||e.shouldRender(x,y,z)&&camera.isVisible(e.getBoundingBoxForCulling().inflate(1.7D,.6D,1.7D));}
    public static final class SpikeRenderer extends GeoEntityRenderer<InkSpike> {
        public SpikeRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
            @Override public ResourceLocation getModelResource(InkSpike e){return resource("geo/blueprint/elite/",InkSpike.ID,".geo.json");}
            @Override public ResourceLocation getTextureResource(InkSpike e){return resource("textures/entity/blueprint/elite/",InkAssassin.ID,".png");}
            @Override public ResourceLocation getAnimationResource(InkSpike e){return resource("animations/blueprint/elite/",InkSpike.ID,".animation.json");}
        });shadowRadius=.12F;}
    }
    public static final class PelletRenderer extends GeoEntityRenderer<InkCloud> {
        public PelletRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
            @Override public ResourceLocation getModelResource(InkCloud e){return resource("geo/blueprint/elite/",InkCloud.ID,".geo.json");}
            @Override public ResourceLocation getTextureResource(InkCloud e){return resource("textures/entity/blueprint/elite/",InkAssassin.ID,".png");}
            @Override public ResourceLocation getAnimationResource(InkCloud e){return resource("animations/blueprint/elite/",InkCloud.ID,".animation.json");}
            @Override public void setCustomAnimations(InkCloud e,long id,software.bernie.geckolib.core.animation.AnimationState<InkCloud> state){super.setCustomAnimations(e,id,state);getBone("root").ifPresent(b->b.setHidden(!e.isWaiting()));}
        });shadowRadius=.15F;}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){event.registerEntityRenderer(EliteContent.INK_ASSASSIN.get(),InkAssassinRenderer::new);event.registerEntityRenderer(EliteContent.INK_SPIKE.get(),SpikeRenderer::new);event.registerEntityRenderer(EliteContent.INK_CLOUD.get(),PelletRenderer::new);}
}

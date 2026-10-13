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
public final class TideYashaRenderer extends GeoEntityRenderer<TideYasha> {
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    public TideYashaRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(TideYasha e){return resource("geo/blueprint/elite/",TideYasha.ID,".geo.json");}
        @Override public ResourceLocation getTextureResource(TideYasha e){return resource("textures/entity/blueprint/elite/",TideYasha.ID,".png");}
        @Override public ResourceLocation getAnimationResource(TideYasha e){return resource("animations/blueprint/elite/",TideYasha.ID,".animation.json");}
        @Override public void setCustomAnimations(TideYasha e,long id,software.bernie.geckolib.core.animation.AnimationState<TideYasha> state){
            super.setCustomAnimations(e,id,state);long age=e.level().getGameTime()-e.skillStart();boolean submerged=e.skillId()==392&&age>=9&&age<30&&!e.isDeadOrDying();
            getBone("root").ifPresent(b->{b.setHidden(submerged);b.setChildrenHidden(submerged);});
            getBone("reef_shell").ifPresent(b->{b.setHidden(!e.isDeadOrDying());b.setChildrenHidden(!e.isDeadOrDying());});
            getBone("planted_trident").ifPresent(b->b.setHidden(!e.isDeadOrDying()));
            getBone("trident").ifPresent(b->b.setHidden(e.isDeadOrDying()));
        }
    });shadowRadius=1.1F;}
    @Override protected float getDeathMaxRotation(TideYasha e){return 0;}
    @Override public boolean shouldRender(TideYasha e,Frustum camera,double x,double y,double z){return super.shouldRender(e,camera,x,y,z)||e.shouldRender(x,y,z)&&camera.isVisible(e.getBoundingBoxForCulling().inflate(1.7D,.8D,1.7D));}
    public static final class VortexRenderer extends GeoEntityRenderer<TideVortex> {
        public VortexRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
            @Override public ResourceLocation getModelResource(TideVortex e){return resource("geo/blueprint/elite/",TideVortex.ID,".geo.json");}
            @Override public ResourceLocation getTextureResource(TideVortex e){return resource("textures/entity/blueprint/elite/",TideYasha.ID,".png");}
            @Override public ResourceLocation getAnimationResource(TideVortex e){return resource("animations/blueprint/elite/",TideVortex.ID,".animation.json");}
        });shadowRadius=.3F;}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){event.registerEntityRenderer(EliteContent.TIDE_YASHA.get(),TideYashaRenderer::new);event.registerEntityRenderer(EliteContent.TIDE_VORTEX.get(),VortexRenderer::new);}
}

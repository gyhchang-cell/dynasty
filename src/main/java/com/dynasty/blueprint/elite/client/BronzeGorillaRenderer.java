package com.dynasty.blueprint.elite.client;
import com.dynasty.blueprint.elite.*;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class BronzeGorillaRenderer extends GeoEntityRenderer<BronzeGorilla>{
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    public BronzeGorillaRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
        public ResourceLocation getModelResource(BronzeGorilla e){return resource("geo/blueprint/elite/",BronzeGorilla.ID,".geo.json");}
        public ResourceLocation getTextureResource(BronzeGorilla e){return resource("textures/entity/blueprint/elite/",BronzeGorilla.ID,".png");}
        public ResourceLocation getAnimationResource(BronzeGorilla e){return resource("animations/blueprint/elite/",BronzeGorilla.ID,".animation.json");}
        @Override public void setCustomAnimations(BronzeGorilla e,long id,software.bernie.geckolib.core.animation.AnimationState<BronzeGorilla> state){super.setCustomAnimations(e,id,state);getBone("held_rock").ifPresent(b->b.setHidden(e.skillId()!=422||e.isDeadOrDying()));}
    });shadowRadius=1.5F;}
    @Override protected float getDeathMaxRotation(BronzeGorilla e){return 0;}
    @Override public boolean shouldRender(BronzeGorilla e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(new AABB(e.getX()-4,e.getY()-1,e.getZ()-4,e.getX()+4,e.getY()+5,e.getZ()+4));}
    public static final class StoneRenderer extends GeoEntityRenderer<GorillaStone>{
        public StoneRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(GorillaStone e){return resource("geo/blueprint/elite/",e.modelId(),".geo.json");}
            public ResourceLocation getTextureResource(GorillaStone e){return resource("textures/entity/blueprint/elite/",BronzeGorilla.ID,".png");}
            public ResourceLocation getAnimationResource(GorillaStone e){return resource("animations/blueprint/elite/",e.modelId(),".animation.json");}
        });shadowRadius=.3F;}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(EliteContent.BRONZE_GORILLA.get(),BronzeGorillaRenderer::new);e.registerEntityRenderer(EliteContent.GORILLA_BOULDER.get(),StoneRenderer::new);e.registerEntityRenderer(EliteContent.GORILLA_FRAGMENT.get(),StoneRenderer::new);}
}

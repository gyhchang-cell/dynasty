package com.dynasty.blueprint.elite.client;

import com.dynasty.blueprint.elite.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class BronzeSuanniRenderer extends GeoEntityRenderer<BronzeSuanni>{
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    public BronzeSuanniRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
        public ResourceLocation getModelResource(BronzeSuanni e){return resource("geo/blueprint/elite/",BronzeSuanni.ID,".geo.json");}
        public ResourceLocation getTextureResource(BronzeSuanni e){return resource("textures/entity/blueprint/elite/",BronzeSuanni.ID+(e.isDeadOrDying()&&e.skillStart()>=0&&e.level().getGameTime()-e.skillStart()>=16?"_dead":""),".png");}
        public ResourceLocation getAnimationResource(BronzeSuanni e){return resource("animations/blueprint/elite/",BronzeSuanni.ID,".animation.json");}
    });shadowRadius=1.4F;}
    @Override protected float getDeathMaxRotation(BronzeSuanni e){return 0;}
    @Override public boolean shouldRender(BronzeSuanni e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(new AABB(e.getX()-3,e.getY()-.5,e.getZ()-3,e.getX()+3,e.getY()+4.5,e.getZ()+3));}
    public static final class EffectRenderer extends GeoEntityRenderer<SuanniEffect>{
        public EffectRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(SuanniEffect e){return resource("geo/blueprint/elite/",e.modelId(),".geo.json");}
            public ResourceLocation getTextureResource(SuanniEffect e){return resource("textures/entity/blueprint/elite/",BronzeSuanni.ID,".png");}
            public ResourceLocation getAnimationResource(SuanniEffect e){return resource("animations/blueprint/elite/",e.modelId(),".animation.json");}
            @Override public void setCustomAnimations(SuanniEffect e,long id,software.bernie.geckolib.core.animation.AnimationState<SuanniEffect> s){super.setCustomAnimations(e,id,s);if(e.flame())getBone("root").ifPresent(b->b.setScaleZ(e.length()/8));}
        });shadowRadius=0;}
        @Override protected void applyRotations(SuanniEffect e,PoseStack pose,float age,float yaw,float partial){super.applyRotations(e,pose,age,e.getYRot(),partial);}
        @Override public boolean shouldRender(SuanniEffect e,Frustum f,double x,double y,double z){AABB box;if(e.flame()){double a=Math.toRadians(e.getYRot());var end=e.position().add(-Math.sin(a)*e.length(),0,Math.cos(a)*e.length());box=new AABB(e.position(),end).inflate(2,1,2);}else box=e.getBoundingBox().inflate(.5);return e.shouldRender(x,y,z)&&f.isVisible(box);}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(EliteContent.BRONZE_SUANNI.get(),BronzeSuanniRenderer::new);e.registerEntityRenderer(EliteContent.SUANNI_FLAME.get(),EffectRenderer::new);e.registerEntityRenderer(EliteContent.SUANNI_CRACK.get(),EffectRenderer::new);}
}

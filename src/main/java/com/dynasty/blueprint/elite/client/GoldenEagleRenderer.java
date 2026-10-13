package com.dynasty.blueprint.elite.client;

import com.dynasty.blueprint.elite.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class GoldenEagleRenderer extends GeoEntityRenderer<GoldenEagle>{
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    public GoldenEagleRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
        public ResourceLocation getModelResource(GoldenEagle e){return resource("geo/blueprint/elite/",GoldenEagle.ID,".geo.json");}
        public ResourceLocation getTextureResource(GoldenEagle e){return resource("textures/entity/blueprint/elite/",GoldenEagle.ID+(e.isDeadOrDying()?"_dead":""),".png");}
        public ResourceLocation getAnimationResource(GoldenEagle e){return resource("animations/blueprint/elite/",GoldenEagle.ID,".animation.json");}
        @Override public void setCustomAnimations(GoldenEagle e,long id,software.bernie.geckolib.core.animation.AnimationState<GoldenEagle> s){super.setCustomAnimations(e,id,s);getBone("drawn_arrow").ifPresent(b->b.setHidden(e.isDeadOrDying()||e.skillId()!=441||e.level().getGameTime()-e.skillStart()>=30));}
    });shadowRadius=.6F;}
    @Override protected float getDeathMaxRotation(GoldenEagle e){return 0;}
    @Override public boolean shouldRender(GoldenEagle e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(new AABB(e.getX()-4,e.getY()-1.8,e.getZ()-4,e.getX()+4,e.getY()+5.2,e.getZ()+4));}
    public static final class ArrowRenderer extends GeoEntityRenderer<EagleArrow>{
        public ArrowRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(EagleArrow e){return resource("geo/blueprint/elite/",EagleArrow.ID,".geo.json");}
            public ResourceLocation getTextureResource(EagleArrow e){return resource("textures/entity/blueprint/elite/",GoldenEagle.ID,".png");}
            public ResourceLocation getAnimationResource(EagleArrow e){return resource("animations/blueprint/elite/",EagleArrow.ID,".animation.json");}
        });shadowRadius=0;}
        // Nonliving Gecko entities do not receive body yaw. Match the native velocity in3D,
        // with the exported tip at the ray contact and the shaft trailing behind it.
        @Override protected void applyRotations(EagleArrow e,PoseStack pose,float age,float yaw,float partial){var v=e.getDeltaMovement();if(v.lengthSqr()>1e-8)pose.mulPose(new Quaternionf().rotationTo(new Vector3f(0,1,0),new Vector3f((float)v.x,(float)v.y,(float)v.z).normalize()));}
        @Override public boolean shouldRender(EagleArrow e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(e.getBoundingBox().inflate(1));}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(EliteContent.GOLDEN_EAGLE.get(),GoldenEagleRenderer::new);e.registerEntityRenderer(EliteContent.EAGLE_ARROW.get(),ArrowRenderer::new);}
}

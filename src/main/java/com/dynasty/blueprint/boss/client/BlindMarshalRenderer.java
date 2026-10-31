package com.dynasty.blueprint.boss.client;
import com.dynasty.blueprint.boss.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.*;
import net.minecraft.world.level.material.FogType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import org.joml.Quaternionf;
import org.joml.Vector3f;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class BlindMarshalRenderer extends GeoEntityRenderer<BlindMarshal>{
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    private static String form(BlindMarshal e){return BlindMarshal.ID+(e.form()==2?"_foot":"");}
    public BlindMarshalRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
        public ResourceLocation getModelResource(BlindMarshal e){return resource("geo/blueprint/boss/",form(e),".geo.json");}
        public ResourceLocation getTextureResource(BlindMarshal e){return resource("textures/entity/blueprint/boss/",form(e)+"_body",".png");}
        public ResourceLocation getAnimationResource(BlindMarshal e){return resource("animations/blueprint/boss/",form(e),".animation.json");}
    });shadowRadius=1.5F;}
    @Override protected float getDeathMaxRotation(BlindMarshal e){return 0;}
    @Override public boolean shouldRender(BlindMarshal e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(new AABB(e.getX()-8,e.getY()-1,e.getZ()-8,e.getX()+8,e.getY()+13,e.getZ()+8));}
    public static final class ProjectileRenderer extends GeoEntityRenderer<MarshalProjectile>{
        public ProjectileRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(MarshalProjectile e){return resource("geo/blueprint/boss/",e.modelId(),".geo.json");}
            public ResourceLocation getTextureResource(MarshalProjectile e){return resource("textures/entity/blueprint/boss/",BlindMarshal.ID,".png");}
            public ResourceLocation getAnimationResource(MarshalProjectile e){return resource("animations/blueprint/boss/",e.modelId(),".animation.json");}
        });shadowRadius=0;}
        @Override protected void applyRotations(MarshalProjectile e,PoseStack pose,float age,float yaw,float partial){if(e.kind()==MarshalProjectile.WALL_ARROW){var d=e.getDeltaMovement();if(d.lengthSqr()>.0001){pose.mulPose(new Quaternionf().rotationTo(new Vector3f(0,1,0),new Vector3f((float)d.x,(float)d.y,(float)d.z).normalize()));return;}}super.applyRotations(e,pose,age,e.getYRot(),partial);}
        @Override public boolean shouldRender(MarshalProjectile e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(e.getBoundingBox().inflate(1.5));}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(BlindMarshalContent.MARSHAL.get(),BlindMarshalRenderer::new);e.registerEntityRenderer(BlindMarshalContent.PROJECTILE.get(),ProjectileRenderer::new);}
    /** Scoped fog is inferred only from this tracked actor's synchronized active storm clock. */
    @Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
    public static final class StormFog {
        private static boolean active(net.minecraft.client.Camera camera){var mc=Minecraft.getInstance();if(mc.level==null||!(camera.getEntity() instanceof Player p)||p.isSpectator()||p.isCreative()||!p.isAlive()||camera.getFluidInCamera()!=FogType.NONE)return false;return mc.level.getEntitiesOfClass(BlindMarshal.class,new AABB(camera.getPosition(),camera.getPosition()).inflate(24,16,24),m->m.stormActive()&&m.arenaCentre()!=null&&p.blockPosition().distSqr(m.arenaCentre())<=15*15).stream().limit(2).findAny().isPresent();}
        @SubscribeEvent public static void fog(ViewportEvent.RenderFog e){if(active(e.getCamera())){e.setNearPlaneDistance(Math.min(e.getNearPlaneDistance(),.5F));e.setFarPlaneDistance(Math.min(e.getFarPlaneDistance(),3));e.setCanceled(true);}}
        @SubscribeEvent public static void colour(ViewportEvent.ComputeFogColor e){if(active(e.getCamera())){e.setRed(.45F);e.setGreen(.27F);e.setBlue(.29F);}}
    }
}

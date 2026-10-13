package com.dynasty.blueprint.artifact.client;
import com.dynasty.blueprint.artifact.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class ArtifactRenderers {
    private static ResourceLocation resource(String dir,String id,String suffix){return new ResourceLocation("dynasty",dir+id+suffix);}
    public static final class Memorial extends GeoEntityRenderer<MarshalBladeMemorial>{
        public Memorial(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(MarshalBladeMemorial e){return resource("geo/blueprint/artifact/",ArtifactContent.ID,".geo.json");}
            public ResourceLocation getTextureResource(MarshalBladeMemorial e){return resource("textures/entity/blueprint/artifact/",ArtifactContent.ID,".png");}
            public ResourceLocation getAnimationResource(MarshalBladeMemorial e){return resource("animations/blueprint/artifact/",ArtifactContent.ID,".animation.json");}
        });shadowRadius=.2F;}
        @Override protected void applyRotations(MarshalBladeMemorial e,PoseStack p,float age,float yaw,float partial){super.applyRotations(e,p,age,e.getYRot(),partial);}
        @Override public boolean shouldRender(MarshalBladeMemorial e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(e.getBoundingBox().inflate(.5));}
    }
    public static final class Wave extends GeoEntityRenderer<ArtifactWave>{
        public Wave(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(ArtifactWave e){return resource("geo/blueprint/artifact/","longyin_ground_crest",".geo.json");}
            public ResourceLocation getTextureResource(ArtifactWave e){return resource("textures/entity/blueprint/artifact/","longyin_ground_crest",".png");}
            public ResourceLocation getAnimationResource(ArtifactWave e){return resource("animations/blueprint/artifact/","longyin_ground_crest",".animation.json");}
        });shadowRadius=0;}
        @Override protected void applyRotations(ArtifactWave e,PoseStack p,float age,float yaw,float partial){super.applyRotations(e,p,age,e.getYRot(),partial);}
        @Override public boolean shouldRender(ArtifactWave e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(e.getBoundingBox().inflate(1));}
    }
    public static final class Ceasefire extends GeoEntityRenderer<ZhanluField>{
        public Ceasefire(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(ZhanluField e){return resource("geo/blueprint/artifact/","zhanlu_ceasefire_field",".geo.json");}
            public ResourceLocation getTextureResource(ZhanluField e){return resource("textures/entity/blueprint/artifact/","zhanlu_ceasefire_field",".png");}
            public ResourceLocation getAnimationResource(ZhanluField e){return resource("animations/blueprint/artifact/","zhanlu_ceasefire_field",".animation.json");}
        });shadowRadius=0;}
        @Override public net.minecraft.client.renderer.RenderType getRenderType(ZhanluField e,ResourceLocation texture,net.minecraft.client.renderer.MultiBufferSource buffers,float partial){return net.minecraft.client.renderer.RenderType.entityTranslucent(texture);}
        @Override public software.bernie.geckolib.core.object.Color getRenderColor(ZhanluField e,float partial,int light){long age=e.level().getGameTime()-e.born();float alpha=age<0||age>=80?0:Math.min(1,Math.min((age+partial)/8F,(80-age-partial)/8F))*.55F;return software.bernie.geckolib.core.object.Color.ofRGBA(1F,1F,1F,Math.max(0,alpha));}
        @Override public boolean shouldRender(ZhanluField e,Frustum f,double x,double y,double z){return e.shouldRender(x,y,z)&&f.isVisible(e.getBoundingBox().inflate(.25));}
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(ArtifactContent.MEMORIAL.get(),Memorial::new);e.registerEntityRenderer(ArtifactContent.WAVE.get(),Wave::new);e.registerEntityRenderer(ArtifactContent.ZHANLU_FIELD.get(),Ceasefire::new);}
    @Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
    public static final class Inputs {
        @SubscribeEvent public static void empty(PlayerInteractEvent.LeftClickEmpty e){if(e.getEntity().getMainHandItem().getItem() instanceof ArtifactItem)com.dynasty.network.DynastyNetwork.CHANNEL.sendToServer(new ArtifactSwingRequest());}
    }
}

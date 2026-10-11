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
public final class GhostBirdRenderer extends GeoEntityRenderer<GhostCarriageBird> {
    public GhostBirdRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(GhostCarriageBird e){return new ResourceLocation("dynasty","geo/blueprint/elite/"+GhostCarriageBird.ID+".geo.json");}
        @Override public ResourceLocation getTextureResource(GhostCarriageBird e){return new ResourceLocation("dynasty","textures/entity/nian_beast.png");}
        @Override public ResourceLocation getAnimationResource(GhostCarriageBird e){return new ResourceLocation("dynasty","animations/blueprint/elite/"+GhostCarriageBird.ID+".animation.json");}
    });shadowRadius=1.4F;}
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){event.registerEntityRenderer(EliteContent.BIRD.get(),GhostBirdRenderer::new);}
    @Override protected float getDeathMaxRotation(GhostCarriageBird e){return 0;}
    @Override public int getPackedOverlay(GhostCarriageBird e,float u,float partial){return net.minecraft.client.renderer.texture.OverlayTexture.pack(u,e.hurtTime>0);}
    @Override public void renderRecursively(com.mojang.blaze3d.vertex.PoseStack pose,GhostCarriageBird entity,
            software.bernie.geckolib.cache.object.GeoBone bone,net.minecraft.client.renderer.RenderType type,
            net.minecraft.client.renderer.MultiBufferSource buffers,com.mojang.blaze3d.vertex.VertexConsumer vertices,
            boolean rerender,float partial,int light,int overlay,float red,float green,float blue,float alpha){
        String name=bone.getName();boolean face=name.startsWith("neck_")||name.startsWith("face_")||name.startsWith("beak_")||name.startsWith("jaw_");
        boolean feather=name.equals("body")||name.equals("tail")||name.contains("wing")||name.contains("feather");
        super.renderRecursively(pose,entity,bone,type,buffers,vertices,rerender,partial,light,overlay,
            face||feather?1:red,face?1:feather?.58F:green,face?1:feather?.55F:blue,alpha);
    }
}

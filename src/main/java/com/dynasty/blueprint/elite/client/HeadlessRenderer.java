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
    @Override public int getPackedOverlay(HeadlessGeneral entity,float u,float partial){
        return net.minecraft.client.renderer.texture.OverlayTexture.pack(u,entity.hurtTime>0);
    }
    @Override public void renderRecursively(com.mojang.blaze3d.vertex.PoseStack pose,HeadlessGeneral entity,
            software.bernie.geckolib.cache.object.GeoBone bone,net.minecraft.client.renderer.RenderType type,
            net.minecraft.client.renderer.MultiBufferSource buffers,com.mojang.blaze3d.vertex.VertexConsumer vertices,
            boolean rerender,float partial,int light,int overlay,float red,float green,float blue,float alpha){
        boolean seal=bone.getName().equals("seal_flame")||bone.getName().equals("neck_seal");
        super.renderRecursively(pose,entity,bone,type,buffers,vertices,rerender,partial,seal?15728880:light,overlay,
            seal?red*.35F:red,seal?green*.9F:green,blue,alpha);
    }
}

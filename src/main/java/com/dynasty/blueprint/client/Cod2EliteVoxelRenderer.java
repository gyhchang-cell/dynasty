package com.dynasty.blueprint.client;

import com.dynasty.blueprint.elite.*;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/** Separate art selection preserves every concurrent elite implementation and legacy resource. */
@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class Cod2EliteVoxelRenderer<T extends LivingEntity & GeoEntity> extends GeoEntityRenderer<T> {
    private final String id;
    public Cod2EliteVoxelRenderer(EntityRendererProvider.Context context,String id,float shadow){
        super(context,new GeoModel<>(){
            @Override public ResourceLocation getModelResource(T e){return resource("geo",id,".geo.json");}
            @Override public ResourceLocation getTextureResource(T e){return resource("textures/entity",id,".png");}
            @Override public ResourceLocation getAnimationResource(T e){return resource("animations",id,".animation.json");}
        });this.id=id;shadowRadius=shadow;
    }
    private static ResourceLocation resource(String folder,String id,String suffix){
        return new ResourceLocation("dynasty",folder+"/blueprint/cod2_voxel/"+id+suffix);
    }
    @Override protected float getDeathMaxRotation(T entity){return 0;}
    @Override public int getPackedOverlay(T entity,float u,float partial){return OverlayTexture.pack(u,entity.hurtTime>0);}
    @Override public void renderRecursively(PoseStack pose,T entity,GeoBone bone,RenderType type,
            MultiBufferSource buffers,VertexConsumer sink,boolean rerender,float partial,int light,int overlay,
            float red,float green,float blue,float alpha){
        if(id.equals(Mechanist.ID)&&bone.getName().contains("_thread_")){
            var threadType=RenderType.entityTranslucent(getGeoModel().getTextureResource(entity));
            super.renderRecursively(pose,entity,bone,threadType,buffers,buffers.getBuffer(threadType),rerender,
                partial,15728880,OverlayTexture.NO_OVERLAY,red,green,blue,.7F);return;
        }
        boolean seal=id.equals(HeadlessGeneral.ID)&&(bone.getName().equals("seal_flame")||bone.getName().equals("neck_seal"));
        super.renderRecursively(pose,entity,bone,type,buffers,sink,rerender,partial,seal?15728880:light,
            overlay,seal?red*.35F:red,seal?green*.9F:green,blue,alpha);
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void register(EntityRenderersEvent.RegisterRenderers event){
        event.registerEntityRenderer(EliteContent.HEADLESS.get(),c->new Cod2EliteVoxelRenderer<>(c,HeadlessGeneral.ID,.7F));
        event.registerEntityRenderer(EliteContent.MECHANIST.get(),c->new Cod2EliteVoxelRenderer<>(c,Mechanist.ID,.45F));
        event.registerEntityRenderer(EliteContent.SPIDER.get(),c->new Cod2EliteVoxelRenderer<>(c,ClockworkSpider.ID,.2F));
    }
}

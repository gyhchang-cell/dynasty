package com.dynasty.blueprint.elite.client;

import com.dynasty.blueprint.elite.*;
import com.dynasty.blueprint.BlueprintSalvage;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class MechanistRenderer extends GeoEntityRenderer<Mechanist> {
    public MechanistRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
        @Override public ResourceLocation getModelResource(Mechanist e){return resource("geo",Mechanist.ID,".geo.json");}
        @Override public ResourceLocation getTextureResource(Mechanist e){return atlas();}
        @Override public ResourceLocation getAnimationResource(Mechanist e){return resource("animations",Mechanist.ID,".animation.json");}
    });shadowRadius=.45F;}
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+"/blueprint/elite/"+id+suffix);}
    private static ResourceLocation atlas(){return new ResourceLocation("dynasty","textures/entity/blueprint/qianji_bailian_yanshi.png");}
    @Override protected float getDeathMaxRotation(Mechanist entity){return 0;}
    @Override public int getPackedOverlay(Mechanist entity,float u,float partial){return net.minecraft.client.renderer.texture.OverlayTexture.pack(u,entity.hurtTime>0);}
    @Override public void renderRecursively(PoseStack pose,Mechanist entity,software.bernie.geckolib.cache.object.GeoBone bone,RenderType type,MultiBufferSource buffers,com.mojang.blaze3d.vertex.VertexConsumer vertices,boolean rerender,float partial,int light,int overlay,float red,float green,float blue,float alpha){
        if(bone.getName().contains("_thread_")){
            var threadType=RenderType.entityTranslucent(atlas());
            super.renderRecursively(pose,entity,bone,threadType,buffers,buffers.getBuffer(threadType),rerender,partial,15728880,net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY,red,green,blue,.7F);return;
        }
        super.renderRecursively(pose,entity,bone,type,buffers,vertices,rerender,partial,light,overlay,red,green,blue,alpha);
    }
    public static final class SpiderRenderer extends GeoEntityRenderer<ClockworkSpider>{
        public SpiderRenderer(EntityRendererProvider.Context context){super(context,new GeoModel<>(){
            @Override public ResourceLocation getModelResource(ClockworkSpider e){return resource("geo",ClockworkSpider.ID,".geo.json");}
            @Override public ResourceLocation getTextureResource(ClockworkSpider e){return atlas();}
            @Override public ResourceLocation getAnimationResource(ClockworkSpider e){return resource("animations",ClockworkSpider.ID,".animation.json");}
        });shadowRadius=.2F;}
        @Override protected float getDeathMaxRotation(ClockworkSpider e){return 0;}
    }
    public static final class WheelRenderer extends EntityRenderer<MechanistWheel>{
        private final net.minecraft.client.renderer.entity.ItemRenderer items;
        public WheelRenderer(EntityRendererProvider.Context context){super(context);items=context.getItemRenderer();}
        @Override public ResourceLocation getTextureLocation(MechanistWheel e){return net.minecraft.world.inventory.InventoryMenu.BLOCK_ATLAS;}
        @Override public void render(MechanistWheel e,float yaw,float partial,PoseStack pose,MultiBufferSource buffers,int light){
            pose.pushPose();pose.translate(0,.1,0);pose.mulPose(Axis.XP.rotationDegrees(90));pose.mulPose(Axis.ZP.rotationDegrees((e.level().getGameTime()+partial)*22));pose.scale(1.5F,1.5F,1.5F);
            items.renderStatic(new ItemStack(BlueprintSalvage.BRONZE_GEAR_PART.get()),ItemDisplayContext.FIXED,light,net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY,pose,buffers,e.level(),e.getId());pose.popPose();super.render(e,yaw,partial,pose,buffers,light);
        }
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(EliteContent.MECHANIST.get(),MechanistRenderer::new);e.registerEntityRenderer(EliteContent.SPIDER.get(),SpiderRenderer::new);e.registerEntityRenderer(EliteContent.WHEEL.get(),WheelRenderer::new);}
}

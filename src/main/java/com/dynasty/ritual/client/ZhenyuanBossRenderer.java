package com.dynasty.ritual.client;
import com.dynasty.ritual.ZhenyuanBosses;
import com.dynasty.ritual.ZhenyuanSovereign;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class ZhenyuanBossRenderer extends GeoEntityRenderer<ZhenyuanSovereign> {
    public ZhenyuanBossRenderer(EntityRendererProvider.Context context) { super(context,new ZhenyuanBossModel());shadowRadius=1.6F; }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e) { e.registerEntityRenderer(ZhenyuanBosses.FINAL_BOSS.get(),ZhenyuanBossRenderer::new); }
    @Override public void renderRecursively(PoseStack pose,ZhenyuanSovereign boss,GeoBone bone,RenderType type,MultiBufferSource buffer,
            VertexConsumer sink,boolean rerender,float partial,int light,int overlay,float red,float green,float blue,float alpha) {
        boolean glow=bone.getName().contains("eye")||bone.getName().equals("core")||bone.getName().equals("seal_core");
        super.renderRecursively(pose,boss,bone,type,buffer,sink,rerender,partial,glow?15728880:light,overlay,red,green,blue,alpha);
    }
}

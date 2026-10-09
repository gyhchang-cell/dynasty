package com.dynasty.client;

import com.dynasty.WhiskPose;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.renderer.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ModelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Fixed palm grip, handle/ferrule/root and five parented silk segments; both hands use model transforms. */
@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class TaiyiWhiskRenderer extends BlockEntityWithoutLevelRenderer {
    public static final ResourceLocation ICON=new ResourceLocation("dynasty","item/taiyi_whisk_icon");
    private static final ResourceLocation TEXTURE=new ResourceLocation("dynasty","textures/item/taiyi_whisk_mesh.png");
    private final ModelPart model,tailRoot;
    private final ModelPart[] tail=new ModelPart[WhiskPose.SEGMENTS];
    public TaiyiWhiskRenderer(){
        super(Minecraft.getInstance().getBlockEntityRenderDispatcher(),Minecraft.getInstance().getEntityModels());
        var mesh=new MeshDefinition();var root=mesh.getRoot();
        root.addOrReplaceChild("handle",CubeListBuilder.create().texOffs(0,0).addBox(-.8F,-10,-.8F,1.6F,15,1.6F),PartPose.ZERO);
        root.addOrReplaceChild("ferrule",CubeListBuilder.create().texOffs(16,0).addBox(-1.4F,-11.5F,-1.4F,2.8F,3,2.8F),PartPose.ZERO);
        var parent=root.addOrReplaceChild("tail_root",CubeListBuilder.create().texOffs(16,12).addBox(-1.7F,-1,-1,3.4F,2,2),PartPose.offsetAndRotation(0,-11,0,0,0,.85F));
        for(int i=0;i<tail.length;i++){
            float width=3.2F-i*.38F;
            parent=parent.addOrReplaceChild("tail_"+i,CubeListBuilder.create().texOffs(32,0)
                    .addBox(-width/2,0,-.65F,width,3.2F,1.3F)
                    .texOffs(48,0).addBox(-width/2-.4F,0,-.3F,.35F,3.5F,.6F)
                    .addBox(width/2+.05F,0,-.3F,.35F,3.5F,.6F),PartPose.offset(0,i==0?0:3,0));
        }
        model=LayerDefinition.create(mesh,64,32).bakeRoot();tailRoot=model.getChild("tail_root");var part=tailRoot;
        for(int i=0;i<tail.length;i++){part=part.getChild("tail_"+i);tail[i]=part;}
    }
    @SubscribeEvent public static void additional(ModelEvent.RegisterAdditional event){event.register(ICON);}
    @SubscribeEvent public static void reload(net.minecraftforge.client.event.RegisterClientReloadListenersEvent event){
        event.registerReloadListener((net.minecraft.server.packs.resources.ResourceManagerReloadListener)resources->Minecraft.getInstance().execute(EdictRenderer::reset));
    }
    @Override public void renderByItem(ItemStack stack,ItemDisplayContext context,PoseStack poses,MultiBufferSource buffers,int light,int overlay){
        var mc=Minecraft.getInstance();poses.pushPose();
        try{
            poses.translate(.5,.5,.5);
            if(context==ItemDisplayContext.GUI){
                // Preserve the original inventory artwork without recursing through this renderer.
                mc.getItemRenderer().render(stack,context,false,poses,buffers,light,overlay,mc.getModelManager().getModel(ICON));return;
            }
            model.getAllParts().forEach(ModelPart::resetPose);
            var cast=EdictRenderer.heldCast(stack);
            if(cast!=null){
                double age=mc.level.getGameTime()+mc.getFrameTime()-cast.born();int windup=com.dynasty.EdictSpells.WINDUP[cast.kind()];
                tailRoot.zRot+=WhiskPose.bend(age,windup,0)*.6F;
                for(int i=0;i<tail.length;i++){tail[i].zRot=WhiskPose.bend(age,windup,i);tail[i].xRot=tail[i].zRot*.2F;}
            }
            poses.scale(1,-1,1);model.render(poses,buffers.getBuffer(RenderType.entityCutoutNoCull(TEXTURE)),light,overlay);
        }finally{poses.popPose();}
    }
}

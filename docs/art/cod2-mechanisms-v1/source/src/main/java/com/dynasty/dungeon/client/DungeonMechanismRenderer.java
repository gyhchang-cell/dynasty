package com.dynasty.dungeon.client;

import com.dynasty.dungeon.DungeonContent;
import com.dynasty.dungeon.DungeonMechanismBlock;
import com.dynasty.dungeon.DungeonMechanismBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Rendering follows the server phase snapshot. No animation callback causes damage. */
@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class DungeonMechanismRenderer implements BlockEntityRenderer<DungeonMechanismBlockEntity> {
    public DungeonMechanismRenderer(BlockEntityRendererProvider.Context ignored){}
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers event){
        event.registerBlockEntityRenderer(DungeonContent.MECHANISM.get(),DungeonMechanismRenderer::new);
        event.registerEntityRenderer(DungeonContent.TRAP_ARROW.get(),net.minecraft.client.renderer.entity.TippableArrowRenderer::new);
    }
    @Override public void render(DungeonMechanismBlockEntity be,float partial,PoseStack pose,MultiBufferSource buffers,int light,int overlay){
        if(be.kind()==DungeonMechanismBlock.Kind.TRAP&&com.dynasty.dungeon.DungeonTrapProfile.forId(be.mechanismId())==com.dynasty.dungeon.DungeonTrapProfile.CRUSHER){
            pose.pushPose();try{
                int phase=be.getBlockState().getValue(DungeonMechanismBlock.STAGE);float progress=be.visualProgress(partial);
                double y=switch(phase){case 1->2.6+Math.sin(progress*Math.PI*6)*.03;case 2->1.02;case 3->1.02+1.58*progress;default->2.6;};
                pose.translate(.05,y,.05);pose.scale(.9F,.65F,.9F);
                Minecraft.getInstance().getBlockRenderer().renderSingleBlock(Blocks.IRON_BLOCK.defaultBlockState(),pose,buffers,light,overlay);
            }finally{pose.popPose();}return;
        }
        if(be.kind()!=DungeonMechanismBlock.Kind.DOOR&&be.kind()!=DungeonMechanismBlock.Kind.FLOOR)return;
        pose.pushPose();
        try{
            var state=be.getBlockState();
            if(be.kind()==DungeonMechanismBlock.Kind.DOOR){
                float open=be.doorProgress(partial);if(open>=1)return;
                pose.scale(1,1-open,1);
                Minecraft.getInstance().getBlockRenderer().renderSingleBlock(Blocks.POLISHED_DEEPSLATE.defaultBlockState(),pose,buffers,light,overlay);
            }else{
                int phase=state.getValue(DungeonMechanismBlock.STAGE);float progress=be.visualProgress(partial);
                float angle=switch(phase){case 1->(float)Math.sin(progress*Math.PI*6)*3;case 2->90;case 3->90*(1-progress);
                    default->state.getValue(DungeonMechanismBlock.OPEN)?90:0;};
                pose.translate(.5,1,.5);
                pose.mulPose(Axis.YP.rotationDegrees(-state.getValue(DungeonMechanismBlock.FACING).toYRot()));
                pose.translate(-.5,0,-.5);pose.mulPose(Axis.XP.rotationDegrees(angle));
                pose.translate(0,-1,0);
                Minecraft.getInstance().getBlockRenderer().renderSingleBlock(Blocks.DEEPSLATE_TILES.defaultBlockState(),pose,buffers,light,overlay);
            }
        }finally{pose.popPose();}
    }
    @Override public int getViewDistance(){return 64;}
}

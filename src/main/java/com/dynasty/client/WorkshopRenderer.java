package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.workshop.WorkshopBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.blockentity.*;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Visible, per-item fill depth plus the actual materials. No particle entities or ticking BE. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class WorkshopRenderer implements BlockEntityRenderer<WorkshopBlockEntity> {
    public WorkshopRenderer(BlockEntityRendererProvider.Context ignored){}
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerBlockEntityRenderer(WorkshopBlockEntity.TYPE.get(),WorkshopRenderer::new);}
    @Override public void render(WorkshopBlockEntity vat,float partial,PoseStack pose,MultiBufferSource buffers,int light,int overlay){
        int amount=vat.deposited();if(amount==0)return;
        var mc=Minecraft.getInstance();double fill=amount/(double)vat.recipe().total();
        var kind=vat.recipe().kind();
        double base=switch(kind){case REPAIR->.88;case LAPIDARY->.76;case EMBER->.38;case ESSENCE->.95;case HIDE->.32;default->.19;};
        double rise=switch(kind){case MARROW->.54;case HERBAL->.28;case HIDE->.45;case VITALITY->.27;case EMBER->.20;default->.12;};
        double z=kind==com.dynasty.block.LivingWorkshopBlock.Kind.VITALITY?-.30:kind==com.dynasty.block.LivingWorkshopBlock.Kind.LAPIDARY?-.32:0;
        pose.pushPose();
        try {
            pose.translate(.5,0,.5);
            pose.mulPose(Axis.YP.rotationDegrees(-vat.getBlockState().getValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.HORIZONTAL_FACING).toYRot()));
            pose.pushPose();
            pose.translate(-.26,base,z-(kind==com.dynasty.block.LivingWorkshopBlock.Kind.HIDE?.12:.22));
            pose.scale(.52f,(float)(.035+fill*rise),kind==com.dynasty.block.LivingWorkshopBlock.Kind.HIDE?.035f:kind==com.dynasty.block.LivingWorkshopBlock.Kind.LAPIDARY?.18f:.44f);
            var state=switch(vat.recipe().kind()){
                case MARROW -> Blocks.SOUL_SOIL.defaultBlockState();case ESSENCE,LAPIDARY -> Blocks.AMETHYST_BLOCK.defaultBlockState();
                case REPAIR -> Blocks.RAW_GOLD_BLOCK.defaultBlockState();case VITALITY,HERBAL -> Blocks.MOSS_BLOCK.defaultBlockState();
                case HIDE -> Blocks.BROWN_WOOL.defaultBlockState();case EMBER -> Blocks.MAGMA_BLOCK.defaultBlockState();};
            mc.getBlockRenderer().renderSingleBlock(state,pose,buffers,light,overlay);pose.popPose();
            if(vat.ready()){
                pose.translate(0,kind==com.dynasty.block.LivingWorkshopBlock.Kind.VITALITY?.48:Math.max(1.05,base+rise+.2),kind==com.dynasty.block.LivingWorkshopBlock.Kind.VITALITY?-.56:0);pose.scale(.45f,.45f,.45f);
                mc.getItemRenderer().renderStatic(vat.recipe().result(),ItemDisplayContext.GROUND,light,overlay,pose,buffers,vat.getLevel(),0);
            }else{
                int remaining=amount,index=0;
                for(var cost:vat.recipe().costs())for(int i=0;i<cost.count()&&remaining>0;i++,remaining--,index++){
                    double angle=index*2.399963;
                    pose.pushPose();pose.translate(Math.cos(angle)*.16,base+.09+fill*rise+index*.006,z+Math.sin(angle)*.09-(kind==com.dynasty.block.LivingWorkshopBlock.Kind.HIDE?.21:0));pose.scale(.19f,.19f,.19f);
                    pose.mulPose(Axis.YP.rotation((float)angle));
                    mc.getItemRenderer().renderStatic(cost.stack(),ItemDisplayContext.GROUND,light,overlay,pose,buffers,vat.getLevel(),index);pose.popPose();
                }
            }
        }finally{pose.popPose();}
    }
}

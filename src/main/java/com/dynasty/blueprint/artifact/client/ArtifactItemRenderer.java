package com.dynasty.blueprint.artifact.client;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ModelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Real vanilla cuboid weapon mesh in hand and on the ground; a separate16px inventory icon. */
@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class ArtifactItemRenderer extends BlockEntityWithoutLevelRenderer {
    public ArtifactItemRenderer(){super(Minecraft.getInstance().getBlockEntityRenderDispatcher(),Minecraft.getInstance().getEntityModels());}
    @SubscribeEvent public static void additional(ModelEvent.RegisterAdditional e){for(var item:com.dynasty.blueprint.artifact.ArtifactContent.ITEMS.getEntries())for(var suffix:new String[]{"_mesh","_icon"})e.register(new ResourceLocation("dynasty","item/"+item.getId().getPath()+suffix));}
    @Override public void renderByItem(ItemStack stack,ItemDisplayContext context,PoseStack poses,MultiBufferSource buffers,int light,int overlay){
        poses.pushPose();try{poses.translate(.5,.5,.5);boolean held=context==ItemDisplayContext.THIRD_PERSON_RIGHT_HAND||context==ItemDisplayContext.THIRD_PERSON_LEFT_HAND||context==ItemDisplayContext.FIRST_PERSON_RIGHT_HAND||context==ItemDisplayContext.FIRST_PERSON_LEFT_HAND;if(held&&stack.getItem() instanceof com.dynasty.blueprint.artifact.ArtifactItem item){poses.translate(0,item.ability().gripOffsetMetres(),0);if(stack.is(com.dynasty.blueprint.artifact.ArtifactContent.ZHANLU.get()))zhanluPose(stack,poses);}var mc=Minecraft.getInstance();var id=net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem());if(id==null)return;var model=new ResourceLocation(id.getNamespace(),"item/"+id.getPath()+(context==ItemDisplayContext.GUI?"_icon":"_mesh"));mc.getItemRenderer().render(stack,context,false,poses,buffers,light,overlay,mc.getModelManager().getModel(model));}finally{poses.popPose();}
    }
    private static void zhanluPose(ItemStack stack,PoseStack pose){var world=Minecraft.getInstance().level;var tag=stack.getTag();if(world==null||tag==null)return;long now=world.getGameTime();if(tag.contains("DynastyZhanluStanceAt")&&now>=tag.getLong("DynastyZhanluStanceAt")&&now-tag.getLong("DynastyZhanluStanceAt")<=101)return;if(!tag.contains("DynastyZhanluCutAt"))return;long age=now-tag.getLong("DynastyZhanluCutAt");if(age<0||age>10)return;float f=1-age/10F;switch(tag.getInt("DynastyZhanluCut")){case 0->pose.mulPose(com.mojang.math.Axis.XP.rotationDegrees(-75*f));case 1->pose.mulPose(com.mojang.math.Axis.ZP.rotationDegrees(65*f));case 2->{pose.mulPose(com.mojang.math.Axis.XP.rotationDegrees(70*f));pose.mulPose(com.mojang.math.Axis.ZP.rotationDegrees(-25*f));}case 3->pose.mulPose(com.mojang.math.Axis.XP.rotationDegrees(-45*f));default->{}}}
}

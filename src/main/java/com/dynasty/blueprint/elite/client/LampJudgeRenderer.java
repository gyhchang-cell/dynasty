package com.dynasty.blueprint.elite.client;

import com.dynasty.blueprint.elite.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.*;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class LampJudgeRenderer extends GeoEntityRenderer<LampJudge>{
    private final Font font;
    private static ResourceLocation resource(String folder,String id,String suffix){return new ResourceLocation("dynasty",folder+id+suffix);}
    public LampJudgeRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
        public ResourceLocation getModelResource(LampJudge e){return resource("geo/blueprint/elite/",LampJudge.ID,".geo.json");}
        public ResourceLocation getTextureResource(LampJudge e){return resource("textures/entity/blueprint/elite/",LampJudge.ID,".png");}
        public ResourceLocation getAnimationResource(LampJudge e){return resource("animations/blueprint/elite/",LampJudge.ID,".animation.json");}
        @Override public void setCustomAnimations(LampJudge e,long id,software.bernie.geckolib.core.animation.AnimationState<LampJudge> s){super.setCustomAnimations(e,id,s);for(int i=0;i<6;i++)getBone("page_butterfly"+i).ifPresent(b->b.setHidden(!e.isDeadOrDying()));}
    });font=c.getFont();shadowRadius=.8F;}
    @Override protected float getDeathMaxRotation(LampJudge e){return 0;}
    @Override public boolean shouldRender(LampJudge e,Frustum f,double x,double y,double z){
        var box=new AABB(e.getX()-3.3,e.getY()-.4,e.getZ()-3.3,e.getX()+3.3,e.getY()+4,e.getZ()+3.3);
        if(e.skillId()==431){var mark=e.mark();box=box.minmax(new AABB(mark.x-.5,mark.y+2,mark.z-.5,mark.x+.5,mark.y+3.2,mark.z+.5));}
        return e.shouldRender(x,y,z)&&f.isVisible(box);
    }
    @Override public void render(LampJudge e,float yaw,float partial,PoseStack pose,MultiBufferSource buffers,int light){
        super.render(e,yaw,partial,pose,buffers,light);long age=e.level().getGameTime()-e.skillStart();
        if(e.isDeadOrDying()||e.skillId()!=431||age<0||age>=40||entityRenderDispatcher.distanceToSqr(e)>64*64)return;
        var mark=e.mark();String text=age<12?"死 2":age<24?"死 1":"死";
        int color=(age>=36||age>=24&&age<27||age>=12&&age<15)?0xFFFF5448:0xFFC92C30;
        pose.pushPose();pose.translate(mark.x-e.getX(),mark.y-e.getY()+2.6,mark.z-e.getZ());pose.mulPose(entityRenderDispatcher.cameraOrientation());pose.scale(-.04F,-.04F,.04F);
        font.drawInBatch(text,-font.width(text)/2F,0,color,false,pose.last().pose(),buffers,Font.DisplayMode.NORMAL,0,light);pose.popPose();
    }
    public static final class SpellRenderer extends GeoEntityRenderer<JudgeSpell>{
        public SpellRenderer(EntityRendererProvider.Context c){super(c,new GeoModel<>(){
            public ResourceLocation getModelResource(JudgeSpell e){return resource("geo/blueprint/elite/",e.modelId(),".geo.json");}
            public ResourceLocation getTextureResource(JudgeSpell e){return resource("textures/entity/blueprint/elite/",LampJudge.ID,".png");}
            public ResourceLocation getAnimationResource(JudgeSpell e){return resource("animations/blueprint/elite/",e.modelId(),".animation.json");}
            @Override public void setCustomAnimations(JudgeSpell e,long id,software.bernie.geckolib.core.animation.AnimationState<JudgeSpell> s){super.setCustomAnimations(e,id,s);getBone("root").ifPresent(b->b.setScaleZ(e.pen()||e.cage()?1:e.strokeLength()/5.5F));}
        });shadowRadius=0;}
        // Gecko's base renderer supplies body yaw only for LivingEntity. A world-space
        // spell is an Entity, so supply its authoritative yaw explicitly.
        @Override protected void applyRotations(JudgeSpell e,PoseStack pose,float age,float yaw,float partial){super.applyRotations(e,pose,age,e.getYRot(),partial);}
        @Override public boolean shouldRender(JudgeSpell e,Frustum f,double x,double y,double z){
            AABB box;
            if(e.cage())box=new AABB(e.getX()-3.7,e.getY()-.2,e.getZ()-3.7,e.getX()+3.7,e.getY()+3,e.getZ()+3.7);
            else if(e.pen())box=new AABB(e.getX()-.6,e.getY()-.1,e.getZ()-.6,e.getX()+.6,e.getY()+5.1,e.getZ()+.6);
            else {double a=Math.toRadians(e.getYRot());var end=e.position().add(-Math.sin(a)*e.strokeLength(),0,Math.cos(a)*e.strokeLength());box=new AABB(e.position(),end).inflate(.5);}
            return e.shouldRender(x,y,z)&&f.isVisible(box);
        }
    }
    @SubscribeEvent public static void register(EntityRenderersEvent.RegisterRenderers e){e.registerEntityRenderer(EliteContent.LAMP_JUDGE.get(),LampJudgeRenderer::new);e.registerEntityRenderer(EliteContent.JUDGE_PEN.get(),SpellRenderer::new);e.registerEntityRenderer(EliteContent.JUDGE_STROKE.get(),SpellRenderer::new);e.registerEntityRenderer(EliteContent.JUDGE_CAGE.get(),SpellRenderer::new);}
}

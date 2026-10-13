package com.dynasty.client;

import com.dynasty.cod3.*;
import com.mojang.blaze3d.pipeline.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.renderer.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoObjectRenderer;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.nio.file.*;
import java.util.*;

/** Art-only QA: actual baked GeckoLib models, four views plus true black silhouettes. */

public final class SecondaryMaterialArt {
    private static boolean done;
    private static int frames;
    private static final Path OUT=Path.of(System.getProperty("dynasty.secondaryMaterialQa.output"));
    private static final List<String> RESULTS=new ArrayList<>();
    public static void drawAll(Path out)throws Exception{
        Files.createDirectories(out);
        for(String role:List.of("clockwork_rat","wooden_magpie","stone_sprite")){
            for(int angle:List.of(180,135,90,-90,0))npc(role,angle,0);
            npc(role,180,1);npc(role,135,2);
        }
        Files.writeString(OUT.resolve("native-material-views.txt"),String.join("\n",RESULTS));
    }
    private static final class Preview implements GeoAnimatable {
        final String role;final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
        Preview(String role){this.role=role;}
        public void registerControllers(AnimatableManager.ControllerRegistrar r){}
        public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
        public double getTick(Object object){return 0;}
    }
    private static void npc(String role,int angle,int mode)throws Exception{
        var model=new GeoModel<Preview>(){
            public ResourceLocation getModelResource(Preview p){return new ResourceLocation("dynasty","geo/secondary/"+p.role+".geo.json");}
            public ResourceLocation getTextureResource(Preview p){return new ResourceLocation("dynasty","textures/entity/secondary/"+p.role+".png");}
            public ResourceLocation getAnimationResource(Preview p){return new ResourceLocation("dynasty","animations/secondary/"+p.role+".animation.json");}
            public void applyMolangQueries(Preview p,double tick){}
        };
        var renderer=new GeoObjectRenderer<Preview>(model){
            @Override public software.bernie.geckolib.core.object.Color getRenderColor(Preview p,float tick,int light){
                return software.bernie.geckolib.core.object.Color.ofRGBA(mode==1?0:mode==2?190:255,mode==1?0:mode==2?190:255,mode==1?0:mode==2?190:255,255);
            }
        };
        var p=new Preview(role);
        var baked=model.getBakedModel(model.getModelResource(p));
        for(String state:List.of("idle","wander","hunt","flee","attack","special","evade"))
            if(model.getAnimation(p,state)==null)throw new AssertionError(role+" missing "+state);
        frame(role+"-"+(mode==1?"silhouette":mode==2?"gray":angle),1.6,.45,()->{
            var pose=new PoseStack();pose.mulPose(com.mojang.math.Axis.YP.rotationDegrees(angle));
            var buffers=Minecraft.getInstance().renderBuffers().bufferSource();
            com.mojang.blaze3d.platform.Lighting.setupFor3DItems();
            renderer.render(pose,p,buffers,RenderType.entityCutoutNoCull(mode==2?new ResourceLocation("dynasty","textures/qa/material-white.png"):model.getTextureResource(p)),null,15728880);buffers.endBatch();
        });
    }
    private static void frame(String name,double size,double height,Runnable draw)throws Exception{
        var mc=Minecraft.getInstance();var oldProjection=new Matrix4f(RenderSystem.getProjectionMatrix());var sort=RenderSystem.getVertexSorting();
        float fogStart=RenderSystem.getShaderFogStart(),fogEnd=RenderSystem.getShaderFogEnd();var target=new TextureTarget(600,600,true,Minecraft.ON_OSX);var view=RenderSystem.getModelViewStack();view.pushPose();
        try(ImperialRenderState state=new ImperialRenderState()){
            target.setClearColor(.72f,.76f,.8f,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);view.setIdentity();
            view.mulPoseMatrix(new Matrix4f().lookAt(0,(float)height,(float)(size*2.1),0,(float)height,0,0,1,0));RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(new Matrix4f().perspective(.57f,1,.05f,256),VertexSorting.DISTANCE_TO_ORIGIN);RenderSystem.setShaderFogStart(1000);RenderSystem.setShaderFogEnd(2000);RenderSystem.setShaderColor(1,1,1,1);
            RenderSystem.enableDepthTest();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.disableCull();draw.run();GL11.glFinish();
            int error=GL11.glGetError();if(error!=GL11.GL_NO_ERROR)throw new AssertionError(name+" GL error "+error);
            try(var image=Screenshot.takeScreenshot(target)){
                int background=image.getPixelRGBA(0,0),pixels=0;for(int y=0;y<600;y++)for(int x=0;x<600;x++)if(image.getPixelRGBA(x,y)!=background)pixels++;
                if(pixels<10)throw new AssertionError(name+" is empty ("+pixels+")");image.writeToFile(OUT.resolve(name+".png"));RESULTS.add("PASS "+name+" pixels="+pixels);
            }
        }finally{view.popPose();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(oldProjection,sort);RenderSystem.setShaderFogStart(fogStart);RenderSystem.setShaderFogEnd(fogEnd);target.destroyBuffers();mc.getMainRenderTarget().bindWrite(true);}
    }
}

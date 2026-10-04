package com.dynasty.client;

import com.dynasty.ritual.*;
import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexSorting;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.AccessibilityOnboardingScreen;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;
import java.nio.file.*;
import java.util.*;

/** Test-only render entry: no level, no player save, no desktop screenshot, not included in the mod jar. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class ZhenyuanRenderQa {
    private static boolean done;
    private static int ready;
    private static Path output;
    private static final List<String> results=new ArrayList<>();
    @SubscribeEvent public static void tick(TickEvent.RenderTickEvent event) {
        if(!Boolean.getBoolean("dynasty.ritualRenderQa")||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        if(mc.level!=null)throw new AssertionError("QA must not open any world");
        if(mc.getOverlay()==null&&mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
        if(!(mc.screen instanceof TitleScreen)||mc.getOverlay()!=null||++ready<12)return;
        done=true;
        try {
            Path parent=Path.of(System.getProperty("dynasty.ritualRenderQa.output")); Files.createDirectories(parent);
            output=Files.createTempDirectory(parent,"run-");
            results.add("Actual Minecraft offscreen GPU rendering, not an in-world gameplay screenshot.");
            results.add("Renderer: "+GL11.glGetString(GL11.GL_RENDERER));
            check(Math.abs(ZhenyuanNodeRenderer.stageRadius(0)/ZhenyuanNodeRenderer.stageRadius(4)-.375)<.001,"Initial radius 37.5 percent of final");
            for(int i=1;i<=4;i++)check(ZhenyuanNodeRenderer.stageRadius(i)>ZhenyuanNodeRenderer.stageRadius(i-1),"Distinct growth stage "+i);
            for(int mask:new int[]{0,1,3,15,31})capture("heart-"+mask,4,mask,mask==31?1:0,12,5.5);
            for(int slot=0;slot<4;slot++) {
                capture("socket-"+slot+"-empty",slot,0,0,1.7,.9);
                capture("socket-"+slot+"-offered",slot,1<<slot,0,1.7,.9);
            }
            for(int slot=0;slot<4;slot++) {
                var session=new ZhenyuanRitualSavedData.Session("minecraft:overworld",BlockPos.ZERO);
                session.phaseOne=true;session.pendingMask=1<<slot;session.offeringTicks[slot]=ZhenyuanPhaseOne.DURATIONS[slot]*2/3;
                capturePhaseOne("phase1-pillar-"+slot,slot,session,2.5,1.0);
            }
            for(int count=0;count<=4;count++) {
                var session=new ZhenyuanRitualSavedData.Session("minecraft:overworld",BlockPos.ZERO);
                session.phaseOne=true;session.mask=(1<<count)-1;
                capturePhaseOne("phase1-growth-"+count,4,session,12,5.5);
            }
            for(int time:new int[]{60,115,135,155,180,230}) {
                var session=new ZhenyuanRitualSavedData.Session("minecraft:overworld",BlockPos.ZERO);
                session.phaseOne=true;session.mask=31;session.ritualStage="FINAL_RITUAL";session.ritualTicks=time;
                capturePhaseOne("phase1-final-"+time,4,session,14,5.5);
            }
            for(int time:new int[]{0,70,95,130,170,190,230,280})for(int angle:new int[]{0,90,180,270,45}) {
                frame("sovereign-"+time+"-"+angle,5.8,2.6,()-> {
                    var model=new com.dynasty.ritual.client.ZhenyuanBossModel();
                    var baked=model.getBakedModel(model.getModelResource(null));
                    check(model.getAnimationProcessor().getRegisteredBones().size()>=87,"87 independent bones loaded");
                    model.poseArrival(time,null,0);
                    var renderer=new software.bernie.geckolib.renderer.GeoObjectRenderer<ZhenyuanSovereign>(model);
                    var pose=new PoseStack();pose.mulPose(Axis.YP.rotationDegrees(angle));
                    var buffers=mc.renderBuffers().bufferSource();var type=RenderType.entityCutoutNoCull(model.getTextureResource(null));
                    for(var bone:baked.topLevelBones())renderer.renderRecursively(pose,null,bone,type,buffers,buffers.getBuffer(type),true,0,15728880,OverlayTexture.NO_OVERLAY,1,1,1,1);
                    buffers.endBatch();
                });
            }
            check(mc.level==null,"No world opened");
            Files.write(output.resolve("PASS.txt"),results);
            System.out.println("ZHENYUAN_RENDER_QA_PASS "+output);
        } catch(Throwable e) {
            e.printStackTrace();results.add("FAIL: "+e);
            try { if(output!=null)Files.write(output.resolve("FAIL.txt"),results); }catch(Exception ignored){}
        } finally { mc.stop(); }
    }
    private static void capture(String name,int slot,int mask,int stage,double size,double target)throws Exception {
        capture(name,slot,mask,stage,size,target,null);
    }
    private static void capturePhaseOne(String name,int slot,ZhenyuanRitualSavedData.Session session,double size,double target)throws Exception {
        capture(name,slot,session.mask,0,size,target,session);
    }
    private static void capture(String name,int slot,int mask,int stage,double size,double target,ZhenyuanRitualSavedData.Session session)throws Exception {
        var state=ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,slot).setValue(ZhenyuanNodeBlock.ACTIVE,(mask&(1<<slot))!=0);
        var node=new ZhenyuanNodeBlockEntity(BlockPos.ZERO,state);
        node.configure(BlockPos.ZERO,slot);node.syncRitual(mask,stage);
        if(session!=null)node.syncTimeline(session);
        var mc=Minecraft.getInstance();
        var renderer=(ZhenyuanNodeRenderer)mc.getBlockEntityRenderDispatcher().getRenderer(node);
        check(renderer!=null,"Renderer registered for slot "+slot);
        check(mc.getBlockRenderer().getBlockModel(state)!=mc.getModelManager().getMissingModel(),"Baked pedestal exists slot "+slot);
        frame(name,size,target,()-> {
            var pose=new PoseStack();pose.translate(0,target,0);pose.mulPose(Axis.XP.rotationDegrees(16));
            pose.mulPose(Axis.YP.rotationDegrees(-24));pose.translate(-.5,-target,-.5);
            var buffers=mc.renderBuffers().bufferSource();
            mc.getBlockRenderer().renderSingleBlock(state,pose,buffers,15728880,OverlayTexture.NO_OVERLAY);
            renderer.renderAtTime(node,200,0,pose,buffers);
            buffers.endBatch();
        });
    }
    private static void frame(String name,double size,double targetY,Runnable draw)throws Exception {
        var mc=Minecraft.getInstance();var oldProjection=new Matrix4f(RenderSystem.getProjectionMatrix());
        var oldSort=RenderSystem.getVertexSorting();float fogStart=RenderSystem.getShaderFogStart(),fogEnd=RenderSystem.getShaderFogEnd();
        RenderTarget target=new TextureTarget(1200,1200,true,Minecraft.ON_OSX);
        var mv=RenderSystem.getModelViewStack();mv.pushPose();
        try {
            target.setClearColor(.055F,.075F,.105F,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);
            mv.setIdentity();mv.mulPoseMatrix(new Matrix4f().lookAt(0,(float)targetY,(float)(size*2.1),0,(float)targetY,0,0,1,0));
            RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(new Matrix4f().perspective(.57F,1,.05F,256),VertexSorting.byDistance(0,(float)targetY,(float)(size*2.1)));
            RenderSystem.setShaderFogStart(1000);RenderSystem.setShaderFogEnd(2000);RenderSystem.setShaderColor(1,1,1,1);
            RenderSystem.enableDepthTest();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.disableCull();
            draw.run();GL11.glFinish();check(GL11.glGetError()==GL11.GL_NO_ERROR,name+" no GL errors");
            try(var image=Screenshot.takeScreenshot(target)) {
                int bg=image.getPixelRGBA(0,0),count=0;
                for(int y=0;y<1200;y++)for(int x=0;x<1200;x++)if(image.getPixelRGBA(x,y)!=bg)count++;
                check(count>2000,name+" non-background pixels="+count);image.writeToFile(output.resolve(name+".png"));
            }
        } finally {
            mv.popPose();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(oldProjection,oldSort);
            RenderSystem.setShaderFogStart(fogStart);RenderSystem.setShaderFogEnd(fogEnd);target.destroyBuffers();mc.getMainRenderTarget().bindWrite(true);
        }
    }
    private static void check(boolean condition,String message) {if(!condition)throw new AssertionError(message);results.add("PASS: "+message);}
}

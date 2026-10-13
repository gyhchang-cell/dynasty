package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.cod3.SevenStarFlash;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.List;

/** Independent finite geometry; does not edit the shared scenic/VFX renderer. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
public final class SevenStarFlashRenderer {
    private static final int LIMIT=8;
    private static final List<Cod3VisualPacket> ACTIVE=new ArrayList<>();
    private static final BufferBuilder BUFFER=new BufferBuilder(16384);
    private static ClientLevel world;

    /** True consumes this dedicated cue, including malformed/expired instances. */
    public static boolean receive(Cod3VisualPacket p) {
        if(!SevenStarFlash.CUE.equals(p.sequence()))return false;
        clean();
        if(world==null||!SevenStarFlash.accepts(p)||!p.dimension().equals(world.dimension().location().toString()))return true;
        long age=world.getGameTime()-p.start();
        if(age< -2||age>=p.duration()||ACTIVE.contains(p))return true;
        if(ACTIVE.size()>=LIMIT)ACTIVE.remove(0);
        ACTIVE.add(p);return true;
    }
    private static void clean() {
        var current=Minecraft.getInstance().level;
        if(current!=world){ACTIVE.clear();world=current;}
        if(world!=null)ACTIVE.removeIf(p->world.getGameTime()-p.start()>=p.duration());
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e) {
        if(e.phase==TickEvent.Phase.END)clean();
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent e) {
        if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_PARTICLES)return;
        clean();if(world==null||ACTIVE.isEmpty())return;
        var camera=e.getCamera().getPosition();var pose=e.getPoseStack();pose.pushPose();boolean drawing=false;
        try(ImperialRenderState state=new ImperialRenderState()) {
            RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.enableDepthTest();
            RenderSystem.depthMask(false);RenderSystem.disableCull();RenderSystem.setShaderColor(1,1,1,1);
            RenderSystem.setShader(GameRenderer::getPositionColorShader);
            pose.translate(-camera.x,-camera.y,-camera.z);
            BUFFER.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);drawing=true;
            var matrix=pose.last().pose();
            for(var p:ACTIVE) {
                if(p.origin().distanceToSqr(camera)>64*64)continue;
                double age=world.getGameTime()-p.start()+e.getPartialTick();
                var right=SevenStarFlash.right(p.direction());
                for(int i=0;i<SevenStarFlash.COUNT;i++) {
                    var pulse=SevenStarFlash.pulse(i,age);if(pulse.alpha()<=0)continue;
                    var center=SevenStarFlash.point(i,p.origin(),p.direction());
                    star(matrix,center,right,pulse.size(),pulse.alpha(),p.tint());
                    // A second hard-edged plane keeps the seven flashes readable
                    // to observers standing side-on to the original attack.
                    star(matrix,center,new Vec3(-right.z,0,right.x),pulse.size(),pulse.alpha(),p.tint());
                    if(i>0)link(matrix,SevenStarFlash.point(i-1,p.origin(),p.direction()),center,right,pulse.alpha()*.25,p.tint());
                }
            }
            BufferUploader.drawWithShader(BUFFER.end());drawing=false;
        }finally{if(drawing)BUFFER.discard();pose.popPose();}
    }
    private static void star(Matrix4f m,Vec3 center,Vec3 r,double size,double alpha,int tint) {
        // Eight hard corners, not a particle shower or camera-facing overlay.
        double[][] edge={{0,1},{.22,.22},{1,0},{.22,-.22},{0,-1},{-.22,-.22},{-1,0},{-.22,.22}};
        for(int i=0;i<edge.length;i++) {
            var a=center.add(r.scale(edge[i][0]*size)).add(0,edge[i][1]*size,0);
            var b=center.add(r.scale(edge[(i+1)%8][0]*size)).add(0,edge[(i+1)%8][1]*size,0);
            triangle(m,center,a,b,alpha,tint);
        }
    }
    private static void link(Matrix4f m,Vec3 a,Vec3 b,Vec3 r,double alpha,int tint) {
        Vec3 direction=b.subtract(a);
        Vec3 offset=r.scale(-direction.y).add(0,direction.dot(r),0).normalize().scale(.008);
        triangle(m,a.add(offset),b.add(offset),b.subtract(offset),alpha,tint);
        triangle(m,a.add(offset),b.subtract(offset),a.subtract(offset),alpha,tint);
    }
    private static void triangle(Matrix4f m,Vec3 a,Vec3 b,Vec3 c,double alpha,int tint) {
        for(var v:new Vec3[]{a,b,c})BUFFER.vertex(m,(float)v.x,(float)v.y,(float)v.z)
            .color((tint>>16&255)/255f,(tint>>8&255)/255f,(tint&255)/255f,(float)alpha).endVertex();
    }
    private SevenStarFlashRenderer() {}
}

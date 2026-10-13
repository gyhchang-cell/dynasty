package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.cod3.WeaponImpactVisual;
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

/** Material hit geometry on the existing packet; bounded independently of scenic effects. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
public final class WeaponImpactRenderer {
    private static final int LIMIT=12;
    private static final List<Cod3VisualPacket> ACTIVE=new ArrayList<>();
    private static final BufferBuilder BUFFER=new BufferBuilder(65536);
    private static ClientLevel world;

    public static boolean receive(Cod3VisualPacket p) {
        if(!p.sequence().startsWith(WeaponImpactVisual.PREFIX))return false;
        clean();
        if(world==null||!WeaponImpactVisual.accepts(p)||!p.dimension().equals(world.dimension().location().toString()))return true;
        long age=world.getGameTime()-p.start();
        if(age< -2||age>=p.duration()||ACTIVE.contains(p))return true;
        if(ACTIVE.size()>=LIMIT)ACTIVE.remove(0);ACTIVE.add(p);return true;
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
            RenderSystem.setShader(GameRenderer::getPositionColorShader);pose.translate(-camera.x,-camera.y,-camera.z);
            BUFFER.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);drawing=true;
            var matrix=pose.last().pose();
            for(var p:ACTIVE) {
                if(p.origin().distanceToSqr(camera)>64*64)continue;
                double age=world.getGameTime()-p.start()+e.getPartialTick();
                for(var t:WeaponImpactVisual.geometry(p,age))triangle(matrix,t);
            }
            BufferUploader.drawWithShader(BUFFER.end());drawing=false;
        }finally{if(drawing)BUFFER.discard();pose.popPose();}
    }
    private static void triangle(Matrix4f m,WeaponImpactVisual.Triangle t) {
        for(Vec3 v:new Vec3[]{t.a(),t.b(),t.c()})BUFFER.vertex(m,(float)v.x,(float)v.y,(float)v.z)
            .color((t.color()>>16&255)/255f,(t.color()>>8&255)/255f,(t.color()&255)/255f,(float)t.alpha()).endVertex();
    }
    private WeaponImpactRenderer() {}
}

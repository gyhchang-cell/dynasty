package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.ArrayList;
import java.util.List;

@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
public final class DragonDecalRenderer {
    private static final ResourceLocation TEXTURE=new ResourceLocation(Dynasty.MODID,"textures/effect/dragon_slayer_decal.png");
    private static final List<Cod3VisualPacket> ACTIVE=new ArrayList<>();
    private static final BufferBuilder BUFFER=new BufferBuilder(4096);
    private static ClientLevel world;
    public static boolean receive(Cod3VisualPacket p) {
        if(!DragonDecal.CUE.equals(p.sequence()))return false;
        clean();if(world==null||!DragonDecal.accepts(p)||!p.dimension().equals(world.dimension().location().toString()))return true;
        long age=world.getGameTime()-p.start();if(age< -2||age>=p.duration()||ACTIVE.contains(p))return true;
        ACTIVE.removeIf(old->old.entityId()==p.entityId());if(ACTIVE.size()>=12)ACTIVE.remove(0);ACTIVE.add(p);return true;
    }
    private static void clean() {
        var current=Minecraft.getInstance().level;if(current!=world){ACTIVE.clear();world=current;}
        if(world!=null)ACTIVE.removeIf(p->world.getGameTime()-p.start()>=p.duration()||world.getEntity(p.entityId())==null||world.getEntity(p.entityId()).isRemoved()
                ||world.getEntity(p.entityId()) instanceof net.minecraft.world.entity.LivingEntity alive&&!alive.isAlive());
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){if(e.phase==TickEvent.Phase.END)clean();}
    @SubscribeEvent public static void render(RenderLevelStageEvent e) {
        if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_PARTICLES)return;
        clean();if(world==null||ACTIVE.isEmpty())return;
        var camera=e.getCamera().getPosition();var pose=e.getPoseStack();pose.pushPose();boolean drawing=false;
        try(ImperialRenderState state=new ImperialRenderState()) {
            RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.enableDepthTest();RenderSystem.depthMask(false);
            RenderSystem.disableCull();RenderSystem.setShaderColor(1,1,1,1);RenderSystem.setShader(GameRenderer::getPositionTexColorShader);
            RenderSystem.setShaderTexture(0,TEXTURE);
            pose.translate(-camera.x,-camera.y,-camera.z);BUFFER.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_TEX_COLOR);drawing=true;
            var matrix=pose.last().pose();float partial=e.getPartialTick();
            for(var p:ACTIVE) {
                var actor=world.getEntity(p.entityId());if(actor==null||actor.isRemoved())continue;
                var anchor=DragonDecal.anchor(p,actor,partial);if(anchor==null||anchor.distanceToSqr(camera)>64*64)continue;
                for(var t:DragonDecal.geometry(p,world.getGameTime()-p.start()+partial,anchor.subtract(p.origin())))triangle(matrix,t);
            }
            BufferUploader.drawWithShader(BUFFER.end());drawing=false;
        }finally{if(drawing)BUFFER.discard();pose.popPose();}
    }
    private static void triangle(Matrix4f matrix,DragonDecal.Triangle t) {
        for(var v:new DragonDecal.Vertex[]{t.a(),t.b(),t.c()})BUFFER.vertex(matrix,(float)v.position().x,(float)v.position().y,(float)v.position().z)
                .uv((float)v.u(),(float)v.v()).color(1f,1f,1f,(float)t.alpha()).endVertex();
    }
    private DragonDecalRenderer() {}
}

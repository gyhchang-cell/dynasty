package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.*;

@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
public final class WeaponLiftRenderer {
    private static final List<Cod3VisualPacket> ACTIVE=new ArrayList<>();
    private static final BufferBuilder BUFFER=new BufferBuilder(65536);
    private static ClientLevel world;
    public static boolean receive(Cod3VisualPacket p) {
        if(!p.sequence().startsWith(WeaponLift.PREFIX))return false;
        clean();if(world==null||!WeaponLift.accepts(p)||!p.dimension().equals(world.dimension().location().toString()))return true;
        long age=world.getGameTime()-p.start();if(age< -2||age>=p.duration()||ACTIVE.contains(p))return true;
        ACTIVE.removeIf(old->old.entityId()==p.entityId());if(ACTIVE.size()>=12)ACTIVE.remove(0);ACTIVE.add(p);return true;
    }
    private static void clean() {
        var current=Minecraft.getInstance().level;if(current!=world){ACTIVE.clear();world=current;}
        if(world!=null)ACTIVE.removeIf(p->world.getGameTime()-p.start()>=p.duration()||!(world.getEntity(p.entityId()) instanceof LivingEntity t)||!t.isAlive()||t.isRemoved());
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){if(e.phase==TickEvent.Phase.END)clean();}
    @SubscribeEvent public static void render(RenderLevelStageEvent e) {
        if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_PARTICLES)return;
        clean();if(world==null||ACTIVE.isEmpty())return;
        var camera=e.getCamera().getPosition();var pose=e.getPoseStack();pose.pushPose();boolean drawing=false;
        try(ImperialRenderState state=new ImperialRenderState()) {
            RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.enableDepthTest();RenderSystem.depthMask(false);
            RenderSystem.disableCull();RenderSystem.setShaderColor(1,1,1,1);RenderSystem.setShader(GameRenderer::getPositionColorShader);
            pose.translate(-camera.x,-camera.y,-camera.z);BUFFER.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);drawing=true;
            var matrix=pose.last().pose();float partial=e.getPartialTick();
            for(var p:ACTIVE) {
                var actor=(LivingEntity)world.getEntity(p.entityId());if(actor==null||!actor.isAlive())continue;
                var feet=new Vec3(Mth.lerp(partial,actor.xOld,actor.getX()),Mth.lerp(partial,actor.yOld,actor.getY()),Mth.lerp(partial,actor.zOld,actor.getZ()));
                if(feet.distanceToSqr(p.origin())>64||feet.distanceToSqr(camera)>64*64)continue;
                for(var t:WeaponLift.geometry(p,world.getGameTime()-p.start()+partial,feet,!actor.onGround()))triangle(matrix,t);
            }
            BufferUploader.drawWithShader(BUFFER.end());drawing=false;
        }finally{if(drawing)BUFFER.discard();pose.popPose();}
    }
    private static void triangle(Matrix4f matrix,WeaponImpactVisual.Triangle t) {
        for(var v:new Vec3[]{t.a(),t.b(),t.c()})BUFFER.vertex(matrix,(float)v.x,(float)v.y,(float)v.z)
                .color((t.color()>>16&255)/255f,(t.color()>>8&255)/255f,(t.color()&255)/255f,(float)t.alpha()).endVertex();
    }
    private WeaponLiftRenderer() {}
}

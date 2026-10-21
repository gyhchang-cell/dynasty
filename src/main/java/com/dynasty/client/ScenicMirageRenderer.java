package com.dynasty.client;

import com.dynasty.cod3.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.phys.Vec3;
import java.util.*;

/** Cached exposed vanilla block-model faces, read from the same source as the NBT. No world writes. */
final class ScenicMirageRenderer {
    private record Check(long tick,boolean valid){}
    private static final Map<Cod3VisualPacket,Check> CHECKS=new HashMap<>();
    private static final ScenicBlockMirageMesh MESH=new ScenicBlockMirageMesh("scenic/mirage_street.json");
    private static ClientLevel world;
    static int lastDrawnFaces;
    static void clear(){CHECKS.clear();world=null;}
    static void retain(List<Cod3VisualPacket> active){CHECKS.keySet().retainAll(active);}
    static boolean valid(ClientLevel level,Cod3VisualPacket p){
        if(world!=level){clear();world=level;}
        if(ScenicMirageSite.visibility(level)<=0)return false;
        var old=CHECKS.get(p);long now=level.getGameTime();
        if(old==null||now<old.tick()||now-old.tick()>=20){old=new Check(now,ScenicMirageSite.valid(level,p.origin()));CHECKS.put(p,old);}
        return old.valid();
    }
    static void render(List<Cod3VisualPacket> scenes,PoseStack pose,Vec3 camera,float partial){
        lastDrawnFaces=0;var level=Minecraft.getInstance().level;if(level==null)return;retain(scenes);
        // The row explicitly permits one street. Choose the nearest valid active regional packet.
        var packet=scenes.stream().filter(p->valid(level,p)).min(Comparator.comparingDouble(p->p.origin().distanceToSqr(camera))).orElse(null);
        if(packet==null)return;double age=level.getGameTime()-packet.start()+partial;
        if(age<0||age>=packet.duration())return;
        float alpha=(float)ScenicMirageSite.alpha(age,packet.duration(),packet.origin().distanceTo(camera),ScenicMirageSite.visibility(level));if(alpha<=0)return;
        pose.pushPose();
        try{
            // A 1/64m visual depth separation prevents the phantom paving fighting real sand.
            // This is a render-only bias; saved ground origin and terrain remain untouched.
            pose.translate(packet.origin().x,packet.origin().y+1./64,packet.origin().z);
            lastDrawnFaces=MESH.render(pose,camera.subtract(packet.origin()),alpha,1,1,1);
        }finally{pose.popPose();}
    }
    private ScenicMirageRenderer(){}
}

package com.dynasty.client;
import com.dynasty.cod3.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.*;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.phys.Vec3;
import java.util.*;
/** Same fixed anchors in both LODs. Far mesh contains only the three original flags. */
final class ScenicGreatWallRenderer {
    private record Check(long tick,boolean valid){}
    private static final Map<Cod3VisualPacket,Check> CHECKS=new HashMap<>();
    private static final ScenicBlockMirageMesh FULL=new ScenicBlockMirageMesh("scenic/great_wall_echo.json"),FLAGS=new ScenicBlockMirageMesh("scenic/great_wall_echo_flags.json");
    private static ClientLevel world;
    static int lastDrawnFaces;static double lastFarBlend;
    static void clear(){CHECKS.clear();world=null;lastDrawnFaces=0;lastFarBlend=0;}
    static boolean valid(ClientLevel level,Cod3VisualPacket p){
        if(world!=level){clear();world=level;}
        if(ScenicGreatWallSite.visibility(level)<=0)return false;
        var old=CHECKS.get(p);long now=level.getGameTime();
        if(old==null||now<old.tick()||now-old.tick()>=20){old=new Check(now,ScenicGreatWallSite.valid(level,p.origin()));CHECKS.put(p,old);}
        return old.valid();
    }
    static void render(List<Cod3VisualPacket> scenes,PoseStack pose,Vec3 camera,float partial){
        lastDrawnFaces=0;lastFarBlend=0;var level=Minecraft.getInstance().level;if(level==null)return;CHECKS.keySet().retainAll(scenes);
        var packet=scenes.stream().filter(p->valid(level,p)).min(Comparator.comparingDouble(p->p.origin().distanceToSqr(camera))).orElse(null);if(packet==null)return;
        double age=level.getGameTime()-packet.start()+partial,distance=packet.origin().distanceTo(camera);if(age<0||age>=packet.duration())return;
        float alpha=(float)ScenicGreatWallSite.alpha(age,packet.duration(),distance,ScenicGreatWallSite.visibility(level));if(alpha<=0)return;
        double far=ScenicGreatWallSite.farBlend(distance,Minecraft.getInstance().options.particles().get()==ParticleStatus.MINIMAL);lastFarBlend=far;
        pose.pushPose();try{
            pose.translate(packet.origin().x,packet.origin().y+1./64,packet.origin().z);var local=camera.subtract(packet.origin());
            if(far<1)lastDrawnFaces+=FULL.render(pose,local,alpha*(float)(1-far),.82f,.91f,1);
            if(far>0)lastDrawnFaces+=FLAGS.render(pose,local,alpha*(float)far,.82f,.91f,1);
        }finally{pose.popPose();}
    }
    private ScenicGreatWallRenderer(){}
}

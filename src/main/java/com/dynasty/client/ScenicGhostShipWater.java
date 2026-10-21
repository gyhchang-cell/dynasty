package com.dynasty.client;

import com.dynasty.cod3.*;
import com.mojang.blaze3d.vertex.BufferBuilder;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.*;

/** The model, broken wake and sound share one checked loaded-liquid route. */
final class ScenicGhostShipWater {
    private record Check(long tick,boolean valid){}
    private static ClientLevel world;
    private static final Map<Cod3VisualPacket,Check> CHECKS=new HashMap<>();
    static void clear(){CHECKS.clear();world=null;}
    static void retain(List<Cod3VisualPacket> active){CHECKS.keySet().retainAll(active);}
    static boolean valid(ClientLevel level,Cod3VisualPacket p){
        if(world!=level){CHECKS.clear();world=level;}
        if(ScenicGhostShipRoute.visibility(level)<=0)return false;
        var old=CHECKS.get(p);long now=level.getGameTime();
        if(old==null||now-old.tick()>=10||now<old.tick()){
            old=new Check(now,ScenicGhostShipRoute.valid(level,new ScenicGhostShipRoute.Route(p.origin(),p.direction())));CHECKS.put(p,old);
        }
        return old.valid();
    }
    static void draw(BufferBuilder buffer,Matrix4f matrix,ClientLevel level,Cod3VisualPacket p,Vec3 camera,double age,boolean low){
        if(!valid(level,p))return;var at=ScenicGhostShipRoute.position(p,age);double distance=at.distanceTo(camera);
        double alpha=ScenicGhostShipRoute.alpha(p,age,distance,ScenicGhostShipRoute.visibility(level));if(alpha<=0)return;
        var f=p.direction();var right=new Vec3(f.z,0,-f.x);var quads=new ArrayList<ScenicAurora.Quad>();
        int lanes=low||distance>96?2:4;
        for(int i=0;i<lanes;i++)for(int side:new int[]{-1,1}){
            double phase=(age/100.+i*.27)%1,z=-10-i*2.4-phase*2,x=side*(2.7+phase*.8),a=alpha*(1-phase)*.18;
            quads.add(new ScenicAurora.Quad(point(right,f,x-.12,.025,z-1.1),point(right,f,x+.12,.025,z-1.1),point(right,f,x+.12,.025,z+1.1),point(right,f,x-.12,.025,z+1.1),0x8aada7,a,true));
        }
        // Small phosphor motes sit beside the lanterns, never over the main sail seal.
        for(int i=0;i<(low?2:4);i++){
            double x=i%2==0?-2.6:2.6,z=i<2?-7:5,y=2.1+Math.sin(age/25.+i)*.15,w=.06;
            quads.add(new ScenicAurora.Quad(point(right,f,x-w,y-w,z),point(right,f,x+w,y-w,z),point(right,f,x+w,y+w,z),point(right,f,x-w,y+w,z),0x9dc6b5,alpha*.55,true));
        }
        ScenicSkyRenderer.append(buffer,matrix,at,camera,quads);
    }
    private static ScenicAurora.Point point(Vec3 right,Vec3 forward,double x,double y,double z){var p=right.scale(x).add(forward.scale(z));return new ScenicAurora.Point(p.x,y,p.z);}
    private ScenicGhostShipWater(){}
}

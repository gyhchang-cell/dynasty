package com.dynasty.client;

import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.cod3.ScenicAurora;
import com.mojang.blaze3d.vertex.BufferBuilder;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.ArrayList;

/** Shared clock/visibility for the dragon, its sparse wake and local sound. */
final class ScenicDragonFlight {
    static double visibility(long dayTime,double rain){
        long time=Math.floorMod(dayTime,24000);
        if(time<11000||time>13000||rain>.01)return 0;
        return Math.min(1,Math.min((time-11000)/40.,(13000-time)/40.));
    }
    static Vec3 forward(Cod3VisualPacket packet){
        var f=packet.direction().multiply(1,0,1).normalize();
        return f.lengthSqr()<1e-8?new Vec3(0,0,1):f;
    }
    static Vec3 position(Cod3VisualPacket packet,double age){
        return packet.origin().add(forward(packet).scale((age/packet.duration()-.5)*56)).add(0,44,0);
    }
    static double soundVolume(Cod3VisualPacket packet,double age,Vec3 listener,long dayTime,double rain){
        double distance=position(packet,age).distanceTo(listener);
        return .08*visibility(dayTime,rain)*ScenicAurora.envelope(age,packet.duration(),distance)
            *Math.max(0,Math.min(1,(128-distance)/64));
    }
    static void draw(BufferBuilder buffer,Matrix4f matrix,Cod3VisualPacket packet,Vec3 camera,
                     double age,boolean low,double visibility){
        var origin=position(packet,age);double distance=origin.distanceTo(camera);
        double alpha=visibility*ScenicAurora.envelope(age,packet.duration(),distance)
            *Math.max(0,Math.min(1,(distance-24)/16));
        if(alpha<=0)return;
        var f=forward(packet);var right=new Vec3(f.z,0,-f.x);
        var quads=new ArrayList<ScenicAurora.Quad>();
        // Detached, coarse cloud wisps sit below the tail. They never form a sheet over the rig.
        int count=low||distance>96?4:8;
        for(int i=0;i<count;i++){
            double phase=(age/160.+i*.173)%1,z=-5-i*2.5-phase*3;
            double x=(i%2==0?-1:1)*(3+(i%3)*.7),y=-.4-(i%3)*.35;
            double width=1.3+(i%2)*.5,length=2.4;
            Vec3 at=right.scale(x).add(f.scale(z));
            quads.add(new ScenicAurora.Quad(point(at,right,f,-width,y,-length),point(at,right,f,width,y,-length),
                point(at,right,f,width,y,length),point(at,right,f,-width,y,length),
                i%2==0?0x9fc9c8:0xc0dcd3,alpha*.16*Math.sin(phase*Math.PI),true));
        }
        ScenicSkyRenderer.append(buffer,matrix,origin,camera,quads);
    }
    private static ScenicAurora.Point point(Vec3 at,Vec3 right,Vec3 forward,double x,double y,double z){
        var p=at.add(right.scale(x)).add(forward.scale(z));return new ScenicAurora.Point(p.x,y,p.z);
    }
    private ScenicDragonFlight(){}
}

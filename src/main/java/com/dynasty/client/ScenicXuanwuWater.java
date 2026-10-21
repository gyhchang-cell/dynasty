package com.dynasty.client;

import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.cod3.ScenicAurora;
import com.mojang.blaze3d.vertex.BufferBuilder;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.ArrayList;
import javax.annotation.Nullable;

/** Waterline shared by the actual rig, its wake and quiet ambient cue. Never loads terrain. */
final class ScenicXuanwuWater {
    @Nullable static Vec3 surface(ClientLevel level,Cod3VisualPacket packet){
        if(level.getRainLevel(1)>.01f)return null;
        var at=BlockPos.containing(packet.origin());
        if(!level.hasChunkAt(at))return null;
        int y=level.getHeight(Heightmap.Types.MOTION_BLOCKING,at.getX(),at.getZ());
        for(int dx:new int[]{-8,0,8})for(int dz:new int[]{-8,0,8}){
            var water=new BlockPos(at.getX()+dx,y-1,at.getZ()+dz);
            if(!level.hasChunkAt(water)||!level.getFluidState(water).is(FluidTags.WATER))return null;
        }
        return new Vec3(packet.origin().x,y,packet.origin().z);
    }
    static double rise(double age,int duration){
        double t=Math.max(0,Math.min(1,Math.min(age,duration-age)/180.));
        return -9+7*t*t*(3-2*t);
    }
    static double soundVolume(double age,int duration,double distance){
        return .12*ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,(48-distance)/24));
    }
    static void draw(BufferBuilder buffer,Matrix4f matrix,ClientLevel level,Cod3VisualPacket packet,Vec3 camera,double age,boolean low){
        var origin=surface(level,packet);if(origin==null)return;
        double distance=origin.distanceTo(camera),alpha=ScenicAurora.envelope(age,packet.duration(),distance)*Math.max(0,Math.min(1,(distance-24)/16));
        if(alpha<=0)return;
        var mesh=new ArrayList<ScenicAurora.Quad>();
        int rings=low||distance>96?2:3;
        for(int i=0;i<rings;i++){
            double phase=(age/110.+i/(double)rings)%1,x=14+phase*6,z=22+phase*6,w=.28;
            double a=alpha*(1-phase)*.35;
            // Broken foam bands: a continuous rectangle reads as a debug bounding box.
            for(int lane=-1;lane<=1;lane++){
                double cx=lane*x*.65,cz=lane*z*.65;
                rect(mesh,cx-x*.22,-z,cx+x*.22,-z+w,a);rect(mesh,cx-x*.22,z-w,cx+x*.22,z,a);
                rect(mesh,-x,cz-z*.22,-x+w,cz+z*.22,a);rect(mesh,x-w,cz-z*.22,x,cz+z*.22,a);
            }
        }
        if(!low&&distance<=96)for(int side:new int[]{-1,1})for(int lane=-1;lane<=1;lane++){
            double phase=(age/70.+lane*.19+side*.13+2)%1,x=side*14,z=lane*10;
            double h=.6+3*Math.sin(phase*Math.PI),w=.23,a=alpha*Math.sin(phase*Math.PI)*.4;
            var p=new ScenicAurora.Point(x-w,.06,z);var q=new ScenicAurora.Point(x+w,.06,z);
            mesh.add(new ScenicAurora.Quad(p,q,new ScenicAurora.Point(x+w,h,z),new ScenicAurora.Point(x-w,h,z),0xa9cdd2,a,true));
            mesh.add(new ScenicAurora.Quad(new ScenicAurora.Point(x,.06,z-w),new ScenicAurora.Point(x,.06,z+w),new ScenicAurora.Point(x,h,z+w),new ScenicAurora.Point(x,h,z-w),0xa9cdd2,a,true));
        }
        ScenicSkyRenderer.append(buffer,matrix,origin,camera,mesh);
    }
    private static void rect(ArrayList<ScenicAurora.Quad> out,double x0,double z0,double x1,double z1,double alpha){
        out.add(new ScenicAurora.Quad(new ScenicAurora.Point(x0,.04,z0),new ScenicAurora.Point(x1,.04,z0),new ScenicAurora.Point(x1,.04,z1),new ScenicAurora.Point(x0,.04,z1),0x95c0c5,alpha,false));
    }
    private ScenicXuanwuWater(){}
}

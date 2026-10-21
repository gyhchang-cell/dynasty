package com.dynasty.cod3;

import com.dynasty.cod3.ScenicAurora.Point;
import com.dynasty.cod3.ScenicAurora.Quad;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/** Seeded autumn foliage. Surface heights are supplied by the loaded client terrain, never generated here. */
public final class ScenicGoldenLeaves {
    public record Column(double ground,double canopy) {}
    @FunctionalInterface public interface Surface { Column column(double x,double z); }
    public static final int MAX_QUADS=480;
    public static double visibility(long dayTime,double rain) {
        long day=Math.floorMod(dayTime,24000);
        return clamp((day-10500)/500.)*clamp((14500-day)/500.)*(1-clamp(rain));
    }
    public static List<Quad> mesh(long seed,double age,int duration,double distance,boolean low,double visibility,Surface surface) {
        double fade=ScenicAurora.envelope(age,duration,distance)*clamp(visibility);
        if(fade<=0)return List.of();
        boolean far=low||distance>=96;
        int count=far?24:distance>=32?56:96;
        var out=new ArrayList<Quad>(MAX_QUADS);
        for(int i=0;i<count;i++) {
            Random r=new Random(seed^(0x9e3779b97f4a7c15L*(i+1)));
            double initial=r.nextDouble(),period=220+r.nextInt(101),cycle=mod(age/period+initial);
            double emitterX=(r.nextDouble()-.5)*48,emitterZ=(r.nextDouble()-.5)*40;
            Column column=surface.column(emitterX,emitterZ);
            if(column==null||!Double.isFinite(column.ground()+column.canopy())||column.canopy()-column.ground()<3)continue;
            double x=emitterX+(cycle-.5)*3+Math.sin(age/68.+i)*.8;
            double z=emitterZ+Math.sin(age/92.+initial*6)*.9;
            Column landing=surface.column(x,z);
            if(landing==null||!Double.isFinite(landing.ground()))continue;
            double ground=Math.max(column.ground(),landing.ground());
            double height=column.canopy()-ground-1;
            if(height<2)continue;
            // Keep the longest stalk (.43 * 1.25) above the landing surface.
            double y=ground+.6+(1-cycle)*height;
            double lod=i>=56?clamp((32-distance)/8.):i>=24?clamp((96-distance)/16.):1;
            double alpha=.88*fade*lod*clamp(cycle*12)*clamp((1-cycle)*10);
            if(alpha<=0)continue;
            double yaw=r.nextDouble()*Math.PI*2+age*.018,pitch=Math.sin(age/29.+i)*1.1;
            double size=.75+r.nextDouble()*.5;
            if(far) {
                tile(out,x,y,z,-.24,-.24,.24,.24,yaw,pitch,1,0xe2b65a,alpha);
                tile(out,x,y,z,-.24,-.24,.24,.24,yaw+Math.PI/2,pitch,1,0xe2b65a,alpha);
            }else {
                // A broad stepped blade with a narrow tip, two tone centre and short stalk.
                tile(out,x,y,z,-.10,-.30,.10,-.16,yaw,pitch,size,0xc08b3c,alpha);
                tile(out,x,y,z,-.20,-.16,0,.16,yaw,pitch,size,0xe2b65a,alpha);
                tile(out,x,y,z,0,-.16,.20,.16,yaw,pitch,size,0xe7c978,alpha);
                tile(out,x,y,z,-.07,.16,.07,.30,yaw,pitch,size,0xe2b65a,alpha);
                tile(out,x,y,z,-.035,-.43,.035,-.30,yaw,pitch,size,0x816037,alpha);
            }
        }
        return List.copyOf(out);
    }
    private static void tile(List<Quad> out,double x,double y,double z,double u0,double v0,double u1,double v1,double yaw,double pitch,double size,int color,double alpha) {
        out.add(new Quad(point(x,y,z,u0,v0,yaw,pitch,size),point(x,y,z,u1,v0,yaw,pitch,size),point(x,y,z,u1,v1,yaw,pitch,size),point(x,y,z,u0,v1,yaw,pitch,size),color,alpha,true));
    }
    private static Point point(double x,double y,double z,double u,double v,double yaw,double pitch,double size) {
        u*=size;v*=size;
        double depth=v*Math.sin(pitch);
        return new Point(x+u*Math.cos(yaw)-depth*Math.sin(yaw),y+v*Math.cos(pitch),z+u*Math.sin(yaw)+depth*Math.cos(yaw));
    }
    private static double mod(double n){return n-Math.floor(n);}
    private static double clamp(double n){return Double.isFinite(n)?Math.max(0,Math.min(1,n)):0;}
    private ScenicGoldenLeaves() {}
}

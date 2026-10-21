package com.dynasty.cod3;

import com.dynasty.cod3.ScenicAurora.Point;
import com.dynasty.cod3.ScenicAurora.Quad;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/** Rain-fed grass veins and seeded fireflies; no entities, block writes or global light. */
public final class ScenicFireflies {
    @FunctionalInterface public interface Ground { double height(double x,double z); }
    public static final int MAX_QUADS=480;
    private static final int[] ROOT_X={0,1,2,3,2,2,2,1,2,3,0,0};
    private static final int[] ROOT_Z={0,0,0,0,0,1,2,2,2,2,0,-1};
    public static double visibility(long dayTime,double rain,int moonPhase) {
        if(moonPhase!=0)return 0;
        long t=Math.floorMod(dayTime,24000);
        return clamp((t-13000)/1000.)*clamp((23000-t)/1000.)*clamp(rain);
    }
    public static List<Quad> mesh(long seed,double age,int duration,double distance,boolean low,double visibility,Ground ground) {
        double fade=ScenicAurora.envelope(age,duration,distance)*clamp(visibility);
        if(fade<=0)return List.of();
        boolean far=low||distance>=96,detail=!low&&distance<32;
        int count=far?24:detail?96:56;
        var out=new ArrayList<Quad>(MAX_QUADS);
        for(int i=0;i<count;i++) {
            var r=new Random(seed^(0x9e3779b97f4a7c15L*(i+1)));
            double initial=r.nextDouble(),period=280+r.nextInt(161),phase=initial*Math.PI*2;
            double cycle=mod(age/period+initial);
            double x=(r.nextDouble()-.5)*44+Math.sin(age/53.+phase)*.8;
            double z=(r.nextDouble()-.5)*36+Math.cos(age/71.+phase)*.7;
            double floor=ground.height(x,z);if(!Double.isFinite(floor))continue;
            double y=floor+.45+cycle*3.6+Math.sin(age/31.+phase)*.08;
            double lod=i>=56?clamp((32-distance)/8.):i>=24?clamp((96-distance)/16.):1;
            double blink=.38+.62*Math.pow(Math.sin(age/27.+phase),2);
            double alpha=.9*fade*lod*blink*clamp(cycle*12)*clamp((1-cycle)*10);
            if(alpha<=0)continue;
            double yaw=phase+Math.sin(age/59.+phase)*.65,half=far?.18:.10;
            upright(out,x,y,z,-half,-half,half,half,yaw,0xb8db70,alpha);
            upright(out,x,y,z,-half,-half,half,half,yaw+Math.PI/2,0x70b859,alpha);
            if(detail) {
                double wing=.04+.09*Math.abs(Math.sin(age*.46+phase));
                double wingAlpha=alpha*.65*clamp((32-distance)/8.);
                upright(out,x,y+.06,z,-.24,-wing,-.10,wing,yaw,0x517753,wingAlpha);
                upright(out,x,y+.06,z,.10,-wing,.24,wing,yaw,0x517753,wingAlpha);
            }
        }
        if(!far)for(int patch=0;patch<8;patch++) {
            var r=new Random(seed^(0x632be59bd9b4e019L*(patch+1)));
            int bx=r.nextInt(38)-19,bz=r.nextInt(30)-15,turn=r.nextBoolean()?1:-1;
            double phase=r.nextDouble()*Math.PI*2;
            for(int step=0;step<12;step++) {
                // A short branching, block-aligned root. Each tile stays inside its sampled block.
                double x=bx+ROOT_X[step]+.5,z=bz+ROOT_Z[step]*turn+.5;
                double y=ground.height(x,z);if(!Double.isFinite(y))continue;
                double alpha=fade*clamp((96-distance)/32.)*(.16+.20*Math.pow(Math.sin(age/55.+phase-step*.45),2));
                boolean alongX=step<4||step>=7&&step<=9;double hx=alongX?.48:.055,hz=alongX?.055:.48;
                out.add(new Quad(new Point(x-hx,y+.025,z-hz),new Point(x+hx,y+.025,z-hz),
                    new Point(x+hx,y+.025,z+hz),new Point(x-hx,y+.025,z+hz),0x70b859,alpha,false));
            }
        }
        return List.copyOf(out);
    }
    private static void upright(List<Quad> out,double x,double y,double z,double u0,double v0,double u1,double v1,double yaw,int color,double alpha) {
        out.add(new Quad(p(x,y,z,u0,v0,yaw),p(x,y,z,u1,v0,yaw),p(x,y,z,u1,v1,yaw),p(x,y,z,u0,v1,yaw),color,alpha,true));
    }
    private static Point p(double x,double y,double z,double u,double v,double yaw){return new Point(x+u*Math.cos(yaw),y+v,z+u*Math.sin(yaw));}
    private static double mod(double x){return x-Math.floor(x);}
    private static double clamp(double x){return Double.isFinite(x)?Math.max(0,Math.min(1,x)):0;}
    private ScenicFireflies(){}
}

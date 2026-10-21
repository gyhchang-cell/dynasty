package com.dynasty.cod3;

import com.dynasty.cod3.ScenicAurora.Point;
import com.dynasty.cod3.ScenicAurora.Quad;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/** A noon parhelic band and four original stepped ruyi clouds, in the vanilla sun's frame. */
public final class ScenicSunHalo {
    public static final int MAX_QUADS=80;
    private static final int IVORY=0xfff4d9,WHITE=0xf4f6eb,JADE=0xc8ddd2,GOLD=0xd9c294;

    public static double skyVisibility(long dayTime,double rain) {
        long day=Math.floorMod(dayTime,24000);
        return clamp((day-4500)/500.)*clamp((8000-day)/500.)*(1-clamp(rain));
    }
    /** The region is world anchored; apparent solar direction must not acquire observer parallax. */
    public static Point solar(Point p,double sunAngle) {
        double sin=Math.sin(sunAngle),cos=Math.cos(sunAngle);
        return new Point(-sin*p.y()+cos*p.z(),cos*p.y()+sin*p.z(),p.x());
    }
    public static Quad solar(Quad q,double sunAngle) {
        return new Quad(solar(q.a(),sunAngle),solar(q.b(),sunAngle),solar(q.c(),sunAngle),solar(q.d(),sunAngle),q.color(),q.alpha(),false);
    }
    /** Four hard color regions, no textured gradients, particles, copied artwork or per-vertex bloom. */
    public static List<Quad> mesh(long seed,double age,int duration,double distance,boolean low,double visibility) {
        double fade=ScenicAurora.envelope(age,duration,distance)*clamp(visibility);
        if(fade<=0)return List.of();
        var out=new ArrayList<Quad>(MAX_QUADS);
        // Single inexpensive LOD in the catalogue: every viewer retains the same angular silhouette.
        // An open stepped arc above and below the sun, rather than a smooth magical circle.
        for(int sign:new int[]{-1,1}) {
            double[][] steps={{-40,-32,24},{-32,-24,32},{-24,24,40},{24,32,32},{32,40,24}};
            for(var step:steps) {
                double z=sign*step[2];
                rect(out,step[0],z-1,step[1],z+1,160,IVORY,.38*fade);
                rect(out,step[0],z+sign*1,step[1],z+sign*2,160,GOLD,.17*fade);
            }
            for(int x:new int[]{-32,-24,24,32}) {
                double z=(Math.abs(x)==32?28:36)*sign;
                rect(out,x-1,z-4,x+1,z+4,160,IVORY,.38*fade);
            }
        }
        // Broad, almost horizontal white ribbon passes through the actual square sun.
        for(int i=-4;i<=4;i++) {
            double x=i*14,z=i*i*.45;
            rect(out,x-7,z-1.2,x+7,z+1.2,158,WHITE,(i==0?.18:.42)*fade);
            if(i<4) {
                double next=(i+1)*(i+1)*.45;
                rect(out,x+6.4,Math.min(z,next)-1.2,x+7.6,Math.max(z,next)+1.2,158,WHITE,.28*fade);
            }
        }
        Random rng=new Random(seed);
        for(int i=0;i<4;i++) {
            double phase=rng.nextDouble()*Math.PI*2;
            double x=(i%2==0?-1:1)*(44+i/2*7)+Math.sin(age/180.+phase)*2;
            double z=(i<2?-1:1)*26+Math.sin(age/220.+phase)*1.5;
            double y=148-i*.8;
            // Contiguous broad cloud body, a squared curled head and an open central notch.
            rect(out,x-16,z,x+14,z+3,y,WHITE,.42*fade);
            rect(out,x-12,z+3,x-4,z+8,y,WHITE,.42*fade);
            rect(out,x-8,z+8,x+2,z+11,y,WHITE,.42*fade);
            rect(out,x+2,z+3,x+6,z+11,y,WHITE,.42*fade);
            rect(out,x+6,z-3,x+22,z,y,WHITE,.42*fade);
            rect(out,x+16,z-6,x+26,z-3,y,WHITE,.42*fade);
            rect(out,x-16,z-1.5,x+6,z,y,JADE,.32*fade);
            rect(out,x-8,z+11,x+2,z+12,y,GOLD,.27*fade);
        }
        return List.copyOf(out);
    }
    private static void rect(List<Quad> out,double x0,double z0,double x1,double z1,double y,int color,double alpha) {
        out.add(new Quad(new Point(x0,y,z0),new Point(x1,y,z0),new Point(x1,y,z1),new Point(x0,y,z1),color,alpha,false));
    }
    private static double clamp(double n){return Double.isFinite(n)?Math.max(0,Math.min(1,n)):0;}
    private ScenicSunHalo() {}
}

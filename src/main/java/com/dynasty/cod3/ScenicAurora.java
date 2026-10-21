package com.dynasty.cod3;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/** Original, world-anchored northern curtains. Pure geometry, also used by offline visual QA. */
public final class ScenicAurora {
    public record Point(double x,double y,double z) {}
    public record Quad(Point a,Point b,Point c,Point d,int color,double alpha,boolean feather) {}
    public static final int MAX_QUADS=276;
    private static final int[] COLORS={0x83dbbe,0x369b9c,0x496a9d};

    /** Dawn/dusk and rain suppress the display without changing the world's sky/fog/light. */
    public static double skyVisibility(long dayTime,double rain) {
        long day=Math.floorMod(dayTime,24000);
        return clamp((day-13000)/1000.)*clamp((23000-day)/1000.)*(1-clamp(rain));
    }
    public static double envelope(double age,int duration,double distance) {
        if(duration<=0||!Double.isFinite(age)||!Double.isFinite(distance)||distance<0)return 0;
        return clamp(age/80)*clamp((duration-age)/80)*clamp((256-distance)/32);
    }
    /** Distances/coordinates are blocks; never scale an already world-sized sky by the packet's mob scale. */
    public static List<Quad> mesh(long seed,double age,int duration,double distance,boolean low,double visibility) {
        double fade=envelope(age,duration,distance)*clamp(visibility);
        if(fade<=0)return List.of();
        boolean far=low||distance>96;
        int sections=far?12:distance>32?16:24;
        int curtains=far?2:3,bands=far?2:3;
        List<Quad> out=new ArrayList<>(MAX_QUADS);
        Random random=new Random(seed);
        double phase=random.nextDouble()*Math.PI*2;
        // Absolute server age is the only clock. LOD/viewers never restart the travelling wave.
        double time=age/180.;
        for(int ribbon=0;ribbon<curtains;ribbon++) {
            double ribbonFade=ribbon==2?clamp((104-distance)/24):1;
            for(int section=0;section<sections;section++) {
                double u=section/(double)sections,v=(section+1.)/sections;
                double x0=-144+288*u,x1=-144+288*v;
                double z0=depth(u,ribbon,phase,time),z1=depth(v,ribbon,phase,time);
                // Broad, hard-edged color regions: no texture noise, bloom or per-vertex gradient.
                double[] left=edges(u,ribbon,phase,time,far),right=edges(v,ribbon,phase,time,far);
                double edgeFade=Math.min(1,Math.min(u+.025,1-v+.025)*10);
                for(int band=0;band<bands;band++) {
                    double opacity=(band==0?.46:band==1?.24:.10)*fade*ribbonFade*edgeFade;
                    if(opacity<=0)continue;
                    out.add(new Quad(new Point(x0,left[band],z0),new Point(x1,right[band],z1),
                        new Point(x1,right[band+1],z1),new Point(x0,left[band+1],z0),COLORS[band],opacity,false));
                }
            }
        }
        int feathers=far?0:distance>32?8:20;
        double featherFade=fade*clamp((96-distance)/24);
        for(int i=0;i<feathers;i++) {
            // Every feather has an immutable seed trajectory. Fewer feathers are a prefix of the same set.
            Random feather=new Random(seed^(0x9e3779b97f4a7c15L*(i+1)));
            double initial=feather.nextDouble(),cycle=positiveMod(age/480.+initial,1);
            double alpha=.65*featherFade*clamp(cycle*8)*clamp((1-cycle)*8);
            double x=(feather.nextDouble()-.5)*240+Math.sin(time*.7+i)*5;
            double y=68-cycle*42+feather.nextDouble()*12;
            double z=(feather.nextDouble()-.5)*100;
            double tilt=Math.sin(time+i*.8)*.55;
            // Three connected coarse tiles give a stepped feather with a readable shaft direction.
            for(int tile=0;tile<3;tile++) {
                double half=tile==1?1.35:.65,lo=tile*1.5;
                out.add(new Quad(featherPoint(x,y,z,-half,lo,tilt),featherPoint(x,y,z,half,lo,tilt),
                    featherPoint(x,y,z,half,lo+1.5,tilt),featherPoint(x,y,z,-half,lo+1.5,tilt),
                    tile==1?0xc4ecda:0x83dbbe,alpha,true));
            }
        }
        return List.copyOf(out);
    }
    private static double depth(double u,int ribbon,double phase,double time) {
        return -46+ribbon*44+Math.sin(u*7.2+phase+time*.35+ribbon)*26;
    }
    private static double[] edges(double u,int ribbon,double phase,double time,boolean far) {
        double base=78+ribbon*18+Math.sin(u*6.2+phase+time+ribbon)*10;
        double height=18+6*Math.sin(u*12-phase-time*.7+ribbon);
        return far?new double[]{base,base+6,base+height+12}:new double[]{base,base+6,base+height,base+height+12};
    }
    private static Point featherPoint(double x,double y,double z,double dx,double dy,double tilt) {
        return new Point(x+dx*Math.cos(tilt)-dy*Math.sin(tilt),y+dx*Math.sin(tilt)+dy*Math.cos(tilt),z+dy*.2);
    }
    private static double positiveMod(double a,double b){return a-Math.floor(a/b)*b;}
    private static double clamp(double n){return Double.isFinite(n)?Math.max(0,Math.min(1,n)):0;}
    private ScenicAurora() {}
}

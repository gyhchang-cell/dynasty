package com.dynasty.cod3;

import com.dynasty.cod3.ScenicAurora.Point;
import com.dynasty.cod3.ScenicAurora.Quad;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/** Original silent shooting stars: short seeded flights, never projectiles, loot or impact damage. */
public final class ScenicMeteors {
    public static final int MAX_QUADS=180;
    public static List<Quad> mesh(long seed,double age,int duration,double distance,boolean low,double visibility) {
        double fade=ScenicAurora.envelope(age,duration,distance)*Math.max(0,Math.min(1,visibility));
        if(!Double.isFinite(fade)||fade<=0)return List.of();
        int lanes=low||distance>96?8:distance>32?14:20;
        var out=new ArrayList<Quad>(MAX_QUADS);
        for(int lane=0;lane<lanes;lane++) {
            // Each lane owns its sequence. LOD only removes lanes; it never changes surviving paths.
            var random=new Random(seed^(0x632be59bd9b4e019L*(lane+1)));
            double period=lane<2?64:112+random.nextInt(56);
            double offset=lane<2?lane*32:random.nextDouble()*period;
            double flight=lane<2?64:32+random.nextInt(16);
            long cycle=(long)Math.floor((age+offset)/period);
            double tick=age+offset-cycle*period;if(tick>=flight)continue;
            // New flight, new position; fade reaches zero before a star is repositioned.
            var path=new Random(seed^((lane+1)*0x9e3779b97f4a7c15L)^cycle*0x5deece66dL);
            double u=tick/flight;
            double lodFade=lane>=14?clamp((32-distance)/8):lane>=8?clamp((96-distance)/24):1;
            double alpha=fade*lodFade*clamp(tick/7)*clamp((flight-tick)/9);
            if(alpha<=0)continue;
            double x=(path.nextDouble()-.5)*(lane<2?12:210)+(lane<2?(lane==0?-20:20):0)+(0.5-u)*96;
            double y=126+(path.nextDouble()-.5)*(lane<2?12:28)-u*48;
            double z=(path.nextDouble()-.5)*(lane<2?12:100)+u*22;
            // Two crossed planes keep the trail readable from either side without following the camera.
            for(int segment=0;segment<3;segment++) {
                double start=segment/3.,end=(segment+1.)/3.;
                double width=segment==0?.85:segment==1?.48:.2;
                double length=32*clamp(tick/10);
                Point a=new Point(x+start*length,y+start*length*.5,z-start*length*.23);
                Point b=new Point(x+end*length,y+end*length*.5,z-end*length*.23);
                int color=segment==0?0xe5cf9a:segment==1?0x9cb9c4:0x657e9c;
                double opacity=alpha*(segment==0?.75:segment==1?.45:.2);
                out.add(new Quad(shift(a,0,-width,0),shift(b,0,-width*.5,0),shift(b,0,width*.5,0),shift(a,0,width,0),color,opacity,false));
                out.add(new Quad(shift(a,0,0,-width),shift(b,0,0,-width*.5),shift(b,0,0,width*.5),shift(a,0,0,width),color,opacity,false));
            }
            // Three coarse squares, no lens-flare sphere or smooth billboard sprite.
            double s=1.1;int color=0xffe9bc;
            out.add(new Quad(new Point(x-s,y-s,z),new Point(x+s,y-s,z),new Point(x+s,y+s,z),new Point(x-s,y+s,z),color,alpha*.92,false));
            out.add(new Quad(new Point(x-s,y,z-s),new Point(x+s,y,z-s),new Point(x+s,y,z+s),new Point(x-s,y,z+s),color,alpha*.92,false));
            out.add(new Quad(new Point(x,y-s,z-s),new Point(x,y+s,z-s),new Point(x,y+s,z+s),new Point(x,y-s,z+s),color,alpha*.92,false));
        }
        return List.copyOf(out);
    }
    private static Point shift(Point p,double x,double y,double z){return new Point(p.x()+x,p.y()+y,p.z()+z);}
    private static double clamp(double x){return Math.max(0,Math.min(1,x));}
    private ScenicMeteors() {}
}

package com.dynasty.cod3;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import static com.dynasty.cod3.ScenicAurora.*;

/** Three stepped celestial water curtains. No fluid blocks, entities, world writes or camera tracking. */
public final class ScenicSilverfall {
    public static final int MAX_QUADS=288;
    private static final int DEEP=0x315b78,WATER=0x5792a7,FLOW=0x9ad3db,FOAM=0xe0eee8;
    public static double visibility(double rain){return 1-clamp(rain);}
    public static double soundVolume(double age,int duration,double distance,double rain){
        return .35*envelope(age,duration,distance)*clamp((48-distance)/24)*visibility(rain);
    }
    /** A shared absolute-age clock moves all highlights upward; every distance keeps the same main silhouette. */
    public static List<Quad> mesh(long seed,double age,int duration,double distance,boolean low,double visibility){
        double fade=envelope(age,duration,distance)*clamp(visibility);if(fade<=0)return List.of();
        var out=new ArrayList<Quad>(MAX_QUADS);
        for(int stream=0;stream<3;stream++){
            double height=height(stream),bottom=2,step=height/10;
            // Coarse axis-aligned steps keep a cuboid silhouette, including both side views.
            for(int band=0;band<10;band++){
                double y=bottom+band*step,w=width(stream,band),x=centerX(stream,band),z=centerZ(stream);
                box(out,x-w/2,y,z-1.2,x+w/2,y+step,z+1.2,fade*.27);
                if(band==0)horizontal(out,x-w/2,x+w/2,y,z,DEEP,fade*.135);
                if(band==9)horizontal(out,x-w/2,x+w/2,y+step,z,WATER,fade*.135);
                if(band>0){
                    double oldX=centerX(stream,band-1),oldW=width(stream,band-1);
                    horizontal(out,oldX-oldW/2,x-w/2,y,z,WATER,fade*.135);
                    horizontal(out,oldX+oldW/2,x+w/2,y,z,WATER,fade*.135);
                }
            }
            Random r=new Random(seed^(0x9e3779b97f4a7c15L*(stream+1)));
            for(int lane=0;lane<3;lane++){
                double initial=r.nextDouble(),speed=.11+r.nextDouble()*.035;
                for(int pulse=0;pulse<3;pulse++){
                    double cycle=mod(age*speed/height+initial+pulse/3.,1),y=bottom+cycle*height;
                    double end=Math.min(bottom+height,y+3+r.nextDouble()*3),half=.24+r.nextDouble()*.20;
                    int band=Math.min(9,(int)((y-bottom)/step));
                    double x=centerX(stream,band)+(lane-1)*width(stream,band)*.27;
                    double alpha=fade*.78*clamp(cycle*12)*clamp((1-cycle)*12);
                    for(int side:new int[]{-1,1})rect(out,x-half,y,x+half,end,centerZ(stream)+side*1.23,lane==1?FOAM:FLOW,alpha,true);
                }
            }
            // Side-facing observers must see reverse motion too, not a static glass strip.
            for(int pulse=0;pulse<3;pulse++){
                double cycle=mod(age*.13/height+stream*.173+pulse/3.,1),y=bottom+cycle*height;
                int band=Math.min(9,(int)((y-bottom)/step));
                double end=Math.min(bottom+height,y+5),z=centerZ(stream),a=fade*.63*clamp(cycle*12)*clamp((1-cycle)*12);
                for(int side:new int[]{-1,1}){
                    double x=centerX(stream,band)+side*(width(stream,band)/2+.03);
                    out.add(new Quad(new Point(x,y,z-.38),new Point(x,y,z+.38),new Point(x,end,z+.38),new Point(x,end,z-.38),FLOW,a,true));
                }
            }
            // A fragmented, rectangular intake suggests water lifting from a small mist shelf.
            for(int tile=0;tile<6;tile++){
                double x=centerX(stream,0)+(tile%3-1)*2.1,z=centerZ(stream)+(tile/3==0?-2.5:2.5);
                double a=fade*(.12+.05*Math.sin(age/35.+tile+stream));
                out.add(new Quad(new Point(x-1,1.2,z-.55),new Point(x+1,1.2,z-.55),new Point(x+1,1.2,z+.55),new Point(x-1,1.2,z+.55),FLOW,a,false));
            }
        }
        if(!low)for(int i=0;i<18;i++){
            Random r=new Random(seed^(0x632be59bd9b4e019L*(i+1)));int stream=i%3;
            double cycle=mod(age/(180+r.nextInt(120))+r.nextDouble(),1);
            double x=centerX(stream,0)+(r.nextDouble()-.5)*11,z=centerZ(stream)+(r.nextDouble()-.5)*8;
            double y=1+cycle*8,half=.20+r.nextDouble()*.35;
            double a=.32*fade*clamp(cycle*8)*clamp((1-cycle)*8);
            rect(out,x-half,y,x+half,y+half*2,z,FLOW,a,true);
            out.add(new Quad(new Point(x,y,z-half),new Point(x,y,z+half),new Point(x,y+half*2,z+half),new Point(x,y+half*2,z-half),FLOW,a,true));
        }
        return List.copyOf(out);
    }
    private static double height(int s){return s==0?48:s==1?34:39;}
    private static double centerX(int s,int band){return (s==0?0:s==1?-11:11)+(s==0?1:s==1?-1:1)*(band/3)*.5;}
    private static double centerZ(int s){return s==0?0:s==1?4:-3;}
    private static double width(int s,int band){return (s==0?6.5:4.5)+(band>=8?(band-7)*1.5:band<=1?1:0);}
    private static void rect(List<Quad> out,double x0,double y0,double x1,double y1,double z,int c,double a,boolean moving){
        out.add(new Quad(new Point(x0,y0,z),new Point(x1,y0,z),new Point(x1,y1,z),new Point(x0,y1,z),c,a,moving));
    }
    private static void box(List<Quad> out,double x0,double y0,double z0,double x1,double y1,double z1,double a){
        rect(out,x0,y0,x1,y1,z0,WATER,a,false);rect(out,x0,y0,x1,y1,z1,WATER,a,false);
        out.add(new Quad(new Point(x0,y0,z0),new Point(x0,y0,z1),new Point(x0,y1,z1),new Point(x0,y1,z0),DEEP,a,false));
        out.add(new Quad(new Point(x1,y0,z0),new Point(x1,y0,z1),new Point(x1,y1,z1),new Point(x1,y1,z0),DEEP,a,false));

    }
    private static void horizontal(List<Quad> out,double x0,double x1,double y,double z,int color,double alpha){
        if(Math.abs(x1-x0)<1e-9)return;
        out.add(new Quad(new Point(x0,y,z-1.2),new Point(x1,y,z-1.2),new Point(x1,y,z+1.2),new Point(x0,y,z+1.2),color,alpha,false));
    }
    private static double mod(double x,double n){return x-Math.floor(x/n)*n;}
    private static double clamp(double n){return Double.isFinite(n)?Math.max(0,Math.min(1,n)):0;}
    private ScenicSilverfall(){}
}

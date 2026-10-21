package com.dynasty.cod3;

import java.util.ArrayList;
import java.util.List;
import static com.dynasty.cod3.ScenicAurora.*;

/** Eight fixed trigram stations; a non-combat, world-space midnight apparition. */
public final class ScenicAncientArray {
    @FunctionalInterface public interface Ground {double height(double x,double z);}
    public static final int MAX_QUADS=132;
    private static final int JADE=0x648c79,CORE=0xb8d6ad,GOLD=0xbca66a,SEAL=0xe2d4a0;
    public static double visibility(long dayTime,double rain){
        long t=Math.floorMod(dayTime,24000);return clamp((t-17000)/200.)*clamp((19000-t)/200.)*(1-clamp(rain));
    }
    public static double soundVolume(double age,int duration,double distance,long dayTime,double rain){
        return .20*envelope(age,duration,distance)*clamp((48-distance)/24)*visibility(dayTime,rain);
    }
    public static List<Quad> mesh(long seed,double age,int duration,double distance,boolean low,double visibility,Ground ground){
        double fade=envelope(age,duration,distance)*clamp(visibility);if(fade<=0)return List.of();
        var flat=new ArrayList<Quad>(MAX_QUADS);double detail=low?0:clamp((96-distance)/24);
        double phase=new java.util.Random(seed).nextDouble()*Math.PI*2;
        for(int station=0;station<8;station++){
            double a=station*Math.PI/4,x=Math.sin(a)*17,z=Math.cos(a)*17;
            double height=station%2==0?20:16,pulse=.75+.25*Math.sin(age/75.+phase-station*Math.PI/4);
            vertical(flat,x,z,.6,height,JADE,fade*.20);vertical(flat,x,z,.24,height,CORE,fade*.62*pulse);
            // Two short cap planes remain narrow from every angle, never a surrounding wall.
            verticalAt(flat,x,z,.85,height,height+.24,GOLD,fade*.5*pulse);
            if(detail<=0)continue;
            double b=(station+1)*Math.PI/4;
            line(flat,x,z,Math.sin(b)*17,Math.cos(b)*17,.12,.055,GOLD,fade*.48*detail);
            line(flat,Math.sin(a)*12.5,Math.cos(a)*12.5,Math.sin(b)*12.5,Math.cos(b)*12.5,.10,.065,JADE,fade*.64*detail);
            line(flat,Math.sin(a)*13,Math.cos(a)*13,Math.sin(a)*16,Math.cos(a)*16,.12,.075,GOLD,fade*.46*detail);
            // Public-domain trigram construction: three whole/broken lines, not copied mod glyphs.
            for(int row=0;row<3;row++){
                double radial=14.4+row*.55;
                if((station&(1<<row))!=0)glyph(flat,a,radial,-1.2,1.2,SEAL,fade*.7*detail);
                else {glyph(flat,a,radial,-1.2,-.25,SEAL,fade*.7*detail);glyph(flat,a,radial,.25,1.2,SEAL,fade*.7*detail);}
            }
            glyph(flat,a,13.9,-1.5,1.5,GOLD,fade*.42*detail);glyph(flat,a,16.05,-1.5,1.5,GOLD,fade*.42*detail);
        }
        if(detail>0){
            for(int sign:new int[]{-1,1}){
                line(flat,sign*1.4,-3,sign*1.4,3,.22,.085,SEAL,fade*.6*detail);
                line(flat,-3,sign*1.4,3,sign*1.4,.22,.085,SEAL,fade*.6*detail);
                line(flat,sign*3.5,-3.5,sign*3.5,3.5,.12,.075,GOLD,fade*.4*detail);
                line(flat,-3.5,sign*3.5,3.5,sign*3.5,.12,.075,GOLD,fade*.4*detail);
            }
        }
        var out=new ArrayList<Quad>(flat.size());
        for(var q:flat){
            var corners=new Point[]{q.a(),q.b(),q.c(),q.d()};Point[] at=new Point[4];double min=Double.POSITIVE_INFINITY,max=Double.NEGATIVE_INFINITY;
            for(int i=0;i<4;i++){double y=ground.height(corners[i].x(),corners[i].z());min=Math.min(min,y);max=Math.max(max,y);at[i]=new Point(corners[i].x(),corners[i].y()+y,corners[i].z());}
            if(!Double.isFinite(min+max)||max-min>4)continue;
            out.add(new Quad(at[0],at[1],at[2],at[3],q.color(),q.alpha(),q.feather()));
        }
        return List.copyOf(out);
    }
    private static void glyph(List<Quad> out,double a,double radius,double from,double to,int color,double alpha){
        double x=Math.sin(a)*radius,z=Math.cos(a)*radius;
        line(out,x+Math.cos(a)*from,z-Math.sin(a)*from,x+Math.cos(a)*to,z-Math.sin(a)*to,.18,.09,color,alpha);
    }
    private static void vertical(List<Quad> out,double x,double z,double half,double height,int color,double alpha){verticalAt(out,x,z,half,.12,height,color,alpha);}
    private static void verticalAt(List<Quad> out,double x,double z,double half,double bottom,double top,int color,double alpha){
        out.add(new Quad(new Point(x-half,bottom,z),new Point(x+half,bottom,z),new Point(x+half,top,z),new Point(x-half,top,z),color,alpha,true));
        out.add(new Quad(new Point(x,bottom,z-half),new Point(x,bottom,z+half),new Point(x,top,z+half),new Point(x,top,z-half),color,alpha,true));
    }
    private static void line(List<Quad> out,double x0,double z0,double x1,double z1,double width,double y,int color,double alpha){
        double len=Math.hypot(x1-x0,z1-z0),dx=(z1-z0)/len*width/2,dz=-(x1-x0)/len*width/2;
        out.add(new Quad(new Point(x0-dx,y,z0-dz),new Point(x1-dx,y,z1-dz),new Point(x1+dx,y,z1+dz),new Point(x0+dx,y,z0+dz),color,alpha,false));
    }
    private static double clamp(double n){return Double.isFinite(n)?Math.max(0,Math.min(1,n)):0;}
    private ScenicAncientArray(){}
}

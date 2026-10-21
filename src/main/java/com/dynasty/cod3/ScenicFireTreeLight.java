package com.dynasty.cod3;

import java.util.*;

/** Original coarse sparks; pure world-time geometry, not server particles/entities. */
public final class ScenicFireTreeLight {
    public static double visibility(long dayTime,double rain){
        long t=Math.floorMod(dayTime,24000);if(rain>.01||t<13000||t>=23000)return 0;
        return Math.min(1,Math.min((t-13000)/60.,(23000-t)/60.));
    }
    public static double soundVolume(double distance,double visibility){return .07*Math.max(0,Math.min(1,(48-distance)/24))*visibility;}
    public static List<ScenicAurora.Quad> mesh(long seed,double worldTime,double distance,boolean low,double visibility,List<ScenicAurora.Point> buds){
        double fade=Math.max(0,Math.min(1,(160-distance)/48))*visibility;
        if(fade<=0||buds.isEmpty())return List.of();
        int count=low?16:distance>80?8:80;
        var out=new ArrayList<ScenicAurora.Quad>(count*2);
        for(int i=0;i<count;i++){
            var random=new Random(seed^(0x9e3779b97f4a7c15L*(i+1)));var bud=buds.get(i%buds.size());
            double cycle=worldTime/100.+random.nextDouble();cycle-=Math.floor(cycle);
            double angle=random.nextDouble()*Math.PI*2,drift=.4+random.nextDouble()*.7;
            double x=bud.x()+.5+Math.cos(angle)*cycle*drift,z=bud.z()+.5+Math.sin(angle)*cycle*drift,y=bud.y()+.5+cycle*(2.5+random.nextDouble()*2);
            double width=i%5==0?.075:.045,height=width*2;
            double alpha=fade*.8*Math.min(1,cycle*8)*Math.min(1,(1-cycle)*6);
            int color=i%4==0?0xe8e1bd:i%3==0?0xe8a55d:0xcbbd8b;
            out.add(new ScenicAurora.Quad(new ScenicAurora.Point(x-width,y,z),new ScenicAurora.Point(x+width,y,z),new ScenicAurora.Point(x+width,y+height,z),new ScenicAurora.Point(x-width,y+height,z),color,alpha,true));
            out.add(new ScenicAurora.Quad(new ScenicAurora.Point(x,y,z-width),new ScenicAurora.Point(x,y,z+width),new ScenicAurora.Point(x,y+height,z+width),new ScenicAurora.Point(x,y+height,z-width),color,alpha,true));
        }
        return List.copyOf(out);
    }
    private ScenicFireTreeLight(){}
}

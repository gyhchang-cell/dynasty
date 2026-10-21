import com.dynasty.cod3.*;
import java.nio.file.*;
import java.util.*;

/** Numerical solar alignment and full lifetime sampling of the actual production mesh. */
public class SunHaloGeometryQa {
    static int frames;static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception {
        Path out=Path.of(args[0]);Files.createDirectories(out);
        for(int t:new int[]{0,4500,8000,18000,24000})check(ScenicSunHalo.skyVisibility(t,0)==0,"outside noon");
        for(int t:new int[]{5500,6000,7100})check(ScenicSunHalo.skyVisibility(t,0)==1,"trigger and full 30s lifetime visible");
        check(ScenicSunHalo.skyVisibility(6000,1)==0,"rain suppresses");
        check(ScenicSunHalo.skyVisibility(4750,.5)==.25,"continuous time/weather fade");
        for(int t:new int[]{-1,0,600,601})check(ScenicSunHalo.mesh(21,t,600,24,false,1).isEmpty(),"lifetime");
        check(ScenicSunHalo.mesh(21,300,600,256,false,1).isEmpty(),"regional boundary");
        for(long seed:new long[]{0,21,1518,-123,Long.MAX_VALUE})for(int t=0;t<=600;t+=10)for(int dist:new int[]{0,24,64,128,248}) {
            var m=ScenicSunHalo.mesh(seed,t,600,dist,false,1);frames++;
            check(m.size()<=ScenicSunHalo.MAX_QUADS,"catalogue budget");
            check(m.equals(ScenicSunHalo.mesh(seed,t,600,dist,false,1)),"same seed/clock");
            check(m.equals(ScenicSunHalo.mesh(seed,t,600,dist,true,1)),"catalogue single LOD, minimal no shape loss");
            for(var q:m) {
                check(q.alpha()>=0&&q.alpha()<=.42,"restrained opacity");
                for(var p:List.of(q.a(),q.b(),q.c(),q.d()))check(Double.isFinite(p.x()+p.y()+p.z())&&Math.abs(p.x())<80&&p.y()>=145&&p.y()<=160&&Math.abs(p.z())<45,"bounded sky geometry");
            }
        }
        for(double angle:new double[]{-.3,0,.3,Math.PI}) {
            var p=ScenicSunHalo.solar(new ScenicAurora.Point(0,160,0),angle);
            check(Math.abs(p.x()+160*Math.sin(angle))<1e-9&&Math.abs(p.y()-160*Math.cos(angle))<1e-9&&p.z()==0,"vanilla Y(-90) X(sunAngle) alignment");
            var q=ScenicSunHalo.solar(new ScenicAurora.Point(17,152,31),angle);
            check(Math.abs(q.x()*q.x()+q.y()*q.y()+q.z()*q.z()-(17*17+152*152+31*31))<1e-8,"orthogonal projection preserves size");
        }
        var first=ScenicSunHalo.mesh(1518,300,600,24,false,1);
        check(!first.equals(ScenicSunHalo.mesh(1518,320,600,24,false,1)),"clouds drift");
        check(!first.equals(ScenicSunHalo.mesh(21,300,600,24,false,1)),"seeded cloud phases");
        for(int t=0;t<=600;t+=20)Files.writeString(out.resolve("frame-"+t+".json"),AuroraGeometryQa.encode(ScenicSunHalo.mesh(1518,t,600,24,false,1)));
        Files.writeString(out.resolve("validation.json"),"{\"sampledFrames\":"+frames+",\"quads\":"+first.size()+",\"maximumQuads\":80,\"solarAlignment\":true,\"productionGeometry\":true,\"nativeClient\":false}");
        System.out.println("PASS "+frames+" solar frames, sun alignment, single LOD and lifetime/weather/region fades");
    }
}

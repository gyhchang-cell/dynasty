import com.dynasty.cod3.*;
import java.nio.file.*;
import java.util.*;
public class MeteorGeometryQa {
    static int frames;static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception{
        Path out=Path.of(args[0]);Files.createDirectories(out);
        for(long seed:new long[]{0,15,1518,-123,Long.MAX_VALUE})for(int t=0;t<=900;t+=10)for(int dist:new int[]{0,24,64,128,248}){
            var m=ScenicMeteors.mesh(seed,t,900,dist,false,1);frames++;
            check(m.size()<=ScenicMeteors.MAX_QUADS,"bounded quads");check(m.equals(ScenicMeteors.mesh(seed,t,900,dist,false,1)),"determinism");
            for(var q:m){check(q.alpha()>=0&&q.alpha()<=.92,"bounded opacity");for(var p:List.of(q.a(),q.b(),q.c(),q.d()))check(Double.isFinite(p.x()+p.y()+p.z())&&Math.abs(p.x())<190&&p.y()>60&&p.y()<180&&Math.abs(p.z())<80,"finite sky flight envelope");}
        }
        for(int t:new int[]{-1,0,900,901})check(ScenicMeteors.mesh(15,t,900,24,false,1).isEmpty(),"inactive lifetime");
        check(ScenicMeteors.mesh(15,400,900,256,false,1).isEmpty(),"region fade");
        check(ScenicMeteors.mesh(15,400,900,24,false,ScenicAurora.skyVisibility(6000,0)).isEmpty(),"day suppressed");
        check(ScenicMeteors.mesh(15,400,900,24,false,ScenicAurora.skyVisibility(18000,1)).isEmpty(),"rain suppressed");
        // Surviving lanes have identical positions at every distance and MINIMAL mode.
        for(int t=100;t<800;t+=7){var n=ScenicMeteors.mesh(1518,t,900,24,false,1);var f=ScenicMeteors.mesh(1518,t,900,128,false,1);check(n.containsAll(f),"far LOD path identity");check(f.equals(ScenicMeteors.mesh(1518,t,900,24,true,1)),"minimal shares the far path");}
        for(int t=0;t<=900;t+=30)Files.writeString(out.resolve("frame-"+t+".json"),AuroraGeometryQa.encode(ScenicMeteors.mesh(1518,t,900,24,false,1)));
        for(int d:new int[]{24,64,128})Files.writeString(out.resolve("lod-"+d+".json"),AuroraGeometryQa.encode(ScenicMeteors.mesh(1518,450,900,d,false,1)));
        Files.writeString(out.resolve("validation.json"),"{\"sampledFrames\":"+frames+",\"maximumQuads\":180,\"productionGeometry\":true,\"nativeClient\":false}");
        System.out.println("PASS "+frames+" meteor frames, actual sky visibility and surviving LOD trajectories");
    }
}

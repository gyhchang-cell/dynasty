import com.dynasty.cod3.*;
import java.nio.file.*;
import java.util.*;
public class AncientArrayGeometryQa {
    static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception{
        Path out=Path.of(args[0]);Files.createDirectories(out);int frames=0;
        for(long seed:new long[]{0,2,1518,-1,Long.MAX_VALUE})for(int age=0;age<=1200;age+=10)for(int dist:new int[]{0,24,64,128,248}){
            var mesh=ScenicAncientArray.mesh(seed,age,1200,dist,false,1,(x,z)->0);frames++;
            check(mesh.size()<=132,"150 total budget");check(mesh.equals(ScenicAncientArray.mesh(seed,age,1200,dist,false,1,(x,z)->0)),"same world clock and seed");
            for(var q:mesh){check(q.alpha()>=0&&q.alpha()<=.7,"alpha");for(var p:List.of(q.a(),q.b(),q.c(),q.d()))check(Double.isFinite(p.x()+p.y()+p.z())&&Math.abs(p.x())<18&&Math.abs(p.z())<18&&p.y()>0&&p.y()<21,"finite bounds");}
        }
        for(long day:new long[]{0,6000,17000,19000,23000})check(ScenicAncientArray.visibility(day,0)==0,"midnight window");
        check(ScenicAncientArray.visibility(18000,0)==1&&ScenicAncientArray.visibility(18000,1)==0,"clear midnight only");
        for(int age:new int[]{-1,0,1200,1201})check(ScenicAncientArray.mesh(2,age,1200,24,false,1,(x,z)->0).isEmpty(),"lifetime");
        check(ScenicAncientArray.mesh(2,600,1200,256,false,1,(x,z)->0).isEmpty(),"region");
        check(ScenicAncientArray.mesh(2,600,1200,24,false,1,(x,z)->Double.NaN).isEmpty(),"unsupported ground");
        var near=ScenicAncientArray.mesh(2,600,1200,24,false,1,(x,z)->0);var far=ScenicAncientArray.mesh(2,600,1200,128,false,1,(x,z)->0);
        check(near.size()==132&&far.size()==48&&near.containsAll(far),"eight immutable stations and far silhouette");
        check(far.equals(ScenicAncientArray.mesh(2,600,1200,24,true,1,(x,z)->0)),"MINIMAL silhouette");
        var high=ScenicAncientArray.mesh(2,600,1200,24,false,1,(x,z)->11);
        for(int i=0;i<near.size();i++)check(Math.abs(high.get(i).a().y()-near.get(i).a().y()-11)<1e-8,"terrain conformity");
        check(ScenicAncientArray.mesh(2,600,1200,24,false,1,(x,z)->x<0?0:20).size()<near.size(),"cliff-spanning quads skipped");
        check(ScenicAncientArray.soundVolume(600,1200,24,18000,0)>0&&ScenicAncientArray.soundVolume(600,1200,48,18000,0)==0&&ScenicAncientArray.soundVolume(600,1200,24,6000,0)==0&&ScenicAncientArray.soundVolume(600,1200,24,18000,1)==0,"local chant range/weather/time");
        for(int age=0;age<=1200;age+=40)Files.writeString(out.resolve("frame-"+age+".json"),AuroraGeometryQa.encode(ScenicAncientArray.mesh(1518,age,1200,24,false,1,(x,z)->0)));
        Files.writeString(out.resolve("validation.json"),"{\"sampledFrames\":"+frames+",\"nearQuads\":132,\"farQuads\":48,\"productionGeometry\":true,\"nativeClient\":false}");System.out.println("PASS "+frames+" ancient array frames; terrain, midnight/rain, LOD, bounded chant");
    }
}

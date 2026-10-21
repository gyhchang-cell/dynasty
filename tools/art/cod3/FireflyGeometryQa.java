import com.dynasty.cod3.*;
import java.nio.file.*;
import java.util.*;
public class FireflyGeometryQa {
    static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
    public static void main(String[] args)throws Exception{
        Path out=Path.of(args[0]);Files.createDirectories(out);int frames=0;
        for(long seed:new long[]{0,7,1518,-1,Long.MAX_VALUE})for(int age=0;age<=1800;age+=10)for(int dist:new int[]{0,24,64,128,248}){
            var mesh=ScenicFireflies.mesh(seed,age,1800,dist,false,1,(x,z)->0);frames++;
            check(mesh.size()<=480,"budget");check(mesh.equals(ScenicFireflies.mesh(seed,age,1800,dist,false,1,(x,z)->0)),"same server clock and seed");
            for(var q:mesh){check(q.alpha()>=0&&q.alpha()<=.9,"alpha");for(var p:List.of(q.a(),q.b(),q.c(),q.d()))check(Double.isFinite(p.x()+p.y()+p.z())&&Math.abs(p.x())<28&&Math.abs(p.z())<22&&p.y()>0&&p.y()<4.4,"finite world bounds above terrain");}
        }
        for(int moon=1;moon<8;moon++)check(ScenicFireflies.visibility(18000,1,moon)==0,"full moon only");
        for(long day:new long[]{0,6000,13000,23000})check(ScenicFireflies.visibility(day,1,0)==0,"night window");
        check(ScenicFireflies.visibility(18000,0,0)==0&&ScenicFireflies.visibility(18000,1,0)==1,"rain required, unlike clear-weather leaves");
        for(int age:new int[]{-1,0,1800,1801})check(ScenicFireflies.mesh(7,age,1800,24,false,1,(x,z)->0).isEmpty(),"lifetime");
        check(ScenicFireflies.mesh(7,600,1800,256,false,1,(x,z)->0).isEmpty(),"outside region");
        check(ScenicFireflies.mesh(7,600,1800,24,false,1,(x,z)->Double.NaN).isEmpty(),"unloaded or unsuitable soil");
        var near=ScenicFireflies.mesh(7,600,1800,24,false,1,(x,z)->0);var mid=ScenicFireflies.mesh(7,600,1800,64,false,1,(x,z)->0);var far=ScenicFireflies.mesh(7,600,1800,128,false,1,(x,z)->0);
        check(near.size()==480&&mid.size()==208&&far.size()==48,"96/56/24 insects plus 96 near/mid ground tiles");
        check(near.containsAll(mid),"shared LOD geometry retains trajectories");
        var roots=near.stream().filter(q->!q.feather()).toList();
        for(int patch=0;patch<8;patch++){
            var tiles=roots.subList(patch*12,patch*12+12);var reached=new HashSet<Integer>();reached.add(0);
            boolean changed=true;while(changed){changed=false;for(int i=0;i<12;i++)if(!reached.contains(i))for(int j:new ArrayList<>(reached)){
                var a=tiles.get(i);var b=tiles.get(j);
                boolean joins=a.a().x()<=b.c().x()+.06&&b.a().x()<=a.c().x()+.06&&a.a().z()<=b.c().z()+.06&&b.a().z()<=a.c().z()+.06;
                if(joins){reached.add(i);changed=true;break;}
            }}
            check(reached.size()==12,"each flat-ground vein is connected, allowing its narrow pixel seams");
        }
        check(far.equals(ScenicFireflies.mesh(7,600,1800,24,true,1,(x,z)->0)),"MINIMAL equals far representation");
        check(!near.equals(ScenicFireflies.mesh(7,605,1800,24,false,1,(x,z)->0)),"actual drift/flap/pulse");
        var high=ScenicFireflies.mesh(7,600,1800,24,false,1,(x,z)->9);
        for(int i=0;i<near.size();i++)check(Math.abs(high.get(i).a().y()-near.get(i).a().y()-9)<1e-8,"actual terrain elevation");
        for(int age=0;age<=1800;age+=60)Files.writeString(out.resolve("frame-"+age+".json"),AuroraGeometryQa.encode(ScenicFireflies.mesh(7,age,1800,24,false,1,(x,z)->0)));
        Files.writeString(out.resolve("validation.json"),"{\"sampledFrames\":"+frames+",\"nearQuads\":480,\"midQuads\":208,\"farQuads\":48,\"productionGeometry\":true,\"nativeClient\":false}");System.out.println("PASS "+frames+" firefly frames; terrain, rain/full-moon/night, lifetime and LOD");
    }
}

import com.dynasty.cod3.*;
import java.nio.file.*;
import java.util.*;
public class GoldenLeafGeometryQa {
    static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
    static final ScenicGoldenLeaves.Surface GROVE=(x,z)->new ScenicGoldenLeaves.Column(0,12);
    public static void main(String[] args)throws Exception {
        Path out=Path.of(args[0]);Files.createDirectories(out);int frames=0;
        for(long seed:new long[]{0,19,1518,-1,Long.MAX_VALUE})for(int age=0;age<=1200;age+=10)for(int dist:new int[]{0,24,64,128,248}) {
            var m=ScenicGoldenLeaves.mesh(seed,age,1200,dist,false,1,GROVE);frames++;
            check(m.size()<=480,"budget");check(m.equals(ScenicGoldenLeaves.mesh(seed,age,1200,dist,false,1,GROVE)),"server-clock determinism");
            for(var q:m){check(q.alpha()>=0&&q.alpha()<=.88,"opacity");for(var p:List.of(q.a(),q.b(),q.c(),q.d()))check(Double.isFinite(p.x()+p.y()+p.z())&&Math.abs(p.x())<28&&Math.abs(p.z())<22&&p.y()>0&&p.y()<12,"entire blade and stalk stay above ground and below canopy");}
        }
        for(int time:new int[]{0,6000,10500,14500,18000})check(ScenicGoldenLeaves.visibility(time,0)==0,"outside dusk");
        check(ScenicGoldenLeaves.visibility(12000,1)==0,"rain");
        for(int age:new int[]{-1,0,1200,1201})check(ScenicGoldenLeaves.mesh(19,age,1200,24,false,1,GROVE).isEmpty(),"lifetime");
        check(ScenicGoldenLeaves.mesh(19,600,1200,256,false,1,GROVE).isEmpty(),"region");
        check(ScenicGoldenLeaves.mesh(19,600,1200,24,false,1,(x,z)->null).isEmpty(),"unloaded terrain");
        check(ScenicGoldenLeaves.mesh(19,600,1200,24,false,1,(x,z)->new ScenicGoldenLeaves.Column(0,0)).isEmpty(),"no phantom leaves in a clearing");
        check(ScenicGoldenLeaves.mesh(19,600,1200,24,false,1,(x,z)->new ScenicGoldenLeaves.Column(Double.NaN,12)).isEmpty(),"invalid terrain");
        var near=ScenicGoldenLeaves.mesh(1518,600,1200,24,false,1,GROVE);var mid=ScenicGoldenLeaves.mesh(1518,600,1200,64,false,1,GROVE);var far=ScenicGoldenLeaves.mesh(1518,600,1200,128,false,1,GROVE);
        check(near.size()==480&&mid.size()==280&&far.size()==48,"96/56/24 leaf LOD");
        check(near.containsAll(mid),"surviving detailed leaves preserve trajectory");
        check(far.equals(ScenicGoldenLeaves.mesh(1518,600,1200,24,true,1,GROVE)),"minimal uses the same far trajectories");
        check(!near.equals(ScenicGoldenLeaves.mesh(1518,605,1200,24,false,1,GROVE)),"actual downward flutter");
        var higher=ScenicGoldenLeaves.mesh(1518,600,1200,24,false,1,(x,z)->new ScenicGoldenLeaves.Column(7,19));
        for(int i=0;i<near.size();i++)check(Math.abs(higher.get(i).a().y()-near.get(i).a().y()-7)<1e-8,"terrain height adaptation");
        for(int age=0;age<=1200;age+=40)Files.writeString(out.resolve("frame-"+age+".json"),AuroraGeometryQa.encode(ScenicGoldenLeaves.mesh(1518,age,1200,24,false,1,GROVE)));
        Files.writeString(out.resolve("validation.json"),"{\"sampledFrames\":"+frames+",\"nearQuads\":480,\"mediumQuads\":280,\"farQuads\":48,\"canopyRequired\":true,\"productionGeometry\":true,\"nativeClient\":false}");
        System.out.println("PASS "+frames+" leaf frames; terrain, weather, lifetime and LOD paths");
    }
}

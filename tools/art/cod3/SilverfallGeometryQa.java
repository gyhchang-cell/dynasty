import com.dynasty.cod3.*;
import java.nio.file.*;
import java.util.*;
public class SilverfallGeometryQa {
    static void check(boolean b,String why){if(!b)throw new AssertionError(why);}
    static double y(ScenicAurora.Quad q){return (q.a().y()+q.c().y())/2;}
    public static void main(String[] args)throws Exception{
        Path out=Path.of(args[0]);Files.createDirectories(out);int frames=0;
        for(long seed:new long[]{0,8,1518,-1,Long.MAX_VALUE})for(int age=0;age<=1200;age+=10)for(int dist:new int[]{0,24,64,128,248}){
            var mesh=ScenicSilverfall.mesh(seed,age,1200,dist,false,1);frames++;
            check(mesh.size()<=288,"300 budget including all water faces");check(mesh.equals(ScenicSilverfall.mesh(seed,age,1200,dist,false,1)),"server clock and seed determinism");
            for(var q:mesh){check(q.alpha()>=0&&q.alpha()<=.78,"alpha");for(var p:List.of(q.a(),q.b(),q.c(),q.d()))check(Double.isFinite(p.x()+p.y()+p.z())&&Math.abs(p.x())<18&&Math.abs(p.z())<9&&p.y()>=1&&p.y()<=50,"finite bound");}
        }
        for(double age:new double[]{-1,0,1200,1201,Double.NaN})check(ScenicSilverfall.mesh(8,age,1200,24,false,1).isEmpty(),"lifetime");
        for(double distance:new double[]{256,257,Double.NaN})check(ScenicSilverfall.mesh(8,600,1200,distance,false,1).isEmpty(),"region");
        check(ScenicSilverfall.mesh(8,600,1200,24,false,ScenicSilverfall.visibility(1)).isEmpty(),"rain suppressed");
        var near=ScenicSilverfall.mesh(8,600,1200,24,false,1);var far=ScenicSilverfall.mesh(8,600,1200,128,false,1);
        check(near.equals(far),"single catalogue LOD keeps all world geometry");
        var low=ScenicSilverfall.mesh(8,600,1200,24,true,1);check(near.subList(0,low.size()).equals(low)&&near.size()-low.size()==36,"minimal strips only mist");
        var t0=ScenicSilverfall.mesh(8,600,1200,24,true,1).stream().filter(ScenicAurora.Quad::feather).toList();
        var t1=ScenicSilverfall.mesh(8,601,1200,24,true,1).stream().filter(ScenicAurora.Quad::feather).toList();
        int upward=0;for(int i=0;i<t0.size();i++)if(y(t1.get(i))>=y(t0.get(i)))upward++;check(upward>=t0.size()-6,"highlights flow UP, allowing wraparound");
        check(!near.equals(ScenicSilverfall.mesh(8,620,1200,24,false,1)),"animated reverse flow");
        check(ScenicSilverfall.soundVolume(600,1200,24,0)>0&&ScenicSilverfall.soundVolume(600,1200,48,0)==0&&ScenicSilverfall.soundVolume(600,1200,24,1)==0&&ScenicSilverfall.soundVolume(1200,1200,24,0)==0,"bounded rain/lifetime/distance sound");
        for(int age=0;age<=1200;age+=40)Files.writeString(out.resolve("frame-"+age+".json"),AuroraGeometryQa.encode(ScenicSilverfall.mesh(1518,age,1200,24,false,1)));
        Files.writeString(out.resolve("validation.json"),"{\"sampledFrames\":"+frames+",\"quads\":"+near.size()+",\"minimalQuads\":"+low.size()+",\"upwardHighlights\":"+upward+",\"productionGeometry\":true,\"nativeClient\":false}");System.out.println("PASS "+frames+" silverfall frames; "+near.size()+" faces; "+upward+" upward highlights");
    }
}

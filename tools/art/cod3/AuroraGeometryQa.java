import com.dynasty.cod3.ScenicAurora;
import java.nio.file.*;
import java.util.*;

/** Runs the production geometry without loading a Minecraft client or renderer. */
public class AuroraGeometryQa {
    static int checks;
    static void require(boolean b,String s){checks++;if(!b)throw new AssertionError(s);}
    static String encode(List<ScenicAurora.Quad> quads){
        var out=new StringBuilder("[");
        for(var q:quads){if(out.length()>1)out.append(',');out.append("{\"color\":").append(q.color()).append(",\"alpha\":").append(q.alpha()).append(",\"feather\":").append(q.feather()).append(",\"points\":[");
            boolean first=true;for(var p:List.of(q.a(),q.b(),q.c(),q.d())){if(!first)out.append(',');first=false;out.append('[').append(p.x()).append(',').append(p.y()).append(',').append(p.z()).append(']');}out.append("]}");}
        return out.append(']').toString();
    }
    public static void main(String[] args)throws Exception{
        Path out=Path.of(args[0]);Files.createDirectories(out);
        for(int t:new int[]{0,6000,12999,23000,23999,24000})require(ScenicAurora.skyVisibility(t,0)==0,"day/dawn hidden "+t);
        for(int t:new int[]{14000,18000,22000})require(ScenicAurora.skyVisibility(t,0)==1,"clear night "+t);
        require(ScenicAurora.skyVisibility(18000,1)==0,"rain hidden");
        require(ScenicAurora.skyVisibility(13500,.5)==.25,"gradual dusk and rain fade");
        for(double age:new double[]{-1,0,1800,1900,Double.NaN})require(ScenicAurora.mesh(15,age,1800,30,false,1).isEmpty(),"inactive lifetime");
        require(ScenicAurora.mesh(15,600,1800,256,false,1).isEmpty(),"outside observer region");
        require(ScenicAurora.mesh(15,600,1800,257,false,1).isEmpty(),"beyond observer region");
        require(ScenicAurora.mesh(15,600,1800,30,false,0).isEmpty(),"no sky visibility");
        int totalFrames=0;
        for(long seed:new long[]{0,15,1518,-123,Long.MAX_VALUE})for(int age=0;age<=1800;age+=20)for(int dist:new int[]{0,24,64,128,248}){
            var mesh=ScenicAurora.mesh(seed,age,1800,dist,false,1);totalFrames++;
            require(mesh.size()<=ScenicAurora.MAX_QUADS,"budget");
            require(mesh.equals(ScenicAurora.mesh(seed,age,1800,dist,false,1)),"late observer determinism");
            for(var q:mesh){
                require(q.alpha()>=0&&q.alpha()<=.65,"no opaque sky sheets");
                for(var p:List.of(q.a(),q.b(),q.c(),q.d()))require(Double.isFinite(p.x()+p.y()+p.z())&&Math.abs(p.x())<=144&&Math.abs(p.z())<=100&&p.y()>=24&&p.y()<=160,"finite bounded sky geometry");
            }
        }
        var near=ScenicAurora.mesh(15,600,1800,24,false,1);var mid=ScenicAurora.mesh(15,600,1800,64,false,1);var far=ScenicAurora.mesh(15,600,1800,128,false,1);
        require(near.size()>mid.size()&&mid.size()>far.size(),"strict LOD reduction");
        require(far.stream().noneMatch(ScenicAurora.Quad::feather),"far sky has no feather clutter");
        require(ScenicAurora.mesh(15,600,1800,24,true,1).stream().noneMatch(ScenicAurora.Quad::feather),"minimal particles strips feathers");
        require(!near.equals(ScenicAurora.mesh(16,600,1800,24,false,1)),"different world seeds");
        require(!near.equals(ScenicAurora.mesh(15,620,1800,24,false,1)),"actual travelling motion");
        require(near.stream().filter(ScenicAurora.Quad::feather).map(ScenicAurora.Quad::a).limit(24).toList().equals(mid.stream().filter(ScenicAurora.Quad::feather).map(ScenicAurora.Quad::a).toList()),"LOD preserves individual feather paths");
        for(int age=0;age<=1800;age+=60)Files.writeString(out.resolve("frame-"+age+".json"),encode(ScenicAurora.mesh(1518,age,1800,24,false,1)));
        for(int dist:new int[]{24,64,128})Files.writeString(out.resolve("lod-"+dist+".json"),encode(ScenicAurora.mesh(1518,600,1800,dist,false,1)));
        Files.writeString(out.resolve("validation.json"),"{\"checks\":"+checks+",\"sampledFrames\":"+totalFrames+",\"nearQuads\":"+near.size()+",\"mediumQuads\":"+mid.size()+",\"farQuads\":"+far.size()+",\"productionGeometry\":true,\"nativeClient\":false}");
        System.out.println("PASS "+totalFrames+" sampled frames; LOD quads "+near.size()+" / "+mid.size()+" / "+far.size());
    }
}

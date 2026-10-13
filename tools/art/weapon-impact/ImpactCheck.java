import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.cod3.WeaponImpactVisual;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import io.netty.buffer.Unpooled;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

/** Exercises the exact triangles consumed by the production renderer, without GLFW. */
public final class ImpactCheck {
    private static void require(boolean ok,String reason){if(!ok)throw new AssertionError(reason);}
    private static List<Double> xyz(Vec3 v){return List.of(v.x,v.y,v.z);}
    public static void main(String[] args)throws Exception {
        int checks=0;var evidence=new LinkedHashMap<String,Object>();var origin=new Vec3(10,65,-4);
        var directions=List.of(new Vec3(0,0,1),new Vec3(1,0,0),new Vec3(0,1,0),Vec3.ZERO,new Vec3(-1,-.7,1));
        var rhythms=new HashSet<List<Integer>>();
        for(String id:new TreeSet<>(WeaponImpactVisual.weapons())) {
            var style=WeaponImpactVisual.style(id);
            require(style!=null&&style.duration()<=12,"Unbounded duration");
            require(style.bursts().stream().mapToInt(b->b.count()).sum()<=9,"Unbounded authored burst");
            if(Set.of("qinggang_sword","gilded_mace","yitian_sword").contains(id))rhythms.add(style.bursts().stream().map(b->b.onset()).toList());
            int peak=0;double reach=0;var colors=new HashSet<Integer>();
            for(var direction:directions)for(long seed:new long[]{0,1234,Long.MIN_VALUE,-1}) {
                var packet=WeaponImpactVisual.packet("minecraft:overworld",id,seed,100,origin,direction);
                require(WeaponImpactVisual.accepts(packet),"Factory rejected "+id);
                var wire=new FriendlyByteBuf(Unpooled.buffer());
                try{Cod3VisualPacket.encode(packet,wire);require(Cod3VisualPacket.decode(wire).equals(packet),"Wire drift "+id);require(wire.readableBytes()==0,"Wire tail");}finally{wire.release();}
                for(int step=-1;step<=style.duration()*8+1;step++) {
                    double age=step/8.;var triangles=WeaponImpactVisual.geometry(packet,age);peak=Math.max(peak,triangles.size());
                    require(triangles.size()<=48,"Triangle budget "+id);
                    if(age<0||age>=style.duration())require(triangles.isEmpty(),"Out-of-lifetime geometry");
                    for(var t:triangles) {
                        require(t.alpha()>0&&t.alpha()<=1&&Double.isFinite(t.alpha()),"Alpha drift");
                        require(t.b().subtract(t.a()).cross(t.c().subtract(t.a())).lengthSqr()>1e-15,"Degenerate face "+id);
                        colors.add(t.color());
                        for(var v:List.of(t.a(),t.b(),t.c())) {
                            require(Double.isFinite(v.lengthSqr()),"NaN vertex");
                            double distance=v.distanceTo(origin);reach=Math.max(reach,distance);
                            require(distance<1.7,"Unbounded impact geometry "+id+" "+distance);
                        }
                        checks++;
                    }
                    checks++;
                }
            }
            require(colors.size()<=(style.shape()==WeaponImpactVisual.Shape.CHIP?3:1),"Unbounded palette "+id);
            // The three rhythms must remain visible as separate newly appearing bursts.
            for(var b:style.bursts())require(!WeaponImpactVisual.geometry(WeaponImpactVisual.packet("minecraft:overworld",id,0,100,Vec3.ZERO,new Vec3(0,0,1)),b.onset()).isEmpty(),"Invisible onset "+id);
            var packet=WeaponImpactVisual.packet("minecraft:overworld",id,0,100,Vec3.ZERO,new Vec3(0,0,1));
            require(WeaponImpactVisual.geometry(packet,Double.NaN).isEmpty(),"NaN age accepted");
            var frames=new ArrayList<Object>();
            for(double age:new double[]{0,1,2,3,4,6,8,10}) {
                var triangles=WeaponImpactVisual.geometry(packet,age);var rows=new ArrayList<Object>();
                for(var t:triangles)rows.add(Map.of("a",xyz(t.a()),"b",xyz(t.b()),"c",xyz(t.c()),"color",t.color(),"alpha",t.alpha()));
                frames.add(Map.of("age",age,"triangles",rows));
            }
            evidence.put(id,Map.of("onsets",style.bursts().stream().map(b->b.onset()).toList(),"colors",colors.size(),"peakTriangles",peak,"maxVertexDistanceBlocks",reach,"frames",frames));
        }
        require(rhythms.size()==3,"Three named weapons share a rhythm");
        require(WeaponImpactVisual.packet("minecraft:overworld","seven_star_saber",0,0,Vec3.ZERO,Vec3.ZERO)==null,"Seven-star cue hijacked");
        var ordinary=new Cod3VisualPacket("minecraft:overworld",29,-1,0,0,8,1,Vec3.ZERO,Vec3.ZERO,"mesh_weapon",0,0);
        require(!WeaponImpactVisual.accepts(ordinary)&&WeaponImpactVisual.geometry(ordinary,1).isEmpty(),"Original afterimage hijacked");
        var valid=WeaponImpactVisual.packet("minecraft:overworld","tie_jian",0,0,Vec3.ZERO,Vec3.ZERO);
        var wrong=new Cod3VisualPacket(valid.dimension(),29,-1,0,0,2400,32,valid.origin(),valid.direction(),valid.sequence(),valid.tick(),valid.tint());
        require(!WeaponImpactVisual.accepts(wrong),"Malformed huge cue accepted");
        require(!WeaponImpactVisual.accepts(WeaponImpactVisual.packet("minecraft:overworld","tie_jian",0,0,new Vec3(Double.NaN,0,0),Vec3.ZERO)),"NaN origin accepted");
        Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(evidence)+"\n");
        System.out.println("PASS "+checks+" actual-geometry/timeline/wire checks; 7 material cues; 3 distinct rhythms; no GUI/gameplay claim");
    }
}

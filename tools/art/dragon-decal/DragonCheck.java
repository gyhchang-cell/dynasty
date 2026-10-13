import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.FriendlyByteBuf;
import io.netty.buffer.Unpooled;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

public final class DragonCheck {
    static int checks;
    static void check(boolean v,String why){checks++;if(!v)throw new AssertionError(why);}
    static List<Double> xyz(Vec3 v){return List.of(v.x,v.y,v.z);}
    static Map<String,Object> vertex(DragonDecal.Vertex v){return Map.of("xyz",xyz(v.position()),"uv",List.of(v.u(),v.v()));}
    public static void main(String[] args)throws Exception {
        var frames=new ArrayList<Object>();double reach=0;
        for(int angle=0;angle<360;angle+=15)for(double scale:new double[]{.45,.8,1.4})for(var offset:List.of(Vec3.ZERO,new Vec3(6,2,0),new Vec3(-6,3,6))) {
            var n=new Vec3(Math.sin(Math.toRadians(angle)),0,Math.cos(Math.toRadians(angle)));var p=DragonDecal.packet("minecraft:overworld",42,100,scale,offset,n);
            check(DragonDecal.accepts(p),"Factory cue rejected");var wire=new FriendlyByteBuf(Unpooled.buffer());
            try{Cod3VisualPacket.encode(p,wire);check(Cod3VisualPacket.decode(wire).equals(p)&&wire.readableBytes()==0,"Wire drift");}finally{wire.release();}
            for(int step=-1;step<=25;step++) {
                double age=step/2.;var feet=new Vec3(10,65,-10);var ts=DragonDecal.geometry(p,age,feet);var delta=new Vec3(2,-1,-3);var moved=DragonDecal.geometry(p,age,feet.add(delta));
                check(ts.size()==(age<0||age>=12?0:2),"Lifetime/budget");
                for(int i=0;i<ts.size();i++) {
                    var t=ts.get(i);check(t.alpha()>0&&t.alpha()<=.85,"Fade");
                    check(t.b().position().subtract(t.a().position()).cross(t.c().position().subtract(t.a().position())).lengthSqr()>1e-9,"Degenerate plane");
                    check(moved.get(i).a().position().subtract(t.a().position()).distanceTo(delta)<1e-8,"Parent follow mismatch");
                    for(var v:List.of(t.a(),t.b(),t.c())){
                        double dist=v.position().distanceTo(feet.add(offset));reach=Math.max(reach,dist);check(dist<1&&Double.isFinite(dist),"Unbounded plane");
                        check((v.u()==0||v.u()==1)&&(v.v()==0||v.v()==1),"Not full exact UV atlas");
                        check(Math.abs(v.position().subtract(feet.add(offset)).dot(n))<1e-8,"Plane off contact surface");
                    }
                }
            }
        }
        for(double age:new double[]{0,3,6,9,11,12}) {
            var p=DragonDecal.packet("minecraft:overworld",42,100,1,Vec3.ZERO,new Vec3(0,0,1));var ts=new ArrayList<Object>();
            for(var t:DragonDecal.geometry(p,age,Vec3.ZERO))ts.add(Map.of("a",vertex(t.a()),"b",vertex(t.b()),"c",vertex(t.c()),"alpha",t.alpha()));
            frames.add(Map.of("age",age,"triangles",ts));
        }
        var p=DragonDecal.packet("minecraft:overworld",42,100,1,Vec3.ZERO,new Vec3(0,0,1));
        for(var bad:List.of(DragonDecal.packet("minecraft:overworld",-1,0,1,Vec3.ZERO,new Vec3(0,0,1)),DragonDecal.packet("minecraft:overworld",1,0,32,Vec3.ZERO,new Vec3(0,0,1)),
                DragonDecal.packet("minecraft:overworld",1,0,1,new Vec3(40,0,0),new Vec3(0,0,1)),DragonDecal.packet("minecraft:overworld",1,0,1,Vec3.ZERO,Vec3.ZERO),
                DragonDecal.packet("minecraft:overworld",1,0,1,Vec3.ZERO,new Vec3(0,0,1),9),
                TangWind.packet("minecraft:overworld",1,0,0,Vec3.ZERO,Vec3.ZERO)))check(!DragonDecal.accepts(bad),"Illegal/stolen cue");
        check(DragonDecal.geometry(p,Double.NaN,Vec3.ZERO).isEmpty()&&DragonDecal.geometry(p,1,new Vec3(Double.NaN,0,0)).isEmpty(),"NaN geometry");
        Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(Map.of("frames",frames,"checks",checks,"peakTriangles",2,"maxLocalRadius",reach))+"\n");
        System.out.println("PASS "+checks+" production UV/anchor/lifetime/wire checks; peak2tris radius="+reach+"; software only, not native/humans");
    }
}

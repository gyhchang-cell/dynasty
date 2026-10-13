import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.FriendlyByteBuf;
import io.netty.buffer.Unpooled;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

public final class CrackCheck {
    private static void check(boolean v,String why){if(!v)throw new AssertionError(why);}
    private static List<Double> xyz(Vec3 v){return List.of(v.x,v.y,v.z);}
    public static void main(String[] args)throws Exception {
        int checks=0,peak=0;double reach=0;var data=new LinkedHashMap<String,Object>();
        for(String weapon:List.of("pojun_axe","xuantian_axe")) {
            for(var direction:List.of(Vec3.ZERO,new Vec3(0,1,0),new Vec3(0,0,1),new Vec3(1,0,0),new Vec3(-1,-1,1)))for(double size:new double[]{.45,.8,1.2}) {
                var p=ArmorCrack.packet("minecraft:overworld",42,weapon,0,100,size,Vec3.ZERO,direction);
                check(ArmorCrack.accepts(p),"Factory cue rejected");var wire=new FriendlyByteBuf(Unpooled.buffer());
                try{Cod3VisualPacket.encode(p,wire);check(Cod3VisualPacket.decode(wire).equals(p)&&wire.readableBytes()==0,"Wire drift");}finally{wire.release();}
                for(int step=-1;step<=21;step++) {
                    double age=step/2.;var center=new Vec3(10,65,-10);var triangles=ArmorCrack.geometry(p,age,center);var offset=new Vec3(2,1,-3);
                    var shifted=ArmorCrack.geometry(p,age,center.add(offset));check(triangles.size()<=80,"Budget");peak=Math.max(peak,triangles.size());
                    if(age<0||age>=10)check(triangles.isEmpty(),"Lifetime");
                    else check(!triangles.isEmpty(),"Missing active frame");
                    for(int i=0;i<triangles.size();i++) {
                        var t=triangles.get(i);check(t.color()==ArmorCrack.DARK||t.color()==ArmorCrack.color(weapon),"Pixel palette");
                        check(t.alpha()>0&&t.alpha()<=.9,"Fade");check(t.b().subtract(t.a()).cross(t.c().subtract(t.a())).lengthSqr()>1e-12,"Degenerate cell");
                        check(shifted.get(i).a().subtract(t.a()).distanceTo(offset)<1e-9,"Victim follow mismatch");
                        for(var v:List.of(t.a(),t.b(),t.c())){double distance=v.distanceTo(center);reach=Math.max(reach,distance);check(Double.isFinite(v.lengthSqr())&&distance<1.25,"Unbounded geometry");checks++;}
                    }checks++;
                }
            }
            var p=ArmorCrack.packet("minecraft:overworld",42,weapon,0,0,.8,Vec3.ZERO,new Vec3(0,0,1));var frames=new ArrayList<Object>();
            for(double age:new double[]{0,1,3,6,8,9,10}) {
                var rows=new ArrayList<Object>();for(var t:ArmorCrack.geometry(p,age,Vec3.ZERO))rows.add(Map.of("a",xyz(t.a()),"b",xyz(t.b()),"c",xyz(t.c()),"color",t.color(),"alpha",t.alpha()));
                frames.add(Map.of("age",age,"triangles",rows));
            }data.put(weapon,Map.of("frames",frames));
            check(!ArmorCrack.accepts(ArmorCrack.packet("minecraft:overworld",-1,weapon,0,0,.8,Vec3.ZERO,Vec3.ZERO)),"Invalid actor");
            check(!ArmorCrack.accepts(ArmorCrack.packet("minecraft:overworld",1,weapon,0,0,32,Vec3.ZERO,Vec3.ZERO)),"Huge cue");
            check(ArmorCrack.geometry(p,Double.NaN,Vec3.ZERO).isEmpty()&&ArmorCrack.geometry(p,1,new Vec3(Double.NaN,0,0)).isEmpty(),"NaN geometry");
        }
        var anchor=ArmorCrack.anchor(new Vec3(10,64,10),.6,1.8,new Vec3(0,0,1));check(anchor.distanceTo(new Vec3(10,64.99,9.675))<1e-9,"Actual chest surface offset");
        check(ArmorCrack.packet("minecraft:overworld",1,"iron_axe",0,0,1,Vec3.ZERO,Vec3.ZERO)==null,"Generic axe guessed");
        check(!ArmorCrack.accepts(TangWind.packet("minecraft:overworld",1,0,0,Vec3.ZERO,Vec3.ZERO)),"Tang cue stolen");
        data.put("measurements",Map.of("peakTriangles",peak,"maxLocalDistanceBlocks",reach,"checks",checks));
        Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(data)+"\n");
        System.out.println("PASS "+checks+" production geometry/anchor/position checks + original wire; peak="+peak+" reach="+reach+"; no graphics/human acceptance");
    }
}

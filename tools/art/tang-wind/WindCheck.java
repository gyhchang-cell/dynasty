import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.FriendlyByteBuf;
import io.netty.buffer.Unpooled;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

public final class WindCheck {
    private static void check(boolean v,String reason){if(!v)throw new AssertionError(reason);}
    private static List<Double> xyz(Vec3 v){return List.of(v.x,v.y,v.z);}
    public static void main(String[] args)throws Exception {
        int checks=0;var p=TangWind.packet("minecraft:overworld",12,4,100,Vec3.ZERO,new Vec3(0,0,1));
        var wire=new FriendlyByteBuf(Unpooled.buffer());try{Cod3VisualPacket.encode(p,wire);check(Cod3VisualPacket.decode(wire).equals(p)&&wire.readableBytes()==0,"Codec drift");}finally{wire.release();}
        var movements=List.of(Vec3.ZERO,new Vec3(0,1,0),new Vec3(0,0,.3),new Vec3(.3,0,0),new Vec3(-.3,0,.3),new Vec3(Double.NaN,0,0));
        for(var movement:movements)for(boolean first:new boolean[]{false,true})for(int tick=-1;tick<=97;tick++) {
            double age=tick/8.;var feet=new Vec3(10,64,-8);var triangles=TangWind.geometry(p,age,feet,movement,first);
            check(triangles.size()==(age<0||age>=12?0:first?20:40),"Budget/lifetime");
            var offset=new Vec3(3,-1,4);var shifted=TangWind.geometry(p,age,feet.add(offset),movement,first);
            for(int i=0;i<triangles.size();i++) {
                var t=triangles.get(i);check(t.color()==TangWind.COLOR&&t.alpha()>0&&t.alpha()<=.8,"Palette/fade");
                check(t.b().subtract(t.a()).cross(t.c().subtract(t.a())).lengthSqr()>1e-10,"Degenerate plane");
                check(shifted.get(i).a().subtract(t.a()).distanceTo(offset)<1e-9,"Does not follow actual actor position");
                for(var v:List.of(t.a(),t.b(),t.c())) {
                    check(Double.isFinite(v.lengthSqr())&&v.distanceTo(feet)<1.8,"Unbounded/NaN");
                    check(v.y>=feet.y+.17&&v.y<=feet.y+(first?.265:.925),"First person upper stream or ground clipping");checks++;
                }
            }
            checks++;
        }
        check(TangWind.horizontal(new Vec3(0,1,0),Vec3.ZERO).equals(new Vec3(0,0,1)),"Vertical fallback");
        check(TangWind.horizontal(new Vec3(.2,0,0),new Vec3(0,0,1)).equals(new Vec3(1,0,0)),"Movement not preferred");
        check(TangWind.geometry(p,Double.NaN,Vec3.ZERO,Vec3.ZERO,false).isEmpty(),"NaN age");
        check(TangWind.geometry(p,1,new Vec3(Double.NaN,0,0),Vec3.ZERO,false).isEmpty(),"NaN anchor");
        check(!TangWind.accepts(TangWind.packet("minecraft:overworld",-1,0,0,Vec3.ZERO,Vec3.ZERO)),"Invalid actor");
        check(!TangWind.accepts(new Cod3VisualPacket(p.dimension(),1,p.entityId(),0,0,2400,32,p.origin(),p.direction(),p.sequence(),0,p.tint())),"Huge cue");
        check(!TangWind.accepts(WeaponImpactVisual.packet("minecraft:overworld","tie_jian",0,0,Vec3.ZERO,Vec3.ZERO)),"Material cue stolen");
        var data=new LinkedHashMap<String,Object>();
        for(boolean first:new boolean[]{false,true})for(var direction:List.of(new Vec3(0,0,.3),new Vec3(.3,0,.3))) {
            var frames=new ArrayList<Object>();for(double age:new double[]{0,1,3,6,9,11,12}) {
                var rows=new ArrayList<Object>();for(var t:TangWind.geometry(p,age,Vec3.ZERO,direction,first))rows.add(Map.of("a",xyz(t.a()),"b",xyz(t.b()),"c",xyz(t.c()),"color",t.color(),"alpha",t.alpha()));
                frames.add(Map.of("age",age,"triangles",rows));
            }
            data.put((first?"own-first-person":"observer")+(direction.x==0?"-straight":"-turn"),Map.of("frames",frames));
        }
        Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(data)+"\n");
        System.out.println("PASS "+checks+" production triangle/position/lifetime checks + real packet codec; no client/human claim");
    }
}

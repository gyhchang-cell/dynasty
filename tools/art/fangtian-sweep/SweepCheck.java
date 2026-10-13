import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.FriendlyByteBuf;
import io.netty.buffer.Unpooled;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

public final class SweepCheck {
    static int checks;
    static void check(boolean b,String s){checks++;if(!b)throw new AssertionError(s);}
    static List<Double> xyz(Vec3 v){return List.of(v.x,v.y,v.z);}
    static Vec3 turn(Vec3 v,double a){return new Vec3(v.x*Math.cos(a)+v.z*Math.sin(a),v.y,-v.x*Math.sin(a)+v.z*Math.cos(a));}
    public static void main(String[] args)throws Exception {
        var data=new LinkedHashMap<String,Object>();double reach=0;int peak=0;
        var at=new Vec3(13,67,-21);var delta=new Vec3(7,.5,-4);
        for(int angle=0;angle<360;angle+=5) {
            double a=Math.toRadians(angle);var direction=turn(new Vec3(0,0,1),a);
            var p=FangtianSweep.packet("minecraft:overworld",42,100,at,direction);
            check(FangtianSweep.accepts(p),"Factory cue rejected");var wire=new FriendlyByteBuf(Unpooled.buffer());
            try{Cod3VisualPacket.encode(p,wire);check(Cod3VisualPacket.decode(wire).equals(p)&&wire.readableBytes()==0,"Wire drift");}finally{wire.release();}
            for(int step=-1;step<=49;step++) {
                double age=step/8.;var ts=FangtianSweep.geometry(p,age);peak=Math.max(peak,ts.size());
                check(ts.size()==(age>=0&&age<6?48:0),"Lifetime/triangle budget");
                var ref=FangtianSweep.geometry(FangtianSweep.packet("minecraft:overworld",42,100,Vec3.ZERO,new Vec3(0,0,1)),age);
                var moved=FangtianSweep.geometry(FangtianSweep.packet("minecraft:overworld",42,100,at.add(delta),direction),age);
                Vec3 rimCenter=Vec3.ZERO;
                for(int i=0;i<ts.size();i++) {
                    var t=ts.get(i);check(t.alpha()>0&&t.alpha()<=.8,"Fade out of range");check(t.color()==0x647F83||t.color()==0x91B6B7,"Nonfinite palette");
                    check(t.b().subtract(t.a()).cross(t.c().subtract(t.a())).lengthSqr()>1e-12,"Degenerate plane");
                    var vertices=List.of(t.a(),t.b(),t.c());var refVertices=List.of(ref.get(i).a(),ref.get(i).b(),ref.get(i).c());
                    var movedVertices=List.of(moved.get(i).a(),moved.get(i).b(),moved.get(i).c());
                    for(int v=0;v<3;v++) {
                        var local=vertices.get(v).subtract(at);reach=Math.max(reach,local.length());
                        check(Double.isFinite(local.lengthSqr())&&local.length()<1.32,"Giant contact cue");
                        check(local.distanceTo(turn(refVertices.get(v),a))<1e-8,"Captured yaw rotation mismatch");
                        check(movedVertices.get(v).subtract(vertices.get(v)).distanceTo(delta)<1e-8,"World anchor mismatch");
                        if(i<24)rimCenter=rimCenter.add(local);
                    }
                }
                if(!ts.isEmpty())check(Math.abs(rimCenter.x)<1e-8&&Math.abs(rimCenter.z)<1e-8,"Full360 rim is asymmetric");
            }
        }
        for(int angle:new int[]{0,90}) {
            var frames=new ArrayList<Object>();var p=FangtianSweep.packet("minecraft:overworld",42,100,new Vec3(0,.7,0),turn(new Vec3(0,0,1),Math.toRadians(angle)));
            for(double age:new double[]{0,1,2,3,4,5,6}) {
                var rows=new ArrayList<Object>();for(var t:FangtianSweep.geometry(p,age))rows.add(Map.of("a",xyz(t.a()),"b",xyz(t.b()),"c",xyz(t.c()),"color",t.color(),"alpha",t.alpha()));
                frames.add(Map.of("age",age,"triangles",rows));
            }data.put("native_yaw_"+angle,Map.of("frames",frames));
        }
        var p=FangtianSweep.packet("minecraft:overworld",42,100,at,new Vec3(0,0,1));
        check(FangtianSweep.geometry(p,Double.NaN).isEmpty(),"NaN age");
        check(!FangtianSweep.accepts(new Cod3VisualPacket(p.dimension(),2,42,0,100,6,32,at,p.direction(),p.sequence(),0,p.tint())),"Giant packet");
        check(!FangtianSweep.accepts(new Cod3VisualPacket(p.dimension(),2,42,0,100,6,1,at,new Vec3(0,1,0),p.sequence(),0,p.tint())),"Vertical yaw");
        check(!FangtianSweep.accepts(FangtianSweep.packet("minecraft:overworld",-1,100,at,p.direction())),"Actorless cue");
        check(!FangtianSweep.accepts(WeaponLift.packet("minecraft:overworld",42,"juque_sword",0,100,1,at,p.direction(),0,true)),"Other receipt stolen");
        data.put("measurements",Map.of("checks",checks,"peakTriangles",peak,"maxLocalRadius",reach));
        Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(data)+"\n");
        System.out.println("PASS "+checks+" actual Java coarse-plane/full360/yaw/world-anchor/lifetime/wire checks; peak="+peak+" reach="+reach+"; software, not graphics/humans");
    }
}

import com.dynasty.cod3.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.FriendlyByteBuf;
import io.netty.buffer.Unpooled;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

public final class FluteCheck {
    static int checks;
    static void check(boolean b,String why){checks++;if(!b)throw new AssertionError(why);}
    static List<Double> xyz(Vec3 v){return List.of(v.x,v.y,v.z);}
    static Vec3 turn(Vec3 v,double a){return new Vec3(v.x*Math.cos(a)+v.z*Math.sin(a),v.y,-v.x*Math.sin(a)+v.z*Math.cos(a));}
    public static void main(String[] args)throws Exception {
        var data=new LinkedHashMap<String,Object>();double reach=0;int peak=0;
        var at=new Vec3(13,67,-21);var delta=new Vec3(7,.5,-4);
        for(var hand:InteractionHand.values())for(int angle=0;angle<360;angle+=15) {
            double a=Math.toRadians(angle);var dir=turn(new Vec3(0,0,1),a);
            var p=FluteWave.packet("minecraft:overworld",42,100,at,dir,hand);check(FluteWave.accepts(p),"Factory rejected");
            var wire=new FriendlyByteBuf(Unpooled.buffer());try{Cod3VisualPacket.encode(p,wire);check(Cod3VisualPacket.decode(wire).equals(p)&&wire.readableBytes()==0,"Wire drift");}finally{wire.release();}
            check(p.tick()==(hand==InteractionHand.OFF_HAND?1:0),"Actual source hand lost");
            for(int step=-1;step<=81;step++) {
                double age=step/8.;var ts=FluteWave.geometry(p,age);peak=Math.max(peak,ts.size());
                int pulses=0;for(int pulse=0;pulse<3;pulse++)if(age>=0&&age<10&&age-pulse*3>=0&&age-pulse*3<4)pulses++;
                check(pulses<=2&&ts.size()==48*pulses,"Offset onset/duration/overlap budget");
                var reference=FluteWave.geometry(FluteWave.packet("minecraft:overworld",42,100,Vec3.ZERO,new Vec3(0,0,1),hand),age);
                var moved=FluteWave.geometry(FluteWave.packet("minecraft:overworld",42,100,at.add(delta),dir,hand),age);var center=Vec3.ZERO;
                for(int i=0;i<ts.size();i++) {
                    var t=ts.get(i);check(t.alpha()>0&&t.alpha()<=.72,"Alpha");check(t.color()==FluteWave.COLOR||t.color()==0xA0CCAE,"Unexpected palette");
                    check(t.b().subtract(t.a()).cross(t.c().subtract(t.a())).lengthSqr()>1e-12,"Degenerate ripple");
                    var vs=List.of(t.a(),t.b(),t.c());var refs=List.of(reference.get(i).a(),reference.get(i).b(),reference.get(i).c());var mv=List.of(moved.get(i).a(),moved.get(i).b(),moved.get(i).c());
                    for(int v=0;v<3;v++) {
                        var local=vs.get(v).subtract(at);reach=Math.max(reach,local.length());check(local.length()<2.4&&Double.isFinite(local.lengthSqr()),"Unbounded area decoration");
                        check(Math.abs(local.y)<=.040001,"World contact height drift");check(local.distanceTo(turn(refs.get(v),a))<1e-8,"Captured look rotation drift");
                        check(mv.get(v).subtract(vs.get(v)).distanceTo(delta)<1e-8,"Explicit world anchor drift");center=center.add(local);
                    }
                }
                if(!ts.isEmpty())check(Math.abs(center.x)<1e-8&&Math.abs(center.z)<1e-8,"Ripple not full centered360");
            }
        }
        for(var hand:InteractionHand.values()) {
            var p=FluteWave.packet("minecraft:overworld",42,100,new Vec3(0,.7,0),new Vec3(0,0,1),hand);var frames=new ArrayList<Object>();
            for(double age:new double[]{0,1,2,3.25,4,6.25,8,9,10}) {
                var rows=new ArrayList<Object>();for(var t:FluteWave.geometry(p,age))rows.add(Map.of("a",xyz(t.a()),"b",xyz(t.b()),"c",xyz(t.c()),"color",t.color(),"alpha",t.alpha()));
                frames.add(Map.of("age",age,"triangles",rows));
            }data.put(hand.toString(),Map.of("frames",frames));
            check(FluteWave.geometry(p,Double.NaN).isEmpty(),"NaN age");
        }
        var p=FluteWave.packet("minecraft:overworld",42,100,at,new Vec3(0,0,1),InteractionHand.MAIN_HAND);
        check(!FluteWave.accepts(new Cod3VisualPacket(p.dimension(),26,42,0,100,10,32,at,p.direction(),p.sequence(),0,p.tint())),"Huge packet");
        check(!FluteWave.accepts(new Cod3VisualPacket(p.dimension(),26,42,0,100,10,1,at,new Vec3(0,1,0),p.sequence(),0,p.tint())),"Vertical yaw");
        check(!FluteWave.accepts(FangtianSweep.packet("minecraft:overworld",42,100,at,p.direction())),"Other cue stolen");
        check(!FluteWave.accepts(FluteWave.packet("minecraft:overworld",-1,100,at,p.direction(),InteractionHand.MAIN_HAND)),"Invalid caster");
        data.put("measurements",Map.of("checks",checks,"peakTriangles",peak,"maxLocalRadius",reach));
        Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(data)+"\n");
        System.out.println("PASS "+checks+" actual Java pulse overlap/faceted geometry/world anchor/yaw/hand/lifetime/wire checks; peak="+peak+" reach="+reach+"; not graphics/humans");
    }
}

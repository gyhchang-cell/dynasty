import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import net.minecraft.network.FriendlyByteBuf;
import io.netty.buffer.Unpooled;
import com.google.gson.GsonBuilder;
import java.nio.file.*;
import java.util.*;

public final class LiftCheck {
    static int checks;
    static void check(boolean v,String why){checks++;if(!v)throw new AssertionError(why);}
    static List<Double> xyz(Vec3 v){return List.of(v.x,v.y,v.z);}
    public static void main(String[] args)throws Exception {
        var data=new LinkedHashMap<String,Object>();double reach=0;int peak=0;
        for(String weapon:List.of("juque_sword","huan_shou_dao")) {
            for(int angle=0;angle<360;angle+=30)for(double scale:new double[]{.45,.8,1.2})for(boolean supported:new boolean[]{false,true}) {
                var n=new Vec3(Math.sin(Math.toRadians(angle)),0,Math.cos(Math.toRadians(angle)));var p=WeaponLift.packet("minecraft:overworld",42,weapon,7,100,scale,Vec3.ZERO,n,0x707070,supported);
                check(WeaponLift.accepts(p),"Factory cue rejected");var wire=new FriendlyByteBuf(Unpooled.buffer());
                try{Cod3VisualPacket.encode(p,wire);check(Cod3VisualPacket.decode(wire).equals(p)&&wire.readableBytes()==0,"Wire drift");}finally{wire.release();}
                for(int step=-1;step<=17;step++)for(boolean air:new boolean[]{false,true}) {
                    double age=step/2.;var feet=new Vec3(0,1,0);var ts=WeaponLift.geometry(p,age,feet,air);peak=Math.max(peak,ts.size());
                    boolean valid=age>=0&&age<8;int dust=valid&&supported&&age<5?48:0;
                    check(ts.size()==dust+(valid&&air?20:0),"Lifetime/ground/arc budget");
                    var moved=WeaponLift.geometry(p,age,feet.add(0,.2,0),air);int arc=valid&&air?20:0;
                    for(int i=0;i<ts.size();i++) {
                        var t=ts.get(i);check(t.alpha()>0&&t.alpha()<=.85,"Fade");
                        check(t.b().subtract(t.a()).cross(t.c().subtract(t.a())).lengthSqr()>1e-12,"Degenerate block/arc");
                        check(moved.get(i).a().subtract(t.a()).distanceTo(i<arc?new Vec3(0,.2,0):Vec3.ZERO)<1e-8,"Arc must follow real victim; dust must stay at ground");
                        for(var v:List.of(t.a(),t.b(),t.c())) {
                            var center=i<arc?feet:p.origin();double dist=v.distanceTo(center);reach=Math.max(reach,dist);check(dist<1.4&&Double.isFinite(dist),"Unbounded geometry");
                            if(i>=arc)check(v.y>=p.origin().y,"Chip buried below actual ground");
                        }
                    }
                }
            }
            var p=WeaponLift.packet("minecraft:overworld",42,weapon,0,100,1,Vec3.ZERO,new Vec3(0,0,1),0x707070,true);var frames=new ArrayList<Object>();
            for(double age:new double[]{0,1,3,5,7,8}) {
                // Controlled pose samples, never presented as native flight or a game screenshot.
                var feet=new Vec3(0,age<5?.3:.02,0);boolean air=age<5;var rows=new ArrayList<Object>();
                for(var t:WeaponLift.geometry(p,age,feet,air))rows.add(Map.of("a",xyz(t.a()),"b",xyz(t.b()),"c",xyz(t.c()),"color",t.color(),"alpha",t.alpha()));
                frames.add(Map.of("age",age,"airborne",air,"triangles",rows));
            }data.put(weapon,Map.of("frames",frames));
            check(WeaponLift.geometry(p,Double.NaN,Vec3.ZERO,true).isEmpty()&&WeaponLift.geometry(p,1,new Vec3(Double.NaN,0,0),true).isEmpty(),"NaN");
        }
        check(WeaponLift.packet("minecraft:overworld",42,"iron_sword",0,0,1,Vec3.ZERO,Vec3.ZERO,0,true)==null,"Generic sword guessed");
        check(!WeaponLift.accepts(WeaponLift.packet("minecraft:overworld",-1,"juque_sword",0,0,1,Vec3.ZERO,Vec3.ZERO,0,true)),"Invalid actor");
        check(!WeaponLift.accepts(WeaponLift.packet("minecraft:overworld",1,"juque_sword",0,0,32,Vec3.ZERO,Vec3.ZERO,0,true)),"Huge cue");
        check(!WeaponLift.accepts(TangWind.packet("minecraft:overworld",1,0,0,Vec3.ZERO,Vec3.ZERO)),"Stolen cue");
        data.put("measurements",Map.of("checks",checks,"peakTriangles",peak,"maxLocalRadius",reach,"poseSource","Controlled software airborne/grounded inputs, not native trajectory"));
        Files.writeString(Path.of(args[0]),new GsonBuilder().setPrettyPrinting().create().toJson(data)+"\n");
        System.out.println("PASS "+checks+" production geometry/ground-victim-separation/wire checks; peak="+peak+" reach="+reach+"; not graphics/humans");
    }
}

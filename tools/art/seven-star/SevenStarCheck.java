import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.cod3.SevenStarFlash;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import io.netty.buffer.Unpooled;
import java.util.*;

/** Actual Java timeline and wire codec; no fake gameplay/client acceptance. */
public final class SevenStarCheck {
    private static void require(boolean ok,String reason){if(!ok)throw new AssertionError(reason);}
    public static void main(String[] args) {
        int checks=0;var onsets=new ArrayList<Integer>();var previous=new double[7];
        for(int frame=-20;frame<=340;frame++) {
            double age=frame/20.;int active=0;
            for(int i=0;i<7;i++) {
                var p=SevenStarFlash.pulse(i,age);
                require(Double.isFinite(p.alpha())&&p.alpha()>=0&&p.alpha()<=1,"Invalid opacity");
                if(p.alpha()>0){active++;require(p.size()>0&&p.size()<=.131,"Unbounded star");}
                if(p.alpha()>previous[i]){require(frame==i*40,"Wrong onset/reflash");onsets.add(i);}
                previous[i]=p.alpha();checks++;
            }
            require(active<=2,"Star shower instead of two-star maximum");
            if(age<0||age>=16)require(active==0,"Effect outside lifetime");
        }
        require(onsets.equals(List.of(0,1,2,3,4,5,6)),"Not seven ordered onsets");
        for(int fps:new int[]{10,15,30,60,144}) {
            var seen=new HashSet<Integer>();
            for(int frame=0;frame<fps;frame++)for(int i=0;i<7;i++)if(SevenStarFlash.pulse(i,frame*20./fps).alpha()>0)seen.add(i);
            require(seen.size()==7,"A flash disappears at "+fps+" FPS");checks++;
        }
        Vec3 origin=new Vec3(10,70,-6);
        for(var direction:List.of(new Vec3(0,0,1),new Vec3(1,0,0),new Vec3(0,1,0),Vec3.ZERO,new Vec3(1,.7,-1))) {
            var points=new HashSet<Vec3>();var right=SevenStarFlash.right(direction);
            require(Math.abs(right.length()-1)<1e-9&&right.y==0,"Unstable vertical fallback");
            for(int i=0;i<7;i++) {
                var point=SevenStarFlash.point(i,origin,direction);points.add(point);
                require(point.distanceTo(origin)<1.65&&point.y>=origin.y+.4&&point.y<=origin.y+1.3,"Unbounded impact cue");checks++;
            }
            require(points.size()==7,"Collapsed constellation");
            var packet=SevenStarFlash.packet("minecraft:overworld",1234,100,origin,direction);
            require(SevenStarFlash.accepts(packet),"Factory rejected");
            var wire=new FriendlyByteBuf(Unpooled.buffer());
            try{Cod3VisualPacket.encode(packet,wire);require(Cod3VisualPacket.decode(wire).equals(packet),"Actual wire codec lost cue/timing/position");require(wire.readableBytes()==0,"Trailing packet data");}finally{wire.release();}
            checks++;
        }
        var ordinary=new Cod3VisualPacket("minecraft:overworld",21,-1,123,100,30,1,origin,Vec3.ZERO,"",0,0xDDD9FF);
        require(ordinary.valid()&&!SevenStarFlash.accepts(ordinary),"Ordinary star template was hijacked");
        var wrongDuration=new Cod3VisualPacket("minecraft:overworld",21,-1,123,100,2400,1,origin,Vec3.ZERO,SevenStarFlash.CUE,0,0xDDD9FF);
        require(!SevenStarFlash.accepts(wrongDuration),"Unbounded dedicated cue accepted");
        require(!SevenStarFlash.packet("minecraft:overworld",123,100,new Vec3(Double.NaN,0,0),Vec3.ZERO).valid(),"NaN packet accepted");
        checks+=3;
        System.out.println("PASS "+checks+" timeline/shape/wire checks; exactly seven onsets 0,2,4,6,8,10,12; no GUI/gameplay claim");
    }
}

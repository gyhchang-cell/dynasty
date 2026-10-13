package com.dynasty.cod3;

import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

/** Cosmetic successful-hit cue; seven onsets, no damage or scheduled server work. */
public final class SevenStarFlash {
    public static final String CUE="equipment_seven_star_hit";
    public static final int DURATION=16,COUNT=7,INTERVAL=2;
    private static final double[][] STARS={{-.55,.20},{-.50,-.20},{-.10,-.18},{0,.18},{.32,.36},{.62,.44},{.92,.66}};
    public record Pulse(int index,double alpha,double size) {}

    public static Pulse pulse(int index,double age) {
        if(index<0||index>=COUNT)throw new IllegalArgumentException("Star index");
        double local=age-index*INTERVAL;
        if(!Double.isFinite(age)||age<0||age>=DURATION||local<0||local>=3)return new Pulse(index,0,0);
        double alpha=1-local/3;
        return new Pulse(index,alpha,.045+.085*alpha);
    }
    public static Vec3 right(Vec3 direction) {
        Vec3 horizontal=new Vec3(direction.x,0,direction.z);
        if(horizontal.lengthSqr()<.000001)horizontal=new Vec3(0,0,1);
        horizontal=horizontal.normalize();return new Vec3(horizontal.z,0,-horizontal.x);
    }
    public static Vec3 point(int index,Vec3 origin,Vec3 direction) {
        if(index<0||index>=COUNT)throw new IllegalArgumentException("Star index");
        return origin.add(right(direction).scale(STARS[index][0])).add(0,.62+STARS[index][1],0);
    }
    public static Cod3VisualPacket packet(String dimension,long seed,long start,Vec3 origin,Vec3 direction) {
        return new Cod3VisualPacket(dimension,21,-1,seed,start,DURATION,1,origin,direction,CUE,0,0xDDD9FF);
    }
    public static boolean accepts(Cod3VisualPacket p) {
        return p.valid()&&p.sequence().equals(CUE)&&p.template()==21&&p.entityId()==-1&&p.duration()==DURATION&&p.scale()==1&&p.tick()==0;
    }
    public static void send(ServerLevel level,Vec3 origin,Vec3 direction) {
        var p=packet(level.dimension().location().toString(),level.random.nextLong(),level.getGameTime(),origin,direction);
        if(!accepts(p))return;
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(origin.x,origin.y,origin.z,32,level.dimension())),p);
    }
    private SevenStarFlash() {}
}

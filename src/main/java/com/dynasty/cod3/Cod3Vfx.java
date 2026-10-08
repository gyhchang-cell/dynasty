package com.dynasty.cod3;

import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;

public final class Cod3Vfx {
    public static void send(ServerLevel level,int template,Vec3 origin,Vec3 direction,int duration,double scale){
        send(level,template,origin,direction,duration,scale,0);
    }
    public static void send(ServerLevel level,int template,Vec3 origin,Vec3 direction,int duration,double scale,int tint){
        var p=new Cod3VisualPacket(level.dimension().location().toString(),template,-1,level.random.nextLong(),level.getGameTime(),duration,scale,origin,direction,"",0,tint);
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(origin.x,origin.y,origin.z,32,level.dimension())),p);
    }
    public static void sync(ServerPlayer p,net.minecraft.world.entity.Mob boss,String sequence,int tick,int total){
        DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->p),new Cod3VisualPacket(boss.level().dimension().location().toString(),0,boss.getId(),boss.getUUID().getLeastSignificantBits(),boss.level().getGameTime()-tick,total,1,boss.position(),boss.getLookAngle(),sequence,tick));
    }
    public static void sequence(net.minecraft.world.entity.Mob boss,String id,int tick,BossSequenceDefinition.Step step){
        if(!(boss.level() instanceof ServerLevel level))return;
        var p=new Cod3VisualPacket(level.dimension().location().toString(),step.vfx(),boss.getId(),boss.getUUID().getLeastSignificantBits()+step.startTick(),level.getGameTime()-tick+step.startTick(),Math.min(120,step.duration()),step.radius()/3,boss.position(),boss.getLookAngle(),id,tick);
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(boss.getX(),boss.getY(),boss.getZ(),32,level.dimension())),p);
    }
    private Cod3Vfx(){}
}

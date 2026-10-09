package com.dynasty.cod3;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.network.NetworkEvent;
import java.util.function.Supplier;

/** World-space effects only: this packet has no camera, screen overlay or player-input fields. */
public record Cod3VisualPacket(String dimension,int template,int entityId,long seed,long start,int duration,double scale,Vec3 origin,Vec3 direction,String sequence,int tick,int tint) {
    public Cod3VisualPacket(String dimension,int template,int entityId,long seed,long start,int duration,double scale,Vec3 origin,Vec3 direction,String sequence,int tick){this(dimension,template,entityId,seed,start,duration,scale,origin,direction,sequence,tick,0);}
    public static void encode(Cod3VisualPacket p,FriendlyByteBuf b){b.writeUtf(p.dimension,128);b.writeVarInt(p.template);b.writeInt(p.entityId);b.writeLong(p.seed);b.writeLong(p.start);b.writeVarInt(p.duration);b.writeDouble(p.scale);write(b,p.origin);write(b,p.direction);b.writeUtf(p.sequence,128);b.writeVarInt(p.tick);b.writeInt(p.tint);}
    private static void write(FriendlyByteBuf b,Vec3 v){b.writeDouble(v.x);b.writeDouble(v.y);b.writeDouble(v.z);}
    private static Vec3 read(FriendlyByteBuf b){return new Vec3(b.readDouble(),b.readDouble(),b.readDouble());}
    public static Cod3VisualPacket decode(FriendlyByteBuf b){return new Cod3VisualPacket(b.readUtf(128),b.readVarInt(),b.readInt(),b.readLong(),b.readLong(),b.readVarInt(),b.readDouble(),read(b),read(b),b.readUtf(128),b.readVarInt(),b.readInt());}
    public boolean valid(){return dimension!=null&&net.minecraft.resources.ResourceLocation.tryParse(dimension)!=null&&sequence!=null&&sequence.length()<=128&&tick>=0&&entityId>=-1&&origin!=null&&direction!=null&&(template!=0||!sequence.isBlank()&&tick<=duration)&&template>=0&&template<=40&&duration>0&&duration<=2400&&tint>=0&&tint<=0xffffff&&Double.isFinite(scale)&&scale>0&&scale<=32&&Double.isFinite(origin.lengthSqr())&&Double.isFinite(direction.lengthSqr());}
    public static void handle(Cod3VisualPacket p,Supplier<NetworkEvent.Context> supplier){var c=supplier.get();if(p.valid()&&c.getDirection().getReceptionSide().isClient())c.enqueueWork(()->DistExecutor.unsafeRunWhenOn(Dist.CLIENT,()->()->com.dynasty.client.Cod3VfxRenderer.receive(p)));c.setPacketHandled(true);}
}
